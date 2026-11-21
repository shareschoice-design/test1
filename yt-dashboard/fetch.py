#!/usr/bin/env python3
"""Stáhne statistiky všech připojených YouTube kanálů a uloží je zašifrované.

Spouští se automaticky z GitHub Actions (.github/workflows/youtube-dashboard.yml).
Vstup: proměnná prostředí YT_DASHBOARD = JSON vygenerovaný stránkou connect.html
       {"client_id", "client_secret", "password", "channels": [{"id", "title", "refresh_token"}]}
Výstup: zašifrovaný soubor (openssl AES-256-CBC, PBKDF2-SHA256) s aktuálními daty a historií.
Používá jen standardní knihovnu Pythonu + příkaz openssl.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

YT = "https://www.googleapis.com/youtube/v3/"
ANALYTICS = "https://youtubeanalytics.googleapis.com/v2/reports"
MAX_VIDEO_PAGES = 40          # max 2000 videí na kanál
H48 = 48 * 3600
HOURLY_KEEP = 14 * 86400      # hodinové snímky držíme 14 dní, starší jen 1 denně
DAILY_KEEP = 400 * 86400
PBKDF2_ITER = "100000"


class ApiError(Exception):
    def __init__(self, status, msg):
        super().__init__(f"{status}: {msg}")
        self.status = status


def http(url, params=None, token=None, data=None):
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                err = json.load(e)
            except Exception:
                err = {}
            er = err.get("error")
            msg = err.get("error_description") or (er.get("message") if isinstance(er, dict) else er) or e.reason
            if e.code >= 500 and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            raise ApiError(e.code, msg)
        except urllib.error.URLError:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            raise


def access_token(cfg, refresh_token):
    r = http("https://oauth2.googleapis.com/token", data={
        "client_id": cfg["client_id"], "client_secret": cfg["client_secret"],
        "refresh_token": refresh_token, "grant_type": "refresh_token"})
    return r["access_token"]


def ts(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()) if iso else None


def fetch_channel(cfg, cred, now):
    tok = access_token(cfg, cred["refresh_token"])
    c = (http(YT + "channels", {"part": "snippet,statistics,contentDetails", "mine": "true"}, tok).get("items") or [None])[0]
    if not c:
        raise ApiError(404, "kanál nenalezen")
    st = c["statistics"]
    out = {
        "id": c["id"], "title": c["snippet"]["title"], "customUrl": c["snippet"].get("customUrl"),
        "thumb": (c["snippet"].get("thumbnails") or {}).get("default", {}).get("url"),
        "t": now, "subs": None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
        "views": int(st.get("viewCount", 0)), "publicCount": int(st.get("videoCount", 0)),
        "counts": {"public": 0, "unlisted": 0, "private": 0, "scheduled": 0},
        "truncated": False, "videos": [], "comments48": [], "commentsMore": False, "analytics": None, "errors": [],
    }

    # všechna videa (vlastník vidí i soukromá / neveřejná / naplánovaná)
    ids, page, n = [], None, 0
    uploads = c.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    while uploads:
        try:
            p = http(YT + "playlistItems", {"part": "contentDetails", "playlistId": uploads, "maxResults": 50, "pageToken": page}, tok)
        except ApiError as e:
            if e.status == 404:  # kanál bez videí
                break
            raise
        ids += [i["contentDetails"]["videoId"] for i in p.get("items", [])]
        page, n = p.get("nextPageToken"), n + 1
        if not page:
            break
        if n >= MAX_VIDEO_PAGES:
            out["truncated"] = True
            break
    vids = []
    for i in range(0, len(ids), 50):
        v = http(YT + "videos", {"part": "snippet,status,statistics", "id": ",".join(ids[i:i + 50]), "maxResults": 50}, tok)
        for x in v.get("items", []):
            s = x.get("statistics", {})
            vids.append({
                "id": x["id"], "title": x["snippet"]["title"],
                "thumb": (x["snippet"].get("thumbnails") or {}).get("default", {}).get("url"),
                "published": ts(x["snippet"]["publishedAt"]), "privacy": x["status"]["privacyStatus"],
                "publishAt": ts(x["status"].get("publishAt")),
                "views": int(s.get("viewCount", 0)), "likes": int(s.get("likeCount", 0)), "comments": int(s.get("commentCount", 0)),
            })
    for v in vids:
        if v["privacy"] == "private" and v["publishAt"] and v["publishAt"] > now:
            out["counts"]["scheduled"] += 1
        else:
            out["counts"][v["privacy"]] = out["counts"].get(v["privacy"], 0) + 1
    vids.sort(key=lambda v: v["published"] or 0, reverse=True)
    out["videos"] = vids[:15]
    out["uploaded48"] = sum(1 for v in vids if now - (v["published"] or 0) < H48)
    out["new48"] = sum(1 for v in vids if v["privacy"] == "public" and now - (v["published"] or 0) < H48)
    top = sorted((v for v in vids if v["privacy"] == "public"), key=lambda v: v["views"], reverse=True)[:5]
    out["topVideos"] = top

    # komentáře za posledních 48 h
    try:
        page, n, stop = None, 0, False
        while True:
            cm = http(YT + "commentThreads", {"part": "snippet", "allThreadsRelatedToChannelId": out["id"], "order": "time", "maxResults": 100, "pageToken": page}, tok)
            for th in cm.get("items", []):
                s = th["snippet"]["topLevelComment"]["snippet"]
                t = ts(s["publishedAt"])
                if now - t > H48:
                    stop = True
                    break
                out["comments48"].append({"author": s.get("authorDisplayName"), "text": s.get("textOriginal", "")[:500], "t": t,
                                          "video": th["snippet"].get("videoId"), "replies": th["snippet"].get("totalReplyCount", 0)})
            page, n = cm.get("nextPageToken"), n + 1
            if stop or not page:
                break
            if n >= 5:
                out["commentsMore"] = True
                break
    except ApiError as e:
        if not (e.status == 403 and "disabled" in str(e).lower()):
            out["errors"].append(f"Komentáře: {e}")

    # YouTube Analytics – 30 dní po dnech
    try:
        end = datetime.fromtimestamp(now, timezone.utc).date()
        a = http(ANALYTICS, {"ids": "channel==MINE", "startDate": str(end - timedelta(days=30)), "endDate": str(end),
                             "metrics": "views,estimatedMinutesWatched,subscribersGained,subscribersLost", "dimensions": "day", "sort": "day"}, tok)
        rows = [{"day": r[0], "views": r[1], "minutes": r[2], "gained": r[3], "lost": r[4]} for r in a.get("rows") or []]

        def agg(rs):
            return {"views": sum(r["views"] for r in rs), "subs": sum(r["gained"] - r["lost"] for r in rs),
                    "hours": round(sum(r["minutes"] for r in rs) / 60)}
        out["analytics"] = {"rows": rows, "lastDay": rows[-1]["day"] if rows else None,
                            "d2": agg(rows[-2:]), "d7": agg(rows[-7:]), "d28": agg(rows[-28:])}
    except ApiError as e:
        out["errors"].append(f"Analytics: {e}")
    return out


def openssl(args, data, password):
    env = dict(os.environ, YTD_PW=password)
    r = subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", PBKDF2_ITER, "-md", "sha256", *args, "-pass", "env:YTD_PW"],
                       input=data, capture_output=True, env=env)
    if r.returncode:
        raise RuntimeError(r.stderr.decode())
    return r.stdout


def prune(hist, now):
    keep, seen_days = [], set()
    for p in sorted(hist, key=lambda p: p["t"], reverse=True):
        age = now - p["t"]
        if age < HOURLY_KEEP:
            keep.append(p)
        elif age < DAILY_KEEP:
            day = datetime.fromtimestamp(p["t"], timezone.utc).date()
            if day not in seen_days:
                seen_days.add(day)
                keep.append(p)
    return sorted(keep, key=lambda p: p["t"])


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data.enc"
    raw = os.environ.get("YT_DASHBOARD", "").strip()
    if not raw:
        sys.exit("Chybí secret YT_DASHBOARD – vytvoř ho podle stránky connect.html.")
    cfg = json.loads(raw)
    pw = cfg["password"]
    now = int(time.time())

    prev = {}
    if os.path.exists(out_path):
        try:
            prev = json.loads(openssl(["-d"], open(out_path, "rb").read(), pw))
        except Exception as e:
            print("Předchozí data nejdou dešifrovat (změněné heslo?), začínám znovu:", e)
    prev_ch = {c["id"]: c for c in prev.get("channels", [])}
    history = prev.get("history", {})

    channels = []
    for cred in cfg["channels"]:
        try:
            ch = fetch_channel(cfg, cred, now)
            print(f"OK  {ch['title']}: {ch['subs']} odběratelů, {ch['views']} zhlédnutí")
            h = history.get(ch["id"], [])
            h.append({"t": now, "subs": ch["subs"], "views": ch["views"], "videos": ch["publicCount"]})
            history[ch["id"]] = prune(h, now)
        except Exception as e:
            print(f"ERR {cred.get('title') or cred.get('id')}: {e}")
            ch = dict(prev_ch.get(cred.get("id")) or {"id": cred.get("id"), "title": cred.get("title")})
            ch["fetchError"] = str(e)
            ch["needsReconnect"] = isinstance(e, ApiError) and e.status in (400, 401)
        channels.append(ch)

    known = {c["id"] for c in channels}
    history = {k: v for k, v in history.items() if k in known}
    payload = json.dumps({"generated": now, "channels": channels, "history": history}, ensure_ascii=False, separators=(",", ":")).encode()
    with open(out_path, "wb") as f:
        f.write(openssl(["-salt"], payload, pw))
    print(f"Uloženo {len(channels)} kanálů do {out_path}")
    if all(c.get("fetchError") for c in channels):
        sys.exit("Žádný kanál se nepodařilo načíst.")


if __name__ == "__main__":
    main()

"""National Park Service videos (www.nps.gov/media/video/view.htm?id=...).

  python3 nps_fetch.py list <park_code> [<park_code> ...]   -> one JSON line per video: id, title, desc, credit, url1080, pd
  python3 nps_fetch.py get <video_id_or_url> <out_path_without_ext>   -> downloads the best mp4 + writes <out>.json

Only videos whose page says "public domain" are downloaded. Credit "National Park Service" (or the credit shown).
"""
import html, json, re, subprocess, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def get(url):
    return subprocess.run(["curl", "-sL", "-m", "60", "-A", UA, url], capture_output=True, text=True).stdout


def info(vid):
    url = f"https://www.nps.gov/media/video/view.htm?id={vid}"
    p = get(url)
    title = html.unescape((re.search(r'<meta property="og:title" content="([^"]*)"', p) or re.search(r"<h1[^>]*>([^<]+)</h1>", p) or [None, ""])[1]).strip()
    desc = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', p) or re.search(r'<meta property="og:description" content="([^"]*)"', p) or [None, ""])[1]).strip()
    mp4s = re.findall(r"https://www\.nps\.gov/nps-audiovideo/audiovideo/[0-9a-f-]+?(\d{3,4})p\.mp4", p)
    urls = sorted(set(re.findall(r"https://www\.nps\.gov/nps-audiovideo/audiovideo/[0-9a-f-]+?\d{3,4}p\.mp4", p)),
                  key=lambda u: int(re.search(r"(\d{3,4})p\.mp4", u).group(1)))
    cr = re.search(r"Credit</[^>]+>\s*<[^>]+>([^<]+)<", p) or re.search(r'Credit">([^<]+)<', p)
    dur = re.search(r"Duration[^0-9]*(\d+)\s*minutes?,?\s*(\d+)?\s*seconds?", p)
    return {"id": vid, "page": url, "title": title, "desc": desc, "credit": html.unescape(cr.group(1)).strip() if cr else "National Park Service",
            "best": urls[-1] if urls else "", "res": max(map(int, mp4s)) if mp4s else 0, "pd": "public domain" in p.lower(),
            "dur": (int(dur.group(1)) * 60 + int(dur.group(2) or 0)) if dur else None}


if sys.argv[1] == "list":
    for park in sys.argv[2:]:
        ids = []
        for pg in [f"https://www.nps.gov/{park}/learn/photosmultimedia/videos.htm", f"https://www.nps.gov/{park}/learn/photosmultimedia/multimedia.htm"]:
            ids += re.findall(r"/media/video/view\.htm\?id=([0-9A-F-]{20,})", get(pg))
        for vid in dict.fromkeys(ids):
            d = info(vid); d["park"] = park
            print(json.dumps(d), flush=True)
else:
    vid, out = sys.argv[2], sys.argv[3]
    vid = re.search(r"id=([0-9A-F-]+)", vid).group(1) if "id=" in vid else vid
    d = info(vid)
    if not d["pd"]:
        sys.exit(f"not marked public domain: {d['page']}")
    if not d["best"]:
        sys.exit("no mp4")
    subprocess.run(["curl", "-sSL", "-m", "900", "-A", UA, "-o", out + ".mp4", d["best"]], check=True)
    meta = {"source": "National Park Service (public domain)", "page": d["page"], "file": d["best"], "title": d["title"],
            "credit": d["credit"] or "National Park Service", "description": d["desc"], "nps_id": vid,
            "note": "NPS public domain; credit National Park Service."}
    json.dump(meta, open(out + ".json", "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("title", "file")}, indent=1))

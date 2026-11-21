"""Find and download stock video from Coverr (free licence, commercial use, no attribution required).
The API key is injected by the environment proxy – no key needed here.

  preview:  python3 coverr_fetch.py preview <out_dir> KEY="search query" [KEY2="query"] ...
            -> downloads 360p previews of the top 4 hits per key, writes <out_dir>/<KEY>_sheet.jpg and candidates.json
  get:      python3 coverr_fetch.py get <out_dir> KEY=<hit_index> ...
            -> downloads the chosen hit in 1080p as <out_dir>/<KEY>.mp4 and records it in credits.json
"""
import json, os, subprocess, sys, urllib.parse, urllib.request

API = "https://api.coverr.co/videos"


def search(q, n=4):
    url = f"{API}?{urllib.parse.urlencode({'query': q, 'page_size': 12, 'urls': 'true'})}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0", "Accept": "application/json"})
    hits = json.load(urllib.request.urlopen(req, timeout=30)).get("hits", [])
    # prefer vertical, then highest resolution
    hits.sort(key=lambda h: (not h.get("is_vertical"), -(h.get("max_width") or 0)))
    return hits[:n]


def fetch(url, out):
    subprocess.run(["curl", "-sSL", "-m", "300", "-o", out, url], check=True)


def preview(out_dir, pairs):
    os.makedirs(out_dir, exist_ok=True)
    cpath = f"{out_dir}/candidates.json"
    cand = json.load(open(cpath)) if os.path.exists(cpath) else {}
    for key, q in pairs:
        hits = search(q)
        cand[key] = [{"id": h["id"], "title": h["title"], "vertical": h.get("is_vertical"),
                      "w": h.get("max_width"), "dur": float(h.get("duration") or 0), "urls": h["urls"]} for h in hits]
        tiles = []
        for i, h in enumerate(cand[key]):
            p = f"{out_dir}/.{key}_{i}.mp4"
            fetch(h["urls"]["mp4_preview"], p)
            j = f"{out_dir}/.{key}_{i}.jpg"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(max(0.5, h["dur"] / 2)), "-i", p, "-frames:v", "1",
                            "-vf", f"scale=-2:240,pad=iw+8:ih+8:4:4:black,drawtext=fontfile=/root/.fonts/Montserrat.ttf:"
                                   f"text='{i}':x=8:y=8:fontsize=28:fontcolor=yellow:box=1:boxcolor=black", j], check=True)
            tiles.append(j)
        if tiles:
            args = sum([["-i", t] for t in tiles], [])
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-filter_complex",
                            "".join(f"[{k}]" for k in range(len(tiles))) + f"hstack={len(tiles)}" if len(tiles) > 1 else "null",
                            f"{out_dir}/{key}_sheet.jpg"], check=True)
        print(key, [(i, h["title"][:40], "V" if h["vertical"] else "H", h["w"]) for i, h in enumerate(cand[key])])
    json.dump(cand, open(cpath, "w"), indent=1)


def get(out_dir, picks):
    cand = json.load(open(f"{out_dir}/candidates.json"))
    cpath = f"{out_dir}/credits.json"
    credits = json.load(open(cpath)) if os.path.exists(cpath) else {}
    for key, idx in picks:
        h = cand[key][int(idx)]
        fetch(h["urls"]["mp4_download"], f"{out_dir}/{key}.mp4")
        credits[key] = {"source": "Coverr", "id": h["id"], "title": h["title"]}
        print("got", key, h["title"])
    json.dump(credits, open(cpath, "w"), indent=1)


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    pairs = [a.split("=", 1) for a in sys.argv[3:]]
    preview(out, pairs) if mode == "preview" else get(out, pairs)

"""Download a public-domain video from a DVIDS video page (www.dvidshub.net/video/<id>/...).
Picks the highest-resolution MP4, refuses anything not marked PUBLIC DOMAIN, writes <out>.json with title/credit.

Usage: python3 dvids_fetch.py <video_page_url> <out_path_without_ext>
"""
import html, json, re, subprocess, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
url, out = sys.argv[1], sys.argv[2]
page = subprocess.run(["curl", "-s", "-m", "30", "-A", UA, url], capture_output=True, text=True).stdout
if "PUBLIC DOMAIN" not in page.upper():
    sys.exit(f"not marked public domain: {url}")
mp4s = sorted(set(re.findall(r"https://[a-z0-9]+\.cloudfront\.net/video/[^\"' ]+?\.mp4", page)))
def res(u):
    m = re.search(r"-(\d+)x(\d+)-", u); return int(m.group(1)) * int(m.group(2)) if m else 0
if not mp4s:
    sys.exit("no mp4 found")
best = max(mp4s, key=res)
subprocess.run(["curl", "-sSL", "-m", "600", "-A", UA, "-o", out + ".mp4", best], check=True)
title = html.unescape((re.search(r"<title>([^<]+)</title>", page) or [None, ""])[1]).replace("DVIDS - Video - ", "").strip()
credit = re.search(r"(Video by [^<]{3,120})", page)
desc = re.search(r'<meta name="description" content="([^"]+)"', page)
meta = {"source": "DVIDS (public domain, U.S. DoD)", "page": url, "file": best, "title": title,
        "credit": html.unescape(credit.group(1)).strip() if credit else "",
        "description": html.unescape(desc.group(1)) if desc else "",
        "note": "Public domain. Do not imply DoD endorsement."}
json.dump(meta, open(out + ".json", "w"), indent=1)
print(json.dumps({k: meta[k] for k in ("title", "credit", "file")}, indent=1))

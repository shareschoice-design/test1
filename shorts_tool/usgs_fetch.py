"""Download a USGS multimedia video (www.usgs.gov/media/videos/<slug>) with its description.
USGS-authored media is public domain (credit "USGS"); the script refuses pages that don't say "Public Domain".

Usage: python3 usgs_fetch.py <page_url_or_slug> <out_path_without_ext>
"""
import html, json, re, subprocess, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
url, out = sys.argv[1], sys.argv[2]
if not url.startswith("http"):
    url = "https://www.usgs.gov/media/videos/" + url.strip("/").split("/")[-1]
page = subprocess.run(["curl", "-sL", "-m", "60", "-A", UA, url], capture_output=True, text=True).stdout
if "Public Domain" not in page:
    sys.exit(f"not marked Public Domain: {url}")
mp4s = sorted(set(re.findall(r"https://usgs-ocapsv2-public-(?:output|input)-media[^\"' ]+?\.mp4", page)))
mp4s += sorted(set(re.findall(r"https://(?:d9|prd)-wret\.s3[^\"' ]+?\.mp4", page)))
if not mp4s:
    sys.exit("no mp4 found")
# prefer the original upload (input bucket) – usually the full resolution
best = next((u for u in mp4s if "input-media" in u), mp4s[0])
subprocess.run(["curl", "-sSL", "-m", "900", "-A", UA, "-o", out + ".mp4", best], check=True)
title = html.unescape((re.search(r"<title>([^<|]+)", page) or [None, ""])[1]).strip()
d = page.find("Detailed Description")
desc = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page[d:d + 4000]))).replace("Detailed Description", "").strip() if d > 0 else ""
desc = desc.split(" Details ")[0].split(" Sources/Usage")[0]
meta = {"source": "USGS (public domain)", "page": url, "file": best, "title": title, "credit": "USGS", "description": desc,
        "usgs_page": url, "note": "USGS public domain; credit USGS."}
json.dump(meta, open(out + ".json", "w"), indent=1)
print(json.dumps({k: meta[k] for k in ("title", "file")}, indent=1))

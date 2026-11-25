"""Download a NASA Image and Video Library video (images.nasa.gov) with its description.
NASA media is generally not copyrighted; credit "NASA" and never imply NASA endorsement.

Usage: python3 nasa_fetch.py <nasa_id> <out_path_without_ext> [max_mb]
Takes ~orig if it is <= max_mb (default 1500), otherwise ~large. Writes <out>.json like dvids_fetch.py.
"""
import json, subprocess, sys, urllib.parse

nid, out = sys.argv[1], sys.argv[2]
MAXMB = float(sys.argv[3]) if len(sys.argv) > 3 else 1500
q = urllib.parse.quote(nid)


def get(url):
    return json.loads(subprocess.run(["curl", "-s", "-m", "60", url], capture_output=True, text=True).stdout)


def size_mb(url):
    h = subprocess.run(["curl", "-sIL", "-m", "60", url], capture_output=True, text=True).stdout.lower()
    sizes = [int(l.split(":")[1]) for l in h.splitlines() if l.startswith("content-length:")]
    return sizes[-1] / 1e6 if sizes else 0


hrefs = [urllib.parse.quote(i["href"].replace("http://", "https://"), safe=":/~%") for i in get(f"https://images-api.nasa.gov/asset/{q}")["collection"]["items"]]
orig = next((h for h in hrefs if "~orig." in h.lower()), None)
large = next((h for h in hrefs if "~large.mp4" in h.lower()), None)
pick = orig if orig and size_mb(orig) <= MAXMB else large
if not pick:
    sys.exit("no mp4")
subprocess.run(["curl", "-sSL", "-m", "1200", "-o", out + ".mp4", pick], check=True)
d = get(f"https://images-api.nasa.gov/search?nasa_id={q}")["collection"]["items"][0]["data"][0]
meta = {"source": "NASA Image and Video Library (not copyrighted)", "page": f"https://images.nasa.gov/details/{q}",
        "file": pick, "title": d.get("title", ""), "credit": "NASA" + (f" / {d['secondary_creator']}" if d.get("secondary_creator") else ""),
        "description": d.get("description", ""), "date": d.get("date_created", "")[:10],
        "note": "NASA content; credit NASA, do not imply NASA endorsement."}
json.dump(meta, open(out + ".json", "w"), indent=1)
print(json.dumps({k: meta[k] for k in ("title", "file")}, indent=1))

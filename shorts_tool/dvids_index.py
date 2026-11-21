"""Build a searchable index of all DVIDS videos from the public video sitemap.
Usage: python3 dvids_index.py build <out.jsonl>        (downloads ~630 sitemap pages, 4 at a time)
       python3 dvids_index.py search <index.jsonl> "regex" [min_s] [max_s]
"""
import json, re, subprocess, sys, html
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
BLOCK = re.compile(r"<url>(.*?)</url>", re.S)
def field(b, name):
    m = re.search(rf"<{name}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{name}>", b, re.S)
    return m.group(1).strip() if m else ""
def parse(xml):
    out = []
    for b in BLOCK.findall(xml):
        u = field(b, "loc")
        if "/video/" not in u: continue
        d = field(b, "video:duration")
        out.append({"url": u, "title": html.unescape(field(b, "video:title")), "desc": html.unescape(field(b, "video:description"))[:1500],
                    "dur": int(d) if d.isdigit() else 0, "date": field(b, "video:publication_date")[:10]})
    return out
def page(i):
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "-m", "90", "--compressed", "-A", UA, f"https://www.dvidshub.net/sitemap-video-{i}.xml"],
                           capture_output=True, text=True)
        if "<url>" in r.stdout:
            return parse(r.stdout)
    return []
if sys.argv[1] == "build":
    with open(sys.argv[2], "w") as f, ThreadPoolExecutor(4) as ex:
        for i, rows in enumerate(ex.map(page, range(630))):
            for r in rows: f.write(json.dumps(r) + "\n")
            if i % 50 == 0: print("page", i, len(rows), flush=True)
else:
    rx = re.compile(sys.argv[3], re.I); lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0; hi = int(sys.argv[5]) if len(sys.argv) > 5 else 99999
    for line in open(sys.argv[2]):
        r = json.loads(line)
        if lo <= r["dur"] <= hi and rx.search(r["title"] + " " + r["desc"]):
            print(f'{r["dur"]:>4}s {r["date"]} {r["url"]}\n      {r["title"]} :: {r["desc"][:160]}')

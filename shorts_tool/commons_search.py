"""Search Wikimedia Commons for openly licensed videos usable in monetised content.

Usage: python3 commons_search.py "<query>" [limit]
Prints only commercially usable licences (public domain, CC0, CC BY, CC BY-SA) – never NC/ND.
"""
import json, re, sys, urllib.parse, urllib.request

UA = "WildRewindShortsTool/1.0 (video research script)"
OK = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?( \d\.\d)?)", re.I)

def search(q, limit=30):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{q} filetype:video", "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        data = json.load(r)
    out = []
    for p in (data.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = re.sub("<[^>]+>", "", md.get("LicenseShortName", {}).get("value", "")).strip()
        if not OK.match(lic) or re.search(r"\b(nc|nd)\b", lic, re.I):
            continue
        artist = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()
        out.append({
            "title": p["title"], "license": lic, "author": artist[:80],
            "w": ii.get("width"), "h": ii.get("height"), "dur": round(ii.get("duration") or 0, 1),
            "size_mb": round((ii.get("size") or 0) / 1e6, 1), "url": ii.get("url"),
            "page": ii.get("descriptionurl"),
        })
    return sorted(out, key=lambda x: -(x["w"] or 0) * (x["h"] or 0))

if __name__ == "__main__":
    res = search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    for r in res:
        print(f"{r['w']}x{r['h']} {r['dur']:>6}s {r['size_mb']:>6}MB | {r['license']:<14} | {r['author'][:30]:<30} | {r['title']}")
    json.dump(res, open("/dev/stderr", "w"), indent=0) if "--json" in sys.argv else None

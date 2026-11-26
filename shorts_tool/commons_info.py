"""Print size, duration, licence, author and URL of Commons files via the API (with polite retries).
Usage: python3 commons_info.py "File:..." ["File:..." ...]   -> one JSON line per file"""
import json, subprocess, sys, time, urllib.parse
UA = "UnbrokenShortsBot/1.0 (research)"
for t in sys.argv[1:]:
    url = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=size|url|extmetadata|mediatype"
           "&format=json&titles=" + urllib.parse.quote(t))
    for attempt in range(6):
        out = subprocess.run(["curl", "-s", "-m", "30", "-A", UA, url], capture_output=True, text=True).stdout
        try:
            p = list(json.loads(out)["query"]["pages"].values())[0]; i = p["imageinfo"][0]; e = i.get("extmetadata", {})
            print(json.dumps({"title": p["title"], "w": i["width"], "h": i["height"], "dur": round(i.get("duration", 0)),
                              "license": e.get("LicenseShortName", {}).get("value"), "artist": e.get("Artist", {}).get("value", ""),
                              "desc": e.get("ImageDescription", {}).get("value", ""), "date": e.get("DateTimeOriginal", {}).get("value", ""),
                              "url": i["url"], "page": i["descriptionurl"]}))
            break
        except Exception:
            time.sleep(5 * (attempt + 1))
    else:
        print(json.dumps({"title": t, "error": out[:200]}))
    time.sleep(3)

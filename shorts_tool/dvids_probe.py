"""Probe DVIDS video pages for the best available MP4 resolution (no video download).
Usage: python3 dvids_probe.py <candidates.jsonl> <out.jsonl> [min_height]
Each output line: {url,title,desc,dur,date,cat,w,h,mp4} for pages that are PUBLIC DOMAIN and >= min_height."""
import json, re, subprocess, sys, time
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
src, out = sys.argv[1], sys.argv[2]; MINH = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
done = set()
try:
    done = {json.loads(l)["url"] for l in open(out)}
except FileNotFoundError:
    pass
with open(out, "a") as f:
    for line in open(src):
        r = json.loads(line)
        if r["url"] in done: continue
        page = subprocess.run(["curl", "-sL", "-m", "30", "-A", UA, r["url"]], capture_output=True, text=True).stdout
        time.sleep(2.5)
        if "PUBLIC DOMAIN" not in page.upper():
            r.update(w=0, h=0, mp4="", note="not PD or blocked"); f.write(json.dumps(r) + "\n"); f.flush(); continue
        mp4s = set(re.findall(r"https://[a-z0-9]+\.cloudfront\.net/video/[^\"' ]+?\.mp4", page))
        best = (0, 0, "")
        # newer pages: an original file without a size suffix; its size is listed in the page text
        dims = [(int(a), int(b)) for a, b in re.findall(r"\b(\d{3,4})x(\d{3,4})\b", page) if 300 <= int(b) <= 2200 and int(a) > int(b)]
        orig = [u for u in mp4s if not re.search(r"-\d+x\d+-", u)]
        if orig and dims:
            w, h = max(dims, key=lambda d: d[1]); best = (w, h, orig[0])
        for u in mp4s:
            m = re.search(r"-(\d+)x(\d+)-", u)
            if m and int(m.group(2)) > best[1]: best = (int(m.group(1)), int(m.group(2)), u)
        # verify the real resolution from the file header (page text lists generic renditions)
        if best[2]:
            # ffprobe can't use the proxy: fetch the first 3 MB with curl and read the header from that
            tmp = out + ".part.mp4"
            subprocess.run(["curl", "-s", "-m", "60", "-r", "0-2999999", "-o", tmp, best[2]])
            pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                 "-of", "csv=p=0", tmp], capture_output=True, text=True).stdout.strip().split("\n")[0]
            if "," in pr:
                w, h = (int(x) for x in pr.split(",")[:2]); best = (w, h, best[2])
            else:
                best = (0, 0, best[2])   # couldn't verify -> don't trust the page text
        short_side = min(best[0], best[1]) if best[0] else 0
        r.update(w=best[0], h=best[1], mp4=best[2], ok=short_side >= MINH)
        f.write(json.dumps(r) + "\n"); f.flush()

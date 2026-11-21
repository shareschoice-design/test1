"""Turn a compact story spec into a build_fast script.json with real DVIDS footage spread across the clip.
spec: {"file": "...", "voice": "...", "music": "...", "dark": bool, "hook": [text, nred], "skip": [0.0,0.05],
       "lines": [[vo, [hl...], label_or_null], ...]}
Each line gets 2 shots taken from consecutive parts of the source (pos 0..1), so the footage follows the story."""
import json, os, re, subprocess, sys
FOOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "footage", os.environ.get("FOOTDIR", "hd"))

def peak_pos(name):
    """position (0..1) of the most intense moment (max frame-difference) – used for the hook shot"""
    src = os.path.join(FOOT, name + ".mp4")
    r = subprocess.run(["ffmpeg", "-i", src, "-vf", "fps=4,scale=160:-2,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"], capture_output=True, text=True).stderr
    v = [float(x) for x in re.findall(r"YAVG=([\d.]+)", r)]
    if len(v) < 8: return 0.5
    sm = [sum(v[i:i+8]) for i in range(len(v) - 8)]
    n = len(v); i = max(range(int(n*0.15), len(sm) - int(n*0.05)), key=lambda k: sm[k])
    return round(i / n, 3)

spec = json.load(open(sys.argv[1])); out = sys.argv[2]
n = len(spec["lines"]); a, b = spec.get("range", [0.06, 0.97])
lines = []
for i, (vo, hl, label) in enumerate(spec["lines"]):
    p0 = a + (b - a) * i / n; p1 = a + (b - a) * (i + 0.5) / n
    ln = {"vo": vo, "hl": hl, "shots": [{"file": spec["file"], "pos": round(p0, 3)}, {"file": spec["file"], "pos": round(p1, 3)}]}
    if label: ln["label"] = label
    lines.append(ln)
if spec.get("hook_peak", True):
    pk = spec.get("hook_pos", peak_pos(spec["file"]))
    lines[0]["shots"] = [{"file": spec["file"], "pos": pk}, {"file": spec["file"], "pos": round(min(pk + 0.04, 0.95), 3)}]
    print(spec["file"], "hook at", pk)
sc = {"voice": spec["voice"], "music": spec["music"], "dark": spec.get("dark", False),
      "hook": {"text": spec["hook"][0], "red": spec["hook"][1]}, "lines": lines}
json.dump(sc, open(out, "w"), indent=1)

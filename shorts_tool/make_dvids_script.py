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
# duplicate guard: refuse if another short already uses this footage or the same event
_reg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shorts", "registry.json")
if os.path.exists(_reg) and not os.environ.get("ALLOW_DUP"):
    _me = os.path.basename(sys.argv[1])[:-5]
    _rows = json.load(open(_reg)); _mine = next((r for r in _rows if r["footage"] == spec["file"]), None)
    for r in _rows:
        others = [s["name"] for s in r["shorts"] if s["name"] != _me and not s.get("rejected")]
        if not others: continue
        same_foot = r["footage"] == spec["file"]
        same_event = _mine and r is not _mine and _mine["event"][0] and r["event"][0] == _mine["event"][0] and set(r["event"][1]) & set(_mine["event"][1])
        if same_foot or same_event:
            sys.exit(f"DUPLICATE: {_me} repeats {others} ({'same footage' if same_foot else 'same event ' + r['event'][0]}). Set ALLOW_DUP=1 to override.")
n = len(spec["lines"]); a, b = spec.get("range", [0.06, 0.97])
lines = []
for i, entry in enumerate(spec["lines"]):
    vo, hl, label = entry[:3]
    card = entry[3] if len(entry) > 3 else None
    p0 = a + (b - a) * i / n; p1 = a + (b - a) * (i + 0.5) / n
    ln = {"vo": vo, "hl": hl, "shots": [{"file": spec["file"], "pos": round(p0, 3)}, {"file": spec["file"], "pos": round(p1, 3)}]}
    if label: ln["label"] = label
    if card:   # our own stat card replaces the second shot of this line
        ln["shots"][1] = {"card": {"file": spec["file"], "pos": round(p1, 3), "big": card[0], "small": card[1] if len(card) > 1 else ""}}
    lines.append(ln)
if spec.get("hook_peak", True):
    pk = spec.get("hook_pos", peak_pos(spec["file"]))
    lines[0]["shots"] = [{"file": spec["file"], "pos": pk}, {"file": spec["file"], "pos": round(min(pk + 0.04, 0.95), 3)}]
    print(spec["file"], "hook at", pk)
sc = {"voice": spec["voice"], "music": spec["music"], "dark": spec.get("dark", False),
      "hook": {"text": spec["hook"][0], "red": spec["hook"][1]}, "lines": lines}
json.dump(sc, open(out, "w"), indent=1)

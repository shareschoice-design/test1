"""Turn a compact story spec into a build_fast script.json with real DVIDS footage spread across the clip.
spec: {"file": "...", "voice": "...", "music": "...", "dark": bool, "hook": [text, nred], "skip": [0.0,0.05],
       "lines": [[vo, [hl...], label_or_null], ...]}
Each line gets 2 shots taken from consecutive parts of the source (pos 0..1), so the footage follows the story."""
import json, sys
spec = json.load(open(sys.argv[1])); out = sys.argv[2]
n = len(spec["lines"]); a, b = spec.get("range", [0.06, 0.97])
lines = []
for i, (vo, hl, label) in enumerate(spec["lines"]):
    p0 = a + (b - a) * i / n; p1 = a + (b - a) * (i + 0.5) / n
    ln = {"vo": vo, "hl": hl, "shots": [{"file": spec["file"], "pos": round(p0, 3)}, {"file": spec["file"], "pos": round(p1, 3)}]}
    if label: ln["label"] = label
    lines.append(ln)
sc = {"voice": spec["voice"], "music": spec["music"], "dark": spec.get("dark", False),
      "hook": {"text": spec["hook"][0], "red": spec["hook"][1]}, "lines": lines}
json.dump(sc, open(out, "w"), indent=1)

"""Generate per-segment voiceover with Piper (darker, slightly slower)."""
import json, subprocess, sys, os
model = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("PIPER_MODEL")
segs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
FX = ("asetrate=22050*0.93,aresample=44100,atempo=1/0.93,bass=g=4:f=120,treble=g=-2:f=6000,"
      "acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
for s in segs:
    if not s["vo"]: continue
    raw = f"{out}/{s['id']}_raw.wav"
    subprocess.run(["python3", "-m", "piper", "-m", model, "--length-scale", os.environ.get("LS", "1.1"), "-f", raw],
                   input=s["vo"].encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", FX, "-ac", "1", f"{out}/{s['id']}.wav"], check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{out}/{s['id']}.wav"],
                       capture_output=True, text=True).stdout.strip()
    print(s["id"], d)

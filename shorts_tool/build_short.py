"""Build a vertical 'rewind' explainer short from a script.json.

Usage: python3 build_short.py <project_dir> <source_video> <vo_dir> <work_dir>
project_dir must contain script.json and images/imgN.png.
Segment types: clip (3s real footage from source), rewind (reversed glitch transition), imgN (Ken Burns infographic).
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from caption import render

PROJ, SRC, VO, WORK = sys.argv[1:5]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
segs = json.load(open(f"{PROJ}/script.json"))

def sh(*a):
    subprocess.run(list(a), check=True)

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

GRADE = "eq=contrast=1.08:brightness=-0.04:saturation=0.9,vignette=PI/5"

# ---- timing ----
t = 0.0
for s in segs:
    vo = f"{VO}/{s['id']}.wav"
    s["vo_len"] = dur(vo) if s["vo"] else 0.0
    if s["src"] == "rewind":
        d = s["dur"]
    elif s["src"] == "clip":
        d = max(3.0, s["vo_len"] + 0.55)
    else:
        d = max(2.2, s["vo_len"] + 0.6)
    if s is segs[-1]:
        d += 0.6
    s["d"], s["t"] = round(d, 3), round(t, 3)
    t += s["d"]
TOTAL = t
print("total", round(TOTAL, 2))

# ---- per-segment video ----
parts = []
for i, s in enumerate(segs):
    out = f"{WORK}/{s['id']}.mp4"
    d = s["d"]
    cap = f"{WORK}/{s['id']}_cap.png"
    render(s["cap"], set(s["hl"]), cap)
    caps = [cap]
    if s.get("label"):
        lab = f"{WORK}/{s['id']}_lab.png"
        render(s["label"], set(range(len(s["label"].split()) - 1)) if "earlier" in s["label"] else set(range(len(s["label"].split()))),
               lab, size=46, y=H * 0.22)
        caps.append(lab)
    inputs, base = [], ""
    if s["src"] == "clip":
        speed = min(d / 3.0, 1.6)
        span = d / speed
        inputs = ["-ss", str(s["start"]), "-t", str(span + 0.1), "-i", SRC]
        base = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},"
                f"setpts={speed}*PTS,{GRADE},trim=duration={d},setpts=PTS-STARTPTS[b]")
    elif s["src"] == "rewind":
        inputs = ["-ss", "0", "-t", "3.3", "-i", SRC]
        n = d
        base = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},reverse,"
                f"setpts=PTS/3.0,trim=duration={n},setpts=PTS-STARTPTS,"
                f"eq=contrast=1.3:brightness=-0.06:saturation=0.6,noise=alls=28:allf=t,rgbashift=rh=-12:bh=12,"
                f"drawbox=y=ih*0.62:w=iw:h=26:color=white@0.25:t=fill,"
                f"drawgrid=w=iw:h=6:t=2:color=black@0.35,vignette=PI/4[b]")
    else:
        img = f"{PROJ}/images/{s['src']}.png"
        frames = int(round(d * FPS))
        zin = i % 2 == 0
        z = f"1.0+0.10*on/{frames}" if zin else f"1.10-0.10*on/{frames}"
        inputs = ["-loop", "1", "-t", str(d), "-i", img]
        base = (f"[0:v]scale=1620:2880,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={frames}:s={W}x{H}:fps={FPS},setsar=1,trim=duration={d},vignette=PI/5[b]")
    fc = base
    last = "b"
    for k, c in enumerate(caps):
        inputs += ["-loop", "1", "-t", str(d), "-i", c]
        delay = 0.08 + 0.12 * k
        fc += (f";[{k+1}:v]format=rgba,fade=t=in:st={delay}:d=0.15:alpha=1[c{k}]"
               f";[{last}][c{k}]overlay=0:0:format=auto[o{k}]")
        last = f"o{k}"
    fc += f";[{last}]format=yuv420p[v]"
    sh("ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[v]",
       "-t", str(d), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", out)
    parts.append(out)
    print("built", s["id"], d)

with open(f"{WORK}/concat.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/concat.txt", "-c", "copy", f"{WORK}/video.mp4")

# ---- audio ----
SR = 44100
ain, amix = [], []
idx = 0
def add(path, at, vol=1.0):
    global idx
    ain.extend(["-i", path])
    ms = int(at * 1000)
    amix.append(f"[{idx}:a]aresample={SR},aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[a{idx}]")
    idx += 1

# dark drone bed
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
   f"aevalsrc='0.35*sin(2*PI*55*t)+0.22*sin(2*PI*82.4*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.12*sin(2*PI*110.3*t)':s={SR}:d={TOTAL}",
   "-f", "lavfi", "-i", f"anoisesrc=c=brown:a=0.25:d={TOTAL}:r={SR}",
   "-filter_complex", f"[1]lowpass=f=300[n];[0][n]amix=inputs=2:weights=1 0.6,lowpass=f=900,afade=t=in:d=1.5,afade=t=out:st={TOTAL-1.5}:d=1.5",
   f"{WORK}/drone.wav")
add(f"{WORK}/drone.wav", 0, 0.22)
# low impact hit
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
   f"aevalsrc='0.9*sin(2*PI*(48+40*exp(-12*t))*t)*exp(-4.5*t)':s={SR}:d=1.4", f"{WORK}/hit.wav")
# rewind tape sound: rising filtered noise warble
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.6:d=1.2:r={SR}",
   "-f", "lavfi", "-i", f"aevalsrc='0.4*sin(2*PI*(300+1400*t*t)*t)':s={SR}:d=1.2",
   "-filter_complex", "[0]highpass=f=800,lowpass=f=6000[n];[n][1]amix=inputs=2,vibrato=f=12:d=0.6,afade=t=in:d=0.1,afade=t=out:st=0.95:d=0.25",
   f"{WORK}/rewind.wav")
# whoosh for the drop
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.7:d=1.0:r={SR}",
   "-af", "bandpass=f=900:w=1200,afade=t=in:d=0.6:curve=exp,afade=t=out:st=0.6:d=0.4", f"{WORK}/whoosh.wav")

for s in segs:
    if s["vo"]:
        add(f"{VO}/{s['id']}.wav", s["t"] + (0.25 if s is segs[0] else 0.15), 1.0)
    if s["src"] == "rewind":
        add(f"{WORK}/rewind.wav", s["t"], 0.5)
    if s["src"] == "clip" or s.get("label"):
        add(f"{WORK}/hit.wav", s["t"], 0.55)
    if s["cap"].lower().startswith("then it drops"):
        add(f"{WORK}/whoosh.wav", max(0, s["t"] - 0.4), 0.6)

fc = ";".join(amix) + ";" + "".join(f"[a{k}]" for k in range(idx)) + \
     f"amix=inputs={idx}:normalize=0,alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5:LRA=9[out]"
sh("ffmpeg", "-y", "-loglevel", "error", *ain, "-filter_complex", fc, "-map", "[out]", "-t", str(TOTAL), "-ar", str(SR),
   f"{WORK}/audio.wav")

final = f"{PROJ}/final.mp4"
sh("ffmpeg", "-y", "-loglevel", "error", "-i", f"{WORK}/video.mp4", "-i", f"{WORK}/audio.wav", "-map", "0:v", "-map", "1:a",
   "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final)
print("done", final, round(dur(final), 2))

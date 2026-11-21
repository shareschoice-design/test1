"""Fast-paced short builder: a cut every ~1.7 s, word-synced pop captions, flashes, whooshes, music bed.

Usage: python3 build_fast.py <project_dir> <footage_dir> <work_dir>
Env: PIPER_MODEL (voice .onnx), LS (length scale, default 1.0), DARK=1 (pitch the voice down),
     MUSIC (optional music file; otherwise a soft synth pad is generated), CUT (seconds per cut, default 1.7)

project_dir/script.json:
{"lines": [
   {"vo": "Sentence...", "hl": ["word", ...], "label": "1982",          # label optional (top text)
    "shots": [{"file": "clip.mp4", "start": 3.0, "cx": 0.5, "fit": false},
              {"img": "img1"}]}                                         # images from project_dir/images/
]}
"""
import json, math, os, re, subprocess, sys

PROJ, FOOT, WORK = sys.argv[1:4]
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
CUT = float(os.environ.get("CUT", "1.7"))
LS = os.environ.get("LS", "1.0")

FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
script = json.load(open(f"{PROJ}/script.json"))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.environ.get("VOICE_DIR", "")
# per-script voice / music override the environment
MODEL = os.path.join(VOICE_DIR, script["voice"] + ".onnx") if script.get("voice") and VOICE_DIR else os.environ["PIPER_MODEL"]
if script.get("music"):
    os.environ["MUSIC"] = os.path.join(REPO, script["music"])
lines = script["lines"]


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


# ---------- 1. voiceover per line ----------
VOICE_FX = "aresample=44100,acompressor=threshold=-18dB:ratio=3:attack=5:release=80"
if os.environ.get("DARK") == "1" or script.get("dark"):
    VOICE_FX = ("asetrate=22050*0.95,aresample=44100,atempo=1/0.95,bass=g=3:f=120,"
                "acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
for i, ln in enumerate(lines):
    raw, out = f"{WORK}/vo{i:02d}_raw.wav", f"{WORK}/vo{i:02d}.wav"
    sh("python3", "-m", "piper", "-m", MODEL, "--length-scale", LS, "-f", raw, input=ln["vo"].encode(), capture_output=True)
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", VOICE_FX, "-ac", "1", out)
    ln["vo_len"] = dur(out)


# ---------- 2. word timings (silences split phrases, chars split words) ----------
def silences(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=n=-38dB:d=0.11", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return list(zip(st, en))


def word_times(text, length, path):
    words = text.split()
    sil = [(a, b) for a, b in silences(path) if a > 0.05 and b < length - 0.05]
    # phrases split at punctuation
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,.;:!?…]$", w):
            phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    lead = 0.0
    s0 = silences(path)
    if s0 and s0[0][0] <= 0.05: lead = s0[0][1]
    spans = []
    if len(sil) == len(phrases) - 1:
        edges = [lead] + [x for ab in sil for x in ab] + [length]
        spans = [(edges[2 * k], edges[2 * k + 1]) for k in range(len(phrases))]
    else:
        spans = None
    out = []
    if spans:
        for ph, (a, b) in zip(phrases, spans):
            wts = [len(re.sub(r"\W", "", w)) + 1.5 for w in ph]
            t = a
            for w, wt in zip(ph, wts):
                d = (b - a) * wt / sum(wts); out.append((w, t, t + d)); t += d
    else:
        wts = [len(re.sub(r"\W", "", w)) + 1.5 + (2.5 if re.search(r"[,.;:!?]$", w) else 0) for w in words]
        t = lead
        for w, wt in zip(words, wts):
            d = (length - lead) * wt / sum(wts); out.append((w, t, t + d)); t += d
    return out


GAP = 0.12
t = 0.25
for i, ln in enumerate(lines):
    ln["t0"] = t
    ln["d"] = ln["vo_len"] + GAP
    ln["words"] = [(w, t + a, t + b) for w, a, b in word_times(ln["vo"], ln["vo_len"], f"{WORK}/vo{i:02d}.wav")]
    t += ln["d"]
TOTAL = t + 0.5
lines[-1]["d"] += 0.5
lines[0]["d"] += 0.25; lines[0]["t0"] = 0.0
print("total", round(TOTAL, 2))

# ---------- 3. visual pieces: a cut every ~CUT seconds ----------
GRADE = "eq=contrast=1.08:saturation=1.05,vignette=PI/5"
pieces, cut_times = [], []
pi = 0
for i, ln in enumerate(lines):
    n = max(1, round(ln["d"] / CUT))
    pd = ln["d"] / n
    shots = ln["shots"]
    for k in range(n):
        shot = shots[k % len(shots)]
        rep = k // len(shots)
        out = f"{WORK}/p{pi:03d}.mp4"
        frames = int(round(pd * FPS)) + 1
        zin = pi % 2 == 0
        flash = ",eq=brightness=0.35:enable='lt(t,0.07)'" if k == 0 and i > 0 else ""
        if "img" in shot:
            img = f"{PROJ}/images/{shot['img']}.png"
            z = f"1.04+0.10*on/{frames}" if zin else f"1.16-0.10*on/{frames}"
            px = "iw/2-(iw/zoom/2)" + ("+on*0.6" if pi % 3 == 0 else "-on*0.6" if pi % 3 == 1 else "")
            vf = (f"scale=1620:2880,zoompan=z='{z}':x='{px}':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
                  f"setsar=1,trim=duration={pd},vignette=PI/5{flash},format=yuv420p")
            sh("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(pd + 0.2), "-i", img, "-vf", vf,
               "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-an", out)
        else:
            fn = shot["file"] if os.path.splitext(shot["file"])[1] else shot["file"] + ".mp4"
            src = os.path.join(FOOT, fn)
            srcd = dur(src)
            st = (shot["start"] if "start" in shot else round(srcd * shot["pos"], 2) if "pos" in shot else round(srcd * 0.25, 2)) + rep * pd
            if st + pd > srcd: st = max(0.0, srcd - pd - 0.05)
            cx = shot.get("cx", 0.5)
            zf = 1.0 + (0.12 * (0 if zin else 1))
            zoom = f"scale=iw*{zf}:ih*{zf}," if zf != 1.0 else ""
            # slow push-in over the piece
            push = f",zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}" if zin else ""
            if shot.get("fit"):
                fc = (f"[0:v]fps={FPS},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                      f"boxblur=40:4,eq=brightness=-0.18[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=0:330,{GRADE}{flash},"
                      f"trim=duration={pd},setpts=PTS-STARTPTS,format=yuv420p[v]")
            else:
                fc = (f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,{zoom}"
                      f"crop={W}:{H}:(iw-{W})*{cx}:(ih-{H})*0.5,setsar=1{push},{GRADE}{flash},"
                      f"trim=duration={pd},setpts=PTS-STARTPTS,format=yuv420p[v]")
            sh("ffmpeg", "-y", "-loglevel", "error", "-ss", str(st), "-t", str(pd + 0.3), "-i", src,
               "-filter_complex", fc, "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "19", "-an", out)
        pieces.append(out)
        cut_times.append(ln["t0"] + k * pd)
        pi += 1
print("pieces", len(pieces))
with open(f"{WORK}/concat.txt", "w") as f:
    for p in pieces: f.write(f"file '{p}'\n")
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/concat.txt",
   "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-r", str(FPS), f"{WORK}/base.mp4")


# ---------- 4. ASS captions: 1-3 words, pop-in, red keywords ----------
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


RED = "&H3B3BFF&"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
       "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,Montserrat XB,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,7,4,5,60,60,0,1",
       "Style: Lab,Montserrat XB,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,5,3,8,60,60,330,1",
       "Style: Hook,Montserrat XB,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,1,0,1,8,5,5,60,60,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
HOOK = script.get("hook")
hook_end = lines[0]["t0"] + lines[0]["d"] if HOOK else -1
if HOOK:
    # BoltMotivation-style hook: 2-4 words, last words red, big, shown over the whole first line (also the thumbnail frame)
    hw = HOOK["text"].upper().split(); nred = HOOK.get("red", 2)
    txt = " ".join(hw[:-nred]) + (" " if len(hw) > nred else "") + f"{{\\c{RED}}}" + " ".join(hw[-nred:])
    ass.append(f"Dialogue: 3,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\pos(540,1000)\\fscx90\\fscy90\\t(0,120,\\fscx100\\fscy100)}}{txt}")
for li, ln in enumerate(lines):
    if HOOK and li == 0:
        continue
    hl = {h.lower() for h in ln.get("hl", [])}
    ws = ln["words"]
    chunks, cur = [], []
    for w in ws:
        cur.append(w)
        clean = re.sub(r"\W", "", w[0]).lower()
        if len(cur) >= 3 or re.search(r"[,.;:!?…]$", w[0]) or clean in hl or len(" ".join(x[0] for x in cur)) > 14:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for c in chunks:
        a, b = c[0][1], c[-1][2]
        parts = []
        for w, _, _ in c:
            word = re.sub(r"[,;:.…]+$", "", w).upper()
            if re.sub(r"\W", "", w).lower() in hl:
                parts.append(f"{{\\c{RED}\\3c&H000040&}}{word}{{\\c&HFFFFFF&\\3c&H000000&}}")
            else:
                parts.append(word)
        pop = "{\\pos(540,1060)\\fscx78\\fscy78\\t(0,90,\\fscx100\\fscy100)}"
        ass.append(f"Dialogue: 1,{ts(a)},{ts(b + 0.04)},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    if ln.get("label"):
        ass.append(f"Dialogue: 2,{ts(ln['t0'])},{ts(ln['t0'] + ln['d'])},Lab,,0,0,0,,"
                   f"{{\\fad(80,80)\\c{RED}}}{ln['label'].upper()}")
open(f"{WORK}/caps.ass", "w").write("\n".join(ass))

# ---------- 5. audio ----------
SR = 44100
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.6:d=0.45:r={SR}",
   "-af", "bandpass=f=1400:w=1800,afade=t=in:d=0.25:curve=exp,afade=t=out:st=0.25:d=0.2", f"{WORK}/whoosh.wav")
sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
   f"aevalsrc='0.9*sin(2*PI*(55+50*exp(-14*t))*t)*exp(-6*t)':s={SR}:d=0.9", f"{WORK}/hit.wav")
music = os.environ.get("MUSIC")
if not music:
    # soft emotional pad: I–V–vi–IV in C, 4 s per chord, warm sine stack with slow tremolo
    chords = [(261.6, 329.6, 392.0), (196.0, 246.9, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 349.2)]
    expr = []
    for ci, (a, b, c) in enumerate(chords):
        env = f"between(mod(t,16),{ci*4},{ci*4+4})"
        expr.append(f"{env}*(sin(2*PI*{a/2}*t)+0.6*sin(2*PI*{a}*t)+0.45*sin(2*PI*{b}*t)+0.35*sin(2*PI*{c}*t))")
    e = "0.12*(" + "+".join(expr) + ")*(0.8+0.2*sin(2*PI*0.5*t))"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"aevalsrc='{e}':s={SR}:d={TOTAL}",
       "-af", f"lowpass=f=2500,aecho=0.8:0.7:120|240:0.35|0.2,afade=t=in:d=1,afade=t=out:st={TOTAL-1.5}:d=1.5",
       f"{WORK}/music.wav")
    music = f"{WORK}/music.wav"
ins, fl, k = [], [], 0
def add(p, at, v):
    global k
    ins.extend(["-i", p]); ms = int(at * 1000)
    fl.append(f"[{k}:a]aresample={SR},aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[x{k}]"); k += 1
for i, ln in enumerate(lines):
    add(f"{WORK}/vo{i:02d}.wav", ln["t0"] + (0.25 if i == 0 else 0.06), 1.0)
for j, ct in enumerate(cut_times):
    if j: add(f"{WORK}/whoosh.wav", max(0, ct - 0.18), 0.22)
for ln in lines:
    if ln.get("label"): add(f"{WORK}/hit.wav", ln["t0"], 0.5)
nv = k
ins.extend(["-stream_loop", "-1", "-i", music]); mi = k; k += 1
fc = ";".join(fl) + ";" + "".join(f"[x{j}]" for j in range(nv)) + f"amix=inputs={nv}:normalize=0[fx];" \
     f"[fx]asplit[fx1][sc];[{mi}:a]aresample={SR},aformat=channel_layouts=stereo,atrim=0:{TOTAL},volume=0.5[m];" \
     f"[m][sc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[md];" \
     f"[fx1][md]amix=inputs=2:normalize=0,alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5:LRA=9[out]"
sh("ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "[out]", "-t", str(TOTAL), f"{WORK}/audio.wav")

# ---------- 6. mux ----------
final = f"{PROJ}/{os.path.basename(os.path.normpath(PROJ))}.mp4"
sh("ffmpeg", "-y", "-loglevel", "error", "-i", f"{WORK}/base.mp4", "-i", f"{WORK}/audio.wav",
   "-vf", f"ass={WORK}/caps.ass:fontsdir={FONTDIR}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
   "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final)
print("done", final, round(dur(final), 2))

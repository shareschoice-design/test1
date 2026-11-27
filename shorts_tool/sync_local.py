"""Make every finished short exist on this computer.

For each shorts/specs/hd_*.json:
  1. download the footage if missing (footage/hd/<file>.mp4, from the DVIDS page stored in footage/hd/<file>.json)
  2. build the script.json and render shorts/<name>/<name>.mp4 if missing
  3. copy the final video + upload texts into OUT (default: ../videos next to the repo, e.g. C:\\m\\bs\\videos)

Usage:  python shorts_tool/sync_local.py [OUT_DIR] [--voices <dir with en_US-*.onnx>]
Needs: python, ffmpeg, piper-tts, opencv-python-headless<5, pillow (one-time: pip install piper-tts "opencv-python-headless<5" pillow)
Safe to re-run: it only does what's missing.
"""
import json, os, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = os.path.abspath(args[0]) if args else os.path.join(os.path.dirname(REPO), "videos")
VOICES = sys.argv[sys.argv.index("--voices") + 1] if "--voices" in sys.argv else os.path.join(os.path.dirname(REPO), "tts")
os.makedirs(OUT, exist_ok=True)
PY = sys.executable


def run(cmd, env=None):
    print(" ", " ".join(cmd[:4]), "...")
    subprocess.run(cmd, check=True, cwd=REPO, env={**os.environ, **(env or {})})


specs = sorted(f[:-5] for f in os.listdir(os.path.join(REPO, "shorts", "specs")) if f.startswith("hd_") and f.endswith(".json"))
for name in specs:
    spec = json.load(open(os.path.join(REPO, "shorts", "specs", name + ".json")))
    foot = os.path.join(REPO, "footage", "hd", spec["file"] + ".mp4")
    meta = os.path.join(REPO, "footage", "hd", spec["file"] + ".json")
    final = os.path.join(REPO, "shorts", name, name + ".mp4")
    dest = os.path.join(OUT, name + ".mp4")
    if os.path.exists(dest):
        continue
    print(f"== {name}")
    try:
        if not os.path.exists(foot):
            m = json.load(open(meta))
            base = os.path.join("footage", "hd", spec["file"])
            if m.get("manual_parts"):     # Wikimedia blocks scripted downloads: use the finished mp4 sent in chat instead
                print(f"   -- {name}: footage must be downloaded by hand ({', '.join(m['manual_parts'])}); copy the finished {name}.mp4 into {OUT}")
                continue
            if m.get("compose"):            # edit of several NASA clips: [[nasa_id, start_s, dur_s], ...]
                parts = []
                for i, (nid, ss, t) in enumerate(m["compose"]):
                    part = base + f".part{i}"
                    if not os.path.exists(os.path.join(REPO, part + ".mp4")):
                        if nid.startswith("usgs:"):
                            run([PY, "shorts_tool/usgs_fetch.py", nid[5:], part])
                        else:
                            run([PY, "shorts_tool/nasa_fetch.py", nid, part, "1200"])
                    parts.append((part + ".mp4", ss, t))
                cmd = ["ffmpeg", "-y", "-loglevel", "error"]
                for f, ss, t in parts: cmd += ["-ss", str(ss), "-t", str(t), "-i", f]
                fc = "".join(f"[{i}:v]scale=1920:1080,setsar=1,fps=30[v{i}];" for i in range(len(parts)))
                fc += "".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]"
                run(cmd + ["-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-an", base + ".mp4"])
            elif m.get("usgs_page"):
                run([PY, "shorts_tool/usgs_fetch.py", m["usgs_page"], base])
            elif m.get("nasa_id"):
                run([PY, "shorts_tool/nasa_fetch.py", m["nasa_id"], base, "1200"])
            else:
                run([PY, "shorts_tool/dvids_fetch.py", m["page"], base])
        if not os.path.exists(final):
            os.makedirs(os.path.join(REPO, "shorts", name), exist_ok=True)
            run([PY, "shorts_tool/make_dvids_script.py", os.path.join("shorts", "specs", name + ".json"),
                 os.path.join("shorts", name, "script.json")], env={"FOOTDIR": "hd"})
            work = os.path.join(REPO, ".work", name)
            run([PY, "shorts_tool/build_fast.py", os.path.join("shorts", name), os.path.join("footage", "hd"), work],
                env={"VOICE_DIR": VOICES, "PIPER_MODEL": os.path.join(VOICES, "en_US-ryan-high.onnx"), "LS": "0.95"})
        shutil.copy2(final, dest)
        cred = os.path.join(REPO, "shorts", name, "CREDITS.md")
        if os.path.exists(cred):
            shutil.copy2(cred, os.path.join(OUT, name + "_CREDITS.md"))
        print(f"   -> {dest}")
    except Exception as e:
        print(f"   !! {name} failed: {e}")
shutil.copy2(os.path.join(REPO, "shorts", "YT_UPLOADS.md"), os.path.join(OUT, "YT_UPLOADS.md"))
print("done ->", OUT)

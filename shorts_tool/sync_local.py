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
            page = json.load(open(meta))["page"]
            run([PY, "shorts_tool/dvids_fetch.py", page, os.path.join("footage", "hd", spec["file"])])
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

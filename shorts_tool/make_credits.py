"""Write shorts/<name>/CREDITS.md (YouTube description block) for DVIDS-based shorts from their spec + footage metadata."""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC = {"Heartwarming": "Heartwarming", "Hitman": "Hitman", "Rising_Tide": "Rising Tide", "Sovereign": "Sovereign", "Dreamer": "Dreamer"}
for name in sys.argv[1:]:
    spec = json.load(open(f"{REPO}/shorts/specs/{name}.json"))
    meta = json.load(open(next(p for p in (f"{REPO}/footage/hd/{spec['file']}.json", f"{REPO}/footage/dvids/{spec['file']}.json") if os.path.exists(p))))
    track = next((v for k, v in MUSIC.items() if k in spec["music"]), "Heartwarming")
    hook = spec["hook"][0]
    if "NASA" in meta.get("source", ""):
        src_block = f"""Real footage: "{meta['title']}" – courtesy NASA ({meta.get('credit','NASA')})
{meta['page']}
NASA does not endorse this channel or video."""
    else:
        src_block = f"""Real footage: "{meta['title']}" – DVIDS (public domain)
{meta['page']}
The appearance of U.S. Department of Defense (DoD) visual information does not imply or constitute DoD endorsement."""
    txt = f"""# {name}

**Title idea:** {hook}... 😳

```
{spec['lines'][0][0]}

{src_block}
Music: "{track}" by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0 – http://creativecommons.org/licenses/by/4.0/

#shorts #truestory #unbroken
```
"""
    open(f"{REPO}/shorts/{name}/CREDITS.md", "w").write(txt)
    print("credits", name)

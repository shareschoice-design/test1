"""Build shorts/YT_UPLOADS.md for every rendered hd_ short: title (hook + emoji), description (story lines + credits).
Hand-polished entries already in the file are kept; new ones are appended in queue order."""
import json, os, re
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMO = [("dog", "🐶"), ("fire", "🔥"), ("sea", "🌊"), ("boat", "🌊"), ("flood", "🌊"), ("home", "🧡"), ("hug", "🧡"),
       ("cliff", "😳"), ("mountain", "🏔️"), ("helicopter", "🚁"), ("gun", "🫡"), ("plane", "✈️")]
path = f"{REPO}/shorts/YT_UPLOADS.md"
doc = open(path).read() if os.path.exists(path) else "# YouTube uploads\n"
done = set(re.findall(r"^## \d+\. (\S+)", doc, re.M))
n = len(done)
for f in sorted(os.listdir(f"{REPO}/shorts/specs")):
    name = f[:-5]
    if not name.startswith("hd_") or name in done or not os.path.exists(f"{REPO}/shorts/{name}/{name}.mp4"):
        continue
    spec = json.load(open(f"{REPO}/shorts/specs/{f}"))
    hook = spec["hook"][0]
    story = " ".join(l[0] for l in spec["lines"])
    emo = next((e for k, e in EMO if k in story.lower()), "😳")
    title = f"{hook[0].upper() + hook[1:]} {emo}"
    credits = open(f"{REPO}/shorts/{name}/CREDITS.md").read()
    block = credits.split("```")[1].strip().split("\n", 1)[1].strip()   # drop first story line, keep credits/hashtags
    n += 1
    doc += f"\n---\n\n## {n}. {name}\n**Title:** {title}\n\n**Description:**\n```\n{story}\n\nWould you have done the same? 👇\n\n{block}\n```\n"
    print("added", name)
open(path, "w").write(doc)

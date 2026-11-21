"""Print licence, author, length, resolution and download URL for Commons file pages (HTML, no API)."""
import re, sys, urllib.request, urllib.parse, html
UA = "Mozilla/5.0 (compatible; research-script)"
for name in sys.argv[1:]:
    url = "https://commons.wikimedia.org/wiki/" + name
    t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode("utf8", "replace").replace("&#95;", "_")
    lic = sorted(set(re.findall(r'class="licensetpl_short[^"]*"[^>]*>([^<]+)<', t)))
    info = re.search(r'class="fileInfo">\(([^)]*)\)', t)
    dl = re.search(r'href="(https://upload\.wikimedia\.org/wikipedia/commons/[0-9a-f]/[0-9a-f]{2}/[^"]+)"', t)
    au = re.search(r'id="fileinfotpl_aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', t, re.S)
    author = re.sub(r"<[^>]+>", "", au.group(1)).strip()[:80] if au else "?"
    print(f"{urllib.parse.unquote(name)}\n  licence: {lic}\n  info: {html.unescape(info.group(1)) if info else '?'}\n  author: {html.unescape(author)}\n  url: {dl.group(1) if dl else '?'}")

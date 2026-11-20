#!/usr/bin/env python3
"""Build the paid app page (server/kitsu/app_html.php) and the local copy (kitsu-oracle.html) from anime.html.
The app's script is minified with terser so the method isn't readable at a glance.
Usage: python3 server/build_app.py /path/to/terser"""
import re, subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
terser = sys.argv[1]
src = (root / 'anime.html').read_text()
i = src.index('</style>') + len('</style>')
head, body = src[:i], src[i:]
m = re.search(r'<script>\n(.*?)\n</script>', body, re.S)
js = subprocess.run([terser, '--compress', 'passes=2', '--mangle', '--toplevel'], input=m.group(1), capture_output=True, text=True, check=True).stdout
body_min = body[:m.start()] + '<script>' + js + '</script>' + body[m.end():]
doc = lambda b, extra='': '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + head + '\n</head>\n<body>' + extra + b + '\n</body>\n</html>\n'
logout = ('<a href="logout.php" style="position:fixed;top:max(10px,env(safe-area-inset-top,0px));right:max(12px,env(safe-area-inset-right,0px));z-index:9;'
          'color:#b9a8d9;font:800 12px \'M PLUS Rounded 1c\',sans-serif;text-decoration:none;border:2px solid #3b2470;border-radius:999px;padding:4px 10px;background:rgba(18,10,36,.85)">Log out</a>')
(root / 'server/kitsu/app_html.php').write_text("<?php if(!defined('KITSU')){http_response_code(403);exit;} ?>\n" + doc(body_min, logout))
(root / 'kitsu-oracle.html').write_text(doc(body))
print('built, script', len(m.group(1)), '->', len(js), 'bytes')

#!/usr/bin/env python3
"""
Build a single-file self-contained index.html with CSS + JS inlined.
Eliminates any external file load failure (Tailscale quirks, iOS Safari caching, etc).
"""
import re
from pathlib import Path

STATIC = Path(__file__).parent.parent / "static"
HTML_IN = STATIC / "index-split.html"   # always rebuild from the clean source
CSS = (STATIC / "style.css").read_text()
JS  = (STATIC / "app.js").read_text()
HTML = HTML_IN.read_text()

# Strip the external CSS link and Google Fonts link
HTML = re.sub(
    r'\s*<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*<link href="https://fonts\.googleapis\.com[^"]*"[^>]*>\s*',
    '\n',
    HTML
)
HTML = re.sub(
    r'\s*<link rel="stylesheet" href="style\.css">\s*',
    '\n',
    HTML
)
HTML = re.sub(
    r'\s*<link rel="stylesheet" href="app\.css">\s*',
    '\n',
    HTML
)
HTML = re.sub(
    r'\s*<script src="app\.js"></script>\s*',
    '\n',
    HTML
)

# Inject inlined CSS + JS
inline_css = f"\n<style id=\"inline-css\">\n{CSS}\n</style>\n"
inline_js  = f"\n<script id=\"inline-js\">\n{JS}\n</script>\n"

# Insert CSS at end of <head>, JS at end of <body>
HTML = HTML.replace('</head>', inline_css + '</head>')
HTML = HTML.replace('</body>', inline_js + '</body>')

# Add cache-busting meta
HTML = HTML.replace(
    '<meta name="theme-color"',
    '<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">\n'
    '<meta http-equiv="Pragma" content="no-cache">\n'
    '<meta http-equiv="Expires" content="0">\n'
    '<meta name="theme-color"'
)

# Write
out = STATIC / "index-inline.html"
out.write_text(HTML)
print(f"OK: built {out} ({out.stat().st_size / 1024:.1f} KB)")

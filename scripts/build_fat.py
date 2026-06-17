#!/usr/bin/env python3
"""Build self-contained index.html with data embedded — zero fetches needed."""
import json, re, gzip
from pathlib import Path

STATIC = Path(__file__).parent.parent / 'static'
html = (STATIC / 'index-split.html').read_text()
css  = (STATIC / 'style.css').read_text()
js   = (STATIC / 'app.js').read_text()
data = json.loads((STATIC / 'models.json').read_text())

# Strip external links
html = re.sub(r'<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*<link href="https://fonts\.googleapis\.com[^"]*"[^>]*>\s*', '\n', html)
html = re.sub(r'\s*<link rel="stylesheet" href="style\.css">\s*', '\n', html)
html = re.sub(r'\s*<script src="app\.js"></script>\s*', '\n', html)

# Inject CSS at end of head
html = html.replace('</head>', f'\n<style id="inline-css">\n{css}\n</style>\n</head>')

# Inject data + JS at end of body (single replacement to avoid missing </body>)
data_json = json.dumps(data, separators=(',', ':'))
html = html.replace('</body>',
    f'\n<script id="inline-data">var __LLM_TRACKER_DATA__={data_json};</script>' +
    f'\n<script id="inline-js">\n{js}\n</script>\n</body>')

# Cache headers
html = html.replace('<meta name="theme-color"',
    '<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">\n'
    '<meta http-equiv="Pragma" content="no-cache">\n'
    '<meta http-equiv="Expires" content="0">\n'
    '<meta name="theme-color"')

out = STATIC / 'index.html'
out.write_text(html)
print(f'OK: {out} ({out.stat().st_size / 1024:.1f} KB)')
gz = gzip.compress(html.encode(), 9)
print(f'    gzipped: {len(gz) / 1024:.1f} KB')
print(f'    data: {data["model_count"]} models, {data["provider_count"]} providers, {data["free_model_count"]} free')
print(f'    has data: {"__LLM_TRACKER_DATA__" in html}')
print(f'    has js:   {"inline-js" in html}')

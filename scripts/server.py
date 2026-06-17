import gzip, json, mimetypes, os, subprocess, sys, threading, time
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path('/home/ryancalpin/workspace/llm-tracker/static')
PORT = 8765
HOST = '0.0.0.0'  # bind all interfaces so Tailscale can reach us
REFRESH_SCRIPT = Path('/home/ryancalpin/workspace/llm-tracker/scripts/refresh.sh')
STATE_FILE = ROOT / 'sync_state.json'

_cache_lock = threading.Lock()
_models_cache = None
_models_mtime = 0
_html_cache = None
_html_mtime = 0
_sync_lock = threading.Lock()
_syncing = False

def load_models():
    global _models_cache, _models_mtime
    p = ROOT / 'models.json'
    if not p.exists(): return b'{"error":"models.json missing"}'
    mtime = p.stat().st_mtime
    with _cache_lock:
        if _models_cache is None or mtime != _models_mtime:
            _models_cache = p.read_bytes()
            _models_mtime = mtime
    return _models_cache

def load_index():
    global _html_cache, _html_mtime
    src = ROOT / 'index.html'
    if not src.exists(): return b'<h1>Build failed</h1>'
    mtime = src.stat().st_mtime
    with _cache_lock:
        if _html_cache is None or mtime != _html_mtime:
            _html_cache = src.read_bytes()
            _html_mtime = mtime
    return _html_cache

def load_state():
    if not STATE_FILE.exists(): return {'last_sync_at':None,'last_sync_status':'never','syncing':False,'history':[]}
    try: return json.loads(STATE_FILE.read_text())
    except: return {'last_sync_at':None,'last_sync_status':'error','syncing':False,'history':[]}

def save_state(state): STATE_FILE.write_text(json.dumps(state, indent=2))

def trigger_sync():
    global _syncing
    with _sync_lock:
        if _syncing: return {'status': 'already_running'}
        _syncing = True
    state = load_state()
    state['syncing'] = True
    state['sync_started_at'] = datetime.now(timezone.utc).isoformat()
    state['sync_trigger'] = 'manual'
    save_state(state)
    def worker():
        global _syncing, _models_cache, _models_mtime
        try:
            env = os.environ.copy(); env['LLM_TRACKER_SYNC_TRIGGER'] = 'manual'
            result = subprocess.run(['bash', str(REFRESH_SCRIPT)], capture_output=True, text=True, timeout=120, env=env)
            ns = load_state()
            ns['syncing'] = False
            ns['last_sync_at'] = datetime.now(timezone.utc).isoformat()
            ns['last_sync_status'] = 'ok' if result.returncode == 0 else 'error'
            ns['last_sync_stdout_tail'] = (result.stdout or '')[-2000:]
            if result.returncode != 0: ns['last_sync_stderr_tail'] = (result.stderr or '')[-2000:]
            h = ns.get('history', [])
            h.append({'at': ns['last_sync_at'], 'status': ns['last_sync_status'], 'trigger': ns.get('sync_trigger', 'manual')})
            ns['history'] = h[-20:]
            save_state(ns)
        except Exception as e:
            ns = load_state()
            ns['syncing'] = False
            ns['last_sync_at'] = datetime.now(timezone.utc).isoformat()
            ns['last_sync_status'] = 'error'
            ns['last_sync_error'] = str(e)
            save_state(ns)
        finally:
            with _sync_lock: _syncing = False
            with _cache_lock: _models_cache = None; _models_mtime = 0
    t = threading.Thread(target=worker, daemon=True); t.start()
    return {'status': 'started'}

GZIP_TYPES = {'text/html','text/css','text/javascript','application/javascript','application/json','image/svg+xml'}

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args): sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {self.address_string()} {fmt % args}\n")
    def end_headers(self):
        if self.path.startswith('/api/'):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    def do_OPTIONS(self): self.send_response(204); self.end_headers()
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/status': return self._json(load_state())
        if path == '/api/health': return self._json({'ok': True})
        if path == '/models.json': return self._send(load_models(), 'application/json', 0)
        if path in ('/', '/index.html'): return self._send(load_index(), 'text/html; charset=utf-8', 0)
        return super().do_GET()
    def do_POST(self):
        if self.path.split('?')[0] == '/api/refresh': return self._json(trigger_sync())
        self.send_error(404)
    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        if 'gzip' in self.headers.get('Accept-Encoding', ''): body = gzip.compress(body)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        if 'gzip' in self.headers.get('Accept-Encoding', ''): self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)
    def _send(self, body, ct, max_age=0):
        ae = self.headers.get('Accept-Encoding', '')
        if 'gzip' in ae and ct.split(';')[0].strip() in GZIP_TYPES:
            body = gzip.compress(body)
            self.send_response(200)
            self.send_header('Content-Type', ct)
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Vary', 'Accept-Encoding')
        else:
            self.send_response(200)
            self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(body)))
        if max_age == 0:
            self.send_header('Cache-Control', 'no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
        self.end_headers()
        self.wfile.write(body)

class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

os.chdir(ROOT)
print(f'[server] {ROOT} on http://{HOST}:{PORT} (threaded, gzip, cached)')
s = Server((HOST, PORT), Handler)
try: s.serve_forever()
except KeyboardInterrupt: s.shutdown()

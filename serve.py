import http.server
import os
import sys
import urllib.request
import urllib.error

DIST = os.path.join(os.path.dirname(__file__), 'ecoscan_frontend', 'dist')
PORT = 3000
BACKEND = 'http://127.0.0.1:8000'


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def _proxy(self):
        url = BACKEND + self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else None

        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ('host', 'connection')}

        req = urllib.request.Request(url, data=body, headers=headers, method=self.command)

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(resp.status)
            for key, val in resp.getheaders():
                if key.lower() not in ('transfer-encoding', 'connection'):
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, val in e.headers.items():
                if key.lower() not in ('transfer-encoding', 'connection'):
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"Backend unreachable"}')

    def do_GET(self):
        if self.path.startswith('/api/') or self.path.startswith('/media/'):
            return self._proxy()
        path = self.translate_path(self.path)
        if not os.path.exists(path) or (os.path.isdir(path) and not os.path.exists(os.path.join(path, 'index.html'))):
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            return self._proxy()
        self.send_response(404)
        self.end_headers()

    def do_PATCH(self):
        if self.path.startswith('/api/'):
            return self._proxy()
        self.send_response(404)
        self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/api/'):
            return self._proxy()
        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            return self._proxy()
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def log_message(self, format, *args):
        pass


print(f'SPA server running on http://localhost:{PORT}')
print(f'Proxying /api/ and /media/ to {BACKEND}')
http.server.HTTPServer(('', PORT), SPAHandler).serve_forever()

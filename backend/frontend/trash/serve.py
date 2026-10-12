from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        return super().end_headers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '6006'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'frontend serving at http://127.0.0.1:{port}')
    server.serve_forever()

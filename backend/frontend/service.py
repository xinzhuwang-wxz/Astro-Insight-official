#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ancient_backend import build_payload
from dim_backend import build_dimensionality_payload
from stellar_backend import build_stellar_analysis_payload

BASE_DIR = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/dim-reduction':
            payload = build_dimensionality_payload()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            return
        if parsed.path == '/api/stellar-analysis':
            payload = build_stellar_analysis_payload()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        return super().end_headers()


def main() -> int:
    port = int(os.environ.get('PORT', '6006'))
    try:
        build_payload()
        build_dimensionality_payload()
        build_stellar_analysis_payload()
        os.chdir(BASE_DIR)
        server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

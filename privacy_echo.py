#!/usr/bin/env python3
"""Minimal signed echo endpoint for privacy checks."""

import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

SECRET = os.environ.get("ECHO_SECRET", "")
PORT = int(os.environ.get("ECHO_PORT", "8088"))
HEADER_NAMES = {"x-forwarded-for", "x-real-ip", "forwarded", "via", "client-ip", "true-client-ip", "x-client-ip", "x-proxyuser-ip", "cf-connecting-ip", "x-privacy-probe"}

def signature(nonce, client_ip, headers):
    canonical = json.dumps(headers, sort_keys=True, separators=(",", ":"))
    return hmac.new(SECRET.encode(), (nonce + "\n" + client_ip + "\n" + canonical).encode(), hashlib.sha256).hexdigest()

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        path = urlsplit(self.path).path
        if not path.startswith("/p/") or len(path) <= 3:
            self.send_error(404)
            return
        nonce = unquote(path[3:])
        client_ip = self.client_address[0]
        headers = {key.lower(): value for key, value in self.headers.items() if key.lower() in HEADER_NAMES}
        payload = {"nonce": nonce, "client_ip": client_ip, "headers": headers, "signature": signature(nonce, client_ip, headers)}
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return

if __name__ == "__main__":
    if not SECRET:
        raise SystemExit("ECHO_SECRET must be set")
    ThreadingHTTPServer(("0.0.0.0", PORT), EchoHandler).serve_forever()

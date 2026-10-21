"""Minimal local NetworkLab Infrastructure API. Read-only; no VM or host mutations."""
from __future__ import annotations
import json
import os
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8512
ALLOWED_ORIGINS = {"http://127.0.0.1:8510", "http://127.0.0.1:8511"}

def payload() -> dict[str, str]:
    return {"status":"ok","service":"NetworkLab-INFRA","platform":platform.system(),"python":platform.python_version(),"runtime":"python-standard-library","virtual_machines_required":"false","mode":"read-only"}

class Handler(BaseHTTPRequestHandler):
    server_version = "NetworkLab-INFRA/1.0"
    def send_json(self, status: int, data: dict) -> None:
        body=json.dumps(data,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        origin=self.headers.get("Origin","")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin",origin)
            self.send_header("Vary","Origin")
        self.send_header("Access-Control-Allow-Methods","GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
        self.wfile.write(body)
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        origin=self.headers.get("Origin","")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin",origin)
            self.send_header("Vary","Origin")
        self.send_header("Access-Control-Allow-Methods","GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.send_header("Content-Length","0")
        self.end_headers()
    def do_GET(self) -> None:
        route=urlparse(self.path).path
        if route in ("/api/health","/healthz"):
            self.send_json(200,{"status":"ok","service":"NetworkLab-INFRA"})
        elif route=="/api/status":
            self.send_json(200,payload())
        elif route=="/":
            try:
                with open(os.path.join(os.path.dirname(__file__),"index.html"),"rb") as f: body=f.read()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(body)))
                self.send_header("Cache-Control","no-store")
                self.end_headers()
                self.wfile.write(body)
            except OSError:
                self.send_json(500,{"status":"error","error":"Infrastructure UI unavailable"})
        else:
            self.send_json(404,{"status":"error","error":"Route not found"})
    def log_message(self, fmt: str, *args: object) -> None:
        print("[NetworkLab-INFRA] "+(fmt % args))

def main() -> None:
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    print(f"NetworkLab INFRA: http://{HOST}:{PORT}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=="__main__": main()

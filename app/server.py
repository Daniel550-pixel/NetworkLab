from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
from urllib.parse import urlparse

from app.services.evidence_service import get_evidence
from app.services.health_service import get_health
from app.services.network_service import get_state

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
HOST = "127.0.0.1"
PORT = int(os.environ.get("NETWORKLAB_PORT", "8501"))


def json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")


class NetworkLabHandler(BaseHTTPRequestHandler):
    server_version = "NetworkLab/1.0"

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, "application/json; charset=utf-8", json_bytes(payload))

    def _file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self._json(HTTPStatus.NOT_FOUND, {"error": "Resource not found"})
            return
        self._send(HTTPStatus.OK, content_type, path.read_bytes())

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        try:
            if route in ("/", "/index.html"):
                self._file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
            elif route == "/app.css":
                self._file(WEB_ROOT / "app.css", "text/css; charset=utf-8")
            elif route == "/app.js":
                self._file(WEB_ROOT / "app.js", "text/javascript; charset=utf-8")
            elif route == "/api/state":
                self._json(HTTPStatus.OK, get_state())
            elif route == "/api/health":
                self._json(HTTPStatus.OK, get_health())
            elif route == "/api/evidence":
                self._json(HTTPStatus.OK, get_evidence())
            elif route == "/api/status":
                health = get_health()
                state = get_state()
                adapters = state.get("adapters", []) if isinstance(state, dict) else []
                connectivity_ok = bool(health.get("connectivity_ok"))
                services_ok = bool(health.get("services_ok"))
                self._json(
                    HTTPStatus.OK,
                    {
                        "operational": connectivity_ok and services_ok,
                        "connectivity_ok": connectivity_ok,
                        "services_ok": services_ok,
                        "interfaces": len(adapters) if isinstance(adapters, list) else 0,
                    },
                )
            elif route == "/healthz":
                self._json(HTTPStatus.OK, {"status": "ok"})
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
        except Exception as exc:
            self._json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": str(exc), "type": type(exc).__name__},
            )

    def log_message(self, format: str, *args: object) -> None:
        print(f"[NetworkLab] {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), NetworkLabHandler)
    print(f"NetworkLab local server: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping NetworkLab.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

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
from app.services.virtualization_service import create_virtual_network, get_virtual_network
from app.services.vm_service import create_vm_topology, get_vm_runtime, get_vm_topology, vm_action
from app.services.storage_service import attach_vm_iso, create_vm_storage, eject_vm_iso, get_vm_storage

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

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        try:
            body = {}
            length = int(self.headers.get("Content-Length", "0"))
            if length:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("Request body must be a JSON object.")

            if route == "/api/virtual-network/create":
                self._json(HTTPStatus.OK, create_virtual_network())
            elif route == "/api/vms/create":
                self._json(HTTPStatus.OK, create_vm_topology())
            elif route == "/api/vms/storage/create":
                self._json(HTTPStatus.OK, create_vm_storage())
            elif route.startswith("/api/vms/") and route.endswith("/iso"):
                parts = route.split("/")
                if len(parts) != 5:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "Invalid VM ISO route"})
                    return
                from urllib.parse import unquote
                name = unquote(parts[3])
                if body.get("action") == "eject":
                    self._json(HTTPStatus.OK, eject_vm_iso(name))
                else:
                    iso_path = str(body.get("path", "")).strip()
                    if not iso_path:
                        raise ValueError("ISO path is required.")
                    self._json(HTTPStatus.OK, attach_vm_iso(name, iso_path))
            elif route.startswith("/api/vms/"):
                parts = route.split("/")
                if len(parts) != 5 or parts[4] not in {"start", "stop", "poweroff"}:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "Invalid VM action route"})
                    return
                from urllib.parse import unquote
                self._json(HTTPStatus.OK, vm_action(unquote(parts[3]), parts[4]))
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
        except Exception as exc:
            self._json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": str(exc), "type": type(exc).__name__},
            )

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
            elif route == "/api/virtual-network":
                self._json(HTTPStatus.OK, get_virtual_network())
            elif route == "/api/vms":
                self._json(HTTPStatus.OK, get_vm_topology())
            elif route == "/api/vms/storage":
                self._json(HTTPStatus.OK, get_vm_storage())
            elif route.startswith("/api/vms/") and route.endswith("/runtime"):
                parts = route.split("/")
                if len(parts) != 5:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "Invalid VM runtime route"})
                    return
                from urllib.parse import unquote
                self._json(HTTPStatus.OK, get_vm_runtime(unquote(parts[3])))
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
                        "virtual_network": get_virtual_network(),
                        "vms": get_vm_topology(),
                        "vm_storage": get_vm_storage(),
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

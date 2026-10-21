from __future__ import annotations
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from apps.infra.server import Handler, payload


class InfrastructureApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get_json(self, path: str, origin: str | None = None):
        headers = {"Origin": origin} if origin else {}
        request = Request(self.base + path, headers=headers)
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8")), response.headers

    def test_payload_is_read_only_and_has_no_vm_dependency(self):
        result = payload()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "read-only")
        self.assertEqual(result["virtual_machines_required"], "false")

    def test_health_endpoint(self):
        status, data, _ = self.get_json("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")

    def test_status_endpoint(self):
        status, data, _ = self.get_json("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(data["service"], "NetworkLab-INFRA")
        self.assertIn("python", data)

    def test_client_and_management_origins_are_allowed(self):
        for origin in ("http://127.0.0.1:8510", "http://127.0.0.1:8511"):
            with self.subTest(origin=origin):
                _, _, headers = self.get_json("/api/health", origin)
                self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)

    def test_unknown_route_returns_404(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(self.base + "/does-not-exist", timeout=3)
        self.assertEqual(raised.exception.code, 404)


if __name__ == "__main__":
    unittest.main()

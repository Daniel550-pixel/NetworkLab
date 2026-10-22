from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WebAppSmokeTests(unittest.TestCase):
    def test_all_three_web_app_entrypoints_exist(self):
        expected = (
            ROOT / "apps" / "client" / "index.html",
            ROOT / "apps" / "mgmt" / "index.html",
            ROOT / "apps" / "infra" / "index.html",
        )
        for path in expected:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertTrue(path.is_file(), f"Missing web app entrypoint: {path}")

    def test_management_links_point_to_expected_local_ports(self):
        page = (ROOT / "apps" / "mgmt" / "index.html").read_text(encoding="utf-8")
        for url in (
            "http://127.0.0.1:8510",
            "http://127.0.0.1:8512",
        ):
            with self.subTest(url=url):
                self.assertIn(url, page)

    def test_infrastructure_server_is_loopback_only_and_read_only(self):
        server = (ROOT / "apps" / "infra" / "server.py").read_text(encoding="utf-8")
        self.assertIn('HOST = "127.0.0.1"', server)
        self.assertIn("def do_GET(self)", server)
        self.assertIn("def do_OPTIONS(self)", server)
        self.assertNotIn("subprocess.", server)
        self.assertNotIn("os.system(", server)

    def test_frontends_do_not_depend_on_external_cdn_assets(self):
        for relative in (
            "apps/client/index.html",
            "apps/mgmt/index.html",
            "apps/infra/index.html",
        ):
            page = (ROOT / relative).read_text(encoding="utf-8").lower()
            with self.subTest(path=relative):
                self.assertNotIn("https://cdn.", page)
                self.assertNotIn("https://unpkg.com/", page)
                self.assertNotIn("https://cdnjs.cloudflare.com/", page)


if __name__ == "__main__":
    unittest.main()

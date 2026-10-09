import csv
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
PORTAL = ROOT / "docs" / "_site" / "index.html"
INVENTORY = ROOT / "docs" / "_site" / "documentation-inventory.csv"
PAGES_DIR = ROOT / "docs" / "_site" / "pages"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def _local_target(source_file: Path, href: str):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path)
    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return (source_file.parent / path).resolve()


def _assert_local_links_resolve(source_file: Path):
    parser = LinkParser()
    parser.feed(source_file.read_text(encoding="utf-8-sig"))
    broken = []
    for href in parser.hrefs:
        target = _local_target(source_file, href)
        if target is not None and not target.exists():
            broken.append(f"{href} -> {target}")
    assert not broken, (
        f"Broken local links in {source_file.relative_to(ROOT)}:\n"
        + "\n".join(broken)
    )


def test_documentation_portal_links_resolve():
    assert PORTAL.is_file()
    assert PAGES_DIR.is_dir()
    sources = [PORTAL, *sorted(PAGES_DIR.glob("*.html"))]
    assert sources, "Expected generated HTML pages in the documentation portal."
    for source in sources:
        _assert_local_links_resolve(source)


def test_documentation_inventory_html_targets_resolve():
    with INVENTORY.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows, "Documentation inventory is empty."
    for row in rows:
        html_view = (row.get("HTMLWeergave") or "").strip()
        if not html_view:
            continue
        target = _local_target(INVENTORY, html_view)
        assert target is not None and target.is_file(), (
            f"Broken HTMLWeergave for {row.get('Bestand')}: {html_view}"
        )

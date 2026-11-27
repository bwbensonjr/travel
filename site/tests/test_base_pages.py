import re

import pytest

from helpers import html_errors
from sitegen.builder import build


@pytest.fixture(scope="module")
def built(site_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build(site_dir, out)
    return out


def test_index_lists_trip(built):
    html = (built / "index.html").read_text()
    assert 'href="2027-ireland/"' in html
    assert "Wild British Isles" in html


def test_every_page_noindex_and_well_formed(built):
    pages = list(built.rglob("*.html"))
    assert pages
    for page in pages:
        html = page.read_text()
        assert '<meta name="robots" content="noindex, nofollow">' in html, page
        assert html_errors(html) == [], page


def test_output_allowlist(built):
    allowed = {".html", ".css", ".js", ".json", ".webmanifest", ".png", ".svg", ".txt"}
    files = [p for p in built.rglob("*") if p.is_file()]
    bad = [p.relative_to(built).as_posix() for p in files
           if p.suffix not in allowed and p.name not in ("LICENSE", "VERSION")]
    assert bad == []
    assert not [p for p in files if p.suffix in (".docx", ".md", ".csv", ".py", ".geojson")]
    assert not (built / "scripts").exists()


def test_robots_txt(built):
    assert (built / "robots.txt").read_text() == "User-agent: *\nDisallow: /\n"


def test_base_template_has_manifest_status_and_date(built):
    html = (built / "index.html").read_text()
    assert 'rel="manifest" href="manifest.webmanifest"' in html
    assert 'id="offline-status"' in html
    assert re.search(r"Data as of \w{3} \d{1,2}, \d{4}", html)

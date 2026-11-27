import json
import re

import pytest

from sitegen.builder import build


@pytest.fixture(scope="module")
def built(site_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build(site_dir, out)
    return out


def precache(built):
    sw = (built / "sw.js").read_text()
    return json.loads(re.search(r"const PRECACHE = (\[.*?\]);", sw, re.S).group(1)), sw


def test_precache_covers_trip(built):
    urls, sw = precache(built)
    for n in range(1, 13):
        assert f"2027-ireland/day/{n}/" in urls
    for u in ("./", "2027-ireland/", "2027-ireland/trip.json", "offline/",
              "static/vendor/leaflet/leaflet.js", "static/vendor/leaflet/leaflet.css",
              "static/map.js", "static/day.js", "static/app.js", "static/tokens.css",
              "manifest.webmanifest", "static/icons/icon-192.png"):
        assert u in urls, u
    assert "sw.js" not in urls and "robots.txt" not in urls
    # Every precached URL exists in the output.
    for u in urls:
        path = built / (u + "index.html" if u.endswith("/") or u == "./" else u)
        assert path.exists(), u


def test_sw_version_matches_pages(built):
    _, sw = precache(built)
    version = re.search(r'const VERSION = "([0-9a-f]+)";', sw).group(1)
    assert f'data-build="{version}"' in (built / "2027-ireland" / "index.html").read_text()


def test_version_changes_with_data(site_dir, repo_root, tmp_path):
    import shutil
    data = tmp_path / "trip"
    shutil.copytree(repo_root / "2027-ireland", data, ignore=shutil.ignore_patterns("*.docx", "*.webp", "scripts"))
    site = tmp_path / "site"
    shutil.copytree(site_dir, site, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (site / "site.yaml").write_text("title: T\ntrips:\n  - {slug: t, title: T, dates: d, data_dir: trip}\n")
    build(site, tmp_path / "a", repo_root=tmp_path)
    csv = data / "excursions.csv"
    csv.write_text(csv.read_text().replace(",129,", ",135,", 1))
    build(site, tmp_path / "b", repo_root=tmp_path)
    va = re.search(r'VERSION = "(\w+)"', (tmp_path / "a" / "sw.js").read_text()).group(1)
    vb = re.search(r'VERSION = "(\w+)"', (tmp_path / "b" / "sw.js").read_text()).group(1)
    assert va != vb


def test_offline_page_links_to_trip_pages(built):
    html = (built / "offline" / "index.html").read_text()
    assert 'href="../2027-ireland/"' in html
    for n in range(1, 13):
        assert f'href="../2027-ireland/day/{n}/"' in html


def test_manifest(built):
    m = json.loads((built / "manifest.webmanifest").read_text())
    assert m["start_url"] == "2027-ireland/"
    assert m["display"] == "standalone"
    sizes = {i["sizes"] for i in m["icons"]}
    assert {"192x192", "512x512"} <= sizes
    for i in m["icons"]:
        assert (built / i["src"]).exists()


def test_pages_register_service_worker(built):
    for page in ("index.html", "2027-ireland/index.html", "2027-ireland/day/3/index.html"):
        assert "static/app.js" in (built / page).read_text()

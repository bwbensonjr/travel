import json
import re

import pytest

from sitegen.builder import build


@pytest.fixture(scope="module")
def built(site_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build(site_dir, out)
    return out


def test_trip_json_references_resolve(built):
    data = json.loads((built / "2027-ireland" / "trip.json").read_text())
    places = [f for f in data["geojson"]["features"] if f["properties"]["kind"] == "place"]
    assert len(places) == 327
    assert all(f["properties"]["id"] for f in places)
    for f in places:
        for eid in f["properties"]["excursion_ids"]:
            assert eid in data["excursions"], (f["properties"]["name"], eid)
    assert [d["day"] for d in data["days"]] == list(range(1, 13))
    assert {c["key"] for c in data["categories"]} >= {f["properties"]["category"] for f in places}


def test_map_page_links_to_day_pages(built):
    html = (built / "2027-ireland" / "index.html").read_text()
    links = re.findall(r'href="([^"]+)"', html)
    assert not [h for h in links if h.endswith(".md")]
    for n in range(1, 13):
        assert f'href="day/{n}/"' in html
    assert "static/vendor/leaflet/leaflet.js" in html
    assert "cdnjs" not in html and "unpkg" not in html


def test_map_script_links_use_site_urls(site_dir):
    js = (site_dir / "static" / "map.js").read_text()
    assert ".md" not in js
    assert re.search(r'day/" \+ e\.day \+\s*"/#exc-"', js)

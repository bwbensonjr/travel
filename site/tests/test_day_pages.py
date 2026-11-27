import re
import shutil

import pytest

from sitegen.builder import build


@pytest.fixture(scope="module")
def built(site_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build(site_dir, out)
    return out


def page(built, n):
    return (built / "2027-ireland" / "day" / str(n) / "index.html").read_text()


def summary_block(html):
    return html.split('<section class="day-summary"', 1)[1].split("</section>", 1)[0]


def test_all_twelve_days_exist(built):
    for n in range(1, 13):
        assert (built / "2027-ireland" / "day" / str(n) / "index.html").exists()


def test_day5_summary_first(built):
    html = page(built, 5)
    s = summary_block(html)
    assert "Day 5 · Jun 26, 2027" in s
    assert "Dun Laoghaire (Dublin)" in s
    assert "<strong>7:00 AM</strong>" in s and "<strong>7:00 PM</strong>" in s
    assert "Tender required" in s and "Wheelchair access limited" in s
    # Summary comes before the port description.
    assert html.index('class="day-summary"') < html.index('class="prose about"')


def test_day2_sea_day(built):
    s = summary_block(page(built, 2))
    assert "Day 2 · Jun 23, 2027" in s
    assert "At sea" in s
    assert "Arrive" not in s and "Depart" not in s


def test_day3_places_grouped_with_map_links(built):
    html = page(built, 3)
    m = re.search(r'<a href="\.\./\.\./\?place=d3-callanish-standing-stones">Callanish Standing Stones</a>', html)
    assert m, "Callanish standing stones link not found"
    group = html[:m.start()].rsplit("<h4>", 1)[1]
    assert "Historic sites" in group


def test_day4_excursions_collapsed(built):
    html = page(built, 4)
    details = re.findall(r'<details class="exc" id="exc-(\d+)"( open)?>', html)
    assert len(details) == 18
    assert all(not open_ for _, open_ in details)
    causeway = html.split("The Giant&#39;s Causeway</span>", 1)[1].split("</details>", 1)[0]
    for label in ("Minimum age", "Meals", "Wheelchair accessible", "Holland America page"):
        assert label in causeway


def test_day9_distinct_excursion_ids_and_two_stops(built):
    html = page(built, 9)
    assert 'id="exc-99005"' in html and 'id="exc-99011"' in html
    assert html.count('class="stop-heading"') == 2
    assert "Scenic cruising Cliffs of Moher" in html


def test_day_navigation(built):
    d1, d6, d12 = page(built, 1), page(built, 6), page(built, 12)
    assert 'rel="prev"' not in d1 and 'href="../2/" rel="next"' in d1
    assert 'href="../7/" rel="next"' in d6 and 'href="../5/" rel="prev"' in d6
    assert 'rel="next"' not in d12
    assert 'href="../../">Map</a>' in d6


def test_notes_rendered(repo_root, site_dir, tmp_path):
    data = tmp_path / "trip"
    shutil.copytree(repo_root / "2027-ireland", data,
                    ignore=shutil.ignore_patterns("*.docx", "*.webp", "scripts"))
    day3 = data / "day-03-stornoway.md"
    day3.write_text(day3.read_text() + "\n## Our research\n\nCallanish predates Stonehenge's sarsens.\n")
    site = tmp_path / "site"
    shutil.copytree(site_dir, site, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (site / "site.yaml").write_text("title: T\ntrips:\n  - {slug: t, title: T, dates: d, data_dir: trip}\n")
    out = tmp_path / "out"
    build(site, out, repo_root=tmp_path)
    html = (out / "t" / "day" / "3" / "index.html").read_text()
    assert '<h2 id="notes-title">Notes</h2>' in html
    assert "Our research" in html and "predates Stonehenge" in html


def test_price_only_in_expanded_details(built):
    html = page(built, 4)
    metas = re.findall(r'<span class="exc-meta">([^<]*)</span>', html)
    assert len(metas) == 18
    assert not [m for m in metas if "$" in m]
    causeway = html.split('<span class="exc-title">The Giant&#39;s Causeway</span>', 1)[1].split("</details>", 1)[0]
    summary, body = causeway.split("</summary>", 1)
    assert "$" not in summary
    assert "6 Hours · Moderate" in summary
    assert '<th scope="row">Starting at</th><td>$179</td>' in body


def stop_sections(html):
    return html.split('<section class="stop"')[1:]


def test_day4_places_before_excursions(built):
    html = page(built, 4)
    about = html.index('class="prose about"')
    places = html.index('<details class="places">')
    excursions = html.index(">Shore excursions <")
    assert about < places < excursions


def test_day9_each_stop_orders_places_first(built):
    galway, cliffs = stop_sections(page(built, 9))
    assert "Galway, Ireland" in galway
    assert galway.index('<details class="places">') < galway.index(">Shore excursions <")
    assert "Scenic cruising Cliffs of Moher" in cliffs
    assert '<details class="places">' in cliffs
    assert "Shore excursions" not in cliffs


def test_stop_without_places_shows_excursions_after_description(repo_root, site_dir, tmp_path):
    import json

    data = tmp_path / "trip"
    shutil.copytree(repo_root / "2027-ireland", data,
                    ignore=shutil.ignore_patterns("*.docx", "*.webp", "scripts"))
    geo = data / "places.geojson"
    fc = json.loads(geo.read_text())
    fc["features"] = [f for f in fc["features"]
                      if not (f["properties"]["kind"] == "place" and f["properties"]["day"] == 3)]
    geo.write_text(json.dumps(fc))
    site = tmp_path / "site"
    shutil.copytree(site_dir, site, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (site / "site.yaml").write_text("title: T\ntrips:\n  - {slug: t, title: T, dates: d, data_dir: trip}\n")
    out = tmp_path / "out"
    build(site, out, repo_root=tmp_path)
    (stop,) = stop_sections((out / "t" / "day" / "3" / "index.html").read_text())
    assert '<details class="places">' not in stop
    between = stop.split('class="prose about"', 1)[1].split(">Shore excursions <", 1)[0]
    assert "<details" not in between and "<h3" in between

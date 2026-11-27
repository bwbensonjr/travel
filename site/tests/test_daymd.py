from sitegen.daymd import parse_day_file


def test_day3_single_stop(repo_root):
    doc = parse_day_file(repo_root / "2027-ireland" / "day-03-stornoway.md")
    assert doc.day == 3
    assert len(doc.stops) == 1
    stop = doc.stops[0]
    assert stop.port_id == "STW"
    assert stop.about_md.startswith("Inhabited for more than 6,000 years")
    assert len(stop.excursions) == 10
    first = stop.excursions[0]
    assert (first.id, first.title) == ("53205", "Great Bernera")
    assert first.facts["Duration"] == "3½ Hours"
    assert first.description_md.startswith("Departing from Stornoway")
    assert "| Field |" not in first.description_md
    assert doc.notes == []


def test_day9_two_stops_and_duplicate_titles(repo_root):
    doc = parse_day_file(repo_root / "2027-ireland" / "day-09-galway-cliffs-of-moher.md")
    galway, cliffs = doc.stops
    assert galway.port_id == "GWY" and cliffs.port_id == "721"
    assert len(galway.excursions) == 13
    assert cliffs.excursions == []
    assert "Cliffs of Moher" in cliffs.about_md or "cliffs" in cliffs.about_md.lower()
    connemara = [e.id for e in galway.excursions if e.title == "A Day in Scenic Connemara"]
    assert sorted(connemara) == ["99005", "99011"]
    assert doc.notes == []


def test_sea_day_has_no_excursions(repo_root):
    doc = parse_day_file(repo_root / "2027-ireland" / "day-02-at-sea.md")
    assert doc.stops[0].port_id == "ATSEADAY"
    assert doc.excursions() == []
    assert doc.notes == []


def test_extra_sections_become_notes(fixtures_dir):
    doc = parse_day_file(fixtures_dir / "day-with-notes.md")
    exc = doc.stops[0].excursions
    assert [e.id for e in exc] == ["53205"]
    assert "#### What to bring" in exc[0].description_md
    assert [n.title for n in doc.notes] == ["Our research"]
    assert "### Reading list" in doc.notes[0].body_md


def test_every_day_file_parses(repo_root):
    total = 0
    for path in sorted((repo_root / "2027-ireland").glob("day-*.md")):
        doc = parse_day_file(path)
        total += len(doc.excursions())
        assert doc.notes == [], path.name
    assert total == 131

from sitegen.data import assign_place_ids, load_trip_data, slugify


def test_ireland_counts(repo_root):
    trip = load_trip_data(repo_root / "2027-ireland")
    assert len(trip.days) == 12
    assert len(trip.ports) == 10
    assert len(trip.routes) == 9
    assert len(trip.places) == 327
    assert len(trip.excursions) == 131


def test_place_ids_unique_and_stable(repo_root):
    trip = load_trip_data(repo_root / "2027-ireland")
    ids = [f["properties"]["id"] for f in trip.places]
    assert len(ids) == len(set(ids))
    assert all(i.startswith(f"d{f['properties']['day']}-") for i, f in zip(ids, trip.places))
    again = load_trip_data(repo_root / "2027-ireland")
    assert ids == [f["properties"]["id"] for f in again.places]


def test_same_name_same_day_disambiguated():
    places = [
        {"properties": {"day": 9, "name": "Cliffs of Moher", "port_id": "GWY"}},
        {"properties": {"day": 9, "name": "Cliffs of Moher", "port_id": "721"}},
    ]
    assign_place_ids(places)
    assert sorted(p["properties"]["id"] for p in places) == ["d9-cliffs-of-moher", "d9-cliffs-of-moher-gwy"]


def test_slugify_handles_accents_and_punctuation():
    assert slugify("Giant's Causeway") == "giant-s-causeway"
    assert slugify("Café Ó Ceallaigh") == "cafe-o-ceallaigh"

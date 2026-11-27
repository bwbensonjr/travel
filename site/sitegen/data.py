"""Load a trip's structured data: places.geojson and excursions.csv."""
import csv
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "place"


@dataclass
class TripData:
    geojson: dict
    days: list
    routes: list
    ports: list
    places: list
    excursions: dict = field(default_factory=dict)


def load_geojson(path):
    path = Path(path)
    data = json.loads(path.read_text())
    if data.get("type") != "FeatureCollection" or "days" not in data:
        raise ValueError(f"{path}: expected a FeatureCollection with a top-level 'days' member")
    return data


def assign_place_ids(places):
    """Give every place a stable, unique ID of the form d<day>-<slug>.

    Places are processed in (day, name, port_id) order so the result does not
    depend on file order. A name repeated on the same day gets its port code
    appended, then a counter if that still collides.
    """
    seen = set()
    for f in sorted(places, key=lambda f: (f["properties"]["day"], f["properties"]["name"],
                                           f["properties"].get("port_id", ""))):
        p = f["properties"]
        base = f"d{p['day']}-{slugify(p['name'])}"
        pid = base
        if pid in seen:
            pid = f"{base}-{slugify(str(p.get('port_id', '')))}"
        n = 2
        while pid in seen:
            pid = f"{base}-{n}"
            n += 1
        seen.add(pid)
        p["id"] = pid
    return places


def load_excursions(path):
    excursions = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            price = row.get("starting_price_usd", "")
            excursions[row["excursion_id"]] = {
                "id": row["excursion_id"],
                "title": row["title"],
                "day": int(row["day"]),
                "port": row["port"],
                "port_id": row["port_id"],
                "price": int(price) if price.isdigit() else None,
                "duration": row.get("duration", ""),
                "activity_level": row.get("activity_level", ""),
                "excursion_type": row.get("excursion_type", ""),
                "wheelchair_accessible": row.get("wheelchair_accessible", ""),
                "minimum_age": row.get("minimum_age", ""),
                "meals": row.get("meals", ""),
                "url": row.get("url", ""),
                "day_file": row.get("day_file", ""),
            }
    return excursions


def load_trip_data(data_dir):
    data_dir = Path(data_dir)
    geojson = load_geojson(data_dir / "places.geojson")
    features = geojson["features"]
    places = assign_place_ids([f for f in features if f["properties"].get("kind") == "place"])
    return TripData(
        geojson=geojson,
        days=geojson["days"],
        routes=[f for f in features if f["properties"].get("kind") == "route"],
        ports=[f for f in features if f["properties"].get("kind") == "port"],
        places=places,
        excursions=load_excursions(data_dir / "excursions.csv"),
    )

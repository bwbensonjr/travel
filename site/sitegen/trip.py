"""Page models for a trip: day views for day pages and the JSON for the map."""
from dataclasses import dataclass, field

from .render import markdown_to_html

# Place categories in display order. "one" is the singular label.
CATEGORIES = [
    ("town", "Towns", "Town"),
    ("castle", "Castles", "Castle"),
    ("historic", "Historic sites", "Historic site"),
    ("religious", "Churches & abbeys", "Church or abbey"),
    ("museum", "Museums", "Museum"),
    ("nature", "Nature", "Nature"),
    ("garden", "Gardens & estates", "Garden or estate"),
    ("distillery", "Distilleries", "Distillery"),
    ("viewpoint", "Viewpoints", "Viewpoint"),
    ("food", "Food & drink", "Food and drink"),
    ("other", "Other", "Other"),
]
CATEGORY_KEYS = [c[0] for c in CATEGORIES]
CATEGORY_LABEL = {k: label for k, label, _ in CATEGORIES}

SEA = "ATSEADAY"

# Facts shown in an excursion's detail table, in order: (label, key in merged record).
EXCURSION_FACTS = [
    ("Starting at", "price_label"),
    ("Duration", "duration"),
    ("Activity level", "activity_level"),
    ("Excursion type", "excursion_type"),
    ("Wheelchair accessible", "wheelchair_accessible"),
    ("Minimum age", "minimum_age"),
    ("Meals", "meals"),
]


def price_label(price):
    return f"${price}" if price is not None else ""


@dataclass
class StopView:
    name: str
    short_name: str
    port_id: str
    is_sea: bool
    arrive: str
    depart: str
    flags: list
    about_html: str
    excursions: list
    place_groups: list
    place_count: int


@dataclass
class DayView:
    day: int
    date: str
    title: str
    is_sea: bool
    stops: list
    notes: list = field(default_factory=list)
    excursion_count: int = 0
    place_count: int = 0
    prev_day: int | None = None
    next_day: int | None = None


def short_name(name):
    return name.split(",")[0].strip()


def merge_excursion(md_exc, csv_exc):
    rec = dict(csv_exc)
    rec["title"] = md_exc.title or csv_exc["title"]
    rec["price_label"] = price_label(csv_exc["price"])
    rec["description_html"] = markdown_to_html(md_exc.description_md)
    rec["facts"] = [(label, rec[key]) for label, key in EXCURSION_FACTS if rec.get(key)]
    # The collapsed row omits price on purpose; it appears in the expanded facts ("Starting at").
    rec["summary"] = " · ".join(x for x in (rec["duration"], rec["activity_level"]) if x)
    return rec


def group_places(places):
    groups = []
    for key, label, _ in CATEGORIES:
        items = sorted((p for p in places if p["category"] == key), key=lambda p: p["name"])
        if items:
            groups.append({"key": key, "label": label, "places": items})
    known = set(CATEGORY_KEYS)
    rest = sorted((p for p in places if p["category"] not in known), key=lambda p: p["name"])
    if rest:
        groups.append({"key": "other", "label": "Other", "places": rest})
    return groups


def build_day_views(trip_data, docs):
    """Combine GeoJSON days, parsed day files, places and CSV facts into DayViews."""
    places_by_day = {}
    for f in trip_data.places:
        places_by_day.setdefault(f["properties"]["day"], []).append(f["properties"])

    views = []
    for day in trip_data.days:
        n = day["day"]
        doc = docs[n]
        stop_ids = [s["port_id"] for s in day["stops"]]
        day_places = places_by_day.get(n, [])
        stops = []
        for i, s in enumerate(day["stops"]):
            md_stop = doc.stops[i] if i < len(doc.stops) else None
            pid = s["port_id"]
            # Places belong to the stop with their port code; strays go to the first stop.
            mine = [p for p in day_places
                    if p.get("port_id") == pid or (i == 0 and p.get("port_id") not in stop_ids)]
            excursions = []
            if md_stop:
                excursions = [merge_excursion(e, trip_data.excursions[e.id]) for e in md_stop.excursions]
            stops.append(StopView(
                name=s["name"], short_name=short_name(s["name"]), port_id=pid,
                is_sea=pid == SEA, arrive=s.get("arrive", ""), depart=s.get("depart", ""),
                flags=s.get("flags", []),
                about_html=markdown_to_html(md_stop.about_md) if md_stop else "",
                excursions=excursions, place_groups=group_places(mine), place_count=len(mine),
            ))
        is_sea = all(s.is_sea for s in stops)
        views.append(DayView(
            day=n, date=day["date"], is_sea=is_sea,
            title="At sea" if is_sea else " + ".join(s.short_name for s in stops),
            stops=stops,
            notes=[{"title": nt.title, "html": markdown_to_html(nt.body_md)} for nt in doc.notes],
            excursion_count=sum(len(s.excursions) for s in stops),
            place_count=sum(s.place_count for s in stops),
        ))
    for i, v in enumerate(views):
        v.prev_day = views[i - 1].day if i > 0 else None
        v.next_day = views[i + 1].day if i + 1 < len(views) else None
    return views


def trip_json(trip_data, views):
    """Data for the map page: GeoJSON (with place IDs), days, excursions, categories."""
    excursions = {
        eid: {k: e[k] for k in ("id", "title", "day", "port_id", "price", "duration",
                                "activity_level", "wheelchair_accessible", "url")}
        for eid, e in trip_data.excursions.items()
    }
    days = [{
        "day": v.day, "date": v.date, "title": v.title, "is_sea": v.is_sea,
        "place_count": v.place_count, "excursion_count": v.excursion_count,
        "stops": [{"name": s.name, "port_id": s.port_id, "arrive": s.arrive, "depart": s.depart,
                   "flags": s.flags} for s in v.stops],
    } for v in views]
    return {
        "geojson": {"type": "FeatureCollection", "features": trip_data.geojson["features"]},
        "days": days,
        "excursions": excursions,
        "categories": [{"key": k, "label": label, "one": one} for k, label, one in CATEGORIES],
    }

"""Cross-check a trip's GeoJSON, excursion CSV and day Markdown files."""
from pathlib import Path

from .daymd import DayParseError, parse_day_file


class ValidationError(ValueError):
    def __init__(self, problems):
        self.problems = problems
        super().__init__("\n  " + "\n  ".join(problems))


def load_and_validate_days(data_dir, trip):
    """Parse every day file listed in the GeoJSON and validate references.

    Returns {day_number: DayDoc}. Raises ValidationError listing every problem
    found, each naming the file and the offending ID.
    """
    data_dir = Path(data_dir)
    problems = []
    docs = {}
    csv_ids = trip.excursions

    for day in trip.days:
        path = data_dir / day["day_file"]
        if not path.exists():
            problems.append(f"{path}: day {day['day']} file is missing")
            continue
        try:
            doc = parse_day_file(path)
        except DayParseError as e:
            problems.append(str(e))
            continue
        if doc.day != day["day"]:
            problems.append(f"{path}: front matter says day {doc.day}, places.geojson says {day['day']}")
        docs[day["day"]] = doc
        for exc in doc.excursions():
            if exc.id not in csv_ids:
                problems.append(f"{path}:{exc.line}: excursion ID {exc.id} ({exc.title}) is not in excursions.csv")
            elif csv_ids[exc.id]["day"] != doc.day:
                problems.append(f"{path}:{exc.line}: excursion ID {exc.id} is listed for day "
                                f"{csv_ids[exc.id]['day']} in excursions.csv")

    for f in trip.places:
        p = f["properties"]
        for eid in p.get("excursion_ids", []):
            if eid not in csv_ids:
                problems.append(f"{data_dir / 'places.geojson'}: place '{p['name']}' (day {p['day']}) "
                                f"references excursion ID {eid}, which is not in excursions.csv")

    for eid, exc in csv_ids.items():
        doc = docs.get(exc["day"])
        if doc is not None and eid not in {e.id for e in doc.excursions()}:
            problems.append(f"{doc.path}: excursion ID {eid} ({exc['title']}) from excursions.csv "
                            f"is missing from the day file")

    if problems:
        raise ValidationError(problems)
    return docs

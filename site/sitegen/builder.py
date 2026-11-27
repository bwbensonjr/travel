"""Top-level build: load config and trip data, render pages, copy assets."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path

import yaml

from .data import load_trip_data
from .offline import manifest, precache_urls, service_worker
from .render import PageWriter, make_env
from .trip import build_day_views, trip_json
from .validate import ValidationError, load_and_validate_days

ROBOTS_TXT = "User-agent: *\nDisallow: /\n"


class BuildError(Exception):
    """Raised for invalid configuration or trip data; the build must not deploy."""


def load_config(site_dir):
    path = Path(site_dir) / "site.yaml"
    try:
        config = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as e:
        raise BuildError(f"cannot read {path}: {e}") from e
    if not isinstance(config, dict) or not isinstance(config.get("trips"), list):
        raise BuildError(f"{path}: expected a mapping with a 'trips' list")
    for trip in config["trips"]:
        for key in ("slug", "title", "dates", "data_dir"):
            if key not in trip:
                raise BuildError(f"{path}: trip entry missing '{key}'")
        trip.setdefault("subtitle", "")
    config.setdefault("title", "Travel")
    return config


def load_trips(config, repo_root):
    """Load and validate every trip; raise BuildError listing all problems."""
    trips = []
    for entry in config["trips"]:
        data_dir = Path(repo_root) / entry["data_dir"]
        try:
            data = load_trip_data(data_dir)
            docs = load_and_validate_days(data_dir, data)
        except ValidationError as e:
            raise BuildError(f"trip '{entry['slug']}' has invalid data:{e}") from e
        except (OSError, ValueError, KeyError) as e:
            raise BuildError(f"trip '{entry['slug']}': cannot load data from {data_dir}: {e}") from e
        trips.append({"config": entry, "data_dir": data_dir, "data": data, "docs": docs})
    return trips


def input_version(site_dir, trips):
    """Hash of every build input, used to version pages and the offline cache."""
    h = hashlib.sha256()
    files = sorted(p for p in Path(site_dir).rglob("*")
                   if p.is_file() and "tests" not in p.parts and "__pycache__" not in p.parts)
    for t in trips:
        d = t["data_dir"]
        files += [d / "places.geojson", d / "excursions.csv"] + sorted(d.glob("day-*.md"))
    for p in files:
        h.update(str(p.name).encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def build(site_dir, out_dir, repo_root=None, today=None):
    site_dir = Path(site_dir)
    out_dir = Path(out_dir)
    repo_root = Path(repo_root) if repo_root else site_dir.parent
    config = load_config(site_dir)
    trips = load_trips(config, repo_root)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    today = today or datetime.date.today()
    common = {
        "site_title": config["title"],
        "build_date": today.strftime("%b %-d, %Y"),
        "build_version": input_version(site_dir, trips),
    }
    writer = PageWriter(make_env(site_dir / "templates"), out_dir, common)

    writer.write("index.html", "index.html", trips=[t["config"] for t in trips])
    writer.write_text("robots.txt", ROBOTS_TXT)
    for t in trips:
        slug = t["config"]["slug"]
        views = build_day_views(t["data"], t["docs"])
        t["views"] = views
        writer.write(f"{slug}/index.html", "map.html", trip=t["config"], days=views)
        writer.write_text(f"{slug}/trip.json",
                          json.dumps(trip_json(t["data"], views), ensure_ascii=False, separators=(",", ":")))
        for v in views:
            writer.write(f"{slug}/day/{v.day}/index.html", "day.html", trip=t["config"], d=v)
    writer.write("offline/index.html", "offline.html", trips=trips)
    writer.write_text("manifest.webmanifest", manifest(config))
    shutil.copytree(site_dir / "static", out_dir / "static",
                    ignore=shutil.ignore_patterns(".DS_Store"))
    # The service worker goes last: it precaches everything written above.
    writer.write_text("sw.js", service_worker(precache_urls(out_dir), common["build_version"]))

    return f"Built {len(trips)} trip(s), {len(writer.written)} pages into {out_dir}"

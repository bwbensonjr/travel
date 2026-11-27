import json
import shutil

import pytest

from sitegen.data import load_trip_data
from sitegen.validate import ValidationError, load_and_validate_days


@pytest.fixture
def trip_copy(repo_root, tmp_path):
    dest = tmp_path / "trip"
    shutil.copytree(repo_root / "2027-ireland", dest,
                    ignore=shutil.ignore_patterns("*.docx", "*.webp", "scripts"))
    return dest


def validate(data_dir):
    return load_and_validate_days(data_dir, load_trip_data(data_dir))


def test_real_data_passes(repo_root):
    docs = validate(repo_root / "2027-ireland")
    assert sorted(docs) == list(range(1, 13))


def test_missing_day_file(trip_copy):
    (trip_copy / "day-04-belfast.md").unlink()
    with pytest.raises(ValidationError) as e:
        validate(trip_copy)
    assert any("day-04-belfast.md" in p and "missing" in p for p in e.value.problems)


def test_place_references_unknown_excursion(trip_copy):
    path = trip_copy / "places.geojson"
    data = json.loads(path.read_text())
    place = next(f for f in data["features"] if f["properties"]["kind"] == "place"
                 and f["properties"]["name"] == "Giant's Causeway")
    place["properties"]["excursion_ids"].append("00000")
    path.write_text(json.dumps(data))
    with pytest.raises(ValidationError) as e:
        validate(trip_copy)
    assert any("Giant's Causeway" in p and "00000" in p for p in e.value.problems)


def test_build_command_fails_on_bad_data(trip_copy, site_dir, tmp_path):
    import subprocess
    import sys

    (trip_copy / "day-04-belfast.md").unlink()
    site_copy = tmp_path / "site"
    shutil.copytree(site_dir, site_copy, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (site_copy / "site.yaml").write_text(
        "title: T\ntrips:\n  - {slug: x, title: X, dates: d, data_dir: trip}\n")
    out = tmp_path / "out"
    result = subprocess.run([sys.executable, str(site_copy / "build.py"), "--out", str(out)],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "day-04-belfast.md" in result.stderr
    assert not out.exists()


def test_markdown_excursion_not_in_csv(trip_copy):
    path = trip_copy / "day-03-stornoway.md"
    path.write_text(path.read_text().replace("| Excursion ID | 53205 |", "| Excursion ID | 99999 |"))
    with pytest.raises(ValidationError) as e:
        validate(trip_copy)
    problems = e.value.problems
    assert any("day-03-stornoway.md" in p and "99999" in p for p in problems)
    assert any("53205" in p and "missing from the day file" in p for p in problems)

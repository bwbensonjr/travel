from sitegen.builder import build, load_config


def test_config_lists_ireland_trip(site_dir):
    config = load_config(site_dir)
    assert [t["slug"] for t in config["trips"]] == ["2027-ireland"]


def test_build_creates_output_dir(site_dir, tmp_path):
    out = tmp_path / "out"
    build(site_dir, out)
    assert out.is_dir()

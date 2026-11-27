"""Shared fixtures. Run with:

    uv run --with pytest --with-requirements site/build.py pytest site/tests
"""
import sys
from pathlib import Path

import pytest

SITE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SITE_DIR.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SITE_DIR))


@pytest.fixture(scope="session")
def site_dir():
    return SITE_DIR


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def fixtures_dir():
    return FIXTURES

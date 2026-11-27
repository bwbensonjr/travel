# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "jinja2>=3.1",
#     "markdown>=3.5",
#     "pyyaml>=6.0",
# ]
# ///
"""Build the static travel site into _site/.

Usage (from the repository root):
    uv run site/build.py            # build into _site/
    uv run site/build.py --out DIR  # build into another directory
"""
import argparse
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE_DIR))

from sitegen.builder import BuildError, build  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Build the static travel site.")
    parser.add_argument("--out", type=Path, default=SITE_DIR.parent / "_site",
                        help="output directory (default: _site/ at the repository root)")
    args = parser.parse_args()
    try:
        summary = build(SITE_DIR, args.out)
    except BuildError as e:
        print(f"Build failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(summary)


if __name__ == "__main__":
    main()

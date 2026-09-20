"""
Run the profile README pipeline.

Usage (from repo root):
    python scripts/build.py              # fetch calendar + heatmap + info card
    python scripts/build.py --ascii      # also rebuild ASCII from source-prepped.png
    python scripts/build.py --portrait   # prep headshot (rembg) then ASCII
"""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run_script(name: str) -> None:
    sys.path.insert(0, str(SCRIPTS))
    runpy.run_path(str(SCRIPTS / name), run_name="__main__")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GitHub profile README assets")
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="rebuild ASCII SVG from existing source-prepped.png",
    )
    parser.add_argument(
        "--portrait",
        action="store_true",
        help="run rembg photo prep, then ASCII",
    )
    args = parser.parse_args()

    if args.portrait:
        run_script("prep_photo.py")
        run_script("make_ascii_svg.py")
    elif args.ascii:
        run_script("make_ascii_svg.py")

    run_script("fetch_contributions.py")
    run_script("render_heatmap_svg.py")
    run_script("make_info_card.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

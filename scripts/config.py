"""Shared config. Change GH_USERNAME to your GitHub username (env var overrides it)."""
import os

GH_USERNAME = os.environ.get("GH_USERNAME", "mdjuman-dev")  # <-- put your real GitHub username here

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SOURCE_PHOTO = os.path.join(ROOT, "assets", "professional-headshot.png")
PREPPED_PHOTO = os.path.join(ROOT, "source-prepped.png")
ASCII_SVG_OUT = os.path.join(ROOT, f"{GH_USERNAME}-ascii.svg")
INFO_CARD_OUT = os.path.join(ROOT, "info-card.svg")
CONTRIB_JSON = os.path.join(DATA_DIR, "contributions.json")
HEATMAP_SVG_OUT = os.path.join(ROOT, "contrib-heatmap.svg")
PROMPT_HOST = f"{GH_USERNAME}@github"

os.makedirs(DATA_DIR, exist_ok=True)

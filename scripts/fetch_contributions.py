"""
Step 5a — pull the real contribution calendar without a token or the GraphQL API.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions -- the same fragment the
profile page itself renders. We fetch it, parse day cells with
BeautifulSoup, and write data/contributions.json with raw days + derived
stats (current streak, longest streak, best day, monthly totals).

Usage:
    python scripts/fetch_contributions.py
"""
import json
from collections import defaultdict
from datetime import date

import requests
from bs4 import BeautifulSoup

from config import GH_USERNAME, CONTRIB_JSON

URL = f"https://github.com/users/{GH_USERNAME}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Current GitHub markup: each day is a <td class="ContributionCalendar-day"
    # data-date="..." data-level="..." id="contribution-day-component-x-y">
    # with NO count on the cell itself -- the count lives in a sibling
    # <tool-tip for="<that id>">N contributions on <date>.</tool-tip>.
    tooltip_by_id = {}
    for tip in soup.select("tool-tip[for]"):
        tooltip_by_id[tip.get("for")] = tip.get_text(strip=True)

    def parse_count(tooltip_text: str) -> int:
        if not tooltip_text:
            return 0
        if tooltip_text.lower().startswith("no contributions"):
            return 0
        first_word = tooltip_text.split(" ", 1)[0].replace(",", "")
        return int(first_word) if first_word.isdigit() else 0

    days = []
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        cell_id = cell.get("id")
        count = parse_count(tooltip_by_id.get(cell_id, ""))
        days.append({
            "date": d,
            "count": count,
            "level": int(level) if level is not None else None,
        })

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})

    # streaks
    longest = current = 0
    running = 0
    today = date.today().isoformat()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run ending today (or most recent day with data)
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            current += 1
        else:
            break

    monthly = defaultdict(int)
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] += d["count"]

    return {
        "total": total,
        "best_day": best,
        "current_streak": current,
        "longest_streak": longest,
        "monthly": dict(sorted(monthly.items())),
    }


if __name__ == "__main__":
    days = fetch_days()
    stats = derive_stats(days)
    payload = {"username": GH_USERNAME, "days": days, "stats": stats}
    with open(CONTRIB_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {CONTRIB_JSON} ({len(days)} days, {stats['total']} total contributions)")

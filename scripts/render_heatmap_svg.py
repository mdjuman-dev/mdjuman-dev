"""
Step 5b — draw the 53-week x 7-day calendar as rounded, colored boxes,
revealed once with a diagonal line-after-line slide-down (plays on load,
then freezes -- no looping). Adds a Less->More legend and a stats footer.

Usage:
    python scripts/render_heatmap_svg.py

Output: contrib-heatmap.svg
"""
import json
from datetime import datetime

from config import CONTRIB_JSON, HEATMAP_SVG_OUT

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none      lvl1       lvl2       lvl3       lvl4       lvl5 (neon top end)

BOX = 11
GAP = 3
LEFT_PAD = 30       # room for day-of-week labels
TOP_PAD = 34        # room for month labels + title
RIGHT_PAD = 16
BOTTOM_PAD = 40      # room for legend + stats footer
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DIM = "#8b949e"
BRIGHT = "#c9d1d9"

STEP_DELAY = 0.028   # seconds between each diagonal (week+day) reveal step
BOX_DUR = 0.35

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level_color(level, count):
    if level is not None:
        return PALETTE[min(max(level, 0), 5)]
    # fallback bucketing if data-level was missing
    if count == 0:
        return PALETTE[0]
    if count < 3:
        return PALETTE[1]
    if count < 6:
        return PALETTE[2]
    if count < 10:
        return PALETTE[3]
    return PALETTE[4]


def build_weeks(days):
    """Group flat day list into weeks (columns), each a list of 7 slots (Sun-Sat)."""
    weeks = []
    current_week = [None] * 7
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        weekday = (dt.weekday() + 1) % 7  # Python Mon=0 -> convert so Sun=0
        if weekday == 0 and any(current_week):
            weeks.append(current_week)
            current_week = [None] * 7
        current_week[weekday] = d
        d["_dt"] = dt
    if any(current_week):
        weeks.append(current_week)
    return weeks


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(payload: dict) -> str:
    days = payload["days"]
    stats = payload["stats"]
    username = payload.get("username", "")
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * (BOX + GAP)
    grid_h = 7 * (BOX + GAP)
    width = LEFT_PAD + grid_w + RIGHT_PAD
    height = TOP_PAD + grid_h + BOTTOM_PAD

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}" font-size="10">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117" rx="8"/>',
    ]

    # day-of-week labels (Mon, Wed, Fri)
    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for wd, label in dow_labels.items():
        y = TOP_PAD + wd * (BOX + GAP) + BOX - 2
        parts.append(f'<text x="4" y="{y}" fill="{DIM}">{label}</text>')

    # month labels (only when the month changes going across weeks)
    last_month = None
    for wi, week in enumerate(weeks):
        first_valid = next((d for d in week if d), None)
        if not first_valid:
            continue
        month = first_valid["_dt"].month
        if month != last_month:
            x = LEFT_PAD + wi * (BOX + GAP)
            parts.append(f'<text x="{x}" y="{TOP_PAD - 10}" fill="{DIM}">{MONTH_NAMES[month-1]}</text>')
            last_month = month

    # boxes, diagonal reveal: step index = week + day so it slides in diagonally
    for wi, week in enumerate(weeks):
        for di in range(7):
            d = week[di]
            x = LEFT_PAD + wi * (BOX + GAP)
            y = TOP_PAD + di * (BOX + GAP)
            if d is None:
                continue
            color = level_color(d.get("level"), d.get("count", 0))
            step = wi + di
            begin = step * STEP_DELAY
            title = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" opacity="0" transform="translate(-6,-6)">'
                f'<title>{esc(title)}</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
                f'dur="{BOX_DUR}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-6 -6" to="0 0" begin="{begin:.3f}s" dur="{BOX_DUR}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                f'</rect>'
            )

    # legend: Less [boxes] More, bottom-left
    legend_y = TOP_PAD + grid_h + 22
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y}" fill="{DIM}">Less</text>')
    lx = LEFT_PAD + 32
    for c in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y-9}" width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>')
        lx += BOX + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y}" fill="{DIM}">More</text>')

    # stats footer, bottom-right
    footer = f'{stats["total"]:,} contributions in the last year · streak {stats["current_streak"]}d · best {stats["longest_streak"]}d'
    parts.append(
        f'<text x="{width - RIGHT_PAD}" y="{legend_y}" text-anchor="end" fill="{BRIGHT}">{esc(footer)}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    with open(CONTRIB_JSON) as f:
        payload = json.load(f)
    svg = build_svg(payload)
    with open(HEATMAP_SVG_OUT, "w") as f:
        f.write(svg)
    print(f"wrote {HEATMAP_SVG_OUT}")

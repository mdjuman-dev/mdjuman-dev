"""
Step 4 — neofetch-style info card: title bar + key/value rows that fade/slide
in on a stagger. Content lives here (not in the heatmap) because the graph
already covers GitHub stats -- this card is for the numbers a graph can't tell.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame for Quick Look

Output: info-card.svg
"""
import os
from config import INFO_CARD_OUT, PROMPT_HOST

STATIC = os.environ.get("STATIC") == "1"

# ---- edit this block to change what the card shows -------------------------
TITLE = PROMPT_HOST
ROWS = [
    ("Name", "Md Juman"),
    ("Now", "Full-Stack Developer @ TechitNext"),
    ("Prev", "Co-Founder @ TechitNext"),
    ("Stack", "Laravel · PHP · React · Next.js · MySQL"),
    ("Building", "Production client apps (web + e-commerce)"),
    ("Base", "Chattogram · juman.techitnext.com"),
]
# -----------------------------------------------------------------------------

WIDTH = 490
PADDING = 22
TITLEBAR_H = 34
ROW_H = 30
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
BG = "#0d1117"
BORDER = "#30363d"
KEY_FILL = "#39d353"
VAL_FILL = "#c9d1d9"
DIM_FILL = "#8b949e"
STAGGER = 0.16
FADE_DUR = 0.4


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    height = TITLEBAR_H + len(ROWS) * ROW_H + PADDING
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}" font-size="14">',
        f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # fake title bar with traffic-light dots
        f'<circle cx="22" cy="{TITLEBAR_H/2:.0f}" r="5" fill="#ff5f56"/>',
        f'<circle cx="40" cy="{TITLEBAR_H/2:.0f}" r="5" fill="#ffbd2e"/>',
        f'<circle cx="58" cy="{TITLEBAR_H/2:.0f}" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="{TITLEBAR_H/2 + 5:.0f}" text-anchor="middle" '
        f'fill="{DIM_FILL}" font-size="12">{esc(TITLE)}</text>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{BORDER}"/>',
    ]

    key_col_w = max(len(k) for k, _ in ROWS) * 8.2 + PADDING

    for i, (key, val) in enumerate(ROWS):
        y = TITLEBAR_H + PADDING + i * ROW_H + 14
        begin = STAGGER * i
        if STATIC:
            opacity_attr = ""
            transform = ""
        else:
            opacity_attr = "opacity=\"0\""
            transform = 'transform="translate(-8,0)"'

        parts.append(f'<g {opacity_attr} {transform}>')
        if not STATIC:
            parts.append(
                f'  <animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.2f}s" dur="{FADE_DUR}s" fill="freeze"/>'
            )
            parts.append(
                f'  <animateTransform attributeName="transform" type="translate" '
                f'from="-8 0" to="0 0" begin="{begin:.2f}s" dur="{FADE_DUR}s" fill="freeze"/>'
            )
        parts.append(
            f'  <text x="{PADDING}" y="{y}" fill="{KEY_FILL}">{esc(key)}</text>'
        )
        parts.append(
            f'  <text x="{key_col_w}" y="{y}" fill="{VAL_FILL}">{esc(val)}</text>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(INFO_CARD_OUT, "w") as f:
        f.write(svg)
    print(f"wrote {INFO_CARD_OUT}{' (static)' if STATIC else ''}")

"""
Step 3b — turn source-prepped.png into a self-typing, monochrome ASCII SVG.

Usage:
    python scripts/make_ascii_svg.py

Output: <GH_USERNAME>-ascii.svg

Design choices:
  - Monochrome fill (one light-gray). Per-char rainbow coloring is what
    makes most ASCII portraits look noisy/static.
  - High contrast source -> busy background washes out to spaces, only
    the subject prints.
  - Each row sits behind a <clipPath> rect that animates width 0 -> 100%,
    staggered top to bottom, so it looks like it's "typing" in. A small
    block cursor rides the wipe edge. Plays once, then freezes.
"""
from PIL import Image

from config import PREPPED_PHOTO, ASCII_SVG_OUT

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FONT_SIZE = 11
FILL = "#8b949e"          # monochrome light gray, GitHub-dark-friendly
CURSOR_FILL = "#c9d1d9"
ROW_DURATION = 0.55       # seconds for one row to "type" across
ROW_STAGGER = 0.045       # seconds between each row's start


def image_to_ascii(path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("L").resize((cols, rows))
    pixels = list(img.getdata())
    ramp_len = len(RAMP)
    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def esc(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(lines: list[str]) -> str:
    width = COLS * CHAR_W + 20
    height = ROWS * CHAR_H + 20
    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{FONT_SIZE}">',
        '<style>text{white-space:pre;} rect.cursor{fill:%s;}</style>' % CURSOR_FILL,
    ]

    for r, line in enumerate(lines):
        y = 10 + (r + 1) * CHAR_H
        row_w = len(line) * CHAR_W
        start = ROW_STAGGER * r
        clip_id = f"clip{r}"
        text_escaped = "".join(esc(c) for c in line)

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'  <rect x="10" y="{y - CHAR_H + 2:.1f}" height="{CHAR_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_w:.1f}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/></rect>'
        )
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'  <text x="10" y="{y}" fill="{FILL}">{text_escaped}</text>')
        # cursor block riding the wipe edge
        parts.append(
            f'  <rect class="cursor" x="10" y="{y - CHAR_H + 2:.1f}" '
            f'width="{CHAR_W:.1f}" height="{CHAR_H}" opacity="0">'
            f'<animate attributeName="x" from="10" to="{10 + row_w:.1f}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.85;1" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION}s" fill="freeze"/>'
            f'</rect>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    lines = image_to_ascii(PREPPED_PHOTO, COLS, ROWS)
    svg = build_svg(lines)
    with open(ASCII_SVG_OUT, "w") as f:
        f.write(svg)
    print(f"wrote {ASCII_SVG_OUT} ({COLS}x{ROWS} chars)")

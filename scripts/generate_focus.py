#!/usr/bin/env python3
"""Generate output/focus-card.svg for GitHub Profile README."""

from pathlib import Path

OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)

BG_CARD = "#0f141b"
BG_PAGE = "#0d1117"
BORDER = "#4a3a7a"
TEXT = "#c9d1d9"
TEXT_DIM = "#8b949e"
ACCENT = "#a78bfa"
GOLD = "#e0a458"
FONT = "sans-serif"
MONO = "monospace"


def build():
    W, H = 880, 260
    PAD = 24  
    INNER_W = W - (PAD * 2) # 832
    
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG_PAGE}"/>',
    ]

    y = 30
    parts.append(
        f'<text x="{PAD}" y="{y}" font-family="{FONT}" font-size="22" '
        f'font-weight="700" fill="{TEXT}">Current Focus</text>'
    )
    parts.append(
        f'<text x="180" y="{y}" font-family="{MONO}" font-size="13" '
        f'fill="{TEXT_DIM}">math -&gt; physics -&gt; notes -&gt; code</text>'
    )
    parts.append(
        '<defs><linearGradient id="g1" x1="0" x2="1">'
        f'<stop offset="0%" stop-color="{ACCENT}"/>'
        f'<stop offset="100%" stop-color="{GOLD}"/>'
        '</linearGradient></defs>'
    )
    parts.append(
        f'<rect x="{PAD}" y="{y + 10}" width="{INNER_W}" height="1" '
        f'fill="url(#g1)" opacity="0.55"/>'
    )

    card_y = y + 30
    card_h = 76
    # Card 1: Interests
    parts.append(
        f'<rect x="{PAD}" y="{card_y}" width="{INNER_W}" height="{card_h}" rx="8" '
        f'fill="{BG_CARD}" stroke="{BORDER}"/>'
    )
    parts.append(
        f'<text x="{PAD + 20}" y="{card_y + 28}" font-family="{FONT}" font-size="15" '
        f'font-weight="600" fill="{TEXT}">Interests</text>'
    )
    parts.append(
        f'<text x="{PAD + INNER_W - 20}" y="{card_y + 28}" font-family="{MONO}" '
        f'font-size="12" font-weight="700" fill="{ACCENT}" '
        f'text-anchor="end">01</text>'
    )
    parts.append(
        f'<text x="{PAD + 20}" y="{card_y + 54}" font-family="{FONT}" font-size="14" '
        f'fill="{TEXT_DIM}">Mathematical Physics &amp; Theoretical Condensed Matter</text>'
    )

    card2_y = card_y + card_h + 12
    card2_h = 76
    card_w = (INNER_W - 12) / 2 # 左右两个卡片均分
    
    # Card 2: Knowledge Notes
    parts.append(
        f'<rect x="{PAD}" y="{card2_y}" width="{card_w}" height="{card2_h}" rx="8" '
        f'fill="{BG_CARD}" stroke="{BORDER}"/>'
    )
    parts.append(
        f'<text x="{PAD + 20}" y="{card2_y + 28}" font-family="{FONT}" font-size="15" '
        f'font-weight="600" fill="{TEXT}">Knowledge Notes</text>'
    )
    parts.append(
        f'<text x="{PAD + card_w - 20}" y="{card2_y + 28}" font-family="{MONO}" '
        f'font-size="12" font-weight="700" fill="{ACCENT}" '
        f'text-anchor="end">02</text>'
    )
    parts.append(
        f'<text x="{PAD + 20}" y="{card2_y + 54}" font-family="{FONT}" font-size="14" '
        f'fill="{TEXT_DIM}">clean ideas and linked writing</text>'
    )

    # Card 3: Open Source
    x3 = PAD + card_w + 12
    parts.append(
        f'<rect x="{x3}" y="{card2_y}" width="{card_w}" height="{card2_h}" rx="8" '
        f'fill="{BG_CARD}" stroke="{BORDER}"/>'
    )
    parts.append(
        f'<text x="{x3 + 20}" y="{card2_y + 28}" font-family="{FONT}" '
        f'font-size="15" font-weight="600" fill="{TEXT}">Open Source</text>'
    )
    parts.append(
        f'<text x="{x3 + card_w - 20}" y="{card2_y + 28}" font-family="{MONO}" '
        f'font-size="12" font-weight="700" fill="{GOLD}" '
        f'text-anchor="end">03</text>'
    )
    parts.append(
        f'<text x="{x3 + 20}" y="{card2_y + 54}" font-family="{FONT}" '
        f'font-size="14" fill="{TEXT_DIM}">small tools and readable systems</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    (OUT / "focus-card.svg").write_text(build(), encoding="utf-8")
    print("OK output/focus-card.svg")


if __name__ == "__main__":
    main()

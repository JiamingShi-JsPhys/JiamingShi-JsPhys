#!/usr/bin/env python3
"""Generate output/wave.gif matching the Pages dynamic profile."""

import json
import math
import os
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

USERNAME = os.environ.get("GH_USERNAME", "JiamingShi-JsPhys")
OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)

BG = "#0d1117"

def fetch_contributions():
    url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())["contributions"]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def brightness(rgb, factor):
    return tuple(min(255, int(c * factor)) for c in rgb)

def build_gif():
    SUP = 3
    WEEKS = 52
    DAYS = 7
    CELL = 14
    GAP = 3

    COLORS_HEX = ["#161b22", "#2d1b69", "#5b21b6", "#7c3aed", "#a78bfa"]
    COLORS = [hex_to_rgb(c) for c in COLORS_HEX]

    GLOW_INNER = (167, 139, 250, 0.28)
    GLOW_OUTER = (124, 58, 237, 0.12)

    SIGMA = 3.6
    GLOW_THRESHOLD = 0.12
    WAVELENGTH_COLS = 3.2
    EDGE_FADE_COLS = 2.5

    try:
        contribs = fetch_contributions()
    except Exception as e:
        print(f"Warning: fetch failed ({e})")
        contribs = []

    by_date = {c["date"]: c for c in contribs}
    today = datetime.now(timezone.utc).date()
    today_dow = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=today_dow)
    start = last_sunday - timedelta(weeks=WEEKS - 1)

    CELL_S = CELL * SUP
    GAP_S = GAP * SUP
    PAD_X = 24 * SUP
    PAD_TOP = 16 * SUP
    PAD_BOTTOM = 16 * SUP

    grid_w = WEEKS * CELL_S + (WEEKS - 1) * GAP_S
    grid_h = DAYS * CELL_S + (DAYS - 1) * GAP_S

    W_big = grid_w + PAD_X * 2
    H_big = grid_h + PAD_TOP + PAD_BOTTOM
    W_final = W_big // SUP
    H_final = H_big // SUP

    cells = []
    total = 0
    for w in range(WEEKS):
        for d in range(DAYS):
            date = start + timedelta(days=w * 7 + d)
            key = date.isoformat()
            item = by_date.get(key, {"count": 0, "level": 0})
            lvl = min(item.get("level", 0), 4)
            total += item.get("count", 0)
            x = PAD_X + w * (CELL_S + GAP_S)
            y = PAD_TOP + d * (CELL_S + GAP_S)
            cells.append((x, y, COLORS[lvl], lvl, w))

    fps = 15
    duration_s = 14.0
    frames = int(fps * duration_s)

    wave_start = -EDGE_FADE_COLS - 2
    wave_end = WEEKS + EDGE_FADE_COLS + 2
    wave_span = wave_end - wave_start
    cols_per_frame = wave_span / frames

    images = []

    for fi in range(frames):
        waveX = wave_start + fi * cols_per_frame

        img = Image.new("RGB", (W_big, H_big), BG)

        left = max(0.0, min(1.0, waveX / EDGE_FADE_COLS))
        right = max(0.0, min(1.0, (WEEKS - waveX) / EDGE_FADE_COLS))
        edge_fade = min(left, right)

        glow_columns = [False] * WEEKS
        for w in range(WEEKS):
            dist = w - waveX
            intensity = math.exp(-(dist * dist) / (2 * SIGMA * SIGMA))
            intensity *= edge_fade
            if intensity > GLOW_THRESHOLD:
                glow_columns[w] = True

        glow_layer = Image.new("RGBA", (W_big, H_big), (0, 0, 0, 0))
        gl = ImageDraw.Draw(glow_layer)
        for (x, y, color, lvl, w) in cells:
            if not glow_columns[w]:
                continue
            outer = 2 * SUP
            gl.rectangle(
                [x - outer, y - outer, x + CELL_S + outer, y + CELL_S + outer],
                fill=(*GLOW_OUTER[:3], int(255 * GLOW_OUTER[3])),
            )
            inner = 1 * SUP
            gl.rectangle(
                [x - inner, y - inner, x + CELL_S + inner, y + CELL_S + inner],
                fill=(*GLOW_INNER[:3], int(255 * GLOW_INNER[3])),
            )

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=3 * SUP))
        img = Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB")
        draw = ImageDraw.Draw(img)

        for (x, y, color, lvl, w) in cells:
            if glow_columns[w]:
                c = brightness(color, 1.06)
                dx = CELL_S * 0.03
                draw.rectangle(
                    [x - dx, y - dx, x + CELL_S + dx, y + CELL_S + dx],
                    fill=c,
                )
            else:
                draw.rectangle([x, y, x + CELL_S, y + CELL_S], fill=color)

        if edge_fade > 0.01:
            centerY = PAD_TOP + grid_h / 2
            amplitude = grid_h * 0.36
            sigma_px = SIGMA * (CELL_S + GAP_S)
            lambda_px = WAVELENGTH_COLS * (CELL_S + GAP_S)

            clampedX = max(0.0, min(WEEKS - 1.0, waveX))
            i0 = int(math.floor(clampedX))
            i1 = min(WEEKS - 1, i0 + 1)
            frac = clampedX - i0
            col_center_i0 = PAD_X + i0 * (CELL_S + GAP_S) + CELL_S / 2
            col_center_i1 = PAD_X + i1 * (CELL_S + GAP_S) + CELL_S / 2
            waveCenterX = col_center_i0 * (1 - frac) + col_center_i1 * frac

            points = []
            step = 1.5 * SUP
            x = PAD_X
            while x <= PAD_X + grid_w:
                dx = x - waveCenterX
                env = math.exp(-(dx * dx) / (2 * sigma_px * sigma_px))
                y = centerY - env * amplitude * edge_fade * math.cos(
                    2 * math.pi * dx / lambda_px
                )
                points.append((x, y))
                x += step

            overlay = Image.new("RGBA", (W_big, H_big), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)

            if len(points) > 1:
                poly = points + [
                    (points[-1][0], centerY),
                    (points[0][0], centerY),
                ]
                fill_alpha = int(255 * 0.04 * edge_fade)
                od.polygon(poly, fill=(167, 139, 250, fill_alpha))

            stroke_alpha = int(255 * 0.30 * edge_fade)
            for i in range(len(points) - 1):
                od.line(
                    [points[i], points[i + 1]],
                    fill=(167, 139, 250, stroke_alpha),
                    width=max(1, int(1.3 * SUP)),
                    joint="curve",
                )

            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(img)

        img_small = img.resize((W_final, H_final), Image.LANCZOS)
        images.append(img_small)

    out = OUT / "wave.gif"
    images[0].save(
        str(out),
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
    )
    print(f"OK {out}")

def main():
    build_gif()

if __name__ == "__main__":
    main()

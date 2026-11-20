#!/usr/bin/env python3
"""Render the make.fun v4 entry: a newspaper front page summing up Thursday
19 November 2026 with 33 stories.

Layout (1024x1024, drawn entirely offline with Pillow):
  * masthead carrying the date "THURSDAY 19 NOVEMBER 2026", a story-count
    strip per region, six big statistics from the day, and a "HOW SURE ARE
    WE?" verification line
  * 3 BIG features, each with a detailed code-drawn cartoon scene and a
    confidence tag (REPORTED / FORECAST / CLAIM)
  * 10 MEDIUM features, each with a small scene, region tag, confidence tag,
    headline and a one-line sourced subline
  * a "MARKETS & MONEY" box with the day's market-moving numbers
  * a "THE DAY BY HOURS" timeline (times verified from primary sources, UTC)
  * 20 more stories as a compact "ALSO ON THURSDAY 19 NOVEMBER" list
  * a world-map panel with numbered pins for the illustrated stories
  * a "DATE CHECK" box naming the stories left out as other days' news
  * a footer crediting the source outlets

Everything is embedded below: no network, no external assets, deterministic.
Running this writes entry.png next to it.

    python3 render.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

from worldmap import LAND

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

W = H = 1024

# ---------------------------------------------------------------- palette ---
BG = (246, 243, 235)
INK = (26, 23, 18)
MUTED = (104, 99, 89)
ACCENT = (161, 20, 32)
HAIR = (222, 215, 203)
PANEL = (255, 255, 255)
CARDBD = (226, 219, 206)
SEA = (214, 230, 240)
GREEN = (24, 128, 84)
BLUE = (28, 88, 160)
BOXBG = (250, 246, 236)

REGION_COLOR = {
    "Asia": (176, 58, 30),
    "Europe": (28, 88, 160),
    "Americas": (24, 128, 84),
    "Middle East": (186, 120, 16),
    "Africa": (128, 52, 148),
    "Oceania": (20, 128, 150),
    "Global": (84, 84, 84),
}

# confidence tag colours (background, text)
CONF_COLOR = {
    "REPORTED": ((22, 110, 74), (255, 255, 255)),
    "FORECAST": ((196, 138, 12), (255, 255, 255)),
    "CLAIM": ((176, 32, 40), (255, 255, 255)),
}

# ------------------------------------------------------------------ fonts ---
_font_cache = {}


def F(size, bold=True, serif=False):
    key = (size, bold, serif)
    f = _font_cache.get(key)
    if f is None:
        if serif:
            path = FONT_SERIF_BOLD if bold else FONT_REG
        else:
            path = FONT_BOLD if bold else FONT_REG
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
    return f


def wrap(d, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ctext(d, cx, y, text, fnt, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2.0, y), text, font=fnt, fill=fill)


def fit_lines(d, text, maxw, maxlines, s_hi, s_lo, serif=False):
    for size in range(s_hi, s_lo - 1, -1):
        f = F(size, bold=True, serif=serif)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
    f = F(s_lo, bold=True, serif=serif)
    return f, wrap(d, text, f, maxw)


def fit_single(d, text, maxw, s_hi=11, s_lo=7):
    for size in range(s_hi, s_lo - 1, -1):
        f = F(size)
        if d.textlength(text, font=f) <= maxw:
            return f
    return F(s_lo)


# ------------------------------------------------------------------ flags ---
def _frame(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def flag_h(d, x, y, w, h, cols):
    n = len(cols)
    for i, c in enumerate(cols):
        d.rectangle([x, y + h * i / n, x + w, y + h * (i + 1) / n], fill=c)


def flag_v(d, x, y, w, h, cols):
    n = len(cols)
    for i, c in enumerate(cols):
        d.rectangle([x + w * i / n, y, x + w * (i + 1) / n, y + h], fill=c)


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for k in range(0, 13, 2):
        d.rectangle([x, y + h * k / 13.0, x + w, y + h * (k + 1) / 13.0],
                    fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.42, y + h * 7 / 13.0], fill=(20, 40, 110))
    for r in range(3):
        for c in range(4):
            d.ellipse([x + w * (0.05 + 0.10 * c) - 1, y + h * (0.03 + 0.14 * r) - 1,
                       x + w * (0.05 + 0.10 * c) + 1, y + h * (0.03 + 0.14 * r) + 1],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    for i, (fx, fy, r) in enumerate([(0.24, 0.30, 0.20), (0.36, 0.16, 0.07),
                                     (0.42, 0.30, 0.07), (0.38, 0.44, 0.07)]):
        d.ellipse([x + w * fx - h * r, y + h * fy - h * r,
                   x + w * fx + h * r, y + h * fy + h * r],
                  fill=(255, 222, 23))


def flag_ru(d, x, y, w, h):
    flag_h(d, x, y, w, h, [(255, 255, 255), (0, 57, 166), (213, 43, 30)])


def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 12, 48))
    d.rectangle([x + w * 0.28, y, x + w * 0.40, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))


def flag_kr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    cx, cy = x + w / 2.0, y + h / 2.0
    r = h * 0.28
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(205, 46, 58))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 180, fill=(0, 71, 160))
    d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4],
              fill=(255, 255, 255))


def flag_id(d, x, y, w, h):
    flag_h(d, x, y, w, h, [(206, 17, 38), (255, 255, 255)])


def flag_co(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.5], fill=(252, 209, 22))
    d.rectangle([x, y + h * 0.5, x + w, y + h * 0.75], fill=(0, 48, 135))
    d.rectangle([x, y + h * 0.75, x + w, y + h], fill=(206, 17, 38))


def flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 36, 125))
    d.rectangle([x, y, x + w * 0.5, y + h * 0.5], fill=(255, 255, 255))
    d.line([(x, y), (x + w * 0.5, y + h * 0.5)], fill=(200, 16, 46), width=2)
    d.line([(x + w * 0.5, y), (x, y + h * 0.5)], fill=(200, 16, 46), width=2)
    for fx, fy in [(0.72, 0.30), (0.80, 0.60), (0.62, 0.72)]:
        d.ellipse([x + w * fx - 2, y + h * fy - 2, x + w * fx + 2, y + h * fy + 2],
                  fill=(255, 255, 255))


def flag_ke(d, x, y, w, h):
    flag_h(d, x, y, w, h, [(0, 0, 0), (255, 255, 255), (187, 0, 0),
                           (255, 255, 255), (0, 100, 0)])
    cx = x + w / 2.0
    d.ellipse([cx - h * 0.12, y + h * 0.32, cx + h * 0.12, y + h * 0.68],
              fill=(187, 0, 0), outline=(255, 255, 255))


def flag_sn(d, x, y, w, h):
    flag_v(d, x, y, w, h, [(0, 133, 63), (253, 239, 66), (227, 27, 35)])
    d.ellipse([x + w / 2 - 2, y + h / 2 - 2, x + w / 2 + 2, y + h / 2 + 2],
              fill=(0, 133, 63))


def flag_tr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(227, 10, 23))
    cx, cy = x + w * 0.42, y + h / 2.0
    r = h * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.ellipse([cx - r * 0.62, cy - r * 0.78, cx + r * 1.18, cy + r * 0.78],
              fill=(227, 10, 23))
    d.ellipse([cx + r * 0.9 - 3, cy - 3, cx + r * 0.9 + 3, cy + 3],
              fill=(255, 255, 255))


def flag_ua(d, x, y, w, h):
    flag_h(d, x, y, w, h, [(0, 87, 183), (255, 215, 0)])


# ---------------------------------------------------------------- scenes ----
def _burst(d, cx, cy, r_out, r_in, n, fill, rot=0):
    pts = []
    for k in range(2 * n):
        rr = r_out if k % 2 == 0 else r_in
        a = math.radians(rot + k * 180.0 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def _cloud(d, x, y, s, col):
    d.ellipse([x, y, x + s, y + s * 0.62], fill=col)
    d.ellipse([x + s * 0.5, y - s * 0.18, x + s * 1.5, y + s * 0.5], fill=col)
    d.ellipse([x + s * 1.0, y, x + s * 1.9, y + s * 0.6], fill=col)


def _figure(d, cx, base, s, skin=(236, 200, 168), suit=(60, 70, 90)):
    hr = s * 0.5
    d.ellipse([cx - hr, base - s * 1.7, cx + hr, base - s * 0.7],
              fill=skin, outline=INK, width=1)
    d.polygon([(cx - s * 1.05, base), (cx + s * 1.05, base),
               (cx + s * 0.72, base - s * 0.85), (cx - s * 0.72, base - s * 0.85)],
              fill=suit, outline=INK)


def scene_summit(d, x, y, w, h):
    """Trump-Xi-Putin trilateral summit, Shenzhen (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(206, 220, 236))
    _cloud(d, x + w * 0.06, y + h * 0.06, w * 0.16, (232, 238, 246))
    _cloud(d, x + w * 0.70, y + h * 0.04, w * 0.14, (232, 238, 246))
    # convention-hall backdrop with columns
    d.rectangle([x + w * 0.05, y + h * 0.12, x + w * 0.95, y + h * 0.80],
                fill=(226, 216, 196), outline=INK)
    for i in range(9):
        cx = x + w * (0.10 + 0.10 * i)
        d.rectangle([cx - w * 0.006, y + h * 0.14, cx + w * 0.006, y + h * 0.78],
                    fill=(205, 193, 172))
    # red banner
    d.rectangle([x + w * 0.20, y + h * 0.15, x + w * 0.80, y + h * 0.30], fill=ACCENT)
    ctext(d, x + w * 0.5, y + h * 0.185, "SHENZHEN 2026", F(9, bold=True),
          (255, 255, 255))
    ctext(d, x + w * 0.5, y + h * 0.235, "TRILATERAL SUMMIT", F(6, bold=True),
          (255, 226, 226))
    # flags
    fw, fh, fy = w * 0.15, h * 0.15, y + h * 0.33
    flag_us(d, x + w * 0.12, fy, fw, fh)
    flag_cn(d, x + w * 0.43, fy, fw, fh)
    flag_ru(d, x + w * 0.74, fy, fw, fh)
    for fx in (0.12, 0.43, 0.74):
        _frame(d, x + w * fx, fy, fw, fh)
    # three leaders
    for i, lab in enumerate(["TRUMP", "XI", "PUTIN"]):
        fx = x + w * (0.24 + 0.26 * i)
        _figure(d, fx, y + h * 0.74, w * 0.045)
        d.text((fx - d.textlength(lab, font=F(6, bold=True)) / 2, y + h * 0.5),
               lab, font=F(6, bold=True), fill=INK)
    # table with folders + mikes
    d.rounded_rectangle([x + w * 0.07, y + h * 0.74, x + w * 0.93, y + h * 0.90],
                        radius=5, fill=(150, 108, 66), outline=INK)
    for i in range(3):
        px = x + w * (0.24 + 0.26 * i)
        d.rectangle([px - w * 0.05, y + h * 0.78, px + w * 0.05, y + h * 0.84],
                    fill=(255, 255, 255), outline=INK)
        d.line([(px + w * 0.03, y + h * 0.78), (px + w * 0.03, y + h * 0.70)],
               fill=INK, width=1)
        d.ellipse([px + w * 0.018, y + h * 0.685, px + w * 0.042, y + h * 0.705],
                  fill=(40, 40, 40))
    ctext(d, x + w * 0.5, y + h * 0.915, "SIDE BY SIDE IN SHENZHEN", F(6, bold=True),
          INK)


def scene_ipo(d, x, y, w, h):
    """Anthropic Nasdaq debut (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 20, 38))
    # ticker bar
    d.rectangle([x, y, x + w, y + h * 0.13], fill=(6, 9, 18))
    ctext(d, x + w * 0.5, y + h * 0.015, "NASDAQ  ANT  ANTHROPIC", F(8, bold=True),
          (90, 200, 240))
    sx0, sy0, sx1, sy1 = x + w * 0.06, y + h * 0.18, x + w * 0.94, y + h * 0.60
    d.rectangle([sx0, sy0, sx1, sy1], fill=(8, 12, 24), outline=GREEN, width=2)
    for gx in range(1, 5):  # gridlines
        gyy = sy0 + (sy1 - sy0) * gx / 5.0
        d.line([(sx0, gyy), (sx1, gyy)], fill=(24, 40, 40), width=1)
    # rising line
    pts = [(sx0 + (sx1 - sx0) * f, sy1 - (sy1 - sy0) * v)
           for f, v in [(0.04, 0.16), (0.22, 0.30), (0.40, 0.26), (0.58, 0.55),
                        (0.78, 0.74), (0.96, 0.94)]]
    d.line(pts, fill=(60, 220, 130), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 8, pts[-1][1] - 3),
               (pts[-1][0] - 3, pts[-1][1] + 8)], fill=(60, 220, 130))
    d.text((sx0 + 6, sy0 + h * 0.16), "ANT", font=F(12, bold=True), fill=(255, 255, 255))
    d.text((sx0 + w * 0.30, sy0 + h * 0.16), "$111.50", font=F(12, bold=True),
           fill=(255, 255, 255))
    d.text((sx0 + 6, sy0 + h * 0.34), "▲ 34%", font=F(11, bold=True), fill=(60, 220, 130))
    d.text((sx0 + w * 0.36, sy0 + h * 0.34), "IPO $83", font=F(7, bold=True),
           fill=(150, 180, 200))
    # opening bell
    d.line([(x + w * 0.09, y + h * 0.68), (x + w * 0.09, y + h * 0.74)], fill=(200, 200, 120), width=2)
    d.polygon([(x + w * 0.075, y + h * 0.74), (x + w * 0.105, y + h * 0.74),
               (x + w * 0.105, y + h * 0.70), (x + w * 0.075, y + h * 0.70)],
              fill=(220, 200, 90), outline=INK)
    # crowd
    for i in range(9):
        cx = x + w * (0.18 + 0.085 * i)
        d.ellipse([cx - 3, y + h * 0.80 - 3, cx + 3, y + h * 0.80 + 3],
                  fill=(96, 106, 126))
        d.rectangle([cx - 4, y + h * 0.80, cx + 4, y + h * 0.92], fill=(72, 82, 102))
    ctext(d, x + w * 0.5, y + h * 0.93, "NASDAQ DEBUT · NEW YORK", F(8, bold=True),
          (220, 220, 230))


def scene_icj(d, x, y, w, h):
    """ICJ rules Myanmar committed genocide, The Hague (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 216, 232))
    _cloud(d, x + w * 0.62, y + h * 0.05, w * 0.14, (222, 236, 248))
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(120, 140, 120))
    bx0, bx1 = x + w * 0.15, x + w * 0.85
    top = y + h * 0.30
    d.rectangle([bx0, top, bx1, y + h * 0.80], fill=(238, 230, 210), outline=INK)
    for i in range(7):
        cx = bx0 + (bx1 - bx0) * (0.06 + 0.147 * i)
        d.rectangle([cx - w * 0.017, top + h * 0.05, cx + w * 0.017, y + h * 0.80],
                    fill=(214, 204, 184), outline=(120, 110, 96))
    d.polygon([(bx0 - w * 0.035, top), (bx1 + w * 0.035, top),
               (x + w * 0.5, y + h * 0.10)], fill=(230, 222, 200), outline=INK)
    # scales of justice
    cx, cy = x + w * 0.5, y + h * 0.215
    d.line([(cx, cy - h * 0.07), (cx, cy + h * 0.06)], fill=(150, 110, 20), width=2)
    d.line([(cx - w * 0.07, cy - h * 0.04), (cx + w * 0.07, cy - h * 0.04)],
           fill=(150, 110, 20), width=2)
    for sx in (cx - w * 0.07, cx + w * 0.07):
        d.line([(sx, cy - h * 0.04), (sx, cy + h * 0.02)], fill=(150, 110, 20), width=1)
        d.arc([sx - w * 0.03, cy - h * 0.01, sx + w * 0.03, cy + h * 0.05],
              0, 180, fill=(150, 110, 20), width=2)
    d.text((bx0 + w * 0.02, y + h * 0.60), "9–6", font=F(15, bold=True), fill=ACCENT)
    d.text((bx0 + w * 0.30, y + h * 0.60), "GENOCIDE", font=F(8, bold=True), fill=INK)
    ctext(d, x + w * 0.5, y + h * 0.85, "THE HAGUE", F(8, bold=True), (50, 60, 50))


def scene_riyadh(d, x, y, w, h):
    """Houthi missiles hit a Riyadh tower (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 58, 80))
    _cloud(d, x + w * 0.04, y + h * 0.05, w * 0.12, (74, 80, 104))
    d.ellipse([x + w * 0.68, y + h * 0.08, x + w * 0.90, y + h * 0.28],
              fill=(240, 220, 150))
    for i, (fx, fw, fh) in enumerate([(0.05, 0.15, 0.40), (0.22, 0.13, 0.28),
                                      (0.62, 0.15, 0.34), (0.79, 0.16, 0.24)]):
        d.rectangle([x + w * fx, y + h * (0.92 - fh), x + w * (fx + fw),
                     y + h * 0.92], fill=(78, 86, 110))
        for r in range(3):
            for c in range(2):
                d.rectangle([x + w * (fx + 0.025 + c * 0.06),
                             y + h * (0.92 - fh + 0.06 + 0.10 * r),
                             x + w * (fx + 0.045 + c * 0.06),
                             y + h * (0.92 - fh + 0.09 + 0.10 * r)],
                            fill=(240, 220, 150))
    tx = x + w * 0.42
    d.rectangle([tx, y + h * 0.20, tx + w * 0.13, y + h * 0.92], fill=(108, 116, 138))
    for r in range(4):
        d.rectangle([tx + w * 0.025, y + h * (0.26 + 0.14 * r),
                     tx + w * 0.105, y + h * (0.30 + 0.14 * r)], fill=(200, 190, 150))
    _burst(d, tx + w * 0.065, y + h * 0.26, w * 0.17, w * 0.075, 11, (233, 150, 30))
    _burst(d, tx + w * 0.065, y + h * 0.26, w * 0.10, w * 0.045, 9, (214, 60, 40))
    for k in range(3):  # missile trails
        d.line([(x, y + h * 0.10), (tx - w * 0.02, y + h * 0.22)], fill=(255, 130, 90), width=2)
    for k in range(3):  # smoke
        d.ellipse([tx + w * 0.10 + k * w * 0.05 - 5, y + h * 0.16 - k * h * 0.05 - 5,
                   tx + w * 0.10 + k * w * 0.05 + 5, y + h * 0.16 - k * h * 0.05 + 5],
                  fill=(150, 150, 160))


def scene_gta(d, x, y, w, h):
    """GTA VI launches worldwide (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(28, 22, 52))
    d.ellipse([x + w * 0.72, y + h * 0.06, x + w * 0.9, y + h * 0.20],
              fill=(250, 220, 150))
    for i, (fx, fw, fh) in enumerate([(0.04, 0.13, 0.52), (0.20, 0.15, 0.70),
                                      (0.39, 0.12, 0.48), (0.55, 0.15, 0.64),
                                      (0.74, 0.18, 0.56)]):
        d.rectangle([x + w * fx, y + h * (0.94 - fh), x + w * (fx + fw),
                     y + h * 0.94], fill=(46, 40, 78))
        for r in range(4):
            for c in range(2):
                d.rectangle([x + w * (fx + 0.025 + c * 0.055),
                             y + h * (0.94 - fh + 0.06 + 0.11 * r),
                             x + w * (fx + 0.045 + c * 0.055),
                             y + h * (0.94 - fh + 0.09 + 0.11 * r)],
                            fill=(240, 210, 120))
    d.rectangle([x + w * 0.28, y + h * 0.06, x + w * 0.72, y + h * 0.34],
                fill=(40, 36, 70), outline=(250, 190, 60), width=2)
    ctext(d, x + w * 0.5, y + h * 0.08, "VI", F(20, bold=True), (250, 190, 60))
    ctext(d, x + w * 0.5, y + h * 0.27, "VICE CITY", F(6, bold=True), (200, 180, 120))
    for px in (0.09, 0.91):  # palms
        bx, by = x + w * px, y + h * 0.94
        d.line([(bx, by), (bx, by - h * 0.30)], fill=(120, 96, 54), width=2)
        for a in (200, 250, 300, 340):
            d.line([(bx, by - h * 0.30),
                    (bx + 0.11 * w * math.cos(math.radians(a)),
                     by - h * 0.30 + 0.09 * h * math.sin(math.radians(a)))],
                   fill=(56, 150, 92), width=2)
    # road
    d.rectangle([x, y + h * 0.94, x + w, y + h], fill=(30, 28, 40))


def scene_cop31(d, x, y, w, h):
    """COP31 draft drops fossil fuels, Antalya (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 224, 232))
    _cloud(d, x + w * 0.05, y + h * 0.05, w * 0.13, (226, 236, 244))
    cr = min(w, h) * 0.33
    cx, cy = x + w * 0.40, y + h * 0.56
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(96, 158, 208),
              outline=(40, 90, 140))
    d.ellipse([cx - cr * 0.7, cy - cr * 0.6, cx - cr * 0.05, cy + cr * 0.1],
              fill=(104, 168, 110))
    d.ellipse([cx + cr * 0.1, cy - cr * 0.1, cx + cr * 0.75, cy + cr * 0.5],
              fill=(104, 168, 110))
    d.ellipse([cx - cr * 0.5, cy + cr * 0.3, cx + cr * 0.1, cy + cr * 0.8],
              fill=(104, 168, 110))
    d.line([(cx - cr, cy), (cx + cr, cy)], fill=(255, 255, 255, 60), width=1)
    tx = x + w * 0.82
    d.rounded_rectangle([tx - 3, y + h * 0.16, tx + 3, y + h * 0.60], radius=3,
                        fill=(255, 255, 255), outline=INK)
    d.rectangle([tx - 2, y + h * 0.32, tx + 2, y + h * 0.60], fill=(214, 60, 40))
    d.ellipse([tx - 7, y + h * 0.58, tx + 7, y + h * 0.72], fill=(214, 60, 40))
    d.rectangle([x + w * 0.05, y + h * 0.60, x + w * 0.15, y + h * 0.92],
                fill=(120, 120, 128))
    for k in range(3):
        d.ellipse([x + w * 0.05 + k * 2 - 6, y + h * 0.56 - k * h * 0.08 - 5,
                   x + w * 0.05 + k * 2 + 6, y + h * 0.56 - k * h * 0.08 + 5],
                  fill=(180, 180, 186))
    ctext(d, x + w * 0.5, y + h * 0.9, "COP31", F(8, bold=True), INK)


def scene_cyclone(d, x, y, w, h):
    """Cyclone Akvan nears India's coast (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(120, 150, 168))
    _cloud(d, x + w * 0.30, y + h * 0.05, w * 0.20, (96, 122, 142))
    _cloud(d, x + w * 0.55, y + h * 0.02, w * 0.16, (86, 112, 132))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(40, 90, 130))
    d.polygon([(x, y + h * 0.72), (x + w * 0.40, y + h * 0.66), (x + w * 0.40, y + h),
               (x, y + h)], fill=(120, 150, 90))
    hx, hy = x + w * 0.15, y + h * 0.50
    d.polygon([(hx - w * 0.09, hy + h * 0.16), (hx + w * 0.09, hy + h * 0.16),
               (hx + w * 0.09, hy), (hx - w * 0.09, hy)], fill=(224, 214, 194))
    d.polygon([(hx - w * 0.11, hy), (hx + w * 0.11, hy), (hx, hy - h * 0.12)],
              fill=(170, 70, 60))
    for k in range(3):  # palm
        bx = x + w * (0.30 + 0.03 * k)
        d.line([(bx, y + h * 0.72), (bx - w * 0.02, y + h * 0.56)], fill=(90, 70, 40), width=2)
    cx, cy = x + w * 0.64, y + h * 0.40
    R = min(w, h) * 0.34
    for k in range(3):
        f = 1 - k * 0.3
        d.arc([cx - R * f, cy - R * f, cx + R * f, cy + R * f], 200 + k * 40,
              200 + k * 40 + 220, fill=(240, 240, 250), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(240, 240, 250))
    for k in range(4):
        d.line([(x + w * (0.5 + 0.1 * k), y + h * 0.6),
                (x + w * (0.46 + 0.1 * k), y + h * 0.82)], fill=(200, 220, 235),
               width=1)


def scene_denmark(d, x, y, w, h):
    """Denmark ratifies the Arctic security pact, 109-0 (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(186, 216, 232))
    d.polygon([(x, y + h * 0.7), (x + w * 0.5, y + h * 0.2),
               (x + w, y + h * 0.7)], fill=(240, 246, 250))
    d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(150, 196, 224))
    for i in range(3):  # ice floes
        d.polygon([(x + w * (0.10 + 0.26 * i), y + h * 0.80),
                   (x + w * (0.18 + 0.26 * i), y + h * 0.74),
                   (x + w * (0.30 + 0.26 * i), y + h * 0.82),
                   (x + w * (0.20 + 0.26 * i), y + h * 0.9)], fill=(255, 255, 255))
    fw, fh = w * 0.19, h * 0.19
    flag_dk(d, x + w * 0.10, y + h * 0.10, fw, fh)
    _frame(d, x + w * 0.10, y + h * 0.10, fw, fh)
    flag_us(d, x + w * 0.70, y + h * 0.10, fw, fh)
    _frame(d, x + w * 0.70, y + h * 0.10, fw, fh)
    ctext(d, x + w * 0.5, y + h * 0.44, "109–0", F(13, bold=True), ACCENT)
    ctext(d, x + w * 0.5, y + h * 0.88, "ARCTIC PACT", F(7, bold=True), (40, 70, 100))


def scene_colombia(d, x, y, w, h):
    """Colombia national strike (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 196))
    flag_co(d, x + w * 0.02, y + h * 0.02, w * 0.20, h * 0.13)
    _frame(d, x + w * 0.02, y + h * 0.02, w * 0.20, h * 0.13)
    cols = [(206, 17, 38), (252, 209, 22), (0, 48, 135), (206, 17, 38), (60, 60, 60)]
    for i in range(8):
        fx = x + w * (0.07 + 0.115 * i)
        d.rectangle([fx - 5, y + h * 0.56, fx + 5, y + h * 0.9],
                    fill=cols[i % len(cols)])
        d.ellipse([fx - 5, y + h * 0.44, fx + 5, y + h * 0.54], fill=(230, 200, 170))
    for i in range(2):  # placards
        px = x + w * (0.24 + 0.4 * i)
        d.line([(px, y + h * 0.5), (px, y + h * 0.24)], fill=(120, 90, 60), width=2)
        d.rectangle([px - w * 0.10, y + h * 0.06, px + w * 0.10, y + h * 0.22],
                    fill=(255, 255, 255), outline=INK)
        d.text((px - w * 0.075, y + h * 0.10), "PARO", font=F(7, bold=True), fill=ACCENT)


def scene_australia(d, x, y, w, h):
    """Australia's jobless rate hits 4.9% (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 226))
    ax, ay, bx, by = x + w * 0.12, y + h * 0.16, x + w * 0.88, y + h * 0.88
    d.line([(ax, ay), (ax, by)], fill=INK, width=2)
    d.line([(ax, by), (bx, by)], fill=INK, width=2)
    vals = [0.30, 0.44, 0.60, 0.88]
    for i, v in enumerate(vals):
        cx = ax + (i + 0.5) * ((bx - ax) / len(vals))
        bw = (bx - ax) / (len(vals) * 1.8)
        d.rectangle([cx - bw / 2, by - (by - ay) * v, cx + bw / 2, by],
                    fill=ACCENT if i == len(vals) - 1 else BLUE)
    d.line([(ax + w * 0.06, by - h * 0.12), (bx - w * 0.03, ay + h * 0.04)],
           fill=GREEN, width=2)
    d.text((x + w * 0.60, y + h * 0.18), "4.9%", font=F(13, bold=True), fill=ACCENT)
    flag_au(d, x + w * 0.76, y + h * 0.03, w * 0.20, h * 0.12)
    _frame(d, x + w * 0.76, y + h * 0.03, w * 0.20, h * 0.12)


def scene_han(d, x, y, w, h):
    """Retrial ordered for ex-PM Han, Seoul (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 212, 226))
    d.rectangle([x + w * 0.14, y + h * 0.40, x + w * 0.86, y + h * 0.86],
                fill=(238, 230, 210), outline=INK)
    d.polygon([(x + w * 0.10, y + h * 0.40), (x + w * 0.90, y + h * 0.40),
               (x + w * 0.5, y + h * 0.16)], fill=(228, 220, 200), outline=INK)
    for i in range(5):
        cx = x + w * (0.22 + 0.14 * i)
        d.rectangle([cx - w * 0.018, y + h * 0.44, cx + w * 0.018, y + h * 0.86],
                    fill=(214, 204, 184), outline=(120, 110, 96))
    flag_kr(d, x + w * 0.04, y + h * 0.04, w * 0.20, h * 0.14)
    _frame(d, x + w * 0.04, y + h * 0.04, w * 0.20, h * 0.14)
    ctext(d, x + w * 0.5, y + h * 0.88, "RETRIAL", F(8, bold=True), ACCENT)


def scene_jepchirchir(d, x, y, w, h):
    """Marathon champion banned for doping, Kenya (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(224, 232, 222))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(196, 110, 84))
    rx, ry = x + w * 0.40, y + h * 0.34
    d.ellipse([rx - 5, ry - 10, rx + 5, ry], fill=(90, 60, 40))
    d.line([(rx, ry), (rx - w * 0.06, ry + h * 0.22)], fill=(206, 60, 40), width=4)
    d.line([(rx - w * 0.06, ry + h * 0.22), (rx - w * 0.12, ry + h * 0.44)],
           fill=INK, width=3)
    d.line([(rx - w * 0.06, ry + h * 0.22), (rx + w * 0.03, ry + h * 0.44)],
           fill=INK, width=3)
    d.line([(rx, ry), (rx + w * 0.08, ry + h * 0.06)], fill=(90, 60, 40), width=3)
    d.line([(rx, ry), (rx - w * 0.10, ry + h * 0.06)], fill=(90, 60, 40), width=3)
    mx, my = x + w * 0.74, y + h * 0.26
    d.line([(mx, my - h * 0.14), (mx, my)], fill=(200, 40, 40), width=2)
    d.ellipse([mx - 6, my, mx + 6, my + 12], fill=(240, 200, 60), outline=(150, 110, 20))
    d.ellipse([x + w * 0.56, y + h * 0.46, x + w * 0.98, y + h * 0.92],
              outline=(206, 30, 30), width=4)
    d.line([(x + w * 0.60, y + h * 0.86), (x + w * 0.94, y + h * 0.52)],
           fill=(206, 30, 30), width=4)


def scene_indonesia(d, x, y, w, h):
    """Indonesia passes an asset-forfeiture law (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 218))
    flag_id(d, x + w * 0.04, y + h * 0.04, w * 0.20, h * 0.13)
    _frame(d, x + w * 0.04, y + h * 0.04, w * 0.20, h * 0.13)
    gx, gy = x + w * 0.34, y + h * 0.42
    d.rounded_rectangle([gx - w * 0.15, gy - h * 0.06, gx + w * 0.15, gy + h * 0.06],
                        radius=3, fill=(150, 108, 66), outline=INK)
    d.line([(gx, gy + h * 0.05), (gx + w * 0.1, gy + h * 0.3)], fill=(120, 90, 60),
           width=3)
    d.rectangle([gx - w * 0.19, y + h * 0.72, gx + w * 0.19, y + h * 0.82],
                fill=(120, 90, 60), outline=INK)
    bx, by = x + w * 0.72, y + h * 0.60
    d.ellipse([bx - w * 0.15, by - h * 0.1, bx + w * 0.15, by + h * 0.26],
              fill=(240, 210, 90), outline=(150, 120, 20))
    d.text((bx - 4, by - h * 0.01), "$", font=F(13, bold=True), fill=(120, 90, 10))
    ctext(d, x + w * 0.5, y + h * 0.87, "18-YEAR WAIT", F(7, bold=True), INK)


def scene_berlin(d, x, y, w, h):
    """European leaders meet in Berlin on Ukraine (19 Nov)."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 214, 232))
    # Brandenburg-gate style monument
    d.rectangle([x + w * 0.30, y + h * 0.22, x + w * 0.70, y + h * 0.74],
                fill=(232, 226, 210), outline=INK)
    d.polygon([(x + w * 0.26, y + h * 0.22), (x + w * 0.74, y + h * 0.22),
               (x + w * 0.5, y + h * 0.08)], fill=(226, 220, 202), outline=INK)
    for i in range(5):
        cx = x + w * (0.36 + 0.07 * i)
        d.rectangle([cx - w * 0.012, y + h * 0.26, cx + w * 0.012, y + h * 0.74],
                    fill=(210, 202, 184))
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(150, 168, 150))
    fw, fh = w * 0.16, h * 0.16
    flag_ua(d, x + w * 0.06, y + h * 0.08, fw, fh)
    _frame(d, x + w * 0.06, y + h * 0.08, fw, fh)
    ctext(d, x + w * 0.5, y + h * 0.84, "BERLIN", F(8, bold=True), (40, 60, 40))


# ------------------------------------------------------------- world map ----
def _poly_bbox(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


_BBOX = [_poly_bbox(r) for r in LAND]


def _inside(px, py, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > py) != (yj > py):
            if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat):
    for ring, (x0, y0, x1, y1) in zip(LAND, _BBOX):
        if lon < x0 or lon > x1 or lat < y0 or lat > y1:
            continue
        if _inside(lon, lat, ring):
            return True
    return False


LAT0, LAT1 = -52.0, 84.0


def draw_map(d, x0, y0, mw, mh, feats):
    d.rectangle([x0, y0, x0 + mw, y0 + mh], fill=SEA)

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (LAT1 - lat) / (LAT1 - LAT0) * mh)

    for ring in LAND:
        pts = [proj(lon, lat) for lon, lat in ring]
        d.polygon(pts, fill=(205, 203, 192), outline=(170, 170, 158))

    ex0, ey0 = proj(-180, 0)
    ex1, _ = proj(180, 0)
    d.line([(ex0, ey0), (ex1, ey0)], fill=(255, 255, 255), width=1)

    pos = [list(proj(f[7], f[8])) for f in feats]
    orig = [list(p) for p in pos]
    min_d = 22.0
    for _ in range(60):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[i][0] - pos[j][0]
                dy = pos[i][1] - pos[j][1]
                dist = math.hypot(dx, dy)
                if dist < min_d:
                    if dist < 0.01:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (min_d - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    pos[i][0] += ux * push
                    pos[i][1] += uy * push
                    pos[j][0] -= ux * push
                    pos[j][1] -= uy * push
                    moved = True
        if not moved:
            break
    for p in pos:
        p[0] = min(max(p[0], x0 + 10), x0 + mw - 10)
        p[1] = min(max(p[1], y0 + 10), y0 + mh - 10)

    r = 8
    for i, f in enumerate(feats):
        ox, oy = orig[i]
        px, py = pos[i]
        if math.hypot(px - ox, py - oy) > 4:
            d.line([(ox, oy), (px, py)], fill=(120, 120, 120), width=1)
    for i, f in enumerate(feats):
        px, py = pos[i]
        col = REGION_COLOR[f[2]]
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=2)
        nf = F(9, bold=True)
        num = str(f[0])
        d.text((px - d.textlength(num, font=nf) / 2, py - nf.size * 0.6),
               num, font=nf, fill=(255, 255, 255))


# ------------------------------------------------------------------ data ----
# BIG features: (n, scene, region, tag, headline, subline, conf, lon, lat)
BIG = [
    (1, scene_summit, "Asia", "ASIA · DIPLOMACY",
     "First Trump–Xi–Putin trilateral summit, in Shenzhen",
     "Joint declaration on oil, nuclear risk and UN reform", "REPORTED", 114.1, 22.6),
    (2, scene_ipo, "Americas", "AMERICAS · TECH & MARKETS",
     "Anthropic debuts on Nasdaq in record $100bn+ IPO",
     "Shares open 34% above the $83 IPO price", "REPORTED", -74.0, 40.7),
    (3, scene_icj, "Europe", "EUROPE · JUSTICE",
     "ICJ: Myanmar committed genocide against Rohingya",
     "World Court votes 9–6, in The Hague", "REPORTED", 4.3, 52.1),
]

# MEDIUM features: (n, scene, region, tag, headline, subline, conf, lon, lat)
MED = [
    (4, scene_riyadh, "Middle East", "M. EAST · RIYADH",
     "Houthi missiles hit a Riyadh tower",
     "Saudi-led coalition repels the barrage", "CLAIM", 46.7, 24.7),
    (5, scene_gta, "Global", "GLOBAL · WORLDWIDE",
     "GTA VI launches after a 13-year wait",
     "Gamers queue worldwide", "REPORTED", -80.2, 25.8),
    (6, scene_cop31, "Europe", "EUROPE · ANTALYA",
     "COP31 draft drops fossil fuels",
     "Fossil fuels cut from the deal text", "REPORTED", 30.7, 36.9),
    (7, scene_cyclone, "Asia", "ASIA · ODISHA, INDIA",
     "Cyclone Akvan nears India's coast",
     "Hundreds of thousands evacuated", "FORECAST", 85.9, 20.3),
    (8, scene_denmark, "Europe", "EUROPE · COPENHAGEN",
     "Denmark ratifies Arctic pact, 109–0",
     "US–Greenland security deal", "REPORTED", 12.6, 55.7),
    (9, scene_colombia, "Americas", "AMERICAS · BOGOTÁ",
     "Colombia hit by a national strike",
     "Unions block roads and the airport", "REPORTED", -74.1, 4.7),
    (10, scene_australia, "Oceania", "OCEANIA · CANBERRA",
     "Australia's jobless rate hits 4.9%",
     "A five-year high, on ABS data", "REPORTED", 149.1, -35.3),
    (11, scene_han, "Asia", "ASIA · SEOUL",
     "Court overturns ex-PM Han's conviction",
     "Retrial ordered over martial law", "REPORTED", 127.0, 37.6),
    (12, scene_jepchirchir, "Africa", "AFRICA · KENYA",
     "Marathon champion banned for doping",
     "Jepchirchir gets three years", "REPORTED", 35.3, 0.5),
    (13, scene_indonesia, "Asia", "ASIA · JAKARTA",
     "Indonesia passes asset-seizure law",
     "After an 18-year wait", "REPORTED", 106.8, -6.2),
]

# ALSO list: (n, text)
ALSO = [
    (14, "Suneung: 551,864 sit Korea's exam — AFP"),
    (15, "Ukraine allies meet in Berlin on Nov 19 — AFP"),
    (16, "Nvidia subpoenaed by California AG — CNBC"),
    (17, "US cleared ~900,000 AI chips for China — Al Jazeera"),
    (18, "Intuit sells Mailchimp for $3.68bn — CNBC"),
    (19, "Walmart raises its full-year outlook — CNBC"),
    (20, "Senate rejects war-powers curb, 48–51 — Al Jazeera"),
    (21, "Somalia expels the UAE ambassador — Africanews"),
    (22, "Kenya awards minerals contract to US — Africanews"),
    (23, "Turkey bars Istanbul mayor from 2028 race — Euronews"),
    (24, "Hegseth lands in Ecuador on drugs tour — Euronews"),
    (25, "El Salvador: Bukele bids for a third term — Reuters"),
    (26, "Mongolia's parliament accepts president's exit — AP"),
    (27, "Philippines and Chile sign free trade deal — AFP"),
    (28, "Israel hits a Hezbollah site in Lebanon — AFP"),
    (29, "Migrant boat capsizes off Senegal — Reuters"),
    (30, "Red giant star caught eating its neighbour — ABC"),
    (31, "Magnitude 5.7 quake jolts Kumamoto — Japan Times"),
    (32, "“Huna” wins the National Book Award — NPR"),
    (33, "FIFA U-17 World Cup opens in Qatar — Euronews"),
]

FEATS = BIG + MED

MARKETS = [
    ("ANTHROPIC", "Opens at $111.50 on Nasdaq, +34% above the $83 IPO price; closes its first day +17% at $97.17"),
    ("INTUIT", "Agrees to sell Mailchimp to Bending Spoons for $3.68bn"),
    ("NVIDIA", "California's attorney general issues a subpoena over alleged China chip diversion"),
    ("US–CHINA", "House committee: ~900,000 AI chips cleared for China in six months"),
    ("WALMART", "Raises its full-year outlook after Q3 results"),
]

TIMELINE = [
    ("00:30 UTC", "ABS: Australia's jobless rate rises to 4.9%"),
    ("09:00 UTC", "ICJ delivers its genocide ruling, The Hague"),
    ("14:30 UTC", "Nasdaq opens; Anthropic trades at $111.50, +34%"),
    ("19:01 UTC", "US Senate rejects Iran war-powers curb, 48–51"),
    ("21:00 UTC", "US markets close; Anthropic ends its first day +17%"),
]

EXCLUDED = ("LEFT OUT AS OTHER DAYS' NEWS: Van Gogh $190.4m sale (Wed 18 Nov) · "
            "EU €45bn Ukraine loan proposal (Wed 18 Nov) · UK inflation 3.6% "
            "one-year high (ONS, Wed 18 Nov) · Clark elected Majority Leader / "
            "Jeffries nominated (Wed 18 Nov) · Voyager 1 one light-day out (Wed 18 Nov) · "
            "Nvidia results (Wed 18 Nov) · Giannis Heat–Bucks game (Wed 18 Nov) · "
            "Egypt–IMF pact (Tue 18 Nov) · Florida deluge (Tue–Wed) · "
            "Kerch Bridge strike (reported 20 Nov).")


# --------------------------------------------------------------- the page ---
def draw_conf(d, x, y, kind):
    bg, fg = CONF_COLOR[kind]
    f = F(8, bold=True)
    tw = d.textlength(kind, font=f)
    d.rounded_rectangle([x, y, x + tw + 12, y + 13], radius=6, fill=bg)
    d.text((x + 6, y + 1), kind, font=f, fill=fg)
    return tw + 12


def draw_tag(d, x, y, tag, col):
    d.rectangle([x, y + 2, x + 3, y + 9], fill=col)
    d.text((x + 7, y), tag, font=F(8, bold=True), fill=col)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 12
    cx = W / 2.0

    # ---------------- masthead ----------------
    d.text((M, 2), "33 STORIES · ILLUSTRATED", font=F(11, bold=True), fill=MUTED)
    right = "ONE PAGE · THU 19 NOV 2026"
    d.text((W - M - d.textlength(right, font=F(11, bold=True)), 2), right,
           font=F(11, bold=True), fill=MUTED)
    name = "THE WORLD TODAY"
    ctext(d, cx, 12, name, F(30, bold=True, serif=True), INK)
    date = "THURSDAY 19 NOVEMBER 2026"
    ctext(d, cx, 46, date, F(34, bold=True), ACCENT)
    d.rectangle([M, 84, W - M, 87], fill=INK)
    regions = ("33 STORIES   ASIA 8 · EUROPE 5 · AMERICAS 9 · MIDDLE EAST 3 · "
               "AFRICA 4 · OCEANIA 1 · GLOBAL 3")
    ctext(d, cx, 90, regions, F(11, bold=True), INK)
    stats = ("$111.50 ANTHROPIC · 9–6 ICJ · 109–0 DENMARK · 4.9% AUSTRALIA · "
             "551,864 SUNEUNG · 48–51 SENATE")
    ctext(d, cx, 104, stats, F(11, bold=True), ACCENT)
    howsure = ("HOW SURE ARE WE? 33 stories, each checked against a primary outlet for "
               "its EVENT date; 10 other-day stories left out (see DATE CHECK).")
    ctext(d, cx, 118, howsure, F(9, bold=True), MUTED)
    d.rectangle([M, 131, W - M, 132], fill=HAIR)

    # ---------------- 3 BIG features ----------------
    by0, by1 = 136, 372
    gap = 9
    cellw = (W - 2 * M - 2 * gap) / 3.0
    for c in range(3):
        bx = M + c * (cellw + gap)
        d.rectangle([bx, by0, bx + cellw, by1], fill=PANEL, outline=CARDBD, width=1)
        n, scene, region, tag, head, sub, conf = BIG[c][:7]
        col = REGION_COLOR[region]
        sh = 138
        scene(d, bx + 4, by0 + 4, cellw - 8, sh)
        d.rectangle([bx + 4, by0 + 4, bx + cellw - 4, by0 + 4 + sh],
                    outline=CARDBD, width=1)
        d.ellipse([bx + 8, by0 + 8, bx + 30, by0 + 30], fill=col,
                  outline=(255, 255, 255), width=2)
        nf = F(13, bold=True)
        d.text((bx + 19 - d.textlength(str(n), font=nf) / 2, by0 + 11), str(n),
               font=nf, fill=(255, 255, 255))
        ty = by0 + sh + 9
        draw_tag(d, bx + 8, ty, tag, col)
        pw = d.textlength(conf, font=F(8, bold=True)) + 12
        draw_conf(d, bx + cellw - 8 - pw, ty - 1, conf)
        ty += 14
        fh, hl = fit_lines(d, head, cellw - 16, 3, 18, 12, serif=True)
        for ln in hl:
            d.text((bx + 8, ty), ln, font=fh, fill=INK)
            ty += int(fh.size * 1.05)
        fs, sl = fit_lines(d, sub, cellw - 16, 2, 10, 8)
        ty += 1
        for ln in sl:
            d.text((bx + 8, ty), ln, font=fs, fill=MUTED)
            ty += int(fs.size * 1.16)

    # ---------------- 10 MEDIUM features ----------------
    my0, my1 = 376, 556
    cols, rows = 5, 2
    gap = 7
    mcw = (W - 2 * M - (cols - 1) * gap) / cols
    mch = (my1 - my0) / rows
    for i, f in enumerate(MED):
        r, c = divmod(i, cols)
        bx = M + c * (mcw + gap)
        by = my0 + r * mch
        d.rectangle([bx + 1, by + 1, bx + mcw - 2, by + mch - 2], fill=PANEL,
                    outline=CARDBD, width=1)
        n, scene, region, tag, head, sub, conf = f[:7]
        col = REGION_COLOR[region]
        sw = 52
        scene(d, bx + 5, by + 5, sw, mch - 10)
        d.rectangle([bx + 5, by + 5, bx + 5 + sw, by + mch - 5], outline=CARDBD, width=1)
        d.ellipse([bx + 5, by + 5, bx + 19, by + 19], fill=col,
                  outline=(255, 255, 255), width=1)
        d.text((bx + 12 - d.textlength(str(n), font=F(9, bold=True)) / 2, by + 6),
               str(n), font=F(9, bold=True), fill=(255, 255, 255))
        tx = bx + 5 + sw + 6
        tw = mcw - (tx - bx) - 5
        ty = by + 5
        d.text((tx, ty), tag, font=F(7, bold=True), fill=col)
        ty += 11
        fh, hl = fit_lines(d, head, tw, 3, 13, 9, serif=True)
        for ln in hl:
            d.text((tx, ty), ln, font=fh, fill=INK)
            ty += int(fh.size * 1.02)
        fs, sl = fit_lines(d, sub, tw, 2, 9, 7)
        ty += 1
        for ln in sl[:2]:
            d.text((tx, ty), ln, font=fs, fill=MUTED)
            ty += int(fs.size * 1.16)
        draw_conf(d, bx + mcw - 5 - (d.textlength(conf, font=F(7, bold=True)) + 9),
                  by + 5, conf)

    # ---------------- bottom band ----------------
    bandy0, bandy1 = 560, 998
    rightx = 664

    # ---- left column: markets ----
    mk = [M, bandy0, rightx - 8, bandy0 + 98]
    d.rectangle(mk, fill=BOXBG, outline=ACCENT, width=2)
    d.rectangle([mk[0], mk[1], mk[2], mk[1] + 17], fill=ACCENT)
    d.text((mk[0] + 8, mk[1] + 2), "MARKETS & MONEY", font=F(11, bold=True),
           fill=(255, 255, 255))
    fy = mk[1] + 22
    for lab, txt in MARKETS:
        fl = F(8, bold=True)
        d.text((mk[0] + 9, fy + 1), lab, font=fl, fill=ACCENT)
        lw = d.textlength(lab, font=fl)
        ft = fit_single(d, txt, mk[2] - (mk[0] + 9 + lw + 8) - 6, s_hi=8, s_lo=7)
        d.text((mk[0] + 9 + lw + 7, fy), txt, font=ft, fill=INK)
        fy += 15

    # ---- left column: day by hours ----
    tl = [M, bandy0 + 102, rightx - 8, bandy0 + 210]
    d.rectangle(tl, fill=PANEL, outline=INK, width=2)
    d.text((tl[0] + 8, tl[1] + 3), "THE DAY BY HOURS", font=F(12, bold=True), fill=INK)
    d.text((tl[2] - 8 - d.textlength("times in UTC", font=F(8)),
            tl[1] + 6), "times in UTC", font=F(8), fill=MUTED)
    d.rectangle([tl[0] + 8, tl[1] + 19, tl[2] - 8, tl[1] + 20], fill=HAIR)
    ry = tl[1] + 23
    for t, txt in TIMELINE:
        ft = F(9, bold=True)
        d.text((tl[0] + 8, ry), t, font=ft, fill=ACCENT)
        tw = d.textlength(t, font=ft)
        d.text((tl[0] + 8 + tw + 7, ry), txt, font=F(9), fill=INK)
        ry += 16

    # ---- left column: world map ----
    mp = [M, bandy0 + 214, rightx - 8, bandy1]
    d.rectangle(mp, fill=PANEL, outline=INK, width=2)
    d.text((mp[0] + 10, mp[1] + 4), "WHERE IT HAPPENED", font=F(13, bold=True), fill=INK)
    note = "pins 1–13 mark the illustrated stories"
    d.text((mp[2] - 10 - d.textlength(note, font=F(8)), mp[1] + 8), note,
           font=F(8), fill=MUTED)
    mwid = mp[2] - mp[0] - 24
    mhgt = int(round(mwid * (LAT1 - LAT0) / 360.0))
    avail_h = mp[3] - (mp[1] + 26) - 30
    if mhgt > avail_h:
        mhgt = avail_h
        mwid = int(round(mhgt * 360.0 / (LAT1 - LAT0)))
    mapx = mp[0] + (mp[2] - mp[0] - mwid) / 2.0
    draw_map(d, mapx, mp[1] + 24, mwid, mhgt, FEATS)
    lregions = ["Asia", "Europe", "Americas", "Middle East", "Africa", "Oceania", "Global"]
    f_leg = F(8, bold=True)
    lx = mp[0] + 10
    ly = mp[1] + 27 + mhgt + 6
    for reg in lregions:
        lbl = reg.upper()
        itemw = 11 + d.textlength(lbl, font=f_leg) + 9
        if lx + itemw > mp[2] - 8:
            lx = mp[0] + 10
            ly += 12
        d.ellipse([lx, ly + 1, lx + 7, ly + 8], fill=REGION_COLOR[reg],
                  outline=(200, 195, 185), width=1)
        d.text((lx + 10, ly), lbl, font=f_leg, fill=INK)
        lx += itemw

    # ---- right column: ALSO list ----
    ar = [rightx, bandy0, W - M, bandy0 + 288]
    d.rectangle(ar, fill=PANEL, outline=INK, width=2)
    d.text((ar[0] + 10, ar[1] + 4), "ALSO ON THURSDAY 19 NOVEMBER",
           font=F(11, bold=True), fill=ACCENT)
    d.rectangle([ar[0] + 10, ar[1] + 22, ar[2] - 10, ar[1] + 23], fill=HAIR)
    nf = F(10, bold=True)
    ly = ar[1] + 27
    rowh = (ar[3] - 6 - ly) / len(ALSO)
    for n, text in ALSO:
        d.text((ar[0] + 9, ly + (rowh - nf.size) / 2.0 - 2), "%d" % n, font=nf,
               fill=ACCENT)
        tf = fit_single(d, text, ar[2] - (ar[0] + 30) - 8, s_hi=9, s_lo=7)
        d.text((ar[0] + 30, ly + (rowh - tf.size) / 2.0 - 1), text, font=tf, fill=INK)
        ly += rowh

    # ---- right column: date check ----
    dc = [rightx, bandy0 + 292, W - M, bandy1]
    d.rectangle(dc, fill=BOXBG, outline=ACCENT, width=2)
    d.rectangle([dc[0], dc[1], dc[2], dc[1] + 17], fill=ACCENT)
    d.text((dc[0] + 8, dc[1] + 2), "DATE CHECK", font=F(11, bold=True),
           fill=(255, 255, 255))
    dc_text = ("Every story on this page is an event of Thursday 19 November 2026. "
               + EXCLUDED)
    fdc = F(8)
    lines = wrap(d, dc_text, fdc, dc[2] - dc[0] - 18)
    ty = dc[1] + 21
    for ln in lines:
        d.text((dc[0] + 9, ty), ln, font=fdc, fill=INK)
        ty += 10

    # ---------------- footer ----------------
    d.rectangle([M, 999, W - M, 1000], fill=INK)
    ctext(d, cx, 1001, "Every story is an event of Thursday 19 November 2026.",
          F(10, bold=True), INK)
    foot = ("Sources: CNBC, Al Jazeera, NPR, Reuters, AP, AFP, Euronews, DW, Le Monde, "
            "The Guardian, BBC, Africanews, ABC News, The Japan Times, "
            "Straits Times, USA Today, ICJ, ABS, US Senate.")
    ctext(d, cx, 1013, foot, F(8), MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

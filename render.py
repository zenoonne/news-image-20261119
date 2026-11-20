#!/usr/bin/env python3
"""Render the make.fun v3 entry: a newspaper front page summing up Thursday
19 November 2026 with 33 stories.

Layout (1024x1024, drawn entirely offline with Pillow):
  * masthead carrying the date "THURSDAY 19 NOVEMBER 2026", a story-count
    strip per region and six big statistics from the day
  * 3 BIG features, each with a detailed code-drawn cartoon scene
  * 10 MEDIUM features, each with a small scene, region tag, headline and
    a one-line sourced subline
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
LANDC = (150, 160, 158)
GREEN = (24, 128, 84)
BLUE = (28, 88, 160)

REGION_COLOR = {
    "Asia": (176, 58, 30),
    "Europe": (28, 88, 160),
    "Americas": (24, 128, 84),
    "Middle East": (186, 120, 16),
    "Africa": (128, 52, 148),
    "Oceania": (20, 128, 150),
    "Global": (84, 84, 84),
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


def fit_single(d, text, maxw, s_hi=10, s_lo=7):
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


# ---------------------------------------------------------------- scenes ----
def _burst(d, cx, cy, r_out, r_in, n, fill, rot=0):
    pts = []
    for k in range(2 * n):
        rr = r_out if k % 2 == 0 else r_in
        a = math.radians(rot + k * 180.0 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def scene_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 222, 235))
    d.rectangle([x, y + h * 0.74, x + w, y + h], fill=(180, 168, 150))
    # banner
    d.rectangle([x + w * 0.20, y + h * 0.04, x + w * 0.80, y + h * 0.20],
                fill=ACCENT)
    ctext(d, x + w * 0.5, y + h * 0.075, "SHENZHEN 2026", F(9, bold=True),
          (255, 255, 255))
    # flags
    fw, fh, fy = w * 0.16, h * 0.17, y + h * 0.26
    flag_us(d, x + w * 0.10, fy, fw, fh)
    flag_cn(d, x + w * 0.42, fy, fw, fh)
    flag_ru(d, x + w * 0.74, fy, fw, fh)
    for fx in (0.10, 0.42, 0.74):
        _frame(d, x + w * fx, fy, fw, fh)
    # figures
    labels = ["TRUMP", "XI", "PUTIN"]
    for i, lab in enumerate(labels):
        fx = x + w * (0.22 + 0.28 * i)
        hr = h * 0.062
        cy = y + h * 0.52
        d.ellipse([fx - hr, cy - hr, fx + hr, cy + hr], fill=(236, 200, 168),
                  outline=INK, width=1)
        d.polygon([(fx - hr * 1.7, y + h * 0.74), (fx + hr * 1.7, y + h * 0.74),
                   (fx + hr * 1.2, cy + hr), (fx - hr * 1.2, cy + hr)],
                  fill=(60, 70, 90), outline=INK)
        d.text((fx - d.textlength(lab, font=F(7, bold=True)) / 2, cy - hr - 9),
               lab, font=F(7, bold=True), fill=INK)
    # table
    d.rounded_rectangle([x + w * 0.06, y + h * 0.74, x + w * 0.94, y + h * 0.90],
                        radius=5, fill=(150, 108, 66), outline=INK)
    for i in range(3):
        px = x + w * (0.22 + 0.28 * i)
        d.rectangle([px - w * 0.045, y + h * 0.80, px + w * 0.045, y + h * 0.85],
                    fill=(255, 255, 255), outline=INK)
        ctext(d, px, y + h * 0.805, "●", F(6, bold=True), BLUE)


def scene_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))
    sx0, sy0, sx1, sy1 = x + w * 0.06, y + h * 0.07, x + w * 0.94, y + h * 0.60
    d.rectangle([sx0, sy0, sx1, sy1], fill=(8, 12, 24), outline=GREEN, width=2)
    d.text((sx0 + 6, sy0 + 3), "ANTHROPIC", font=F(8, bold=True), fill=(90, 200, 240))
    # rising line
    pts = [(sx0 + (sx1 - sx0) * f, sy1 - (sy1 - sy0) * v)
           for f, v in [(0.06, 0.22), (0.25, 0.34), (0.44, 0.30), (0.62, 0.58),
                        (0.80, 0.72), (0.94, 0.92)]]
    d.line(pts, fill=(60, 220, 130), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 7, pts[-1][1] - 2),
               (pts[-1][0] - 2, pts[-1][1] + 7)], fill=(60, 220, 130))
    d.text((sx0 + 6, sy0 + h * 0.22), "ANT", font=F(11, bold=True), fill=(255, 255, 255))
    d.text((sx0 + w * 0.34, sy0 + h * 0.22), "$111.50", font=F(11, bold=True),
           fill=(255, 255, 255))
    d.text((sx0 + 6, sy0 + h * 0.38), "▲ 34%", font=F(10, bold=True), fill=(60, 220, 130))
    # crowd row
    for i in range(9):
        cx = x + w * (0.10 + 0.10 * i)
        d.ellipse([cx - 3, y + h * 0.72 - 3, cx + 3, y + h * 0.72 + 3],
                  fill=(90, 100, 120))
        d.rectangle([cx - 4, y + h * 0.72, cx + 4, y + h * 0.86], fill=(70, 80, 100))
    ctext(d, x + w * 0.5, y + h * 0.87, "NASDAQ DEBUT · NEW YORK", F(8, bold=True),
          (220, 220, 230))


def scene_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 216, 232))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(120, 140, 120))
    bx0, bx1 = x + w * 0.16, x + w * 0.84
    top = y + h * 0.30
    d.rectangle([bx0, top, bx1, y + h * 0.78], fill=(238, 230, 210), outline=INK)
    for i in range(6):
        cx = bx0 + (bx1 - bx0) * (0.08 + 0.168 * i)
        d.rectangle([cx - w * 0.018, top + h * 0.06, cx + w * 0.018, y + h * 0.78],
                    fill=(214, 204, 184), outline=(120, 110, 96))
    d.polygon([(bx0 - w * 0.03, top), (bx1 + w * 0.03, top),
               (x + w * 0.5, y + h * 0.12)], fill=(238, 230, 210), outline=INK)
    # scales emblem
    cx, cy = x + w * 0.5, y + h * 0.20
    d.line([(cx, cy - h * 0.05), (cx, cy + h * 0.05)], fill=(150, 110, 20), width=2)
    d.line([(cx - w * 0.06, cy - h * 0.03), (cx + w * 0.06, cy - h * 0.03)],
           fill=(150, 110, 20), width=2)
    d.text((bx0, y + h * 0.58), "9–6", font=F(15, bold=True), fill=ACCENT)
    ctext(d, x + w * 0.5, y + h * 0.84, "THE HAGUE", F(8, bold=True), (60, 70, 60))


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(56, 62, 84))
    d.ellipse([x + w * 0.66, y + h * 0.08, x + w * 0.9, y + h * 0.3],
              fill=(240, 220, 150))
    for i, (fx, fw, fh) in enumerate([(0.06, 0.16, 0.42), (0.24, 0.14, 0.30),
                                      (0.62, 0.16, 0.36), (0.80, 0.16, 0.26)]):
        d.rectangle([x + w * fx, y + h * (0.92 - fh), x + w * (fx + fw),
                     y + h * 0.92], fill=(84, 92, 116))
        for r in range(3):
            d.rectangle([x + w * (fx + 0.03), y + h * (0.92 - fh + 0.06 + 0.1 * r),
                         x + w * (fx + fw - 0.03), y + h * (0.92 - fh + 0.09 + 0.1 * r)],
                        fill=(240, 220, 150))
    # the hit tower
    tx = x + w * 0.44
    d.rectangle([tx, y + h * 0.20, tx + w * 0.12, y + h * 0.92], fill=(110, 118, 140))
    _burst(d, tx + w * 0.06, y + h * 0.26, w * 0.16, w * 0.07, 11, (233, 150, 30))
    _burst(d, tx + w * 0.06, y + h * 0.26, w * 0.09, w * 0.04, 9, (214, 60, 40))
    for k in range(3):
        d.ellipse([tx + w * 0.10 + k * w * 0.05 - 5, y + h * 0.16 - k * h * 0.05 - 5,
                   tx + w * 0.10 + k * w * 0.05 + 5, y + h * 0.16 - k * h * 0.05 + 5],
                  fill=(160, 160, 170))
    d.line([(x, y + h * 0.06), (tx + w * 0.02, y + h * 0.22)], fill=(255, 120, 90),
           width=2)


def scene_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 22, 48))
    for i, (fx, fw, fh) in enumerate([(0.05, 0.14, 0.55), (0.22, 0.16, 0.72),
                                      (0.42, 0.13, 0.5), (0.58, 0.16, 0.66),
                                      (0.78, 0.17, 0.58)]):
        d.rectangle([x + w * fx, y + h * (0.94 - fh), x + w * (fx + fw),
                     y + h * 0.94], fill=(44, 40, 74))
        for r in range(4):
            for c in range(2):
                d.rectangle([x + w * (fx + 0.03 + c * 0.06),
                             y + h * (0.94 - fh + 0.06 + 0.12 * r),
                             x + w * (fx + 0.05 + c * 0.06),
                             y + h * (0.94 - fh + 0.09 + 0.12 * r)],
                            fill=(240, 210, 120))
    # VI billboard
    d.rectangle([x + w * 0.30, y + h * 0.06, x + w * 0.70, y + h * 0.34],
                fill=(40, 36, 70), outline=(250, 190, 60), width=2)
    ctext(d, x + w * 0.5, y + h * 0.09, "VI", F(20, bold=True), (250, 190, 60))
    # palms
    for px in (0.10, 0.90):
        bx, by = x + w * px, y + h * 0.94
        d.line([(bx, by), (bx, by - h * 0.3)], fill=(90, 70, 40), width=2)
        for a in (200, 250, 300, 340):
            d.line([(bx, by - h * 0.3),
                    (bx + 0.12 * w * math.cos(math.radians(a)),
                     by - h * 0.3 + 0.1 * h * math.sin(math.radians(a)))],
                   fill=(46, 130, 80), width=2)


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 224, 232))
    cr = min(w, h) * 0.34
    cx, cy = x + w * 0.42, y + h * 0.54
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(96, 158, 208),
              outline=(40, 90, 140))
    d.ellipse([cx - cr * 0.7, cy - cr * 0.6, cx - cr * 0.05, cy + cr * 0.1],
              fill=(104, 168, 110))
    d.ellipse([cx + cr * 0.1, cy - cr * 0.1, cx + cr * 0.75, cy + cr * 0.5],
              fill=(104, 168, 110))
    d.ellipse([cx - cr * 0.5, cy + cr * 0.3, cx + cr * 0.1, cy + cr * 0.8],
              fill=(104, 168, 110))
    # thermometer
    tx = x + w * 0.82
    d.rounded_rectangle([tx - 3, y + h * 0.18, tx + 3, y + h * 0.62], radius=3,
                        fill=(255, 255, 255), outline=INK)
    d.rectangle([tx - 2, y + h * 0.34, tx + 2, y + h * 0.62], fill=(214, 60, 40))
    d.ellipse([tx - 7, y + h * 0.6, tx + 7, y + h * 0.74], fill=(214, 60, 40))
    # smokestack
    d.rectangle([x + w * 0.06, y + h * 0.62, x + w * 0.16, y + h * 0.92],
                fill=(120, 120, 128))
    for k in range(3):
        d.ellipse([x + w * 0.06 + k * 2 - 6, y + h * 0.58 - k * h * 0.08 - 5,
                   x + w * 0.06 + k * 2 + 6, y + h * 0.58 - k * h * 0.08 + 5],
                  fill=(180, 180, 186))
    ctext(d, x + w * 0.5, y + h * 0.9, "COP31", F(8, bold=True), INK)


def scene_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 150, 168))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(40, 90, 130))
    # coast with house
    d.polygon([(x, y + h * 0.72), (x + w * 0.4, y + h * 0.68), (x + w * 0.4, y + h),
               (x, y + h)], fill=(120, 150, 90))
    hx, hy = x + w * 0.16, y + h * 0.5
    d.polygon([(hx - w * 0.09, hy + h * 0.16), (hx + w * 0.09, hy + h * 0.16),
               (hx + w * 0.09, hy), (hx - w * 0.09, hy)], fill=(220, 210, 190))
    d.polygon([(hx - w * 0.11, hy), (hx + w * 0.11, hy),
               (hx, hy - h * 0.12)], fill=(170, 70, 60))
    # spiral
    cx, cy = x + w * 0.64, y + h * 0.4
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
    d.rectangle([x, y, x + w, y + h], fill=(186, 216, 232))
    d.polygon([(x, y + h * 0.7), (x + w * 0.5, y + h * 0.2),
               (x + w, y + h * 0.7)], fill=(240, 246, 250))
    d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(150, 196, 224))
    d.polygon([(x + w * 0.28, y + h * 0.72), (x + w * 0.44, y + h * 0.5),
               (x + w * 0.6, y + h * 0.72)], fill=(255, 255, 255))
    fw, fh = w * 0.2, h * 0.2
    flag_dk(d, x + w * 0.10, y + h * 0.12, fw, fh)
    _frame(d, x + w * 0.10, y + h * 0.12, fw, fh)
    flag_us(d, x + w * 0.70, y + h * 0.12, fw, fh)
    _frame(d, x + w * 0.70, y + h * 0.12, fw, fh)
    ctext(d, x + w * 0.5, y + h * 0.76, "109–0", F(11, bold=True), ACCENT)


def scene_colombia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 196))
    flag_co(d, x + w * 0.02, y + h * 0.02, w * 0.2, h * 0.14)
    _frame(d, x + w * 0.02, y + h * 0.02, w * 0.2, h * 0.14)
    cols = [(206, 17, 38), (252, 209, 22), (0, 48, 135), (206, 17, 38), (60, 60, 60)]
    for i in range(7):
        fx = x + w * (0.08 + 0.13 * i)
        d.rectangle([fx - 5, y + h * 0.56, fx + 5, y + h * 0.9],
                    fill=cols[i % len(cols)])
        d.ellipse([fx - 5, y + h * 0.44, fx + 5, y + h * 0.54], fill=(230, 200, 170))
    # placards
    for i in range(3):
        px = x + w * (0.16 + 0.3 * i)
        d.line([(px, y + h * 0.5), (px, y + h * 0.24)], fill=(120, 90, 60), width=2)
        d.rectangle([px - w * 0.09, y + h * 0.06, px + w * 0.09, y + h * 0.22],
                    fill=(255, 255, 255), outline=INK)


def scene_australia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 226))
    ax, ay, bx, by = x + w * 0.12, y + h * 0.14, x + w * 0.9, y + h * 0.88
    d.line([(ax, ay), (ax, by)], fill=INK, width=2)
    d.line([(ax, by), (bx, by)], fill=INK, width=2)
    vals = [0.3, 0.44, 0.6, 0.86]
    for i, v in enumerate(vals):
        cx = ax + (i + 0.5) * ((bx - ax) / len(vals))
        bw = (bx - ax) / (len(vals) * 1.7)
        d.rectangle([cx - bw / 2, by - (by - ay) * v, cx + bw / 2, by],
                    fill=ACCENT if i == len(vals) - 1 else BLUE)
    d.line([(ax + w * 0.06, by - h * 0.12), (bx - w * 0.05, ay + h * 0.06)],
           fill=GREEN, width=2)
    d.text((x + w * 0.62, y + h * 0.2), "4.9%", font=F(12, bold=True), fill=ACCENT)
    flag_au(d, x + w * 0.78, y + h * 0.03, w * 0.18, h * 0.12)


def scene_han(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 212, 226))
    d.rectangle([x + w * 0.14, y + h * 0.4, x + w * 0.86, y + h * 0.86],
                fill=(238, 230, 210), outline=INK)
    d.polygon([(x + w * 0.1, y + h * 0.4), (x + w * 0.9, y + h * 0.4),
               (x + w * 0.5, y + h * 0.16)], fill=(238, 230, 210), outline=INK)
    for i in range(4):
        cx = x + w * (0.24 + 0.17 * i)
        d.rectangle([cx - w * 0.02, y + h * 0.44, cx + w * 0.02, y + h * 0.86],
                    fill=(214, 204, 184), outline=(120, 110, 96))
    flag_kr(d, x + w * 0.04, y + h * 0.04, w * 0.2, h * 0.14)
    _frame(d, x + w * 0.04, y + h * 0.04, w * 0.2, h * 0.14)
    ctext(d, x + w * 0.5, y + h * 0.88, "RETRIAL", F(8, bold=True), ACCENT)


def scene_jepchirchir(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(224, 232, 222))
    # runner
    rx, ry = x + w * 0.42, y + h * 0.4
    d.ellipse([rx - 5, ry - 10, rx + 5, ry], fill=(90, 60, 40))
    d.line([(rx, ry), (rx - w * 0.06, ry + h * 0.22)], fill=(206, 60, 40), width=4)
    d.line([(rx - w * 0.06, ry + h * 0.22), (rx - w * 0.12, ry + h * 0.42)],
           fill=INK, width=3)
    d.line([(rx - w * 0.06, ry + h * 0.22), (rx + w * 0.02, ry + h * 0.42)],
           fill=INK, width=3)
    d.line([(rx, ry), (rx + w * 0.08, ry + h * 0.06)], fill=(90, 60, 40), width=3)
    d.line([(rx, ry), (rx - w * 0.1, ry + h * 0.06)], fill=(90, 60, 40), width=3)
    # medal
    mx, my = x + w * 0.72, y + h * 0.3
    d.line([(mx, my - h * 0.16), (mx, my)], fill=(200, 40, 40), width=2)
    d.ellipse([mx - 6, my, mx + 6, my + 12], fill=(240, 200, 60), outline=(150, 110, 20))
    # ban sign
    d.ellipse([x + w * 0.6, y + h * 0.5, x + w * 0.96, y + h * 0.92],
              outline=(206, 30, 30), width=4)
    d.line([(x + w * 0.64, y + h * 0.86), (x + w * 0.92, y + h * 0.56)],
           fill=(206, 30, 30), width=4)


def scene_indonesia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 218))
    flag_id(d, x + w * 0.04, y + h * 0.04, w * 0.2, h * 0.13)
    _frame(d, x + w * 0.04, y + h * 0.04, w * 0.2, h * 0.13)
    # gavel
    gx, gy = x + w * 0.34, y + h * 0.44
    d.rounded_rectangle([gx - w * 0.14, gy - h * 0.06, gx + w * 0.14, gy + h * 0.06],
                        radius=3, fill=(150, 108, 66), outline=INK)
    d.line([(gx, gy + h * 0.05), (gx + w * 0.1, gy + h * 0.3)], fill=(120, 90, 60),
           width=3)
    d.rectangle([gx - w * 0.18, y + h * 0.72, gx + w * 0.18, y + h * 0.82],
                fill=(120, 90, 60), outline=INK)
    # money bag
    bx, by = x + w * 0.7, y + h * 0.62
    d.ellipse([bx - w * 0.14, by - h * 0.1, bx + w * 0.14, by + h * 0.24],
              fill=(240, 210, 90), outline=(150, 120, 20))
    d.text((bx - 4, by - h * 0.02), "$", font=F(12, bold=True), fill=(120, 90, 10))
    ctext(d, x + w * 0.5, y + h * 0.86, "18-YEAR WAIT", F(7, bold=True), INK)


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

    # land as lightly filled polygons (from the v1/v2 polygons), not bare dots
    for ring in LAND:
        pts = [proj(lon, lat) for lon, lat in ring]
        d.polygon(pts, fill=(205, 203, 192), outline=(170, 170, 158))

    ex0, ey0 = proj(-180, 0)
    ex1, _ = proj(180, 0)
    d.line([(ex0, ey0), (ex1, ey0)], fill=(255, 255, 255), width=1)

    pos = [list(proj(f[6], f[7])) for f in feats]
    orig = [list(p) for p in pos]
    min_d = 24.0
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
        p[0] = min(max(p[0], x0 + 11), x0 + mw - 11)
        p[1] = min(max(p[1], y0 + 11), y0 + mh - 11)

    r = 9
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
        nf = F(10, bold=True)
        num = str(f[0])
        d.text((px - d.textlength(num, font=nf) / 2, py - nf.size * 0.62),
               num, font=nf, fill=(255, 255, 255))


# ------------------------------------------------------------------ data ----
# BIG features: (n, scene, region, tag, headline, subline, lon, lat)
BIG = [
    (1, scene_summit, "Asia", "ASIA · DIPLOMACY",
     "First Trump–Xi–Putin trilateral summit, in Shenzhen",
     "Joint declaration on oil, nuclear risk and UN reform", 114.1, 22.6),
    (2, scene_ipo, "Americas", "AMERICAS · TECH & MARKETS",
     "Anthropic debuts on Nasdaq in record $100bn+ IPO",
     "Shares open 34% above the $83 IPO price", -74.0, 40.7),
    (3, scene_icj, "Europe", "EUROPE · JUSTICE",
     "ICJ: Myanmar committed genocide against Rohingya",
     "World Court votes 9–6, in The Hague", 4.3, 52.1),
]

# MEDIUM features: (n, scene, region, tag, headline, subline, lon, lat)
MED = [
    (4, scene_riyadh, "Middle East", "M. EAST · RIYADH",
     "Houthi missiles hit a Riyadh tower",
     "Saudi-led coalition repels the barrage", 46.7, 24.7),
    (5, scene_gta, "Global", "GLOBAL · WORLDWIDE",
     "GTA VI launches after a 13-year wait",
     "Gamers queue worldwide", -80.2, 25.8),
    (6, scene_cop31, "Europe", "EUROPE · ANTALYA",
     "COP31 draft drops fossil fuels",
     "Fossil fuels cut from the deal text", 30.7, 36.9),
    (7, scene_cyclone, "Asia", "ASIA · ODISHA, INDIA",
     "Cyclone Akvan nears India's coast",
     "Hundreds of thousands evacuated", 85.9, 20.3),
    (8, scene_denmark, "Europe", "EUROPE · COPENHAGEN",
     "Denmark ratifies Arctic pact, 109–0",
     "US–Greenland security deal", 12.6, 55.7),
    (9, scene_colombia, "Americas", "AMERICAS · BOGOTÁ",
     "Colombia hit by a national strike",
     "Unions block roads and the airport", -74.1, 4.7),
    (10, scene_australia, "Oceania", "OCEANIA · CANBERRA",
     "Australia's jobless rate hits 4.9%",
     "A five-year high, on ABS data", 149.1, -35.3),
    (11, scene_han, "Asia", "ASIA · SEOUL",
     "Court overturns ex-PM Han's conviction",
     "Retrial ordered over martial law", 127.0, 37.6),
    (12, scene_jepchirchir, "Africa", "AFRICA · KENYA",
     "Marathon champion banned for doping",
     "Jepchirchir gets three years", 35.3, 0.5),
    (13, scene_indonesia, "Asia", "ASIA · JAKARTA",
     "Indonesia passes asset-seizure law",
     "After an 18-year wait", 106.8, -6.2),
]

# ALSO list: (n, text)
ALSO = [
    (14, "Suneung exam: 551,864 sit in Korea — Straits Times"),
    (15, "UK inflation hits a 12-month high — Euronews"),
    (16, "Nvidia handed a subpoena by California AG — CNBC"),
    (17, "US cleared ~900,000 AI chips for China — Al Jazeera"),
    (18, "Intuit sells Mailchimp for $3.68bn — CNBC"),
    (19, "Walmart raises its full-year outlook — CNBC"),
    (20, "Senate rejects war-powers curb, 51–48 — Al Jazeera"),
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
    (32, "\"Huna\" wins the National Book Award — NPR"),
    (33, "FIFA U-17 World Cup opens in Qatar — Euronews"),
]

FEATS = BIG + MED


# --------------------------------------------------------------- the page ---
def draw_tag(d, x, y, tag, col):
    d.rectangle([x, y + 2, x + 3, y + 9], fill=col)
    d.text((x + 7, y), tag, font=F(9, bold=True), fill=col)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 12
    cx = W / 2.0

    # ---------------- masthead ----------------
    d.text((M, 4), "33 STORIES", font=F(12, bold=True), fill=MUTED)
    d.text((W - M - d.textlength("ONE PAGE · ILLUSTRATED", font=F(12, bold=True)), 4),
           "ONE PAGE · ILLUSTRATED", font=F(12, bold=True), fill=MUTED)
    name = "THE WORLD TODAY"
    ctext(d, cx, 14, name, F(32, bold=True, serif=True), INK)
    date = "THURSDAY 19 NOVEMBER 2026"
    ctext(d, cx, 50, date, F(35, bold=True), ACCENT)
    d.rectangle([M, 92, W - M, 95], fill=INK)
    regions = ("33 STORIES   ASIA 8 · EUROPE 5 · AMERICAS 10 · MIDDLE EAST 3 · "
               "AFRICA 4 · OCEANIA 1 · GLOBAL 2")
    ctext(d, cx, 98, regions, F(12, bold=True), INK)
    stats = ("$100bn+ ANTHROPIC IPO   ·   9–6 ICJ RULING   ·   109–0 DENMARK   ·   "
             "4.9% AUSTRALIA   ·   551,864 SUNEUNG   ·   51–48 SENATE VOTE")
    ctext(d, cx, 113, stats, F(12, bold=True), ACCENT)
    d.rectangle([M, 130, W - M, 131], fill=HAIR)

    # ---------------- 3 BIG features ----------------
    by0, by1 = 136, 400
    gap = 10
    cellw = (W - 2 * M - 2 * gap) / 3.0
    for c in range(3):
        bx = M + c * (cellw + gap)
        d.rectangle([bx, by0, bx + cellw, by1], fill=PANEL, outline=CARDBD, width=1)
        n, scene, region, tag, head, sub = BIG[c][:6]
        col = REGION_COLOR[region]
        scene(d, bx + 4, by0 + 4, cellw - 8, 150)
        d.rectangle([bx + 4, by0 + 4, bx + cellw - 4, by0 + 154], outline=CARDBD, width=1)
        # big number chip
        d.ellipse([bx + 8, by0 + 8, bx + 30, by0 + 30], fill=col,
                  outline=(255, 255, 255), width=2)
        nf = F(13, bold=True)
        d.text((bx + 19 - d.textlength(str(n), font=nf) / 2, by0 + 11), str(n),
               font=nf, fill=(255, 255, 255))
        ty = by0 + 162
        draw_tag(d, bx + 8, ty, tag, col)
        ty += 14
        fh, hl = fit_lines(d, head, cellw - 16, 3, 19, 13, serif=True)
        for ln in hl:
            d.text((bx + 8, ty), ln, font=fh, fill=INK)
            ty += int(fh.size * 1.06)
        fs, sl = fit_lines(d, sub, cellw - 16, 2, 11, 9)
        ty += 1
        for ln in sl:
            d.text((bx + 8, ty), ln, font=fs, fill=MUTED)
            ty += int(fs.size * 1.2)

    # ---------------- 10 MEDIUM features ----------------
    my0, my1 = 404, 638
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
        n, scene, region, tag, head, sub = f[:6]
        col = REGION_COLOR[region]
        sw = 54
        scene(d, bx + 5, by + 5, sw, mch - 10)
        d.rectangle([bx + 5, by + 5, bx + 5 + sw, by + mch - 5], outline=CARDBD, width=1)
        # number chip
        d.ellipse([bx + 5, by + 5, bx + 19, by + 19], fill=col,
                  outline=(255, 255, 255), width=1)
        d.text((bx + 12 - d.textlength(str(n), font=F(9, bold=True)) / 2, by + 6),
               str(n), font=F(9, bold=True), fill=(255, 255, 255))
        tx = bx + 5 + sw + 6
        tw = mcw - (tx - bx) - 5
        ty = by + 5
        d.text((tx, ty), tag, font=F(7, bold=True), fill=col)
        ty += 10
        fh, hl = fit_lines(d, head, tw, 3, 13, 9, serif=True)
        for ln in hl:
            d.text((tx, ty), ln, font=fh, fill=INK)
            ty += int(fh.size * 1.02)
        fs, sl = fit_lines(d, sub, tw, 2, 9, 7)
        ty += 1
        for ln in sl[:2]:
            d.text((tx, ty), ln, font=fs, fill=MUTED)
            ty += int(fs.size * 1.16)

    # ---------------- bottom band ----------------
    boty = 642
    mapw = 632
    maph = 246
    d.rectangle([M, boty, M + mapw, boty + maph], fill=PANEL, outline=INK, width=2)
    d.text((M + 10, boty + 5), "WHERE IT HAPPENED", font=F(17, bold=True), fill=INK)
    note = "pins 1–13 mark the illustrated stories"
    d.text((M + mapw - 10 - d.textlength(note, font=F(9)), boty + 10), note,
           font=F(9), fill=MUTED)
    mwid = mapw - 24
    mhgt = int(round(mwid * (LAT1 - LAT0) / 360.0))
    draw_map(d, M + 12, boty + 30, mwid, mhgt, FEATS)
    # legend
    lregions = ["Asia", "Europe", "Americas", "Middle East", "Africa",
                "Oceania", "Global"]
    f_leg = F(9, bold=True)
    lx = M + 12
    ly = boty + 34 + mhgt + 6
    for reg in lregions:
        lbl = reg.upper()
        itemw = 12 + d.textlength(lbl, font=f_leg) + 9
        if lx + itemw > M + mapw - 8:
            lx = M + 12
            ly += 13
        d.ellipse([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLOR[reg],
                  outline=(200, 195, 185), width=1)
        d.text((lx + 11, ly), lbl, font=f_leg, fill=INK)
        lx += itemw

    # ---------------- date check box ----------------
    dcy = boty + maph + 6
    dch = 986 - dcy
    d.rectangle([M, dcy, M + mapw, dcy + dch], fill=(250, 246, 236),
                outline=ACCENT, width=2)
    d.text((M + 10, dcy + 5), "DATE CHECK", font=F(12, bold=True), fill=ACCENT)
    dc = ("Every story on this page is an event of Thursday 19 November 2026. "
          "LEFT OUT AS OTHER DAYS' NEWS: Van Gogh $190.4m sale (Wed 18 Nov) · "
          "EU €45bn Ukraine loan proposal (Wed 18 Nov) · Clark elected Majority "
          "Leader / Jeffries nominated (Wed 18 Nov) · Voyager 1 one light-day out "
          "(Wed 18 Nov) · Nvidia results (Wed 18 Nov) · Giannis Heat–Bucks game "
          "(Wed 18 Nov) · Egypt–IMF pact (Tue 18 Nov) · Florida deluge (Tue–Wed) · "
          "Kerch Bridge strike (reported 20 Nov).")
    fdc = F(9)
    dcl = wrap(d, dc, fdc, mapw - 24)
    ty = dcy + 20
    for ln in dcl:
        d.text((M + 10, ty), ln, font=fdc, fill=INK)
        ty += 11

    # ---------------- ALSO list ----------------
    lx0 = M + mapw + 8
    lw = W - M - lx0
    d.rectangle([lx0, boty, lx0 + lw, 986 - 6], fill=PANEL, outline=INK, width=2)
    d.text((lx0 + 10, boty + 5), "ALSO ON THURSDAY 19 NOVEMBER",
           font=F(13, bold=True), fill=ACCENT)
    d.rectangle([lx0 + 10, boty + 24, lx0 + lw - 10, boty + 25], fill=HAIR)
    nf = F(11, bold=True)
    ly = boty + 30
    rowh = (986 - 6 - 6 - ly) / len(ALSO)
    for n, text in ALSO:
        d.text((lx0 + 10, ly + 2), "%d" % n, font=nf, fill=ACCENT)
        tf = fit_single(d, text, lw - 40, s_hi=10, s_lo=7)
        d.text((lx0 + 34, ly + (rowh - tf.size) / 2.0 - 1), text, font=tf, fill=INK)
        ly += rowh

    # ---------------- footer ----------------
    d.rectangle([M, 990, W - M, 991], fill=INK)
    ctext(d, cx, 993, "Every story is an event of Thursday 19 November 2026.",
          F(11, bold=True), INK)
    foot = ("Sources: CNBC, Al Jazeera, NPR, Reuters, AP, AFP, Euronews, Le Monde, "
            "The Guardian, BBC, Africanews, ABC News, The Japan Times, Straits Times, USA Today.")
    ctext(d, cx, 1008, foot, F(9), MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

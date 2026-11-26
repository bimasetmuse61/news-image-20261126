#!/usr/bin/env python3
"""news-image-20261126: sum up Thursday 26 November 2026's world news
in one image.

Pure standard library (zlib, struct, os). Renders a 1024x1024 newspaper
front page to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png):
a masthead dated 26 November 2026, a lead story on the Houthi claim of
strikes on Saudi oil sites, and six more panels covering the day's
tariffs, markets, Cairo fire, BepiColombo, Ukraine and North Korea,
plus a ticker of further 26 November stories. Every pixel is drawn in
code; the program runs with no network and is fully deterministic.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (248, 244, 232)
INK = (18, 22, 34)
NAVY = (20, 33, 61)
NAVY_LT = (38, 58, 94)
RED = (178, 34, 34)
GOLD = (184, 134, 11)
GREY = (110, 108, 100)
LT_GREY = (214, 209, 196)
SKY = (174, 205, 225)
FLAME = (232, 98, 20)
FLAME_Y = (255, 190, 60)
GREEN = (34, 120, 70)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = bytes(c) * (x1 - x0)
            self.px[base:base + len(row)] = row

    def hline(self, x0, x1, y, c):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            self.set(x, y, c)

    def vline(self, x, y0, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for tx in range(thick):
                for ty in range(thick):
                    self.set(x + tx - thick // 2, y + ty - thick // 2, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, c)

    def triangle(self, p0, p1, p2, c):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        y0, y1 = min(ys), max(ys)
        for y in range(y0, y1 + 1):
            xs_at = []
            for (ax, ay), (bx, by) in ((p0, p1), (p1, p2), (p2, p0)):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    t = (y - ay) / (by - ay)
                    xs_at.append(ax + t * (bx - ax))
            if len(xs_at) >= 2:
                xa, xb = int(min(xs_at)), int(max(xs_at))
                for x in range(xa, xb + 1):
                    self.set(x, y, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, written out by hand for this entry.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
}
FONT.update({
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "\u2022": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
})


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    return len(text) * (6 * scale) - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw uppercase text; unknown chars render as spaces."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_lines(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(cv, x, y, text, max_width, scale, color, leading=4):
    lines = wrap_lines(text, max_width, scale)
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * (7 * scale + leading), line, scale, color)
    return y + len(lines) * (7 * scale + leading)


# ------------------------------------------------------------- illustrations
def draw_flame(cv, x, y, w, h):
    """A stylised flame inside box (x, y, w, h); y is the top."""
    cx = x + w // 2
    cv.triangle((cx - w // 2, y + h), (cx + w // 2, y + h),
                (cx, y), FLAME)
    cv.triangle((cx - w // 4, y + h), (cx + w // 4, y + h),
                (cx, y + h // 3), FLAME_Y)
    cv.triangle((cx - w // 6, y + h), (cx + w // 6, y + h),
                (cx, y + 2 * h // 3), (255, 235, 150))


def draw_smoke(cv, x, y, color=(150, 148, 140)):
    cv.circle(x, y, 9, color)
    cv.circle(x + 12, y - 8, 7, color)
    cv.circle(x - 10, y - 10, 6, color)


def draw_refinery(cv, x, y, w, h):
    """Oil refinery scene: sky, towers, tanks, flame, ground."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 42, y + 30, 20, (255, 214, 120))  # sun
    ground = y + h - 26
    cv.rect(x, ground, w, 26, (96, 88, 74))
    # distillation towers
    for i, th in enumerate((86, 108, 74)):
        tx = x + 24 + i * 52
        cv.rect(tx, ground - th, 30, th, (74, 78, 88))
        cv.rect(tx - 3, ground - th - 8, 36, 8, (74, 78, 88))
        cv.rect(tx + 4, ground - th + 10, 22, 4, (200, 200, 200))
        cv.rect(tx + 4, ground - th + 26, 22, 4, (200, 200, 200))
    # storage tanks
    for i in range(2):
        tx = x + 190 + i * 62
        cv.rect(tx, ground - 44, 52, 44, (210, 205, 190))
        cv.rect(tx - 3, ground - 50, 58, 6, (160, 155, 140))
    # pipes
    cv.rect(x + 24, ground - 14, w - 48, 5, (60, 62, 70))
    # flame on the right tower + smoke
    draw_flame(cv, x + w - 92, ground - 148, 34, 46)
    draw_smoke(cv, x + w - 76, ground - 156)
    draw_smoke(cv, x + w - 60, ground - 172)
    # oil barrel with $ sign
    cv.rect(x + 14, ground - 34, 26, 34, (30, 60, 110))
    draw_text(cv, x + 19, ground - 28, "$", 1, WHITE)


def draw_bars(cv, x, y, w, h):
    """Tariff bar chart: three rising bars with % labels."""
    cv.rect(x, y, w, h, (232, 226, 210))
    base = y + h - 14
    cv.hline(x + 6, x + w - 6, base, INK)
    labels = ("5%", "10%", "15%")
    heights = (h // 3, (2 * h) // 3, h - 26)
    cols = ((120, 140, 170), (200, 120, 60), RED)
    for i in range(3):
        bx = x + 14 + i * (w // 3)
        bh = heights[i]
        cv.rect(bx, base - bh, w // 3 - 20, bh, cols[i])
        draw_text(cv, bx + 2, base - bh - 12, labels[i], 1, INK)
    draw_text(cv, x + 8, y + 4, "DUTIES RISE", 1, INK)


def draw_crash_chart(cv, x, y, w, h):
    """Falling market line with a red arrow."""
    cv.rect(x, y, w, h, (232, 226, 210))
    pts = [(x + 8, y + 12), (x + w // 4, y + 18), (x + w // 2, y + h // 2),
           (x + 3 * w // 4, y + h - 26), (x + w - 10, y + h - 12)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, thick=3)
    ex, ey = pts[-1]
    cv.triangle((ex, ey + 2), (ex - 12, ey - 2), (ex - 2, ey - 12), RED)
    cv.circle(pts[0][0], pts[0][1], 3, INK)
    draw_text(cv, x + 8, y + 4, "NASDAQ", 1, INK)
    draw_text(cv, x + w - 44, y + 4, "-4%", 2, RED)


def draw_fire_scene(cv, x, y, w, h):
    """Highway, tanker and fire."""
    cv.rect(x, y, w, h, (232, 226, 210))
    cv.rect(x, y + h - 30, w, 30, (70, 70, 74))  # road
    for i in range(6):
        cv.rect(x + 8 + i * (w // 6), y + h - 17, 18, 3, (240, 220, 90))
    # tanker: cab + cylinder tank
    cv.rect(x + 14, y + h - 62, 34, 32, (170, 40, 30))
    cv.rect(x + 20, y + h - 56, 20, 10, SKY)
    cv.rect(x + 52, y + h - 58, w - 110, 28, (200, 196, 186))
    cv.circle(x + 52, y + h - 44, 14, (200, 196, 186))
    cv.circle(x + 30, y + h - 34, 8, INK)
    cv.circle(x + w - 34, y + h - 34, 8, INK)
    draw_flame(cv, x + w - 88, y + 8, 44, 52)
    draw_smoke(cv, x + w - 66, y + 12)
    draw_smoke(cv, x + w - 48, y + 8)


def draw_mercury(cv, x, y, w, h):
    """Mercury with craters, a probe on its orbit, on a dark sky."""
    cv.rect(x, y, w, h, (16, 20, 40))
    for sx, sy in ((14, 14), (w - 20, 10), (w // 2, 8), (10, h - 12),
                   (w - 12, h - 20), (w // 3, h - 8)):
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    cx, cy, r = x + w // 2 - 8, y + h // 2 + 2, 22
    cv.circle(cx, cy, r, (176, 152, 120))
    for dx, dy, cr in ((-10, -7, 5), (7, 5, 4), (2, -11, 3), (-3, 10, 4),
                       (11, -8, 3)):
        cv.circle(cx + dx, cy + dy, cr, (140, 118, 92))
    # orbit ring + probe
    cv.circle(cx, cy, r + 9, GOLD, fill=False)
    px, py = cx + r + 9, cy - 4
    cv.rect(px - 3, py - 3, 7, 7, WHITE)
    cv.rect(px - 16, py - 1, 10, 3, (120, 160, 220))
    cv.rect(px + 6, py - 1, 10, 3, (120, 160, 220))
    draw_text(cv, x + 8, y + 4, "8-YEAR TRIP", 1, WHITE)


def draw_strike(cv, x, y, w, h):
    """Jet silhouette over an airfield with a blast starburst."""
    cv.rect(x, y, w, h, (232, 226, 210))
    cv.rect(x, y + h - 22, w, 22, (120, 118, 110))
    cv.rect(x, y + h - 14, w, 3, WHITE)
    # jet: fuselage triangle + wings
    jx, jy = x + 26, y + 8
    cv.triangle((jx, jy), (jx + 64, jy + 10), (jx, jy + 20), (70, 74, 82))
    cv.triangle((jx + 30, jy + 10), (jx + 46, jy + 34),
                (jx + 40, jy + 10), (70, 74, 82))
    cv.triangle((jx + 30, jy + 10), (jx + 44, jy - 12),
                (jx + 38, jy + 10), (70, 74, 82))
    # blast starburst
    bx, by = x + w - 46, y + h - 28
    for ang in range(0, 360, 30):
        r1 = 26 if ang % 60 == 0 else 14
        ex = bx + int(r1 * math.cos(math.radians(ang)))
        ey = by + int(r1 * math.sin(math.radians(ang)))
        cv.line(bx, by, ex, ey, FLAME, thick=3)
    cv.circle(bx, by, 10, FLAME_Y)
    draw_text(cv, x + 8, y + 4, "5 PLANES HIT", 1, INK)


def draw_expulsion(cv, x, y, w, h):
    """Two flags and a closed gate: a diplomat sent home."""
    cv.rect(x, y, w, h, (232, 226, 210))
    # North Korea flag: blue-white-red-white-blue bands + red star disc
    fx, fy, fw, fh = x + 12, y + 16, 76, 46
    cv.rect(fx, fy, fw, 8, (20, 60, 160))
    cv.rect(fx, fy + 8, fw, 6, WHITE)
    cv.rect(fx, fy + 14, fw, 18, (200, 30, 40))
    cv.rect(fx, fy + 32, fw, 6, WHITE)
    cv.rect(fx, fy + 38, fw, 8, (20, 60, 160))
    cv.circle(fx + 22, fy + 23, 10, WHITE)
    cv.circle(fx + 22, fy + 23, 7, RED)
    # Swiss flag: red square, white cross
    sx, sy = x + w - 62, y + 16
    cv.rect(sx, sy, 46, 46, (220, 20, 30))
    cv.rect(sx + 19, sy + 8, 8, 30, WHITE)
    cv.rect(sx + 8, sy + 19, 30, 8, WHITE)
    # gate bars between them + arrow pointing home
    for i in range(4):
        cv.vline(x + 100 + i * 12, y + 14, y + h - 18, INK)
    cv.line(x + w - 70, y + h - 16, x + w - 96, y + h - 30, RED, thick=3)
    cv.line(x + w - 96, y + h - 30, x + w - 86, y + h - 30, RED, thick=3)
    cv.line(x + w - 96, y + h - 30, x + w - 96, y + h - 20, RED, thick=3)


# ---------------------------------------------------------------- PNG output
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        base = y * cv.w * 3
        raw += cv.px[base:base + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- stories
# All items happened or were first reported on 26 November 2026.
LEAD = {
    "kicker": "MIDDLE EAST - ENERGY",
    "headline": "HOUTHIS CLAIM STRIKE ON SAUDI REFINERY",
    "subhead": "BRENT CRUDE TOPS $94",
    "body": "Yemen's Houthis claim attacks on the Ras Tanura refinery and "
            "Riyadh's financial district, jolting oil markets and raising "
            "fears of supply disruption.",
    "art": draw_refinery,
}

PANELS = [
    {
        "kicker": "TRADE",
        "headline": "US UNVEILS NEW TARIFFS ON 14 PARTNERS",
        "body": "Washington proposes duties of up to 15% to fight factory "
                "overcapacity.",
        "art": draw_bars,
    },
    {
        "kicker": "MARKETS",
        "headline": "NASDAQ SLIDES NEARLY 4% IN AI ROUT",
        "body": "US stocks fall sharply as AI-stock fears deepen; tech leads "
                "the drop.",
        "art": draw_crash_chart,
    },
    {
        "kicker": "EGYPT",
        "headline": "TANKER FIRE KILLS AT LEAST 30 IN CAIRO",
        "body": "A fuel tanker crashes on a Cairo highway, igniting a huge "
                "blaze.",
        "art": draw_fire_scene,
    },
    {
        "kicker": "SPACE",
        "headline": "BEPICOLOMBO REACHES MERCURY ORBIT",
        "body": "Europe and Japan's probe enters orbit around Mercury after "
                "eight years.",
        "art": draw_mercury,
    },
    {
        "kicker": "WAR IN UKRAINE",
        "headline": "UKRAINE SAYS IT HIT RUSSIAN AIR BASE",
        "body": "Kyiv says its strike damaged five planes at a Russian air "
                "base.",
        "art": draw_strike,
    },
    {
        "kicker": "ASIA",
        "headline": "NORTH KOREA EXPELS SWISS DIPLOMAT",
        "body": "Pyongyang tells Switzerland to shut its new Pyongyang "
                "office.",
        "art": draw_expulsion,
    },
]

TICKER = [
    "ALSO TODAY: RUSSIA'S OWN FIGURES PUT ITS WAR DEAD NEAR 500,000",
    "ISRAELI JUDGES URGE DROPPING THE GRAVEST CHARGES AGAINST NETANYAHU",
    "GUKESH DRAWS GAME 2 OF THE WORLD CHESS FINAL \u2022 INDIA MARKS "
    "CONSTITUTION DAY",
]


def panel_border(cv, x, y, w, h):
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)


def draw_panel(cv, x, y, w, h, story):
    panel_border(cv, x, y, w, h)
    draw_text(cv, x + 12, y + 10, story["kicker"], 2, RED)
    lines = wrap_lines(story["headline"], w - 24, 3)
    for i, line in enumerate(lines[:3]):
        draw_text(cv, x + 12, y + 34 + i * 25, line, 3, INK)
    body_lines = wrap_lines(story["body"], w - 24, 2)
    for i, line in enumerate(body_lines[:3]):
        draw_text(cv, x + 12, y + 112 + i * 18, line, 2, INK)
    story["art"](cv, x + 12, y + h - 82, w - 24, 70)


def render():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(28, 20, 968, 3, GOLD)
    draw_text_centered(cv, W // 2, 28, "THE WORLD TODAY", 8, NAVY)
    cv.rect(28, 92, 968, 2, GOLD)
    draw_text_centered(cv, W // 2, 102, "THURSDAY, 26 NOVEMBER 2026", 4,
                       NAVY)
    draw_text_centered(cv, W // 2, 136, "THE DAY'S NEWS IN ONE PICTURE",
                       2, GREY)
    cv.rect(28, 156, 968, 4, RED)

    # lead story
    lx, ly, lw, lh = 28, 168, 968, 252
    panel_border(cv, lx, ly, lw, lh)
    draw_text(cv, lx + 16, ly + 14, LEAD["kicker"], 2, RED)
    lines = wrap_lines(LEAD["headline"], 560, 4)
    for i, line in enumerate(lines):
        draw_text(cv, lx + 16, ly + 42 + i * 32, line, 4, INK)
    draw_text(cv, lx + 16, ly + 114, LEAD["subhead"], 3, RED)
    draw_paragraph(cv, lx + 16, ly + 146, LEAD["body"], 560, 2, INK)
    LEAD["art"](cv, lx + 600, ly + 16, 352, 220)

    # two rows of three panels
    pw, ph = 312, 252
    for row in range(2):
        for col in range(3):
            story = PANELS[row * 3 + col]
            draw_panel(cv, 28 + col * (pw + 16), 436 + row * (ph + 16),
                       pw, ph, story)

    # ticker
    cv.rect(28, 960, 968, 2, GOLD)
    for i, line in enumerate(TICKER):
        draw_text_centered(cv, W // 2, 968 + i * 16, line, 2, INK)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(render())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Front-page poster of 17 November 2026 world news.

Draws a 1024x1024 PNG newspaper front page with the Python standard
library only: a tiny built-in 5x7 bitmap font, flat vector shapes, and a
zlib+struct PNG encoder. No network, no third-party packages.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output). Deterministic:
two runs produce identical bytes.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (22, 22, 22)
RED = (176, 32, 24)
NAVY = (20, 41, 77)
BLUE = (46, 94, 170)
SKY = (186, 214, 232)
SEA = (38, 90, 150)
GOLD = (192, 138, 45)
TEAL = (31, 110, 107)
GREY = (107, 101, 88)
WHITE = (255, 255, 255)
YELLOW = (240, 196, 60)
ORANGE = (232, 120, 40)
DARKGREY = (70, 70, 70)

# 5x7 bitmap font, one row per string, "1" = ink.
FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
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
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

BULLET = ("00000", "00000", "01100", "01100", "01100", "00000", "00000")

buf = bytearray(bytes(PAPER) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def border(x, y, w, h, c=INK, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, y, 2 * dx + 1, 1, c)


def poly(points, c):
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    poly([(x0, y0), (x1, y1), (x2, y2)], c)


def starburst(cx, cy, r, c, spikes=8):
    for i in range(spikes):
        a = 2 * math.pi * i / spikes
        tip = (cx + int(r * math.cos(a)), cy + int(r * math.sin(a)))
        b1 = (cx + int(r * 0.35 * math.cos(a + 0.35)),
              cy + int(r * 0.35 * math.sin(a + 0.35)))
        b2 = (cx + int(r * 0.35 * math.cos(a - 0.35)),
              cy + int(r * 0.35 * math.sin(a - 0.35)))
        tri(tip[0], tip[1], b1[0], b1[1], b2[0], b2[1], c)


def _clean(s):
    return (s.upper()
             .replace("\u2014", "-").replace("\u2013", "-")
             .replace("\u2019", "'").replace("\u201c", '"')
             .replace("\u201d", '"').replace("\u2026", "..."))


def text_w(s, scale):
    s = _clean(s)
    return len(s) * 6 * scale - scale if s else 0


def text(s, x, y, scale, c, align="left"):
    s = _clean(s)
    if align == "center":
        x -= text_w(s, scale) // 2
    elif align == "right":
        x -= text_w(s, scale)
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = glyph[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale


def wrap(s, scale, maxw):
    words = _clean(s).split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(s, x, y, scale, maxw, c=INK, leading=4):
    lh = 7 * scale + leading
    for ln in wrap(s, scale, maxw):
        text(ln, x, y, scale, c)
        y += lh
    return y


def headline_block(s, x, y, scale, maxw):
    lh = 7 * scale + 4
    for part in s.split("\n"):
        for ln in wrap(part, scale, maxw):
            text(ln, x, y, scale, INK)
            y += lh
    return y


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def png_bytes():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))


# ---------------------------------------------------------------- layout

def panel(x, y, w, h, kicker, headline, deck, hscale=3):
    border(x, y, w, h)
    text(kicker, x + 14, y + 12, 2, RED)
    hy = headline_block(headline, x + 14, y + 34, hscale, w - 28)
    return para(deck, x + 14, hy + 6, 2, w - 28)


def draw_bridge(x0, y0, x1, y1):
    """Kerch Bridge: two towers, a collapsed middle span, explosion."""
    rect(x0, y0, x1 - x0, 120, SKY)          # sky
    rect(x0, y0 + 120, x1 - x0, y1 - y0 - 120, SEA)  # sea
    circle(x1 - 38, y0 + 24, 16, YELLOW)     # sun
    # towers and deck
    rect(x0 + 48, y0 + 30, 10, 76, DARKGREY)
    rect(x0 + 44, y0 + 24, 18, 8, DARKGREY)
    rect(x0 + 308, y0 + 30, 10, 76, DARKGREY)
    rect(x0 + 304, y0 + 24, 18, 8, DARKGREY)
    rect(x0 + 8, y0 + 96, 148, 10, DARKGREY)    # left deck
    rect(x0 + 212, y0 + 96, 168, 10, DARKGREY)  # right deck
    # cables
    line(x0 + 53, y0 + 32, x0 + 12, y0 + 96, GREY)
    line(x0 + 53, y0 + 32, x0 + 152, y0 + 96, GREY)
    line(x0 + 313, y0 + 32, x0 + 216, y0 + 96, GREY)
    line(x0 + 313, y0 + 32, x0 + 376, y0 + 96, GREY)
    # collapsed span sinking in the gap
    poly([(x0 + 162, y0 + 116), (x0 + 206, y0 + 116),
          (x0 + 196, y0 + 146), (x0 + 154, y0 + 144)], DARKGREY)
    # explosion right on the deck gap
    starburst(x0 + 184, y0 + 96, 30, YELLOW)
    circle(x0 + 184, y0 + 96, 18, ORANGE)
    circle(x0 + 184, y0 + 96, 9, RED)
    # smoke rising above the blast
    circle(x0 + 156, y0 + 52, 12, (196, 192, 182))
    circle(x0 + 184, y0 + 40, 16, (196, 192, 182))
    circle(x0 + 212, y0 + 54, 11, (196, 192, 182))
    # small boat on the sea
    poly([(x0 + 20, y0 + 164), (x0 + 80, y0 + 164),
          (x0 + 72, y0 + 178), (x0 + 28, y0 + 178)], WHITE)
    line(x0 + 50, y0 + 164, x0 + 50, y0 + 142, INK)
    tri(x0 + 50, y0 + 142, x0 + 50, y0 + 158, x0 + 66, y0 + 158, RED)
    # waves
    line(x0 + 220, y0 + 192, x0 + 260, y0 + 192, WHITE)
    line(x0 + 300, y0 + 196, x0 + 350, y0 + 196, WHITE)
    line(x0 + 120, y0 + 200, x0 + 170, y0 + 200, WHITE)


def draw_tanker(x, y):
    """Tanker, containers and a mine with a blast."""
    rect(x + 14, y + 6, 30, 20, RED)
    rect(x + 48, y + 6, 30, 20, BLUE)
    rect(x + 82, y + 6, 30, 20, GOLD)
    rect(x, y + 26, 200, 20, DARKGREY)       # hull
    tri(x + 200, y + 26, x + 200, y + 46, x + 224, y + 46, DARKGREY)
    rect(x + 174, y + 10, 16, 16, NAVY)      # funnel
    # mine + blast
    starburst(x + 300, y - 6, 18, YELLOW)
    circle(x + 300, y + 14, 10, DARKGREY)
    for a in range(8):
        ang = 2 * math.pi * a / 8
        line(x + 300 + int(9 * math.cos(ang)), y + 14 + int(9 * math.sin(ang)),
             x + 300 + int(16 * math.cos(ang)), y + 14 + int(16 * math.sin(ang)),
             DARKGREY)
    line(x + 260, y + 50, x + 300, y + 50, WHITE)
    line(x + 330, y + 54, x + 380, y + 54, WHITE)


def draw_flags(x, y):
    """China, USA, Russia flags on poles."""
    poles = [x, x + 150, x + 300]
    for px in poles:
        line(px, y, px, y + 48, INK)
    # China
    rect(poles[0], y, 46, 28, RED)
    circle(poles[0] + 9, y + 8, 3, YELLOW)
    circle(poles[0] + 19, y + 5, 2, YELLOW)
    circle(poles[0] + 22, y + 11, 2, YELLOW)
    circle(poles[0] + 19, y + 17, 2, YELLOW)
    # USA: stripes + canton
    for i in range(7):
        rect(poles[1], y + i * 4, 46, 4, RED if i % 2 == 0 else WHITE)
    rect(poles[1], y, 18, 16, NAVY)
    circle(poles[1] + 5, y + 5, 1, WHITE)
    circle(poles[1] + 12, y + 5, 1, WHITE)
    circle(poles[1] + 5, y + 11, 1, WHITE)
    circle(poles[1] + 12, y + 11, 1, WHITE)
    # Russia
    rect(poles[2], y, 46, 10, WHITE)
    rect(poles[2], y + 10, 46, 9, BLUE)
    rect(poles[2], y + 19, 46, 9, RED)


def draw_virus(cx, cy, r, c):
    for a in range(8):
        ang = 2 * math.pi * a / 8
        line(cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang)),
             cx + int((r + 8) * math.cos(ang)),
             cy + int((r + 8) * math.sin(ang)), c)
    circle(cx, cy, r, c)
    circle(cx - r // 3, cy - r // 4, r // 4, WHITE)
    circle(cx + r // 3, cy + r // 4, r // 5, WHITE)


def draw_pentagon(cx, cy, r):
    pts = []
    for i in range(5):
        ang = -math.pi / 2 + 2 * math.pi * i / 5
        pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
    poly(pts, NAVY)
    line(cx - 34, cy - 34, cx + 34, cy + 34, RED)
    line(cx + 34, cy - 34, cx - 34, cy + 34, RED)
    text("$4.8TN", cx, cy + 54, 2, RED, align="center")


def compose():
    border(8, 8, 1008, 1008, INK, 4)
    # ---- masthead
    text("THE WORLD IN ONE DAY", 512, 22, 7, NAVY, align="center")
    rect(20, 82, 984, 3, INK)
    rect(20, 90, 984, 52, RED)
    text("TUESDAY, 17 NOVEMBER 2026", 512, 102, 5, WHITE, align="center")
    rect(20, 150, 984, 3, INK)

    # ---- lead story: Kerch Bridge
    border(20, 162, 984, 234)
    text("LEAD STORY - UKRAINE", 36, 178, 2, RED)
    headline_block("KERCH BRIDGE", 36, 200, 5, 520)
    headline_block("HIT AGAIN", 36, 239, 5, 520)
    para("Ukraine strikes the Crimea bridge a second time in under "
         "24 hours; a road section collapses. Russia hits Kyiv's river "
         "bridges, cutting heat, water and power.",
         36, 282, 2, 520)
    text("2ND STRIKE IN UNDER 24 HOURS", 36, 356, 2, RED)
    draw_bridge(600, 176, 988, 384)

    # ---- row 2: Hormuz + summit
    panel(20, 408, 486, 240, "MIDDLE EAST", "MINES IN THE GULF",
          "Tankers hit by mines near the Strait of Hormuz. Iran fires "
          "drones at a US radar in Bahrain - intercepted, no casualties. "
          "US intel: Tehran is weighing a dirty-bomb or chemical attack "
          "on Trump officials in Washington.")
    draw_tanker(36, 592)
    panel(518, 408, 486, 240, "ASIA - SUMMIT", "XI, TRUMP AND\nPUTIN TO MEET",
          "China confirms the first trilateral summit: Thursday "
          "19 November in Shenzhen, on the APEC sidelines. Trump travels "
          "to Asia for nuclear talks.")
    draw_flags(540, 598)

    # ---- row 3: measles, Pentagon, in brief
    panel(20, 660, 312, 324, "HEALTH - USA", "MEASLES STATUS LOST",
          "The US loses measles elimination status after about 30 years. "
          "Cases are the highest since 1991; 13 babies were born with "
          "congenital measles.")
    draw_virus(90, 920, 20, RED)
    draw_virus(190, 940, 15, RED)
    draw_virus(270, 915, 12, RED)

    panel(356, 660, 312, 324, "USA - DEFENCE", "PENTAGON FAILS ITS AUDIT",
          "Ninth year in a row: $4.8 trillion in assets cannot be "
          "verified.")
    draw_pentagon(512, 884, 56)

    border(692, 660, 312, 324)
    text("IN BRIEF", 706, 672, 2, RED)
    headline_block("AROUND THE WORLD", 706, 694, 3, 284)
    y = 752
    for item in (
        "JAPAN scrambles jets after suspected Russian aircraft violate "
        "its airspace.",
        "FIVE EUROPEAN states unveil a joint Rwanda migrant-return hub.",
        "THIRD US CARRIER - USS Theodore Roosevelt - reaches the "
        "Middle East.",
    ):
        for ln in wrap(item, 2, 260):
            # bullet on the first line only
            if ln == wrap(item, 2, 260)[0]:
                for r in range(7):
                    for col in range(5):
                        if BULLET[r][col] == "1":
                            rect(706 + col * 2, y + r * 2, 2, 2, RED)
            text(ln, 722, y, 2, INK)
            y += 18
        y += 8

    # ---- footer
    text("ALL EVENTS OF TUESDAY, 17 NOVEMBER 2026", 512, 992, 2, GREY,
         align="center")


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    compose()
    data = png_bytes()
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""news-image-20261126: one-day world news image, drawn with stdlib only.

Writes a single 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png.
Fully deterministic: no time, no randomness, no network, no external files.
"""

import os
import struct
import zlib
from binascii import crc32

W = 1024
H = 1024

# ---- palette: light paper, dark ink, restrained navy/red/teal/gold ----
PAPER = (250, 247, 240)
PAPER2 = (243, 238, 228)
INK = (24, 28, 38)
NAVY = (24, 44, 84)
NAVY2 = (36, 62, 110)
RED = (178, 34, 34)
RED2 = (205, 70, 55)
TEAL = (14, 122, 110)
GOLD = (184, 138, 28)
GOLD2 = (214, 168, 60)
SLATE = (88, 102, 122)
SLATE_D = (58, 70, 92)
SKY = (196, 214, 228)
SKY2 = (168, 192, 214)
WHITE = (255, 255, 255)
GREY = (120, 118, 112)

# ---- 5x7 bitmap font, designed here. Each glyph is 7 rows of 5 bits. ----
# Bit 4 is the leftmost pixel. Text is rendered upper-case.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
}

BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px per char cell)."""
    return len(text) * 6 * scale


def wrap_text(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    """A plain RGB pixel buffer with simple drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if thick <= 1:
                self.set(x, y, color)
            else:
                self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, 2 * half + 1, 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            half = int(rx * (t ** 0.5)) if t > 0 else 0
            self.fill_rect(cx - half, cy + dy, 2 * half + 1, 1, color)

    def fill_polygon(self, points, color):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa = int(round(xs[j]))
                xb = int(round(xs[j + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, color)

    def star(self, cx, cy, r_out, r_in, color, points=5, rot=-90.0):
        import math
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            ang = math.radians(rot + i * 180.0 / points)
            pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
        self.fill_polygon(pts, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw upper-case bitmap text; (x, y) is the top-left corner."""
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


# ---- small flat icons, drawn from primitives (each fits in a ~30x30 box) ----

def icon_chart(cv, x, y, color):
    # rising bar chart with an arrow
    cv.fill_rect(x + 2, y + 20, 5, 9, color)
    cv.fill_rect(x + 10, y + 14, 5, 15, color)
    cv.fill_rect(x + 18, y + 8, 5, 21, color)
    cv.line(x + 1, y + 26, x + 27, y + 2, color, 2)
    cv.fill_polygon([(x + 27, y + 2), (x + 19, y + 2), (x + 27, y + 10)], color)


def icon_flame(cv, x, y, color):
    # a flame: outer teardrop, inner lighter tongue
    cv.fill_polygon([(x + 15, y + 1), (x + 24, y + 12), (x + 26, y + 19),
                     (x + 21, y + 28), (x + 9, y + 28), (x + 4, y + 19),
                     (x + 6, y + 12)], color)
    cv.fill_polygon([(x + 15, y + 12), (x + 20, y + 18), (x + 19, y + 25),
                     (x + 11, y + 25), (x + 10, y + 18)], GOLD2)


def icon_shield_check(cv, x, y, color):
    cv.fill_polygon([(x + 2, y + 2), (x + 28, y + 2), (x + 28, y + 14),
                     (x + 15, y + 29), (x + 2, y + 14)], color)
    cv.line(x + 8, y + 14, x + 13, y + 20, INK, 3)
    cv.line(x + 13, y + 20, x + 23, y + 8, INK, 3)


def icon_rocket(cv, x, y, color):
    cv.fill_polygon([(x + 15, y + 1), (x + 22, y + 12), (x + 22, y + 20),
                     (x + 8, y + 20), (x + 8, y + 12)], color)
    cv.fill_circle(x + 15, y + 12, 3, INK)
    cv.fill_polygon([(x + 8, y + 16), (x + 2, y + 24), (x + 8, y + 22)], color)
    cv.fill_polygon([(x + 22, y + 16), (x + 28, y + 24), (x + 22, y + 22)], color)
    cv.fill_polygon([(x + 12, y + 21), (x + 18, y + 21), (x + 15, y + 29)], GOLD2)


def icon_court(cv, x, y, color):
    # courthouse: pediment, three columns, steps
    cv.fill_polygon([(x + 1, y + 8), (x + 15, y + 1), (x + 29, y + 8)], color)
    cv.fill_rect(x + 4, y + 11, 3, 12, color)
    cv.fill_rect(x + 13, y + 11, 3, 12, color)
    cv.fill_rect(x + 22, y + 11, 3, 12, color)
    cv.fill_rect(x + 1, y + 24, 28, 2, color)
    cv.fill_rect(x, y + 27, 30, 2, color)


def icon_globe(cv, x, y, color):
    cv.fill_circle(x + 15, y + 15, 14, color)
    cv.fill_ellipse(x + 15, y + 15, 6, 14, TEAL)
    cv.line(x + 1, y + 15, x + 29, y + 15, TEAL, 1)
    cv.fill_ellipse(x + 15, y + 8, 13, 3, TEAL)
    cv.fill_ellipse(x + 15, y + 22, 13, 3, TEAL)


def icon_drop(cv, x, y, color):
    cv.fill_polygon([(x + 15, y + 1), (x + 25, y + 16), (x + 23, y + 23),
                     (x + 15, y + 29), (x + 7, y + 23), (x + 5, y + 16)], color)
    cv.fill_circle(x + 15, y + 20, 8, color)


def icon_flag(cv, x, y, color):
    cv.fill_rect(x + 4, y + 2, 3, 27, INK)
    cv.fill_polygon([(x + 7, y + 3), (x + 27, y + 7), (x + 7, y + 13)], color)
    cv.fill_circle(x + 5, y + 2, 2, GOLD)


def icon_plane(cv, x, y, color):
    # side view of a jet, nose to the right
    cv.fill_polygon([(x + 2, y + 14), (x + 12, y + 11), (x + 24, y + 11),
                     (x + 29, y + 14), (x + 24, y + 17), (x + 12, y + 17)], color)
    cv.fill_polygon([(x + 12, y + 11), (x + 17, y + 3), (x + 20, y + 11)], color)
    cv.fill_polygon([(x + 16, y + 17), (x + 19, y + 25), (x + 22, y + 17)], color)
    cv.fill_polygon([(x + 2, y + 14), (x + 6, y + 8), (x + 9, y + 13)], color)


def cloud(cv, x, y, w, color):
    """A puffy storm cloud: a filled mass with a bumpy top and rounded base."""
    cv.fill_ellipse(x + w // 2, y + 12, w // 2, 13, color)
    cv.fill_circle(x + w // 4, y + 6, 13, color)
    cv.fill_circle(x + w // 2, y, 16, color)
    cv.fill_circle(x + 3 * w // 4, y + 6, 13, color)
    cv.fill_circle(x + 10, y + 14, 9, color)
    cv.fill_circle(x + w - 10, y + 14, 9, color)


# ---- verified stories for Thursday 26 November 2026 ----
# Bodies are shortened only where the card needs it; every fact is kept.

LEAD_HEADLINE = "STORM STOPS THE PARADE"
LEAD_BODY = (
    "A POWERFUL THANKSGIVING STORM BATTERS THE EAST COAST WITH FLOODING "
    "AND HIGH WINDS, AND MACY'S PARADE IS POSTPONED FOR THE FIRST TIME "
    "IN 100 YEARS."
)

# (tag, tag colour, headline, body, icon function)
CARDS = [
    ("TRADE", NAVY, "US UNVEILS NEW TARIFFS",
     "NEW LEVIES ON CHINA, THE EU, BRAZIL AND A DOZEN PARTNERS OVER SUBSIDIES.",
     icon_chart),
    ("EGYPT", RED, "30 KILLED IN CAIRO FIRE",
     "A FUEL TANKER BURSTS INTO FLAMES ON A CAIRO HIGHWAY; AT LEAST 30 KILLED.",
     icon_flame),
    ("COLOMBIA", TEAL, "HOSTAGES FREED IN CARTAGENA",
     "TROOPS STORM A SUPERMARKET, FREE EVERY HOSTAGE OF A 17-HOUR SIEGE. "
     "ONE CAPTOR DIES.",
     icon_shield_check),
    ("SPACE", NAVY, "PAKISTAN'S FIRST ASTRONAUT",
     "CHINA NAMES A PAKISTANI PAYLOAD SPECIALIST FOR TIANGONG, A FIRST "
     "FOR A FOREIGN ASTRONAUT.",
     icon_rocket),
    ("JUSTICE", RED, "HUAWEI FOUND GUILTY",
     "A US JURY CONVICTS THE TECH GIANT OF STEALING TRADE SECRETS.",
     icon_court),
    ("CLIMATE", TEAL, "NO DEAL AT COP31",
     "CLIMATE TALKS END WITHOUT AN AGREEMENT; NEGOTIATIONS MAY RESUME NEXT YEAR.",
     icon_globe),
    ("INDONESIA", NAVY, "MINE FLOOD IN WEST JAVA",
     "FLOODWATER SWAMPS AN UNDERGROUND PIT; 9 MINERS DEAD, 17 MISSING.",
     icon_drop),
    ("PACIFIC", RED, "AUSTRALIA-SOLOMONS PACT",
     "CANBERRA AND HONIARA SIGN A LANDMARK SECURITY PARTNERSHIP.",
     icon_flag),
    ("ASIA", TEAL, "BOMBER NEAR MANILA",
     "A CHINESE H-6 BOMBER IS SPOTTED 170 NAUTICAL MILES FROM MANILA, MANILA SAYS.",
     icon_plane),
]

TICKER = [
    "US ARMY DETONATES FIVE TONS OF UNSTABLE EXPLOSIVES IN IOWA.",
    "WRONGLY DEPORTED MIGRANT LEAVES THE US FOR SPAIN.",
    "NORTH KOREA MOVES TO SHUT SWITZERLAND'S OFFICE IN PYONGYANG.",
    "TWO CHARGED OVER A BREAK-IN AT SANDRINGHAM, PRINCE WILLIAM'S HOME.",
    "NVIDIA BRINGS BACK JENSEN HUANG AS CHIEF EXECUTIVE.",
]


def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 104, NAVY)
    cv.fill_rect(0, 100, W, 4, GOLD)
    cv.text_centered(W // 2, 16, "THE WORLD TODAY", 6, WHITE)
    cv.draw_text(24, 68, "WORLD EDITION", 2, GOLD2)
    cv.draw_text(W - 24 - text_width("NO. 330", 2), 68, "NO. 330", 2, GOLD2)
    cv.text_centered(W // 2, 68, "THURSDAY 26 NOVEMBER 2026", 2, GOLD2)


def draw_lead(cv):
    # --- scene: storm sky, rain, skyline, parade balloon (y 112..292) ---
    x0, y0, x1, y1 = 24, 112, 1000, 292
    cv.fill_rect(x0, y0, x1 - x0, y1 - y0, SKY)
    cv.fill_rect(x0, 240, x1 - x0, y1 - 240, SKY2)
    cloud(cv, 60, 122, 220, SLATE_D)
    cloud(cv, 380, 114, 260, SLATE_D)
    cloud(cv, 700, 130, 240, SLATE)
    cloud(cv, 250, 150, 180, SLATE)
    # diagonal rain under the clouds
    for rx in range(48, 960, 26):
        cv.line(rx, 176, rx - 12, 208, SLATE, 2)
        cv.line(rx + 10, 196, rx - 2, 228, SLATE, 2)
    # skyline silhouettes with lit windows
    heights = [60, 92, 46, 112, 70, 100, 56, 86, 64, 96, 50, 80]
    bx = x0
    bw = (x1 - x0) // len(heights)
    for i, bh in enumerate(heights):
        top = y1 - bh
        cv.fill_rect(bx, top, bw - 6, bh, NAVY)
        for wy in range(top + 10, y1 - 8, 16):
            for wx in range(bx + 8, bx + bw - 14, 16):
                if (wx + wy) % 48 == 0:
                    cv.fill_rect(wx, wy, 5, 7, GOLD2)
        bx += bw
    # parade balloon: big red envelope, highlight, ropes, basket
    cv.fill_ellipse(760, 182, 62, 44, RED)
    cv.fill_ellipse(742, 176, 12, 30, RED2)
    cv.fill_ellipse(760, 182, 46, 30, RED)
    cv.fill_ellipse(742, 176, 9, 22, RED2)
    cv.line(728, 220, 748, 242, INK, 2)
    cv.line(792, 220, 772, 242, INK, 2)
    cv.fill_rect(746, 242, 28, 16, GOLD)
    cv.fill_rect(746, 242, 28, 3, GOLD2)
    # --- headline panel below the scene (y 292..392) ---
    cv.fill_rect(x0, 300, 6, 84, RED)
    cv.fill_rect(40, 302, 118, 24, RED)
    cv.draw_text(48, 308, "THE LEAD", 2, WHITE)
    cv.draw_text(40, 332, LEAD_HEADLINE, 3, INK)
    body_lines = wrap_text(LEAD_BODY, 80)
    by = 360
    for line in body_lines:
        cv.draw_text(40, by, line, 2, INK)
        by += 18


def draw_grid(cv):
    gx, gy = 24, 404
    cw, ch = 317, 152
    gapx, gapy = 12, 10
    for idx, (tag, color, headline, body, icon) in enumerate(CARDS):
        col = idx % 3
        row = idx // 3
        x = gx + col * (cw + gapx)
        y = gy + row * (ch + gapy)
        cv.fill_rect(x, y, cw, ch, WHITE)
        cv.rect(x, y, cw, ch, GREY, 1)
        # coloured tag bar with the icon at its right end
        cv.fill_rect(x, y, cw, 30, color)
        cv.draw_text(x + 10, y + 8, tag, 2, WHITE)
        icon(cv, x + cw - 36, y + 1, WHITE)
        # headline, up to 2 lines
        head_lines = wrap_text(headline, 24)
        hy = y + 38
        for line in head_lines:
            cv.draw_text(x + 10, hy, line, 2, INK)
            hy += 17
        # body, up to 4 lines
        body_lines = wrap_text(body, 24)
        by = hy + 4
        for line in body_lines[:4]:
            cv.draw_text(x + 10, by, line, 2, (52, 56, 66))
            by += 17


def draw_ticker(cv):
    cv.fill_rect(0, 892, W, 132, NAVY)
    cv.fill_rect(0, 892, W, 3, GOLD)
    cv.draw_text(24, 904, "ALSO TODAY", 2, GOLD2)
    ty = 930
    for line in TICKER:
        cv.fill_rect(24, ty + 4, 8, 8, GOLD)
        cv.draw_text(44, ty, line, 2, WHITE)
        ty += 18


def build_image():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    draw_grid(cv)
    draw_ticker(cv)
    return cv


# ---- PNG writer: pure stdlib, fully deterministic ----

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    row_bytes = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter type 0 (None) for every scanline
        start = y * row_bytes
        raw += cv.px[start:start + row_bytes]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_image()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

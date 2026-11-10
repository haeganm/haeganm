#!/usr/bin/env python3
"""Draws this profile's pixel art, and its NetOps diagram, as SVG. Standard library only.

    python assets/build.py

The pixel art is a grid of logical pixels. Same-coloured pixels are merged into
rectangles, and the moving parts are separate layers driven by stepped CSS
keyframes, so nothing here is a bitmap. Seeded, so the output is reproducible.
"""
import base64
import random
import re
import sys
from pathlib import Path
from urllib.parse import quote

OUT = Path(__file__).parent
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
# the page's palette: a night-time navy lit by neon pink and cyan
NIGHT, PANEL, EDGE, TEXT, MUTED = "#1b1236", "#26184d", "#4a3486", "#f3ebff", "#b8a6e6"
PINK, CYAN, GOLD, VIOLET = "#ff5ad9", "#5ff3ff", "#ffd36b", "#a98bff"


class Layer:
    def __init__(self):
        self.px = {}

    def put(self, x, y, c):
        self.px[(x, y)] = c

    def rect(self, x, y, w, h, c):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.px[(i, j)] = c

    def sprite(self, x, y, rows, pal):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal:
                    self.px[(x + i, y + j)] = pal[ch]

    def svg(self, attrs=""):
        """Greedy-merge each colour into rectangles, one <path> per colour."""
        by_colour = {}
        for p, c in self.px.items():
            by_colour.setdefault(c, set()).add(p)
        out = []
        for c in sorted(by_colour):
            pts, d = by_colour[c], []
            for x, y in sorted(pts, key=lambda p: (p[1], p[0])):
                if (x, y) not in pts:
                    continue
                w = 1
                while (x + w, y) in pts:
                    w += 1
                h = 1
                while all((x + i, y + h) in pts for i in range(w)):
                    h += 1
                for j in range(h):
                    for i in range(w):
                        pts.discard((x + i, y + j))
                d.append(f"M{x} {y}h{w}v{h}h-{w}z")
            out.append(f'<path fill="{c}" d="{"".join(d)}"/>')
        return f"<g {attrs}>{''.join(out)}</g>" if attrs else "".join(out)


def ramp(t, colours, x, y, sharp=2.4):
    """Pick a colour along a ramp, with an ordered-dither edge between bands."""
    t = min(max(t, 0.0), 0.9999) * (len(colours) - 1)
    i = int(t)
    f = min(max((t - i - 0.5) * sharp + 0.5, 0.0), 1.0)
    return colours[i + 1] if f > (BAYER[y % 4][x % 4] + 0.5) / 16 else colours[i]


def mix(a, b, t):
    """Blend two #rrggbb colours, t=0 giving a and t=1 giving b."""
    rgb = [round(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (1, 3, 5)]
    return "#" + "".join(f"{v:02x}" for v in rgb)


def curve(p0, p1, p2, steps=48):
    """The pixels along a quadratic Bezier."""
    return {(round((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]),
             round((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
            for t in (i / steps for i in range(steps + 1))}


def palm(crown, fronds, trunk):
    """A palm's pixels: each frond is (tip, bend) as offsets from the crown, the trunk a curve."""
    cx, cy = crown
    pts = set(curve(*trunk))
    for (tx, ty), (bx, by) in fronds:
        pts |= curve(crown, (cx + bx, cy + by), (cx + tx, cy + ty))
    return pts


def neon(layer, tube, core, ring, glow):
    """Light pixels as a neon tube: a pale core, a coloured ring, then a dithered glow."""
    near = {}
    for x, y in tube:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                p = (x + dx, y + dy)
                near[p] = min(near.get(p, 9), dx * dx + dy * dy)
    for (x, y), d in near.items():
        if 1 <= d <= 2:
            layer.put(x, y, ring)
        elif 4 <= d <= 5 and (x + y) % 2 == 0:
            layer.put(x, y, glow)
    for p in tube:
        layer.put(*p, core)


def doc(w, h, scale, label, css, body):
    css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w * scale}" height="{h * scale}" shape-rendering="crispEdges" role="img" '
        f'aria-label="{label}"><title>{label}</title><style>{css}</style>{body}</svg>\n'
    )


FONT = {  # 5x7, only the letters the name needs
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "c": (".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
}


def text(layer, x, y, s, c, scale=2):
    for n, ch in enumerate(s):
        for j, row in enumerate(FONT[ch]):
            for i, bit in enumerate(row):
                if bit == "#":
                    layer.rect(x + (n * 6 + i) * scale, y + j * scale, scale, scale, c)


CAT_NAP = (  # curled up, head to the left
    "..K...K...........",
    ".KGK.KGK..........",
    ".KGGKGGKKKKKKKK...",
    "KGGGGGGGDGGDGGGKK.",
    "KGEEGEEGGGGGGGGGGK",
    "KWGGPGGWDGGDGGGGGK",
    "KWWWWWWGGGGGGGKKGK",
    ".KKKKKKKKKKKKKKKK.",
)
GREY = {"K": "#1d1436", "G": "#a39bc8", "D": "#7a70a6", "W": "#f1eaff", "E": "#1d1436", "P": "#ff8fc8"}

CRAB_SPECS = (  # the Claude crab, in glasses; its right arm is drawn apart so it can wave
    ".OOOOOOOOOOOOOO.",
    ".OOOOOOOOOOOOOO.",
    ".OGGGGGOOGGGGGO.",
    "OOGLKLGGGGLKLGO.",
    "OOGLKLGOOGLKLGO.",
    ".OGGGGGOOGGGGGO.",
    ".OOOOOOOOOOOOOO.",
    ".OOOOOOOOOOOOOO.",
    ".OOOOOOOOOOOOOO.",
    ".OO.OO....OO.OO.",
    ".OO.OO....OO.OO.",
    ".OO.OO....OO.OO.",
)
CLAUDE = "#d97757"

Z_SMALL = ("ZZZ", ".Z.", "ZZZ")
Z_BIG = ("ZZZZ", "..Z.", ".Z..", "ZZZZ")
ZZZ = (
    ".z1,.z2{opacity:0}.z1{animation:z1 3.2s steps(1) infinite}.z2{animation:z2 3.2s steps(1) infinite}"
    "@keyframes z1{25%{opacity:1}75%{opacity:0}}@keyframes z2{50%{opacity:1}75%{opacity:0}}"
)

FRAMES2 = (  # two-frame flick: mostly a, a quick b
    ".a{animation:a 4s steps(1) infinite}.b{opacity:0;animation:b 4s steps(1) infinite}"
    "@keyframes a{0%{opacity:1}70%{opacity:0}80%{opacity:1}90%{opacity:0}}"
    "@keyframes b{0%{opacity:0}70%{opacity:1}80%{opacity:0}90%{opacity:1}}"
)


def banner():
    W, H = 280, 84
    rnd = random.Random(7)
    bg, fg = Layer(), Layer()
    twinkle, shimmer = [Layer(), Layer(), Layer()], [Layer(), Layer()]

    # wall, cooled by the desk lamp on the left
    wall = ("#21103d", "#291448", "#321a57", "#3c2167", "#472a78", "#55358a")
    for y in range(H):
        for x in range(W):
            d = ((x - 29) ** 2 + ((y - 46) * 1.2) ** 2) ** 0.5
            bg.put(x, y, ramp(max(0.0, 1 - d / 64) ** 1.4, wall, x, y))

    # night over the bay: stars, two thin clouds, a full moon
    gx0, gy0, gx1, gy1, sea = 172, 11, 265, 54, 46  # the glass, and the waterline
    sky = ("#0a0a26", "#100e36", "#181448", "#22185a", "#33206c", "#4a2479", "#6a2a86")
    for y in range(gy0, sea + 1):
        for x in range(gx0, gx1 + 1):
            bg.put(x, y, ramp((y - gy0) / (sea - gy0), sky, x, y))
    for x, y in ((176, 13), (199, 12), (206, 17), (226, 13), (240, 19), (252, 12), (261, 17), (213, 22), (247, 21)):
        bg.put(x, y, "#cdd6ff")
    for x0, x1, y in ((195, 211, 21), (199, 206, 20), (227, 244, 16), (231, 238, 15)):
        bg.rect(x0, y, x1 - x0 + 1, 1, "#1d1a52")
    for y in range(12, 25):
        for x in range(180, 193):
            d = ((x - 186) ** 2 + (y - 18) ** 2) ** 0.5
            if d <= 4.6:
                bg.put(x, y, "#b9c8f2" if (x, y) in ((184, 16), (188, 19), (185, 20), (187, 15)) else "#e6eeff")
            elif d <= 6.2 and (x + y) % 2 == 0:
                bg.put(x, y, "#2a2770")

    # the skyline in three depths; lit windows and neon crowns throw colour on the water
    lights = {}

    def skyline(colour, lo, hi, wmin, wmax, lit=(), p=0.0, gap=0.0, spire=0.0, crown=0.0, edge=None, reflect=False):
        x = gx0 - rnd.randint(0, 3)
        while x <= gx1:
            w = rnd.randint(wmin, wmax)
            top = rnd.randint(lo, hi) if rnd.random() >= gap else sea - 2
            cols = range(max(x, gx0), min(x + w, gx1 + 1))
            spike = x + w // 2 if rnd.random() < spire else None
            for i in cols:
                for j in range(top - 4 if i == spike else top, sea + 1):
                    bg.put(i, j, edge if edge and i == x and i != spike else colour)
                    for t in twinkle:  # a nearer building hides what is behind it
                        t.px.pop((i, j), None)
            if lit and rnd.random() < crown:
                c = rnd.choice((PINK, CYAN))
                for i in cols:
                    bg.put(i, top, c)
                    lights[i] = c
            for j in range(top + 2, sea - 1, 3):
                for i in range(x + 1, x + w - 1, 2):
                    if lit and gx0 <= i <= gx1 and rnd.random() < p:
                        c = rnd.choice(lit)
                        (rnd.choice(twinkle) if rnd.random() < 0.12 else bg).rect(i, j, 1, 2, c)
                        if reflect:
                            lights[i] = c
            x += w

    skyline("#3a2875", 28, 38, 4, 8, ("#6f5fc0",), 0.12, gap=0.25)
    skyline("#221a55", 17, 36, 5, 10, (CYAN, PINK, "#c9b8ff", "#eef0ff"), 0.42, spire=0.35, crown=0.4, edge="#30276e")
    skyline("#120d33", 36, 43, 7, 13, (GOLD, CYAN, PINK), 0.35, edge="#1d1748", reflect=True)
    for x in range(gx0 + 3, gx1, 7):  # lamps along the waterfront
        bg.put(x, sea, "#ffcf8a")
        lights[x] = "#ffcf8a"

    # the bay, with the city and the moon broken up on it
    water = ("#3a1d70", "#22145a", "#160f44", "#0c0a2a")
    for y in range(sea + 1, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            bg.put(x, y, ramp((y - sea - 1) / (gy1 - sea - 1), water, x, y))
    lights.update({x: "#c9d6ff" for x in range(185, 188)})  # the moon's path
    for x, c in lights.items():
        for k in range(0, gy1 - sea, 2):  # every other row, so the streaks break up
            if rnd.random() < 0.85 - 0.12 * k:
                tone = mix(c, water[-1], 0.3 + 0.06 * k)
                shimmer[0].put(x, sea + 1 + k, tone)
                shimmer[1].put(min(max(x + rnd.choice((-1, 1)), gx0), gx1), sea + 1 + k, tone)

    # a palm against the city, right of the cat
    trunk = ((260, gy1), (255, 45), (257, 33))
    tree = palm((257, 32), (((-9, 5), (-5, -3)), ((-7, -2), (-4, -5)), ((1, -6), (0, -4)),
                            ((7, -2), (4, -5)), ((9, 5), (5, -3))), trunk)
    tree |= {(x + 1, y) for x, y in curve(*trunk)} | {(x, y + 1) for x, y in tree}
    for x, y in tree:
        if gx0 <= x <= gx1 and gy0 <= y <= gy1:
            bg.put(x, y, "#0b0820")
            for t in twinkle + shimmer:
                t.px.pop((x, y), None)

    # window frame, sill
    frame, frame_hi = "#150c2a", "#2a1a4f"
    for x in range(168, 270):
        for y in range(7, 58):
            if not (gx0 <= x <= gx1 and gy0 <= y <= gy1):
                fg.put(x, y, frame)
    fg.rect(218, gy0, 2, gy1 - gy0 + 1, frame)
    fg.rect(gx0, 25, gx1 - gx0 + 1, 2, frame)
    fg.rect(168, 7, 102, 1, frame_hi)
    fg.rect(168, 7, 1, 51, frame_hi)
    fg.rect(164, 58, 110, 2, "#3a2c72")
    fg.rect(164, 60, 110, 1, "#241a4f")

    # plant on the sill
    greens = ("#1d5a4a", "#2e8a62", "#57c48b")
    for x in range(174, 187):
        for y in range(44, 55):
            if ((x - 180) / 6.5) ** 2 + ((y - 50) / 5) ** 2 < 1 and rnd.random() < 0.72:
                fg.put(x, y, rnd.choice(greens))
    fg.rect(176, 54, 9, 1, "#ff7ac8")
    fg.rect(177, 55, 7, 3, "#c4489c")

    # cat asleep on the sill
    fg.sprite(229, 50, CAT_NAP, GREY)
    z1, z2 = Layer(), Layer()
    z1.sprite(238, 46, Z_SMALL, {"Z": "#9ff7ff"})
    z2.sprite(242, 43, Z_BIG, {"Z": "#9ff7ff"})

    # low bookcase under the window
    fg.rect(170, 68, 98, 1, "#3a2c72")
    fg.rect(170, 69, 98, 1, "#2a1f5c")
    fg.rect(170, 70, 98, 14, "#1a1236")
    fg.rect(173, 72, 92, 10, "#0d0820")
    spines = (PINK, CYAN, "#7b5cd6", GOLD, "#3a2f7a", "#e9e3ff", "#c94fd8", "#2fb8c9")
    x = 174
    while x < 263:
        if rnd.random() < 0.1:
            x += rnd.randint(2, 4)
            continue
        w, h = rnd.randint(2, 3), rnd.randint(6, 9)
        fg.rect(x, 82 - h, w, h, rnd.choice(spines))
        if w == 3 and h > 6:
            fg.put(x + 1, 82 - h + 2, "#f3e3ff")
        x += w
    fg.rect(157, 80, 13, 4, "#120c28")
    fg.rect(268, 80, 12, 4, "#120c28")

    # desk, lit cyan by the lamp, with a neon strip along its edge
    for x in range(157):
        fg.put(x, 66, ramp(max(0.0, 1 - abs(x - 29) / 50), ("#2a1d5a", "#34468f", "#5fd9ec"), x, 66))
    fg.rect(0, 67, 157, 1, "#ff4fd2")
    fg.rect(0, 68, 157, 16, "#1a1236")
    fg.rect(0, 68, 157, 1, "#6a2479")
    for x0 in (9, 97):
        fg.rect(x0, 72, 51, 1, "#2d2060")
        fg.rect(x0, 81, 51, 1, "#2d2060")
        fg.rect(x0, 72, 1, 10, "#2d2060")
        fg.rect(x0 + 50, 72, 1, 10, "#2d2060")
        fg.rect(x0 + 24, 76, 3, 1, "#ff7ad9")

    # lamp
    metal, metal_hi = "#1c1840", "#3c3680"
    fg.rect(9, 64, 12, 2, metal)
    fg.rect(14, 46, 2, 18, metal)
    for i in range(11):
        fg.rect(15 + i, 46 - i, 2, 1, metal)
    for j, (a, b) in enumerate(((26, 29), (25, 31), (24, 33), (23, 35), (22, 36))):
        fg.rect(a, 35 + j, b - a + 1, 1, metal)
        fg.put(a, 35 + j, metal_hi)
    fg.rect(22, 40, 15, 1, metal_hi)
    fg.rect(24, 41, 11, 1, "#e3feff")
    fg.rect(26, 42, 7, 1, CYAN)

    # books, laptop, mug, the Claude crab, cactus
    fg.rect(40, 63, 18, 3, "#7b5cd6")
    fg.rect(40, 63, 18, 1, "#a58cff")
    fg.rect(43, 64, 2, 2, "#ece6ff")
    fg.rect(42, 60, 15, 3, "#e04fbf")
    fg.rect(42, 60, 15, 1, "#ff8fe6")
    fg.rect(41, 58, 14, 2, "#2fb8c9")
    fg.rect(41, 58, 14, 1, "#8ff3ff")

    fg.rect(69, 44, 30, 19, "#1a1440")
    fg.rect(71, 46, 26, 15, "#0b0a26")
    code = (
        (0, (GOLD, 4), (VIOLET, 6)),
        (2, (CYAN, 3), ("#5d5890", 5), (PINK, 3)),
        (2, (VIOLET, 5), (GOLD, 3)),
        (4, (CYAN, 7)),
        (2, (PINK, 2), ("#5d5890", 6)),
        (0, (GOLD, 3)),
    )
    for n, (indent, *segs) in enumerate(code):
        x = 73 + indent
        for c, w in segs:
            fg.rect(x, 48 + n * 2, w, 1, c)
            x += w + 1
    cursor = Layer()
    cursor.rect(x, 58, 2, 1, "#e9fbff")
    fg.rect(65, 63, 38, 2, "#8f88cc")
    fg.rect(65, 65, 38, 1, "#5d5596")

    fg.sprite(108, 60, ("WWWWWWS..", "WWWWWWSHH", "WWWWWWS.H", "WWWWWWSHH", "WWWWWWS..", ".WWWWS..."),
              {"W": "#2a1f5c", "S": "#1c1545", "H": "#2a1f5c"})
    fg.rect(108, 60, 6, 1, "#3d3080")
    steam = [Layer(), Layer(), Layer()]
    wisps = (
        ((111, 58), (112, 57), (111, 56), (110, 55), (111, 54)),
        ((112, 58), (111, 57), (110, 56), (111, 55), (112, 54), (112, 53)),
        ((111, 58), (110, 57), (111, 56), (112, 55), (111, 54), (110, 53), (111, 52)),
    )
    for layer, pts in zip(steam, wisps):
        for p in pts:
            layer.put(*p, "#e9dcff")

    fg.sprite(121, 54, CRAB_SPECS, {"O": CLAUDE, "G": "#120b26", "L": "#2a2060", "K": "#2a2060"})
    for x in (124, 131):  # sunglasses here, with a glint on each lens
        fg.put(x, 57, "#9ff7ff")
    arm_down, arm_up = Layer(), Layer()
    arm_down.rect(136, 57, 1, 2, CLAUDE)
    arm_up.rect(136, 55, 1, 2, CLAUDE)

    fg.rect(142, 61, 8, 1, "#ff7ac8")
    fg.rect(143, 62, 6, 4, "#c4489c")
    fg.rect(145, 54, 2, 7, "#2e8a62")
    fg.put(145, 54, "#57c48b")
    for p in ((144, 58), (143, 58), (143, 57), (147, 57), (148, 57), (148, 56)):
        fg.put(*p, "#2e8a62")

    # hanging vines
    for x0, length in ((3, 31), (10, 21), (17, 27), (275, 19)):
        x = x0
        for y in range(length):
            fg.put(x, y, greens[0])
            if y % 3 == 1:
                s = 1 if (y // 3 + x0) % 2 else -1
                fg.put(x + s, y, greens[2])
                fg.put(x + 2 * s, y, greens[1])
                fg.put(x + s, y + 1, greens[1])
                fg.put(x + 2 * s, y + 1, greens[0])
            if y % 5 == 4:
                x += rnd.choice((-1, 0, 1))

    # the name in pink neon, and a cyan neon palm beside it
    letters = Layer()
    text(letters, 46, 10, "HAEGAN", PINK)
    text(letters, 46, 27, "McGARRY", PINK)
    neon(fg, letters.px.keys(), "#ffe0f6", "#e03abb", "#7a2a92")
    sign = Layer()
    neon(sign, palm((149, 13), (((-12, 7), (-6, -3)), ((-9, -2), (-5, -6)), ((-1, -8), (-1, -5)),
                                ((8, -3), (4, -6)), ((12, 6), (6, -3))), ((146, 40), (152, 27), (149, 14))),
         "#e3feff", "#3fe0ff", "#1f4f8f")

    # pixel-rounded corners
    for layer in (bg, fg):
        for cx, sx in ((0, 1), (W - 1, -1)):
            for cy, sy in ((0, 1), (H - 1, -1)):
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    layer.px.pop((cx + sx * dx, cy + sy * dy), None)

    css = (
        ZZZ
        + FRAMES2
        + ".w1,.w2{animation:w 3s steps(1) infinite}.w2{animation-delay:-1.5s}@keyframes w{50%{opacity:0}}"
        + ".s1{animation:s1 2.4s steps(1) infinite}.s2,.s3{opacity:0}"
        ".s2{animation:s2 2.4s steps(1) infinite}.s3{animation:s3 2.4s steps(1) infinite}"
        "@keyframes s1{0%{opacity:1}33.3%{opacity:0}}"
        "@keyframes s2{0%{opacity:0}33.3%{opacity:1}66.6%{opacity:0}}"
        "@keyframes s3{0%{opacity:0}66.6%{opacity:1}}"
        ".cur{animation:cur 1.1s steps(1) infinite}@keyframes cur{50%{opacity:0}}"
        ".flk{animation:flk 7s steps(1) infinite}"
        "@keyframes flk{90%{opacity:.35}91.5%{opacity:1}93%{opacity:.55}94%{opacity:1}}"
        ".tw{animation:tw 9s steps(1) infinite}.t2{animation-delay:-3s}.t3{animation-delay:-6s}"
        "@keyframes tw{55%{opacity:0}70%{opacity:1}}"
    )
    body = (
        bg.svg()
        + "".join(t.svg(f'class="tw t{n + 1}"') for n, t in enumerate(twinkle))
        + "".join(s.svg(f'class="w{n + 1}"') for n, s in enumerate(shimmer))
        + sign.svg('class="flk"')
        + fg.svg()
        + z1.svg('class="z1"') + z2.svg('class="z2"')
        + "".join(s.svg(f'class="s{n + 1}" fill-opacity=".6"') for n, s in enumerate(steam))
        + cursor.svg('class="cur"')
        + arm_down.svg('class="a"') + arm_up.svg('class="b"')
    )
    label = ("Haegan McGarry in pink neon. Pixel art of a desk at night by the bay: a neon palm on the wall, "
             "city lights on the water, a cat asleep on the sill and the Claude crab in sunglasses on the desk.")
    return doc(W, H, 3, label, css, body)


def crab():
    dark, lens = "#160e2e", "#fbeed8"
    body, down, up, blink = Layer(), Layer(), Layer(), Layer()
    body.sprite(0, 0, CRAB_SPECS, {"O": CLAUDE, "G": dark, "K": dark, "L": lens})
    down.rect(15, 3, 1, 2, CLAUDE)  # right arm at rest
    up.rect(15, 1, 1, 2, CLAUDE)  # and waving
    for x in (3, 10):  # eyes shut: the lens empties above a closed lid
        blink.rect(x, 3, 3, 1, lens)
        blink.rect(x, 4, 3, 1, dark)
    css = FRAMES2 + ".blink{opacity:0;animation:blink 5s steps(1) infinite}@keyframes blink{46%{opacity:1}49%{opacity:0}}"
    parts = body.svg() + down.svg('class="a"') + up.svg('class="b"') + blink.svg('class="blink"')
    return doc(16, 12, 3, "A small orange crab wearing glasses, waving.", css, parts)


NETOPS = (("Detect", "CloudTrail"), ("Prove", "vs baseline"), ("Measure", "reachability"), ("Repair", "policy gate"))
TIERS = (("LOW", "60 s veto", CYAN), ("MED", "1 approval", GOLD), ("HIGH", "2 approvers", PINK))
NETOPS_CSS = (
    "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif;"
    "text-anchor:middle}.t{font-size:12px;font-weight:600;fill:" + TEXT + "}"
    ".c{font-size:10px;fill:" + MUTED + "}.k{font-size:9px;font-weight:700;letter-spacing:.06em;text-anchor:start}"
    ".a{font-size:10px;fill:" + TEXT + ";text-anchor:start}.box{fill:" + PANEL + ";stroke:" + EDGE + "}"
    ".ln{fill:none;stroke:" + CYAN + ";stroke-width:1.5;stroke-linejoin:round}"
    ".tick{stroke:" + EDGE + ";stroke-dasharray:2 3}"
    ".l{text-anchor:start}.m{text-anchor:middle}.r{text-anchor:end}"  # last, so they win over .k and .a
)
NETOPS_LABEL = (
    "Agentic NetOps incident loop: detect from CloudTrail, prove the drift against the baseline, "
    "measure reachability, plan a policy-gated repair, route it by risk tier (low runs after a 60 s veto, "
    "medium needs one approval, high needs two approvers), execute with scoped STS credentials, "
    "verify by re-diffing. Every decision lands in a hash-chained ledger."
)
ARROWHEAD = (
    '<defs><marker id="ah" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="7" markerHeight="7" '
    f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L8 4L0 8z" fill="{CYAN}"/></marker></defs>'
)


def netops():
    """Agentic NetOps' incident loop, as a card in the page's colours."""
    W, H, Y, R = 840, 160, 62, 120  # Y: the row's centre line, R: the ledger rail's top
    bw, bh, dia, sw = 86, 46, 26, 118  # box size, diamond half-diagonal, approval stack width
    out, ticks = [], []

    def box(x, title, caption):
        out.append(f'<rect x="{x}" y="{Y - bh // 2}" width="{bw}" height="{bh}" rx="6" class="box"/>'
                   f'<text x="{x + bw // 2}" y="{Y - 3}" class="t">{title}</text>'
                   f'<text x="{x + bw // 2}" y="{Y + 13}" class="c">{caption}</text>')
        ticks.append((x + bw // 2, Y + bh // 2))
        return x + bw

    def arrow(d):
        out.append(f'<path d="{d}" class="ln" marker-end="url(#ah)"/>')

    x = 18
    for title, caption in NETOPS:
        if x > 18:
            arrow(f"M{x + 1} {Y}H{x + 13}")
            x += 14
        x = box(x, title, caption)
    arrow(f"M{x + 1} {Y}H{x + 13}")
    cx = x + 14 + dia
    out.append(f'<path d="M{cx - dia} {Y}L{cx} {Y - dia}L{cx + dia} {Y}L{cx} {Y + dia}z" '
               f'fill="{PANEL}" stroke="{VIOLET}"/>'
               f'<text x="{cx}" y="{Y - 2}" class="c">risk</text><text x="{cx}" y="{Y + 10}" class="c">tier</text>')
    ticks.append((cx, Y + dia))
    x, stack = cx + dia, cx + dia + 24
    for k, (tier, action, colour) in enumerate(TIERS):
        cy = Y + (k - 1) * 28
        arrow(f"M{x + 1} {Y}H{x + 12}V{cy}H{stack - 1}")
        out.append(f'<rect x="{stack}" y="{cy - 11}" width="{sw}" height="22" rx="11" fill="#1f1442" stroke="{colour}"/>'
                   f'<text x="{stack + 10}" y="{cy + 3.5}" class="k" fill="{colour}">{tier}</text>'
                   f'<text x="{stack + 44}" y="{cy + 3.5}" class="a">{action}</text>')
        out.append(f'<path d="M{stack + sw + 1} {cy}H{stack + sw + 12}V{Y}" class="ln"/>')
    ticks.append((stack + sw // 2, Y + 39))
    x = stack + sw + 12
    arrow(f"M{x} {Y}H{x + 11}")
    x = box(x + 12, "Execute", "scoped STS")
    arrow(f"M{x + 1} {Y}H{x + 13}")
    x = box(x + 14, "Verify", "re-diff")
    assert x == W - 18, x  # the row fills the card exactly

    ledger = "every decision lands in a hash-chained ledger in DynamoDB, its head anchored out of band"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{NETOPS_LABEL}"><title>{NETOPS_LABEL}</title><style>{NETOPS_CSS}</style>'
        + ARROWHEAD
        + f'<rect width="{W}" height="{H}" rx="12" fill="{NIGHT}"/>'
        + "".join(f'<path d="M{tx} {ty + 3}V{R - 3}" class="tick"/>' for tx, ty in ticks)
        + f'<rect x="18" y="{R}" width="{W - 36}" height="22" rx="11" fill="#140d2a" stroke="#3a2a6e"/>'
        f'<text x="{W // 2}" y="{R + 15}" class="c">{ledger}</text>'
        + "".join(out)
        + "</svg>\n"
    )


def netops_narrow():
    """The same loop stacked top to bottom, which the README serves to phones and portrait tablets."""
    W, x0, bw, bh = 360, 14, 332, 30
    cx, rail = W // 2, W - 7
    centres = [x0 + 52 + k * 114 for k in range(3)]  # three 104-wide tier pills, 10 apart
    out, ticks = [], []

    def box(y, title, caption):
        out.append(f'<rect x="{x0}" y="{y}" width="{bw}" height="{bh}" rx="6" class="box"/>'
                   f'<text x="{x0 + 12}" y="{y + 19}" class="t l">{title}</text>'
                   f'<text x="{x0 + bw - 12}" y="{y + 19}" class="c r">{caption}</text>')
        ticks.append(y + bh // 2)
        return y + bh

    def arrow(d):
        out.append(f'<path d="{d}" class="ln" marker-end="url(#ah)"/>')

    y = 14
    for title, caption in NETOPS:
        if y > 14:
            arrow(f"M{cx} {y + 1}V{y + 13}")
            y += 14
        y = box(y, title, caption)
    split, pills = y + 14, y + 26  # the repair fans out by risk tier, then joins again
    merge = pills + 40
    out.append(f'<path d="M{cx} {y + 1}V{split}M{centres[0]} {split}H{centres[-1]}M{centres[0]} {merge}H{centres[-1]}" '
               f'class="ln"/><text x="{cx + 6}" y="{split - 4}" class="c l">risk tier</text>')
    for (tier, action, colour), px in zip(TIERS, centres):
        arrow(f"M{px} {split}V{pills - 1}")
        out.append(f'<rect x="{px - 52}" y="{pills}" width="104" height="30" rx="8" fill="#1f1442" stroke="{colour}"/>'
                   f'<text x="{px}" y="{pills + 12}" class="k m" fill="{colour}">{tier}</text>'
                   f'<text x="{px}" y="{pills + 24}" class="a m">{action}</text>'
                   f'<path d="M{px} {pills + 31}V{merge}" class="ln"/>')
    ticks.append(pills + 15)
    arrow(f"M{cx} {merge}V{merge + 13}")
    y = box(merge + 14, "Execute", "scoped STS")
    arrow(f"M{cx} {y + 1}V{y + 13}")
    y = box(y + 14, "Verify", "re-diff")
    ledger, H = y + 14, y + 64
    ticks.append(ledger + 18)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{NETOPS_LABEL}"><title>{NETOPS_LABEL}</title><style>{NETOPS_CSS}</style>'
        + ARROWHEAD
        + f'<rect width="{W}" height="{H}" rx="12" fill="{NIGHT}"/>'
        + "".join(f'<path d="M{x0 + bw + 1} {ty}H{rail}" class="tick"/>' for ty in ticks)
        + f'<path d="M{rail} {ticks[0]}V{ticks[-1]}" class="tick"/>'
        + f'<rect x="{x0}" y="{ledger}" width="{bw}" height="36" rx="10" fill="#140d2a" stroke="#3a2a6e"/>'
        f'<text x="{cx}" y="{ledger + 15}" class="c">every decision lands in a hash-chained ledger</text>'
        f'<text x="{cx}" y="{ledger + 28}" class="c">in DynamoDB, its head anchored out of band</text>'
        + "".join(out)
        + "</svg>\n"
    )


CHIPS = (  # (icon in icons/, label): each project's tech tags, one image apiece so a line wrap never splits one
    ("aws", "AWS SAM"), ("stepfunctions", "Step Functions"), ("lambda", "Lambda"), ("dynamodb", "DynamoDB"),
    ("eventbridge", "EventBridge"), ("cognito", "Cognito"), ("bedrock", "Bedrock"), ("iam", "IAM"),
    ("cloudfront", "CloudFront"), ("go", "Go"), ("docker", "Docker"), ("linux", "tc netem"),
    ("apigateway", "API Gateway"), ("terraform", "Terraform"), ("githubactions", "GitHub Actions"),
    ("c", "C11"), ("cmake", "CMake"), ("python", "Python ctypes"), ("pypi", "PyPI trusted publishing"),
    ("typescript", "TypeScript"), ("nextjs", "Next.js"), ("sqlite", "SQLite"), ("python", "Python"),
    ("spotify", "Spotify Web API"), ("oauth", "OAuth PKCE"), ("windows", "Windows"),
)


def chip_name(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower().replace(".", "")).strip("-")


def chip(icon, label):
    """A tech tag: the icon nested at 14 px, then the label in monospace, forced to a known width."""
    src = (OUT / "icons" / f"{icon}.svg").read_text(encoding="utf-8")
    start = re.search(r"<svg\b[^>]*>", src)
    view = start and re.search(r'viewBox="([^"]+)"', start.group(0))
    assert start and view, f"icons/{icon}.svg needs an <svg> with a viewBox"
    inner = src[start.end():src.rindex("</svg>")]
    tw = round(6.6 * len(label), 1)  # 11 px monospace runs about 0.6 em a character
    w = round(24 + tw + 7)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} 20" width="{w}" height="20" role="img" aria-label="{label}"><title>{label}</title>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="19" rx="3.5" fill="{NIGHT}" stroke="#35206a"/>'
        # icons that set no fill of their own would be black on navy, so give them a light default
        f'<svg x="5" y="3" width="14" height="14" viewBox="{view.group(1)}" fill="#e9e3ff">{inner}</svg>'
        f'<text x="24" y="14" textLength="{tw}" lengthAdjust="spacingAndGlyphs" fill="{TEXT}" font-size="11" '
        f"font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace\">{label}</text></svg>\n"
    )


BADGE_ICONS = {  # shields.io dropped the LinkedIn and AWS logos, so the badges carry these
    "linkedin": ("X......", ".......", "X.XXX..", "X.X..X.", "X.X..X.", "X.X..X.", "X.X..X."),
    "email": ("XXXXXXXXX", "XX.....XX", "X.X...X.X", "X..X.X..X", "X...X...X", "X.......X", "XXXXXXXXX"),
    "cloud": ("...XXX...", "..XXXXX..", ".XXXXXXXX", "XXXXXXXXX", "XXXXXXXXX", ".XXXXXXX."),
}


def badge_logo(rows, colour=PINK):
    """A data URI for the `logo=` parameter of a shields.io badge."""
    icon = Layer()
    icon.sprite(0, 0, rows, {"X": colour})
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {len(rows[0])} {len(rows)}" '
           f'shape-rendering="crispEdges">{icon.svg()}</svg>')
    return "data:image/svg%2bxml;base64," + quote(base64.b64encode(svg.encode()).decode(), safe="")


if __name__ == "__main__":
    if "--badges" in sys.argv:
        for name, rows in BADGE_ICONS.items():
            print(name, badge_logo(rows))
        sys.exit()
    for name, draw in (("banner", banner), ("crab", crab), ("netops-loop", netops), ("netops-loop-narrow", netops_narrow)):
        svg = draw()
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"{name}.svg  {len(svg) / 1024:.1f} KB")
    (OUT / "chips").mkdir(exist_ok=True)
    for icon, label in CHIPS:
        (OUT / "chips" / f"{chip_name(label)}.svg").write_text(chip(icon, label), encoding="utf-8", newline="\n")
    print(f"chips/  {len(CHIPS)} tags")

#!/usr/bin/env python3
"""Draws this profile's pixel art, and its NetOps diagram, as SVG. Standard library only.

    python assets/build.py

The pixel art is a grid of logical pixels. Same-coloured pixels are merged into
rectangles, and the moving parts are separate layers driven by stepped CSS
keyframes, so nothing here is a bitmap. Seeded, so the output is reproducible.
"""
import base64
import random
import sys
from pathlib import Path
from urllib.parse import quote

OUT = Path(__file__).parent
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


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
GREY = {"K": "#3a2a3f", "G": "#9d94ad", "D": "#756c87", "W": "#f3ead9", "E": "#3a2a3f", "P": "#f29aa5"}

CRAB = (
    ".OOOOOOOO.",
    ".OKOOOOKO.",
    "OOKOOOOKOO",
    ".OOOOOOOO.",
    ".OOOOOOOO.",
    ".O.O..O.O.",
)

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
    rnd = random.Random(11)
    bg, fg = Layer(), Layer()

    # wall, lit by the desk lamp
    wall = ("#3f2c47", "#4b3049", "#5e374a", "#784449", "#96564a", "#b8704f")
    for y in range(H):
        for x in range(W):
            d = ((x - 29) ** 2 + ((y - 46) * 1.2) ** 2) ** 0.5
            bg.put(x, y, ramp(max(0.0, 1 - d / 64) ** 1.4, wall, x, y))

    # dusk sky through the glass
    gx0, gy0, gx1, gy1 = 172, 11, 265, 54
    sky = ("#2a2356", "#3d2c6b", "#5c3a7c", "#8a4a82", "#bb5f7c", "#e27c66", "#f4a460", "#fbc97f")
    for y in range(gy0, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            bg.put(x, y, ramp((y - gy0) / 34, sky, x, y))
    for x, y in ((176, 13), (191, 17), (203, 12), (226, 14), (240, 19), (252, 13), (261, 21), (212, 21)):
        bg.put(x, y, "#e9dcff")
    bg.sprite(182, 15, (".XX", "XX.", "XX.", "XX.", ".XX"), {"X": "#fdf0c8"})

    # skyline: three depths, the nearer ones with lit windows
    twinkle = [Layer(), Layer(), Layer()]

    def skyline(colour, lo, hi, wmin, wmax, lit, p, gap=0.0, spire=0.0):
        x = gx0 - rnd.randint(0, 3)
        while x <= gx1:
            w = rnd.randint(wmin, wmax)
            top = rnd.randint(lo, hi) if rnd.random() >= gap else gy1 - 3
            for i in range(max(x, gx0), min(x + w, gx1 + 1)):
                for j in range(top, gy1 + 1):
                    bg.put(i, j, colour)
            if rnd.random() < spire and gx0 <= x + w // 2 <= gx1:
                for j in range(top - 4, top):
                    bg.put(x + w // 2, j, colour)
            for j in range(top + 2, gy1 - 1, 3):
                for i in range(x + 1, x + w - 1, 2):
                    if lit and gx0 <= i <= gx1 and rnd.random() < p:
                        target = rnd.choice(twinkle) if rnd.random() < 0.12 else bg
                        target.put(i, j, rnd.choice(lit))
                        target.put(i, j + 1, lit[0])
            x += w

    skyline("#a8607f", 34, 43, 4, 8, None, 0, gap=0.3)
    skyline("#56397a", 30, 45, 6, 11, ("#f2b06a", "#e58f6a"), 0.22, gap=0.15, spire=0.3)
    skyline("#251d42", 43, 50, 8, 14, ("#ffd277", "#ff9f5a"), 0.4)

    # rain, one tile repeated so the loop is seamless
    rain = Layer()
    for _ in range(34):
        x, y = rnd.randint(gx0, gx1), rnd.randint(0, 11)
        for k in range(-1, 5):
            rain.rect(x, gy0 + y + k * 12, 1, 2, "#d9c8f5")

    # window frame, sill
    frame, frame_hi = "#2e1e2e", "#4a2f3e"
    for x in range(168, 270):
        for y in range(7, 58):
            if not (gx0 <= x <= gx1 and gy0 <= y <= gy1):
                fg.put(x, y, frame)
    fg.rect(218, gy0, 2, gy1 - gy0 + 1, frame)
    fg.rect(gx0, 25, gx1 - gx0 + 1, 2, frame)
    fg.rect(168, 7, 102, 1, frame_hi)
    fg.rect(168, 7, 1, 51, frame_hi)
    fg.rect(164, 58, 110, 2, "#8a5a45")
    fg.rect(164, 60, 110, 1, "#5e3a34")

    # plant on the sill
    greens = ("#3f6b3a", "#5f9148", "#8cba5c")
    for x in range(174, 187):
        for y in range(44, 55):
            if ((x - 180) / 6.5) ** 2 + ((y - 50) / 5) ** 2 < 1 and rnd.random() < 0.72:
                fg.put(x, y, rnd.choice(greens))
    fg.rect(176, 54, 9, 1, "#d98a6a")
    fg.rect(177, 55, 7, 3, "#c26e55")

    # cat asleep on the sill
    fg.sprite(229, 50, CAT_NAP, GREY)
    z1, z2 = Layer(), Layer()
    z1.sprite(238, 46, Z_SMALL, {"Z": "#fbeed8"})
    z2.sprite(242, 43, Z_BIG, {"Z": "#fbeed8"})

    # low bookcase under the window
    fg.rect(170, 68, 98, 1, "#8a5a45")
    fg.rect(170, 69, 98, 1, "#6d4539")
    fg.rect(170, 70, 98, 14, "#4a2e33")
    fg.rect(173, 72, 92, 10, "#261a26")
    spines = ("#6f5aa8", "#c9605a", "#5a8a7a", "#d9a05b", "#8a6fb5", "#b5677f", "#4f6d8f", "#e0c9a6")
    x = 174
    while x < 263:
        if rnd.random() < 0.1:
            x += rnd.randint(2, 4)
            continue
        w, h = rnd.randint(2, 3), rnd.randint(6, 9)
        c = rnd.choice(spines)
        fg.rect(x, 82 - h, w, h, c)
        if w == 3 and h > 6:
            fg.put(x + 1, 82 - h + 2, "#f3e3c8")
        x += w
    fg.rect(157, 80, 13, 4, "#33222f")
    fg.rect(268, 80, 12, 4, "#33222f")

    # desk
    for x in range(157):
        lit = ramp(max(0.0, 1 - abs(x - 29) / 60), ("#8f5d45", "#a9714c", "#c68a57"), x, 66)
        fg.put(x, 66, lit)
        fg.put(x, 67, "#7a4c3d")
    fg.rect(0, 68, 157, 16, "#5c3a37")
    fg.rect(0, 68, 157, 1, "#4a2e2f")
    for x0 in (9, 97):
        fg.rect(x0, 72, 51, 1, "#4a2e2f")
        fg.rect(x0, 81, 51, 1, "#4a2e2f")
        fg.rect(x0, 72, 1, 10, "#4a2e2f")
        fg.rect(x0 + 50, 72, 1, 10, "#4a2e2f")
        fg.rect(x0 + 24, 76, 3, 1, "#c9965c")

    # lamp
    metal, metal_hi = "#2b2033", "#4a3a5a"
    fg.rect(9, 64, 12, 2, metal)
    fg.rect(14, 46, 2, 18, metal)
    for i in range(11):
        fg.rect(15 + i, 46 - i, 2, 1, metal)
    for j, (a, b) in enumerate(((26, 29), (25, 31), (24, 33), (23, 35), (22, 36))):
        fg.rect(a, 35 + j, b - a + 1, 1, metal)
        fg.put(a, 35 + j, metal_hi)
    fg.rect(22, 40, 15, 1, metal_hi)
    fg.rect(24, 41, 11, 1, "#fff0b8")
    fg.rect(26, 42, 7, 1, "#ffd27a")

    # books, laptop, mug, crab, cactus
    fg.rect(40, 63, 18, 3, "#6f5aa8")
    fg.rect(40, 63, 18, 1, "#8a76c2")
    fg.rect(43, 64, 2, 2, "#e9dcc6")
    fg.rect(42, 60, 15, 3, "#c9605a")
    fg.rect(42, 60, 15, 1, "#de7c70")
    fg.rect(41, 58, 14, 2, "#5a8a7a")
    fg.rect(41, 58, 14, 1, "#76a892")

    fg.rect(69, 44, 30, 19, "#2b2336")
    fg.rect(71, 46, 26, 15, "#1b1930")
    code = (
        (0, ("#f6a66a", 4), ("#b79cf0", 6)),
        (2, ("#7fd6b0", 3), ("#7c779a", 5), ("#f58ea8", 3)),
        (2, ("#b79cf0", 5), ("#f6a66a", 3)),
        (4, ("#7fd6b0", 7)),
        (2, ("#f58ea8", 2), ("#7c779a", 6)),
        (0, ("#f6a66a", 3)),
    )
    for n, (indent, *segs) in enumerate(code):
        x = 73 + indent
        for c, w in segs:
            fg.rect(x, 48 + n * 2, w, 1, c)
            x += w + 1
    cursor = Layer()
    cursor.rect(x, 58, 2, 1, "#fbeed8")
    fg.rect(65, 63, 38, 2, "#a39cb8")
    fg.rect(65, 65, 38, 1, "#6f6888")

    fg.sprite(108, 60, ("WWWWWWS..", "WWWWWWSHH", "WWWWWWS.H", "WWWWWWSHH", "WWWWWWS..", ".WWWWS..."),
              {"W": "#f1e2cf", "S": "#d2bca9", "H": "#f1e2cf"})
    steam = [Layer(), Layer(), Layer()]
    wisps = (
        ((111, 58), (112, 57), (111, 56), (110, 55), (111, 54)),
        ((112, 58), (111, 57), (110, 56), (111, 55), (112, 54), (112, 53)),
        ((111, 58), (110, 57), (111, 56), (112, 55), (111, 54), (110, 53), (111, 52)),
    )
    for layer, pts in zip(steam, wisps):
        for p in pts:
            layer.put(*p, "#f3e6f5")

    fg.sprite(124, 60, CRAB, {"O": "#d97757", "K": "#2a1b22"})
    blink = Layer()
    blink.rect(126, 61, 1, 2, "#d97757")
    blink.rect(131, 61, 1, 2, "#d97757")

    fg.rect(142, 61, 8, 1, "#d98a6a")
    fg.rect(143, 62, 6, 4, "#c26e55")
    fg.rect(145, 54, 2, 7, "#5f9148")
    fg.put(145, 54, "#8cba5c")
    for p in ((144, 58), (143, 58), (143, 57), (147, 57), (148, 57), (148, 56)):
        fg.put(*p, "#5f9148")

    # hanging vines
    for x0, length in ((3, 31), (10, 21), (17, 27), (150, 24), (158, 15), (275, 19)):
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

    # the name
    for dx, c in ((1, "#2b1d33"), (0, "#fbeed8")):
        text(fg, 46 + dx, 10 + dx, "HAEGAN", c)
        text(fg, 46 + dx, 27 + dx, "McGARRY", c)

    # pixel-rounded corners
    for layer in (bg, fg):
        for cx, sx in ((0, 1), (W - 1, -1)):
            for cy, sy in ((0, 1), (H - 1, -1)):
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    layer.px.pop((cx + sx * dx, cy + sy * dy), None)

    css = (
        ".rain{animation:rain .7s steps(6) infinite}@keyframes rain{to{transform:translateY(12px)}}"
        + ZZZ
        + ".s1{animation:s1 2.4s steps(1) infinite}.s2,.s3{opacity:0}"
        ".s2{animation:s2 2.4s steps(1) infinite}.s3{animation:s3 2.4s steps(1) infinite}"
        "@keyframes s1{0%{opacity:1}33.3%{opacity:0}}"
        "@keyframes s2{0%{opacity:0}33.3%{opacity:1}66.6%{opacity:0}}"
        "@keyframes s3{0%{opacity:0}66.6%{opacity:1}}"
        ".cur{animation:cur 1.1s steps(1) infinite}@keyframes cur{50%{opacity:0}}"
        ".blink{opacity:0;animation:blink 5s steps(1) infinite}@keyframes blink{94%{opacity:1}97%{opacity:0}}"
        ".tw{animation:tw 9s steps(1) infinite}.t2{animation-delay:-3s}.t3{animation-delay:-6s}"
        "@keyframes tw{55%{opacity:0}70%{opacity:1}}"
    )
    body = (
        bg.svg()
        + "".join(t.svg(f'class="tw t{n + 1}"') for n, t in enumerate(twinkle))
        + f'<clipPath id="glass"><rect x="{gx0}" y="{gy0}" width="{gx1 - gx0 + 1}" height="{gy1 - gy0 + 1}"/></clipPath>'
        + '<g clip-path="url(#glass)">' + rain.svg('class="rain" fill-opacity=".45"') + "</g>"
        + fg.svg()
        + z1.svg('class="z1"') + z2.svg('class="z2"')
        + "".join(s.svg(f'class="s{n + 1}" fill-opacity=".6"') for n, s in enumerate(steam))
        + cursor.svg('class="cur"') + blink.svg('class="blink"')
    )
    return doc(W, H, 3, "Haegan McGarry. A pixel art desk at dusk: rain on the window, a cat asleep on the sill.", css, body)


CRAB_SPECS = (  # the desk crab, bigger and wearing glasses
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


def crab():
    orange, dark, lens = "#d97757", "#2a1b22", "#fbeed8"
    body, down, up, blink = Layer(), Layer(), Layer(), Layer()
    body.sprite(0, 0, CRAB_SPECS, {"O": orange, "G": dark, "K": dark, "L": lens})
    down.rect(15, 3, 1, 2, orange)  # right arm at rest
    up.rect(15, 1, 1, 2, orange)  # and waving
    for x in (3, 10):  # eyes shut: the lens empties above a closed lid
        blink.rect(x, 3, 3, 1, lens)
        blink.rect(x, 4, 3, 1, dark)
    css = FRAMES2 + ".blink{opacity:0;animation:blink 5s steps(1) infinite}@keyframes blink{46%{opacity:1}49%{opacity:0}}"
    parts = body.svg() + down.svg('class="a"') + up.svg('class="b"') + blink.svg('class="blink"')
    return doc(16, 12, 3, "A small orange crab wearing glasses, waving.", css, parts)


NETOPS = (("Detect", "CloudTrail"), ("Prove", "vs baseline"), ("Measure", "reachability"), ("Repair", "policy gate"))
TIERS = (("LOW", "60 s veto", "#7fd6b0"), ("MED", "1 approval", "#f6b077"), ("HIGH", "2 approvers", "#f58ea8"))
NETOPS_CSS = (
    "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif;"
    "text-anchor:middle}.t{font-size:12px;font-weight:600;fill:#fbeed8}.c{font-size:10px;fill:#c9b3d6}"
    ".k{font-size:9px;font-weight:700;letter-spacing:.06em;text-anchor:start}"
    ".a{font-size:10px;fill:#fbeed8;text-anchor:start}.box{fill:#3d2c48;stroke:#5d4569}"
    ".ln{fill:none;stroke:#f6b077;stroke-width:1.5;stroke-linejoin:round}"
    ".tick{stroke:#5d4569;stroke-dasharray:2 3}"
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
               'fill="#3d2c48" stroke="#b79cf0"/>'
               f'<text x="{cx}" y="{Y - 2}" class="c">risk</text><text x="{cx}" y="{Y + 10}" class="c">tier</text>')
    ticks.append((cx, Y + dia))
    x, stack = cx + dia, cx + dia + 24
    for k, (tier, action, colour) in enumerate(TIERS):
        cy = Y + (k - 1) * 28
        arrow(f"M{x + 1} {Y}H{x + 12}V{cy}H{stack - 1}")
        out.append(f'<rect x="{stack}" y="{cy - 11}" width="{sw}" height="22" rx="11" fill="#33263d" stroke="{colour}"/>'
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
    label = ("Agentic NetOps incident loop: detect from CloudTrail, prove the drift against the baseline, "
             "measure reachability, plan a policy-gated repair, route it by risk tier (low runs after a 60 s veto, "
             "medium needs one approval, high needs two approvers), execute with scoped STS credentials, "
             "verify by re-diffing. Every decision lands in a hash-chained ledger.")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{label}"><title>{label}</title><style>{NETOPS_CSS}</style>'
        '<defs><marker id="ah" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="7" markerHeight="7" '
        'markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L8 4L0 8z" fill="#f6b077"/></marker></defs>'
        f'<rect width="{W}" height="{H}" rx="12" fill="#2b2336"/>'
        + "".join(f'<path d="M{tx} {ty + 3}V{R - 3}" class="tick"/>' for tx, ty in ticks)
        + f'<rect x="18" y="{R}" width="{W - 36}" height="22" rx="11" fill="#231b2b" stroke="#4b3a57"/>'
        f'<text x="{W // 2}" y="{R + 15}" class="c">{ledger}</text>'
        + "".join(out)
        + "</svg>\n"
    )


BADGE_ICONS = {  # shields.io dropped the LinkedIn and AWS logos, so the badges carry these
    "linkedin": ("X......", ".......", "X.XXX..", "X.X..X.", "X.X..X.", "X.X..X.", "X.X..X."),
    "email": ("XXXXXXXXX", "XX.....XX", "X.X...X.X", "X..X.X..X", "X...X...X", "X.......X", "XXXXXXXXX"),
    "cloud": ("...XXX...", "..XXXXX..", ".XXXXXXXX", "XXXXXXXXX", "XXXXXXXXX", ".XXXXXXX."),
}


def badge_logo(rows, colour="#f6b077"):
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
    for name, draw in (("banner", banner), ("crab", crab), ("netops-loop", netops)):
        svg = draw()
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
        print(f"{name}.svg  {len(svg) / 1024:.1f} KB")

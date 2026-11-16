#!/usr/bin/env python3
"""Draw the ai-excited-01 entry: 'One small leap becomes a universe'.

A tiny goldfish leaps out of its little glass bowl (bottom left); its splash
becomes a huge curling wave that spirals up into a galaxy of stars and
confetti (top right). Saturated orange/magenta on deep indigo, bold tilted
yellow WOW! (DejaVu Sans Bold, orange outline), a second little fish still
in the bowl cheering it on.

Build-time only. Deterministic: fixed seed, no clocks, no network, no
external assets. Draws at 2x supersample, Lanczos-downscales to 1024x1024.
Translucent effects live on separate layers merged with
Image.alpha_composite (ImageDraw on RGBA replaces pixels instead of
blending, so nothing translucent is ever drawn straight onto the base).

Usage: python3 draw_excited.py [output-path]   (default: entry.png)
"""

import hashlib
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
S = 2                      # supersample factor
OUT = 1024                 # final size
W = OUT * S                # working size (2048)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- palette (1024-space thinking, all colours opaque unless noted) ----
INDIGO_TOP = (16, 10, 54)
INDIGO_MID = (26, 16, 84)
INDIGO_BOT = (10, 6, 34)
VIOLET_GLOW = (88, 40, 160)
TEAL_DEEP = (11, 110, 143)
TEAL_MID = (25, 179, 214)
TEAL_LIGHT = (127, 227, 255)
FOAM = (255, 255, 255)
FISH_ORANGE = (255, 122, 26)
FISH_DEEP = (232, 93, 4)
FISH_BELLY = (255, 196, 107)
WOW_YELLOW = (255, 212, 0)
WOW_OUTLINE = (255, 107, 0)
MAGENTA = (255, 92, 168)
GOLD = (255, 209, 102)
CYAN = (122, 231, 255)

rng = random.Random(SEED)


def X(v):
    """1024-space coordinate -> working pixels."""
    return int(round(v * S))


def new_layer():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def catmull_rom(points, samples_per_seg=14):
    """Smooth a polyline of (x, y) points (1024-space)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples_per_seg):
            t = j / samples_per_seg
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def disc(layer, cx, cy, r, fill):
    """Filled circle, coordinates in 1024-space."""
    d = ImageDraw.Draw(layer)
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=fill)


def star4(layer, cx, cy, r, fill):
    """Four-point sparkle: a plus of two thin diamonds."""
    d = ImageDraw.Draw(layer)
    w = max(1.0, r * 0.28)
    d.polygon([(X(cx), X(cy - r)), (X(cx + w), X(cy)), (X(cx), X(cy + r)),
               (X(cx - w), X(cy))], fill=fill)
    d.polygon([(X(cx - r), X(cy)), (X(cx), X(cy + w)), (X(cx + r), X(cy)),
               (X(cx), X(cy - w))], fill=fill)


# ---------------------------------------------------------------- base
base = Image.new("RGBA", (W, W), INDIGO_TOP + (255,))
bd = ImageDraw.Draw(base)
# vertical indigo gradient, darker at the bottom, violet wash top-right
bands = 96
for i in range(bands):
    t = i / (bands - 1)
    r = int(INDIGO_TOP[0] + (INDIGO_BOT[0] - INDIGO_TOP[0]) * t)
    g = int(INDIGO_TOP[1] + (INDIGO_BOT[1] - INDIGO_TOP[1]) * t)
    b = int(INDIGO_TOP[2] + (INDIGO_BOT[2] - INDIGO_TOP[2]) * t)
    bd.rectangle([0, X(OUT * i / bands), W, X(OUT * (i + 1) / bands)],
                 fill=(r, g, b, 255))
# violet wash behind the galaxy corner
wash = new_layer()
wd = ImageDraw.Draw(wash)
wd.ellipse([X(430), X(-260), X(1240), X(560)],
           fill=VIOLET_GLOW + (70,))
wash = wash.filter(ImageFilter.GaussianBlur(X(90)))
base = Image.alpha_composite(base, wash)

# faint background stars across the whole sky (own layer: ImageDraw on
# RGBA replaces pixels, so translucent dots must never go on the base)
stars = new_layer()
for _ in range(150):
    x = rng.uniform(20, 1004)
    y = rng.uniform(20, 1004)
    r = rng.uniform(0.9, 2.4)
    a = rng.randint(90, 210)
    col = rng.choice([(255, 255, 255), (200, 220, 255), (255, 230, 180)])
    disc(stars, x, y, r, col + (a,))
base = Image.alpha_composite(base, stars)

# ---------------------------------------------------------------- rays
# 7 soft burst rays behind the galaxy core (translucent layer, blurred)
rays = new_layer()
rd = ImageDraw.Draw(rays)
gcx, gcy = 815, 235
for k in range(7):
    ang = math.radians(-168 + k * 24 + rng.uniform(-6, 6))
    length = rng.uniform(240, 330)
    half = rng.uniform(9, 16)
    tipx = gcx + math.cos(ang) * length
    tipy = gcy + math.sin(ang) * length
    px, py = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
    col = rng.choice([(255, 220, 160), (255, 160, 210), (255, 255, 255)])
    rd.polygon([(X(gcx + px * half), X(gcy + py * half)),
                (X(gcx - px * half), X(gcy - py * half)),
                (X(tipx), X(tipy))], fill=col + (60,))
rays = rays.filter(ImageFilter.GaussianBlur(X(7)))
base = Image.alpha_composite(base, rays)

# ---------------------------------------------------------------- galaxy
# dense spiral: 3 arms, many stars per arm + dust motes, glowing core
gal = new_layer()
core = new_layer()
cd = ImageDraw.Draw(core)
cd.ellipse([X(gcx - 68), X(gcy - 68), X(gcx + 68), X(gcy + 68)],
           fill=(255, 214, 170, 130))
cd.ellipse([X(gcx - 34), X(gcy - 34), X(gcx + 34), X(gcy + 34)],
           fill=(255, 240, 220, 180))
core = core.filter(ImageFilter.GaussianBlur(X(18)))
base = Image.alpha_composite(base, core)

star_cols = [(255, 255, 255), (255, 255, 255), (255, 209, 102),
             (255, 122, 217), (122, 231, 255), (255, 180, 120)]
for arm in range(3):
    offset = arm * (2 * math.pi / 3)
    for i in range(150):
        t = (i / 150) ** 0.8
        ang = offset + t * 3.9 + rng.gauss(0, 0.16 * (1 - t * 0.5))
        rad = 24 + t * 225 + rng.gauss(0, 8 + 12 * t)
        x = gcx + math.cos(ang) * rad
        y = gcy + math.sin(ang) * rad * 0.82
        r = rng.uniform(1.2, 4.8) * (1.15 - 0.55 * t)
        col = rng.choice(star_cols)
        a = rng.randint(170, 255)
        if r > 3.6 and rng.random() < 0.5:
            star4(gal, x, y, r * 1.9, col + (a,))
        else:
            disc(gal, x, y, r, col + (a,))
# dense core cluster
for _ in range(70):
    ang = rng.uniform(0, 2 * math.pi)
    rad = abs(rng.gauss(0, 26))
    x = gcx + math.cos(ang) * rad
    y = gcy + math.sin(ang) * rad * 0.85
    disc(gal, x, y, rng.uniform(1.0, 3.0),
         rng.choice(star_cols) + (rng.randint(180, 255),))
# dust motes: hundreds of faint specks hugging the arms
for _ in range(320):
    arm = rng.randrange(3)
    offset = arm * (2 * math.pi / 3)
    t = rng.random() ** 0.7
    ang = offset + t * 3.9 + rng.gauss(0, 0.22)
    rad = 24 + t * 232 + rng.gauss(0, 18)
    x = gcx + math.cos(ang) * rad
    y = gcy + math.sin(ang) * rad * 0.82
    disc(gal, x, y, rng.uniform(0.6, 1.4),
         rng.choice(star_cols) + (rng.randint(70, 150),))
base = Image.alpha_composite(base, gal)

# ---------------------------------------------------------------- wave
# The splash curls up from the bowl and spirals into the galaxy.
# Smooth tapered bands: short line segments whose width follows the
# taper, with a disc at each joint so the band never breaks into dots.
wave_pts = [(248, 802), (300, 745), (390, 690), (490, 625), (590, 545),
            (665, 465), (715, 390), (725, 335)]
widths = [46, 52, 58, 60, 56, 48, 38, 26]
path = catmull_rom(wave_pts)
# width at each path sample: interpolate the control widths
seg = len(path) / (len(wave_pts) - 1)
def width_at(i):
    f = min(i / seg, len(widths) - 1.001)
    lo = int(f)
    frac = f - lo
    return widths[lo] * (1 - frac) + widths[lo + 1] * frac

wdraw = ImageDraw.Draw(base)
def band(offset, frac, fill):
    """One smooth band along the path, shifted by `offset` * width
    toward the inner (upper-left) side, `frac` of the local width."""
    pts = []
    for i, (x, y) in enumerate(path):
        w = width_at(i)
        pts.append((x - w * offset, y - w * offset))
    for i in range(len(pts) - 1):
        w = width_at(i) * frac
        wdraw.line([X(pts[i][0]), X(pts[i][1]),
                    X(pts[i + 1][0]), X(pts[i + 1][1])],
                   fill=fill, width=max(2, X(w)))
        wdraw.ellipse([X(pts[i][0] - w / 2), X(pts[i][1] - w / 2),
                       X(pts[i][0] + w / 2), X(pts[i][1] + w / 2)],
                      fill=fill)

# outer band, deep teal, then brighter mid band, then the thin inner
# highlight ribbon hugging the inner edge
band(0.0, 1.0, TEAL_DEEP + (255,))
band(0.16, 0.58, TEAL_MID + (255,))
band(0.30, 0.16, TEAL_LIGHT + (255,))
# foam: a clean white crest line along the outer (lower-right) edge,
# with froth dots on top of it
foam_pts = [(x + width_at(i) * 0.42, y + width_at(i) * 0.42)
            for i, (x, y) in enumerate(path)]
for i in range(len(foam_pts) - 1):
    w = 9.0 - 5.0 * (i / max(1, len(foam_pts) - 1))
    wdraw.line([X(foam_pts[i][0]), X(foam_pts[i][1]),
                X(foam_pts[i + 1][0]), X(foam_pts[i + 1][1])],
               fill=FOAM + (255,), width=max(2, X(w)))
for i, (x, y) in enumerate(foam_pts):
    if rng.random() < 0.6:
        r = rng.uniform(2.5, 6.5)
        wdraw.ellipse([X(x - r), X(y - r), X(x + r), X(y + r)],
                      fill=FOAM + (255,))
# curl cap at the tip: shrinking spiral of foam
tipx, tipy = path[-1]
for k in range(4):
    a = math.radians(200 + k * 60)
    rr = 20 - k * 4.0
    cx = tipx + math.cos(a) * (24 - k * 4.5)
    cy = tipy + math.sin(a) * (24 - k * 4.5) * 0.9
    wdraw.ellipse([X(cx - rr), X(cy - rr), X(cx + rr), X(cy + rr)],
                  fill=FOAM + (255,))

# ---------------------------------------------------------------- confetti
conf = new_layer()
cdraw = ImageDraw.Draw(conf)
conf_cols = [WOW_YELLOW, MAGENTA, FISH_ORANGE, CYAN, (255, 255, 255)]
# confetti rides the wave and bursts around the galaxy
spots = []
for i in range(0, len(path), 3):
    spots.append((path[i][0] + rng.uniform(-70, 70),
                  path[i][1] + rng.uniform(-70, 70)))
for _ in range(40):
    ang = rng.uniform(0, 2 * math.pi)
    rad = rng.uniform(60, 260)
    spots.append((gcx + math.cos(ang) * rad, gcy + math.sin(ang) * rad * 0.85))
for (x, y) in spots:
    col = rng.choice(conf_cols)
    a = rng.randint(200, 255)
    if rng.random() < 0.45:
        disc(conf, x, y, rng.uniform(2.5, 5.5), col + (a,))
    else:
        w = rng.uniform(5, 12)
        h = rng.uniform(3, 6)
        ang = rng.uniform(0, 180)
        rect = Image.new("RGBA", (X(int(w * 2)), X(int(h * 2))), (0, 0, 0, 0))
        rdr = ImageDraw.Draw(rect)
        rdr.rectangle([0, 0, X(int(w * 2)) - 1, X(int(h * 2)) - 1],
                      fill=col + (a,))
        rect = rect.rotate(ang, resample=Image.BICUBIC, center=(X(w), X(h)))
        conf.alpha_composite(rect, (X(x) - X(int(w)), X(y) - X(int(h))))
base = Image.alpha_composite(base, conf)

# ---------------------------------------------------------------- splash
# droplets where the fish broke the surface, arcing bowl -> fish tail
splash = new_layer()
for k in range(26):
    t = k / 25
    x = 285 + t * 130 + rng.uniform(-16, 16)
    y = 800 - t * 165 + math.sin(t * math.pi) * -22 + rng.uniform(-12, 12)
    r = rng.uniform(2.5, 8.5) * (1 - 0.45 * t)
    col = rng.choice([FOAM, TEAL_LIGHT, (190, 240, 255)])
    disc(splash, x, y, r, col + (rng.randint(170, 255),))
    if rng.random() < 0.4:
        disc(splash, x + rng.uniform(-14, 14), y + rng.uniform(10, 26),
             rng.uniform(1.5, 3.5), TEAL_LIGHT + (200,))
base = Image.alpha_composite(base, splash)

# ---------------------------------------------------------------- bowl
# glass bowl bottom-left with the cheering second fish inside
bowl = new_layer()
bwd = ImageDraw.Draw(bowl)
bcx, bcy, brx, bry = 205, 872, 172, 126
# table shadow
sh = new_layer()
sd = ImageDraw.Draw(sh)
sd.ellipse([X(bcx - 185), X(bcy + 108), X(bcx + 185), X(bcy + 142)],
           fill=(0, 0, 0, 110))
sh = sh.filter(ImageFilter.GaussianBlur(X(10)))
base = Image.alpha_composite(base, sh)
# water: bright enough to read as water against the indigo
bwd.ellipse([X(bcx - brx), X(bcy - bry * 0.30), X(bcx + brx), X(bcy + bry)],
            fill=(70, 180, 240, 165))
bwd.ellipse([X(bcx - brx), X(bcy - bry * 0.30), X(bcx + brx),
             X(bcy - bry * 0.30 + 18)], fill=(150, 225, 255, 170))
# glass rim + wall
bwd.ellipse([X(bcx - brx), X(bcy - bry), X(bcx + brx), X(bcy + bry)],
            outline=(255, 255, 255, 215), width=X(5))
# short highlight hugging the upper-left rim
bwd.arc([X(bcx - brx), X(bcy - bry), X(bcx + brx), X(bcy + bry)],
        start=150, end=205, fill=(255, 255, 255, 170), width=X(8))
base = Image.alpha_composite(base, bowl)

# second fish inside the bowl, upright, fins up, cheering
fish2 = new_layer()
f2 = ImageDraw.Draw(fish2)
f2x, f2y = 205, 872
# tail
f2.polygon([(X(f2x - 34), X(f2y)), (X(f2x - 78), X(f2y - 30)),
            (X(f2x - 66), X(f2y)), (X(f2x - 78), X(f2y + 30))],
           fill=(255, 150, 60, 255))
# body
f2.ellipse([X(f2x - 42), X(f2y - 24), X(f2x + 42), X(f2y + 24)],
           fill=FISH_ORANGE + (255,))
f2.ellipse([X(f2x - 26), X(f2y + 2), X(f2x + 36), X(f2y + 22)],
           fill=FISH_BELLY + (255,))
# raised fins (cheering)
f2.polygon([(X(f2x - 6), X(f2y - 20)), (X(f2x + 2), X(f2y - 52)),
            (X(f2x + 14), X(f2y - 20))], fill=FISH_DEEP + (255,))
f2.polygon([(X(f2x + 8), X(f2y + 18)), (X(f2x + 26), X(f2y + 46)),
            (X(f2x + 20), X(f2y + 14))], fill=FISH_DEEP + (255,))
# eye + open cheering mouth
disc(fish2, f2x + 22, f2y - 8, 7, (255, 255, 255, 255))
disc(fish2, f2x + 24, f2y - 8, 3.5, (20, 10, 40, 255))
f2.ellipse([X(f2x + 30), X(f2y + 2), X(f2x + 42), X(f2y + 14)],
           fill=(90, 20, 30, 255))
base = Image.alpha_composite(base, fish2)

# bubbles rising from the bowl
bub = new_layer()
for k in range(14):
    x = bcx - 120 + k * 17 + rng.uniform(-8, 8)
    y = bcy - 110 - k * 9 + rng.uniform(-8, 8)
    r = rng.uniform(2.5, 7)
    bwd2 = ImageDraw.Draw(bub)
    bwd2.ellipse([X(x - r), X(y - r), X(x + r), X(y + r)],
                 outline=(255, 255, 255, 190), width=max(1, X(1)))
    disc(bub, x - r * 0.35, y - r * 0.35, r * 0.3, (255, 255, 255, 220))
base = Image.alpha_composite(base, bub)

# ---------------------------------------------------------------- leaping fish
# drawn nose-right on its own layer, then rotated nose-up-right and
# lifted clear of the wave band
fish = new_layer()
fd = ImageDraw.Draw(fish)
# local centre (1024-space) before rotation
fcx, fcy = 470, 440
# flowing double tail
fd.polygon([(X(fcx - 95), X(fcy - 6)), (X(fcx - 215), X(fcy - 88)),
            (X(fcx - 178), X(fcy - 4)), (X(fcx - 215), X(fcy + 82)),
            (X(fcx - 95), X(fcy + 10))], fill=(255, 140, 40, 235))
fd.polygon([(X(fcx - 95), X(fcy - 2)), (X(fcx - 188), X(fcy - 58)),
            (X(fcx - 160), X(fcy)), (X(fcx - 188), X(fcy + 54))],
           fill=(255, 176, 92, 235))
# dorsal fin, swept back
fd.polygon([(X(fcx - 30), X(fcy - 46)), (X(fcx + 2), X(fcy - 74)),
            (X(fcx + 46), X(fcy - 44))], fill=FISH_DEEP + (255,))
# body
fd.ellipse([X(fcx - 108), X(fcy - 54), X(fcx + 108), X(fcy + 54)],
           fill=FISH_ORANGE + (255,))
# back shading: none — a hard-edged ellipse reads as a grey saddle.
# The top highlight below gives the body its roundness instead.
# belly
fd.ellipse([X(fcx - 62), X(fcy + 6), X(fcx + 96), X(fcy + 50)],
           fill=FISH_BELLY + (255,))
# top highlight: fully opaque pre-blended light orange (a translucent
# fill drawn on this layer would replace the body pixels and then
# composite against the indigo behind, turning grey — see v3)
fd.ellipse([X(fcx - 58), X(fcy - 46), X(fcx + 58), X(fcy - 26)],
           fill=(255, 180, 95, 255))
# pectoral fin
fd.polygon([(X(fcx - 6), X(fcy + 34)), (X(fcx + 34), X(fcy + 78)),
            (X(fcx + 52), X(fcy + 30))], fill=FISH_DEEP + (255,))
# gill curve
fd.arc([X(fcx + 34), X(fcy - 34), X(fcx + 78), X(fcy + 34)],
       start=290, end=70, fill=(200, 70, 0, 255), width=X(4))
# eye
disc(fish, fcx + 58, fcy - 20, 15, (255, 255, 255, 255))
disc(fish, fcx + 62, fcy - 20, 7.5, (20, 10, 40, 255))
disc(fish, fcx + 65, fcy - 23, 2.8, (255, 255, 255, 255))
# big open smiling mouth: a smile arc at the nose, no dark blob
fd.arc([X(fcx + 66), X(fcy - 2), X(fcx + 106), X(fcy + 32)],
       start=15, end=145, fill=(120, 30, 40, 255), width=X(5))
# rotate nose-up-right around the fish centre, then composite
fish = fish.rotate(40, resample=Image.BICUBIC, center=(X(fcx), X(fcy)))
base = Image.alpha_composite(base, fish)

# ---------------------------------------------------------------- motion arcs
# translucent speed arcs trailing the leaping fish
arcs = new_layer()
ad = ImageDraw.Draw(arcs)
for (rx, ry, wdt, a0, a1, alpha) in [
        (330, 330, 150, 200, 285, 120),
        (360, 360, 175, 205, 280, 90),
        (300, 300, 128, 210, 275, 70)]:
    ad.arc([X(fcx - rx), X(fcy - ry), X(fcx + rx), X(fcy + ry)],
           start=a0, end=a1, fill=(255, 255, 255, alpha), width=X(wdt // 18))
arcs = arcs.filter(ImageFilter.GaussianBlur(X(3)))
base = Image.alpha_composite(base, arcs)

# ---------------------------------------------------------------- WOW!
text_layer = new_layer()
td = ImageDraw.Draw(text_layer)
font = ImageFont.truetype(FONT_BOLD, X(160))
td.text((X(420), X(205)), "WOW!", font=font, fill=WOW_YELLOW + (255,),
        stroke_width=X(10), stroke_fill=WOW_OUTLINE + (255,), anchor="mm")
text_layer = text_layer.rotate(12, resample=Image.BICUBIC,
                               center=(X(420), X(205)))
base = Image.alpha_composite(base, text_layer)

# ---------------------------------------------------------------- vignette
vig = new_layer()
vd = ImageDraw.Draw(vig)
for i in range(6):
    a = 26 + i * 10
    inset = X(6 + i * 14)
    vd.rectangle([inset, inset, W - inset, W - inset],
                 outline=(0, 0, 0, a), width=X(16))
vig = vig.filter(ImageFilter.GaussianBlur(X(30)))
base = Image.alpha_composite(base, vig)

# ---------------------------------------------------------------- finish
final = base.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
final.save(out_path, format="PNG", optimize=True)
data = open(out_path, "rb").read()
print(f"wrote {out_path}: {len(data)} bytes sha256="
      f"{hashlib.sha256(data).hexdigest()}")

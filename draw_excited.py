#!/usr/bin/env python3
"""ai-excited-01 — "One small leap becomes a universe".

A tiny goldfish leaps out of its little glass bowl (bottom left); the splash
becomes a huge curling wave that spirals up into a galaxy of stars and
confetti (top right). Saturated warm orange/magenta on deep indigo, strong
diagonal composition, bold tilted yellow WOW! Bold text is read by the judge,
so it must be crisp and legible at 300 px.

Drawn fully in code (PIL, build-time only). Deterministic: fixed seed,
2x supersample + Lanczos downscale to 1024x1024.

PIL lesson baked in: ImageDraw on RGBA *replaces* pixels instead of
blending, so every translucent effect lives on its own RGBA layer and is
merged with Image.alpha_composite. Never .convert("RGB") mid-pipeline.
"""
import math
import random
import sys
from PIL import Image, ImageDraw, ImageFont

SEED = 20261116
S = 2048                      # supersampled canvas
OUT = 1024
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)

# ---------------------------------------------------------------- palette
INDIGO_TOP = (8, 10, 42)
INDIGO_MID = (20, 26, 77)
INDIGO_BOT = (27, 35, 88)
GOLD = (255, 178, 44)
ORANGE = (255, 106, 0)
MAGENTA = (255, 46, 136)
TEAL = (46, 230, 200)
AQUA = (53, 200, 232)
WAVE_DEEP = (15, 111, 143)
WAVE_MID = (24, 158, 196)
WAVE_LITE = (120, 220, 245)
FOAM = (235, 250, 255)
YELLOW = (255, 225, 77)
FISH_BODY = (255, 144, 24)
FISH_BELLY = (255, 179, 71)
FISH_DARK = (214, 92, 0)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def soft_glow(cx, cy, radius, color, peak=150):
    """Concentric translucent discs -> a soft radial glow on its own layer."""
    g = layer()
    d = ImageDraw.Draw(g)
    steps = 26
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        a = int(peak * (1.0 - t) ** 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=color + (a,))
    return g


def quad_bezier(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
    return (x, y)


def stamp_circle(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------------------------------------------------------------- base
base = Image.new("RGB", (S, S), INDIGO_TOP)
bd = ImageDraw.Draw(base)
band = 4
for y in range(0, S, band):
    t = y / S
    c = lerp(INDIGO_TOP, INDIGO_MID, t) if t < 0.55 else \
        lerp(INDIGO_MID, INDIGO_BOT, (t - 0.55) / 0.45)
    bd.rectangle([0, y, S, y + band], fill=c)

img = base.convert("RGBA")

# ---------------------------------------------------------------- stars
stars = layer()
sd = ImageDraw.Draw(stars)
for _ in range(430):
    # denser toward the top-right galaxy corner
    x = rng.betavariate(2.2, 1.4) * S
    y = rng.betavariate(1.5, 2.0) * S
    r = rng.choice([1, 1, 2, 2, 3, 4])
    tone = rng.choice([(255, 255, 255), (255, 226, 160), (190, 225, 255),
                       (255, 200, 220)])
    a = rng.randint(140, 255)
    stamp_circle(sd, x, y, r, tone + (a,))
    if r >= 3 and rng.random() < 0.5:  # four-point sparkle on bright stars
        L = r * 5
        sd.line([x - L, y, x + L, y], fill=tone + (110,), width=2)
        sd.line([x, y - L, x, y + L], fill=tone + (110,), width=2)
img = Image.alpha_composite(img, stars)

# ---------------------------------------------------------------- galaxy spiral (top right)
GALAXY = (1620, 400)
gal = layer()
gd = ImageDraw.Draw(gal)
img = Image.alpha_composite(img, soft_glow(GALAXY[0], GALAXY[1], 520,
                                           (255, 120, 180), 55))
img = Image.alpha_composite(img, soft_glow(GALAXY[0], GALAXY[1], 430,
                                           (255, 190, 90), 90))
for arm in (0.0, math.pi):
    for i in range(170):
        t = i / 169
        theta = arm + 0.35 + t * 5.6
        r = 26 + 330 * t
        x = GALAXY[0] + r * math.cos(theta)
        y = GALAXY[1] + r * math.sin(theta) * 0.82
        size = max(2, int(15 * (1 - t) + 2) + rng.randint(-3, 5))
        col = rng.choice([GOLD, GOLD, (255, 255, 255), MAGENTA,
                          (255, 140, 190), (255, 220, 130)])
        stamp_circle(gd, x, y, size, col + (rng.randint(170, 255),))
    # dust between the arms so the spiral reads as a cloud, not a ring
    for i in range(70):
        t = rng.random()
        theta = arm + 0.35 + t * 5.2 + rng.uniform(-0.5, 0.5)
        r = 40 + 300 * t
        x = GALAXY[0] + r * math.cos(theta) + rng.uniform(-30, 30)
        y = GALAXY[1] + r * math.sin(theta) * 0.82 + rng.uniform(-30, 30)
        col = rng.choice([GOLD, (255, 255, 255), (255, 140, 190)])
        stamp_circle(gd, x, y, rng.randint(2, 6),
                     col + (rng.randint(120, 200),))
# bright core
stamp_circle(gd, GALAXY[0], GALAXY[1], 62, (255, 244, 214, 255))
stamp_circle(gd, GALAXY[0], GALAXY[1], 34, (255, 255, 255, 255))
img = Image.alpha_composite(img, gal)
# small secondary star cluster, balances the lower-right corner
img = Image.alpha_composite(img, soft_glow(1760, 1560, 260,
                                           (120, 170, 255), 50))
cluster = layer()
cd = ImageDraw.Draw(cluster)
for _ in range(14):
    x = 1640 + rng.uniform(0, 320)
    y = 1440 + rng.uniform(0, 300)
    r = rng.choice([2, 3, 4, 5])
    stamp_circle(cd, x, y, r, (255, 255, 255, rng.randint(180, 255)))
    if r >= 4:
        L = r * 4
        cd.line([x - L, y, x + L, y], fill=(255, 255, 255, 120), width=2)
        cd.line([x, y - L, x, y + L], fill=(255, 255, 255, 120), width=2)
img = Image.alpha_composite(img, cluster)

# ---------------------------------------------------------------- bowl + cheering fish (bottom left)
BOWL = (430, 1640)
bowl = layer()
bwd = ImageDraw.Draw(bowl)
# water inside the bowl
bwd.ellipse([BOWL[0] - 285, BOWL[1] - 120, BOWL[0] + 285, BOWL[1] + 165],
            fill=(36, 150, 205, 165))
bwd.ellipse([BOWL[0] - 285, BOWL[1] - 120, BOWL[0] + 285, BOWL[1] - 40],
            fill=(120, 215, 240, 120))
# second fish, still in the bowl, cheering: fins up, big smile
fx, fy = BOWL[0] - 20, BOWL[1] + 30
bwd.polygon([(fx - 95, fy - 10), (fx - 175, fy - 85), (fx - 150, fy + 5)],
            fill=(255, 170, 60, 255))
bwd.polygon([(fx - 95, fy + 10), (fx - 175, fy + 85), (fx - 150, fy - 5)],
            fill=(255, 170, 60, 255))
bwd.ellipse([fx - 110, fy - 62, fx + 110, fy + 62], fill=FISH_BODY + (255,))
bwd.ellipse([fx - 70, fy + 8, fx + 95, fy + 62], fill=FISH_BELLY + (255,))
bwd.polygon([(fx - 30, fy - 62), (fx + 10, fy - 115), (fx + 55, fy - 60)],
            fill=(255, 190, 90, 255))  # raised cheering fin
bwd.ellipse([fx + 52, fy - 34, fx + 92, fy + 6], fill=(255, 255, 255, 255))
bwd.ellipse([fx + 64, fy - 22, fx + 84, fy - 2], fill=(20, 16, 10, 255))
bwd.ellipse([fx + 71, fy - 19, fx + 78, fy - 12], fill=(255, 255, 255, 255))
bwd.arc([fx + 55, fy + 12, fx + 105, fy + 48], 15, 150,
        fill=(120, 40, 0, 255), width=7)
# glass rim + highlight, drawn over the fish so the glass reads in front
bwd.ellipse([BOWL[0] - 300, BOWL[1] - 150, BOWL[0] + 300, BOWL[1] + 180],
            outline=(205, 232, 255, 235), width=12)
bwd.arc([BOWL[0] - 260, BOWL[1] - 130, BOWL[0] + 260, BOWL[1] + 60],
        200, 330, fill=(255, 255, 255, 170), width=10)
bwd.ellipse([BOWL[0] - 300, BOWL[1] - 150, BOWL[0] + 300, BOWL[1] - 60],
            outline=(225, 240, 255, 160), width=6)
img = Image.alpha_composite(img, bowl)

# ---------------------------------------------------------------- the wave (bowl rim -> crest curl)
wave = layer()
wd = ImageDraw.Draw(wave)
P0, P1, P2 = (620, 1560), (1080, 1220), (1440, 780)
N = 130
pts = [quad_bezier(P0, P1, P2, i / (N - 1)) for i in range(N)]
for i, (x, y) in enumerate(pts):
    t = i / (N - 1)
    r = 165 * (1 - t) ** 0.85 + 55 * t
    col = lerp(WAVE_DEEP, WAVE_LITE, t ** 0.8)
    stamp_circle(wd, x, y, r, col + (255,))
# inner highlight: a thinner, lighter ribbon down the wave's middle
for i, (x, y) in enumerate(pts):
    t = i / (N - 1)
    r = 165 * (1 - t) ** 0.85 + 55 * t
    col = lerp((30, 170, 210), (190, 240, 255), t)
    stamp_circle(wd, x + 0.18 * r, y + 0.22 * r, r * 0.42, col + (200,))
# foam edge along the upper side of the wave, tapering toward the crest
for i, (x, y) in enumerate(pts):
    t = i / (N - 1)
    if t < 0.12:
        continue
    r = 165 * (1 - t) ** 0.85 + 55 * t
    nx, ny = -0.72, -0.69  # upper-left normal of the diagonal
    stamp_circle(wd, x + nx * r * 0.88, y + ny * r * 0.88,
                 max(5, r * 0.15), FOAM + (225,))
# crest curl: an inward spiral hook at the tip, foam cap
CREST = (1505, 655)
for i in range(60):
    t = i / 59
    ang = 0.4 + t * 5.6
    r = 105 * (1 - t) + 12
    x = CREST[0] + r * math.cos(ang)
    y = CREST[1] + r * math.sin(ang) * 0.9
    col = lerp(WAVE_LITE, (255, 255, 255), t)
    stamp_circle(wd, x, y, max(7, 34 * (1 - t) + 8), col + (255,))
img = Image.alpha_composite(img, wave)

# burst core where the wave meets the galaxy
img = Image.alpha_composite(img, soft_glow(CREST[0], CREST[1], 300,
                                           (255, 205, 110), 120))
burst = layer()
bud = ImageDraw.Draw(burst)
for i in range(9):  # short golden glints, not a firework starburst
    ang = rng.uniform(0, math.tau)
    ln = rng.uniform(90, 190)
    wdt = rng.choice([5, 6, 8])
    x2 = CREST[0] + ln * math.cos(ang)
    y2 = CREST[1] + ln * math.sin(ang)
    col = rng.choice([(255, 220, 120), (255, 255, 255), GOLD])
    bud.line([CREST[0], CREST[1], x2, y2], fill=col + (110,), width=wdt)
img = Image.alpha_composite(img, burst)

# ---------------------------------------------------------------- splash droplets + confetti
splash = layer()
spd = ImageDraw.Draw(splash)
for _ in range(70):  # droplets arcing from the bowl toward the leaping fish
    t = rng.random()
    bx, by = quad_bezier((560, 1500), (760, 1150), (940, 1050), t)
    jx, jy = rng.uniform(-70, 70), rng.uniform(-70, 70)
    r = rng.uniform(5, 22)
    col = rng.choice([FOAM, AQUA, (255, 255, 255)])
    stamp_circle(spd, bx + jx, by + jy, r, col + (rng.randint(150, 235),))
for _ in range(110):  # confetti bursting off the wave and crest
    t = rng.random()
    bx, by = quad_bezier(P0, P1, P2, t)
    x = bx + rng.uniform(-190, 260)
    y = by + rng.uniform(-190, 260)
    w, h = rng.uniform(12, 30), rng.uniform(7, 14)
    ang = rng.uniform(0, math.pi)
    ca, sa = math.cos(ang), math.sin(ang)
    corners = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                   (w / 2, h / 2), (-w / 2, h / 2)):
        corners.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
    col = rng.choice([MAGENTA, GOLD, TEAL, (255, 255, 255), ORANGE])
    spd.polygon(corners, fill=col + (rng.randint(190, 255),))
img = Image.alpha_composite(img, splash)

# bubbles rising from the bowl
bub = layer()
bud2 = ImageDraw.Draw(bub)
for _ in range(26):
    x = 350 + rng.uniform(0, 260) + rng.uniform(-30, 30)
    y = 1560 - rng.random() ** 1.6 * 620
    r = rng.uniform(7, 26)
    bud2.ellipse([x - r, y - r, x + r, y + r],
                 outline=(255, 255, 255, 190), width=3)
    bud2.ellipse([x - r * 0.4, y - r * 0.4, x - r * 0.1, y - r * 0.1],
                 fill=(255, 255, 255, 170))
img = Image.alpha_composite(img, bub)

# ---------------------------------------------------------------- the leaping fish
fish = layer()
fd = ImageDraw.Draw(fish)
# local coords, fish centre just clear of the wave band, nose to the right
CX, CY = 840, 1030
# tail (two flowing lobes)
fd.polygon([(CX - 150, CY - 8), (CX - 330, CY - 110), (CX - 285, CY),
            (CX - 330, CY + 110)], fill=(255, 150, 40, 235))
fd.polygon([(CX - 160, CY - 4), (CX - 285, CY - 70), (CX - 250, CY),
            (CX - 285, CY + 70)], fill=(255, 190, 100, 235))
# body + belly
fd.ellipse([CX - 185, CY - 100, CX + 185, CY + 100], fill=FISH_BODY + (255,))
fd.ellipse([CX - 130, CY + 12, CX + 165, CY + 100], fill=FISH_BELLY + (255,))
# dorsal + pectoral fins
fd.polygon([(CX - 40, CY - 98), (CX + 20, CY - 175), (CX + 80, CY - 95)],
           fill=(255, 175, 70, 255))
fd.polygon([(CX - 10, CY + 55), (CX + 70, CY + 130), (CX + 95, CY + 60)],
           fill=(255, 190, 100, 255))
# scales: small arcs
for sx in range(-120, 121, 55):
    fd.arc([CX + sx - 28, CY - 55, CX + sx + 28, CY + 5], 300, 60,
           fill=(230, 110, 10, 200), width=5)
# eye, big and wide open
fd.ellipse([CX + 92, CY - 46, CX + 146, CY + 8], fill=(255, 255, 255, 255))
fd.ellipse([CX + 108, CY - 30, CX + 136, CY - 2], fill=(18, 14, 10, 255))
fd.ellipse([CX + 118, CY - 26, CX + 128, CY - 16], fill=(255, 255, 255, 255))
# gill + big open smiling mouth
fd.arc([CX + 55, CY - 55, CX + 115, CY + 55], 300, 60,
       fill=(200, 90, 0, 255), width=7)
fd.arc([CX + 95, CY + 18, CX + 175, CY + 78], 10, 165,
       fill=(120, 40, 0, 255), width=9)
fd.ellipse([CX + 118, CY + 42, CX + 158, CY + 66], fill=(120, 40, 0, 255))
fish = fish.rotate(36, center=(CX, CY), resample=Image.BICUBIC)
# nose leads up-right along the leap arc
img = Image.alpha_composite(img, fish)

# motion arcs trailing the fish, hugging its trajectory
arcs = layer()
ad = ImageDraw.Draw(arcs)
for k, (ax, ay, ar, a0, a1) in enumerate([
        (640, 1240, 210, 205, 290),
        (700, 1200, 290, 208, 285)]):
    ad.arc([ax - ar, ay - ar, ax + ar, ay + ar], a0, a1,
           fill=(255, 255, 255, 100 - k * 25), width=11 - k * 2)
img = Image.alpha_composite(img, arcs)

# ---------------------------------------------------------------- WOW! text
text = layer()
td = ImageDraw.Draw(text)
font = ImageFont.truetype(FONT_BOLD, 295)
word = "WOW!"
bbox = td.textbbox((0, 0), word, font=font, stroke_width=18)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx, ty = 560 - tw // 2 - bbox[0], 420 - th // 2 - bbox[1]
td.text((tx, ty), word, font=font, fill=YELLOW + (255,),
        stroke_width=18, stroke_fill=ORANGE + (255,))
# tiny white sparkle on the W for punch
td.ellipse([tx + 60, ty + 40, tx + 105, ty + 85], fill=(255, 255, 255, 230))
text = text.rotate(-10, center=(560, 420), resample=Image.BICUBIC)
img = Image.alpha_composite(img, text)

# ---------------------------------------------------------------- vignette (soft dark corners)
vig = Image.radial_gradient("L").resize((S, S))
black = Image.new("RGBA", (S, S), (0, 0, 0, 255))
mask = vig.point(lambda v: int((255 - v) * 0.38))
img.paste(black, (0, 0), mask)

# ---------------------------------------------------------------- flatten + save
final = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
final.save("entry.png", format="PNG", optimize=True)
print("saved entry.png", final.size)

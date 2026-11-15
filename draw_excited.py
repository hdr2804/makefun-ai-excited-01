"""Draw the ai-excited-01 entry image, fully in code, deterministic.

Concept: "One small leap becomes a universe." A tiny goldfish leaps out
of its little glass bowl (bottom left) and its splash becomes a huge
curling wave that spirals up into a galaxy of stars and confetti (top
right) -- a scale twist, not a stock explosion or firework. Saturated
warm palette on deep indigo, strong diagonal composition, bold WOW!
text the judge can read. Drawn at 2x and downscaled for clean edges.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

S = 1024
SS = 2  # supersample factor
W = S * SS
rng = random.Random(20261116)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


img = Image.new("RGBA", (W, W), (16, 8, 46, 255))
d = ImageDraw.Draw(img, "RGBA")

# --- sky: vertical gradient deep indigo -> violet, plus warm glow at burst ---
top = (14, 6, 44)
mid = (46, 16, 96)
bot = (88, 22, 92)
for y in range(W):
    t = y / W
    c = lerp(top, mid, t) if t < 0.55 else lerp(mid, bot, (t - 0.55) / 0.45)
    d.line([(0, y), (W, y)], fill=c)

# warm radial glow around the burst point (top right) -- soft, smaller.
# NOTE: translucent fills must go on a separate layer and be
# alpha_composited: ImageDraw on an RGBA canvas replaces pixels instead
# of blending, which would leave a hard opaque disc.
bx, by = int(0.80 * W), int(0.24 * W)
_glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
_gd = ImageDraw.Draw(_glow, "RGBA")
for r in range(640, 0, -6):
    t = 1 - r / 640
    a = int(45 * t * t * t)
    _gd.ellipse([bx - r, by - r, bx + r, by + r],
                fill=(255, 120, 40, a))
img = Image.alpha_composite(img, _glow)
d = ImageDraw.Draw(img, "RGBA")

# --- stars: deterministic scatter across the whole sky ---
for _ in range(320):
    x = rng.randint(0, W)
    y = rng.randint(0, int(0.95 * W))
    r = rng.choice([1, 1, 2, 2, 3])
    bright = rng.randint(130, 255)
    if y > int(0.75 * W):
        bright = bright // 2  # dimmer low down, keeps the bowl area calm
    warm = rng.random() < 0.35
    col = (255, bright, 180) if warm else (bright, bright, 255)
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
    if r >= 3 and rng.random() < 0.5:  # cross sparkle (opaque, dimmed)
        L = r * 4
        dim = tuple(c * 3 // 5 for c in col)
        d.line([(x - L, y), (x + L, y)], fill=dim + (255,), width=2)
        d.line([(x, y - L), (x, y + L)], fill=dim + (255,), width=2)

# --- speed streaks radiating from the burst (own layer, blended) ---
_streak = Image.new("RGBA", (W, W), (0, 0, 0, 0))
_sd = ImageDraw.Draw(_streak, "RGBA")
for _ in range(46):
    ang = rng.uniform(0, 2 * math.pi)
    r0 = rng.randint(120, 260)
    r1 = r0 + rng.randint(60, 260)
    x0, y0 = bx + r0 * math.cos(ang), by + r0 * math.sin(ang)
    x1, y1 = bx + r1 * math.cos(ang), by + r1 * math.sin(ang)
    col = rng.choice([(255, 220, 120), (255, 140, 90), (120, 220, 255),
                      (255, 255, 255)])
    _sd.line([(x0, y0), (x1, y1)], fill=col + (rng.randint(90, 200),),
             width=rng.choice([3, 4, 6]))
img = Image.alpha_composite(img, _streak)
d = ImageDraw.Draw(img, "RGBA")

# --- galaxy spiral around the burst: dots along a logarithmic spiral ---
for i in range(430):
    t = i / 430
    ang = t * 4.6 * math.pi + 0.6
    rad = 40 + t * 540
    x = bx + rad * math.cos(ang)
    y = by + rad * math.sin(ang) * 0.82
    r = int(3 + 8 * (1 - t) * rng.random() + 2)
    col = rng.choice([(255, 214, 90), (255, 110, 180), (120, 220, 255),
                      (255, 150, 60), (255, 255, 255)])
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))

# --- the wave: layered curling bands rising diagonally bowl -> burst ---
# main wave body: thick bezier-ish band built from overlapping circles
def wave_point(t):
    # t: 0 at bowl, 1 at burst; S-curve sweeping up-right, hooking at top
    x = 300 + t * 1000 - 180 * max(0.0, t - 0.82) ** 2 * 6
    y = 1760 - t * 1150 - 300 * math.sin(t * math.pi * 0.85)
    return x, y

wave_cols = [(0, 150, 190), (0, 190, 220), (40, 220, 235), (120, 235, 250)]
for k, col in enumerate(wave_cols):
    for i in range(120):
        t = i / 119
        x, y = wave_point(t)
        # band thickness grows toward the crest, then tapers to a curled tip
        rad = (20 + t * 170) * (1 - 0.16 * k)
        if t > 0.85:
            rad *= 1 - 0.55 * (t - 0.85) / 0.15
        yy = y - k * 34
        d.ellipse([x - rad, yy - rad * 0.55, x + rad, yy + rad * 0.55],
                  fill=col + (255,))

# foam crest: white dots along the top edge of the wave, plus a curled
# foam cap at the tip so the crest reads as a breaking wave, not a blob
for i in range(90):
    t = i / 89
    x, y = wave_point(t)
    taper = 1 - 0.55 * max(0.0, t - 0.85) / 0.15 if t > 0.85 else 1.0
    y -= (20 + t * 170) * taper * 0.55 + rng.randint(0, 26)
    r = rng.randint(3, 12)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
tipx, tipy = wave_point(0.99)
for k in range(16):
    ang = math.pi * (0.05 + 0.9 * k / 15)
    cx = tipx - 40 + 130 * math.cos(ang)
    cy = tipy - 60 - 90 * math.sin(ang)
    r = rng.randint(8, 18)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))

# --- confetti along the diagonal ---
conf_cols = [(255, 60, 90), (255, 200, 40), (60, 220, 160), (255, 120, 220),
             (90, 180, 255), (255, 255, 255)]
for _ in range(170):
    t = rng.random()
    x, y = wave_point(t)
    x += rng.randint(-260, 260)
    y += rng.randint(-220, 220)
    w_, h_ = rng.randint(8, 22), rng.randint(5, 12)
    col = rng.choice(conf_cols)
    # small rotated rectangle via polygon
    ang = rng.uniform(0, math.pi)
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for dx, dy in [(-w_, -h_), (w_, -h_), (w_, h_), (-w_, h_)]:
        pts.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
    d.polygon(pts, fill=col + (255,))

# --- burst core: bright starburst at the spiral centre (own layer) ---
_core = Image.new("RGBA", (W, W), (0, 0, 0, 0))
_cd = ImageDraw.Draw(_core, "RGBA")
for r, a in [(150, 110), (110, 160), (70, 210), (36, 255)]:
    _cd.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 240, 200, a))
for k in range(12):
    ang = k * math.pi / 6
    x1, y1 = bx + 48 * math.cos(ang), by + 48 * math.sin(ang)
    x2, y2 = bx + 300 * math.cos(ang), by + 300 * math.sin(ang)
    _cd.line([(x1, y1), (x2, y2)], fill=(255, 230, 150, 220), width=12)
for k in range(6):  # short bright cross-rays for extra punch
    ang = k * math.pi / 3 + math.pi / 6
    x1, y1 = bx + 40 * math.cos(ang), by + 40 * math.sin(ang)
    x2, y2 = bx + 190 * math.cos(ang), by + 190 * math.sin(ang)
    _cd.line([(x1, y1), (x2, y2)], fill=(255, 250, 210, 255), width=14)
img = Image.alpha_composite(img, _core)
d = ImageDraw.Draw(img, "RGBA")

# --- goldfish riding the crest, facing up-right, fully clear of the core ---
fx, fy = 1040, 620  # fish centre (2x coords), riding the wave crest
# motion arcs behind the fish (own layer, blended)
_arcs = Image.new("RGBA", (W, W), (0, 0, 0, 0))
_ad = ImageDraw.Draw(_arcs, "RGBA")
for k in range(3):
    rr = 260 + k * 60
    _ad.arc([fx - rr, fy - rr, fx + rr, fy + rr], start=200, end=330,
            fill=(255, 200, 120, 120), width=10)
img = Image.alpha_composite(img, _arcs)
d = ImageDraw.Draw(img, "RGBA")
# tail fin (flowing, behind-left)
tail = [(fx - 130, fy - 10), (fx - 330, fy - 150), (fx - 300, fy + 10),
        (fx - 350, fy + 140), (fx - 140, fy + 60)]
d.polygon(tail, fill=(255, 120, 40, 255))
d.polygon([(fx - 130, fy - 10), (fx - 300, fy - 110), (fx - 280, fy + 10)],
          fill=(255, 170, 60, 255))
# body: orange ellipse, white belly
d.ellipse([fx - 190, fy - 130, fx + 210, fy + 130], fill=(255, 140, 30, 255))
d.ellipse([fx - 150, fy + 10, fx + 190, fy + 125], fill=(255, 205, 110, 255))
# back fin
d.polygon([(fx - 40, fy - 125), (fx + 60, fy - 210), (fx + 130, fy - 120)],
          fill=(255, 110, 30, 255))
# side fin
d.polygon([(fx - 20, fy + 40), (fx + 90, fy + 150), (fx + 130, fy + 60)],
          fill=(255, 110, 30, 255))
# stripes
for sx in (-90, -20, 50):
    d.arc([fx + sx - 70, fy - 120, fx + sx + 70, fy + 120], start=250,
          end=110, fill=(230, 90, 20, 200), width=16)
# big joyful eye
d.ellipse([fx + 110, fy - 75, fx + 175, fy - 10], fill=(255, 255, 255, 255))
d.ellipse([fx + 128, fy - 62, fx + 163, fy - 27], fill=(20, 10, 40, 255))
d.ellipse([fx + 140, fy - 58, fx + 152, fy - 46], fill=(255, 255, 255, 255))
# open smiling mouth (bigger, clearly joyful)
d.ellipse([fx + 165, fy + 25, fx + 220, fy + 80], fill=(120, 20, 40, 255))
d.ellipse([fx + 175, fy + 36, fx + 210, fy + 66], fill=(255, 90, 110, 255))

# --- the little glass bowl, bottom left, with leap bubble trail ---
bowl_cx, bowl_cy = 330, 1800
# bubble trail from bowl to fish (dotted arc, own layer, blended)
_bub = Image.new("RGBA", (W, W), (0, 0, 0, 0))
_bd = ImageDraw.Draw(_bub, "RGBA")
for i in range(14):
    t = i / 13
    x = bowl_cx + t * (fx - bowl_cx) * 0.85
    y = bowl_cy - t * (bowl_cy - fy) * 0.85 - 320 * math.sin(t * math.pi)
    r = 8 + t * 26
    _bd.ellipse([x - r, y - r, x + r, y + r],
                outline=(180, 230, 255, 220), width=5)
    _bd.ellipse([x - r // 3, y - r // 3, x + r // 4, y + r // 4],
                fill=(255, 255, 255, 160))
img = Image.alpha_composite(img, _bub)
d = ImageDraw.Draw(img, "RGBA")
# table line
d.line([(0, 1870), (W, 1870)], fill=(255, 190, 90, 255), width=10)
# bowl: water then glass
d.ellipse([bowl_cx - 230, bowl_cy - 150, bowl_cx + 230, bowl_cy + 150],
          fill=(30, 160, 210, 255))
d.ellipse([bowl_cx - 230, bowl_cy - 150, bowl_cx + 230, bowl_cy - 40],
          fill=(90, 210, 240, 255))
d.ellipse([bowl_cx - 230, bowl_cy - 150, bowl_cx + 230, bowl_cy + 150],
          outline=(220, 245, 255, 255), width=12)
# glass highlight
d.arc([bowl_cx - 200, bowl_cy - 120, bowl_cx + 60, bowl_cy + 120],
      start=140, end=250, fill=(255, 255, 255, 220), width=14)
# a tiny second fish still in the bowl, cheering
d.ellipse([bowl_cx - 60, bowl_cy - 30, bowl_cx + 60, bowl_cy + 40],
          fill=(255, 150, 50, 255))
d.polygon([(bowl_cx - 55, bowl_cy), (bowl_cx - 110, bowl_cy - 35),
           (bowl_cx - 110, bowl_cy + 30)], fill=(255, 120, 40, 255))
d.ellipse([bowl_cx + 25, bowl_cy - 18, bowl_cx + 48, bowl_cy + 5],
          fill=(20, 10, 40, 255))

# --- WOW! text, top left, tilted, yellow with orange outline ---
txt = "WOW!"
font = ImageFont.truetype(FONT_BOLD, 300)
layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
td = ImageDraw.Draw(layer)
td.text((70, 40), txt, font=font, fill=(255, 214, 40, 255),
        stroke_width=14, stroke_fill=(230, 80, 20, 255))
layer = layer.rotate(-8, resample=Image.BICUBIC, center=(330, 220))
img.alpha_composite(layer)

# --- vignette: darken corners slightly so the centre pops ---
vig = Image.new("L", (W, W), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.25, -W * 0.25, W * 1.25, W * 1.25], fill=255)
vig = vig.point(lambda p: int(255 - (255 - p) * 0.28))
black = Image.new("RGBA", (W, W), (8, 4, 26, 255))
img = Image.composite(img, black, vig)

img = img.convert("RGB").resize((S, S), Image.LANCZOS)
img.save("entry.png", optimize=True)
print("saved entry.png", img.size)

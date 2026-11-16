#!/usr/bin/env python3
"""Draw the ai-excited-01 entry: 'One small leap becomes a universe'.

A goldfish leaps from its bowl (bottom-left); its splash becomes a curling
wave that spirals up into a dense galaxy of stars and confetti (top-right).
Saturated orange/magenta on deep indigo, bold tilted yellow WOW! text.

Deterministic: fixed seed, 2x supersample, Lanczos downscale to 1024x1024.
Usage: python3 draw_excited.py <output-png-path>
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
SS = 2                      # supersample factor
W = 1024 * SS               # working canvas
FINAL = 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else "entry.png"

rng = random.Random(SEED)

# ---------------------------------------------------------------- palette
INDIGO_DEEP = (10, 8, 38)
INDIGO_MID = (26, 18, 72)
VIOLET_GLOW = (74, 38, 130)
MAGENTA = (235, 40, 150)
ORANGE = (255, 122, 26)
GOLD = (255, 176, 32)
YELLOW = (255, 214, 0)
CYAN = (80, 220, 255)
ICE = (190, 235, 255)
WHITE = (255, 255, 255)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def layer():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def soft_disc(draw, cx, cy, r, color, alpha):
    """A radial-gradient disc (bright core fading to transparent)."""
    d = int(r * 2)
    tmp = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    steps = 24
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        a = int(alpha * (1 - t) ** 2)
        td.ellipse([r - rr, r - rr, r + rr, r + rr],
                   fill=color + (a,))
    tmp = tmp.filter(ImageFilter.GaussianBlur(r / 6))
    draw._image.alpha_composite(tmp, (int(cx - r), int(cy - r)))


# ================================================================ canvas
base = Image.new("RGBA", (W, W), INDIGO_DEEP + (255,))
bd = ImageDraw.Draw(base)

# vertical+radial indigo gradient: lighter toward the galaxy (top-right)
gx, gy = 0.78 * W, 0.22 * W
grad = Image.new("RGBA", (W, W))
gd = ImageDraw.Draw(grad)
for y in range(0, W, 8):
    for x in range(0, W, 8):
        d = math.hypot(x - gx, y - gy) / (W * 0.95)
        t = max(0.0, min(1.0, d))
        c = lerp(VIOLET_GLOW, INDIGO_DEEP, t ** 1.4)
        gd.rectangle([x, y, x + 8, y + 8], fill=c + (255,))
grad = grad.filter(ImageFilter.GaussianBlur(18))
base.alpha_composite(grad)

# faint magenta / orange nebula clouds near the galaxy
neb = layer()
nd = ImageDraw.Draw(neb)
for (cx, cy, r, col, a) in [
        (0.80 * W, 0.20 * W, 0.30 * W, (200, 40, 140), 46),
        (0.66 * W, 0.30 * W, 0.22 * W, (120, 40, 200), 40),
        (0.88 * W, 0.38 * W, 0.20 * W, (255, 110, 40), 34),
        (0.55 * W, 0.12 * W, 0.18 * W, (60, 60, 220), 30)]:
    soft_disc(nd, cx, cy, r, col, a)
neb = neb.filter(ImageFilter.GaussianBlur(60))
base.alpha_composite(neb)

# sparse background stars over the whole sky
sky = layer()
sd = ImageDraw.Draw(sky)
for _ in range(260):
    x = rng.uniform(0, W)
    y = rng.uniform(0, W)
    r = rng.uniform(0.8, 2.6) * SS
    a = rng.randint(60, 200)
    col = rng.choice([WHITE, ICE, (255, 230, 170)])
    sd.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
base.alpha_composite(sky)

# ================================================================ burst rays (soft, <=9)
rays = layer()
rd = ImageDraw.Draw(rays)
cxg, cyg = 0.79 * W, 0.21 * W
for i in range(7):
    ang = math.radians(-160 + i * 26 + rng.uniform(-6, 6))
    length = rng.uniform(0.30, 0.46) * W
    spread = math.radians(rng.uniform(4, 7))
    x2 = cxg + math.cos(ang) * length
    y2 = cyg + math.sin(ang) * length
    px = math.cos(ang + math.pi / 2) * length * math.tan(spread)
    py = math.sin(ang + math.pi / 2) * length * math.tan(spread)
    rd.polygon([(cxg, cyg), (x2 + px, y2 + py), (x2 - px, y2 - py)],
               fill=(255, 220, 130, 26))
rays = rays.filter(ImageFilter.GaussianBlur(14))
base.alpha_composite(rays)

# ================================================================ galaxy
# Dense spiral: 3 arms, many stars per arm + dust motes, core glow.
gal = layer()
gd2 = ImageDraw.Draw(gal)
core_r = 0.055 * W
soft_disc(gd2, cxg, cyg, 0.16 * W, (255, 240, 200), 150)
soft_disc(gd2, cxg, cyg, 0.09 * W, WHITE, 200)
for arm in range(3):
    base_ang = arm * (2 * math.pi / 3) + 0.35
    for k in range(240):
        t = (k / 240) ** 0.8
        ang = base_ang + t * 3.4
        rad = 0.02 * W + t * 0.235 * W
        jx = rng.gauss(0, 0.012 * W * (0.4 + t))
        jy = rng.gauss(0, 0.012 * W * (0.4 + t))
        x = cxg + math.cos(ang) * rad + jx
        y = cyg + math.sin(ang) * rad * 0.82 + jy
        r = rng.uniform(1.0, 3.4) * SS * (1.15 - 0.55 * t)
        col = rng.choice([WHITE, WHITE, GOLD, (255, 200, 220),
                          ICE, (255, 170, 90)])
        a = rng.randint(150, 255)
        gd2.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
        if rng.random() < 0.10:  # sparkle cross on a few bright stars
            s = r * 2.6
            gd2.line([x - s, y, x + s, y], fill=col + (120,), width=1)
            gd2.line([x, y - s, x, y + s], fill=col + (120,), width=1)
# dust motes filling the disc between arms
for _ in range(420):
    ang = rng.uniform(0, 2 * math.pi)
    rad = rng.uniform(0, 0.26 * W) * math.sqrt(rng.random())
    x = cxg + math.cos(ang) * rad
    y = cyg + math.sin(ang) * rad * 0.82
    r = rng.uniform(0.6, 1.8) * SS
    col = rng.choice([(255, 190, 220), (255, 220, 160), ICE, WHITE])
    gd2.ellipse([x - r, y - r, x + r, y + r],
                fill=col + (rng.randint(70, 170),))
gal = gal.filter(ImageFilter.GaussianBlur(1.2))
base.alpha_composite(gal)

# ================================================================ wave
# A curling band: a sweeping Bezier from the bowl up toward the galaxy,
# ending in a small spiral curl around the galaxy's edge.
wave = layer()
wd = ImageDraw.Draw(wave)


def bezier(t, p0, p1, p2, p3):
    mt = 1 - t
    x = (mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0]
         + t**3 * p3[0])
    y = (mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1]
         + t**3 * p3[1])
    return x, y


pts = [bezier(t / 110, (0.30 * W, 0.80 * W), (0.44 * W, 0.60 * W),
              (0.60 * W, 0.56 * W), (0.72 * W, 0.40 * W))
       for t in range(111)]
# tip curls around the galaxy core
for k in range(41):
    t = k / 40
    ang = math.radians(105 - 160 * t)
    rad = (0.095 - 0.04 * t) * W
    pts.append((cxg + math.cos(ang) * rad, cyg + math.sin(ang) * rad))


def left_normal(pts, i):
    x0, y0 = pts[max(0, i - 1)]
    x1, y1 = pts[min(len(pts) - 1, i + 1)]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    return -dy / n, dx / n  # left of travel direction


# main band: tapered, deep cyan-blue with a bright crest
for i in range(len(pts) - 1):
    t = i / (len(pts) - 1)
    wdt = (24 - 19 * t) * SS
    col = lerp((16, 110, 190), (90, 200, 255), t)
    wd.line([pts[i], pts[i + 1]], fill=col + (235,), width=int(wdt))
# inner highlight ribbon, offset toward the inside of the curl
inner = []
for i in range(len(pts)):
    t = i / (len(pts) - 1)
    nx, ny = left_normal(pts, i)
    off = (6 - 3.5 * t) * SS
    inner.append((pts[i][0] + nx * off, pts[i][1] + ny * off))
for i in range(len(inner) - 1):
    t = i / (len(inner) - 1)
    wdt = max(2, int((6 - 4 * t) * SS))
    wd.line([inner[i], inner[i + 1]], fill=(220, 245, 255, 220), width=wdt)
# foam: tapering white bubbles along the outer crest, shrinking to the tip
for i in range(0, len(pts), 2):
    t = i / (len(pts) - 1)
    nx, ny = left_normal(pts, i)
    off = (13 - 9 * t) * SS
    fx, fy = pts[i][0] - nx * off, pts[i][1] - ny * off
    r = (5.5 - 4.5 * t) * SS * rng.uniform(0.7, 1.25)
    wd.ellipse([fx - r, fy - r, fx + r, fy + r],
               fill=(235, 250, 255, rng.randint(150, 220)))
# spray droplets flying off the crest near the bowl end
for _ in range(46):
    t = rng.uniform(0, 0.45)
    x, y = pts[int(t * (len(pts) - 1))]
    x += rng.gauss(0, 26 * SS)
    y += rng.gauss(0, 26 * SS) - 14 * SS
    r = rng.uniform(1.5, 4.5) * SS
    wd.ellipse([x - r, y - r, x + r, y + r],
               fill=(200, 235, 255, rng.randint(120, 220)))
wave = wave.filter(ImageFilter.GaussianBlur(1.6))
base.alpha_composite(wave)

# ================================================================ confetti
conf = layer()
cd = ImageDraw.Draw(conf)
for _ in range(90):
    # cluster around the galaxy + along the wave, a few drifting elsewhere
    pick = rng.random()
    if pick < 0.55:
        x = cxg + rng.gauss(0, 0.20 * W)
        y = cyg + rng.gauss(0, 0.16 * W)
    elif pick < 0.85:
        t = rng.uniform(0.15, 0.95)
        x, y = pts[int(t * (len(pts) - 1))]
        x += rng.gauss(0, 34 * SS)
        y += rng.gauss(0, 34 * SS)
    else:
        x = rng.uniform(0.05 * W, 0.95 * W)
        y = rng.uniform(0.05 * W, 0.75 * W)
    s = rng.uniform(3, 8) * SS
    col = rng.choice([ORANGE, MAGENTA, YELLOW, CYAN, (140, 255, 170), WHITE])
    shape = rng.random()
    if shape < 0.45:  # rotated rectangle
        tmp = Image.new("RGBA", (int(s * 2), int(s * 2)), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).rectangle(
            [s * 0.4, s * 0.75, s * 1.6, s * 1.25], fill=col + (235,))
        tmp = tmp.rotate(rng.uniform(0, 360), resample=Image.BICUBIC,
                         expand=False)
        conf.alpha_composite(tmp, (int(x - s), int(y - s)))
    elif shape < 0.75:  # dot
        cd.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2],
                   fill=col + (235,))
    else:  # tiny triangle
        cd.polygon([(x, y - s), (x - s, y + s * 0.7), (x + s, y + s * 0.7)],
                   fill=col + (235,))
base.alpha_composite(conf)

# ================================================================ bowl (bottom-left)
bowl = layer()
bd2 = ImageDraw.Draw(bowl)
bcx, bcy = 0.225 * W, 0.875 * W     # bowl centre (waterline height)
bw, bh = 0.165 * W, 0.105 * W      # bowl half-width / body depth
# table shadow under the bowl
bd2.ellipse([bcx - bw * 1.02, bcy + bh * 0.88, bcx + bw * 1.02,
             bcy + bh * 1.12], fill=(0, 0, 0, 110))
# glass body: straight walls + rounded bottom (bottom half of an ellipse)
bd2.rectangle([bcx - bw, bcy - bh * 0.30, bcx + bw, bcy + 2],
              fill=(30, 140, 220, 200))
bd2.pieslice([bcx - bw, bcy - bh, bcx + bw, bcy + bh],
             0, 180, fill=(30, 140, 220, 200))
# water surface
bd2.ellipse([bcx - bw, bcy - bh * 0.52, bcx + bw, bcy - bh * 0.08],
            fill=(120, 210, 255, 220))
# glass rim + highlight
bd2.arc([bcx - bw, bcy - bh * 0.52, bcx + bw, bcy - bh * 0.08],
        180, 360, fill=(230, 245, 255, 230), width=int(4 * SS))
bd2.arc([bcx - bw * 0.88, bcy - bh * 0.25, bcx - bw * 0.28, bcy + bh * 0.85],
        110, 250, fill=(255, 255, 255, 160), width=int(5 * SS))

# second fish inside the bowl, cheering: upright, fins raised, mouth open
fish2 = layer()
f2 = ImageDraw.Draw(fish2)
fx2, fy2 = bcx + 0.02 * W, bcy + 0.02 * W
# body (small, tilted nose-up)
body = [(fx2 - 46 * SS, fy2 + 6 * SS), (fx2 - 18 * SS, fy2 - 26 * SS),
        (fx2 + 26 * SS, fy2 - 30 * SS), (fx2 + 52 * SS, fy2 - 8 * SS),
        (fx2 + 30 * SS, fy2 + 16 * SS), (fx2 - 10 * SS, fy2 + 26 * SS)]
f2.polygon(body, fill=(255, 150, 40, 255))
f2.polygon([(fx2 + 44 * SS, fy2 - 14 * SS), (fx2 + 78 * SS, fy2 - 34 * SS),
            (fx2 + 72 * SS, fy2 + 2 * SS)], fill=(255, 110, 60, 235))  # tail
# raised cheering fins
f2.polygon([(fx2 - 8 * SS, fy2 - 24 * SS), (fx2 - 26 * SS, fy2 - 62 * SS),
            (fx2 + 2 * SS, fy2 - 44 * SS)], fill=(255, 90, 90, 240))
f2.polygon([(fx2 + 8 * SS, fy2 - 26 * SS), (fx2 + 30 * SS, fy2 - 58 * SS),
            (fx2 + 34 * SS, fy2 - 28 * SS)], fill=(255, 90, 90, 240))
# eye + open mouth
f2.ellipse([fx2 + 34 * SS, fy2 - 26 * SS, fx2 + 46 * SS, fy2 - 14 * SS],
           fill=(255, 255, 255, 255))
f2.ellipse([fx2 + 38 * SS, fy2 - 23 * SS, fx2 + 44 * SS, fy2 - 17 * SS],
           fill=(10, 10, 20, 255))
f2.ellipse([fx2 + 50 * SS, fy2 - 12 * SS, fx2 + 58 * SS, fy2 - 2 * SS],
           fill=(120, 20, 20, 255))
# bubbles rising from the cheering fish
for k in range(5):
    bx = fx2 + 30 * SS + k * 12 * SS
    by = fy2 - 44 * SS - k * 16 * SS
    r = (4 + k) * SS
    f2.ellipse([bx - r, by - r, bx + r, by + r],
               outline=(190, 235, 255, 200), width=2)
bowl.alpha_composite(fish2)
bowl = bowl.filter(ImageFilter.GaussianBlur(0.8))
base.alpha_composite(bowl)

# ================================================================ leaping goldfish
# Drawn on its own layer, rotated nose-up-right, lifted clear of the wave band.
fish = Image.new("RGBA", (int(0.62 * W), int(0.42 * W)), (0, 0, 0, 0))
fd = ImageDraw.Draw(fish)
FW, FH = fish.size
ox, oy = FW * 0.50, FH * 0.52   # fish centre in its layer
L = 0.24 * W                    # body length
# flowing tail (behind body)
fd.polygon([(ox - L * 0.42, oy - 6 * SS), (ox - L * 0.95, oy - 62 * SS),
            (ox - L * 0.78, oy - 4 * SS), (ox - L * 0.98, oy + 48 * SS),
            (ox - L * 0.42, oy + 10 * SS)],
           fill=(255, 90, 90, 225))
fd.polygon([(ox - L * 0.42, oy - 4 * SS), (ox - L * 0.80, oy - 30 * SS),
            (ox - L * 0.70, oy + 26 * SS)],
           fill=(255, 140, 60, 200))
# body: solid two-tone ellipse, orange back over a gold belly
fd.ellipse([ox - L * 0.5, oy - 30 * SS, ox + L * 0.5, oy + 30 * SS],
           fill=(255, 140, 40, 255))
fd.ellipse([ox - L * 0.42, oy + 2 * SS, ox + L * 0.44, oy + 30 * SS],
           fill=(255, 200, 90, 255))
fd.ellipse([ox - L * 0.5, oy - 30 * SS, ox + L * 0.5, oy + 30 * SS],
           outline=(220, 70, 10, 255), width=int(3 * SS))
# dorsal + pectoral fins
fd.polygon([(ox - L * 0.05, oy - 28 * SS), (ox + L * 0.12, oy - 66 * SS),
            (ox + L * 0.22, oy - 26 * SS)], fill=(255, 120, 50, 240))
fd.polygon([(ox + L * 0.05, oy + 18 * SS), (ox + L * 0.22, oy + 52 * SS),
            (ox + L * 0.28, oy + 16 * SS)], fill=(255, 150, 70, 230))
# gill + eye (nose at +x end)
fd.arc([ox + L * 0.18, oy - 24 * SS, ox + L * 0.38, oy + 24 * SS],
       300, 60, fill=(200, 60, 10, 220), width=int(3 * SS))
fd.ellipse([ox + L * 0.30, oy - 20 * SS, ox + L * 0.42, oy - 8 * SS],
           fill=(255, 255, 255, 255))
fd.ellipse([ox + L * 0.335, oy - 17 * SS, ox + L * 0.405, oy - 11 * SS],
           fill=(12, 12, 24, 255))
fd.ellipse([ox + L * 0.355, oy - 16 * SS, ox + L * 0.375, oy - 13 * SS],
           fill=(255, 255, 255, 255))
# open mouth, mid-leap
fd.ellipse([ox + L * 0.46, oy - 4 * SS, ox + L * 0.52, oy + 8 * SS],
           fill=(140, 25, 25, 255))
# rotate nose-up-right and place: clear above the wave band, below WOW!
fish = fish.rotate(38, resample=Image.BICUBIC, expand=False)
base.alpha_composite(fish, (int(0.165 * W), int(0.355 * W)))

# bubble trail from the bowl up to the leaping fish
bub = layer()
bd3 = ImageDraw.Draw(bub)
for k in range(14):
    t = k / 13
    bx = (0.27 + 0.13 * t) * W + rng.gauss(0, 8 * SS)
    by = (0.78 - 0.30 * t) * W + rng.gauss(0, 8 * SS)
    r = (3 + 5 * t) * SS
    bd3.ellipse([bx - r, by - r, bx + r, by + r],
                outline=(190, 235, 255, 190), width=2)
    bd3.ellipse([bx - r * 0.35, by - r * 0.35, bx + r * 0.1, by + r * 0.1],
                fill=(255, 255, 255, 150))
base.alpha_composite(bub)

# ================================================================ WOW! text
# Bold tilted yellow with orange outline, fully inside the frame.
txt = Image.new("RGBA", (int(0.62 * W), int(0.30 * W)), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)
font = ImageFont.truetype(FONT_PATH, int(0.115 * W))
word = "WOW!"
# soft dark shadow for legibility
td.text((14 * SS + 6, 12 * SS + 8), word, font=font, fill=(20, 8, 60, 200))
td.text((14 * SS, 12 * SS), word, font=font, fill=YELLOW + (255,),
        stroke_width=int(9 * SS), stroke_fill=(255, 90, 0, 255))
# small white sparkle accents on the letters
for (sx, sy, sr) in [(0.10, 0.16, 7), (0.52, 0.10, 9), (0.88, 0.30, 6)]:
    x, y = sx * txt.size[0], sy * txt.size[1]
    td.line([x - sr * SS, y, x + sr * SS, y], fill=WHITE + (230,),
            width=2)
    td.line([x, y - sr * SS, x, y + sr * SS], fill=WHITE + (230,),
            width=2)
txt = txt.rotate(-11, resample=Image.BICUBIC, expand=False,
                 fillcolor=(0, 0, 0, 0))
base.alpha_composite(txt, (int(0.315 * W), int(0.315 * W)))

# ================================================================ finish
img = base.convert("RGB").resize((FINAL, FINAL), Image.LANCZOS)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT} {img.size[0]}x{img.size[1]}")

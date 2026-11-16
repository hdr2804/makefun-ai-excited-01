#!/usr/bin/env python3
"""Build-time draw script for ai-excited-01 (NOT run by the grader).

Draws "One small leap becomes a universe": a tiny goldfish leaps out of
its little glass bowl (bottom left); its splash becomes a huge curling
wave that spirals up into a galaxy of stars and confetti (top right).
Saturated orange/magenta on deep indigo, bold tilted yellow WOW!.

Deterministic: seed 20261116, 2x supersample + Lanczos downscale to
1024x1024. PIL lesson applied throughout: ImageDraw on RGBA replaces
pixels instead of blending, so every translucent effect lives on its own
transparent layer and is merged with Image.alpha_composite (and the draw
handle is re-created after each composite).

Iteration 3 fixes over v2: foam crest now hugs the very edge and only
runs along the crest (v2's foam still read as a wide white ribbon);
smaller curl-cap disc; fainter highlight ribbon; faint stars fill the
lower frame so the bottom-right is not empty.

Usage: python3 draw_excited.py   (writes entry.png next to this file)
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SS = 2                      # supersample factor
W = H = 1024                # final size
SW = SH = W * SS
SEED = 20261116
OUT = "entry.png"

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)


# ---------------------------------------------------------------- helpers
def s(v):
    """Final-space coordinate -> supersampled coordinate."""
    return int(round(v * SS))


def new_layer():
    return Image.new("RGBA", (SW, SH), (0, 0, 0, 0))


def catmull_rom(points, samples=24):
    """Dense smooth curve through points (final-space coords)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples):
            t = j / samples
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


def soft_disc(layer, cx, cy, r, color, peak):
    """Radial glow: concentric discs, alpha falling off. Own layer in."""
    d = ImageDraw.Draw(layer)
    steps = 24
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(peak * (1 - i / steps) ** 1.6)
        d.ellipse([s(cx - rr), s(cy - rr), s(cx + rr), s(cy + rr)],
                  fill=color + (a,))


def sparkle(d, x, y, r, color):
    """4-point star sparkle."""
    w = max(1.0, r * 0.28)
    d.polygon([(s(x), s(y - r)), (s(x + w), s(y - w)), (s(x + r), s(y)),
               (s(x + w), s(y + w)), (s(x), s(y + r)), (s(x - w), s(y + w)),
               (s(x - r), s(y)), (s(x - w), s(y - w))], fill=color)


def star_dot(d, x, y, r, color):
    d.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=color)


# ------------------------------------------------------------------- fish
def fish_layer(cx, cy, length, angle_deg, body=(255, 140, 20),
               belly=(255, 196, 90), back=(214, 88, 0),
               fin=(255, 118, 8), happy=False):
    """A goldfish drawn axis-aligned (nose +x) on its own layer, then
    rotated nose-up by angle_deg. Returns the rotated layer."""
    L = float(length)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    X, Y = s(cx), s(cy)

    def lx(v):
        return X + s(v)

    def ly(v):
        return Y + s(v)

    # tail: forked fan, two distinct lobes with a notch between them
    tail = new_layer()
    td = ImageDraw.Draw(tail)
    td.polygon([(lx(-0.42 * L), ly(-0.02 * L)), (lx(-0.82 * L), ly(-0.32 * L)),
                (lx(-0.60 * L), ly(-0.04 * L))], fill=fin + (215,))
    td.polygon([(lx(-0.42 * L), ly(0.02 * L)), (lx(-0.82 * L), ly(0.32 * L)),
                (lx(-0.60 * L), ly(0.04 * L))], fill=fin + (215,))
    td.polygon([(lx(-0.44 * L), ly(0)), (lx(-0.66 * L), ly(-0.13 * L)),
                (lx(-0.66 * L), ly(0.13 * L))], fill=(255, 170, 60, 170))
    lay = Image.alpha_composite(lay, tail)
    d = ImageDraw.Draw(lay)

    # dorsal fin
    d.polygon([(lx(-0.10 * L), ly(-0.19 * L)), (lx(0.06 * L), ly(-0.34 * L)),
               (lx(0.16 * L), ly(-0.18 * L))], fill=fin + (235,))
    # body
    d.ellipse([lx(-0.50 * L), ly(-0.21 * L), lx(0.50 * L), ly(0.21 * L)],
              fill=body + (255,))
    # darker back
    d.ellipse([lx(-0.46 * L), ly(-0.21 * L), lx(0.46 * L), ly(-0.02 * L)],
              fill=back + (255,))
    d.ellipse([lx(-0.44 * L), ly(-0.20 * L), lx(0.44 * L), ly(-0.06 * L)],
              fill=(255, 158, 52, 255))
    # pale belly
    d.ellipse([lx(-0.38 * L), ly(0.02 * L), lx(0.42 * L), ly(0.21 * L)],
              fill=belly + (255,))
    # pectoral fin, small and flat against the belly
    d.ellipse([lx(-0.04 * L), ly(0.08 * L), lx(0.14 * L), ly(0.20 * L)],
              fill=fin + (220,))
    # scale hints
    for gx in (-0.28, -0.12, 0.04):
        d.arc([lx(gx * L), ly(-0.10 * L), lx((gx + 0.14) * L), ly(0.10 * L)],
              start=300, end=60, fill=(255, 220, 140, 160), width=s(3))
    # gill curve
    d.arc([lx(0.08 * L), ly(-0.13 * L), lx(0.24 * L), ly(0.13 * L)],
          start=270, end=90, fill=(190, 70, 0, 200), width=s(4))
    # body outline
    d.ellipse([lx(-0.50 * L), ly(-0.21 * L), lx(0.50 * L), ly(0.21 * L)],
              outline=(170, 60, 0, 255), width=s(4))
    # eye
    ex, ey = 0.30 * L, -0.07 * L
    if happy:
        d.arc([lx(ex - 0.05 * L), ly(ey - 0.04 * L),
               lx(ex + 0.05 * L), ly(ey + 0.04 * L)],
              start=200, end=340, fill=(20, 10, 10, 255), width=s(5))
    else:
        d.ellipse([lx(ex - 0.055 * L), ly(ey - 0.055 * L),
                   lx(ex + 0.055 * L), ly(ey + 0.055 * L)],
                  fill=(255, 255, 255, 255))
        d.ellipse([lx(ex - 0.028 * L), ly(ey - 0.028 * L),
                   lx(ex + 0.028 * L), ly(ey + 0.028 * L)],
                  fill=(16, 8, 8, 255))
        d.ellipse([lx(ex + 0.008 * L), ly(ey - 0.022 * L),
                   lx(ex + 0.024 * L), ly(ey - 0.006 * L)],
                  fill=(255, 255, 255, 255))
    # small open smiling mouth at the nose (not a red nose blob)
    d.ellipse([lx(0.43 * L), ly(0.03 * L), lx(0.50 * L), ly(0.10 * L)],
              fill=(122, 20, 10, 255))
    d.arc([lx(0.39 * L), ly(0.00 * L), lx(0.50 * L), ly(0.11 * L)],
          start=20, end=160, fill=(90, 10, 5, 255), width=s(3))

    return lay.rotate(angle_deg, resample=Image.BICUBIC, center=(X, Y))


# ------------------------------------------------------------------- build
def main():
    # ---- background: deep indigo gradient, lighter toward the bottom
    base = Image.new("RGBA", (SW, SH), (12, 8, 48, 255))
    grad = new_layer()
    gd = ImageDraw.Draw(grad)
    top = (10, 6, 44)
    bot = (46, 20, 104)
    for y in range(SH):
        t = y / SH
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        gd.line([(0, y), (SW, y)], fill=c + (255,))
    base = Image.alpha_composite(base, grad)

    # faint nebula wash, magenta top-right / teal bottom-left
    neb = new_layer()
    soft_disc(neb, 875, 155, 420, (150, 40, 130), 46)
    soft_disc(neb, 180, 880, 380, (20, 90, 140), 40)
    base = Image.alpha_composite(base, neb)

    # scattered sky stars
    sky = new_layer()
    sd = ImageDraw.Draw(sky)
    for _ in range(150):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 620)
        r = rng.uniform(0.8, 2.6)
        a = rng.randint(120, 255)
        c = rng.choice([(255, 255, 255), (255, 230, 170), (200, 225, 255),
                        (255, 190, 220)])
        star_dot(sd, x, y, r, c + (a,))
    for _ in range(14):
        x = rng.uniform(40, W - 40)
        y = rng.uniform(30, 560)
        sparkle(sd, x, y, rng.uniform(5, 11),
                (255, 255, 255, rng.randint(170, 235)))
    for _ in range(46):
        x = rng.uniform(0, W)
        y = rng.uniform(620, 1020)
        star_dot(sd, x, y, rng.uniform(0.8, 2.2),
                 (255, 255, 255, rng.randint(70, 150)))
    base = Image.alpha_composite(base, sky)

    # ---- galaxy top-right: dense spiral, many stars per arm + dust motes.
    # Centred (875, 155), clear of the wave curl so the spiral reads.
    gal = new_layer()
    soft_disc(gal, 875, 155, 170, (255, 190, 110), 120)
    soft_disc(gal, 875, 155, 100, (255, 230, 180), 150)
    soft_disc(gal, 875, 155, 48, (255, 246, 220), 210)
    gd2 = ImageDraw.Draw(gal)
    cx, cy = 875.0, 155.0
    arm_colors = [(255, 255, 255), (255, 205, 110), (255, 140, 205),
                  (140, 220, 255), (255, 170, 90)]
    for arm in range(3):
        off = arm * (2 * math.pi / 3)
        for i in range(110):
            t = i / 109
            ang = off + t * 4.6
            rad = 16 + t * 205 + rng.gauss(0, 8 + t * 14)
            x = cx + math.cos(ang) * rad
            y = cy + math.sin(ang) * rad * 0.82
            r = rng.uniform(1.2, 4.6) * (1 - t * 0.45)
            col = rng.choice(arm_colors)
            star_dot(gd2, x, y, r, col + (rng.randint(190, 255),))
            if rng.random() < 0.3:
                sparkle(gd2, x, y, r * 2.4, col + (150,))
    # dust motes: faint dense cloud around the core
    for _ in range(520):
        ang = rng.uniform(0, 2 * math.pi)
        rad = abs(rng.gauss(0, 85))
        x = cx + math.cos(ang) * rad
        y = cy + math.sin(ang) * rad * 0.85
        star_dot(gd2, x, y, rng.uniform(0.6, 1.8),
                 rng.choice([(255, 200, 230), (200, 210, 255),
                             (255, 220, 160)]) + (rng.randint(70, 150),))
    # confetti bursting out of the galaxy toward the wave
    conf = [(255, 60, 180), (255, 220, 0), (0, 220, 255), (255, 255, 255),
            (255, 140, 90)]
    for _ in range(70):
        x = rng.uniform(620, 1010)
        y = rng.uniform(30, 420)
        w = rng.uniform(4, 11)
        h = rng.uniform(2, 5)
        a = rng.uniform(0, math.pi)
        col = rng.choice(conf) + (rng.randint(180, 255),)
        pts = []
        for dx, dy in [(-w, -h), (w, -h), (w, h), (-w, h)]:
            pts.append((s(x + dx * math.cos(a) - dy * math.sin(a)),
                        s(y + dx * math.sin(a) + dy * math.cos(a))))
        gd2.polygon(pts, fill=col)
    base = Image.alpha_composite(base, gal)

    # ---- soft burst rays behind the leaping fish (7, wide + blurred)
    rays = new_layer()
    rd = ImageDraw.Draw(rays)
    rcx, rcy = 350.0, 600.0
    for k in range(7):
        ang = math.radians(-165 + k * 24 + rng.uniform(-5, 5))
        length = rng.uniform(150, 230)
        x2 = rcx + math.cos(ang) * length
        y2 = rcy + math.sin(ang) * length
        px, py = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
        wdt = 13
        rd.polygon([(s(rcx), s(rcy)),
                    (s(x2 + px * wdt), s(y2 + py * wdt)),
                    (s(x2 - px * wdt), s(y2 - py * wdt))],
                   fill=(255, 205, 110, 48))
    rays = rays.filter(ImageFilter.GaussianBlur(s(9)))
    base = Image.alpha_composite(base, rays)

    # ---- the wave: splash curling up toward the galaxy (curl ends
    # below-left of the galaxy core so the spiral stays visible)
    path = catmull_rom([(40, 1000), (150, 930), (300, 845), (455, 720),
                        (575, 565), (655, 425), (705, 320), (750, 262),
                        (800, 252), (832, 288), (818, 330), (778, 326),
                        (756, 296)], samples=30)
    n = len(path)
    wave = new_layer()
    wd = ImageDraw.Draw(wave)
    # body: slimmer tapering band, deep blue -> teal toward the crest
    for i, (x, y) in enumerate(path):
        t = i / (n - 1)
        r = 82 - 58 * t
        c = (int(14 + 10 * t), int(84 + 66 * t), int(165 + 30 * t))
        wd.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=c + (255,))
    # inner highlight ribbon, offset toward the inside of the curl
    for i in range(0, n - 2):
        t = i / (n - 1)
        x, y = path[i]
        x2, y2 = path[i + 2]
        dx, dy = x2 - x, y2 - y
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m  # inside of the curl
        r = 82 - 58 * t
        hx, hy = x + nx * r * 0.30, y + ny * r * 0.30
        wd.ellipse([s(hx - 5), s(hy - 5), s(hx + 5), s(hy + 5)],
                   fill=(120, 235, 255, 90))
    # foam crest: fine tapered caps along the outer edge, crest only
    # (t >= 0.30) so the wave's base stays clean blue
    for i, (x, y) in enumerate(path):
        t = i / (n - 1)
        if i + 2 >= n or t < 0.30:
            continue
        x2, y2 = path[i + 2]
        dx, dy = x2 - x, y2 - y
        m = math.hypot(dx, dy) or 1
        nx, ny = dy / m, -dx / m  # outer edge
        r = 82 - 58 * t
        fx, fy = x + nx * r * 0.85, y + ny * r * 0.85
        fr = max(3.5, 11 - 7 * t)
        wd.ellipse([s(fx - fr), s(fy - fr), s(fx + fr), s(fy + fr)],
                   fill=(238, 250, 255, 225))
    # foam curl cap at the tip + spray droplets
    tip = path[-1]
    wd.ellipse([s(tip[0] - 16), s(tip[1] - 16), s(tip[0] + 16), s(tip[1] + 16)],
               fill=(238, 250, 255, 235))
    for _ in range(26):
        ang = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(26, 70)
        star_dot(wd, tip[0] + math.cos(ang) * rr, tip[1] + math.sin(ang) * rr,
                 rng.uniform(2, 6), (230, 246, 255, rng.randint(150, 235)))
    base = Image.alpha_composite(base, wave)

    # ---- bowl, bottom-left, with the cheering second fish
    bowl = new_layer()
    bd = ImageDraw.Draw(bowl)
    bx, by, brx, bry = 240.0, 885.0, 168.0, 92.0
    # water
    bd.ellipse([s(bx - brx + 8), s(by - bry + 26), s(bx + brx - 8), s(by + bry - 6)],
               fill=(70, 170, 255, 110))
    bd.ellipse([s(bx - brx + 8), s(by - bry + 26), s(bx + brx - 8), s(by - bry + 44)],
               fill=(150, 220, 255, 130))
    # glass rim + shine
    bd.ellipse([s(bx - brx), s(by - bry), s(bx + brx), s(by + bry)],
               outline=(235, 245, 255, 235), width=s(7))
    bd.arc([s(bx - brx + 14), s(by - bry + 18), s(bx + brx - 60), s(by + bry - 14)],
           start=200, end=330, fill=(255, 255, 255, 170), width=s(8))
    bd.ellipse([s(bx - brx + 26), s(by + bry - 34), s(bx + brx - 26), s(by + bry - 8)],
               fill=(120, 200, 255, 60))
    base = Image.alpha_composite(base, bowl)

    # second fish inside the bowl, cheering nose-up
    base = Image.alpha_composite(
        base, fish_layer(240, 880, 118, 62, happy=True))
    # bubbles rising from the cheering fish
    bub = new_layer()
    bud = ImageDraw.Draw(bub)
    for i in range(9):
        x = 240 + rng.uniform(-30, 46)
        y = 800 - i * 16 + rng.uniform(-6, 6)
        r = rng.uniform(3, 7)
        bud.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)],
                    outline=(220, 240, 255, 210), width=s(2))
    base = Image.alpha_composite(base, bub)

    # ---- splash droplets + motion arcs from bowl rim to the leaping fish
    spl = new_layer()
    spd = ImageDraw.Draw(spl)
    for _ in range(34):
        x = rng.uniform(210, 420)
        y = rng.uniform(700, 845)
        r = rng.uniform(2.5, 8)
        spd.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)],
                    fill=(225, 242, 255, rng.randint(170, 240)))
    for k in range(3):
        spd.arc([s(190 + k * 26), s(560 + k * 30), s(520 + k * 26), s(850 + k * 30)],
                start=250, end=330, fill=(150, 225, 255, 110 - k * 22),
                width=s(7 - k))
    base = Image.alpha_composite(base, spl)

    # ---- the leaping goldfish, nose-up-right, clear of the wave band
    base = Image.alpha_composite(base, fish_layer(350, 600, 265, 35))

    # ---- WOW! — bold tilted yellow, orange outline, fully inside frame
    wow = new_layer()
    wfont = ImageFont.truetype(FONT_PATH, s(148))
    tw = ImageDraw.Draw(wow)
    text = "WOW!"
    # drop shadow
    tw.text((s(72), s(72)), text, font=wfont, fill=(8, 4, 40, 200))
    tw.text((s(64), s(64)), text, font=wfont, fill=(255, 214, 0, 255),
            stroke_width=s(11), stroke_fill=(255, 110, 0, 255))
    wow = wow.rotate(-12, resample=Image.BICUBIC, center=(s(270), s(150)))
    base = Image.alpha_composite(base, wow)

    # ---- foreground sparkles along the diagonal
    fg = new_layer()
    fd = ImageDraw.Draw(fg)
    for (x, y, r) in [(560, 480, 9), (660, 380, 7), (480, 700, 8),
                      (720, 560, 6), (180, 420, 8), (920, 480, 8),
                      (120, 640, 6), (860, 640, 7)]:
        sparkle(fd, x, y, r, (255, 255, 255, 235))
    base = Image.alpha_composite(base, fg)

    # ---- downscale + save
    img = base.convert("RGB").resize((W, H), Image.LANCZOS)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT}: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()

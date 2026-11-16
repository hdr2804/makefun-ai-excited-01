#!/usr/bin/env python3
"""ai-excited-01: 'One small leap becomes a universe'.

A goldfish leaps from its bowl (bottom-left); its splash becomes a curling
wave that spirals up into a galaxy of stars and confetti (top-right).
Saturated orange / magenta on deep indigo. Bold tilted yellow WOW! with an
orange outline. A second fish cheers from inside the bowl.

Deterministic: fixed seed 20261116, no timestamps, no input files.
Renders at 2x (2048) then Lanczos-downscales to 1024x1024.

Usage: python3 draw_excited.py [output.png]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
S = 2                      # supersample factor
W = H = 1024 * S           # working canvas
OUT = 1024

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)

# ---------------------------------------------------------------- palette
INDIGO_TOP = (10, 10, 40)
INDIGO_MID = (22, 16, 66)
INDIGO_BOT = (34, 12, 58)
MAGENTA = (255, 42, 140)
ORANGE = (255, 122, 26)
GOLD = (255, 178, 44)
YELLOW = (255, 212, 0)
WOW_OUTLINE = (255, 106, 0)
CYAN = (55, 200, 232)
FOAM = (230, 250, 255)
GALAXY_CORE = (255, 240, 190)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def new_layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def glow(layer, cx, cy, radius, color, peak_alpha):
    """Soft radial glow: concentric circles, alpha falling off."""
    d = ImageDraw.Draw(layer)
    steps = 24
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        a = int(peak_alpha * (1 - t) ** 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))


def sparkle(d, cx, cy, r, color, alpha=255):
    """Four-point star sparkle."""
    pts = [
        (cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy),
        (cx + r * 0.22, cy + r * 0.22), (cx, cy + r),
        (cx - r * 0.22, cy + r * 0.22), (cx - r, cy),
        (cx - r * 0.22, cy - r * 0.22),
    ]
    d.polygon(pts, fill=color + (alpha,))


def bezier(p0, p1, p2, p3, n=140):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
             + 3 * mt * t**2 * p2[0] + t**3 * p3[0])
        y = (mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
             + 3 * mt * t**2 * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


def make_fish(length, height, body=(255, 122, 26), belly=(255, 179, 71),
              back=(232, 93, 4), fin=(255, 158, 44)):
    """A goldfish facing right, nose at the right edge. Own RGBA layer."""
    pad = int(length * 0.12)
    lw, lh = length + 2 * pad, height + 2 * pad
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = pad, pad
    # tail fan (left): two orange lobes + a slim magenta centre wedge
    d.polygon([(ox + 6, oy + height * 0.52), (ox + length * 0.22, oy + height * 0.08),
               (ox + length * 0.26, oy + height * 0.48)], fill=fin + (255,))
    d.polygon([(ox + 6, oy + height * 0.52), (ox + length * 0.22, oy + height * 0.96),
               (ox + length * 0.26, oy + height * 0.56)], fill=fin + (255,))
    d.polygon([(ox + 30, oy + height * 0.52), (ox + length * 0.20, oy + height * 0.38),
               (ox + length * 0.22, oy + height * 0.52),
               (ox + length * 0.20, oy + height * 0.66)], fill=(255, 92, 110, 255))
    # body
    d.ellipse([ox + length * 0.20, oy + height * 0.16,
               ox + length * 0.94, oy + height * 0.86], fill=body + (255,))
    # darker back
    d.ellipse([ox + length * 0.20, oy + height * 0.16,
               ox + length * 0.94, oy + height * 0.52], fill=back + (255,))
    # bright belly
    d.ellipse([ox + length * 0.30, oy + height * 0.52,
               ox + length * 0.90, oy + height * 0.88], fill=belly + (255,))
    # dorsal fin
    d.polygon([(ox + length * 0.42, oy + height * 0.20),
               (ox + length * 0.52, oy + height * 0.00),
               (ox + length * 0.66, oy + height * 0.18)], fill=back + (255,))
    # pectoral fin
    d.polygon([(ox + length * 0.48, oy + height * 0.62),
               (ox + length * 0.58, oy + height * 0.86),
               (ox + length * 0.50, oy + height * 0.88)], fill=fin + (255,))
    # scales: rows of small arcs
    for row, yy in enumerate([0.34, 0.46, 0.58, 0.70]):
        x0 = length * (0.34 + 0.03 * row)
        for k in range(6):
            x = ox + x0 + k * length * 0.085
            y = oy + height * yy
            r = length * 0.045
            d.arc([x - r, y - r, x + r, y + r], start=200, end=340,
                  fill=(194, 78, 0, 130), width=max(2, int(length * 0.006)))
    # gill arc
    gx = ox + length * 0.70
    d.arc([gx - length * 0.07, oy + height * 0.28,
           gx + length * 0.07, oy + height * 0.78],
          start=300, end=60, fill=(194, 78, 0, 220),
          width=max(3, int(length * 0.012)))
    # mouth: tiny smile at the nose
    mx, my = ox + length * 0.92, oy + height * 0.60
    d.arc([mx - length * 0.05, my - length * 0.03,
           mx + length * 0.02, my + length * 0.05],
          start=10, end=170, fill=(140, 40, 0, 255),
          width=max(3, int(length * 0.010)))
    # eye
    ex, ey = ox + length * 0.80, oy + height * 0.38
    er = length * 0.045
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(255, 255, 255, 255))
    pr = er * 0.55
    d.ellipse([ex - pr, ey - pr, ex + pr, ey + pr], fill=(10, 10, 20, 255))
    hr = er * 0.22
    d.ellipse([ex - pr * 0.4 - hr, ey - pr * 0.4 - hr,
               ex - pr * 0.4 + hr, ey - pr * 0.4 + hr], fill=(255, 255, 255, 255))
    return layer


def paste_centered(base, layer, cx, cy, angle=0):
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    x = int(cx - layer.width / 2)
    y = int(cy - layer.height / 2)
    base.alpha_composite(layer, dest=(x, y))


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("entry.png")

    # ---------------------------------------------------------- background
    base = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(base)
    for y in range(H):
        t = y / (H - 1)
        c = lerp(INDIGO_TOP, INDIGO_MID, t) if t < 0.55 else lerp(
            INDIGO_MID, INDIGO_BOT, (t - 0.55) / 0.45)
        d.line([(0, y), (W, y)], fill=c + (255,))

    # faint background stars everywhere
    stars = new_layer()
    ds = ImageDraw.Draw(stars)
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(0.8, 2.6)
        a = rng.randint(40, 130)
        ds.ellipse([x - r, y - r, x + r, y + r],
                   fill=(255, 255, 255, a))
    base.alpha_composite(stars)

    # ambient glows: magenta top-right (galaxy), warm orange bottom-left (bowl)
    gl = new_layer()
    glow(gl, 1620, 520, 900, (255, 42, 140), 46)
    glow(gl, 480, 1750, 800, (255, 122, 26), 40)
    glow(gl, 1024, 1024, 1200, (40, 30, 120), 26)
    base.alpha_composite(gl)

    # ---------------------------------------------------------- burst rays
    # <=9 soft rays from the galaxy core; blurred so they never read as fireworks
    rays = new_layer()
    dr = ImageDraw.Draw(rays)
    gx, gy = 1620, 520
    ray_cols = [(255, 220, 130), (255, 150, 200), (190, 230, 255),
                (255, 200, 90), (255, 120, 170)]
    for i in range(7):
        ang = math.radians(-168 + i * 26 + rng.uniform(-6, 6))
        length = rng.uniform(420, 620)
        width = math.radians(rng.uniform(5, 9))
        tip = (gx + length * math.cos(ang), gy + length * math.sin(ang))
        left = (gx + 60 * math.cos(ang - width / 2),
                gy + 60 * math.sin(ang - width / 2))
        right = (gx + 60 * math.cos(ang + width / 2),
                 gy + 60 * math.sin(ang + width / 2))
        dr.polygon([left, tip, right],
                   fill=ray_cols[i % len(ray_cols)] + (52,))
    rays = rays.filter(ImageFilter.GaussianBlur(7))
    base.alpha_composite(rays)

    # ---------------------------------------------------------- galaxy
    gal = new_layer()
    dg = ImageDraw.Draw(gal)
    # core glow + bright heart
    glow(gal, gx, gy, 210, (255, 220, 150), 150)
    glow(gal, gx, gy, 110, (255, 250, 220), 200)
    dg.ellipse([gx - 42, gy - 42, gx + 42, gy + 42],
               fill=GALAXY_CORE + (255,))
    dg.ellipse([gx - 22, gy - 22, gx + 22, gy + 22],
               fill=(255, 255, 255, 255))
    # three dense spiral arms: many stars per arm + dust motes
    arm_cols = [(255, 255, 255), (255, 233, 168), (255, 154, 213),
                (127, 231, 255), (255, 190, 90)]
    for arm in range(3):
        phi0 = arm * 2 * math.pi / 3
        for i in range(150):
            t = i / 149
            r = 46 + 430 * t
            th = phi0 + 2.4 * math.pi * t + rng.uniform(-0.10, 0.10)
            rr = r * (1 + rng.uniform(-0.05, 0.05))
            x = gx + rr * math.cos(th)
            y = gy + rr * math.sin(th) * 0.86
            size = max(1.2, 7.5 * (1 - t) + rng.uniform(-1, 1))
            col = arm_cols[rng.randrange(len(arm_cols))]
            a = rng.randint(150, 255)
            if size > 4.5 and rng.random() < 0.35:
                sparkle(dg, x, y, size * 1.7, col, a)
            else:
                dg.ellipse([x - size, y - size, x + size, y + size],
                           fill=col + (a,))
    # extra inner-disc stars so the core is a dense cloud, not a bare ring
    for _ in range(140):
        ang = rng.uniform(0, 2 * math.pi)
        rr = 200 * math.sqrt(rng.random())
        x = gx + rr * math.cos(ang)
        y = gy + rr * math.sin(ang) * 0.86
        r = rng.uniform(1.5, 4.5)
        col = arm_cols[rng.randrange(len(arm_cols))]
        dg.ellipse([x - r, y - r, x + r, y + r],
                   fill=col + (rng.randint(170, 255),))
    # dust motes: dense faint cloud filling the disc between arms
    for _ in range(520):
        ang = rng.uniform(0, 2 * math.pi)
        rr = 480 * math.sqrt(rng.random())
        x = gx + rr * math.cos(ang)
        y = gy + rr * math.sin(ang) * 0.86
        r = rng.uniform(0.8, 2.4)
        col = arm_cols[rng.randrange(len(arm_cols))]
        dg.ellipse([x - r, y - r, x + r, y + r],
                   fill=col + (rng.randint(60, 150),))
    # confetti bursting out of the galaxy, top-right
    for _ in range(80):
        x = gx + rng.uniform(-420, 480)
        y = gy + rng.uniform(-420, 380)
        if math.hypot(x - gx, (y - gy) / 0.86) < 190:
            continue
        ln = rng.uniform(12, 30)
        wd = rng.uniform(5, 10)
        ang = rng.uniform(0, math.pi)
        col = [(255, 122, 26), (255, 42, 140), (255, 212, 0),
               (55, 200, 232), (255, 255, 255)][rng.randrange(5)]
        cx, cy = math.cos(ang), math.sin(ang)
        px, py = -cy, cx
        pts = [(x + cx * ln / 2 + px * wd / 2, y + cy * ln / 2 + py * wd / 2),
               (x - cx * ln / 2 + px * wd / 2, y - cy * ln / 2 + py * wd / 2),
               (x - cx * ln / 2 - px * wd / 2, y - cy * ln / 2 - py * wd / 2),
               (x + cx * ln / 2 - px * wd / 2, y + cy * ln / 2 - py * wd / 2)]
        dg.polygon(pts, fill=col + (rng.randint(190, 255),))
    base.alpha_composite(gal)

    # ---------------------------------------------------------- bowl
    bowl = new_layer()
    db = ImageDraw.Draw(bowl)
    bx, by = 560, 1700          # bowl centre (rim line y)
    bw, bh = 760, 300           # bowl width / depth below rim
    # water: bottom half-ellipse below the rim (a real bowl, not a flat disc)
    db.pieslice([bx - bw / 2, by - 46, bx + bw / 2, by + bh], start=0, end=180,
                fill=(70, 160, 235, 150))
    db.pieslice([bx - bw / 2 + 40, by + 40, bx + bw / 2 - 40, by + bh - 10],
                start=0, end=180, fill=(28, 88, 180, 90))
    # glass body: outline of the same half-ellipse
    db.pieslice([bx - bw / 2, by - 30, bx + bw / 2, by + bh], start=0, end=180,
                outline=(150, 210, 255, 200), width=10)
    db.pieslice([bx - bw / 2 + 26, by - 6, bx + bw / 2 - 26, by + bh - 26],
                start=0, end=180, outline=(200, 235, 255, 90), width=6)
    # water surface line + rim highlight
    db.ellipse([bx - bw / 2, by - 52, bx + bw / 2, by + 6],
               outline=(190, 235, 255, 230), width=8)
    db.arc([bx - bw / 2 + 60, by + bh - 90, bx + bw / 2 - 60, by + bh + 30],
           start=20, end=160, fill=(255, 255, 255, 110), width=8)
    # foot
    db.polygon([(bx - 130, by + bh - 8), (bx + 130, by + bh - 8),
                (bx + 92, by + bh + 42), (bx - 92, by + bh + 42)],
               fill=(30, 40, 90, 255))
    db.polygon([(bx - 130, by + bh - 8), (bx + 130, by + bh - 8),
                (bx + 92, by + bh + 42), (bx - 92, by + bh + 42)],
               outline=(150, 210, 255, 160))
    base.alpha_composite(bowl)

    # second fish cheering inside the bowl, nose up-right
    fish2 = make_fish(300, 190)
    paste_centered(base, fish2, 560, 1790, angle=28)
    # cheering bubbles above it
    bub = new_layer()
    db2 = ImageDraw.Draw(bub)
    for i, (bx2, by2, br) in enumerate([(470, 1600, 16), (540, 1540, 22),
                                        (620, 1590, 13), (590, 1480, 18)]):
        db2.ellipse([bx2 - br, by2 - br, bx2 + br, by2 + br],
                    outline=(220, 245, 255, 220), width=5)
        db2.ellipse([bx2 - br * 0.35, by2 - br * 0.4,
                     bx2 - br * 0.05, by2 - br * 0.1],
                    fill=(255, 255, 255, 200))
    base.alpha_composite(bub)

    # ---------------------------------------------------------- wave
    # curling band: splash at the bowl rim spiralling up into the galaxy
    wave = new_layer()
    dw = ImageDraw.Draw(wave)
    pts = bezier((880, 1640), (920, 1160), (1420, 1080), (1690, 640))
    for i, (x, y) in enumerate(pts):
        t = i / (len(pts) - 1)
        r = 96 * (1 - t) + 14
        c = lerp((16, 70, 150), (55, 200, 232), t)
        dw.ellipse([x - r, y - r, x + r, y + r], fill=c + (235,))
    # inner highlight ribbon: a thinner bright line hugging the inside of the curl
    for i, (x, y) in enumerate(pts):
        t = i / (len(pts) - 1)
        if t < 0.10 or t > 0.92:
            continue
        # perpendicular offset toward the inside of the curve
        x2, y2 = pts[min(i + 2, len(pts) - 1)]
        x0, y0 = pts[max(i - 2, 0)]
        dx, dy = x2 - x0, y2 - y0
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        cx, cy = x + nx * 34, y + ny * 34
        r = 26 * (1 - t) + 7
        dw.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(191, 243, 255, 235))
    # foam: tapered white caps along the outer edge + droplets at the tip
    for i, (x, y) in enumerate(pts):
        t = i / (len(pts) - 1)
        if rng.random() < 0.55:
            x2, y2 = pts[min(i + 2, len(pts) - 1)]
            x0, y0 = pts[max(i - 2, 0)]
            dx, dy = x2 - x0, y2 - y0
            ln = math.hypot(dx, dy) or 1
            nx, ny = dy / ln, -dx / ln
            off = (96 * (1 - t) + 14) * rng.uniform(0.55, 0.95)
            fx, fy = x + nx * off, y + ny * off
            fr = rng.uniform(5, 15) * (1 - t * 0.5)
            dw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
                       fill=FOAM + (rng.randint(180, 255),))
    base.alpha_composite(wave)

    # splash crown where the fish left the water
    sp = new_layer()
    dsp = ImageDraw.Draw(sp)
    sx, sy = 880, 1620
    for ang in range(-160, -20, 14):
        a = math.radians(ang)
        ln = rng.uniform(90, 210)
        ex, ey = sx + ln * math.cos(a), sy + ln * math.sin(a)
        r = rng.uniform(8, 20)
        dsp.ellipse([ex - r, ey - r, ex + r, ey + r],
                    fill=FOAM + (230,))
        dsp.line([(sx, sy), (ex, ey)], fill=(160, 220, 255, 160), width=7)
    for _ in range(26):
        a = math.radians(rng.uniform(-170, -10))
        ln = rng.uniform(40, 260)
        ex, ey = sx + ln * math.cos(a), sy + ln * math.sin(a)
        r = rng.uniform(3, 9)
        dsp.ellipse([ex - r, ey - r, ex + r, ey + r],
                    fill=(200, 235, 255, 220))
    base.alpha_composite(sp)

    # ---------------------------------------------------------- leaping fish
    # nose up-right, lifted clear of the wave band
    fish = make_fish(620, 400)
    paste_centered(base, fish, 860, 1180, angle=35)
    # sparkle at the nose
    spk = new_layer()
    dspk = ImageDraw.Draw(spk)
    sparkle(dspk, 1160, 960, 46, (255, 255, 255), 255)
    sparkle(dspk, 1220, 1030, 26, (255, 233, 168), 230)
    base.alpha_composite(spk)

    # ---------------------------------------------------------- WOW!
    font = ImageFont.truetype(FONT, 300)
    txt = "WOW!"
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = probe.textbbox((0, 0), txt, font=font, stroke_width=20)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 60
    tl = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tl)
    dt.text((pad - bbox[0], pad - bbox[1]), txt, font=font,
            fill=YELLOW + (255,), stroke_width=20,
            stroke_fill=WOW_OUTLINE + (255,))
    # small white sparkle accents on the text layer
    sparkle(dt, tw + pad - 40, pad + 26, 30, (255, 255, 255), 255)
    sparkle(dt, pad + 30, th + pad - 30, 20, (255, 233, 168), 230)
    paste_centered(base, tl, 700, 560, angle=-12)

    # ---------------------------------------------------------- vignette
    # smooth radial falloff rendered small, then upscaled (no rectangle banding)
    vs = 256
    vmask = Image.new("L", (vs, vs), 0)
    dv = ImageDraw.Draw(vmask)
    for yy in range(vs):
        for xx in range(vs):
            dx = (xx / (vs - 1) - 0.5) * 2
            dy = (yy / (vs - 1) - 0.5) * 2
            dist = math.sqrt(dx * dx + dy * dy)
            a = max(0.0, (dist - 0.72) / 0.55) ** 2
            dv.point((xx, yy), fill=int(64 * a))
    vmask = vmask.resize((W, H), Image.BICUBIC)
    dark = Image.new("RGBA", (W, H), (4, 4, 18, 255))
    dark.putalpha(vmask)
    base.alpha_composite(dark)

    # ---------------------------------------------------------- finish
    img = base.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ai-excited-01 — build-time image generator (PIL, stdlib + Pillow).

"One small leap becomes a universe": a goldfish leaps from its bowl
(bottom-left); its splash becomes a curling wave spiralling into a galaxy
of stars and confetti (top-right); bold tilted yellow WOW! in the sky.
Deterministic: seed 20261116, 2x supersample (2048) + Lanczos downscale
to 1024. All translucent effects live on separate layers merged with
Image.alpha_composite (ImageDraw on RGBA replaces pixels instead of
blending — drawing glow/foam straight onto the base smears it).
"""
import math
import random
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
S = 2048          # supersampled canvas
OUT = 1024        # final size
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

rng = random.Random(SEED)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def paste(base, lay):
    base.alpha_composite(lay)


def soft_glow(base, cx, cy, radius, color, peak=70, blur=90):
    """Radial glow: concentric ellipses, fading alpha, then blurred."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    steps = 24
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    paste(base, lay)


def bezier(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return (x, y), (dx, dy)


def draw_fish(length, angle_deg, mouth_open=True):
    """A cartoon goldfish pointing +x, on its own layer, rotated nose-up-right.

    Returns a layer with the fish centred. Body: warm orange with pale
    belly and deep-red back; magenta-tinted flowing tail and fins; one eye,
    open smiling mouth, gill arc, scale hints. One dorsal fin, one pectoral
    fin — nothing extra, so the anatomy reads clean at 300 px.
    """
    w = int(length * 1.7)
    h = int(length * 0.95)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = w * 0.58, h * 0.5
    L, H = length, length * 0.42
    # tail: two flowing lobes fanning from the rear
    tx = cx - L * 0.42
    tail = layer()
    td = ImageDraw.Draw(tail)
    td.polygon([(tx + 30, cy), (w * 0.02, cy - H * 0.62),
                (w * 0.10, cy), (w * 0.02, cy + H * 0.62)],
               fill=(255, 46, 136, 210))
    td.polygon([(tx + 30, cy), (w * 0.06, cy - H * 0.42),
                (w * 0.13, cy), (w * 0.06, cy + H * 0.42)],
               fill=(255, 110, 60, 200))
    tail = tail.filter(ImageFilter.GaussianBlur(3))
    lay.alpha_composite(tail)
    d = ImageDraw.Draw(lay)
    # body
    d.ellipse([cx - L / 2, cy - H / 2, cx + L / 2, cy + H / 2],
              fill=(255, 138, 42, 255))
    # pale belly (lower half)
    d.ellipse([cx - L * 0.38, cy - H * 0.05, cx + L * 0.42, cy + H * 0.48],
              fill=(255, 196, 107, 255))
    # deep back shading along the top
    d.arc([cx - L / 2, cy - H / 2, cx + L / 2, cy + H / 2],
          start=195, end=345, fill=(232, 62, 26, 255), width=int(H * 0.10))
    # dorsal fin on top, swept back
    d.polygon([(cx - L * 0.10, cy - H * 0.42), (cx + L * 0.12, cy - H * 0.78),
               (cx + L * 0.30, cy - H * 0.44)], fill=(255, 46, 136, 220))
    # pectoral fin below, angled back
    d.polygon([(cx - L * 0.02, cy + H * 0.28), (cx + L * 0.10, cy + H * 0.62),
               (cx + L * 0.24, cy + H * 0.30)], fill=(255, 110, 60, 220))
    # scale hints: short arcs on the flank
    for i, sx in enumerate([-0.18, -0.02, 0.14]):
        d.arc([cx + sx * L - 26, cy - 26, cx + sx * L + 26, cy + 26],
              start=300, end=60, fill=(255, 220, 140, 160), width=5)
    # gill arc behind the eye
    d.arc([cx + L * 0.18, cy - H * 0.22, cx + L * 0.38, cy + H * 0.22],
          start=300, end=60, fill=(200, 60, 20, 220), width=7)
    # eye
    ex, ey = cx + L * 0.33, cy - H * 0.14
    er = H * 0.085
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(255, 255, 255, 255))
    d.ellipse([ex - er * 0.55, ey - er * 0.55, ex + er * 0.55, ey + er * 0.55],
              fill=(20, 10, 40, 255))
    d.ellipse([ex - er * 0.25, ey - er * 0.5, ex + er * 0.15, ey - er * 0.1],
              fill=(255, 255, 255, 255))
    # open smiling mouth at the nose
    mx, my = cx + L * 0.47, cy + H * 0.06
    if mouth_open:
        d.ellipse([mx - 16, my - 12, mx + 16, my + 12], fill=(122, 30, 0, 255))
        d.arc([mx - 26, my - 8, mx + 22, my + 26], start=10, end=150,
              fill=(122, 30, 0, 255), width=6)
    else:
        d.arc([mx - 26, my - 14, mx + 22, my + 20], start=10, end=150,
              fill=(122, 30, 0, 255), width=6)
    return lay.rotate(angle_deg, expand=True, resample=Image.BICUBIC)


def main(out_path):
    base = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(base)
    # --- deep indigo background: vertical gradient ---
    top, bot = (11, 15, 46), (36, 22, 64)
    for y in range(S):
        d.line([(0, y), (S, y)], fill=lerp(top, bot, y / S) + (255,))
    d = ImageDraw.Draw(base)

    gx, gy = 1630, 430            # galaxy centre
    fx, fy = 660, 1090           # leaping fish centre (clear of the wave)
    bx, by = 430, 1620           # bowl centre

    # --- glows (own layers, blurred) ---
    soft_glow(base, gx, gy, 620, (255, 46, 136), peak=46, blur=110)
    soft_glow(base, fx, fy, 520, (255, 140, 40), peak=40, blur=100)

    # --- galaxy: dense spiral arms + dust motes ---
    gal = layer()
    gd = ImageDraw.Draw(gal)
    core = layer()
    cd = ImageDraw.Draw(core)
    for i in range(26, 0, -1):
        r = 220 * i / 26
        cd.ellipse([gx - r, gy - r, gx + r, gy + r],
                   fill=(255, 220, 160, int(170 * (1 - i / 26) ** 2)))
    core = core.filter(ImageFilter.GaussianBlur(36))
    gal.alpha_composite(core)
    gd = ImageDraw.Draw(gal)
    star_cols = [(255, 255, 255), (255, 233, 168), (127, 231, 255),
                 (255, 122, 217), (255, 190, 120)]
    for arm in range(3):
        base_ang = arm * 2 * math.pi / 3
        for i in range(175):
            t = i / 175
            ang = base_ang + t * 2.5 + rng.uniform(-0.09, 0.09)
            rad = 30 + t * 510 + rng.uniform(-26, 26)
            px = gx + math.cos(ang) * rad
            py = gy + math.sin(ang) * rad
            sz = max(2.0, 9.5 * (1 - t * 0.72) + rng.uniform(-1.5, 1.5))
            col = star_cols[int(t * len(star_cols)) % len(star_cols)]
            if sz > 6:
                gd.line([px - sz, py, px + sz, py], fill=col + (235,), width=3)
                gd.line([px, py - sz, px, py + sz], fill=col + (235,), width=3)
            gd.ellipse([px - sz / 2, py - sz / 2, px + sz / 2, py + sz / 2],
                       fill=col + (240,))
    for _ in range(170):  # dust motes
        ang = rng.uniform(0, 2 * math.pi)
        rad = rng.uniform(20, 520)
        px = gx + math.cos(ang) * rad
        py = gy + math.sin(ang) * rad
        r = rng.uniform(1.5, 4.5)
        col = rng.choice([(255, 150, 220), (200, 160, 255), (255, 210, 140)])
        gd.ellipse([px - r, py - r, px + r, py + r],
                   fill=col + (rng.randint(35, 95),))
    paste(base, gal)

    # --- confetti: bright rotated rectangles, biased to the top-right ---
    conf = layer()
    conf_cols = [(255, 210, 63), (255, 94, 138), (63, 210, 255), (124, 255, 107),
                 (255, 122, 217)]
    for _ in range(95):
        px = rng.uniform(850, 2010)
        py = rng.uniform(70, 1080)
        w, h = rng.uniform(12, 30), rng.uniform(7, 14)
        tile = Image.new("RGBA", (int(w * 2), int(h * 2)), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.rectangle([w / 2, h / 2, w / 2 + w, h / 2 + h],
                     fill=rng.choice(conf_cols) + (235,))
        tile = tile.rotate(rng.uniform(0, 360), expand=True,
                           resample=Image.BICUBIC)
        conf.alpha_composite(tile, (int(px - tile.width / 2),
                                    int(py - tile.height / 2)))
    paste(base, conf)

    # --- wave: curling band from the bowl up into the galaxy ---
    # Narrower than a first pass, bowed right so the leaping fish clears it.
    p0, p1, p2 = (560, 1560), (1250, 1250), (1620, 480)
    wave = layer()
    wd = ImageDraw.Draw(wave)
    pts = []
    for i in range(61):
        t = i / 60
        (x, y), (dx, dy) = bezier(p0, p1, p2, t)
        r = 210 * (1 - t * 0.92) + 12
        col = lerp((20, 85, 160), (63, 193, 255), t)
        wd.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
        pts.append(((x, y), (dx, dy), r, t))
    wave = wave.filter(ImageFilter.GaussianBlur(2))
    paste(base, wave)
    # foam: dense tapered white edge along the outer side.
    # Normals are chosen with continuity (dot with the previous normal),
    # not a per-sample sign test — a per-sample test flips the foam to the
    # other side mid-curve and leaves a visible step in the edge.
    foam = layer()
    fd = ImageDraw.Draw(foam)
    prev_n = None
    for j in range(121):
        t = j / 120
        (x, y), (dx, dy) = bezier(p0, p1, p2, t)
        r = 210 * (1 - t * 0.92) + 12
        n = (-dy, dx)
        if prev_n is not None:
            if n[0] * prev_n[0] + n[1] * prev_n[1] < 0:
                n = (-n[0], -n[1])
        elif n[0] - n[1] < 0:
            n = (-n[0], -n[1])
        prev_n = n
        nl = math.hypot(*n) or 1
        ox, oy = x + n[0] / nl * r * 0.82, y + n[1] / nl * r * 0.82
        fr = max(4, r * 0.20 * (1 - t * 0.45))
        fd.ellipse([ox - fr, oy - fr, ox + fr, oy + fr],
                   fill=(255, 255, 255, 225))
    # inner highlight ribbon: one smooth line inset from the foam, not dots
    rib = []
    prev_n = None
    for (x, y), (dx, dy), r, t in pts:
        n = (-dy, dx)
        if prev_n is not None:
            if n[0] * prev_n[0] + n[1] * prev_n[1] < 0:
                n = (-n[0], -n[1])
        elif n[0] - n[1] < 0:
            n = (-n[0], -n[1])
        prev_n = n
        nl = math.hypot(*n) or 1
        rib.append((x + n[0] / nl * r * 0.30, y + n[1] / nl * r * 0.30))
    fd.line(rib, fill=(191, 239, 255, 200), width=16, joint="curve")
    # splash crown where the wave erupts from the bowl
    for k in range(7):
        a = math.radians(-70 + k * 18)
        dx = math.cos(a) * rng.uniform(60, 170)
        dy = math.sin(a) * rng.uniform(50, 150)
        rr = rng.uniform(10, 26)
        fd.ellipse([p0[0] + dx - rr, p0[1] + dy - rr,
                    p0[0] + dx + rr, p0[1] + dy + rr],
                   fill=(255, 255, 255, 230))
    foam = foam.filter(ImageFilter.GaussianBlur(2))
    paste(base, foam)

    # --- burst rays behind the leap: 7 soft rays, no firework look ---
    rays = layer()
    rd = ImageDraw.Draw(rays)
    for i in range(7):
        ang = math.radians(-160 + i * 24 + rng.uniform(-5, 5))
        ln = rng.uniform(420, 620)
        x2, y2 = fx + math.cos(ang) * ln, fy + math.sin(ang) * ln
        perp = (-math.sin(ang), math.cos(ang))
        wdt = rng.uniform(16, 30)
        rd.polygon([(fx, fy),
                    (x2 + perp[0] * wdt, y2 + perp[1] * wdt),
                    (x2 - perp[0] * wdt, y2 - perp[1] * wdt)],
                   fill=(255, 200, 80, 52))
    rays = rays.filter(ImageFilter.GaussianBlur(18))
    paste(base, rays)

    # --- motion arcs trailing the leaping fish ---
    arcs = layer()
    ad = ImageDraw.Draw(arcs)
    for i, rr in enumerate([210, 280, 350]):
        ad.arc([fx - rr, fy - rr, fx + rr, fy + rr], start=95, end=175,
               fill=(255, 255, 255, 110 - i * 22), width=12)
    arcs = arcs.filter(ImageFilter.GaussianBlur(6))
    paste(base, arcs)

    # --- bowl (bottom-left) with water, pebbles, glass highlight ---
    bowl = layer()
    bd = ImageDraw.Draw(bowl)
    bd.ellipse([bx - 330, by - 170, bx + 330, by + 250],
               fill=(90, 180, 235, 90))                       # glass body
    bd.ellipse([bx - 330, by - 170, bx + 330, by + 250],
               outline=(200, 235, 255, 220), width=10)         # rim glass
    bd.ellipse([bx - 310, by - 120, bx + 310, by + 230],
               fill=(70, 160, 230, 130))                       # water
    for px, pr in [(-180, 26), (-60, 34), (80, 22), (190, 30)]:
        bd.ellipse([bx + px - pr, by + 200 - pr, bx + px + pr, by + 200 + pr],
                   fill=(120, 120, 160, 200))                  # pebbles
    bd.arc([bx - 300, by - 140, bx + 300, by + 220], start=200, end=330,
           fill=(255, 255, 255, 170), width=14)                # glass shine
    bd.ellipse([bx - 330, by - 185, bx + 330, by - 135],
               fill=(160, 220, 255, 120))                      # water surface
    paste(base, bowl)

    # --- second fish in the bowl, cheering (upright, mouth open) ---
    small = draw_fish(210, 55)
    base.alpha_composite(small, (int(bx - small.width / 2 - 10),
                                 int(by - small.height / 2 + 20)))
    cheer = layer()
    chd = ImageDraw.Draw(cheer)
    for i, ang in enumerate([-55, -90, -125]):
        a = math.radians(ang)
        x1, y1 = bx + math.cos(a) * 190, by - 160 + math.sin(a) * 60
        x2, y2 = bx + math.cos(a) * 260, by - 160 + math.sin(a) * 90
        chd.line([x1, y1, x2, y2], fill=(255, 220, 90, 230), width=12)
    paste(base, cheer)

    # --- leaping fish, nose-up-right, clear of the wave band ---
    fish = draw_fish(460, 38)
    base.alpha_composite(fish, (int(fx - fish.width / 2),
                                int(fy - fish.height / 2)))

    # --- bubbles rising from bowl to fish ---
    bub = layer()
    bud = ImageDraw.Draw(bub)
    for _ in range(26):
        t = rng.uniform(0, 1)
        px = 430 + t * 300 + rng.uniform(-40, 40)
        py = 1560 - t * 480 + rng.uniform(-40, 40)
        r = rng.uniform(8, 30)
        bud.ellipse([px - r, py - r, px + r, py + r],
                    outline=(255, 255, 255, 200), width=4)
        bud.ellipse([px - r * 0.4, py - r * 0.55, px - r * 0.1, py - r * 0.25],
                    fill=(255, 255, 255, 220))
    paste(base, bub)

    # --- WOW! bold tilted yellow with orange outline, fully in frame ---
    try:
        font = ImageFont.truetype(FONT_PATHS[0], 330)
    except OSError:
        font = ImageFont.truetype(FONT_PATHS[1], 330)
    text_lay = Image.new("RGBA", (1200, 560), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_lay)
    td.text((600, 280), "WOW!", font=font, anchor="mm",
            fill=(255, 212, 0, 255), stroke_width=16,
            stroke_fill=(255, 106, 0, 255))
    text_lay = text_lay.rotate(-12, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(text_lay, (120, 300))

    img = base.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    img.save(out_path, "PNG", optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")

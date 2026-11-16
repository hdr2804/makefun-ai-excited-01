#!/usr/bin/env python3
"""ai-excited-01 — "One small leap becomes a universe".

Build-time art script (PIL only, deterministic seed 20261116).
Draws at 2x supersample (2048x2048) and downscales with Lanczos to
1024x1024 -> entry.png in this directory.

Composition: a goldfish leaps from its bowl (bottom-left); its splash
becomes a curling wave that spirals into a galaxy of stars and confetti
(top-right). Saturated orange/magenta on deep indigo, bold tilted yellow
WOW!, and a second little fish in the bowl cheering it on.

PIL note: ImageDraw on an RGBA image REPLACES pixels instead of blending,
so every translucent effect (glow, streaks, burst core, motion arcs,
bubbles) is drawn on its own layer and merged with alpha_composite.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
S = 2                      # supersample factor
W = 1024 * S               # working size 2048
OUT = 1024
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)


def sc(v):
    """Scale a 1024-space coordinate to working space."""
    return v * S


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


# Palette
INDIGO_TOP = (16, 10, 48)
INDIGO_BOT = (38, 14, 74)
ORANGE = (255, 122, 26)
ORANGE_DK = (232, 84, 10)
MAGENTA = (255, 45, 149)
CYAN = (38, 214, 255)
TEAL = (20, 184, 196)
YELLOW = (255, 221, 40)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- background
def make_background():
    base = Image.new("RGB", (W, W))
    px = base.load()
    for y in range(W):
        t = y / W
        c = mix(INDIGO_TOP, INDIGO_BOT, t)
        for x in range(0, W, 8):
            # subtle radial lift toward the galaxy (top-right)
            d = math.hypot(x - sc(790), y - sc(230)) / sc(1050)
            lift = max(0.0, 1.0 - d) ** 2 * 26
            col = tuple(min(255, int(v + lift)) for v in c)
            for dx in range(8):
                if x + dx < W:
                    px[x + dx, y] = col
    img = base.convert("RGBA")
    # faint distant stars on their own layer so alpha behaves
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(340):
        x = rng.uniform(0, W)
        y = rng.uniform(0, W)
        r = rng.uniform(0.8, 2.4) * S / 2
        a = rng.randint(50, 150)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 255, a))
    return Image.alpha_composite(img, layer)


# ---------------------------------------------------------------- glow helper
def glow_layer(centre, radius, colour, peak_alpha):
    """Soft radial glow: filled disc on its own layer, blurred hard."""
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = centre
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=colour + (peak_alpha,))
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.55))


# ---------------------------------------------------------------- wave path
def wave_point(t):
    """Quadratic bezier from the bowl lip up to the galaxy heart."""
    p0 = (sc(205), sc(722))
    p1 = (sc(300), sc(648))
    p2 = (sc(742), sc(268))
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y


def ribbon(t_values, width_fn, offset_fn):
    """Return (left_edge, right_edge) point lists for a tapered ribbon."""
    left, right = [], []
    pts = [wave_point(t) for t in t_values]
    for i, (x, y) in enumerate(pts):
        if i + 1 < len(pts):
            nx, ny = pts[i + 1]
        else:
            nx, ny = pts[i - 1]
        dx, dy = x - nx, y - ny
        length = math.hypot(dx, dy) or 1.0
        ux, uy = -dy / length, dx / length     # unit normal
        w = width_fn(t_values[i]) / 2
        ox, oy = offset_fn(t_values[i])
        left.append((x + ux * w + ox, y + uy * w + oy))
        right.append((x - ux * w + ox, y - uy * w + oy))
    return left, right


def draw_wave(img):
    ts = [i / 90 for i in range(91)]
    # main body: draw segment quads with a teal->cyan->magenta gradient
    d = ImageDraw.Draw(img)
    left, right = ribbon(ts, lambda t: sc(lerp(150, 34, t ** 0.8)),
                         lambda t: (0, 0))
    for i in range(len(ts) - 1):
        t = ts[i]
        col = mix(TEAL, CYAN, min(1.0, t * 1.25)) if t < 0.72 \
            else mix(CYAN, MAGENTA, (t - 0.72) / 0.28)
        d.polygon([left[i], right[i], right[i + 1], left[i + 1]], fill=col + (255,))
    # deep shade along the lower edge for volume
    sl, sr = ribbon(ts, lambda t: sc(lerp(60, 10, t)),
                    lambda t: (0, sc(lerp(52, 6, t))))
    for i in range(len(ts) - 1):
        d.polygon([sl[i], sr[i], sr[i + 1], sl[i + 1]], fill=(10, 92, 140, 255))
    # foam: tapered white ribbon hugging the upper edge
    fl, fr = ribbon(ts, lambda t: sc(lerp(40, 7, t ** 0.9)),
                    lambda t: (0, -sc(lerp(52, 12, t))))
    for i in range(len(ts) - 1):
        d.polygon([fl[i], fr[i], fr[i + 1], fl[i + 1]], fill=(245, 252, 255, 255))
    # inner highlight ribbon inside the foam (pale cyan, thinner)
    hl, hr = ribbon(ts, lambda t: sc(lerp(16, 3, t)),
                    lambda t: (0, -sc(lerp(46, 10, t))))
    for i in range(len(ts) - 1):
        d.polygon([hl[i], hr[i], hr[i + 1], hl[i + 1]], fill=(178, 240, 255, 255))
    # rounded cap where the wave leaves the bowl (no flat slide end)
    sx, sy = wave_point(0.0)
    sr = sc(74)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=TEAL + (255,))
    # foam curl cap where the wave breaks into the galaxy
    cx, cy = wave_point(0.985)
    for rr, col in [(sc(37), (245, 252, 255, 255)), (sc(26), (178, 240, 255, 255)),
                    (sc(15), (255, 255, 255, 255))]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    return img


# ---------------------------------------------------------------- galaxy
def draw_galaxy(img):
    gx, gy = sc(758), sc(238)
    # spiral arms: 3 arms, stars beaded along each with jitter
    star_layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(star_layer)
    arm_cols = [(255, 240, 190), (160, 235, 255), (255, 170, 220)]
    for arm in range(3):
        base_ang = arm * (2 * math.pi / 3)
        for i in range(190):
            t = i / 190
            ang = base_ang + t * 4.4
            rad = sc(14 + 228 * t ** 0.92)
            jx = rng.gauss(0, sc(8 + 19 * t))
            jy = rng.gauss(0, sc(8 + 19 * t))
            x = gx + math.cos(ang) * rad + jx
            y = gy + math.sin(ang) * rad * 0.82 + jy
            r = max(1.4, (5.4 - 3.2 * t) * rng.uniform(0.55, 1.3))
            col = arm_cols[arm]
            a = int(lerp(255, 130, t))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
            if rng.random() < 0.06:  # sparkle cross on the brightest
                L = r * 3.4
                d.line([x - L, y, x + L, y], fill=col + (150,), width=max(1, S))
                d.line([x, y - L, x, y + L], fill=col + (150,), width=max(1, S))
    # inter-arm dust: many tiny dim motes filling the disc (not a thin ring)
    for _ in range(1500):
        ang = rng.uniform(0, 2 * math.pi)
        rad = sc(245) * (rng.random() ** 0.6)
        x = gx + math.cos(ang) * rad + rng.gauss(0, sc(6))
        y = gy + math.sin(ang) * rad * 0.82 + rng.gauss(0, sc(6))
        r = rng.uniform(0.8, 2.4)
        col = rng.choice([(190, 200, 255), (255, 205, 235), (170, 230, 255)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (rng.randint(70, 175),))
    img = Image.alpha_composite(img, star_layer)
    # burst: at most 9 rays so it never reads as a firework
    ray_layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ray_layer)
    for k in range(7):
        ang = k * (2 * math.pi / 7) + 0.35
        ln = sc(rng.uniform(64, 118))
        x2 = gx + math.cos(ang) * ln
        y2 = gy + math.sin(ang) * ln
        rd.line([gx, gy, x2, y2], fill=(255, 236, 170, 85), width=int(sc(11)))
    ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(sc(6)))
    img = Image.alpha_composite(img, ray_layer)
    # hot core on its own layer, blurred so no hard disc edge shows
    core = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for rr, a in [(sc(52), 70), (sc(38), 120), (sc(26), 185), (sc(15), 255)]:
        cd.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=(255, 244, 200, a))
    core = core.filter(ImageFilter.GaussianBlur(sc(5)))
    return Image.alpha_composite(img, core)


# ---------------------------------------------------------------- confetti
def draw_confetti(img):
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cols = [ORANGE, MAGENTA, YELLOW, CYAN, (120, 255, 150), (255, 90, 90)]
    for _ in range(120):
        t = rng.random() ** 0.8
        x, y = wave_point(t)
        x += rng.gauss(0, sc(95))
        y += rng.gauss(0, sc(95))
        col = rng.choice(cols) + (235,)
        if rng.random() < 0.5:
            wdt = rng.uniform(sc(7), sc(15))
            hgt = wdt * 0.45
            ang = rng.uniform(0, 180)
            piece = Image.new("RGBA", (int(wdt * 3), int(wdt * 3)), (0, 0, 0, 0))
            pd = ImageDraw.Draw(piece)
            cxp = piece.width / 2
            pd.rectangle([cxp - wdt / 2, cxp - hgt / 2, cxp + wdt / 2, cxp + hgt / 2],
                         fill=col)
            piece = piece.rotate(ang, expand=True, resample=Image.BICUBIC)
            layer.alpha_composite(piece, (int(x - piece.width / 2),
                                          int(y - piece.height / 2)))
        else:
            r = rng.uniform(sc(3), sc(6))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    return Image.alpha_composite(img, layer)


# ---------------------------------------------------------------- fish
def fish_image(length, body=ORANGE, belly=(255, 196, 110), fin=MAGENTA,
               cheer=False):
    """A goldfish drawn pointing right (+x), centred, on a transparent tile."""
    L = length
    H = L * 0.62
    tile = Image.new("RGBA", (int(L * 1.5), int(H * 2.2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    cx, cy = tile.width * 0.56, tile.height / 2
    # tail fin (fan at the back)
    tx = cx - L * 0.42
    d.polygon([(tx + L * 0.10, cy), (tx - L * 0.22, cy - H * 0.46),
               (tx - L * 0.10, cy), (tx - L * 0.22, cy + H * 0.46)],
              fill=fin + (255,))
    # dorsal + pectoral fins
    d.polygon([(cx - L * 0.05, cy - H * 0.30), (cx + L * 0.16, cy - H * 0.52),
               (cx + L * 0.24, cy - H * 0.26)], fill=fin + (255,))
    d.polygon([(cx + L * 0.05, cy + H * 0.18), (cx + L * 0.20, cy + H * 0.44),
               (cx + L * 0.26, cy + H * 0.10)], fill=fin + (230,))
    # body: plump ellipse-ish shape via two arcs approximated by an ellipse
    d.ellipse([cx - L * 0.46, cy - H * 0.36, cx + L * 0.46, cy + H * 0.36],
              fill=body + (255,))
    # snout taper overlay in background-transparent trick: redraw head circle
    d.ellipse([cx + L * 0.10, cy - H * 0.33, cx + L * 0.52, cy + H * 0.33],
              fill=body + (255,))
    # belly sheen: pre-mixed OPAQUE colour — a translucent fill on this
    # transparent tile would replace body pixels and blend with the dark
    # background when composited, turning muddy grey-brown.
    belly_solid = mix(body, belly, 0.55)
    d.ellipse([cx - L * 0.16, cy + H * 0.10, cx + L * 0.26, cy + H * 0.33],
              fill=belly_solid + (255,))
    # eye
    ex, ey = cx + L * 0.30, cy - H * 0.10
    er = H * 0.085
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(20, 16, 40, 255))
    d.ellipse([ex - er * 0.35, ey - er * 0.55, ex + er * 0.25, ey + er * 0.05],
              fill=(255, 255, 255, 255))
    # mouth: open smile (cheering) or a happy open O
    mx, my = cx + L * 0.40, cy + H * 0.13
    mr = H * (0.11 if cheer else 0.085)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(120, 30, 20, 255))
    return tile


def draw_leaping_fish(img):
    # motion arcs first (translucent layer, merged with alpha_composite)
    arcs = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arcs)
    for i, rr in enumerate([sc(120), sc(155), sc(190)]):
        box = [sc(215) - rr, sc(700) - rr, sc(215) + rr, sc(700) + rr]
        ad.arc(box, start=300, end=385, fill=(160, 235, 255, 150 - i * 35),
               width=int(sc(7)))
    img = Image.alpha_composite(img, arcs)
    fish = fish_image(sc(215))
    fish = fish.rotate(38, expand=True, resample=Image.BICUBIC)  # nose up-right
    img.alpha_composite(fish, (int(sc(292)), int(sc(392))))
    return img


# ---------------------------------------------------------------- splash
def draw_splash(img):
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = sc(225), sc(712)
    for _ in range(46):
        ang = rng.uniform(-2.7, -0.45)
        dist = rng.uniform(sc(18), sc(120))
        x = ox + math.cos(ang) * dist
        y = oy + math.sin(ang) * dist * 0.8
        r = rng.uniform(sc(2.5), sc(7.5)) * (1 - dist / sc(150))
        r = max(1.2, r)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(190, 240, 255, 215))
    # burst of foam where the fish left the water
    for rr, a in [(sc(30), 200), (sc(19), 235), (sc(10), 255)]:
        d.ellipse([ox - rr, oy - rr * 0.55, ox + rr, oy + rr * 0.55],
                  fill=(240, 250, 255, a))
    return Image.alpha_composite(img, layer)


# ---------------------------------------------------------------- bowl
def draw_bowl(img):
    d = ImageDraw.Draw(img)
    cx, cy, R = sc(215), sc(838), sc(148)
    # glass body
    d.ellipse([cx - R, cy - R * 0.92, cx + R, cy + R * 0.92],
              fill=(120, 200, 245, 70), outline=(210, 245, 255, 255),
              width=int(sc(6)))
    # water fill (lower two-thirds)
    wy = cy - R * 0.28
    d.chord([cx - R * 0.94, cy - R * 0.86, cx + R * 0.94, cy + R * 0.86],
            start=0, end=180, fill=(30, 130, 210, 210))
    d.rectangle([cx - R * 0.94, wy - sc(2), cx + R * 0.94, wy + sc(3)],
                fill=(30, 130, 210, 210))
    # the little friend inside, cheering (drawn, then re-glassed lightly)
    friend = fish_image(sc(105), cheer=True)
    friend = friend.rotate(18, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(friend, (int(cx - sc(58)), int(cy - sc(6))))
    d = ImageDraw.Draw(img)
    # rim + water line
    d.ellipse([cx - R * 0.97, wy - sc(13), cx + R * 0.97, wy + sc(13)],
              outline=(225, 250, 255, 255), width=int(sc(5)))
    # glass highlight
    d.arc([cx - R * 0.80, cy - R * 0.78, cx + R * 0.30, cy + R * 0.30],
          start=120, end=205, fill=(255, 255, 255, 190), width=int(sc(8)))
    # base shadow
    d.ellipse([cx - R * 0.9, cy + R * 0.86, cx + R * 0.9, cy + R * 1.02],
              fill=(8, 5, 26, 160))
    # bubbles rising inside the bowl (translucent layer)
    bub = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bub)
    for _ in range(16):
        x = cx + rng.uniform(-R * 0.68, -R * 0.05)
        y = cy + rng.uniform(-R * 0.2, R * 0.62)
        r = rng.uniform(sc(3), sc(8))
        bd.ellipse([x - r, y - r, x + r, y + r], outline=(230, 250, 255, 200),
                   width=int(sc(2)))
    return Image.alpha_composite(img, bub)


# ---------------------------------------------------------------- WOW! text
def draw_wow(img):
    size = int(sc(168))
    font = ImageFont.truetype(FONT, size)
    tile = Image.new("RGBA", (int(sc(640)), int(sc(300))), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.text((sc(28), sc(52)), "WOW!", font=font, fill=YELLOW + (255,),
            stroke_width=int(sc(13)), stroke_fill=ORANGE_DK + (255,))
    tile = tile.rotate(11, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tile, (int(sc(96)), int(sc(96))))
    return img


# ---------------------------------------------------------------- main
def main():
    img = make_background()
    img = Image.alpha_composite(img, glow_layer((sc(758), sc(238)), sc(300),
                                                (255, 120, 200), 70))
    img = Image.alpha_composite(img, glow_layer((sc(758), sc(238)), sc(150),
                                                (255, 190, 80), 80))
    img = draw_wave(img)
    img = draw_galaxy(img)
    img = draw_confetti(img)
    img = draw_splash(img)
    img = draw_bowl(img)
    img = draw_leaping_fish(img)
    img = draw_wow(img)
    img = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()

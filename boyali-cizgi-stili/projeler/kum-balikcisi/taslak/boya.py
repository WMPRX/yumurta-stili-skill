"""Kum Balıkçısı taslağı: 2B boyalı çizim motoru (pycairo + numpy + opencv).

Bütün çizimler 1920x1080 koordinatında yapılır; SCALE ile küçük önizleme alınabilir.
Stil kuralları (STIL_KITABI.md): kontur yok, fırça dokulu mat yüzeyler, tek güneş,
gölge yüzeyin tonunu korur, karakter sahnenin en koyu öğesi, göz akı en açığı.
"""
import math
import random
import numpy as np
import cv2
import cairo

W, H = 1920, 1080


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def mul(a, k):
    return tuple(min(1, x * kk) for x, kk in zip(a, k if isinstance(k, (tuple, list)) else (k, k, k)))


CREAM = hexrgb("#eeebd2")
INK = hexrgb("#1a111c")          # en koyu (saf siyah yok)

# ---------------------------------------------------------------- dokular
_TILES = {}


def tile(name, base, kind="yatay", seed=1, size=384, n=700, jit=0.07, wmin=3, wmax=10, lmin=10, lmax=46, alpha=(0.12, 0.32), spots=None):
    """Elle boyanmış görünümlü, kenarları sarmalanan doku karosu (gouache fırça vuruşları)."""
    key = (name, size)
    if key in _TILES:
        return _TILES[key]
    rnd = random.Random(seed)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    c = cairo.Context(s)
    c.set_source_rgb(*base); c.paint()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        if kind == "yatay":
            a = rnd.gauss(0, 0.18)
        elif kind == "dikey":
            a = math.pi / 2 + rnd.gauss(0, 0.25)
        else:
            a = rnd.uniform(0, math.pi)
        L = rnd.uniform(lmin, lmax); w = rnd.uniform(wmin, wmax)
        f = rnd.gauss(1, jit)
        hue = rnd.gauss(0, 0.015)
        col = (min(1, base[0] * f + hue), min(1, base[1] * f), min(1, base[2] * f - hue))
        c.set_source_rgba(*col, rnd.uniform(*alpha))
        c.set_line_width(w)
        x, y = rnd.uniform(0, size), rnd.uniform(0, size)
        dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                c.move_to(x - dx + ox, y - dy + oy); c.line_to(x + dx + ox, y + dy + oy); c.stroke()
    if spots:
        col, cnt, rmin, rmax = spots
        for _ in range(cnt):
            x, y, r = rnd.uniform(0, size), rnd.uniform(0, size), rnd.uniform(rmin, rmax)
            c.set_source_rgba(*col, rnd.uniform(0.35, 0.7))
            for ox in (-size, 0, size):
                for oy in (-size, 0, size):
                    c.save(); c.translate(x + ox, y + oy); c.scale(1, rnd.uniform(0.6, 1)); c.arc(0, 0, r, 0, 2 * math.pi); c.restore(); c.fill()
    s.flush()
    a = np.ndarray((size, size, 4), np.uint8, s.get_data()).copy()
    a = cv2.GaussianBlur(a, (0, 0), 0.9, borderType=cv2.BORDER_WRAP)
    s2 = cairo.ImageSurface.create_for_data(a, cairo.FORMAT_ARGB32, size, size)
    p = cairo.SurfacePattern(s2); p.set_extend(cairo.EXTEND_REPEAT); p.set_filter(cairo.FILTER_GOOD)
    _TILES[key] = (p, a, s2)
    return _TILES[key]


class Mat:
    """Malzeme: taban rengi + doku + gölge/ışık tonu. Gölge tonu korur, değeri ~0,6'ya düşer."""

    def __init__(self, name, base, kind="yatay", seed=1, shade=None, hi=None, tex_scale=1.0, **kw):
        self.name = name
        self.base = hexrgb(base) if isinstance(base, str) else base
        self.shade = hexrgb(shade) if isinstance(shade, str) else (shade or mul(self.base, (0.56, 0.57, 0.64)))
        self.hi = hexrgb(hi) if isinstance(hi, str) else (hi or mix(self.base, CREAM, 0.28))
        self.kind, self.seed, self.tex_scale, self.kw = kind, seed, tex_scale, kw

    @property
    def pattern(self):
        return tile(self.name, self.base, self.kind, self.seed, **self.kw)[0]


M = {}


def mats():
    if M:
        return M
    M.update({
        "gok": Mat("gok", "#78b3b9", "yatay", 2, n=260, jit=0.025, wmin=10, wmax=26, lmin=60, lmax=160, alpha=(0.06, 0.14)),
        "kum": Mat("kum", "#d1b974", "yatay", 3, shade="#786e50", n=900, jit=0.08, spots=(hexrgb("#b89a58"), 60, 1, 3)),
        "kum_gol": Mat("kum_gol", "#e0c98a", "yatay", 4, shade="#8a7c58", n=700, jit=0.05),
        "ova": Mat("ova", "#8ebcb1", "yatay", 5, n=300, jit=0.04, wmin=6, wmax=16, lmin=40, lmax=120),
        "kaya": Mat("kaya", "#bb8180", "dikey", 6, n=500, jit=0.06),
        "cali": Mat("cali", "#9e803b", "rastgele", 7, shade="#5e4b22", n=900, jit=0.12, wmin=4, wmax=9, lmin=6, lmax=16),
        "ten": Mat("ten", "#3b2b37", "rastgele", 8, shade="#1a111c", hi="#4a3844", n=400, jit=0.06, wmin=6, wmax=14),
        "goz": Mat("goz", "#faf4eb", "rastgele", 9, shade="#d9cfc0", hi="#fffdf7", n=80, jit=0.01),
        "sapka": Mat("sapka", "#c9a24a", "yatay", 10, shade="#7a6128", n=900, jit=0.1, wmin=2, wmax=5, lmin=14, lmax=40, alpha=(0.25, 0.5)),
        "bant": Mat("bant", "#9c4c37", "yatay", 11),
        "yelek": Mat("yelek", "#1f5f66", "dikey", 12, shade="#123a40", hi="#2f7680", n=500),
        "gomlek": Mat("gomlek", "#e4e0b2", "dikey", 13, shade="#a59f74", n=400, jit=0.04),
        "atki": Mat("atki", "#7b697c", "rastgele", 14, shade="#4a3d4c"),
        "tulum": Mat("tulum", "#9c4c37", "dikey", 15, shade="#5a2a1f", hi="#b8664a", n=600),
        "eldiven": Mat("eldiven", "#2e2c30", "rastgele", 16, shade="#17151a", hi="#46434a"),
        "bambu": Mat("bambu", "#b89447", "dikey", 17, shade="#6e5527"),
        "samandira": Mat("samandira", "#e07a10", "rastgele", 18, shade="#7b2b19", hi="#f6a640", n=200, jit=0.04),
        "beyaz": Mat("beyaz", "#e8e2cf", "rastgele", 19, shade="#a8a08a"),
        "kova": Mat("kova", "#6f8a87", "dikey", 20, shade="#3c4f4e", hi="#9cb3ae", n=300),
        "bez": Mat("bez", "#e4e0b2", "yatay", 21, shade="#a59f74"),
        "balik": Mat("balik", "#d1b974", "rastgele", 22, shade="#7d6a3f", n=600, spots=(hexrgb("#a68b42"), 70, 4, 11)),
        "yuzgec": Mat("yuzgec", "#9c4c37", "dikey", 23, shade="#5a2a1f"),
        "karin": Mat("karin", "#e4e0b2", "yatay", 24, shade="#b89a7a"),
        "agiz": Mat("agiz", "#4a0f14", "rastgele", 25, shade="#23030c", hi="#7b2b19"),
        "balen": Mat("balen", "#c9a24a", "dikey", 26, shade="#6e5527"),
        "yanak": Mat("yanak", "#ac594f", "rastgele", 27),
    })
    return M


# ---------------------------------------------------------------- yollar
def ellipse(c, cx, cy, rx, ry, rot=0.0):
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(max(rx, 1e-3), max(ry, 1e-3)); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()


def catmull(pts, closed=False, n=10):
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-2])
    return out


def blob(c, pts, n=10):
    q = catmull(pts, True, n)
    c.move_to(*q[0])
    for p in q[1:]:
        c.line_to(*p)
    c.close_path()


def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def tube(c, pts, w0, w1=None, n=8, cap=True):
    """Uçları yuvarlak, kalınlığı w0'dan w1'e inen tüp (dolgu yolu)."""
    w1 = w0 if w1 is None else w1
    q = catmull(pts, False, n) if len(pts) > 2 else [pts[0], pts[1]]
    if len(q) < 2:
        return
    L, R = [], []
    m = len(q)
    for i, p in enumerate(q):
        a = q[max(i - 1, 0)]; b = q[min(i + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / (m - 1)) / 2
        L.append((p[0] + nx * w, p[1] + ny * w)); R.append((p[0] - nx * w, p[1] - ny * w))
    c.move_to(*L[0])
    for p in L[1:]:
        c.line_to(*p)
    if cap:
        p = q[-1]; a0 = math.atan2(L[-1][1] - p[1], L[-1][0] - p[0])
        c.arc_negative(p[0], p[1], w1 / 2, a0, a0 - math.pi) if False else c.arc(p[0], p[1], w1 / 2, a0, a0 + math.pi)
    for p in reversed(R):
        c.line_to(*p)
    if cap:
        p = q[0]; a0 = math.atan2(R[0][1] - p[1], R[0][0] - p[0])
        c.arc(p[0], p[1], w0 / 2, a0, a0 + math.pi)
    c.close_path()


# ---------------------------------------------------------------- dolgu
LIGHT = [0.62, -0.78]     # ışık yönü (ekran), sahne başına değiştirilir


def fill(c, path, mat, shade=0.55, hi=0.35, light=None, tex=1.0, alpha=1.0):
    """Yolu doku + yönlü gölgelendirme ile doldurur (kontur yok)."""
    lx, ly = light or LIGHT
    c.save()
    c.new_path()
    path(c)
    x0, y0, x1, y1 = c.fill_extents()
    c.clip()
    pat = mat.pattern
    m = cairo.Matrix(); m.scale(1 / (tex * mat.tex_scale), 1 / (tex * mat.tex_scale))
    # dokuyu nesne konumuna kilitle
    m.translate(-x0 * 0, 0)
    pat.set_matrix(m)
    if alpha < 1:
        c.push_group()
    c.set_source(pat); c.paint()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = max(math.hypot(x1 - x0, y1 - y0) / 2, 1)
    g = cairo.LinearGradient(cx - lx * r, cy - ly * r, cx + lx * r, cy + ly * r)
    g.add_color_stop_rgba(0.0, *mat.shade, shade)
    g.add_color_stop_rgba(0.48, *mat.shade, 0.0)
    g.add_color_stop_rgba(0.62, *mat.hi, 0.0)
    g.add_color_stop_rgba(1.0, *mat.hi, hi)
    c.set_source(g); c.paint()
    if alpha < 1:
        c.pop_group_to_source(); c.paint_with_alpha(alpha)
    c.restore()


def solid(c, path, rgb, a=1.0):
    c.save(); c.new_path(); path(c); c.set_source_rgba(*rgb, a); c.fill(); c.restore()


# ---------------------------------------------------------------- katmanlar
class Frame:
    """Bir karenin katmanları: arka (bg), orta (karakterler), ön (fg)."""

    def __init__(self, scale=1.0):
        self.s = scale
        self.w, self.h = int(W * scale), int(H * scale)
        self.layers = {}

    def ctx(self, name):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        c = cairo.Context(surf)
        c.scale(self.s, self.s)
        c.set_antialias(cairo.ANTIALIAS_BEST)
        self.layers[name] = surf
        return c

    def arr(self, name):
        s = self.layers[name]; s.flush()
        a = np.ndarray((self.h, self.w, 4), np.uint8, s.get_data()).astype(np.float32) / 255
        # BGRA premultiplied -> RGB premultiplied + alpha
        return a[..., [2, 1, 0]], a[..., 3:4]


def blur(img, sigma):
    if sigma <= 0.3:
        return img
    return cv2.GaussianBlur(img, (0, 0), sigma)


def motion(img, length, ang):
    length = int(max(1, length))
    k = np.zeros((2 * length + 1, 2 * length + 1), np.float32)
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for t in np.linspace(-length, length, 4 * length + 1):
        k[int(round(length + t * dy)), int(round(length + t * dx))] = 1
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_CONSTANT)


def cast(fx, fy, dx=-0.8, dy=0.28):
    """Ayak noktası (fx, fy) etrafında düşen gölge matrisi: güneş arkada-sağda, gölge öne-sola düşer.
    Ekran koordinatında (SCALE'den bağımsız; composite ölçekler)."""
    return [[1, -dx, dx * fy], [0, -dy, (1 + dy) * fy]]


SHADOW_K = np.array([0.58, 0.60, 0.68], np.float32)   # kum ışık -> kum gölge oranı (ölçülen)


def composite(fr, spec):
    """spec: bg_blur, fg_blur, mid_blur, shadows=[(katman, M2x3, opaklık, blur)], mid_motion=(len, ang), bloom.
    Sonuç: uint8 RGB (h, w, 3)."""
    s = fr.s
    bg, _ = fr.arr("bg")
    out = bg.copy()
    for (lname, Mx, op, sb) in spec.get("shadows", []):
        if lname not in fr.layers:
            continue
        _, a = fr.arr(lname)
        Ms = np.array(Mx, np.float32).copy(); Ms[:, 2] *= s
        sh = cv2.warpAffine(a[..., 0], Ms, (fr.w, fr.h), flags=cv2.INTER_LINEAR)
        sh = blur(sh, sb * s)[..., None] * op
        out = out * (1 - sh * (1 - SHADOW_K))
    out = blur(out, spec.get("bg_blur", 0) * s)
    for lname in spec.get("order", ["mid2", "lake", "mid", "fg"]):
        if lname not in fr.layers:
            continue
        rgb, a = fr.arr(lname)
        a = a[..., 0]
        sb = spec.get(lname + "_blur", 0) * s
        if sb > 0.3:
            rgb, a = blur(rgb, sb), blur(a, sb)
        mm = spec.get(lname + "_motion")
        if mm and mm[0] and mm[0] * s >= 1:
            rgb, a = motion(rgb, mm[0] * s, mm[1]), motion(a, mm[0] * s, mm[1])
        d = spec.get(lname + "_dark", 0)
        if d:
            # ters ışık: koyulaştır ama çok parlak pikselleri (göz akı) koru
            lum = (rgb.max(axis=2) / np.maximum(a, 1e-4))
            keep = np.clip((lum - 0.82) / 0.1, 0, 1)
            dd = (d * (1 - keep))[..., None]
            rgb = rgb * (1 - dd) + a[..., None] * np.array([0.11, 0.08, 0.11], np.float32) * dd
        out = rgb + out * (1 - a[..., None])
    # ışık halesi (yalnız güneş gibi parlak kaynaklar)
    lum = out.max(axis=2)
    br = np.clip((lum - 0.95) / 0.05, 0, 1)[..., None] * out
    if br.max() > 0:
        out = out + blur(br, 60 * s) * spec.get("bloom", 0.5) + blur(br, 18 * s) * 0.25
    # vektör sertliğini kır: çok hafif yumuşatma (boya hissi)
    out = blur(out, 0.55 * s)
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


# ---------------------------------------------------------------- dünya
def sky(c, horizon, sun=None, top="#6aa8b1", bottom="#93c2c1"):
    g = cairo.LinearGradient(0, 0, 0, horizon)
    g.add_color_stop_rgb(0, *hexrgb(top)); g.add_color_stop_rgb(1, *hexrgb(bottom))
    c.rectangle(0, 0, W, horizon + 4); c.set_source(g); c.fill()
    # boyalı gök: çok hafif yatay fırça
    c.save(); c.rectangle(0, 0, W, horizon + 4); c.clip(); c.set_source(mats()["gok"].pattern); c.paint_with_alpha(0.35); c.restore()
    if sun:
        sx, sy, sr = sun
        for r, a in ((sr * 5.5, 0.18), (sr * 3.0, 0.28), (sr * 1.7, 0.45)):
            rg = cairo.RadialGradient(sx, sy, sr * 0.6, sx, sy, r)
            rg.add_color_stop_rgba(0, *hexrgb("#f3efd6"), a); rg.add_color_stop_rgba(1, *hexrgb("#f3efd6"), 0)
            c.rectangle(0, 0, W, H); c.set_source(rg); c.fill()
        c.arc(sx, sy, sr, 0, 2 * math.pi); c.set_source_rgb(*hexrgb("#fdfef4")); c.fill()


def mesas(c, horizon, x0=0, scale=1.0, seed=3, side=None):
    rnd = random.Random(seed)
    x = x0
    while x < W + 200:
        w = rnd.uniform(90, 260) * scale; h = rnd.uniform(25, 75) * scale
        if side is None or (side == "sol" and x < W * 0.45) or (side == "sag" and x > W * 0.55):
            pts = [(x, horizon + 2), (x + w * 0.12, horizon - h * 0.9), (x + w * 0.2, horizon - h), (x + w * 0.75, horizon - h * rnd.uniform(0.85, 1)),
                   (x + w * 0.85, horizon - h * 0.6), (x + w, horizon + 2)]
            fill(c, lambda cc, p=pts: poly(cc, p), mats()["kaya"], shade=0.35, hi=0.2, light=(0.7, -0.7))
            # atmosfer: göğe karışsın
            solid(c, lambda cc, p=pts: poly(cc, p), hexrgb("#9cc6c3"), 0.35)
        x += w + rnd.uniform(60, 420) * scale


def ground(c, horizon, far_band=60):
    # uzak ova (teal-yeşil köprü) -> kum
    c.save(); c.rectangle(0, horizon, W, H - horizon); c.clip()
    c.set_source(mats()["kum"].pattern); c.paint()
    g = cairo.LinearGradient(0, horizon, 0, horizon + far_band * 2.2)
    g.add_color_stop_rgba(0, *hexrgb("#8ebcb1"), 1); g.add_color_stop_rgba(0.45, *hexrgb("#a9c1a2"), 0.75); g.add_color_stop_rgba(1, *hexrgb("#d1b974"), 0)
    c.set_source(g); c.paint()
    # yakına doğru biraz daha sıcak ve koyu
    g = cairo.LinearGradient(0, horizon, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, *hexrgb("#786e50"), 0.42)
    c.set_source(g); c.paint()
    c.restore()


def scatter(c, horizon, seed=5, n_tuft=40, n_flower=26, y0=None, y1=H, x0=0, x1=W, avoid=None, near=1.0):
    """Ot tutamları ve lila çiçekler; ufka yaklaştıkça küçülür."""
    rnd = random.Random(seed)
    y0 = y0 or horizon + 8
    items = []
    for _ in range(n_tuft):
        items.append(("t", rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.random()))
    for _ in range(n_flower):
        items.append(("f", rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.random()))
    items.sort(key=lambda it: it[2])
    for kind, x, y, r in items:
        if avoid and avoid(x, y):
            continue
        k = ((y - horizon) / max(H - horizon, 1)) ** 1.1 * near + 0.08
        if kind == "t":
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            for j in range(7):
                a = -math.pi / 2 + (j - 3) * 0.28 + (r - 0.5) * 0.3
                L = (22 + 18 * ((j * 37 + int(r * 100)) % 5) / 5) * k
                c.set_source_rgba(*mix(hexrgb("#9e803b"), hexrgb("#c9a24a"), (j % 3) / 3), 0.9)
                c.set_line_width(max(1.2, 4.2 * k))
                c.move_to(x + (j - 3) * 3 * k, y); c.curve_to(x + (j - 3) * 3 * k, y - L * 0.5, x + math.cos(a) * L * 0.8, y + math.sin(a) * L * 0.8, x + math.cos(a) * L, y + math.sin(a) * L); c.stroke()
        else:
            pr = 13 * k
            col = mix(hexrgb("#d3afc9"), hexrgb("#e6c8d8"), r)
            for j in range(5):
                a = j * 2 * math.pi / 5 + r
                ellipse(c, x + math.cos(a) * pr * 0.8, y + math.sin(a) * pr * 0.45, pr * 0.75, pr * 0.42, a)
                c.set_source_rgba(*col, 0.95); c.fill()
            ellipse(c, x, y, pr * 0.35, pr * 0.22); c.set_source_rgba(*hexrgb("#a98aa6"), 1); c.fill()


def sand_lake(c, cx, cy, rx, ry):
    m = mats()
    # kenar (biraz koyu) + iç (açık ince kum) + halka dalgalar
    fill(c, lambda cc: ellipse(cc, cx, cy + ry * 0.04, rx * 1.04, ry * 1.08), m["kum"], shade=0.5, hi=0.0, light=(0, -1))
    c.save(); ellipse(c, cx, cy, rx, ry); c.clip()
    c.set_source(m["kum_gol"].pattern); c.paint()
    g = cairo.LinearGradient(0, cy - ry, 0, cy + ry)
    g.add_color_stop_rgba(0, *hexrgb("#8a7c58"), 0.35); g.add_color_stop_rgba(0.35, *hexrgb("#8a7c58"), 0.0); g.add_color_stop_rgba(1, *hexrgb("#f1e2a8"), 0.25)
    c.rectangle(cx - rx, cy - ry, 2 * rx, 2 * ry); c.set_source(g); c.fill()
    c.restore()


def ripples(c, cx, cy, rx, ry, n=6, phase=0.0, a=0.45, clip=None):
    c.save()
    if clip:
        clip(c); c.clip()
    for i in range(n):
        k = ((i + phase) % n + 0.6) / n
        c.set_line_width(max(1.5, 5 * k * (ry / 120)))
        ellipse(c, cx, cy, rx * k, ry * k)
        c.set_source_rgba(*hexrgb("#a8925f"), a * (1 - k * 0.5)); c.stroke_preserve()
        c.set_line_width(max(1, 3 * k * (ry / 120)))
        c.save(); c.translate(0, -2.5 * k * (ry / 120)); c.new_path(); ellipse(c, cx, cy, rx * k, ry * k); c.set_source_rgba(*hexrgb("#f4e6b4"), a * 0.8); c.stroke(); c.restore()
        c.new_path()
    c.restore()


def bush_dune(c, cx, base, w, h, seed=9, grass=True):
    """Yuvarlak kum tepesi (balinanın gömülü sırtı)."""
    m = mats()
    pts = [(cx - w / 2, base + 4), (cx - w * 0.42, base - h * 0.45), (cx - w * 0.22, base - h * 0.92), (cx + w * 0.05, base - h),
           (cx + w * 0.3, base - h * 0.85), (cx + w * 0.46, base - h * 0.4), (cx + w / 2, base + 4), (cx, base + h * 0.06)]
    fill(c, lambda cc: blob(cc, pts), m["kum"], shade=0.6, hi=0.3)
    if grass:
        rnd = random.Random(seed)
        for _ in range(int(w / 30)):
            u = rnd.uniform(-0.4, 0.4)
            top = base - h * max(0.05, (1 - (u / 0.5) ** 2)) ** 0.6
            x = cx + u * w; y = top + rnd.uniform(6, (base - top) * 0.7)
            scatter_one(c, x, y, rnd.random(), k=h / 330, flower=rnd.random() < 0.35)


def scatter_one(c, x, y, r, k=1.0, flower=False):
    if not flower:
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for j in range(7):
            a = -math.pi / 2 + (j - 3) * 0.3 + (r - 0.5) * 0.3
            L = (26 + 16 * ((j * 37 + int(r * 100)) % 5) / 5) * k
            c.set_source_rgba(*mix(hexrgb("#9e803b"), hexrgb("#c9a24a"), (j % 3) / 3), 0.95)
            c.set_line_width(max(1.2, 4.5 * k))
            c.move_to(x + (j - 3) * 3 * k, y); c.curve_to(x, y - L * 0.5, x + math.cos(a) * L * 0.8, y + math.sin(a) * L * 0.8, x + math.cos(a) * L, y + math.sin(a) * L); c.stroke()
    else:
        pr = 14 * k
        for j in range(5):
            a = j * 2 * math.pi / 5 + r
            ellipse(c, x + math.cos(a) * pr * 0.8, y + math.sin(a) * pr * 0.45, pr * 0.75, pr * 0.42, a)
            c.set_source_rgba(*hexrgb("#d3afc9"), 0.95); c.fill()
        ellipse(c, x, y, pr * 0.35, pr * 0.22); c.set_source_rgba(*hexrgb("#a98aa6"), 1); c.fill()


def particles(c, items, rgb=None, alpha=0.85):
    """items: (x, y, r, [dx, dy]) — kum taneleri; dx,dy verilirse hareket çizgisi."""
    rgb = rgb or hexrgb("#d9c07a")
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for it in items:
        x, y, r = it[:3]
        if len(it) > 3 and (abs(it[3]) + abs(it[4])) > 1:
            c.set_line_width(r * 2); c.move_to(x - it[3], y - it[4]); c.line_to(x, y)
            c.set_source_rgba(*rgb, alpha * 0.8); c.stroke()
        else:
            c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgba(*rgb, alpha); c.fill()


# ---------------------------------------------------------------- nesneler
def float_(c, x, y, r, sink=0.0, glint=0.0, clip_y=None, tilt=0.0):
    """Şamandıra: üst turuncu, alt krem, tepede çubuk. sink 0..1 kuma batma."""
    m = mats()
    c.save()
    if clip_y is not None:
        c.rectangle(-5000, -5000, 12000, clip_y + 5000); c.clip()
    c.translate(x, y + sink * r * 2.2); c.rotate(tilt)
    # çubuk
    fill(c, lambda cc: tube(cc, [(0, -r * 0.8), (0, -r * 1.75)], r * 0.16, r * 0.1), m["samandira"], shade=0.4, hi=0.2)
    fill(c, lambda cc: ellipse(cc, 0, r * 0.18, r * 0.92, r * 0.85), m["beyaz"], shade=0.6, hi=0.2)
    fill(c, lambda cc: (cc.arc(0, 0, r, math.pi * 1.0, math.pi * 2.0), cc.close_path()), m["samandira"], shade=0.55, hi=0.45)
    fill(c, lambda cc: ellipse(cc, 0, 0, r, r * 0.16), m["samandira"], shade=0.3, hi=0.1)
    # parlama noktası
    ellipse(c, r * 0.35, -r * 0.55, r * 0.17, r * 0.11, -0.5); c.set_source_rgba(*hexrgb("#fff1d6"), 0.85); c.fill()
    c.restore()
    if glint > 0:
        star(c, x + r * 0.35, y - r * 0.6, r * 0.9 * glint)


def star(c, x, y, s):
    c.save(); c.translate(x, y)
    c.move_to(0, -s)
    for a, rr in ((0.5, 0.13), (1, 1), (1.5, 0.13), (2, 1), (2.5, 0.13), (3, 1), (3.5, 0.13), (4, 1)):
        ang = -math.pi / 2 + a * math.pi / 2
        c.line_to(math.cos(ang) * s * rr, math.sin(ang) * s * rr)
    c.close_path(); c.set_source_rgba(*hexrgb("#fffbea"), 0.95); c.fill()
    c.restore()


def bucket(c, x, y, s, tilt=0.0, fish_peek=0.0, t=0.0, upside=False):
    """Teneke kova; (x, y) taban ortası; s yükseklik."""
    m = mats()
    c.save(); c.translate(x, y); c.rotate(tilt)
    if upside:
        c.scale(1, -1); c.translate(0, s)
    wt, wb = s * 0.46, s * 0.36
    body = [(-wb, 0), (-wt, -s), (wt, -s), (wb, 0)]
    fill(c, lambda cc: (ellipse(cc, 0, 0, wb, wb * 0.25), ), m["kova"], shade=0.6)
    fill(c, lambda cc: poly(cc, body), m["kova"], shade=0.6, hi=0.4, light=(0.8, -0.3))
    for k in (0.3, 0.62):
        w = wb + (wt - wb) * k
        c.set_line_width(s * 0.025); ellipse(c, 0, -s * k, w, w * 0.22); c.set_source_rgba(*hexrgb("#3c4f4e"), 0.35)
        c.save(); c.rectangle(-w * 1.2, -s * k, w * 2.4, s); c.clip(); c.stroke(); c.restore(); c.new_path()
    if not upside:
        fill(c, lambda cc: ellipse(cc, 0, -s, wt, wt * 0.24), m["kova"], shade=0.2, hi=0.5, light=(0, -1))
        fill(c, lambda cc: ellipse(cc, 0, -s + wt * 0.03, wt * 0.88, wt * 0.19), mats()["eldiven"], shade=0.0, hi=0.0)
        if fish_peek > 0:
            c.save(); ellipse(c, 0, -s + wt * 0.03, wt * 0.88, wt * 0.19); c.rectangle(-wt, -s * 3, wt * 2, s * 2 + wt * 0.03); c.clip()
            fish(c, 0, -s - fish_peek * s * 0.25, s * 0.9, ang=-1.3, t=t, flap=1)
            c.restore()
        c.set_line_width(s * 0.035); c.set_source_rgba(*hexrgb("#4d5f5d"), 1)
        c.arc(0, -s, wt * 0.95, math.pi * 1.05, math.pi * 1.95); c.stroke()
    c.restore()


def stool(c, x, y, s, tilt=0.0):
    m = mats()
    c.save(); c.translate(x, y); c.rotate(tilt)
    for dx, d2 in ((-0.35, 0.3), (0.35, -0.3), (0.05, 0.0)):
        fill(c, lambda cc, a=dx, b=d2: tube(cc, [(a * s, 0), (b * s, -s * 0.8)], s * 0.06), m["bambu"], shade=0.5)
    fill(c, lambda cc: blob(cc, [(-s * 0.42, -s * 0.84), (0, -s * 0.76), (s * 0.42, -s * 0.84), (s * 0.4, -s * 0.94), (0, -s * 0.9), (-s * 0.4, -s * 0.94)], 6), m["bez"], shade=0.4, hi=0.3)
    c.restore()


def rod_points(hand, angle, length, bend):
    """Olta eğrisi: el noktasından açıyla; bend >0 ucu aşağı büker."""
    pts = []
    for i in range(9):
        u = i / 8
        a = angle + bend * u * u
        if i == 0:
            p = hand
        else:
            prev = pts[-1]
            p = (prev[0] + math.cos(a) * length / 8, prev[1] + math.sin(a) * length / 8)
        pts.append(p)
    return pts


def rod(c, pts, w):
    m = mats()
    fill(c, lambda cc: tube(cc, pts, w, w * 0.25), m["bambu"], shade=0.5, hi=0.4)
    # boğumlar
    c.set_line_width(w * 0.35); c.set_source_rgba(*hexrgb("#6e5527"), 0.6)
    for p in pts[2:-1:2]:
        c.arc(p[0], p[1], w * 0.35, 0, 2 * math.pi); c.fill()
    # makara
    fill(c, lambda cc: ellipse(cc, pts[1][0], pts[1][1] + w * 0.9, w * 0.9, w * 0.9), mats()["sapka"], shade=0.5, hi=0.6)


def line(c, a, b, sag=0.0, w=2.2):
    c.set_line_width(w); c.set_source_rgba(*hexrgb("#efe9d2"), 0.85)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag
    c.move_to(*a); c.curve_to(mx, my, mx, my, *b); c.stroke()


def fish(c, x, y, L, ang=0.0, t=0.0, flap=1.0, mouth="kapali", flip=False, curl=0.0):
    """Küçük kum balığı. (x, y) gövde merkezi, L boy. curl: kıvrılma (final)."""
    m = mats()
    c.save(); c.translate(x, y); c.rotate(ang)
    if flip:
        c.scale(-1, 1)
    c.scale(L, L)
    wag = math.sin(t * 22) * 0.35 * flap
    # kuyruk
    c.save(); c.translate(-0.42, 0); c.rotate(wag + curl)
    fill(c, lambda cc: blob(cc, [(0.02, 0), (-0.2, -0.17), (-0.26, -0.12), (-0.18, 0), (-0.26, 0.12), (-0.2, 0.17)], 6), m["yuzgec"], shade=0.4)
    c.restore()
    body = [(-0.45, 0), (-0.3, -0.17), (0.0, -0.23), (0.3, -0.2), (0.5, -0.06), (0.52, 0.04), (0.3, 0.18), (0.0, 0.22), (-0.3, 0.15)]
    # yüzgeç saçağı
    fill(c, lambda cc: blob(cc, [(p[0] * 1.06, p[1] * 1.35) for p in body], 6), m["yuzgec"], shade=0.5)
    fill(c, lambda cc: blob(cc, body, 8), m["balik"], shade=0.55, hi=0.3)
    fill(c, lambda cc: blob(cc, [(-0.3, 0.1), (0.0, 0.15), (0.3, 0.12), (0.42, 0.05), (0.2, 0.2), (-0.1, 0.2)], 6), m["karin"], shade=0.2, hi=0.2)
    # ağız
    if mouth == "acik":
        fill(c, lambda cc: ellipse(cc, 0.47, 0.05, 0.09, 0.08), m["agiz"], shade=0.3)
        for k in range(4):
            c.move_to(0.42 + k * 0.025, 0.0); c.line_to(0.43 + k * 0.025, 0.03); c.line_to(0.44 + k * 0.025, 0.0)
            c.set_source_rgb(*hexrgb("#efe6cf")); c.fill()
    else:
        c.set_line_width(0.025); c.set_source_rgb(*INK)
        c.move_to(0.36, 0.08); c.curve_to(0.42, 0.04, 0.47, 0.05, 0.51, 0.09); c.stroke()
    # gözler (üstte iki küçük disk)
    for ex, ey in ((0.2, -0.14), (0.31, -0.1)):
        fill(c, lambda cc, a=ex, b=ey: ellipse(cc, a, b, 0.075, 0.075), m["goz"], shade=0.3, hi=0.1)
        c.set_line_width(0.018); ellipse(c, ex, ey, 0.075, 0.075); c.set_source_rgba(*INK, 0.9); c.stroke()
        c.arc(ex + 0.02, ey + 0.01, 0.018, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        # huysuz kaş
        c.set_line_width(0.03); c.move_to(ex - 0.07, ey - 0.1); c.line_to(ex + 0.07, ey - 0.06); c.set_source_rgba(*hexrgb("#5a2a1f"), 1); c.stroke()
    c.restore()


def whale(c, cx, base, w, rise, eye=0.0, mouth=0.0, t=0.0, line_to=None, emerge_clip=True):
    """Kum balinası. rise 0 (tepe) .. 1 (tam yükselmiş). cx gövde merkezi, base zemin çizgisi.
    Ağız sağa (balıkçıya) bakar."""
    m = mats()
    h0, h1 = w * 0.32, w * 0.62
    h = h0 + (h1 - h0) * rise
    c.save()
    if emerge_clip:
        c.rectangle(-9000, -9000, 20000, base + 9000 + 6); c.clip()
    lift = rise * w * 0.12
    # gövde: arka sırt (kum), ön alt karın (krem oluklu), sağda ağız
    back = [(cx - w * 0.55, base + 10), (cx - w * 0.45, base - h * 0.55 - lift * 0.4), (cx - w * 0.2, base - h * 0.95 - lift),
            (cx + w * 0.12, base - h - lift), (cx + w * 0.38, base - h * 0.8 - lift), (cx + w * 0.55, base - h * 0.42 - lift * 0.8),
            (cx + w * 0.6, base - h * 0.1 - lift * 0.5), (cx + w * 0.5, base + 10)]
    fill(c, lambda cc: blob(cc, back, 10), m["kum"], shade=0.65, hi=0.3)
    if rise > 0.05:
        # karın bandı
        bl = [(cx - w * 0.45, base + 8), (cx - w * 0.2, base - h * 0.18 * rise - lift * 0.2), (cx + w * 0.3, base - h * 0.22 * rise - lift * 0.5),
              (cx + w * 0.56, base - h * 0.08 - lift * 0.5), (cx + w * 0.5, base + 12)]
        fill(c, lambda cc: blob(cc, bl, 8), m["karin"], shade=0.45, hi=0.2, alpha=min(1, rise * 1.6))
        c.save(); blob(c, bl, 8); c.clip()
        c.set_line_width(w * 0.008); c.set_source_rgba(*hexrgb("#ac594f"), 0.55 * min(1, rise * 1.6))
        for k in range(7):
            yy = base - h * 0.03 * k * rise - lift * 0.3
            c.move_to(cx - w * 0.45, yy + 6); c.curve_to(cx, yy - h * 0.06 * rise, cx + w * 0.3, yy - h * 0.04, cx + w * 0.6, yy - lift * 0.2); c.stroke()
        c.restore()
    # ağız (sağ uçta kama)
    if mouth > 0.02:
        mx, my = cx + w * 0.5, base - h * 0.32 - lift * 0.65
        op = mouth * h * 0.35
        mp = [(mx + w * 0.1, my - op * 0.2), (mx - w * 0.28, my - op * 0.15), (mx - w * 0.3, my + op * 0.1), (mx + w * 0.1, my + op * 0.8)]
        fill(c, lambda cc: blob(cc, mp, 6), m["agiz"], shade=0.6, hi=0.2)
        c.save(); blob(c, mp, 6); c.clip()
        c.set_line_width(w * 0.006); c.set_source_rgba(*hexrgb("#c9a24a"), 0.9)
        for k in range(14):
            xx = mx - w * 0.27 + k * w * 0.026
            c.move_to(xx, my - op * 0.25); c.line_to(xx + w * 0.004, my - op * 0.25 + op * 0.35); c.stroke()
        c.restore()
    # göz (küçük, uykulu)
    ex, ey = cx + w * 0.3, base - h * 0.55 - lift * 0.85
    er = w * 0.028
    if eye > 0.01:
        fill(c, lambda cc: ellipse(cc, ex, ey, er, er), m["goz"], shade=0.3, hi=0.1)
        c.arc(ex - er * 0.15, ey + er * 0.1, er * 0.22, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
    # ağır göz kapağı
    lid = 1 - eye
    c.save(); ellipse(c, ex, ey, er * 1.05, er * 1.05); c.clip()
    c.rectangle(ex - er * 2, ey - er * 2, er * 4, er * (1 + 2 * lid * 0.95))
    c.set_source_rgb(*hexrgb("#8a7444")); c.fill(); c.restore()
    c.set_line_width(er * 0.35); c.set_source_rgba(*hexrgb("#5e4b22"), 0.9)
    c.arc(ex, ey, er * 1.05, math.pi * 1.05, math.pi * 1.95); c.stroke()
    # sırtta ot ve çiçekler
    rnd = random.Random(11)
    for _ in range(10):
        u = rnd.uniform(-0.42, 0.45)
        top = base - h * max(0.05, (1 - ((u - 0.0) / 0.6) ** 2)) - lift
        scatter_one(c, cx + u * w, top + rnd.uniform(12, 50) * w / 1000, rnd.random(), k=w / 1100, flower=rnd.random() < 0.4)
    c.restore()
    if line_to:
        return (cx + w * 0.56, base - h * 0.3 - lift * 0.6)
    return (ex, ey)


def tail(c, x, base, s, up, t=0.0):
    """Balina kuyruğu: up 0..1 kumdan çıkma."""
    m = mats()
    c.save(); c.rectangle(-9000, -9000, 20000, base + 9000); c.clip()
    c.translate(x, base + s * (1 - up) * 1.2)
    c.rotate(math.sin(t * 3) * 0.06)
    stem = [(-s * 0.12, s * 0.2), (-s * 0.09, -s * 0.5), (s * 0.09, -s * 0.5), (s * 0.12, s * 0.2)]
    fill(c, lambda cc: poly(cc, stem), m["kum"], shade=0.6)
    fl = [(0, -s * 0.48), (-s * 0.25, -s * 0.62), (-s * 0.55, -s * 0.95), (-s * 0.3, -s * 0.88), (0, -s * 0.7), (s * 0.3, -s * 0.88), (s * 0.55, -s * 0.95), (s * 0.25, -s * 0.62)]
    fill(c, lambda cc: blob(cc, fl, 8), m["kum"], shade=0.6, hi=0.35)
    fill(c, lambda cc: blob(cc, [(0, -s * 0.5), (-s * 0.25, -s * 0.6), (s * 0.25, -s * 0.6)], 6), m["karin"], shade=0.3, alpha=0.6)
    c.restore()

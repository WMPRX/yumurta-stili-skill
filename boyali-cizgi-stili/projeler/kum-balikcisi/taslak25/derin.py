"""Kum Balıkçısı 2.5D motoru.

Dünya: X sağ, Y yukarı, Z ileri (metre). Zemin Y=0 düzlemi.
- Kamera: konum + yaw/pitch + dikey görüş açısı; gerçek perspektif ve paralaks.
- Gök: her pikselin bakış yüksekliğine göre gradyan; güneş diski ve halesi güneş yönünden izdüşer.
- Zemin: piksel başına ışın-düzlem kesişimi; dünyaya sabit boyalı kum dokusu (mip seviyeli),
  büyük ölçekli renk lekeleri, analitik kum gölü ve halka dalgaları, uzaklık pusu.
- Nesneler: 2B çizilmiş kartlar (boya.py / tikir.py) dünyada konumlanır, derinliğe göre ölçeklenir.
- Hacimli ışık: her parçanın kimlik tamponundan uzaklık dönüşümü -> şişirilmiş yükseklik -> normal;
  güneş (Lambert) + gök dolgusu + kum yansıması + ters ışıkta kenar ışığı.
- Gölgeler: kart alfası güneş yönünde zemine homografiyle izdüşer; gölge yüzey tonunu korur.
- Alan derinliği: derinliğe bağlı bulanıklık (zemin piksel başına, kartlar nesne başına).
"""
import math
import os
import sys
import numpy as np
import cv2
import cairo
from scipy import ndimage

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "taslak"))
import boya as B  # noqa: E402

W, H = B.W, B.H


def v3(*a):
    return np.array(a, np.float64)


def wblur(img, sigma):
    """Kenarları sarmalayan Gauss bulanıklığı (karo dokular için)."""
    h, w = img.shape[:2]
    big = np.tile(img, (3, 3) + ((1,) if img.ndim == 3 else ()))
    big = cv2.GaussianBlur(big, (0, 0), sigma)
    return big[h:2 * h, w:2 * w].copy()


def norm(v):
    return v / (np.linalg.norm(v) + 1e-12)


# ------------------------------------------------------------ kamera
class Cam:
    def __init__(self, pos, target=None, yaw=0.0, pitch=0.0, fov=42.0, scale=1.0):
        self.C = v3(*pos)
        if target is not None:
            d = v3(*target) - self.C
            yaw = math.atan2(d[0], d[2]); pitch = math.atan2(d[1], math.hypot(d[0], d[2]))
        self.yaw, self.pitch, self.fov, self.s = yaw, pitch, fov, scale
        cp, sp, cy, sy = math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
        self.f = v3(sy * cp, sp, cy * cp)
        self.r = v3(cy, 0, -sy)
        self.u = np.cross(self.f, self.r)
        self.F = (H / 2) / math.tan(math.radians(fov) / 2)
        self.cx, self.cy = W / 2, H / 2

    def proj(self, P):
        d = v3(*P) - self.C
        z = float(d @ self.f)
        z = max(z, 1e-3)
        return (self.cx + self.F * float(d @ self.r) / z, self.cy - self.F * float(d @ self.u) / z, z)

    def px(self, meters, z):
        return self.F * meters / max(z, 1e-3)

    def dir_cam(self, D):
        """Dünya yönünü görünüm çerçevesine çevir: (sağ, yukarı, izleyiciye doğru)."""
        D = norm(v3(*D)); return np.array([D @ self.r, D @ self.u, -(D @ self.f)])

    def rays(self, scale):
        w, h = int(W * scale), int(H * scale)
        uu, vv = np.meshgrid((np.arange(w) + 0.5) / scale, (np.arange(h) + 0.5) / scale)
        a = (uu - self.cx) / self.F; b = (vv - self.cy) / self.F
        d = self.f[None, None, :] + a[..., None] * self.r[None, None, :] - b[..., None] * self.u[None, None, :]
        return d   # normalize edilmemiş; d·f = 1


def lerp_cam(a, b, u):
    """Kamera anahtarları: dict(pos, target, fov)."""
    return dict(pos=tuple(x + (y - x) * u for x, y in zip(a["pos"], b["pos"])),
                target=tuple(x + (y - x) * u for x, y in zip(a["target"], b["target"])),
                fov=a.get("fov", 42) + (b.get("fov", 42) - a.get("fov", 42)) * u)


# ------------------------------------------------------------ ortam
SUN_COL = np.array([1.0, 0.95, 0.84], np.float32)
SKY_COL = np.array([0.74, 0.90, 0.95], np.float32)
BOUNCE_COL = np.array([1.0, 0.86, 0.62], np.float32)
HAZE = np.array(B.hexrgb("#9cc4bf"), np.float32)
SKY_TOP = np.array(B.hexrgb("#62a2ad"), np.float32)
SKY_HOR = np.array(B.hexrgb("#9cc8c4"), np.float32)


class World:
    def __init__(self, sun_dir=(0.42, 0.72, 0.55), lake=(-2.6, 14.0, 4.6, 2.9)):
        self.L = norm(v3(*sun_dir))          # güneşe doğru
        self.lake = lake                     # (cx, cz, rx, rz)
        self._tex()

    def _tex(self):
        m = B.mats()
        tile = B.tile("kum", m["kum"].base, "yatay", 3, n=900, jit=0.08, spots=(B.hexrgb("#b89a58"), 60, 1, 3))[1]
        rgb = tile[..., [2, 1, 0]].astype(np.float32) / 255
        self.tex_m = 2.4                     # karo = 2.4 m
        self.mip = [rgb] + [wblur(rgb, s) for s in (1.5, 4, 10, 24)]
        lt = B.tile("kum_gol", m["kum_gol"].base, "yatay", 4, n=700, jit=0.05)[1]
        lrgb = lt[..., [2, 1, 0]].astype(np.float32) / 255
        self.lmip = [lrgb] + [wblur(lrgb, s) for s in (1.5, 4, 10, 24)]
        rng = np.random.default_rng(4)
        n = rng.random((32, 32)).astype(np.float32)
        self.patch = cv2.resize(wblur(n, 1.2), (256, 256), interpolation=cv2.INTER_CUBIC)
        self.patch = (self.patch - self.patch.mean()) / (self.patch.std() + 1e-6)
        self.patch_m = 40.0                  # leke karosu = 40 m

    # -------------------------------------------------------- gök
    def sky(self, cam, scale, sun_disc=None):
        d = cam.rays(scale)
        dn = d / np.linalg.norm(d, axis=2, keepdims=True)
        el = np.clip(dn[..., 1], -0.2, 1)
        t = np.clip(el / 0.55, 0, 1) ** 0.7
        img = SKY_HOR[None, None] * (1 - t[..., None]) + SKY_TOP[None, None] * t[..., None]
        # boyalı gök: çok hafif yatay fırça (kamera yönüne kilitli dokudan kaçınmak için açıdan örnekle)
        gk = B.tile("gok", B.mats()["gok"].base, "yatay", 2, n=260, jit=0.025, wmin=10, wmax=26, lmin=60, lmax=160, alpha=(0.06, 0.14))[1]
        g = gk[..., [2, 1, 0]].astype(np.float32) / 255
        az = np.arctan2(dn[..., 0], dn[..., 2])
        mx = ((az / (2 * np.pi)) * 6 * g.shape[1]) % g.shape[1]
        my = ((el + 0.2) * 3 * g.shape[0]) % g.shape[0]
        gs = cv2.remap(g, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        img = img * (0.93 + 0.07 * gs / gs.mean(axis=(0, 1), keepdims=True))
        # güneş halesi + disk
        Ls = v3(*(sun_disc if sun_disc is not None else self.L)); Ls = norm(Ls)
        cosang = np.clip((dn @ Ls.astype(np.float32)), -1, 1)
        ang = np.degrees(np.arccos(cosang))
        halo = 0.55 * np.exp(-(ang / 9) ** 2) + 0.25 * np.exp(-(ang / 22) ** 2) + 0.1 * np.exp(-(ang / 45) ** 2)
        cream = np.array(B.hexrgb("#f3efd6"), np.float32)
        img = img * (1 - halo[..., None] * 0.8) + cream * halo[..., None] * 0.8
        disc = np.clip((4.2 - ang) / 0.25, 0, 1)
        img = img * (1 - disc[..., None]) + np.array(B.hexrgb("#fdfef4"), np.float32) * disc[..., None]
        return img.astype(np.float32), el

    # -------------------------------------------------------- zemin
    def ground(self, cam, scale, t=0.0, ripple_phase=0.0, lake_on=True):
        d = cam.rays(scale)
        dy = d[..., 1]
        below = dy < -1e-4
        tt = np.where(below, -cam.C[1] / np.where(below, dy, -1), 1e6)
        X = cam.C[0] + tt * d[..., 0]; Z = cam.C[2] + tt * d[..., 2]
        depth = tt                          # d·f = 1 olduğu için z_c = t
        # doku: mip seviyesini piksel ayak izine göre seç
        ts = self.mip[0].shape[0]
        foot = depth / cam.F / scale        # m/piksel
        tpp = foot * ts / self.tex_m        # piksel başına texel
        mx = ((X / self.tex_m) * ts) % ts; mz = ((Z / self.tex_m) * ts) % ts
        mx = mx.astype(np.float32); mz = mz.astype(np.float32)
        lvl = np.clip(np.log2(np.maximum(tpp, 1e-3)) * 0.9, 0, len(self.mip) - 1.001)
        base = self._mip_sample(self.mip, mx, mz, lvl)
        # büyük ölçekli lekeler (kuru fırça bölgeleri)
        ps = self.patch.shape[0]
        pv = cv2.remap(self.patch, ((X / self.patch_m * ps) % ps).astype(np.float32), ((Z / self.patch_m * ps) % ps).astype(np.float32),
                       cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        dark = np.array(B.hexrgb("#a88c52"), np.float32); light = np.array(B.hexrgb("#e2cc8a"), np.float32)
        w1 = np.clip(pv * 0.35, 0, 0.6)[..., None]; w2 = np.clip(-pv * 0.25, 0, 0.4)[..., None]
        base = base * (1 - w1) + dark * w1
        base = base * (1 - w2) + light * w2
        # kumu biraz soldur (tozlu-pastel; ölçülen sıcak/soğuk dengesine yaklaş)
        g = base.mean(axis=2, keepdims=True)
        col = g + (base - g) * 0.86
        # kum gölü
        if lake_on and self.lake:
            cx, cz, rx, rz = self.lake
            dd = np.sqrt(((X - cx) / rx) ** 2 + ((Z - cz) / rz) ** 2)
            lk = self._mip_sample(self.lmip, mx, mz, lvl)
            # kenar: içe doğru hafif çukur gölgesi, dışta koyu sırt
            inside = np.clip((1.0 - dd) / 0.03, 0, 1)
            rim = np.exp(-((dd - 1.0) / 0.05) ** 2)
            lk = lk * (1 - 0.25 * np.exp(-((dd - 0.93) / 0.08) ** 2))[..., None]
            # halka dalgalar: koyu çizgi + hemen dışında açık çizgi
            r = dd * 7 - ripple_phase
            fr = r - np.floor(r)
            aa = np.clip(np.abs(np.gradient(r, axis=0)) + np.abs(np.gradient(r, axis=1)), 1e-3, 1)
            line_d = np.clip(1 - np.abs(fr - 0.5) / (aa * 1.2 + 0.03), 0, 1)
            line_l = np.clip(1 - np.abs(fr - 0.62) / (aa * 1.0 + 0.025), 0, 1)
            ring = (dd < 0.96) & (dd > 0.08)
            lk = lk * (1 - 0.13 * (line_d * ring)[..., None]) + np.array(B.hexrgb("#f4e6b4"), np.float32) * (0.1 * line_l * ring)[..., None]
            col = col * (1 - inside[..., None]) + lk * inside[..., None]
            col = col * (1 - 0.25 * rim[..., None])
        # uzaklık pusu (uzak ova teal-yeşile döner)
        haze = 1 - np.exp(-np.maximum(depth - 6, 0) / 90)
        haze = np.clip(haze * 1.15, 0, 1)
        col = col * (1 - haze[..., None]) + HAZE * haze[..., None]
        # kameraya yakın kenar biraz koyu (ön plan ağırlığı)
        near = np.clip(1 - depth / 6, 0, 1) * 0.12
        col = col * (1 - near[..., None])
        return col.astype(np.float32), np.where(below, depth, np.inf).astype(np.float32), below

    def _mip_sample(self, mip, mx, mz, lvl):
        i0 = np.floor(lvl).astype(int); fr = (lvl - i0)[..., None]
        out = np.zeros(mx.shape + (3,), np.float32)
        for k in range(len(mip) - 1):
            m = (i0 == k)
            if not m.any():
                continue
            a = cv2.remap(mip[k], mx, mz, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            b = cv2.remap(mip[k + 1], mx, mz, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            out = np.where(m[..., None], a * (1 - fr) + b * fr, out)
        return out


# ------------------------------------------------------------ hacimli ışık
def volume_shade(rgb, a, idbuf, mats_list, cam, L, scale, inflate=0.85, back_rim=1.0):
    """rgb: önçarpımlı renk, a: alfa, idbuf: (h,w) int. Görünüm çerçevesinde ışık."""
    ids = idbuf
    if ids.max() == 0:
        return rgb
    # kimlik kenarları -> uzaklık dönüşümü (tek çağrı)
    edge = np.zeros(ids.shape, np.uint8)
    edge[:, 1:] |= (ids[:, 1:] != ids[:, :-1]); edge[1:, :] |= (ids[1:, :] != ids[:-1, :])
    edge[:, :-1] |= (ids[:, 1:] != ids[:, :-1]); edge[:-1, :] |= (ids[1:, :] != ids[:-1, :])
    edge |= (ids == 0)
    dt = cv2.distanceTransform((1 - edge).astype(np.uint8), cv2.DIST_L2, 5)
    labs = np.unique(ids); labs = labs[labs > 0]
    R = np.zeros(int(ids.max()) + 1, np.float32)
    R[labs] = np.asarray(ndimage.maximum(dt, labels=ids, index=labs), np.float32)
    Rm = np.maximum(R[ids], 1.0)
    u = np.clip(dt / Rm, 0, 1)
    h = np.sqrt(np.clip(1 - (1 - u) ** 2, 0, 1)) * Rm * inflate
    h = cv2.GaussianBlur(h, (0, 0), 1.2)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8; gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    Lv = cam.dir_cam(L).astype(np.float32)
    direct = np.clip(n @ Lv, 0, 1)
    up = n[..., 1]
    amb = SKY_COL[None, None] * (0.5 + 0.5 * up)[..., None] + BOUNCE_COL[None, None] * (0.5 - 0.5 * up)[..., None] * 0.85
    back = max(0.0, float(L @ cam.f))         # güneş öznenin arkasında mı
    rim = (1 - n[..., 2]) ** 2.2 * np.clip((n[..., 0] * Lv[0] + n[..., 1] * Lv[1]) / (math.hypot(Lv[0], Lv[1]) + 1e-6) + 0.35, 0, 1) * back * back_rim
    light = amb * 0.62 + SUN_COL[None, None] * (direct * 0.55)[..., None] + SUN_COL[None, None] * (rim * 0.55)[..., None]
    # malzeme başına ışık gücü (göz akı hep beyaz kalsın)
    strength = np.ones(int(ids.max()) + 1, np.float32)
    for k, name in enumerate(mats_list, start=1):
        if k < len(strength):
            strength[k] = B.NO_SHADE.get(name, 1.0)
    st = strength[ids][..., None]
    st = np.where((ids > 0)[..., None], st, 0.0)
    lit = rgb * (1 - st) + rgb * light * st * 1.12
    return lit.astype(np.float32)


# ------------------------------------------------------------ katman yardımcıları
def new_layer(scale):
    w, h = int(W * scale), int(H * scale)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s); c.scale(scale, scale); c.set_antialias(cairo.ANTIALIAS_BEST)
    return s, c


def to_np(surf):
    surf.flush()
    w, h = surf.get_width(), surf.get_height()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data()).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3]


def id_np(surf):
    surf.flush()
    w, h = surf.get_width(), surf.get_height()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data())
    return a[..., 2].astype(np.int32) + (a[..., 1].astype(np.int32) << 8)


def coc(z, zf, ap, F):
    """Bulanıklık yarıçapı (piksel, 1920 genişlikte)."""
    return ap * F * abs(1 / max(z, 0.05) - 1 / zf)


def shadow_H(cam, G, L, wm, hm):
    """Zemindeki G noktasında duran (kameraya bakan) kartın ekran->gölge homografisi."""
    rh = norm(v3(cam.r[0], 0, cam.r[2]))
    off = v3(-L[0] / L[1], 0, -L[2] / L[1])
    src, dst = [], []
    for a, b in ((-wm, 0), (wm, 0), (-wm, hm), (wm, hm)):
        P = v3(*G) + rh * a + v3(0, b, 0)
        S = v3(*G) + rh * a + off * b
        p = cam.proj(P); q = cam.proj(S)
        src.append(p[:2]); dst.append(q[:2])
    return cv2.getPerspectiveTransform(np.float32(src), np.float32(dst))


class Obj:
    """Dünyadaki bir kart. draw(c, x, y, k): (x,y) ekran zemin noktası, k = piksel/metre."""

    def __init__(self, name, G, draw, height=1.8, width=1.0, caster=True, shaded=True, lift=0.0, ap_scale=1.0, motion=None, dark=0.0):
        self.name, self.G, self.draw, self.hm, self.wm = name, G, draw, height, width
        self.caster, self.shaded, self.lift, self.motion, self.dark = caster, shaded, lift, motion, dark


FAR = [(-260, 330, 70, 22), (-120, 360, 50, 15), (-30, 310, 34, 12), (60, 340, 80, 20), (170, 320, 46, 16), (260, 350, 70, 24), (380, 330, 40, 13), (-400, 340, 60, 18)]


def draw_far(c, cam, items=FAR):
    """Uzak pembe-kırmızı kayalıklar (soluk, göğe karışan)."""
    import random
    for i, (X, Z, wm, hm) in enumerate(items):
        x, y, z = cam.proj((X, 0, Z))
        if z < 1:
            continue
        w = cam.px(wm, z); hh = cam.px(hm, z)
        if x + w < -50 or x - w > W + 50:
            continue
        rnd = random.Random(i)
        pts = [(x - w / 2, y + 3), (x - w * 0.38, y - hh * 0.9), (x - w * 0.3, y - hh), (x + w * 0.25, y - hh * rnd.uniform(0.85, 1)),
               (x + w * 0.35, y - hh * 0.6), (x + w / 2, y + 3)]
        B.fill(c, lambda cc, p=pts: B.poly(cc, p), B.mats()["kaya"], shade=0.35, hi=0.2, light=(0.7, -0.7))
        B.solid(c, lambda cc, p=pts: B.poly(cc, p), B.hexrgb("#a3c9c4"), 0.42)


def render(world, cam, objs, scale=1.0, t=0.0, zf=12.0, ap=0.0, sun_disc=None, ripple_phase=0.0, lake_on=True,
           scatter=None, shadow_op=0.55, bloom=0.6, extra_ground=None, far=True, overlay=None):
    """Bir kare: gök -> zemin (+ot/çiçek) -> gölgeler -> kartlar (uzaktan yakına), DoF, hale."""
    w, h = int(W * scale), int(H * scale)
    sky, _ = world.sky(cam, scale, sun_disc)
    if far:
        fs, fc = new_layer(scale)
        draw_far(fc, cam)
        frgb, fa = to_np(fs)
        sky = frgb + sky * (1 - fa[..., None])
    gcol, gdepth, below = world.ground(cam, scale, t, ripple_phase, lake_on)
    img = np.where(below[..., None], gcol, sky)
    # zemin üstü küçük öğeler (ot, çiçek) — zemin katmanına
    if scatter or extra_ground:
        gs, gc = new_layer(scale)
        if extra_ground:
            extra_ground(gc)
        for (X, Z, kind, r) in (scatter or []):
            x, y, z = cam.proj((X, 0, Z))
            if z < 0.4 or not (-200 < x < W + 200 and -50 < y < H + 200):
                continue
            k = cam.px(1.0, z)
            B.scatter_one(gc, x, y, r, k=k * 0.009, flower=(kind == "f"))
        grgb, ga = to_np(gs)
        img = grgb + img * (1 - ga[..., None])
    # kartlar: önce çiz (gölge için alfa lazım)
    layers = []
    Lsun = world.L
    for o in objs:
        x, y, z = cam.proj((o.G[0], o.lift, o.G[2]))
        if z < 0.15:
            continue
        k = cam.px(1.0, z)
        surf, c = new_layer(scale)
        ids_surf = None
        if o.shaded:
            ids_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
            idc = cairo.Context(ids_surf); idc.scale(scale, scale); idc.set_antialias(cairo.ANTIALIAS_NONE)
            B.REC = dict(ctx=idc, mats=[])
        B.SHADE_SCALE = 0.25 if o.shaded else 1.0
        try:
            o.draw(c, x, y, k)
        finally:
            rec = B.REC; B.REC = None; B.SHADE_SCALE = 1.0
        rgb, a = to_np(surf)
        if o.shaded and rec and rec["mats"]:
            rgb = volume_shade(rgb, a, id_np(ids_surf), rec["mats"], cam, Lsun, scale)
        layers.append((z, o, rgb, a))
    # gölgeler zemine
    sh_total = np.zeros((h, w), np.float32)
    for z, o, rgb, a in layers:
        if not o.caster:
            continue
        Hm = shadow_H(cam, o.G, Lsun, o.wm, o.hm)
        S = np.diag([scale, scale, 1.0]); Hs = S @ Hm @ np.linalg.inv(S)
        sh = cv2.warpPerspective(a, Hs, (w, h), flags=cv2.INTER_LINEAR)
        sh = cv2.GaussianBlur(sh, (0, 0), max(1.0, 2.5 * scale + cam.px(0.04, z) * scale))
        sh_total = np.maximum(sh_total, sh)
    sh_total *= below
    img = img * (1 - (sh_total * shadow_op)[..., None] * (1 - B.SHADOW_K[None, None]))
    # zemin DoF (derinliğe göre bulanık seviyeler)
    if ap > 0:
        cz = np.where(np.isfinite(gdepth), ap * cam.F * np.abs(1 / np.maximum(gdepth, 0.05) - 1 / zf), ap * cam.F / zf) * scale
        cz = np.clip(cz, 0, 40 * scale)
        levels = [0, 2, 5, 11, 22]
        blurred = [img] + [cv2.GaussianBlur(img, (0, 0), s * scale) for s in levels[1:]]
        sig = cz / 2
        out = np.zeros_like(img)
        for i in range(len(levels) - 1):
            a0, a1 = levels[i] * scale, levels[i + 1] * scale
            m = (sig >= a0) & (sig < a1) if i < len(levels) - 2 else (sig >= a0)
            f = np.clip((sig - a0) / max(a1 - a0, 1e-6), 0, 1)[..., None]
            out = np.where(m[..., None], blurred[i] * (1 - f) + blurred[i + 1] * f, out)
        img = out
    # kartlar uzaktan yakına
    for z, o, rgb, a in sorted(layers, key=lambda q: -q[0]):
        if o.dark:
            lum = rgb.max(axis=2) / np.maximum(a, 1e-4)
            keep = np.clip((lum - 0.82) / 0.1, 0, 1)
            dd = (o.dark * (1 - keep))[..., None]
            rgb = rgb * (1 - dd) + a[..., None] * np.array([0.11, 0.08, 0.11], np.float32) * dd
        if ap > 0:
            sg = coc(z, zf, ap, cam.F) * scale / 2
            if sg > 0.4:
                rgb = cv2.GaussianBlur(rgb, (0, 0), sg); a = cv2.GaussianBlur(a, (0, 0), sg)
        if o.motion and o.motion[0] * scale >= 1:
            rgb = B.motion(rgb, o.motion[0] * scale, o.motion[1]); a = B.motion(a, o.motion[0] * scale, o.motion[1])
        img = rgb + img * (1 - a[..., None])
    if overlay:
        os_, oc = new_layer(scale)
        overlay(oc)
        orgb, oa = to_np(os_)
        img = orgb + img * (1 - oa[..., None])
    # hale + boya yumuşatması
    lum = img.max(axis=2)
    br = np.clip((lum - 0.95) / 0.05, 0, 1)[..., None] * img
    if br.max() > 0:
        img = img + cv2.GaussianBlur(br, (0, 0), 60 * scale) * bloom + cv2.GaussianBlur(br, (0, 0), 18 * scale) * 0.2
    img = cv2.GaussianBlur(img, (0, 0), 0.55 * scale)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def scatter_world(seed, n_tuft, n_flower, xr, zr, avoid=None):
    rng = np.random.default_rng(seed)
    out = []
    for kind, n in (("t", n_tuft), ("f", n_flower)):
        for _ in range(n):
            X, Z = rng.uniform(*xr), rng.uniform(*zr)
            if avoid and avoid(X, Z):
                continue
            out.append((X, Z, kind, float(rng.random())))
    out.sort(key=lambda q: -q[1])
    return out

"""Kum Balıkçısı: 12 planın animasyonu. Her plan shot(t, fr) -> composite spec döndürür.
Plan süreleri SENARYO.md'deki listeyle aynı (kare sayısı 25 fps)."""
import math
import random
import boya as B
import tikir as T
from boya import W, H, hexrgb

FPS = 25


# ------------------------------------------------------------ zaman yardımcıları
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):
    u = clamp(u); return u * u * (3 - 2 * u)


def eout(u):
    u = clamp(u); return 1 - (1 - u) ** 3


def ein(u):
    u = clamp(u); return u ** 3


def seg(t, a, b):
    return clamp((t - a) / max(b - a, 1e-6))


def lerp(a, b, u):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * u
    if isinstance(a, (tuple, list)):
        return type(a)(lerp(x, y, u) for x, y in zip(a, b))
    if isinstance(a, dict):
        return {k: (lerp(a[k], b[k], u) if k in b else a[k]) for k in a}
    return b if u > 0.5 else a


def kf(t, keys, fn=ease):
    """keys: [(t, değer), ...] — değerler sayı/demet/sözlük olabilir."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, fn(seg(t, t0, t1)))
    return keys[-1][1]


def expr_at(t, keys, blinks=(), blend=0.08):
    """keys: [(t, isim veya dict)], blinks: göz kırpma saatleri (4 kare: yarım, kapalı, kapalı, yarım)."""
    def ex(v):
        return T.expr(v) if isinstance(v, str) else v
    e = ex(keys[0][1])
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t >= t1 - blend:
            e = T.lerp_expr(ex(v0), ex(v1), seg(t, t1 - blend, t1))
            e = ex(v1) if t >= t1 else e
    e = dict(e)
    for b in blinks:
        f = (t - b) * FPS
        if 0 <= f < 4:
            e["open"] = min(e["open"], (0.5, 0.0, 0.0, 0.5)[int(f)] * 0.9)
    return e


def pose_mix(a, b, u):
    out = dict(a)
    for k in ("rot", "hip", "chest", "head", "head_rot", "look", "legL", "legR", "armL", "armR"):
        out[k] = lerp(a[k], b[k], u)
    return out


def sand_spray(seed, t, origin, n, spread, speed, life=0.7, g=1600, size=(2.5, 6), t0=0.0, t1=99.0, dir_ang=-math.pi / 2):
    """Kum fışkırması: t0..t1 arasında doğan tanecikler."""
    rnd = random.Random(seed)
    items = []
    for i in range(n):
        born = t0 + (t1 - t0) * rnd.random() if t1 < 50 else t0 + rnd.random() * 0.15
        age = t - born
        if age < 0 or age > life:
            continue
        a = dir_ang + rnd.gauss(0, spread)
        v = speed * rnd.uniform(0.5, 1.1)
        vx, vy = math.cos(a) * v, math.sin(a) * v
        x = origin[0] + vx * age; y = origin[1] + vy * age + 0.5 * g * age * age
        items.append((x, y, rnd.uniform(*size), vx * 0.02, (vy + g * age) * 0.02))
    return items


# ------------------------------------------------------------ sahne ortak
LAKE = (700, 830, 470, 125)
WHALE = dict(cx=430, base=722, w=840)
HZ = 626


def wide_bg(c, t, whale_rise=0.0, whale_eye=0.0, show_lake=True, ripple_phase=0.0, sun=None):
    B.sky(c, HZ, sun=sun)
    B.mesas(c, HZ, seed=3)
    B.ground(c, HZ)
    B.scatter(c, HZ, seed=5, n_tuft=46, n_flower=30,
              avoid=lambda x, y: ((x - LAKE[0]) / (LAKE[2] + 40)) ** 2 + ((y - LAKE[1]) / (LAKE[3] + 30)) ** 2 < 1 or (x < 900 and y < 740))
    mouth_pt = B.whale(c, WHALE["cx"], WHALE["base"], WHALE["w"], whale_rise, eye=whale_eye, mouth=0.0, t=t, line_to=True)
    if show_lake:
        B.sand_lake(c, *LAKE)
        B.ripples(c, *LAKE, n=6, phase=ripple_phase)
    return mouth_pt


def puller_pose(t_pull=0.0, yank=0.0):
    """Ayakta, sola doğru oltaya asılan poz (yüz sola dönük)."""
    p = T.P(rot=0.22 + 0.08 * yank, look=-0.75,
            legL=[(-0.17, -1.25), (-0.42, -0.66), (-0.62, -0.06)], legR=[(0.17, -1.25), (0.28, -0.62), (0.3, -0.06)],
            armL=[(-0.36, -2.12), (-0.72, -1.95), (-0.98, -1.78)], armR=[(0.36, -2.12), (-0.1, -1.75), (-0.62, -1.7)],
            handL=("tut", 0.0), handR=("tut", 0.0), head=(-0.08, -3.1), head_rot=-0.12)
    return p


# ------------------------------------------------------------ 1. Arzu
def shot1(t, fr):
    B.LIGHT[:] = [0.3, -0.95]
    c = fr.ctx("bg")
    hz = 990
    sun = (1205, 330, 74)
    B.sky(c, hz, sun=sun)
    B.mesas(c, hz, seed=8, scale=0.8)
    B.ground(c, hz, far_band=20)
    m = fr.ctx("mid")
    lean = kf(t, [(0, 0.0), (0.9, 1.0)])
    flick = math.sin(math.pi * seg(t, 1.25, 1.55)) if 1.25 <= t <= 1.55 else 0.0
    p = T.seated(e=expr_at(t, [(0, "notr"), (0.9, "kararli")], blinks=(0.55, 2.2)),
                 head=(0.08 + 0.04 * lean, -2.82 + 0.08 * lean), head_rot=0.05 * lean, look=0.05, rot=0.03 * lean)
    p["armL"] = [(-0.31, -1.82), (-0.25, -1.38), (-0.02, -1.25 - 0.12 * flick)]
    p["armR"] = [(0.41, -1.82), (0.42, -1.36), (0.16, -1.28 - 0.12 * flick)]
    ox, oy, s = 1075, 1150, 252 + 10 * lean
    J = T.joints(p, ox, oy, s)
    hand = J((0.06, -1.27 - 0.12 * flick))
    rp = B.rod_points(hand, 2.42 + 0.06 * flick, 820, -0.18 + 0.1 * flick)
    fl = (300, 880)

    def between(cc):
        B.line(cc, rp[-1], (fl[0] + 25, fl[1] - 150), sag=10, w=3)
        B.rod(cc, rp, 26)
    B.stool(m, ox, oy + 30, s * 1.0)
    T.draw(m, p, ox, oy, s, between=between, t=t)
    f = fr.ctx("fg")
    B.float_(f, fl[0], fl[1], 150, glint=0.0)
    crest = [(1250, 1090), (1420, 960), (1640, 900), (1900, 920), (1990, 1000), (1990, 1100)]
    B.fill(f, lambda cc: B.blob(cc, crest, 8), B.mats()["kum_gol"], shade=0.7, hi=0.4, light=(-0.4, -0.9))
    crest2 = [(-40, 1100), (-40, 1010), (120, 1000), (380, 1040), (560, 1100)]
    B.fill(f, lambda cc: B.blob(cc, crest2, 6), B.mats()["kum_gol"], shade=0.6, hi=0.3)
    return dict(bg_blur=2.0, fg_blur=16, mid_dark=0.42, bloom=0.9)


# ------------------------------------------------------------ 2. Araç (şamandıra)
def shot2(t, fr):
    B.LIGHT[:] = [0.5, -0.85]
    c = fr.ctx("bg")
    m = B.mats()
    c.set_source(m["kum_gol"].pattern); c.paint()
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexrgb("#8a7c58"), 0.45); g.add_color_stop_rgba(0.45, *hexrgb("#8a7c58"), 0.0); g.add_color_stop_rgba(1, *hexrgb("#f1e2a8"), 0.25)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    cx, cy = 960, 640
    B.ripples(c, cx, cy + 30, 1500, 420, n=8, phase=t * 0.6, a=0.5)
    # batış halkaları
    if t > 0.46:
        for k in range(3):
            u = seg(t, 0.46 + k * 0.08, 0.95 + k * 0.08)
            if u > 0:
                c.set_line_width(8 * (1 - u) + 2); B.ellipse(c, cx, cy + 22, 90 + 420 * u, 26 + 120 * u)
                c.set_source_rgba(*hexrgb("#8a7c58"), 0.55 * (1 - u)); c.stroke()
    f = fr.ctx("mid")
    tw = 0.0
    for tt in (0.1, 0.28):
        if tt <= t < tt + 0.1:
            tw = math.sin(math.pi * (t - tt) / 0.1)
    sink = ein(seg(t, 0.46, 0.72))
    r = 125
    top = (cx + 35, cy - r * 1.75 + 14 * tw + sink * r * 2.2)
    B.line(f, (cx + 70, -20), top, sag=0, w=3)
    B.float_(f, cx, cy + 14 * tw, r, sink=sink, glint=max(0, math.sin(math.pi * seg(t, 0.0, 0.3))), clip_y=cy + r * 0.2, tilt=0.06 * tw)
    # kenara düşen gölge
    if sink < 0.9:
        c.save(); B.ellipse(c, cx - 70, cy + 40, r * 0.9 * (1 - sink), r * 0.25 * (1 - sink)); c.set_source_rgba(*hexrgb("#786e50"), 0.35); c.fill(); c.restore()
    if t > 0.46:
        B.particles(f, B_spray(t, (cx, cy + 20), 0.46))
    return dict(bg_blur=1.2)


def B_spray(t, o, t0):
    return sand_spray(21, t, o, 50, 0.6, 520, life=0.45, t0=t0, t1=t0 + 0.12, size=(3, 7))


# ------------------------------------------------------------ 3. Küçük zafer
def shot3(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 500
    B.sky(c, hz)
    B.mesas(c, hz, seed=4, scale=1.4)
    B.ground(c, hz)
    B.sand_lake(c, 760, 860, 1100, 260); B.ripples(c, 760, 860, 1100, 260, n=6)
    B.whale(c, 260, 600, 700, 0.0, line_to=False)
    spit = seg(t, 1.0, 1.25)
    recoil = math.sin(math.pi * seg(t, 1.0, 1.5)) if 1.0 <= t <= 1.5 else 0.0
    e = expr_at(t, [(0, T.expr("gurur", gx=0.5)), (1.05, "sok"), (1.5, "notr"), (2.35, T.expr("sinsi", gx=-0.2, gy=0.0))],
                blinks=(1.55, 1.75, 1.95, 3.2))
    look = kf(t, [(0, 0.35), (1.0, 0.35), (1.1, 0.0), (2.3, 0.0), (2.5, -0.15)])
    s = 520
    hx = 830 - 25 * recoil
    ox, oy = hx, 470 + 3.12 * s
    wob = math.sin(t * 2.0) * 0.02
    p = T.P(e=e, look=look, head_rot=0.06 - 0.12 * recoil + wob, dirty=0.75 if t > 1.15 else 0.0,
            armL=[(-0.36, -2.12), (0.3, -2.25), (0.68, -2.62)], armR=[(0.36, -2.12), (0.95, -2.3), (1.22, -2.72)],
            handL=("tut", -0.6), handR=("tut", -0.9))
    m = fr.ctx("mid")
    flop = 1.0 if t < 1.0 or t > 1.4 else 0.3
    fx, fy = hx + 560, 560 + math.sin(t * 9) * 6
    T.draw(m, p, ox, oy, s, t=t, between=None)
    m2 = fr.ctx("fg")
    B.fish(m2, fx, fy, 520, ang=0.12 + math.sin(t * 7) * 0.05, t=t, flap=flop, mouth="acik" if 0.95 < t < 1.35 else "kapali", flip=True)
    # eller balığın üstünde
    J = T.joints(p, ox, oy, s)
    T._hand_screen = None
    for wr, ang in (((0.68, -2.62), -0.6), ((1.22, -2.72), -0.9)):
        x, y = J(wr)
        m2.save(); m2.translate(x, y); m2.scale(s, s)
        T._hand(m2, 0, 0, "tut", ang)
        m2.restore()
    if 1.0 <= t <= 1.45:
        B.particles(m2, sand_spray(31, t, (fx - 255, fy + 20), 160, 0.35, 1500, life=0.3, g=200, t0=1.0, t1=1.15, dir_ang=math.pi + 0.15, size=(4, 10)))
    return dict(bg_blur=5.0)


# ------------------------------------------------------------ 4. Tırmanma
def shot4(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    target = (560, 712)
    wide_bg(c, t, ripple_phase=t * 0.3)
    m2 = fr.ctx("mid2")
    fish_u = seg(t, 0.0, 0.35)
    B.bucket(m2, 1590, 935, 100, tilt=0.06 * math.sin(math.pi * seg(t, 0.33, 0.6)))
    B.stool(m2, 1700, 925, 95)
    m = fr.ctx("mid")
    yank = 0.0
    for ty in (1.1, 1.55):
        if ty - 0.05 <= t <= ty + 0.3:
            yank = max(yank, math.sin(math.pi * seg(t, ty - 0.05, ty + 0.3)))
    toss = T.P(look=0.4, e=T.expr("gurur", gx=0.6),
               armL=[(-0.36, -2.12), (-0.5, -1.62), (-0.45, -1.2)], armR=[(0.36, -2.12), (0.75, -2.2), (1.05, -2.5)],
               handL=("tut", 1.4), handR=("acik", -0.4))
    cast = T.P(look=-0.4, e=T.expr("kararli"), rot=-0.05,
               armL=[(-0.36, -2.12), (-0.6, -2.5), (-0.5, -2.95)], armR=[(0.36, -2.12), (0.1, -2.6), (-0.3, -2.9)],
               handL=("tut", -1.2), handR=("tut", -1.2))
    pull = puller_pose(yank=yank)
    if t < 0.35:
        p = pose_mix(toss, cast, ease(seg(t, 0.2, 0.35)))
    elif t < 0.9:
        p = pose_mix(cast, pull, eout(seg(t, 0.4, 0.75)))
    else:
        p = pull
    p["e"] = expr_at(t, [(0, T.expr("gurur", gx=0.6)), (0.4, "kararli"), (0.95, "gergin")], blinks=(0.7,))
    ox, oy, s = 1400, 930, 118
    J = T.joints(p, ox, oy, s)
    hand = J(p["armL"][2])
    if t < 0.4:
        ang, bend = -1.4, 0.0
    elif t < 0.75:
        ang, bend = lerp(-1.4, -2.75, ease(seg(t, 0.4, 0.6))), 0.2 * math.sin(math.pi * seg(t, 0.4, 0.75))
    else:
        ang, bend = -2.75 + 0.15 * yank, -0.35 - 0.35 * yank - (0.15 if t > 0.9 else 0)
    rp = B.rod_points(hand, ang, 430, bend)
    tip = rp[-1]
    cast_u = seg(t, 0.45, 0.8)
    if t < 0.45:
        fl = None
    elif t < 0.8:
        u = eout(cast_u)
        fl = (lerp(tip[0], target[0], u), lerp(tip[1], target[1], u) - 260 * math.sin(math.pi * u))
    else:
        fl = target

    def between(cc):
        if fl:
            B.line(cc, tip, fl, sag=40 if t < 0.85 else 0, w=2.5)
        B.rod(cc, rp, 13)
    T.draw(m, p, ox, oy, s, between=between, t=t)
    if fl and t < 0.95:
        B.float_(m, fl[0], fl[1], 16, sink=ein(seg(t, 0.82, 0.95)), clip_y=target[1] + 3)
    if t < 0.35:
        u = fish_u
        fx, fy = lerp(1520, 1595, u), lerp(760, 820, u) - 120 * math.sin(math.pi * u)
        B.fish(m, fx, fy, 70, ang=u * 4, t=t)
    for ty in (1.1, 1.55):
        B.particles(m, sand_spray(int(ty * 10), t, J((-0.62, 0.0)), 40, 0.5, 420, life=0.5, t0=ty - 0.05, t1=ty + 0.05, dir_ang=-math.pi * 0.85, size=(2, 5)))
    return dict(bg_blur=0.8, shadows=[("mid", B.cast(ox, oy), 0.55, 5), ("mid2", B.cast(1600, 930), 0.5, 5)])


# ------------------------------------------------------------ 5. Ters köşe 1
def shot5(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    rise = eout(seg(t, 0.0, 1.25))
    eye = ease(seg(t, 0.65, 1.1))
    B.sky(c, HZ); B.mesas(c, HZ, seed=3); B.ground(c, HZ)
    B.scatter(c, HZ, seed=5, n_tuft=46, n_flower=30,
              avoid=lambda x, y: ((x - LAKE[0]) / (LAKE[2] + 40)) ** 2 + ((y - LAKE[1]) / (LAKE[3] + 30)) ** 2 < 1 or (x < 900 and y < 740))
    m3 = fr.ctx("mid2")
    mouth_pt = B.whale(m3, WHALE["cx"], WHALE["base"], WHALE["w"], rise, eye=eye, mouth=0.0, t=t, line_to=True)
    # kum şelaleleri
    rnd = random.Random(5)
    items = []
    h = WHALE["w"] * (0.32 + 0.3 * rise) + WHALE["w"] * 0.12 * rise
    for k in range(22):
        u = rnd.uniform(-0.48, 0.55)
        x0 = WHALE["cx"] + u * WHALE["w"]
        top = WHALE["base"] - h * max(0.1, 1 - (u / 0.62) ** 2)
        for j in range(16):
            ph = (t * 1.6 + j / 16 + rnd.random()) % 1
            y = top + (WHALE["base"] - top) * ph ** 1.6
            items.append((x0 + rnd.gauss(0, 8), y, rnd.uniform(3, 8), 0, 18 * ph))
    if t > 0.05:
        B.particles(m3, items, alpha=0.85 * min(1, t / 0.2))
    # göl önde (ayrı katman: gölge düşürmesin)
    lkc = fr.ctx("lake")
    B.sand_lake(lkc, *LAKE); B.ripples(lkc, *LAKE, n=6, phase=t * 2.0, a=0.6)
    lk = fr.ctx("mid")
    eyes = T.expr("gergin") if t < 0.35 else T.expr("sok", size=1.1 + 0.2 * ease(seg(t, 0.35, 1.0)), mouth="cizgi")
    p = puller_pose(yank=0.4)
    p["e"] = eyes
    ox, oy, s = 1400, 930, 118
    J = T.joints(p, ox, oy, s)
    hand = J(p["armL"][2])
    rp = B.rod_points(hand, -2.6, 430, -0.55 + 0.4 * rise)

    def between(cc):
        B.line(cc, rp[-1], mouth_pt, w=2.5)
        B.rod(cc, rp, 13)
    T.draw(lk, p, ox, oy, s, between=between, t=t)
    B.bucket(lk, 1590, 935, 100); B.stool(lk, 1700, 925, 95)
    return dict(bg_blur=0.8, mid2_blur=0.5, shadows=[("mid", B.cast(ox, oy), 0.55, 5)])


# ------------------------------------------------------------ 6. Bedel a
def shot6(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 600
    B.sky(c, hz); B.mesas(c, hz, seed=12); B.ground(c, hz)
    B.scatter(c, hz, seed=15, n_tuft=40, n_flower=24)
    up = 1 - ein(seg(t, 0.0, 1.0))
    B.tail(c, 430, 770, 420, up, t=t)
    m = fr.ctx("mid")
    B.particles(m, sand_spray(61, t, (430, 760), 260, 0.7, 900, life=1.0, t0=0.0, t1=0.9, size=(3, 9)))
    u = seg(t, 0.05, 1.35)
    x = lerp(1560, 260, ein(u) * 0.35 + u * 0.65)
    y = 560 - 60 * math.sin(math.pi * u)
    flap = math.sin(t * 28)
    p = T.P(rot=-1.45, look=-0.2, e=T.expr("panik"),
            legL=[(-0.17, -1.25), (-0.35 + 0.15 * flap, -0.66), (-0.3 + 0.3 * flap, -0.06)],
            legR=[(0.17, -1.25), (0.35 - 0.15 * flap, -0.66), (0.3 - 0.3 * flap, -0.06)],
            armL=[(-0.36, -2.12), (-0.3, -2.7), (-0.1, -3.25)], armR=[(0.36, -2.12), (0.25, -2.7), (0.05, -3.3)],
            handL=("tut", -1.5), handR=("tut", -1.5), hat=dict(on=False))
    s = 120
    J = T.joints(p, x, y, s)
    hand = J((0.0, -3.3))
    rp = B.rod_points(hand, math.pi + 0.05, 260, 0.1)

    def between(cc):
        if up > 0.05:
            B.line(cc, rp[-1], (430, 770 - 420 * 0.5 * up), w=2.5)
        else:
            B.line(cc, rp[-1], (-20, 700), w=2.5)
        B.rod(cc, rp, 12)
    if t < 1.5:
        T.draw(m, p, x, y, s, between=between, t=t)
    # şapka uçar
    m2 = fr.ctx("mid2")
    hu = seg(t, 0.1, 1.8)
    hx, hy = lerp(1500, 1250, hu), 470 - 380 * math.sin(math.pi * 0.5 * hu) + 300 * hu * hu
    m2.save(); m2.translate(hx, hy); m2.scale(120, 120); T.draw_hat(m2, 0, 0, t * 5); m2.restore()
    # tabure yuvarlanır
    tu = seg(t, 0.1, 1.2)
    B.stool(m2, lerp(1600, 1800, eout(tu)), 930, 100, tilt=eout(tu) * 4.5)
    B.bucket(m2, 1450, 935, 100, tilt=0.4 * math.sin(math.pi * seg(t, 0.1, 0.6)))
    return dict(bg_blur=0.8, mid_motion=(26 if 0.05 < t < 1.4 else 0, 0), shadows=[("mid2", B.cast(1600, 930), 0.5, 5)])


# ------------------------------------------------------------ 7. Bedel b (kum kayağı)
def shot7(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    bump = abs(math.sin(t * 7.5))
    hz = 470 + 10 * math.sin(t * 7.5)
    B.sky(c, hz); B.mesas(c, hz, seed=21, scale=1.2); B.ground(c, hz)
    # hareket hissi: kameraya doğru akan kuru fırça izleri ve tutamlar
    rnd = random.Random(3)
    import cairo
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(140):
        ph = (rnd.random() + t * 0.9) % 1
        d = ph ** 2.2
        y = hz + 6 + (H - hz + 120) * d
        x = 960 + (rnd.random() - 0.5) * (300 + 3200 * d)
        L = 8 + 140 * d
        c.set_line_width(2 + 9 * d); c.set_source_rgba(*hexrgb("#a8925f" if k % 2 else "#e6d08e"), 0.5)
        c.move_to(x, y - L * 0.5); c.line_to(x, y + L * 0.5); c.stroke()
    m = fr.ctx("mid")
    face = int(t / 0.6) % 2
    p = T.P(rot=0.05 * math.sin(t * 5), look=0.0,
            hip=(0, -1.05), chest=(0, -2.0), head=(0, -2.92),
            legL=[(-0.17, -1.05), (-0.48, -0.6), (-0.5, -0.06)], legR=[(0.17, -1.05), (0.48, -0.6), (0.5, -0.06)],
            armL=[(-0.36, -1.92), (-0.4, -1.55), (-0.08, -1.42)], armR=[(0.36, -1.92), (0.42, -1.55), (0.1, -1.4)],
            handL=("tut", 0.3), handR=("tut", 0.3),
            e=T.expr("keyif") if face == 0 else T.expr("panik"), hat=dict(on=True, tilt=-0.15, dy=-0.04 * bump))
    ox, oy, s = 960, 1060 - 24 * bump, 200
    J = T.joints(p, ox, oy, s)
    hand = J((0.0, -1.41))
    rp = B.rod_points(hand, 1.75, 260, 0.0)

    def between(cc):
        B.line(cc, rp[-1], (1000, 1200), w=3)
        B.rod(cc, rp, 18)
    T.draw(m, p, ox, oy, s, between=between, t=t)
    f = fr.ctx("fg")
    for sx in (-1, 1):
        o = J((sx * 0.55, 0.0))
        B.particles(f, sand_spray(70 + sx, t, o, 420, 0.25, 1100, life=0.55, g=1900, t0=0, t1=2.6,
                                  dir_ang=-math.pi / 2 + sx * 0.9, size=(3, 9)))
    return dict(bg_blur=1.5, fg_blur=1.0, shadows=[("mid", B.cast(ox, oy, dx=-0.5, dy=0.15), 0.5, 6)])


# ------------------------------------------------------------ 8. Sessiz duraklama
def shot8(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 570
    B.sky(c, hz); B.mesas(c, hz, seed=31); B.ground(c, hz)
    B.scatter(c, hz, seed=33, n_tuft=44, n_flower=30, avoid=lambda x, y: 1180 < x < 1640 and 760 < y < 900)
    up = ease(seg(t, 0.0, 0.3)) * (1 - ein(seg(t, 0.35, 0.75)))
    B.tail(c, 470, 740, 300, up, t=t)
    m = fr.ctx("mid")
    B.particles(m, sand_spray(81, t, (470, 735), 220, 0.8, 700, life=0.9, t0=0.45, t1=0.6, size=(3, 8)))
    # gömülü baş
    hx, hy, s = 1350, 742, 165
    e = expr_at(t, [(0, "bon"), (3.4, T.expr("bon", gx=-0.85)), (3.75, T.expr("bon", gx=0.0))], blinks=(2.3, 3.15))
    m.save(); m.translate(hx, hy); m.scale(s, s)
    T.head(m, 0, 0, e, look=0.0, rot=-0.06, hat=dict(on=True, tilt=-0.38, dx=-0.12, dy=0.06), dirty=0.8, seed=8, t=t)
    m.restore()
    # boyun çevresinde kum yığını
    B.fill(m, lambda cc: B.blob(cc, [(hx - 210, hy + 125), (hx - 80, hy + 70), (hx + 80, hy + 72), (hx + 220, hy + 125), (hx, hy + 140)], 8), B.mats()["kum"], shade=0.4, hi=0.35)
    # düğüm olmuş olta
    pts = [(1560, 860), (1575, 740), (1640, 700), (1660, 760), (1590, 780), (1600, 690), (1690, 650), (1700, 600)]
    B.fill(m, lambda cc: B.tube(cc, pts, 14, 6, n=6), B.mats()["bambu"], shade=0.5, hi=0.4)
    # kova düşer
    bu = seg(t, 1.0, 1.25)
    if t >= 1.0:
        by = lerp(-250, 865, bu * bu)
        if t > 1.25:
            by = 865 - 40 * math.sin(math.pi * seg(t, 1.25, 1.45)) * (1 if t < 1.45 else 0)
        B.bucket(m, 1150, by, 115, tilt=0.15 * (1 - seg(t, 1.25, 1.5)))
    if 1.25 <= t <= 1.8:
        B.particles(m, sand_spray(82, t, (1150, 865), 60, 0.9, 380, life=0.45, t0=1.25, t1=1.3, size=(2, 5)))
    return dict(bg_blur=0.8, shadows=[("mid", B.cast(1350, 865), 0.45, 6)])


# ------------------------------------------------------------ 9. İkinci deneme
def shot9(t, fr):
    B.LIGHT[:] = [0.75, -0.65]
    c = fr.ctx("bg")
    hz = 640
    B.sky(c, hz, sun=(1860, 40, 150))
    B.mesas(c, hz, seed=41, scale=1.6, side="sol")
    B.ground(c, hz)
    B.scatter(c, hz, seed=43, n_tuft=24, n_flower=16)
    wob = 0.12 * math.sin(t * 30) * (1 if 1.5 < t < 1.85 else 0)
    B.bucket(c, 1380, 985, 220, tilt=wob)
    m = fr.ctx("mid")
    turn = ease(seg(t, 1.0, 1.3))
    e = expr_at(t, [(0, T.expr("kararli", gy=0.7, gx=0.1)), (1.05, T.expr("sinsi", gx=0.0, gy=0.0))], blinks=(0.45,))
    thread = math.sin(t * 6) * 0.04 if t < 1.0 else 0
    p = T.P(hip=(0, -0.3), chest=(0.02, -1.25), head=(0.04, -2.17), look=lerp(0.1, -0.05, turn), head_rot=lerp(0.12, 0.0, turn),
            legL=[(-0.17, -0.3), (-0.75, -0.75), (-1.05, -0.06)], legR=[(0.17, -0.3), (0.65, -0.68), (1.05, -0.06)],
            armL=[(-0.33, -1.18), (-0.38, -0.72), (-0.08 + thread, -0.9)], armR=[(0.37, -1.18), (0.45, -0.72), (0.14 - thread, -0.92)],
            handL=("tut", -0.3), handR=("tut", 2.8), e=e, dirty=0.8, hat=dict(on=True, tilt=-0.25, dx=-0.08), seed=9)
    ox, oy, s = 840, 1000, 235
    J = T.joints(p, ox, oy, s)

    def between(cc):
        a = J((-0.02 + thread, -1.0)); b = J((0.08 - thread, -1.02))
        cc.set_line_width(4); cc.set_source_rgb(*hexrgb("#9aa3a0")); cc.move_to(a[0], a[1] + 30); cc.line_to(a[0], a[1] - 10)
        cc.arc_negative(a[0] + 9, a[1] - 10, 9, math.pi, 0.2); cc.stroke()
        B.fill(cc, lambda q: B.tube(q, [(b[0] - 2, b[1] - 18), (b[0] + 10, b[1] - 34), (b[0] + 2, b[1] - 50)], 7, 5), B.mats()["yanak"], shade=0.3, hi=0.4)
    T.draw(m, p, ox, oy, s, between=between, t=t)
    f = fr.ctx("fg")
    B.float_(f, 300, 985, 75)
    return dict(bg_blur=2.0, bloom=0.9, shadows=[("mid", B.cast(ox, oy, dx=-0.9, dy=0.2), 0.5, 7)])


# ------------------------------------------------------------ 10. Ters köşe 2
def shot10(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 580
    B.sky(c, hz); B.mesas(c, hz, seed=51, scale=1.4); B.ground(c, hz)
    B.bucket(c, 1520, 1000, 330, tilt=0.15 * math.sin(math.pi * seg(t, 0.45, 0.75)))
    s = 330
    rec = eout(seg(t, 0.8, 1.0)) * (1 - 0.6 * seg(t, 1.0, 1.6))
    hx, hy = 880 - 50 * rec, 430 + 20 * rec
    ox, oy = hx, hy + 3.12 * s
    e = expr_at(t, [(0, "sinsi"), (0.82, "sok"), (1.15, "aci")], blinks=(0.3,))
    up = eout(seg(t, 0.85, 1.05))
    p = T.P(e=e, head_rot=-0.15 * rec, look=0.05, sore=False,
            armL=[(-0.36, -2.12), lerp((-0.5, -1.62), (-0.95, -2.3), up), lerp((-0.3, -1.95), (-1.25, -3.0), up)],
            armR=[(0.36, -2.12), lerp((0.6, -1.7), (0.95, -2.3), up), lerp((0.75, -2.3), (1.25, -3.05), up)],
            handL=("tut", 0.5) if up < 0.5 else ("acik", -2.2), handR=("tut", -0.5) if up < 0.5 else ("acik", -1.0),
            dirty=0.8, hat=dict(on=True, tilt=-0.25, dx=-0.08), seed=9)
    m = fr.ctx("mid")
    T.draw(m, p, ox, oy, s, t=t)
    nose = (hx + 0 * s, hy + 0.16 * s)
    f = fr.ctx("fg")
    if t < 0.82:
        u = seg(t, 0.48, 0.82)
        if u > 0:
            fx = lerp(1520, nose[0] + 20, u); fy = lerp(700, nose[1] + 120, u) - 260 * math.sin(math.pi * u)
            B.fish(f, fx, fy, 260, ang=lerp(-0.6, -2.4, u), t=t)
            spec_m = (22, math.degrees(math.atan2(-1, -1.6)))
        else:
            spec_m = None
    else:
        sw = math.sin(t * 7) * 0.3 * (1 - seg(t, 1.2, 2.8) * 0.6)
        ang = -math.pi / 2 - 0.55 + sw
        L = 260
        cxp = nose[0] - math.cos(ang) * L * 0.5; cyp = nose[1] - math.sin(ang) * L * 0.5
        B.fish(f, cxp, cyp, L, ang=ang, t=t, flap=1.2, mouth="kapali")
        spec_m = None
    return dict(bg_blur=5.0, fg_motion=spec_m)


# ------------------------------------------------------------ 11. Panik
def shot11(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 540
    B.sky(c, hz); B.mesas(c, hz, seed=61, scale=1.3); B.ground(c, hz)
    B.scatter(c, hz, seed=63, n_tuft=26, n_flower=18)
    stretch = 0.0
    for ty in (0.2, 0.9, 1.5):
        if ty <= t <= ty + 0.32:
            u = (t - ty) / 0.32
            stretch = max(stretch, math.sin(math.pi * min(1, u * 1.6)) if u < 0.62 else math.sin(math.pi * u * 1.6) * 0.0 - 0.25 * math.sin(math.pi * (u - 0.62) / 0.38))
    spin = math.sin(t * 5.5)
    s = 190
    ox, oy = 960 + 40 * spin, 1050
    nose_vec = (0.25 + 1.6 * max(stretch, 0), 0.1 + 0.35 * max(stretch, 0))
    p = T.P(e=T.expr("panik", tears=1.0), look=0.35 * spin, rot=0.06 * spin - 0.05 * max(stretch, 0),
            nose=nose_vec, dirty=0.8, hat=dict(on=True, tilt=-0.3 + 0.1 * spin, dx=-0.08), seed=9,
            armL=[(-0.36, -2.12), (0.1, -2.3), (0.55 + nose_vec[0] * 0.6, -2.92)], armR=[(0.36, -2.12), (0.8, -2.25), (0.9 + nose_vec[0] * 0.6, -2.88)],
            handL=("tut", 0.0), handR=("tut", 0.0))
    m = fr.ctx("mid")
    T.draw(m, p, ox, oy, s, t=t)
    J = T.joints(p, ox, oy, s)
    hx, hy = J(p["head"])
    tip = (hx + (nose_vec[0] + p["look"] * 0.16) * s, hy + (0.16 + nose_vec[1]) * s)
    f = fr.ctx("fg")
    L = 230
    ang = 0.15 + math.sin(t * 9) * 0.25
    B.fish(f, tip[0] + math.cos(ang) * L * 0.47, tip[1] + math.sin(ang) * L * 0.47, L, ang=ang + math.pi, t=t, flip=False)
    return dict(bg_blur=2.5, mid_motion=(10 if stretch > 0.3 else 0, 0), shadows=[("mid", B.cast(ox, oy), 0.45, 6)])


# ------------------------------------------------------------ 12. Final
def shot12(t, fr):
    B.LIGHT[:] = [0.62, -0.78]
    c = fr.ctx("bg")
    hz = 560
    B.sky(c, hz); B.mesas(c, hz, seed=71, scale=1.4); B.ground(c, hz)
    B.whale(c, 360, 760, 900, 0.0, eye=ease(seg(t, 3.0, 3.6)) * 0.85, line_to=False)
    B.scatter(c, hz, seed=73, n_tuft=20, n_flower=16, x0=1100)
    s = 380
    hx, hy = 960, 560
    ox, oy = hx, hy + 3.12 * s
    e = expr_at(t, [(0, T.expr("bon")), (1.5, T.expr("bon", gy=-0.95, gx=0.1)), (2.45, T.expr("bon", gx=-0.95, gy=0.1)), (3.5, T.expr("bon", gx=-0.4, gy=0.0))],
                blinks=(0.9, 2.42, 3.55), blend=0.12)
    p = T.P(e=e, sore=True, dirty=0.6, hat=dict(on=True, tilt=-0.1), seed=9,
            armL=[(-0.36, -2.12), (-0.5, -1.62), (-0.46, -1.15)], armR=[(0.36, -2.12), (0.5, -1.62), (0.46, -1.15)])
    m = fr.ctx("mid")
    T.draw(m, p, ox, oy, s, t=t)
    flap = 0.25 if 2.0 < t < 2.4 else 0.04
    B.fish(m, hx + 10, hy - 0.86 * s - 30, 300, ang=0.05, t=t, flap=flap, curl=0.5)
    return dict(bg_blur=5.0)


SHOTS = [
    ("01_arzu", shot1, 65), ("02_arac", shot2, 23), ("03_zafer", shot3, 88), ("04_tirmanma", shot4, 50),
    ("05_terskose", shot5, 40), ("06_bedel_a", shot6, 45), ("07_bedel_b", shot7, 63), ("08_duraklama", shot8, 100),
    ("09_ikinci", shot9, 50), ("10_terskose2", shot10, 70), ("11_panik", shot11, 50), ("12_final", shot12, 100),
]

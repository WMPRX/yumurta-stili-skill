"""Kum Balıkçısı 2.5D: 12 plan, tek bir tutarlı dünyada gerçek kamera hareketleriyle.

Mekân 1 (plan 1-7): kum gölü (0, 12.5), arkasında gömülü balina (-2, 18.5), kıyıda Tıkır (4.6, 13).
Mekân 2 (plan 8-12): sürüklendiği düzlük; balina (-1.5, 24)'te yeniden gömülür.
Birim: metre. Tıkır'ın çizim birimi 0.5 m (boy ~1.8 m).
"""
import math
import random
import numpy as np
import derin as D
import boya as B
import tikir as T
from sahneler import clamp, ease, eout, ein, seg, lerp, kf, expr_at, pose_mix, sand_spray, puller_pose, FPS

LAKE = (0.0, 12.5, 4.0, 2.6)
WH = (-2.0, 18.5)
WH_W = 9.0
TK = (4.6, 13.0)
BUCKET = (6.2, 13.7)
STOOL = (4.05, 13.9)
SITE2_WH = (-1.5, 24.0)
SITE2_TK = (4.0, 13.5)
SITE2_BUCKET = (5.3, 14.3)

W1 = D.World(sun_dir=(0.42, 0.72, 0.55), lake=LAKE)
W2 = D.World(sun_dir=(0.42, 0.72, 0.55), lake=None)


def in_lake(X, Z, m=1.15):
    return ((X - LAKE[0]) / LAKE[2]) ** 2 + ((Z - LAKE[1]) / LAKE[3]) ** 2 < m


SC1 = D.scatter_world(5, 220, 150, (-16, 18), (3, 45), avoid=lambda X, Z: in_lake(X, Z) or (abs(X - TK[0]) < 1.4 and abs(Z - TK[1]) < 1.2))
SC2 = D.scatter_world(9, 220, 150, (-16, 18), (3, 45), avoid=lambda X, Z: abs(X - SITE2_TK[0]) < 1.6 and abs(Z - SITE2_TK[1]) < 1.4)


def cam_at(keys, t):
    k = kf(t, keys)
    return D.Cam(k["pos"], target=k["target"], fov=k.get("fov", 42))


def U(k):
    """Tıkır'ın çizim birimi (0.5 m) -> piksel."""
    return k * 0.5


def tikir(name, G, pose, between=None, lift=0.0, dark=0.0, caster=True, motion=None, t=0.0, extra=None, pre=None):
    def draw(c, x, y, k):
        if pre:
            pre(c, x, y, k)
        bt = (lambda cc: between(cc, x, y, k)) if between else None
        T.draw(c, pose, x, y, U(k), between=bt, t=t)
        if extra:
            extra(c, x, y, k)
    return D.Obj(name, (G[0], 0, G[1]), draw, height=1.8, width=0.45, caster=caster, lift=lift, dark=dark, motion=motion)


def prop(name, G, fn, h, w=0.3, caster=True, shaded=True, lift=0.0, motion=None):
    return D.Obj(name, (G[0], 0, G[1]), fn, height=h, width=w, caster=caster, shaded=shaded, lift=lift, motion=motion)


def whale_obj(G, rise=0.0, eye=0.0, line_store=None, t=0.0):
    def draw(c, x, y, k):
        pt = B.whale(c, x, y, k * WH_W, rise, eye=eye, mouth=0.0, t=t, line_to=True)
        if line_store is not None:
            line_store["mouth"] = pt
    return D.Obj("balina", (G[0], 0, G[1]), draw, height=3.0 + 2.6 * rise, width=WH_W * 0.45, caster=True)


def bucket_obj(G, t=0.0, tilt=0.0, lift=0.0, caster=True):
    return prop("kova", G, lambda c, x, y, k: B.bucket(c, x, y, k * 0.42, tilt=tilt), 0.42, 0.22, caster=caster, lift=lift)


def stool_obj(G, tilt=0.0):
    return prop("tabure", G, lambda c, x, y, k: B.stool(c, x, y, k * 0.46, tilt=tilt), 0.46, 0.22)


def seated_hold(e, flick=0.0, lean=0.0):
    p = T.seated(e=e, head=(0.08 + 0.04 * lean, -2.82 + 0.08 * lean), head_rot=0.05 * lean, look=-0.25, rot=0.03 * lean)
    p["armL"] = [(-0.31, -1.82), (-0.38, -1.38), (-0.2, -1.25 - 0.12 * flick)]
    p["armR"] = [(0.41, -1.82), (0.3, -1.36), (-0.06, -1.28 - 0.12 * flick)]
    return p


# ------------------------------------------------------------ 1. Arzu: göl yüzeyinden, ters ışık
def shot1(t, sc):
    cam = cam_at([(0, dict(pos=(2.78, 0.13, 10.1), target=(4.6, 0.95, 13.0), fov=52)),
                  (2.6, dict(pos=(2.9, 0.14, 10.35), target=(4.6, 0.97, 13.0), fov=52))], t)
    # güneş tam arkada, hafif sağda ve alçak: hale başın yanında
    sun = D.norm(D.v3(4.95, 2.3, 13.4) - cam.C)
    W1.L = sun
    lean = kf(t, [(0, 0.0), (0.9, 1.0)])
    flick = math.sin(math.pi * seg(t, 1.25, 1.55)) if 1.25 <= t <= 1.55 else 0.0
    p = seated_hold(expr_at(t, [(0, "notr"), (0.9, "kararli")], blinks=(0.55, 2.2)), flick, lean)
    flt = (2.99, 11.1)
    fx, fy, fz = cam.proj((flt[0], 0.0, flt[1]))

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        hand = J((-0.13, -1.27 - 0.12 * flick))
        rp = B.rod_points(hand, 2.55 + 0.05 * flick, U(k) * 3.2, -0.12 + 0.08 * flick)
        B.line(cc, rp[-1], (fx + 10, fy - cam.px(0.12, fz)), sag=8, w=2.5)
        B.rod(cc, rp, U(k) * 0.09)

    def extra(c, x, y, k):
        pass
    objs = [whale_obj((WH[0], WH[1])),
            stool_obj((TK[0], TK[1] + 0.05)),
            tikir("tikir", TK, p, between, t=t, dark=0.15),
            bucket_obj(BUCKET),
            prop("samandira", flt, lambda c, x, y, k: B.float_(c, x, y, k * 0.07, clip_y=y + k * 0.012), 0.12, 0.07, caster=False, shaded=True)]
    img = D.render(W1, cam, objs, scale=sc, t=t, zf=3.6, ap=0.035, sun_disc=sun, scatter=SC1, ripple_phase=t * 0.25, bloom=0.9)
    W1.L = D.norm(D.v3(0.42, 0.72, 0.55))
    return img


# ------------------------------------------------------------ 2. Şamandıra: yukarıdan, göl yüzeyi
def shot2(t, sc):
    F = (1.0, 12.0)
    cam = D.Cam((1.04, 0.5, 11.42), target=(F[0], 0.0, F[1]), fov=34)
    tw = 0.0
    for tt in (0.1, 0.28):
        if tt <= t < tt + 0.1:
            tw = math.sin(math.pi * (t - tt) / 0.1)
    sink = ein(seg(t, 0.46, 0.72))
    gl = max(0, math.sin(math.pi * seg(t, 0.0, 0.3)))

    def splash(c):
        if t > 0.46:
            for kk in range(3):
                u = seg(t, 0.46 + kk * 0.08, 0.95 + kk * 0.08)
                if u <= 0:
                    continue
                R = 0.05 + 0.45 * u
                pts = [cam.proj((F[0] + math.cos(a) * R, 0, F[1] + math.sin(a) * R)) for a in np.linspace(0, 2 * math.pi, 48)]
                c.set_line_width(6 * (1 - u) + 1.5); c.move_to(*pts[0][:2])
                for q in pts[1:]:
                    c.line_to(*q[:2])
                c.close_path(); c.set_source_rgba(*B.hexrgb("#8a7c58"), 0.55 * (1 - u)); c.stroke()

    def draw_float(c, x, y, k):
        r = k * 0.07
        top = (x + r * 0.28, y - r * 1.75 + 14 * tw + sink * r * 2.2)
        B.line(c, (x + 90, -40), top, sag=0, w=3)
        B.float_(c, x, y + 14 * tw, r, sink=sink, glint=gl, clip_y=y + r * 0.2, tilt=0.06 * tw)
        if t > 0.46:
            B.particles(c, sand_spray(21, t, (x, y), 50, 0.6, 520, life=0.45, t0=0.46, t1=0.58, size=(3, 7)))
    objs = [prop("samandira", F, draw_float, 0.12, 0.07, caster=True)]
    return D.render(W1, cam, objs, scale=sc, t=t, zf=1.0, ap=0.012, scatter=None, ripple_phase=t * 0.6, extra_ground=splash)


# ------------------------------------------------------------ 3. Küçük zafer: yakın plan, gerçek dolly
def shot3(t, sc):
    cam = cam_at([(0, dict(pos=(4.0, 1.42, 11.05), target=(4.62, 1.38, 13.0), fov=40)),
                  (3.52, dict(pos=(4.1, 1.42, 11.35), target=(4.62, 1.4, 13.0), fov=40))], t, )
    recoil = math.sin(math.pi * seg(t, 1.0, 1.5)) if 1.0 <= t <= 1.5 else 0.0
    e = expr_at(t, [(0, T.expr("gurur", gx=0.5)), (1.05, "sok"), (1.5, "notr"), (2.35, T.expr("sinsi", gx=-0.2, gy=0.0))],
                blinks=(1.55, 1.75, 1.95, 3.2))
    look = kf(t, [(0, 0.35), (1.0, 0.35), (1.1, 0.0), (2.3, 0.0), (2.5, -0.15)])
    p = T.seated(e=e, look=look, head_rot=0.06 - 0.12 * recoil + math.sin(t * 2.0) * 0.02, dirty=0.75 if t > 1.15 else 0.0,
                 armL=[(-0.31, -1.82), (0.2, -1.95), (0.62, -2.42)], armR=[(0.41, -1.82), (0.95, -1.95), (1.18, -2.5)],
                 handL=("tut", -0.6), handR=("tut", -0.9))
    p["head"] = (0.08 - 0.05 * recoil, -2.82)
    flop = 1.0 if t < 1.0 or t > 1.4 else 0.3

    def between(cc, x, y, k):
        s = U(k)
        fx, fy = x + s * 1.02, y - s * 2.6 + math.sin(t * 9) * 3
        B.fish(cc, fx, fy, s * 1.0, ang=0.12 + math.sin(t * 7) * 0.05, t=t, flap=flop, mouth="acik" if 0.95 < t < 1.35 else "kapali", flip=True)
        if 1.0 <= t <= 1.45:
            B.particles(cc, sand_spray(31, t, (fx - s * 0.5, fy + s * 0.04), 160, 0.35, 1500 * s / 520, life=0.3, g=200, t0=1.0, t1=1.15,
                                       dir_ang=math.pi + 0.15, size=(4 * s / 520, 10 * s / 520)))
    objs = [whale_obj((WH[0], WH[1])), bucket_obj(BUCKET), stool_obj((TK[0], TK[1] + 0.05)),
            tikir("tikir", TK, p, between, t=t)]
    return D.render(W1, cam, objs, scale=sc, t=t, zf=1.95, ap=0.022, scatter=SC1, ripple_phase=t * 0.2)


# ------------------------------------------------------------ 4. Tırmanma: geniş, yavaş yan kayma
def shot4(t, sc):
    cam = cam_at([(0, dict(pos=(0.2, 1.75, 2.4), target=(0.6, 2.2, 14.0), fov=46)),
                  (2.0, dict(pos=(0.5, 1.75, 2.4), target=(0.8, 2.2, 14.0), fov=46))], t)
    store = {}
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
    target_w = (-0.4, 0.0, 17.6)
    tx, ty_, tz = cam.proj(target_w)

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        hand = J(p["armL"][2])
        if t < 0.4:
            ang, bend = -1.4, 0.0
        elif t < 0.75:
            ang, bend = lerp(-1.4, -2.75, ease(seg(t, 0.4, 0.6))), 0.2 * math.sin(math.pi * seg(t, 0.4, 0.75))
        else:
            ang, bend = -2.75 + 0.15 * yank, -0.35 - 0.35 * yank - (0.15 if t > 0.9 else 0)
        rp = B.rod_points(hand, ang, U(k) * 3.6, bend)
        tip = rp[-1]
        if t >= 0.45:
            if t < 0.8:
                u = eout(seg(t, 0.45, 0.8))
                fl = (lerp(tip[0], tx, u), lerp(tip[1], ty_, u) - 260 * math.sin(math.pi * u))
            else:
                fl = (tx, ty_)
            B.line(cc, tip, fl, sag=40 if t < 0.85 else 0, w=2.2)
            if t < 0.95:
                B.float_(cc, fl[0], fl[1], 12, sink=ein(seg(t, 0.82, 0.95)), clip_y=ty_ + 3)
        B.rod(cc, rp, U(k) * 0.1)
        if t < 0.35:
            u = seg(t, 0.0, 0.35)
            bx, by, _ = cam.proj((BUCKET[0], 0.45, BUCKET[1]))
            fx, fy = lerp(x + U(k) * 0.9, bx, u), lerp(y - U(k) * 2.5, by, u) - 90 * math.sin(math.pi * u)
            B.fish(cc, fx, fy, U(k) * 0.55, ang=u * 4, t=t)
        for tyy in (1.1, 1.55):
            B.particles(cc, sand_spray(int(tyy * 10), t, J((-0.62, 0.0)), 40, 0.5, 420, life=0.5, t0=tyy - 0.05, t1=tyy + 0.05,
                                       dir_ang=-math.pi * 0.85, size=(2, 5)))
    bt = 0.06 * math.sin(math.pi * seg(t, 0.33, 0.6))
    objs = [whale_obj((WH[0], WH[1])), tikir("tikir", TK, p, between, t=t), bucket_obj(BUCKET, tilt=bt), stool_obj(STOOL)]
    return D.render(W1, cam, objs, scale=sc, t=t, zf=12.0, ap=0.008, scatter=SC1, ripple_phase=t * 0.3)


# ------------------------------------------------------------ 5. Ters köşe 1: balina yükselir, kamera geri çekilir
def shot5(t, sc):
    cam = cam_at([(0, dict(pos=(0.5, 1.75, 2.4), target=(0.8, 2.2, 14.0), fov=46)),
                  (1.6, dict(pos=(0.3, 1.85, 1.6), target=(0.6, 2.45, 14.0), fov=46))], t, )
    rise = eout(seg(t, 0.0, 1.25))
    eye = ease(seg(t, 0.65, 1.1))
    store = {}
    p = puller_pose(yank=0.4)
    p["e"] = T.expr("gergin") if t < 0.35 else T.expr("sok", size=1.1 + 0.2 * ease(seg(t, 0.35, 1.0)), mouth="cizgi")

    def wdraw(c, x, y, k):
        w = k * WH_W
        pt = B.whale(c, x, y, w, rise, eye=eye, mouth=0.0, t=t, line_to=True)
        store["mouth"] = pt
        rnd = random.Random(5); items = []
        hh = w * (0.32 + 0.3 * rise) + w * 0.12 * rise
        for kk in range(22):
            u = rnd.uniform(-0.48, 0.55)
            x0 = x + u * w; top = y - hh * max(0.1, 1 - (u / 0.62) ** 2)
            for j in range(16):
                ph = (t * 1.6 + j / 16 + rnd.random()) % 1
                items.append((x0 + rnd.gauss(0, 8), top + (y - top) * ph ** 1.6, rnd.uniform(3, 8) * k / 60, 0, 18 * ph))
        if t > 0.05:
            B.particles(c, items, alpha=0.85 * min(1, t / 0.2))

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        rp = B.rod_points(J(p["armL"][2]), -2.6, U(k) * 3.6, -0.55 + 0.4 * rise)
        if "mouth" in store:
            B.line(cc, rp[-1], store["mouth"], w=2.2)
        B.rod(cc, rp, U(k) * 0.1)
    objs = [D.Obj("balina", (WH[0], 0, WH[1]), wdraw, height=3.0 + 2.6 * rise, width=WH_W * 0.45),
            tikir("tikir", TK, p, between, t=t), bucket_obj(BUCKET), stool_obj(STOOL)]
    return D.render(W1, cam, objs, scale=sc, t=t, zf=12.0, ap=0.008, scatter=SC1, ripple_phase=t * 2.0)


# ------------------------------------------------------------ 6. Bedel a: Tıkır balinaya doğru uçar (derinliğe doğru)
def shot6(t, sc):
    cam = cam_at([(0, dict(pos=(2.2, 1.6, 4.5), target=(0.5, 2.1, 16.0), fov=50)),
                  (1.8, dict(pos=(2.0, 1.6, 4.8), target=(0.2, 2.1, 16.0), fov=50))], t)
    up = 1 - ein(seg(t, 0.0, 1.0))
    u = seg(t, 0.05, 1.35)
    P0, P1 = D.v3(4.6, 1.0, 13.0), D.v3(-1.2, 0.8, 18.0)
    P = P0 + (P1 - P0) * (ein(u) * 0.35 + u * 0.65); P[1] += 0.9 * math.sin(math.pi * u)
    flap = math.sin(t * 28)
    p = T.P(rot=-1.45, look=-0.2, e=T.expr("panik"),
            legL=[(-0.17, -1.25), (-0.35 + 0.15 * flap, -0.66), (-0.3 + 0.3 * flap, -0.06)],
            legR=[(0.17, -1.25), (0.35 - 0.15 * flap, -0.66), (0.3 - 0.3 * flap, -0.06)],
            armL=[(-0.36, -2.12), (-0.3, -2.7), (-0.1, -3.25)], armR=[(0.36, -2.12), (0.25, -2.7), (0.05, -3.3)],
            handL=("tut", -1.5), handR=("tut", -1.5), hat=dict(on=False))
    tx, ty_, tz = cam.proj((WH[0], 1.6 * up, WH[1]))

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        rp = B.rod_points(J((0.0, -3.3)), math.pi + 0.05, U(k) * 2.2, 0.1)
        B.line(cc, rp[-1], (tx, ty_), w=2.2)
        B.rod(cc, rp, U(k) * 0.1)

    def tail_draw(c, x, y, k):
        B.tail(c, x, y, k * 4.0, up, t=t)
        B.particles(c, sand_spray(61, t, (x, y), 260, 0.7, k * 9, life=1.0, t0=0.0, t1=0.9, size=(k * 0.03, k * 0.09)))
    hu = seg(t, 0.1, 1.8)
    hat_P = (lerp(4.5, 5.6, hu), 1.9 + 1.6 * math.sin(math.pi * 0.5 * hu) - 1.2 * hu * hu, lerp(13.0, 13.6, hu))

    def hat_draw(c, x, y, k):
        c.save(); c.translate(x, y); c.scale(U(k), U(k)); T.draw_hat(c, 0, 0, t * 5); c.restore()
    tu = seg(t, 0.1, 1.2)
    objs = [D.Obj("kuyruk", (WH[0], 0, WH[1]), tail_draw, height=4.0 * up, width=1.5, caster=up > 0.1),
            D.Obj("sapka", (hat_P[0], 0, hat_P[2]), hat_draw, lift=hat_P[1], caster=False),
            D.Obj("tabure", (lerp(TK[0], TK[0] + 1.4, eout(tu)), 0, TK[1] + 0.05), lambda c, x, y, k: B.stool(c, x, y, k * 0.46, tilt=eout(tu) * 4.5), height=0.46, width=0.22),
            bucket_obj(BUCKET, tilt=0.4 * math.sin(math.pi * seg(t, 0.1, 0.6)))]
    if t < 1.5:
        objs.append(tikir("tikir", (P[0], P[2]), p, between, lift=P[1], caster=False, t=t, motion=(22 if 0.05 < t < 1.4 else 0, 10)))
    return D.render(W1, cam, objs, scale=sc, t=t, zf=13.0, ap=0.008, scatter=SC1, ripple_phase=t * 1.2)


# ------------------------------------------------------------ 7. Bedel b: kum kayağı (kamera onunla birlikte geri gider)
def shot7(t, sc):
    # yan takip: Tıkır sağa doğru sürüklenir, kamera onunla aynı hızda yana kayar (paralaks: yakın otlar hızlı, uzak kayalar yavaş)
    speed = 5.0
    PX = -6.0 + speed * t
    PZ = 30.0 + 0.3 * math.sin(t * 2.0)
    bump = abs(math.sin(t * 7.5))
    back = lerp(4.0, 4.4, ease(t / 2.52))
    cam = D.Cam((PX - 0.9, 1.25 + 0.03 * bump, PZ - back), target=(PX - 0.2, 1.3, PZ), fov=44)
    face = int(t / 0.6) % 2
    p = T.P(rot=0.05 * math.sin(t * 5), look=0.0, hip=(0, -1.05), chest=(0, -2.0), head=(0, -2.92),
            legL=[(-0.17, -1.05), (-0.48, -0.6), (-0.5, -0.06)], legR=[(0.17, -1.05), (0.48, -0.6), (0.5, -0.06)],
            armL=[(-0.36, -1.92), (-0.4, -1.55), (-0.08, -1.42)], armR=[(0.36, -1.92), (0.42, -1.55), (0.1, -1.4)],
            handL=("tut", 0.3), handR=("tut", 0.3),
            e=T.expr("keyif") if face == 0 else T.expr("panik"), hat=dict(on=True, tilt=-0.15, dy=-0.04 * bump))

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        rp = B.rod_points(J((0.0, -1.41)), -0.25, U(k) * 2.2, 0.15)
        B.line(cc, rp[-1], (2200, rp[-1][1] + 60), sag=20, w=3)
        B.rod(cc, rp, U(k) * 0.1)

    def spray(c, x, y, k):
        J = T.joints(p, x, y, U(k))
        for sx in (-1, 1):
            B.particles(c, sand_spray(70 + sx, t, J((sx * 0.55 - 0.3, 0.0)), 380, 0.3, k * 2.6, life=0.5, g=k * 5.0, t0=0, t1=2.6,
                                      dir_ang=-math.pi / 2 - 1.0 + sx * 0.35, size=(k * 0.005, k * 0.014)))
    objs = [tikir("tikir", (PX, PZ), p, between, lift=0.03 * bump, t=t, pre=spray)]
    return D.render(W2, cam, objs, scale=sc, t=t, zf=back, ap=0.012, scatter=SC2, lake_on=False)


# ------------------------------------------------------------ 8. Sessiz duraklama (mekân 2)
def shot8(t, sc):
    cam = D.Cam((3.2, 1.5, 7.0), target=(1.8, 1.65, 17.0), fov=44)
    up = ease(seg(t, 0.0, 0.3)) * (1 - ein(seg(t, 0.35, 0.75)))
    e = expr_at(t, [(0, "bon"), (3.4, T.expr("bon", gx=-0.85)), (3.75, T.expr("bon", gx=0.0))], blinks=(2.3, 3.15))

    def buried(c, x, y, k):
        s = U(k)
        c.save(); c.translate(x, y - s * 0.55); c.scale(s, s)
        T.head(c, 0, 0, e, look=0.0, rot=-0.06, hat=dict(on=True, tilt=-0.38, dx=-0.12, dy=0.06), dirty=0.8, seed=8, t=t)
        c.restore()
        B.fill(c, lambda cc: B.blob(cc, [(x - s * 1.3, y + s * 0.08), (x - s * 0.5, y - s * 0.28), (x + s * 0.5, y - s * 0.27), (x + s * 1.35, y + s * 0.08), (x, y + s * 0.2)], 8),
               B.mats()["kum"], shade=0.4, hi=0.35)
        pts = [(x + s * 1.3, y + 2), (x + s * 1.4, y - s * 0.75), (x + s * 1.8, y - s * 1.0), (x + s * 1.95, y - s * 0.62), (x + s * 1.5, y - s * 0.5),
               (x + s * 1.56, y - s * 1.1), (x + s * 2.1, y - s * 1.35), (x + s * 2.15, y - s * 1.65)]
        B.fill(c, lambda cc: B.tube(cc, pts, s * 0.09, s * 0.04, n=6), B.mats()["bambu"], shade=0.5, hi=0.4)

    def tail_draw(c, x, y, k):
        B.tail(c, x, y, k * 3.4, up, t=t)
        B.particles(c, sand_spray(81, t, (x, y), 220, 0.8, k * 7, life=0.9, t0=0.45, t1=0.6, size=(k * 0.03, k * 0.08)))
    objs = [D.Obj("kuyruk", (SITE2_WH[0], 0, SITE2_WH[1]), tail_draw, height=3.4 * up, width=1.2, caster=up > 0.1),
            D.Obj("gomulu", (SITE2_TK[0], 0, SITE2_TK[1]), buried, height=0.6, width=0.5)]
    if t >= 1.0:
        bu = seg(t, 1.0, 1.25)
        lift = lerp(7.0, 0.0, bu * bu)
        if t > 1.25:
            lift = 0.2 * math.sin(math.pi * seg(t, 1.25, 1.45)) if t < 1.45 else 0.0
        objs.append(bucket_obj((SITE2_TK[0] - 0.95, SITE2_TK[1] - 0.1), tilt=0.15 * (1 - seg(t, 1.25, 1.5)), lift=lift, caster=lift < 0.3))

    def dust(c):
        if 1.25 <= t <= 1.8:
            x, y, z = cam.proj((SITE2_TK[0] - 0.95, 0, SITE2_TK[1] - 0.1))
            B.particles(c, sand_spray(82, t, (x, y), 60, 0.9, 380, life=0.45, t0=1.25, t1=1.3, size=(2, 5)))
    return D.render(W2, cam, objs, scale=sc, t=t, zf=8.5, ap=0.006, scatter=SC2, lake_on=False, overlay=dust)


# ------------------------------------------------------------ 9. İkinci deneme: yerde alçak, güneş kadrajda
def shot9(t, sc):
    cam = cam_at([(0, dict(pos=(2.95, 0.5, 9.6), target=(4.0, 0.62, 13.4), fov=46)),
                  (2.0, dict(pos=(3.0, 0.5, 9.75), target=(4.0, 0.62, 13.4), fov=46))], t)
    hx = math.tan(math.radians(46) / 2) * 16 / 9
    sun = D.norm(cam.f + cam.r * hx * 0.93 + cam.u * math.tan(math.radians(23)) * 0.92)
    W2.L = D.norm(D.v3(sun[0], max(sun[1], 0.35), sun[2]))
    turn = ease(seg(t, 1.0, 1.3))
    e = expr_at(t, [(0, T.expr("kararli", gy=0.7, gx=0.1)), (1.05, T.expr("sinsi", gx=0.0, gy=0.0))], blinks=(0.45,))
    thread = math.sin(t * 6) * 0.04 if t < 1.0 else 0
    p = T.P(hip=(0, -0.3), chest=(0.02, -1.25), head=(0.04, -2.17), look=lerp(0.1, -0.05, turn), head_rot=lerp(0.12, 0.0, turn),
            legL=[(-0.17, -0.3), (-0.75, -0.75), (-1.05, -0.06)], legR=[(0.17, -0.3), (0.65, -0.68), (1.05, -0.06)],
            armL=[(-0.33, -1.18), (-0.38, -0.72), (-0.08 + thread, -0.9)], armR=[(0.37, -1.18), (0.45, -0.72), (0.14 - thread, -0.92)],
            handL=("tut", -0.3), handR=("tut", 2.8), e=e, dirty=0.8, hat=dict(on=True, tilt=-0.25, dx=-0.08), seed=9)

    def between(cc, x, y, k):
        J = T.joints(p, x, y, U(k))
        a = J((-0.02 + thread, -1.0)); b = J((0.08 - thread, -1.02))
        cc.set_line_width(3); cc.set_source_rgb(*B.hexrgb("#9aa3a0")); cc.move_to(a[0], a[1] + 20); cc.line_to(a[0], a[1] - 7)
        cc.arc_negative(a[0] + 6, a[1] - 7, 6, math.pi, 0.2); cc.stroke()
        B.fill(cc, lambda q: B.tube(q, [(b[0] - 2, b[1] - 12), (b[0] + 7, b[1] - 23), (b[0] + 1, b[1] - 34)], 5, 4), B.mats()["yanak"], shade=0.3, hi=0.4)
    wob = 0.12 * math.sin(t * 30) * (1 if 1.5 < t < 1.85 else 0)
    objs = [tikir("tikir", SITE2_TK, p, between, t=t), bucket_obj(SITE2_BUCKET, tilt=wob),
            prop("samandira", (2.75, 11.7), lambda c, x, y, k: B.float_(c, x, y, k * 0.07), 0.12, 0.07)]
    img = D.render(W2, cam, objs, scale=sc, t=t, zf=3.9, ap=0.02, sun_disc=sun, scatter=SC2, lake_on=False, bloom=0.9)
    W2.L = D.norm(D.v3(0.42, 0.72, 0.55))
    return img


# ------------------------------------------------------------ 10. Ters köşe 2: yakın-orta, kamera geri kaçar
def shot10(t, sc):
    rec = eout(seg(t, 0.8, 1.0)) * (1 - 0.6 * seg(t, 1.0, 1.6))
    back = ease(seg(t, 0.8, 2.8))
    cam = D.Cam((lerp(3.62, 3.57, back), 0.98, lerp(11.85, 11.6, back)), target=(4.05, 0.9, 13.4), fov=40)
    e = expr_at(t, [(0, "sinsi"), (0.82, "sok"), (1.15, "aci")], blinks=(0.3,))
    upa = eout(seg(t, 0.85, 1.05))
    p = T.P(hip=(0, -0.3), chest=(0.02, -1.25), head=(0.04 - 0.05 * rec, -2.17), head_rot=-0.15 * rec, look=0.05,
            legL=[(-0.17, -0.3), (-0.75, -0.75), (-1.05, -0.06)], legR=[(0.17, -0.3), (0.65, -0.68), (1.05, -0.06)],
            armL=[(-0.33, -1.18), lerp((-0.45, -0.75), (-0.95, -1.5), upa), lerp((-0.1, -0.95), (-1.2, -2.2), upa)],
            armR=[(0.37, -1.18), lerp((0.5, -0.75), (0.95, -1.5), upa), lerp((0.3, -1.1), (1.2, -2.25), upa)],
            handL=("tut", 0.5) if upa < 0.5 else ("acik", -2.2), handR=("tut", -0.5) if upa < 0.5 else ("acik", -1.0),
            e=e, dirty=0.8, hat=dict(on=True, tilt=-0.25, dx=-0.08), seed=9)
    bx, by, bz = cam.proj((SITE2_BUCKET[0], 0.42, SITE2_BUCKET[1]))
    st = {}

    def extra(c, x, y, k):
        J = T.joints(p, x, y, U(k))
        hx, hy = J(p["head"])
        st["nose"] = (hx + 0.06 * U(k), hy + 0.16 * U(k)); st["s"] = U(k)

    def fish_layer(c):
        if "nose" not in st:
            return
        nose = st["nose"]
        s = st["s"] * 1.6
        if t < 0.82:
            u = seg(t, 0.48, 0.82)
            if u > 0:
                fx = lerp(bx, nose[0] + 20, u); fy = lerp(by, nose[1] + s * 0.4, u) - s * 0.9 * math.sin(math.pi * u)
                fs, fc_ = D.new_layer(1.0) if False else (None, c)
                B.fish(c, fx, fy, s * 0.5, ang=lerp(-0.6, -2.4, u), t=t)
        else:
            sw = math.sin(t * 7) * 0.3 * (1 - seg(t, 1.2, 2.8) * 0.6)
            ang = -math.pi / 2 - 0.55 + sw
            L = s * 0.5
            B.fish(c, nose[0] - math.cos(ang) * L * 0.5, nose[1] - math.sin(ang) * L * 0.5, L, ang=ang, t=t, flap=1.2)
    bt = 0.15 * math.sin(math.pi * seg(t, 0.45, 0.75))
    objs = [bucket_obj(SITE2_BUCKET, tilt=bt), tikir("tikir", SITE2_TK, p, None, t=t, extra=extra, caster=False)]
    zf = float((D.v3(SITE2_TK[0], 0.9, SITE2_TK[1]) - cam.C) @ cam.f)
    return D.render(W2, cam, objs, scale=sc, t=t, zf=zf, ap=0.03, scatter=SC2, lake_on=False, overlay=fish_layer)


# ------------------------------------------------------------ 11. Panik: ayakta döner
def shot11(t, sc):
    cam = D.Cam((3.45, 1.15, 8.9), target=(4.0, 1.0, 13.5), fov=44)
    stretch = 0.0
    for ty in (0.2, 0.9, 1.5):
        if ty <= t <= ty + 0.32:
            u = (t - ty) / 0.32
            stretch = max(stretch, math.sin(math.pi * min(1, u * 1.6)) if u < 0.62 else 0.0)
    spin = math.sin(t * 5.5)
    nv = (0.25 + 1.6 * stretch, 0.1 + 0.35 * stretch)
    p = T.P(e=T.expr("panik", tears=1.0), look=0.35 * spin, rot=0.06 * spin - 0.05 * stretch,
            nose=nv, dirty=0.8, hat=dict(on=True, tilt=-0.3 + 0.1 * spin, dx=-0.08), seed=9,
            armL=[(-0.36, -2.12), (0.1, -2.3), (0.55 + nv[0] * 0.6, -2.92)], armR=[(0.36, -2.12), (0.8, -2.25), (0.9 + nv[0] * 0.6, -2.88)],
            handL=("tut", 0.0), handR=("tut", 0.0))

    def extra(c, x, y, k):
        J = T.joints(p, x, y, U(k))
        hx, hy = J(p["head"])
        tip = (hx + (nv[0] + p["look"] * 0.16) * U(k), hy + (0.16 + nv[1]) * U(k))
        L = U(k) * 1.2
        ang = 0.15 + math.sin(t * 9) * 0.25
        B.fish(c, tip[0] + math.cos(ang) * L * 0.47, tip[1] + math.sin(ang) * L * 0.47, L, ang=ang + math.pi, t=t)
    objs = [bucket_obj((SITE2_BUCKET[0] + 0.5, SITE2_BUCKET[1] + 0.6), tilt=1.4),
            tikir("tikir", (SITE2_TK[0] + 0.1 * spin, SITE2_TK[1]), p, None, t=t, extra=extra, motion=(10 if stretch > 0.3 else 0, 0))]
    return D.render(W2, cam, objs, scale=sc, t=t, zf=4.6, ap=0.015, scatter=SC2, lake_on=False)


# ------------------------------------------------------------ 12. Final: sabit yakın-orta, arkada balinanın gözü açılır
def shot12(t, sc):
    cam = D.Cam((3.55, 1.58, 11.55), target=(4.0, 1.5, 13.5), fov=40)
    e = expr_at(t, [(0, T.expr("bon")), (1.5, T.expr("bon", gy=-0.95, gx=0.1)), (2.45, T.expr("bon", gx=-0.95, gy=0.1)), (3.5, T.expr("bon", gx=-0.4, gy=0.0))],
                blinks=(0.9, 2.42, 3.55), blend=0.12)
    p = T.P(e=e, sore=True, dirty=0.6, hat=dict(on=True, tilt=-0.1), seed=9,
            armL=[(-0.36, -2.12), (-0.5, -1.62), (-0.46, -1.15)], armR=[(0.36, -2.12), (0.5, -1.62), (0.46, -1.15)])
    flap = 0.25 if 2.0 < t < 2.4 else 0.04

    def extra(c, x, y, k):
        J = T.joints(p, x, y, U(k))
        hx, hy = J(p["head"])
        B.fish(c, hx + 5, hy - 0.86 * U(k) - U(k) * 0.08, U(k) * 0.8, ang=0.05, t=t, flap=flap, curl=0.5)
    objs = [whale_obj(SITE2_WH, 0.0, eye=ease(seg(t, 3.0, 3.6)) * 0.85, t=t),
            tikir("tikir", SITE2_TK, p, None, t=t, extra=extra)]
    return D.render(W2, cam, objs, scale=sc, t=t, zf=1.95, ap=0.02, scatter=SC2, lake_on=False)


SHOTS = [
    ("01_arzu", shot1, 65), ("02_arac", shot2, 23), ("03_zafer", shot3, 88), ("04_tirmanma", shot4, 50),
    ("05_terskose", shot5, 40), ("06_bedel_a", shot6, 45), ("07_bedel_b", shot7, 63), ("08_duraklama", shot8, 100),
    ("09_ikinci", shot9, 50), ("10_terskose2", shot10, 70), ("11_panik", shot11, 50), ("12_final", shot12, 100),
]

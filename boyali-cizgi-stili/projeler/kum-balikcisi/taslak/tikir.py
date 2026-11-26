"""Tıkır: kum balıkçısı. Birim: baş genişliği = 1. Orijin: ayakların arası (zemin).
Yerel koordinatlarda y yukarı NEGATİF (cairo gibi)."""
import math
import random
import cairo
from boya import mats, fill, solid, ellipse, blob, tube, poly, hexrgb, INK, mix

# ------------------------------------------------------------ ifadeler
EXPR = {
    "notr":    dict(size=1.0, open=0.85, brow=0.0, mouth="cizgi"),
    "kararli": dict(size=0.95, open=0.55, brow=-0.6, mouth="cizgi"),
    "gurur":   dict(size=1.0, open=0.75, brow=0.3, mouth="sirit"),
    "keyif":   dict(size=1.05, open=0.9, brow=0.5, mouth="sirit"),
    "sinsi":   dict(size=0.95, open=0.42, brow=-0.7, mouth="sinsi", gy=0.25),
    "sok":     dict(size=1.18, open=1.0, brow=1.0, mouth="o", mo=0.35, pupil=0.7),
    "panik":   dict(size=1.2, open=1.0, brow=1.0, mouth="o", mo=1.0, pupil=0.7, tears=0.6),
    "endise":  dict(size=1.0, open=0.9, brow=0.9, mouth="kas"),
    "gergin":  dict(size=0.95, open=0.25, brow=-0.9, mouth="dis"),
    "aci":     dict(size=1.05, open=0.3, brow=1.0, mouth="dis", tears=1.0),
    "bon":     dict(size=1.05, open=0.8, brow=0.1, mouth="cizgi", pupil=0.8),
    "kirp":    dict(size=1.0, open=0.0, brow=0.0, mouth="cizgi"),
}


def expr(name, **over):
    e = dict(size=1.0, open=0.85, brow=0.0, mouth="cizgi", mo=0.5, gx=0.0, gy=0.0, pupil=1.0, tears=0.0)
    e.update(EXPR[name]); e.update(over)
    return e


def lerp_expr(a, b, t):
    out = dict(a)
    for k in ("size", "open", "brow", "mo", "gx", "gy", "pupil", "tears"):
        out[k] = a[k] + (b[k] - a[k]) * t
    out["mouth"] = b["mouth"] if t > 0.5 else a["mouth"]
    return out


# ------------------------------------------------------------ pozlar
def base_pose():
    return dict(
        rot=0.0, hip=(0, -1.25), chest=(0, -2.2), head=(0, -3.12), head_rot=0.0, look=0.0,
        legL=[(-0.17, -1.25), (-0.2, -0.64), (-0.22, -0.06)], legR=[(0.17, -1.25), (0.2, -0.64), (0.22, -0.06)],
        bootL=-1, bootR=1,
        armL=[(-0.36, -2.12), (-0.52, -1.62), (-0.46, -1.15)], armR=[(0.36, -2.12), (0.52, -1.62), (0.46, -1.15)],
        handL=("acik", 1.6), handR=("acik", 1.5),
        e=expr("notr"), hat=dict(on=True, tilt=0.0, dx=0.0, dy=0.0), nose=None, sore=False,
        dirty=0.0, legs=True, body=True, seed=1,
    )


def P(**kw):
    p = base_pose(); p.update(kw); return p


def seated(**kw):
    """Tabureye oturmuş, oltayı iki eliyle önde tutuyor."""
    p = base_pose()
    p.update(hip=(0, -0.95), chest=(0.05, -1.9), head=(0.08, -2.82),
             legL=[(-0.17, -0.95), (-0.55, -0.98), (-0.5, -0.06)], legR=[(0.17, -0.95), (0.55, -0.98), (0.52, -0.06)],
             armL=[(-0.31, -1.82), (-0.2, -1.38), (0.05, -1.3)], armR=[(0.41, -1.82), (0.45, -1.38), (0.2, -1.32)],
             handL=("tut", 0.2), handR=("tut", 0.2))
    p.update(kw); return p


# ------------------------------------------------------------ yardımcılar
def _hand(c, x, y, kind, ang, r=0.17):
    m = mats()
    c.save(); c.translate(x, y); c.rotate(ang)
    if kind == "acik":
        for k in range(4):
            a = -0.65 + k * 0.42
            fill(c, lambda cc, a=a: tube(cc, [(0, 0), (math.cos(a) * r * 1.8, math.sin(a) * r * 1.8)], r * 0.42, r * 0.34), m["eldiven"], shade=0.5, hi=0.3)
        fill(c, lambda cc: tube(cc, [(0, 0), (r * 0.6, r * 1.5)], r * 0.44, r * 0.36), m["eldiven"], shade=0.5, hi=0.3)
        fill(c, lambda cc: ellipse(cc, r * 0.3, 0, r * 0.95, r * 0.85), m["eldiven"], shade=0.5, hi=0.3)
    else:  # tut / yumruk
        fill(c, lambda cc: ellipse(cc, r * 0.25, 0, r * 1.05, r * 0.9), m["eldiven"], shade=0.55, hi=0.35)
        c.set_line_width(r * 0.1); c.set_source_rgba(*INK, 0.45)
        for k in range(3):
            yy = -r * 0.45 + k * r * 0.42
            c.move_to(r * 0.75, yy); c.line_to(r * 1.1, yy + r * 0.05); c.stroke()
        fill(c, lambda cc: tube(cc, [(-r * 0.1, -r * 0.55), (r * 0.6, -r * 0.85)], r * 0.42, r * 0.36), m["eldiven"], shade=0.4, hi=0.4)
    c.restore()


def _boot(c, x, y, d):
    m = mats()
    pts = [(x - 0.16 * d, y - 0.22), (x + 0.12 * d, y - 0.2), (x + 0.36 * d, y - 0.07), (x + 0.46 * d, y - 0.16), (x + 0.42 * d, y + 0.02), (x - 0.16 * d, y + 0.03)]
    fill(c, lambda cc: blob(cc, pts, 6), m["tulum"], shade=0.6, hi=0.3)
    c.set_line_width(0.035); c.set_source_rgba(*hexrgb("#5a2a1f"), 0.8)
    c.move_to(x - 0.17 * d, y - 0.02); c.line_to(x + 0.42 * d, y - 0.0); c.stroke()


def _leg(c, pts, d):
    m = mats()
    fill(c, lambda cc: tube(cc, pts, 0.3, 0.24), m["tulum"], shade=0.6, hi=0.3)
    _boot(c, pts[-1][0], pts[-1][1] + 0.06, d)


def head(c, cx, cy, e, look=0.0, rot=0.0, hat=None, nose=None, sore=False, dirty=0.0, seed=1, t=0.0):
    m = mats()
    c.save(); c.translate(cx, cy); c.rotate(rot)
    fx = look * 0.12
    # yanak/kulak lekesi arkadan
    for sx in (-1, 1):
        fill(c, lambda cc, sx=sx: ellipse(cc, sx * 0.47 + fx * 0.3, 0.12, 0.11, 0.16), m["yanak"], shade=0.4, hi=0.2)
    shape = [(0, -0.52), (0.4, -0.45), (0.52, -0.12), (0.45, 0.2), (0.26, 0.44), (0.05 + fx * 0.6, 0.56), (-0.16 + fx * 0.6, 0.5), (-0.4, 0.24), (-0.52, -0.1), (-0.42, -0.44)]
    fill(c, lambda cc: blob(cc, shape, 10), m["ten"], shade=0.65, hi=0.35)
    # yanak pembeliği (yüzde, yumuşak)
    for sx in (-1, 1):
        rg = cairo.RadialGradient(sx * 0.33 + fx, 0.14, 0.01, sx * 0.33 + fx, 0.14, 0.14)
        rg.add_color_stop_rgba(0, *hexrgb("#ac594f"), 0.45); rg.add_color_stop_rgba(1, *hexrgb("#ac594f"), 0)
        c.save(); blob(c, shape, 10); c.clip(); c.arc(sx * 0.33 + fx, 0.14, 0.15, 0, 2 * math.pi); c.set_source(rg); c.fill(); c.restore()
    # gözler
    r = 0.2 * e["size"]
    for sx in (-1, 1):
        ex, ey = sx * 0.215 + fx * 1.1, -0.1
        fill(c, lambda cc: ellipse(cc, ex, ey, r, r), m["goz"], shade=0.35, hi=0.1, light=(0.3, -0.9))
        # bebek
        pr = 0.028 * e["pupil"]
        px = ex + (e["gx"] + look * 0.3) * r * 0.55; py = ey + e["gy"] * r * 0.55
        c.arc(px, py, pr, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
        # kapak (ten rengi, üstten)
        lid = 1 - e["open"]
        if lid > 0.01:
            c.save(); ellipse(c, ex, ey, r * 1.01, r * 1.01); c.clip()
            yb = ey - r + 2 * r * lid
            c.move_to(ex - r * 1.2, ey - r * 1.2); c.line_to(ex + r * 1.2, ey - r * 1.2); c.line_to(ex + r * 1.2, yb - sx * 0.0)
            c.curve_to(ex + r * 0.4, yb + r * 0.12, ex - r * 0.4, yb + r * 0.12, ex - r * 1.2, yb); c.close_path()
            c.set_source_rgb(*hexrgb("#3b2b37")); c.fill_preserve(); c.restore()
            c.new_path()
            # kapak kenarı
            c.save(); ellipse(c, ex, ey, r * 1.01, r * 1.01); c.clip()
            c.set_line_width(0.035); c.move_to(ex - r * 1.2, yb); c.curve_to(ex - r * 0.4, yb + r * 0.12, ex + r * 0.4, yb + r * 0.12, ex + r * 1.2, yb)
            c.set_source_rgb(*INK); c.stroke(); c.restore()
        # kalın koyu göz kenarı
        c.set_line_width(0.034); ellipse(c, ex, ey, r, r); c.set_source_rgba(*INK, 0.95); c.stroke()
        # kaş
        b = e["brow"]
        by = ey - r - 0.05 - abs(b) * 0.02
        inner = by - b * 0.06 * (1 if b > 0 else 1)
        outer = by + b * 0.03
        c.set_line_width(0.045); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(ex + sx * r * 0.95, outer); c.curve_to(ex + sx * r * 0.3, by - 0.04, ex - sx * r * 0.2, inner, ex - sx * r * 0.75, inner + (0.04 if b < 0 else 0))
        c.set_source_rgba(*INK, 0.85); c.stroke()
        if e["tears"] > 0.05:
            c.set_source_rgba(*hexrgb("#f4f1e6"), 0.8 * e["tears"])
            ellipse(c, ex - sx * r * 0.3, ey + r * 0.95 + 0.03 * math.sin(t * 9 + sx), 0.03, 0.045); c.fill()
            c.set_line_width(0.02); c.arc(ex, ey, r * 0.85, math.pi * 0.25, math.pi * 0.75); c.set_source_rgba(*hexrgb("#ffffff"), 0.5 * e["tears"]); c.stroke()
    # burun
    nx, ny = fx * 1.35, 0.16
    if nose:
        tx, ty = nose
        fill(c, lambda cc: tube(cc, [(nx, ny), (nx + tx * 0.5, ny + ty * 0.5 - 0.02), (nx + tx, ny + ty)], 0.13, 0.17), m["ten"], shade=0.5, hi=0.3)
        rg = cairo.RadialGradient(nx + tx, ny + ty, 0.01, nx + tx, ny + ty, 0.14)
        rg.add_color_stop_rgba(0, *hexrgb("#b8574a"), 0.9); rg.add_color_stop_rgba(1, *hexrgb("#b8574a"), 0)
        c.arc(nx + tx, ny + ty, 0.14, 0, 2 * math.pi); c.set_source(rg); c.fill()
    else:
        fill(c, lambda cc: ellipse(cc, nx, ny, 0.07, 0.05), m["ten"], shade=0.5, hi=0.5, light=(0.5, -0.9))
        for sx in (-1, 1):
            ellipse(c, nx + sx * 0.03, ny + 0.025, 0.014, 0.01); c.set_source_rgba(*INK, 0.9); c.fill()
        if sore:
            rg = cairo.RadialGradient(nx, ny, 0.01, nx, ny, 0.11)
            rg.add_color_stop_rgba(0, *hexrgb("#c0584a"), 0.95); rg.add_color_stop_rgba(1, *hexrgb("#c0584a"), 0)
            c.arc(nx, ny, 0.11, 0, 2 * math.pi); c.set_source(rg); c.fill()
    # ağız
    mx, my = fx * 1.3, 0.34
    mo = e["mouth"]
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if mo in ("cizgi", "kas"):
        c.set_line_width(0.03); c.move_to(mx - 0.1, my)
        if mo == "cizgi":
            c.curve_to(mx - 0.03, my + 0.008, mx + 0.03, my + 0.008, mx + 0.1, my - 0.005)
        else:
            c.curve_to(mx - 0.05, my - 0.035, mx + 0.05, my - 0.035, mx + 0.1, my + 0.01)
        c.set_source_rgba(*INK, 0.95); c.stroke()
    elif mo in ("sirit", "sinsi", "dis"):
        if mo == "sirit":
            pts = [(mx - 0.3, my - 0.07), (mx, my - 0.03), (mx + 0.3, my - 0.08), (mx + 0.2, my + 0.08), (mx, my + 0.12), (mx - 0.2, my + 0.08)]
        elif mo == "sinsi":
            pts = [(mx - 0.22, my - 0.01), (mx + 0.05, my - 0.03), (mx + 0.3, my - 0.11), (mx + 0.22, my + 0.06), (mx + 0.02, my + 0.07), (mx - 0.16, my + 0.04)]
        else:
            pts = [(mx - 0.24, my - 0.05), (mx, my - 0.06), (mx + 0.24, my - 0.05), (mx + 0.25, my + 0.05), (mx, my + 0.06), (mx - 0.25, my + 0.05)]
        solid(c, lambda cc: blob(cc, pts, 6), hexrgb("#23030c"))
        c.save(); blob(c, pts, 6); c.clip()
        fill(c, lambda cc: blob(cc, [(p[0], p[1] - (0.0 if mo != "dis" else 0)) for p in pts], 6), m["goz"], shade=0.35, hi=0.1, light=(0, -1))
        c.set_line_width(0.012); c.set_source_rgba(*hexrgb("#8a7e70"), 0.8)
        for k in range(-4, 5):
            c.move_to(mx + k * 0.06, my - 0.12); c.line_to(mx + k * 0.06, my + 0.14); c.stroke()
        if mo == "dis":
            c.move_to(mx - 0.3, my); c.line_to(mx + 0.3, my); c.stroke()
        c.restore()
        c.set_line_width(0.03); blob(c, pts, 6); c.set_source_rgba(*INK, 0.95); c.stroke()
    elif mo == "o":
        o = e["mo"]
        fill(c, lambda cc: ellipse(cc, mx, my + 0.02 * o, 0.06 + 0.1 * o, 0.05 + 0.13 * o), m["agiz"], shade=0.5, hi=0.1)
        fill(c, lambda cc: ellipse(cc, mx, my + 0.08 * o, 0.04 + 0.06 * o, 0.02 + 0.04 * o), m["yanak"], shade=0.3, alpha=0.8)
    # şapka
    if hat and hat.get("on", True):
        hx, hy, ht = hat.get("dx", 0.0), -0.36 + hat.get("dy", 0.0), hat.get("tilt", 0.0)
        draw_hat(c, hx, hy, ht)
    if dirty > 0:
        rnd = random.Random(seed)
        for _ in range(int(60 * dirty)):
            x, y = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.75, 0.5)
            if (x * x) / 0.25 + ((y + 0.0) ** 2) / 0.36 < 1.05:
                ellipse(c, x, y, rnd.uniform(0.008, 0.022), rnd.uniform(0.006, 0.016), rnd.uniform(0, 3))
                c.set_source_rgba(*hexrgb("#d9bf7a"), rnd.uniform(0.6, 0.95)); c.fill()
    c.restore()


def draw_hat(c, hx, hy, tilt):
    m = mats()
    c.save(); c.translate(hx, hy); c.rotate(tilt)
    fill(c, lambda cc: ellipse(cc, 0, 0, 0.92, 0.17), m["sapka"], shade=0.6, hi=0.4, light=(0.4, -0.9))
    crown = [(-0.4, 0.02), (-0.38, -0.25), (-0.2, -0.42), (0.05, -0.45), (0.3, -0.38), (0.4, -0.2), (0.41, 0.02), (0, 0.06)]
    fill(c, lambda cc: blob(cc, crown, 8), m["sapka"], shade=0.55, hi=0.4)
    band = [(-0.4, -0.02), (-0.39, -0.13), (0, -0.1), (0.4, -0.14), (0.41, -0.02), (0, 0.03)]
    fill(c, lambda cc: blob(cc, band, 5), m["bant"], shade=0.5, hi=0.3)
    # iğne
    c.set_line_width(0.018); c.set_source_rgb(*hexrgb("#9aa3a0"))
    c.arc(0.22, -0.07, 0.035, 0.3, math.pi * 1.6); c.stroke(); c.move_to(0.22, -0.07); c.line_to(0.22, -0.17); c.stroke()
    # ön kenar gölgesi
    c.save(); ellipse(c, 0, 0, 0.92, 0.17); c.clip()
    c.rectangle(-1, 0.02, 2, 0.3); c.set_source_rgba(*hexrgb("#7a6128"), 0.45); c.fill(); c.restore()
    c.restore()


def joints(p, x, y, s, flip=1):
    """Yerel noktayı ekrana çevir."""
    cr, sr = math.cos(p["rot"]), math.sin(p["rot"])

    def f(pt):
        lx, ly = pt[0] * flip, pt[1]
        return (x + (lx * cr - ly * sr) * s, y + (lx * sr + ly * cr) * s)
    return f


def draw(c, p, x, y, s, flip=1, between=None, t=0.0):
    """Karakteri çizer. between(c): kollardan sonra, ellerden önce ekran koordinatında çağrılır (olta için)."""
    m = mats()
    c.save(); c.translate(x, y); c.scale(s * flip, s); c.rotate(p["rot"] * flip)
    hip, chest, hd = p["hip"], p["chest"], p["head"]
    if p.get("body", True):
        if p.get("legs", True):
            _leg(c, p["legL"], p["bootL"]); _leg(c, p["legR"], p["bootR"])
        # gövde: tulum alt + yelek + gömlek
        tor = [(hip[0] - 0.3, hip[1] + 0.05), (chest[0] - 0.36, chest[1] + 0.08), (chest[0] - 0.2, chest[1] - 0.05), (chest[0] + 0.2, chest[1] - 0.05),
               (chest[0] + 0.36, chest[1] + 0.08), (hip[0] + 0.3, hip[1] + 0.05), (hip[0], hip[1] + 0.12)]
        fill(c, lambda cc: blob(cc, tor, 6), m["gomlek"], shade=0.55, hi=0.3)
        for sx in (-1, 1):
            v = [(chest[0] + sx * 0.07, chest[1] + 0.0), (chest[0] + sx * 0.36, chest[1] + 0.08), (hip[0] + sx * 0.31, hip[1] - 0.25), (hip[0] + sx * 0.07, hip[1] - 0.3)]
            fill(c, lambda cc, v=v: poly(cc, v), m["yelek"], shade=0.6, hi=0.35)
            # cepler
            for k in range(2):
                yy = chest[1] + 0.3 + k * 0.25
                xx = chest[0] + sx * 0.22
                fill(c, lambda cc, xx=xx, yy=yy: poly(cc, [(xx - 0.08, yy), (xx + 0.08, yy), (xx + 0.08, yy + 0.15), (xx - 0.08, yy + 0.15)]), m["yelek"], shade=0.8, hi=0.1)
        bib = [(hip[0] - 0.31, hip[1] + 0.1), (hip[0] - 0.29, hip[1] - 0.42), (hip[0] + 0.29, hip[1] - 0.42), (hip[0] + 0.31, hip[1] + 0.1)]
        fill(c, lambda cc: poly(cc, bib), m["tulum"], shade=0.6, hi=0.3)
        for sx in (-1, 1):
            fill(c, lambda cc, sx=sx: tube(cc, [(hip[0] + sx * 0.22, hip[1] - 0.4), (chest[0] + sx * 0.25, chest[1] + 0.05)], 0.06), m["tulum"], shade=0.5)
        # boyun + atkı
        neck_top = (hd[0] - math.sin(p["head_rot"]) * 0.4, hd[1] + 0.4)
        fill(c, lambda cc: tube(cc, [(chest[0], chest[1] + 0.05), neck_top], 0.17, 0.15), m["ten"], shade=0.6, hi=0.3)
        fill(c, lambda cc: blob(cc, [(chest[0] - 0.22, chest[1]), (chest[0], chest[1] - 0.1), (chest[0] + 0.22, chest[1]), (chest[0] + 0.12, chest[1] + 0.13), (chest[0] - 0.12, chest[1] + 0.13)], 6), m["atki"], shade=0.5, hi=0.3)
        # kollar
        for arm in (p["armL"], p["armR"]):
            sh, el, wr = arm
            fill(c, lambda cc, a=sh, b=el: tube(cc, [a, b], 0.2, 0.17), m["gomlek"], shade=0.5, hi=0.3)
            fill(c, lambda cc, a=el, b=wr: tube(cc, [a, b], 0.11, 0.095), m["ten"], shade=0.5, hi=0.3)
            fill(c, lambda cc, a=el: ellipse(cc, a[0], a[1], 0.11, 0.08), m["gomlek"], shade=0.5, hi=0.3)
    head(c, hd[0], hd[1], p["e"], p["look"], p["head_rot"], p["hat"], p.get("nose"), p.get("sore", False), p.get("dirty", 0), p.get("seed", 1), t)
    c.restore()
    if between:
        between(c)
    if p.get("body", True):
        c.save(); c.translate(x, y); c.scale(s * flip, s); c.rotate(p["rot"] * flip)
        for arm, hd_ in ((p["armL"], p["handL"]), (p["armR"], p["handR"])):
            _hand(c, arm[2][0], arm[2][1], hd_[0], hd_[1])
        c.restore()

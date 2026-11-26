#!/usr/bin/env python3
"""Ölçüm JSON'undan palet ve ritim panoları çizer (referans/ klasörü için).

    python tools/pano.py analiz/veri/referans_olcum.json referans/
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

d = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
try:
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    Fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
except Exception:
    F = Fs = ImageFont.load_default()

def lum(h):
    r, g, b = [int(h[i:i+2], 16) for i in (1, 3, 5)]; return 0.299*r + 0.587*g + 0.114*b

# 1) genel palet (pay oranlı şerit)
pal = d["palet"]; W = 1800
im = Image.new("RGB", (W, 280), "#f4efe6"); dr = ImageDraw.Draw(im)
dr.text((20, 14), "Genel palet (k-means, Lab) — şerit genişliği = ekrandaki pay", fill="#2a2228", font=F)
x = 20
for p in pal:
    w = int((W - 40) * p["pay"])
    dr.rectangle([x, 60, x + w, 250], fill=p["hex"])
    c = "#ffffff" if lum(p["hex"]) < 120 else "#1d1519"
    if w > 70:
        dr.text((x + 6, 200), p["hex"], fill=c, font=Fs); dr.text((x + 6, 222), f"%{p['pay']*100:.0f}", fill=c, font=Fs)
    x += w
im.save(os.path.join(out, "palet_genel.png"))

# 2) öğe renkleri (elle örneklenmiş)
groups = [
 ("Gök ve uzak", [("gök üst", "#72afb7"), ("gök orta", "#8abec0"), ("uzak ova", "#8ebcb1"), ("uzak kaya", "#bb8180"), ("güneş halesi", "#eeebd2"), ("güneş diski", "#fdfef4")]),
 ("Zemin ve bitki", [("kum ışık", "#d1b974"), ("kum gölge", "#786e50"), ("çalı ışık", "#a68b42"), ("çalı", "#9e803b"), ("çiçek lila", "#d3afc9"), ("mavi bitki", "#4676a1")]),
 ("Karakter", [("ten ışık", "#443442"), ("ten", "#362a38"), ("ten gölge", "#1a111c"), ("göz akı", "#faf4eb"), ("yanak", "#ac594f"), ("ağız içi", "#23030c")]),
 ("Kostüm", [("teal kol", "#185a62"), ("kask pembe", "#d6837d"), ("krem", "#e4e0b2"), ("sarı yelek", "#e4bd59"), ("deri", "#572d2e"), ("pas çanta", "#9c4c37"), ("pantolon", "#2a2c2c"), ("mor dizlik", "#7b697c")]),
 ("Aksesuar", [("meyve", "#d57906"), ("meyve gölge", "#7b2b19"), ("ip/kök", "#836b40")]),
]
im = Image.new("RGB", (W, 120 + 150 * len(groups)), "#f4efe6"); dr = ImageDraw.Draw(im)
dr.text((20, 14), "Öğe renkleri (1920x1080 karelerden medyan örnek)", fill="#2a2228", font=F)
y = 60
for name, cols in groups:
    dr.text((20, y + 45), name, fill="#2a2228", font=F)
    x = 230
    for lab, h in cols:
        dr.rectangle([x, y, x + 180, y + 100], fill=h)
        c = "#ffffff" if lum(h) < 120 else "#1d1519"
        dr.text((x + 8, y + 52), lab, fill=c, font=Fs); dr.text((x + 8, y + 74), h, fill=c, font=Fs)
        x += 195
    y += 150
im.save(os.path.join(out, "palet_ogeler.png"))

# 3) ritim: plan şeridi + kamera + ses
pl = d["planlar"]; T = d["format"]["sure"]; W2 = 1800; X0 = 40; sc = (W2 - 80) / T
im = Image.new("RGB", (W2, 470), "#f4efe6"); dr = ImageDraw.Draw(im)
dr.text((X0, 12), f"Ritim: {len(pl)} plan / {T:.1f} sn · ort {d['plan']['sure_ort']} sn · medyan {d['plan']['sure_medyan']} sn", fill="#2a2228", font=F)
cols = ["#72afb7", "#d1b974"]
for i, s in enumerate(pl):
    x0 = X0 + s["bas"] * sc; x1 = X0 + s["son"] * sc
    dr.rectangle([x0, 60, x1 - 2, 140], fill=cols[i % 2])
    dr.text((x0 + 4, 66), str(i + 1), fill="#2a2228", font=F); dr.text((x0 + 4, 112), f"{s['sure']:.2f}", fill="#2a2228", font=Fs)
    if d["plan"]["smear_kare"][i - 1] if i > 0 else 0:
        dr.polygon([(x0 - 6, 150), (x0 + 6, 150), (x0, 140)], fill="#b65b2f")
    z = s["toplam_zoom_yuzde"]
    dr.text((x0 + 4, 160), f"{z:+.0f}%", fill="#2a2228", font=Fs)
dr.text((X0, 185), "▲ smear girişli kesme · % = plan boyunca toplam itme(+)/çekme(-)", fill="#6b5a4a", font=Fs)
fr = d["kare_basina"]
def track(key, y0, h, label, mx):
    dr.text((X0, y0 - 24), label, fill="#2a2228", font=Fs)
    pts = [(X0 + p["t"] * sc, y0 + h - min(p[key] if not isinstance(p[key], dict) else 0, mx) / mx * h) for p in fr]
    dr.line(pts, fill="#2a2228", width=2)
fr2 = [{"t": p["t"], "sp": (p["mot"]["dx"]**2 + p["mot"]["dy"]**2) ** .5 if p.get("mot") else 0} for p in fr]
dr.text((X0, 222), "Global görüntü hareketi (px/kare, 0-6 kırpılmış; kamera + büyük karakter hareketi)", fill="#2a2228", font=Fs)
dr.line([(X0 + p["t"] * sc, 250 + 80 - min(p["sp"], 6) / 6 * 80) for p in fr2], fill="#185a62", width=2)
rms = d.get("ses", {}).get("rms_100ms", [])
if rms:
    m = max(rms)
    dr.text((X0, 352), "Ses yüksekliği (RMS, 100 ms)", fill="#2a2228", font=Fs)
    dr.line([(X0 + i * 0.1 * sc, 450 - r / m * 70) for i, r in enumerate(rms)], fill="#b65b2f", width=2)
for s in pl:
    x = X0 + s["bas"] * sc
    dr.line([(x, 220), (x, 455)], fill="#c9bfae", width=1)
im.save(os.path.join(out, "ritim.png"))
print("yazıldı:", out)

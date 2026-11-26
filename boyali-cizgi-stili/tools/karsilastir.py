#!/usr/bin/env python3
"""Ölçülmüş bir videoyu (olc.py çıktısı) stil hedefleriyle karşılaştırır.

    python tools/karsilastir.py olcum.json [analiz/veri/hedefler.json]

Her hedef için TAMAM / SINIRDA / DIŞINDA yazar. Çıkış kodu: dışında kalan hedef sayısı.
"""
import json, sys, os

here = os.path.dirname(os.path.abspath(__file__))
olc = json.load(open(sys.argv[1]))
hed = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "analiz", "veri", "hedefler.json")))


def get(d, yol):
    for k in yol.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


bad = 0
rows = []
for h in hed["hedefler"]:
    v = get(olc, h["yol"])
    if v is None:
        rows.append(("YOK", h["yol"], "-", h)); continue
    lo, hi = h["min"], h["max"]
    span = (hi - lo) or 1
    if lo <= v <= hi:
        st = "TAMAM"
    elif lo - 0.15 * span <= v <= hi + 0.15 * span:
        st = "SINIRDA"
    else:
        st = "DISINDA"; bad += 1
    rows.append((st, h["yol"], v, h))

w = max(len(r[1]) for r in rows)
for st, yol, v, h in rows:
    vs = f"{v:.3f}" if isinstance(v, float) else str(v)
    print(f"{st:8s} {yol:{w}s} {vs:>9s}   hedef {h['min']}..{h['max']} (ref {h['ref']})  {h['not'] if st != 'TAMAM' else ''}")
print(f"\n{sum(r[0]=='TAMAM' for r in rows)} tamam, {sum(r[0]=='SINIRDA' for r in rows)} sınırda, {bad} dışında")
sys.exit(bad)

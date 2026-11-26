#!/usr/bin/env python3
"""Bir projenin planlar.json dosyasından, kopyalanıp yapıştırılmaya hazır prompt sayfası üretir.

    python tools/promptla.py projeler/<ad>/planlar.json projeler/<ad>/PROMPTLAR.md

[STİL] ve [NEGATİF] blokları sablonlar/promptlar.md dosyasından okunur. Böylece stil tek yerde durur.
planlar.json: {baslik, sahne, karakterler{anahtar: tanım}, referans_dosyalari{anahtar: yol}, planlar[{no, ad, tur, sure, uret, ref[], kare, hareket}]}
`kare` ve `hareket` metinlerindeki {anahtar} yer tutucuları karakter tanımlarıyla değiştirilir.
"""
import json, os, re, sys

here = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(here, "..", "sablonlar", "promptlar.md"), encoding="utf-8").read()


def block(title):
    m = re.search(r"## \[" + re.escape(title) + r"\].*?```\n(.*?)```", tpl, re.S)
    if not m:
        raise SystemExit(f"sablonlar/promptlar.md içinde [{title}] bloğu bulunamadı")
    return m.group(1).strip()


STIL, NEG = block("STİL"), block("NEGATİF")
p = json.load(open(sys.argv[1], encoding="utf-8"))
chars = p.get("karakterler", {})


def fill(s):
    return re.sub(r"\{(\w+)\}", lambda m: chars.get(m.group(1), m.group(0)), s)


out = [f"# {p['baslik']}: hazır promptlar", "",
       "Bu sayfa `tools/promptla.py` ile `planlar.json` dosyasından üretildi; promptları değiştirmek için o dosyayı düzenleyip yeniden çalıştırın.", "",
       "Her plan için:",
       "1. **Anahtar kare** promptunu görsel üreticiye verin. `Referans` satırındaki görselleri ekleyin. Negatif alan varsa `Negatif` metnini girin.",
       "2. Seçtiğiniz kareyi `kareler/NN.png` olarak kaydedin.",
       "3. Kareyi ve **hareket** promptunu görselden videoya üreticisine verin. Belirtilen sürede üretip `klipler/<ad>.mp4` olarak kaydedin.", "",
       f"**Negatif (bütün anahtar kareler):**\n```\n{NEG}\n```", ""]
for pl in p["planlar"]:
    rf = p.get("referans_dosyalari", {})
    refs = ", ".join(f"`{rf.get(r, r)}`" for r in pl.get("ref", [])) or "yok"
    out += [f"## Plan {pl['no']}: `{pl['ad']}` (tür {pl['tur']}, kurguda {pl['sure']} sn, {pl.get('uret', 4)} sn üretin)", "",
            f"**Referans:** {refs}", "",
            "**Anahtar kare:**", "```", fill(pl["kare"]) + "\n" + p["sahne"] + "\n" + STIL, "```", "",
            "**Hareket:**", "```", fill(pl["hareket"]), "```", ""]
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
print("yazıldı:", sys.argv[2], f"({len(p['planlar'])} plan)")

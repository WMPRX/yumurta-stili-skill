# Kum Balıkçısı: kodla taslak (animatik)

Yapay zekâ üreticisi kullanmadan, Python ile çizilmiş 2B boyalı bir taslak. Amaç, son üretimden önce zamanlamayı, kurguyu, kamera kurallarını, paleti ve sesi görmek. Karakterler referanstaki 3B görünüme yaklaşmaz; görsel üretim için `../PROMPTLAR.md` kullanılır.

| Dosya | Ne |
|---|---|
| `boya.py` | Çizim motoru (pycairo): elle boyanmış dokulu malzemeler, kontursuz dolgu, yönlü gölgelendirme, düşen gölgeler (gölge yüzeyin tonunu korur), alan derinliği, hareket bulanığı, ışık halesi; gök, kum, kum gölü, tepe/balina, kuyruk, kova, tabure, olta, şamandıra, balık |
| `tikir.py` | Tıkır: iskelet pozları, 12 ifade, göz kırpma, şapka, yelek, tulum, eldivenler, uzayan burun |
| `sahneler.py` | 12 planın animasyonu (SENARYO.md'deki sürelerle) |
| `render.py` | `python render.py kare --olcek 0.5 --plan 3 --t 1.0` tek kare önizleme; `python render.py hepsi` 12 klip → `../klipler/` |
| `ses.py` | SES.md'deki planın sentezi (rüzgâr, foley, vuruşlar, formant nidaları, marimba) → `../ses/miks.wav`, −21 LUFS |
| `kurgu_taslak.json` | Klipleri birleştirme ayarları: itme/çekme, darbe sarsıntıları, smear geçişleri |

## Baştan üretmek
```bash
pip install pycairo numpy opencv-python-headless scipy pillow
cd projeler/kum-balikcisi/taslak
python render.py hepsi                     # ~10 dk, 4 çekirdek
python ses.py
python ../../../tools/kurgu.py kurgu_taslak.json ../kurgu_taslak.mp4
python ../../../tools/renk_esle.py ../kurgu_taslak.mp4 ../kum-balikcisi_taslak.mp4
python ../../../tools/olc.py ../kum-balikcisi_taslak.mp4 ../olcum_taslak.json --plan "2.6,3.52,7.04,9.04,10.64,12.44,14.96,18.96,20.96,23.76,25.76"
python ../../../tools/karsilastir.py ../olcum_taslak.json
```

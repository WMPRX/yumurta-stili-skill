---
name: boyali-cizgi-stili
description: Make a 25-40 s wordless cartoon short in the measured "painterly desert" style (stylized 3D with hand-painted matte textures and no outlines, dusty teal sky against ochre sand, a very dark plum-skinned character with huge white eyes, one warm sun with soft cast shadows, ~2.5 s shots, mostly locked-off camera with slow push/pull, smear cuts, slapstick told only through poses, faces and sound effects). The pipeline is AI image and video generation, then edit, colour match and QC with the bundled tools. Use when the user asks for a video "boyalı çizgi stiliyle", "bu videonun tasarımıyla", "çöl/teal-turuncu çizgi film stiliyle", or wants to check a video against this style.
---

# Boyalı çizgi stili: sessiz komedi kısa filmi

Kullanıcıya Türkçe yanıt verin. Bu skill, bir referans videonun **ölçülen** tasarımını kullanıcının kendi hikâyeleri ve karakterleriyle yeniden üretir. Sayılar `STIL_KITABI.md` içinde, ham ölçüm `analiz/veri/` içinde, panolar `referans/` içinde, plan plan döküm `analiz/plan_listesi.md` içinde.

## Kurallar

- **Stil kopyalanır, içerik kopyalanmaz.** Referanstaki karakter, canlı çalı, gözlü meyve ve kırkayak ile plan sırası örnek olarak kalır. Her projede yeni bir karakter, yeni bir dünya nesnesi ve yeni bir şaka zinciri yazın.
- **Diyalog yok.** Hikâye poz, ifade ve sesle anlatılır. Altyazı ya da anlatıcı eklemeyin.
- **Değer yapısı korunur.** Karakter sahnenin en koyu öğesidir (ten L 15-25), göz akı en açığıdır (L ~96). Gök açık teal'dir (L 68-74).
- **Renk ekseni teal ↔ turuncu.** Saf yeşil ve saf mavi yoktur. Bitkiler hardal-zeytin, gök teal. Her planda en fazla bir doygun vurgu bulunur. Gölge yüzeyin tonunu korur, değeri ~0,6'ya iner. Mavi ya da gri gölge olmaz.
- **Kontur yok, gren yok, vinyet yok.** Doku fırça izinden gelir.
- **Işık tek güneştir:** sıcak, arkadan-yandan. Düşen gölgeler gerçek ve kenarları yumuşak. En az bir planda güneş diski kadrajın köşesinde görünür.
- **Ritim:** 30 sn başına 10-14 plan, ortalama ~2,5 sn, en kısa ~0,9 sn, en uzun ~4 sn. Kesmelerin yaklaşık üçte biri smear ile girer. En az bir ≥3 sn'lik sessiz duraklama olur.
- **Kamera:** çoğunlukla sabit. Kibir anında yavaş itme (+5..+8 %), felakette yavaş çekme (−7..−12 %), darbede 0,3 sn'lik sarsıntı. Whip pan, orbit ve dutch açı yok. 25 fps.
- Her teslimden önce `tools/olc.py` + `tools/karsilastir.py` çalıştırılır ve sonuç kullanıcıya bildirilir. DIŞINDA kalan bir ölçü varsa nedeni açıklanır.

## İş akışı

### 1. Hazırlık
```bash
pip install -r requirements.txt          # numpy, opencv-python-headless
# ffmpeg ve ffprobe PATH'te olmalı
```
Önce `STIL_KITABI.md` dosyasını baştan sona okuyun. Karakter tasarlarken §3'ü, kurgu yaparken §4-5'i tekrar açın.

### 2. Fikir ve senaryo
`sablonlar/senaryo_sablonu.md` dosyasını `projeler/<ad>/SENARYO.md` olarak kopyalayıp doldurun. Yapı: arzu → araç → küçük zafer → tırmanma → ters köşe 1 → bedel → sessiz duraklama → ikinci deneme → ters köşe 2 → final tepkisi. Kullanıcı yalnızca bir konu verirse 2-3 kısa gag fikri önerin ve birini seçmesini isteyin. Sonra 12 planlık listeyi doldurun.

### 3. Karakter ve dünya
- `sablonlar/karakter_sayfasi.md` formunu doldurun ve `sablonlar/promptlar.md` → `[KARAKTER]` ile karakter sayfası promptunu yazın.
- `[SAHNE]` bloğunu bir kez yazın ve bütün planlarda aynen kullanın.
- Kullanıcı görseli kendi aracında (Higgsfield, Midjourney, Flux, Nano Banana vb.) üretir ve en iyisini `projeler/<ad>/karakterler/` klasörüne koyar. Claude bu dosyayı görüp sayfanın kontrol listesine göre değerlendirir: kontur, ten değeri, göz büyüklüğü, palet.

### 4. Anahtar kareler ve plan videoları
- Her plan için `[PLAN]` türünü seçin (A-H). Plan metinlerini `projeler/<ad>/planlar.json` dosyasına yazın (örnek: `projeler/kum-balikcisi/planlar.json`), sonra `python tools/promptla.py projeler/<ad>/planlar.json projeler/<ad>/PROMPTLAR.md` çalıştırın. Bu, `[PLAN] + [SAHNE] + [STİL]` birleşimini ve `[NEGATİF]` bloğunu her plan için hazır hale getirir.
- Anahtar kareleri kullanıcı üretir ve `projeler/<ad>/kareler/NN.png` olarak koyar. Claude her kareyi `promptlar.md` sonundaki kontrol listesiyle inceler, sorunlu olanlar için düzeltilmiş prompt verir.
- Her plan için `[HAREKET]` promptu yazın. Kamera cümlesi başta, pozlar sırayla, ifadeler oklarla. 3-5 sn üretilir ve `projeler/<ad>/klipler/NN_ad.mp4` olarak kaydedilir.
- Tek bir anahtar karenin ölçüsünü hızlıca görmek için kareyi 1 sn'lik videoya çevirip ölçebilirsiniz:
  `ffmpeg -loop 1 -i kare.png -t 1 -r 25 -pix_fmt yuv420p kare.mp4 && python tools/olc.py kare.mp4 k.json`

### 5. Kurgu
- `sablonlar/kurgu_ornek.json` dosyasını `projeler/<ad>/kurgu.json` olarak kopyalayın. Her klip için en iyi aralığı `bas`/`sure` ile seçin; klipleri `tools/kontakt.sh klip.mp4 k.png 5` ile inceleyin.
- `itme`, `sarsinti` ve `gecis: smear` değerlerini senaryodaki kamera sütunundan alın.
- ```bash
  python tools/kurgu.py projeler/<ad>/kurgu.json projeler/<ad>/kurgu.mp4
  ```

### 6. Renk eşleme
```bash
python tools/renk_esle.py projeler/<ad>/kurgu.mp4 projeler/<ad>/renk.mp4 --guc 0.6 --ton 0.6
```
Bu adım ton yüzdeliklerini, kontrastı, kromayı ve bölünmüş tonu (mor gölge, okra orta, teal ışık) referansa çeker ve saf siyahı mor-siyaha kaldırır. Referansın kendisine uygulandığında neredeyse hiç değişiklik yapmaz (27/27 hedef korunur). Araç bilerek temkinli: ton kaydırması en fazla 8/6/6 L birimi, renk kaydırması en fazla 6 Lab birimi; bir bandın ortalaması hedeften çok uzaksa (ör. gökyüzü olmayan bir planda açık tonlar kum olduğu için) o bant hiç kaydırılmaz. Bu yüzden kompozisyonu farklı planları bozmaz, ama rengi çok kaymış bir klibi tek başına kurtaramaz: o durumda promptu düzeltip yeniden üretin.

### 7. Ses
`sablonlar/ses_plani.md`: ortam + foley + vuruşlar + nidalar, kelime yok. Vuruşlar kesmelere oturur, sessiz duraklama gerçekten sessizdir. Hedef −21 LUFS, LRA ≥ 8, TP ≤ −1. Ses dosyası `kurgu.json` → `"ses"` ile eklenir; kurguyu tekrar çalıştırıp 6. adımı yineleyin.

### 8. Ölçüm ve kalite kontrolü
```bash
tools/kontakt.sh projeler/<ad>/renk.mp4 projeler/<ad>/kontakt.png 2
python tools/olc.py projeler/<ad>/renk.mp4 projeler/<ad>/olcum.json --plan "<kurgu.py'nin yazdığı kesme saatleri>"
python tools/karsilastir.py projeler/<ad>/olcum.json
python tools/pano.py projeler/<ad>/olcum.json projeler/<ad>/pano/
```
- `--plan` verin. Otomatik kesme algılayıcısı (eşik `--kesme 0.18`) referansta 11 kesmenin 10'unu buldu ama ifade değişimlerinde ve sarsıntılı planlarda yanılabilir.
- Kontakt sayfasına bakıp şunları kontrol edin: karakter tutarlılığı (kostüm rengi, göz), ışık yönü sürekliliği, ölçek değişimi, ağız/el bozulmaları.
- Kullanıcıya `karsilastir.py` tablosunu özetleyin. DIŞINDA kalan her ölçü için hangi adımda düzeltileceğini söyleyin: renk ve ton → 6. adım ya da prompt; ritim → kurgu.json; kamera → `itme` değerleri ya da hareket promptu; ses → miks.

### 9. Teslim
```bash
ffmpeg -i projeler/<ad>/renk.mp4 -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart projeler/<ad>/<ad>.mp4
```

## Araçlar

| Araç | Ne yapar |
|---|---|
| `tools/olc.py` | Videoyu ölçer: kesmeler, plan süreleri, smear, kamera (öteleme/zoom/dönme/sarsıntı), özne hareketi, ton, renk aileleri, palet, gren, kontur, alan derinliği, vinyet, ses (LUFS/LRA/TP/sessizlik) |
| `tools/karsilastir.py` | Ölçümü `analiz/veri/hedefler.json` ile karşılaştırır: TAMAM / SINIRDA / DIŞINDA |
| `tools/renk_esle.py` | Klibi referansın ton ve renk dağılımına çeker |
| `tools/kurgu.py` | Klipleri birleştirir; itme/çekme, kayma, darbe sarsıntısı, smear geçişi, ses |
| `tools/kontakt.sh` | Zaman damgalı kontakt sayfası |
| `tools/pano.py` | Palet ve ritim panoları |
| `projeler/kum-balikcisi/taslak/` | Örnek: aynı senaryonun kodla çizilmiş 2B taslağı (pycairo). Yapay zekâ üreticisi yokken zamanlamayı, kurguyu ve sesi görmek için bir şablon |
| `tools/promptla.py` | Projenin `planlar.json` dosyasından kopyalanmaya hazır `PROMPTLAR.md` üretir (stil ve negatif blokları `sablonlar/promptlar.md`'den alır) |

## Sık sorunlar
- **Video modeli kamerayı gezdiriyor:** hareket promptunun ilk cümlesi kamera cümlesi olmalı. Hâlâ geziyorsa klibin en sakin 1-2 sn'sini seçin ve kurguda `itme` ile kontrollü hareket ekleyin.
- **Gök maviye kayıyor ya da bitkiler yeşilleniyor:** `[STİL]` bloğundaki hex'leri koruyun, `[NEGATİF]`e `blue sky, green grass` ekleyin. Kalan kaymayı `renk_esle.py` düzeltir.
- **Kontur çıkıyor:** `NO outlines` ifadesini promptun başına da koyun. Anahtar kare kontursuz değilse videoyu üretmeyin.
- **Karakter planlar arasında değişiyor:** her planda aynı karakter sayfasını referans verin. Kostüm renklerini hex ile yazın.
- **Plan süreleri kısa çıkıyor (ort < 1,9 sn):** sessiz duraklama ve final planlarını 3,5-4 sn'ye uzatın.

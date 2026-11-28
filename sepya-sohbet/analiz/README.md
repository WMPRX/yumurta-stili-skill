# Analiz raporları

Stilin sayılara dökülmüş hâli. Her rapor bir konuyu altı referans videoda ölçüyor, hedef aralığı ve kuralları yazıyor; sonunda örnek videoyla karşılaştırıyor.

| Rapor | Konu |
|---|---|
| [metin.md](metin.md) | Diyaloğun kalıbı, konuşma hızı, satır sayısı, kırılmanın yeri |
| [kurgu.md](kurgu.md) | Plan süreleri, kesmeler, kameranın itmesi ve eğrisi, plan türleri, mekân, kapanışın zamanlaması |
| [renk.md](renk.md) | Parlaklık, Lab renk, palet, vinyet, tarama çizgileri, gren; renk düzeltmesinin formülü |
| [karakter.md](karakter.md) | Çizim dili, kontur kalınlığı, kadrajdaki yer, iki rolün farkı, hareket; bizim karakterlerimiz |
| [altyazi.md](altyazi.md) | Altyazı, filigran ve kapanış yazısının yeri, boyu, rengi |
| [ses.md](ses.md) | Ses yüksekliği, müzik yatağı, iki sesin perdesi, miks |

Ham sayılar: [veri/](veri/). Özet: [../STIL_KITABI.md](../STIL_KITABI.md).

## Neyi, nasıl ölçtük

- **Referans:** kullanıcının verdiği altı video, 720 × 1280, 30 fps, 77,6 – 94,8 sn (toplam 521,6 sn, 15.649 kare). Repoda yoklar; raporlarda `r1` – `r6`.
- **Araç:** görüntü ölçülerinin hepsi [`../tools/olc.py`](../tools/olc.py) ile; aynı araç kendi videonuzu ölçüp aynı tabloyu verir. Ek olarak:
  Whisper (kelime saatleri), pYIN (perde), k-means (palet), ECC (her planın 5 noktasında yakınlaşma eğrisi), elle plan türü etiketi (115 plan),
  kare şeritleriyle her kesmenin gözle doğrulanması.
- **Maskeler:** altyazı bandı (%64 – 86) ve kapanış kartı renk ölçülerine girmiyor; kamera ölçüsünden önce kareler bulanıklaştırılıyor (tarama çizgileri hareket sayılmasın diye).
- **Ne ölçülmedi:** karakter animasyonunun ayrıntısı (ağız şekilleri, el hareketleri) yalnızca kare kare izlenerek not edildi.

## Örnek video nerede duruyor

Soğuk Çay, render çıktısı (`stories/soguk-cay/out/soguk-cay.mp4`, crf 16) `python tools/olc.py` ile. `ornek/soguk-cay.mp4` aynı videonun repo için küçültülmüş hâli (crf 26).

| Ölçü | Referans aralığı (ortanca) | Soğuk Çay | |
|---|---|---|---|
| Süre (sn) | 77,6 – 94,8 (87) | 84,73 | ✓ |
| Plan süresi ortanca (sn) | 3,4 – 5,23 (3,85) | 3,567 | ✓ |
| Kesme / dakika | 12,9 – 15,9 (13,3) | 15,65 | ✓ |
| Plan başına itme (%) | 3,22 – 4,68 (3,81) | 3,463 | ✓ |
| İçeri iten planlar (%) | 79,2 – 95 (87,8) | 85,71 | ✓ |
| Orta parlaklık | 0,118 – 0,192 (0,155) | 0,1412 | ✓ |
| Karanlık uç (p5) | 0,0274 – 0,0588 (0,049) | 0,05098 | ✓ |
| Kontrast | 0,443 – 0,624 (0,559) | 0,6078 | ✓ |
| Lab a* | 5,88 – 7,51 (6,67) | 6,771 | ✓ |
| Lab b* | 8,22 – 13 (9,81) | 10,38 | ✓ |
| C* ortanca | 10 – 16,1 (12,9) | 12,53 | ✓ |
| C* p90 | 15,7 – 19,3 (17,5) | 18,36 | ✓ |
| Köşe / merkez | 0,168 – 0,315 (0,223) | 0,2139 | ✓ |
| Tarama periyodu (yüksekliğin payı) | 0,01445 – 0,01446 (0,01445) | 0,01445 | ✓ |
| Tarama genliği | 0,0357 – 0,044 (0,0386) | 0,03668 | ✓ |
| Tarama kayması (kare başına) | 0,00033 – 0,00044 (0,00037) | 0,0004466 | üstünde |
| Altyazı merkezi | 0,72 – 0,764 (0,764) | 0,7635 | ✓ |
| Altyazı harf yüksekliği | 0,0273 – 0,0281 (0,0281) | 0,0276 | ✓ |
| Ses yüksekliği (LUFS) | -14,2 – -14,1 (-14,1) | -14,1 | ✓ |
| Kararmadan sona (sn) | 7,3 – 8,27 (7,85) | 8,033 | ✓ |

20 ölçünün 19'u referans aralığında. Tarama kayması üst sınırın %1,5 üstünde (render 0,00042 ayarıyla yapıldı); varsayılan bu yüzden 0,00036'ya çekildi.

## Ölçümün göremediği

Sayılar tuttuktan sonra kareler tek tek izlendi. Ölçünün göstermediği, gözle bulunup düzeltilenler:

| Kusur | Sebep | Çözüm |
|---|---|---|
| Omuz üstü karakter kadrajın yarısını kaplıyor | Ön plan karakteri büyük ve merkeze yakın çizilmişti | Ölçek 0,95, yana %80 kaydırılmış; yalnızca bulanık bir kenar görünüyor |
| Telefon ekranı bembeyaz | Beyaz ekran + parıltı, renk düzeltmesinden sonra patlıyor | Ekran gri-bej (`#cfc6b8`) |
| Telefon çok uzun, mesajlar okunmuyor | Ekran oranı 2,05, yazı 26 px | Oran 1,95, yazı 36 px |
| Geniş planda masa / korkuluk kadrajı kaplamıyor | Ön plan kadraj genişliğinde çiziliyordu, geniş planda %66'ya küçülüyor | Ön plan kadrajın 1,6 katı genişlikte |
| Koyu tonlar gri, renk yoğunluğu düşük (C* 7) | Tek gamalı renk düzeltmesi koyuları nötr bırakıyor | Kanal başına gama (bölünmüş tonlama) ve hafif negatif kaldırma |
| Akıl hocası ve öğrencinin perdesi ters | Taslak ses aracı ilk konuşanı akıl hocası sayıyordu | Son satırı söyleyen akıl hocası |

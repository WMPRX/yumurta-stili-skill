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

Soğuk Çay (`ornek/soguk-cay.mp4`), `python tools/olc.py ornek/soguk-cay.mp4` ile:

ÖLÇÜM_TABLOSU

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

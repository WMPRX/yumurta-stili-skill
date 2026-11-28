# Altyazı, filigran ve kapanış kartı

Yöntem: altyazı bandında (%62 – 86) parlak ve renksiz piksellerin (V > 215, S < 45) bağlı bileşenleri, saniyede iki kare; altyazının
değişimi bandın 90 × 38'lik küçük maskesinden kare kare. Filigran ve kapanış yazısı tam çözünürlükte kırpılıp ölçüldü.

## Altyazı

| Ölçü | Değer |
|---|---|
| Kelime sayısı | her seferinde tek kelime (kısa bağlaçlar da tek başına: "VE", "DE", "Mİ") |
| Yazı | büyük harf, Türkçe kurallarıyla (İ, I); noktalama yok, kesme işareti kalıyor ("SEVİYORUM'UN") |
| Yazı tipi | kalın, dar, eğik çizgi roman yazısı. Açık lisanslı en yakın: **Bangers** (OFL, Türkçe harfler var) |
| Renk | beyaz dolgu; koyu kontur (yazı boyunun ~%17'si); aşağı-sağa yumuşak gölge |
| Yer | yatayda ortada; merkez yüksekliğin %76,4'ünde (beş videoda), bir videoda %72 |
| Boyut | harf yüksekliği yüksekliğin %2,73 – 2,81'i (1920'de ~54 px) |
| Süre | kelimeyle başlıyor, sonraki kelimeye ya da kelime bittikten ~0,35 sn sonrasına kadar; ekranda kalma payı %62 – 84 |
| Kapanış kartında | altyazı sürüyor (imza cümlesi de yazılı) |

## Filigran (kanal adı)

| Ölçü | Değer |
|---|---|
| Yer | tepede ortada, merkez %5,3 yükseklik |
| Biçim | serif büyük harf (Trajan / Cinzel türü), harf arası ~0,55 em |
| Boyut | harf yüksekliği yüksekliğin ~%0,94'ü (1920'de ~18 px); genişlik karenin ~%17,5'i |
| Renk | altın-kahve: ortalama ≈ (134, 112, 87), en açık ≈ (183, 161, 131) |
| Süre | baştan kapanış kartına kadar; kanal adı büyük çıkarken kayboluyor |

## Kapanış kartı

| Ölçü | Değer |
|---|---|
| Sahne | son planın (akıl hocası) ışıkları ~4 sn'de iniyor; silüet ve kontur hafifçe seçiliyor |
| Gözler | sıcak sarı-turuncu parlıyor, yarı kapalı kapak şekli korunuyor, çevresinde hale |
| Kanal adı | altın serif büyük harf, parlama ile; merkez %27,9 yükseklikte, genişlik karenin ~%57'si, harf yüksekliği ~%3,5 |
| Renk | ortalama ≈ (136, 113, 86), en açık ≈ (208, 182, 148) |
| Zamanlama | bkz. [kurgu.md](kurgu.md) → Kapanış |

Bizde: `engine/src/overlay.js` (`drawCaption`, `drawWatermark`, `drawTitle`), gözler `main.js` → `endEyes`.
Kanal adı `story.js` → `BRAND.ad`; yazı tipi Cinzel (OFL).

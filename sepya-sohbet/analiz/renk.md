# Renk, ton ve doku

Yöntem: her kare 180 × 320'ye küçültüldü; altyazı bandı (%64 – 86) ve kapanış kartı ölçüme girmedi. Parlaklık 0 – 1, renk CIELab
(a* + kırmızıya, b* + sarıya, C* = renk yoğunluğu). Video değerleri kare değerlerinin ortancası. Tarama çizgileri: karenin üst yarısında
dikey yüksek geçiren profilin FFT'si, art arda iki karede faz farkı. Ham sayılar: [`veri/renk_referans.json`](veri/renk_referans.json),
[`veri/olc_referans.json`](veri/olc_referans.json).

## Ton ve renk

| Video | Orta parlaklık | p5 | Kontrast | a* | b* | C* ortanca | C* p90 | Köşe / merkez |
|---|---|---|---|---|---|---|---|---|
| r1 | 0,173 | 0,027 | 0,55 | 7,0 | 13,0 | 16,1 | 19,2 | 0,19 |
| r2 | 0,118 | 0,039 | 0,58 | 6,4 | 8,4 | 10,3 | 17,9 | 0,17 |
| r3 | 0,192 | 0,039 | 0,62 | 5,9 | 9,4 | 12,8 | 16,2 | 0,17 |
| r4 | 0,161 | 0,059 | 0,45 | 7,5 | 11,4 | 13,9 | 19,3 | 0,31 |
| r5 | 0,149 | 0,059 | 0,44 | 7,3 | 10,2 | 13,0 | 17,0 | 0,25 |
| r6 | 0,137 | 0,059 | 0,57 | 6,2 | 8,2 | 10,0 | 15,7 | 0,30 |
| **Ortanca** | **0,155** | **0,049** | **0,56** | **6,7** | **9,8** | **12,9** | **17,5** | **0,22** |

Okuma:

- **Karanlık.** Orta parlaklık 0,12 – 0,19: gece, lambalar ve pencereler dışında her yer koyu.
- **Tek tonlu sepya.** Renk yoğunluğunun ortancası (12,9) ile %90'lık dilimi (17,5) birbirine çok yakın: bütün pikseller aynı sıcak
  tonu taşıyor, doygun bir renk öne çıkmıyor. Karakterlerin kendi renkleri (turuncu kürk, yeşil yelek, kırmızı kravat) yalnızca bir ipucu olarak kalıyor.
- **Sıcak ve hafif kırmızı.** a* ≈ +6,7, b* ≈ +9,8; doygun piksellerin tonu 18° – 26° (turuncu-kahve).
- **Uçlar.** En koyu %0,5 ≈ (6 – 17, 1 – 5, 0 – 2) RGB: neredeyse siyah ama mavisiz. En açık %0,5 ≈ (180 – 237, 157 – 217, 140 – 204): krem, saf beyaz yok.
- **Palet** (10 küme, pay): #301e14 %21, #22120b %18, #402b1e %15, #100703 %12, #533c2d %9, #6c503c %8, #836853 %6, #9d8472 %4, #b6a091 %4, #dac6b8 %2.
- **Vinyet ağır.** Merkezden köşeye halkalarda parlaklık / merkez: 1,00 · 1,02 · 0,86 · 0,71 · 0,56 · 0,48 · 0,41 · 0,33 · 0,26 · 0,18 (içerikle birlikte).

### Bizde nasıl

Sahne normal renklerle boyanıyor; `engine/src/post.js` tek WebGL geçişinde:

```
c = mix(gri(c), c, sat)                 sat = 0,12      (renklerin %12'si kalıyor)
c = c ^ gamma                            gamma = (1,0  1,17  1,36)   koyu tonlarda mavi önce düşüyor: bölünmüş tonlama
c = lift + c · (gain − lift)             gain = (0,97  0,85  0,79)   lift = (−0,03  −0,032  −0,034)
c = c · (1 − 0,72 · smoothstep(0,28; 1,05; r))      vinyet
c = c · (1 + 0,046 · sin(2π (y − kare · 0,00036 · H) / (0,014453 · H)))      tarama çizgileri
```

Bu değerler örnek videoda 22 karelik ölçümle bulundu: orta parlaklık 0,145, p5 0,055, a* 6,6, b* 10,5, C* 12,2 / 18,4, köşe 0,22.
İlk denemelerde (sat 0,42, tek gama) koyu tonlar griydi (C* ortanca 7) ve siyahlar açıktı (p5 0,078); referansın tek tonlu görünümü
ancak kanal başına gama ile geldi.

## Doku

| Ölçü | Değer |
|---|---|
| Tarama çizgisi periyodu | yüksekliğin %1,445'i (altı videoda aynı; 1280'de 18,5 px, 1920'de 27,7 px) |
| Biçimi | yumuşak sinüs (ikinci harmonik birincinin < %9'u) |
| Genliği | ±%3,6 – 4,4 parlaklık (ortanca 3,9; sıkıştırmadan sonra) |
| Hareketi | aşağı doğru, kare başına yüksekliğin %0,033 – 0,044'ü (1920'de ~0,7 px/kare); saniyede ~0,75 periyot |
| Gren | çok zayıf: düz alanlarda artık gürültü σ ≈ 0,4 / 255 |
| Işık titremesi | kare kare parlaklık ±%0,4 (ortanca), şimşek anları hariç |
| Arka plan | tek planlarda güçlü alan derinliği (bokeh'li ışıklar), ikili planda hafif bulanık |

Tarama çizgileri altyazının ve filigranın altında: yazılar temiz.

## Örnek videoda (Soğuk Çay)

Orta parlaklık 0,141 · p5 0,051 · kontrast 0,61 · a* 6,8 · b* 10,4 · C* 12,5 / 18,4 · köşe 0,21 · tarama periyodu 0,01445, genliği 0,037: hepsi aralıkta.
Tam tablo: [README.md](README.md).

# Sepya Sohbet stili: ölçülmüş stil kitabı

Kaynak: kullanıcının verdiği, aynı kanaldan altı dikey video ("Bazen ..." başlıklı, iki hayvan karakterin gece sohbeti).
720 × 1280, 30 fps, 77,6 – 94,8 sn; toplam 521,6 sn, 15.649 kare. Videolar yalnızca stil çalışması için kullanıldı: repoda yoklar,
raporlarda `r1` – `r6` diye geçiyorlar. Karakterleri, kanal adı, logosu, kapanış sözü ve metinleri o kanalın; buraya alınan yalnızca
**sayılar ve yapı**. Bütün ölçümler `tools/olc.py` ile yapıldı; aynı aracı kendi videonuzda çalıştırıp aynı tabloyu alırsınız.

Ayrıntılı raporlar [`analiz/`](analiz/) içinde, ham sayılar [`analiz/veri/`](analiz/veri/) içinde. Bu dosya onların özeti.

## 1. Metin ve ses (ayrıntı: `analiz/metin.md`, `analiz/ses.md`)

| Ölçü | 6 referans: aralık (ortanca) |
|---|---|
| Süre | 77,6 – 94,8 sn (87) |
| Kelime | 105 – 148 (119) |
| Konuşma hızı, konuşulan sürede | 3,8 – 4,6 hece/sn (4,1); 1,55 – 2,0 kelime/sn |
| Konuşma hızı, bütün video | 1,3 – 1,6 kelime/sn |
| Satır arası boşluk | ortanca 0,4 – 1,0 sn; 1 sn'den uzun boşluk video başına 3 – 6 |
| İlk kelime | 0,0 – 1,5 sn (dördünde 0,0) |
| Akıl hocasının sesi | ≈ 88 Hz (78 – 99): çok kalın |
| Öğrencinin sesi | ≈ 245 Hz (205 – 289): ince, genç |
| Öğrencinin son repliği | konuşmanın %42 – 55'inde (45) |
| Satır sayısı | 15 – 28; öğrenci satırların ~%31'ini, kelimelerin ~%25 – 30'unu söylüyor |
| Ses yüksekliği | -14,1 LUFS (altısında da), LRA 2,4 – 4,0 LU |
| Müzik yatağı | sürekli, tonal (spektral düzlük < 0,01), yumuşak; boşluklarda sesin 4 – 10 dB (6) altında |

**Kurgu kalıbı** (6/6):

1. Öğrenci 0,0 sn'de birinci tekil bir itiraf ya da şikâyetle açıyor: "Babam beni hiç sevmedi." Giriş, selam yok.
2. Akıl hocası 2 – 4 kelimelik bir soruyla karşılık veriyor: "Adı ne?", "Ne konuştunuz?", "Nereden biliyorsun?".
3. 2 – 4 Sokratik soru; her biri somut bir nesneye ya da kişiye bağlı (mesaj, araba, garson, fanus, fotoğraf, durak).
4. Öğrenci itiraz ediyor ("Ama ..." 6/6), duraksıyor ("Şey, ..." 3/6), sonunda anladığını soruyla söylüyor ("Yani ... mı?" 3/6, "Ne? Anlamadım." 1/6).
5. Bundan sonra yalnızca akıl hocası konuşuyor: nesne üzerinden bir benzetme, sonra karşıtlıkla kurulmuş 3 – 6 kısa özdeyiş
   ("X değişmez ama Y değişir", "Bir hayır bir gece acıtır; söylenmemiş bir belki bir ömür").
6. Kapanış özdeyişi; çoğu "Unutma," ile (2/6) ya da bir eylem çağrısıyla ("Bu akşam cevap ver.").
7. Sabit kapanış sözü (kanalın imzası, 6/6), akıl hocasının sesiyle, ışıklar kararırken. **Kendi imza cümlenizi yazın.**

## 2. Kurgu ve kamera (ayrıntı: `analiz/kurgu.md`)

| Ölçü | 6 referans: aralık (ortanca) |
|---|---|
| Plan süresi (video ortancası) | 3,4 – 5,2 sn (3,85); bütün planlarda %10 – 90'lık dilim 2,1 – 6,7 sn |
| Kesme | yalnızca sert kesme; dakikada 12,9 – 15,9 (13,3). Geçiş efekti, kararma, kayma yok |
| Planın içinde kamera | %88'inde içeri itme; plan başına toplam %3,2 – 4,7 (3,8), kare başına ~%0,035 |
| İtmenin eğrisi | yavaş başlıyor, yavaş bitiyor: hareketin %12'si planın ilk çeyreğinde, %54'ü yarısında, %93'ü dörtte üçünde |
| Büyük hareket | 115 planın 12'si: %15 – 38 itme ya da %20 – 31 geri çekilme |
| Yana kayma | yok denecek kadar az: ortanca 0,08 px/kare (1080 genişlikte) |
| Plan türleri (115 plan, elle) | akıl hocası tek %35, öğrenci tek %30, nesne / ara plan %24, ikili %11 |
| İlk plan | ikili (3/6), öğrencinin yakını (2/6), nesne (1/6) |
| Son plan | her zaman akıl hocası (6/6); kapanış kartı bu planın üstünde |
| Mekân | video başına tek mekân, gece (6/6) |

## 3. Görüntü (ayrıntı: `analiz/renk.md`)

| Ölçü | 6 referans: aralık (ortanca) |
|---|---|
| Orta parlaklık | 0,118 – 0,192 (0,155): karanlık |
| Karanlık uç (p5) | 0,027 – 0,059 (0,049) |
| Kontrast (p95 − p5) | 0,44 – 0,62 (0,56) |
| Renk: Lab a* / b* | +5,9 – 7,5 (6,7) / +8,2 – 13,0 (9,8): sıcak kahve, hafif kırmızı |
| Renk yoğunluğu C* ortanca / p90 | 10,0 – 16,1 (12,9) / 15,7 – 19,3 (17,5): tek tonlu sepya, renkler yalnızca ipucu |
| Ton (doygun piksellerde) | 18° – 26° (turuncu-kahve) |
| En koyu ve en açık uç (RGB) | siyah ≈ (6 – 17, 1 – 5, 0 – 2), beyaz ≈ (180 – 237, 157 – 217, 140 – 204): saf beyaz yok, krem |
| Vinyet (köşe / merkez) | 0,17 – 0,31 (0,22): ağır |
| Tarama çizgisi (CRT) | periyot yüksekliğin %1,445'i (1920'de 27,7 px), genlik ±%3,6 – 4,4, aşağı doğru kare başına yüksekliğin %0,037'si kadar kayıyor |
| Gren | çok az (sıkıştırma silmiş); ışık titremesi ~%0,4 |
| Baskın palet | koyu kahveler: #22120b, #301e14, #402b1e, #533c2d, #6c503c … krem #dac6b8 |

## 4. Karakterler (ayrıntı: `analiz/karakter.md`)

- Düz 2B, kalın koyu kahve kontur (#2a1a12 civarı, siyah değil). Kontur genişliği ikili planda ~4,6 px, yakın planda ~10 px (1080 genişlikte): çizgi çizimle büyüyor ama yarı oranda.
- Hayvan kafalı, takım elbiseli / kazaklı, önden duran figürler. Gövde dikdörtgen, omuzlar yuvarlak, kollar kalın tüp, eller eldiven gibi.
- **Akıl hocası**: hep yarı kapalı göz kapakları (bilge, biraz alaycı), küçük gülümseme, koyu takım, kravat. Kalın ses.
- **Öğrenci**: iri yuvarlak gözler, parlak göz bebekleri, yanaklarda allık, abartılı kaşlar; ifadesi her satırda değişiyor. İnce ses.
- Kadrajda: ikili planda kafa genişliği karenin ~%27'si, kafalar %35 – 55 yükseklikte; tek planda ~%58, gözler %42'de; yakın planda ~%88, gözler %40'ta.
- Hareket kısıtlı: ağız konuşmayla (şekiller 2 kare duruyor), göz kırpma, kelimede ifade değişimi, arada bir el hareketi. Boşta sallanma yok.
- Gölgelendirme: tek ton gölge (cel), ışığın gelmediği yanda yumuşak bir bant.

## 5. Yazı (ayrıntı: `analiz/altyazi.md`)

| Öğe | Ölçü |
|---|---|
| Altyazı | tek kelime, büyük harf, kalın eğik çizgi roman yazısı (bizde Bangers), beyaz, koyu kontur + aşağı sağa gölge |
| Altyazının yeri | merkez yüksekliğin %76,4'ünde (bir videoda %72), harf yüksekliği yüksekliğin %2,8'i (1920'de 54 px) |
| Altyazı süresi | kelime başlarken çıkıyor, sonraki kelimeye ya da 0,35 sn sonrasına kadar kalıyor; konuşmanın %62 – 84'ünde ekranda |
| Filigran | kanal adı, tepede ortada (%5,3), aralıklı serif büyük harf, altın-kahve, genişlik ~%17,5, harf yüksekliği 1920'de ~18 px |
| Kapanış kartı | ışıklar 4 sn'de iniyor, akıl hocasının gözleri parlıyor, kanal adı altın serif olarak gözlerin üstünde (%27,9 yükseklik, genişlik %57); kararmadan sona ~7,8 sn |

## 6. Bizim kurallarımız

1. Karakter, kanal adı, logo, imza cümlesi ve metin bizim. Referanstan yalnızca sayılar ve yapı alınıyor.
2. Görünüm renk düzeltmesinden geliyor: sahne normal renklerle boyanıyor, `post.js` sepyaya çeviriyor. Elle sepya boyanmıyor.
3. Her plan ve her ifade bir kelimeye bağlı (`W()`, `L()`); saniye yazılmıyor.
4. Kamera hiç durmuyor: her plan ~%3,8 içeri itiyor; her on planda bir büyük hareket.
5. Video başına tek mekân, gece, görünen sıcak ışık kaynakları.
6. Son plan akıl hocası; kapanış kartı onun üstünde.
7. Bitince `tools/olc.py` ile ölçülüyor; her satır OK olmalı. Sonra video baştan sona izleniyor.

## Örnek videonun ölçümü (Soğuk Çay, aynı araçla)

Örnek video `ornek/soguk-cay.mp4`. Ses taslak (yerel Piper TTS, iki karakter için perde kaydırma). Ölçüm tablosu [`analiz/README.md`](analiz/README.md) sonunda.

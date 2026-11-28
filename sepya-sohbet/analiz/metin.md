# Metin: diyaloğun yapısı ve hızı

Yöntem: altı videonun sesi Whisper (faster-whisper, medium) ile kelime saatleriyle çözüldü. Konuşmacılar her satırın perdesinden
(pYIN, temel frekans ortancası) ayrıldı: ikisi arasında ~1,5 oktav fark olduğu için ayrım net. Hece = Türkçe ünlü sayısı.
Ham sayılar: [`veri/ses_metin_referans.json`](veri/ses_metin_referans.json).

## Sayılar

| Video | Süre (sn) | Kelime | Satır | Kelime/sn (bütün) | Hece/sn (konuşurken) | Satır arası boşluk ortanca / %90 (sn) | Öğrencinin son repliği |
|---|---|---|---|---|---|---|---|
| r1 | 93,4 | 116 | 19 | 1,31 | 4,11 | 0,79 / 1,13 | %45 |
| r2 | 77,6 | 105 | 15 | 1,43 | 3,79 | 1,03 / 1,98 | %55 |
| r3 | 89,2 | 130 | 23 | 1,51 | 4,49 | 0,42 / 1,20 | %44 |
| r4 | 94,8 | 148 | 28 | 1,60 | 4,58 | 0,62 / 1,00 | %45 |
| r5 | 81,9 | 114 | 16 | 1,45 | 4,07 | 0,78 / 1,27 | %42 |
| r6 | 84,8 | 123 | 25 | 1,50 | 4,09 | 0,69 / 1,52 | %46 |
| **Ortanca** | **87** | **119** | **21** | **1,47** | **4,10** | **0,73 / 1,24** | **%45** |

- Satırların ~%31'i öğrencinin; ama öğrencinin satırları kısa, akıl hocasınınki uzun: kelimelerin ~%70'i akıl hocasının.
- İlk kelime 0,0 sn'de (4/6) ya da 1,1 – 1,5 sn'de (2/6, müzik girişiyle).
- Son söz videonun bitmesinden ~3 sn önce bitiyor; sonra yalnızca logo ve müzik.

## Kalıp (6 videonun 6'sında)

| Vuruş | Ne | Ölçü / örnek yapı |
|---|---|---|
| 1. Açılış | Öğrencinin birinci tekil itirafı ya da şikâyeti | 3 – 6 kelime, düz cümle. "Bugün X'e yine Y yaptım." / "Z beni hiç ...madı." |
| 2. İlk soru | Akıl hocası kısa soruyla karşılık veriyor | 2 – 4 kelime: "Adı ne?", "Neden ...?", "Nereden biliyorsun?" |
| 3. Sorgu | 2 – 4 Sokratik soru, her biri somut bir şeye bağlı | "O garson seni bir daha görecek mi?", "Peki o mesajda ne yazıyor?" |
| 4. Direnç | Öğrenci itiraz ediyor, duraksıyor | "Ama ..." (6/6), "Şey, ..." (3/6) |
| 5. Kırılma | Öğrenci anladığını soruyla söylüyor | "Yani ... mı?" (3/6), "Ne? Anlamadım." (1/6). Konuşmanın %42 – 55'inde |
| 6. Ders | Yalnız akıl hocası: nesne üzerinden benzetme | fincanlar camın ardında misafiri bekler; fanusun camı her şeyi büyük gösterir |
| 7. Özdeyişler | 3 – 6 kısa cümle, karşıtlıkla | "X ... ama Y ...", "Bir A bir gece ..., bir B bir ömür." İkişer, üçer kelimelik eksiltili ikinci yarı |
| 8. Kapanış | Son özdeyiş ya da eylem çağrısı | "Unutma, ..." (2/6), "O yüzden bu akşam ..." |
| 9. İmza | Kanalın sabit sözü, ışıklar kararırken | 2 cümle, ~5 sn. **Sizinki size ait olmalı** |

Diğer gözlemler:

- **Hitap**: akıl hocası öğrenciye video başına 1 – 2 kez sabit bir hitapla sesleniyor (referansta kanala özgü). Kendi hitabınızı seçin ("çocuğum", "yavrum", isim).
- **Nesne**: 5/6 videoda hikâye tek bir somut nesneye bağlanıyor ve o nesne ara planda büyük gösteriliyor (mesaj, araba, fincan, fanus, fotoğraf). r1'de nesne yerine komşuların pencereleri.
- **Konu**: aile (anne, baba), arkadaşlık, aşk, korku, başkalarının ne diyeceği. Hep gündelik, hep içe dönük; ders ahlaki değil duygusal.
- **Ton**: akıl hocası hiç yargılamıyor, sorarak götürüyor; son cümleleri kısa ve kesin.

## Örnek videoda (Soğuk Çay)

| Ölçü | Referans | Soğuk Çay |
|---|---|---|
| Kelime | 105 – 148 | 118 |
| Satır | 15 – 28 | 21 |
| Hece/sn (konuşurken) | 3,8 – 4,6 | 4,32 |
| Öğrencinin son repliği | %42 – 55 | %77 (ek "Ya cevap vermezse?" satırı) |

Örnekte öğrencinin "Yani ben hep mi bekliyorum?" kırılması %52'de; sonraya eklenen "Ya cevap vermezse?" satırı kalıbı kasten esnetiyor
(akıl hocasının sonucunu sınayan bir itiraz). Kendi metninizde kırılmadan sonra öğrenciye en fazla bir kısa satır verin.

# Ses

Yöntem: ffmpeg `ebur128` (yükseklik), `silencedetect` (−40 dB, 0,25 sn); konuşmacı perdesi pYIN; müzik, son sözden sonraki kuyrukta ve
satır aralarında (Whisper satır sınırlarının 0,12 sn içi atılarak) spektral düzlük, kroma ve bant enerjisiyle incelendi.

| Video | LUFS | LRA | Akıl hocası (Hz) | Öğrenci (Hz) | Boşlukta yatak, sesin altında (dB) | −40 dB sessizlik |
|---|---|---|---|---|---|---|
| r1 | −14,1 | 4,0 | 92 | 248 | 10,1 | 1 |
| r2 | −14,1 | 3,4 | 82 | 246 | 5,8 | 1 |
| r3 | −14,2 | 2,4 | 96 | 205 | 6,6 | 2 |
| r4 | −14,1 | 2,6 | 84 | 289 | 6,3 | 0 |
| r5 | −14,1 | 2,9 | 78 | 247 | 4,4 | 1 |
| r6 | −14,1 | 3,7 | 99 | 211 | 6,0 | 1 |

- **Yükseklik**: altısı da −14,1 LUFS (platform normalizasyonu). Dinamik aralık dar (LRA 2,4 – 4).
- **Hiç sessizlik yok**: müzik baştan sona sürüyor; −40 dB altına inen an video başına 0 – 2.
- **Müzik**: tonal (spektral düzlük 0,0004 – 0,007), enerjinin %33 – 65'i 250 – 2000 Hz'de; yumuşak, ağırbaşlı (piyano / yaylı türü).
  Satır aralarında konuşmanın 4 – 10 dB (ortanca 6) altında; konuşma altında hafifçe kısılıyor. Her videoda başka bir parça, başka bir ton.
- **Sesler**: akıl hocası çok kalın (78 – 99 Hz), öğrenci ince (205 – 289 Hz); aralarında ~18 yarım ton. İkisi de hafif oda yankısıyla.
- **Efekt**: yalnızca mekânın sesi (yağmur, gök gürültüsü). Geçiş "whoosh"u yok, çünkü kesmeler sert.
- **Son**: son sözden sonra ~3 sn müzik; kanal adı çıkarken müzik hafifçe yükseliyor, görüntüyle birlikte sönüyor.

## Bizde (`audio/mix.py`)

| Parça | Ayar |
|---|---|
| Müzik | numpy ile sentez piyano + yumuşak ped; minör i – VI – III – VII, `MUSIC.key`, `MUSIC.bpm` (varsayılan Am, 66); 2,6 sn yankı |
| Müziğin seviyesi | sesin RMS'inin 7 dB altı; konuşurken 3 dB daha kısık (0,25 sn rampa) |
| Ambiyans | sete göre: kafe = oda tonu + uzak uğultu, sokak = rüzgâr, oda / ara plan = oda tonu; şimşekte gök gürültüsü; sesin 24 dB altı |
| Kapanış | müzik 3 sn'de %35 yükseliyor; kanal adıyla birlikte pes bir piyano notası; son 1,3 sn'de her şey sönüyor |
| Ses | 0,5 sn'lik hafif oda yankısı (%8) |
| Yükseklik | iki geçişli loudnorm: −14 LUFS, TP −1,5 |

Lisanslı bir parça kullanmak için: `python audio/mix.py stories/<ad> --muzik=parca.mp3`.

## Ses kaydı

- Taslak: `tools/taslak_ses.py` (yerel Piper TTS, Türkçe `dfki` sesi ~109 Hz; akıl hocası −2,5, öğrenci +9 yarım ton → ~94 / ~180 Hz).
- Kendi kaydınız, iki rolü tek seferde okuyarak: `tools/perde.py` her satırı konuşmacısına göre kaydırır. Erkek sesi (~115 Hz) için
  akıl hocası −4, öğrenci +8; kadın sesi (~200 Hz) için −12 / +3. Akıl hocasında formant korunuyor (doğal), öğrencide formant da kayıyor (küçük, çizgi film).
- Hız hedefi: konuşurken 3,8 – 4,6 hece/sn; satır arası ~0,7 sn. `kelime_saat.py` ikisini de yazar.

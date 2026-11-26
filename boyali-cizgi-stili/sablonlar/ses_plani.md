# Ses planı

Ölçülen hedefler: −21 LUFS entegre (−23 … −15), LRA 15 LU, true peak ≤ −1 dBFS. Enerji alt frekanslarda: 20-150 Hz bandı toplamın −3 dB'i, 2-6 kHz −15 dB. Konuşma yok.

## Katmanlar
1. **Ortam (sürekli, alçak):** çöl rüzgârı, uzak böcek vızıltısı. −35 … −30 dB RMS. Sessiz duraklamada bu da kısılır (−40 dB altı).
2. **Foley (aksiyona kare kare):** ip gerilmesi, yaprak hışırtısı, kum, yutma, tükürme, çırpınma. Tok ve gövdeli sesler seçin. Tiz ve çıtırtılı olanlardan kaçının.
3. **Vuruşlar (kesmelerle):** ters köşe anında en yüksek ses (tepe −1,5 dBFS). Kesmelerin en az yarısı ±0,1 sn içinde bir vuruşa denk gelmeli.
4. **Karakter nidaları:** "oh", "hıh", çığlık, inleme. Kelime yok.
5. **Müzik (isteğe bağlı, seyrek):** pizzicato ya da marimba gibi kısa komik vurgular. Sürekli bir müzik yatağı yok.

## Zaman çizelgesi
`kurgu.py` plan sürelerini yazdırır. Her vuruşu bu sürelere göre yerleştirin. Seslerin yasal kaynağı sizin sorumluluğunuzda: kendi kayıtlarınız, lisanslı kütüphaneler ya da ses üreten bir yapay zekâ olabilir.

## Miks ve normalize
```bash
# katmanları birleştir (örnek: 3 dosya)
ffmpeg -i ortam.wav -i foley.wav -i vurus.wav -filter_complex "amix=inputs=3:normalize=0" -ar 44100 miks_ham.wav
# −21 LUFS, LRA'yı ezmeden, tepe −1.5 dBTP
ffmpeg -i miks_ham.wav -af loudnorm=I=-21:LRA=18:TP=-1.5 -ar 44100 miks.wav
```
Sonra `python tools/olc.py son.mp4 olcum.json` ile `ses.lufs`, `ses.lra` ve `ses.true_peak_dbfs` değerlerini kontrol edin.

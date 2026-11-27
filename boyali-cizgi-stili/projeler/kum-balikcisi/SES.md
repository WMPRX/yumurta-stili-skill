# Kum Balıkçısı: ses planı

Hedefler: −21 LUFS, LRA ≥ 8 (referans 15), TP ≤ −1,5 dBTP. Konuşma yok. Saatler, `kurgu.json` ile birleştirilmiş videonun zaman çizelgesine göre.

| Saat | Plan | Katman | Ses | Seviye |
|---|---|---|---|---|
| 0,0–14,9 | 1-7 | ortam | Çöl rüzgârı, hafif kum hışırtısı | −32 dB |
| 0,6 | 1 | foley | Bambu oltanın gıcırtısı | orta |
| 1,6 | 1 | foley | Oltanın küçük "fışt" savruluşu | orta |
| 2,9 / 3,1 | 2 | foley | "tık … tık" (tahta tıkırtısı) | orta-yüksek |
| 3,4 | 2 | vuruş | Boğuk "plop" (kuma batma) | yüksek |
| 3,5 | 3 | foley | Islak balık çırpınması | orta |
| 4,6 | 3 | foley | "pfft" kum püskürmesi | orta-yüksek |
| 5,0–5,6 | 3 | nida | Tıkır'ın şaşkın "hıh", kırpıştırma | düşük |
| 6,4 | 3 | müzik | Kısa kibirli pizzicato (2 nota) | düşük |
| 7,0 | 4 | foley | Balığın kovaya düşüşü "tang" | orta |
| 7,3 | 4 | foley | Misina ıslığı (savurma) | orta |
| 7,5 / 8,3 | 4 | vuruş | Olta gerilme gıcırtısı + "hıngh" çaba nidası (sarsıntılarla aynı an) | yüksek |
| 9,0 | 5 | **vuruş** | Derin gürleme + kum çağlayanı (**en yüksek an**, tepe −1,5 dBTP) | en yüksek |
| 10,6 | 6 | vuruş | "vıııınn" çekilme + kısa çığlık | yüksek |
| 11,0 | 6 | foley | Taburenin yuvarlanması | orta |
| 12,4–14,9 | 7 | foley | Sürekli kum fışkırması, tümsek "güp"leri; "yuhuu" ↔ çığlık | yüksek |
| 14,9 | 8 | vuruş | Kuyruk şlapı (kum) | yüksek |
| 15,8 | 8 | foley | Kova "tonk" (yere iniş) | orta |
| 16,3–18,9 | 8 | **sessizlik** | Ortam −40 dB altına iner; yalnız bir göz kırpma "tık"ı | çok düşük |
| 18,9–20,9 | 9 | foley | Solucan takarken küçük ıslak ses; sinsi bakışta tek "tık" | düşük |
| 20,9 | 10 | vuruş | Kovadan fırlayış "fşşt" + "hap!" ısırma | yüksek |
| 21,1 | 10 | nida | Boğuk burun çığlığı "mmmh!" | yüksek |
| 23,7–25,7 | 11 | foley | Üç çekiştirme: "boing" lastik burun (sarsıntılarla aynı an) | yüksek |
| 25,7 | 12 | foley | Balığın şapkaya yerleşmesi, küçük hışırtı | düşük |
| 26,5–28,8 | 12 | sessizlik | Yalnız kısık rüzgâr | çok düşük |
| 27,6 | 12 | müzik | Tek marimba notası (göz yukarı kayarken) | düşük |
| 29,0 | 12 | vuruş | Uzaktan boğuk gürleme (balinanın gözü açılır) | orta |

Kesmelerin 7'si (2,6 · 7,0 · 9,0 · 10,6 · 14,9 · 20,9 · 23,7) bir ses vuruşuyla aynı anda başlıyor; referansta bu oran 7/11.

## Miks
```bash
ffmpeg -i ses/ortam.wav -i ses/foley.wav -i ses/vurus.wav -i ses/nida.wav -i ses/muzik.wav \
  -filter_complex "amix=inputs=5:normalize=0" -ar 44100 ses/miks_ham.wav
ffmpeg -i ses/miks_ham.wav -af loudnorm=I=-21:LRA=18:TP=-1.5 -ar 44100 ses/miks.wav
```

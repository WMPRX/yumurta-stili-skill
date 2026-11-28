# Ölçüm verisi

Altı referans video `r1` – `r6` (720 × 1280, 30 fps). Altyazı bandı (yüksekliğin %64 – 86'sı) ve kapanış kartı görüntü ölçümlerine girmiyor.

| Dosya | İçerik |
|---|---|
| `olc_referans.json` | `tools/olc.py`'nin altı referanstaki sonucu: `aralik` her ölçü için [en düşük, ortanca, en yüksek], `video` video video değerler. `olc.py`'nin hedef tablosu bu dosyadan |
| `kurgu_referans.json` | `ozet` video başına süre, kesme, plan sayısı ve süreleri, kapanış; `planlar` 115 planın her biri: `a`/`b` başlangıç–bitiş (sn), `len`, `ecc_tot` plan boyunca toplam yakınlaşma (%), `ecc_pf` kare başına (%), `ecc_tx`/`ecc_ty` kare başına kayma (1080 px), `zoom_*` optik akışla aynı ölçü (daha kaba), `y50` orta parlaklık |
| `renk_referans.json` | `video` renk ve ton ortancaları (y50, y5, kontrast, a*, b*, C* ortanca / p90, köşe/merkez); `siyah_beyaz` en koyu / en açık %0,5'in RGB'si; `palet` 10 renk kümesi ve payı (%); `radyal` merkezden köşeye 10 halkada parlaklık / merkez |
| `ses_metin_referans.json` | `konusma` kelime sayısı, ilk / son kelime, kelime/sn, konuşma payı, boşluklar, satır sayısı, iki sesin perdesi (Hz); `altyazi` altyazı değişim sayısı, ekranda kalma payı, ilk / son altyazı |

Metinlerin tamamı (transkriptler) repoya konmadı; raporlarda yalnızca yapıyı göstermek için birkaç kısa alıntı var.

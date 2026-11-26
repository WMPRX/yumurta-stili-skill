# Prompt şablonları (görsel ve video üreticileri için)

Promptlar İngilizce. Görsel ve video modelleri İngilizce stil terimlerine daha tutarlı yanıt veriyor. Aracın adı fark etmez: Higgsfield, Kling, Veo, Seedance, Runway, Midjourney, Flux ya da Nano Banana olabilir. Akış her araçta aynı:

1. **Karakter sayfası** (görsel): her karakter için tek bir referans görseli. Bütün planlarda bu görsel referans olarak verilir.
2. **Plan anahtar karesi** (görsel): her plan için bir ilk kare. Karakter sayfası referans olarak eklenir.
3. **Plan videosu** (görselden videoya): anahtar kare + hareket promptu, 3-5 sn üretilir, kurguda 0,9-4 sn'ye kırpılır.

Her promptu `[STİL]` + `[SAHNE]` + `[PLAN]` (+ videoda `[HAREKET]`) bloklarından kurun. `[STİL]` bloğu her seferinde **aynen** kullanılır. Tutarlılık buradan gelir.

---

## [STİL] — her görsel promptun sonuna aynen ekleyin

```
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

## [NEGATİF] — aracın negatif alanı varsa

```
black outlines, ink lines, cel shading, anime, manga, comic book, photorealistic, glossy plastic, specular highlights, PBR, lens flare streaks, neon colors, green grass, blue sky, deep blue, night, dark moody grade, pure black shadows, blue shadows, film grain, noise, vignette, chromatic aberration, text, subtitles, watermark, logo, extra fingers, deformed hands, multiple suns
```

---

## [KARAKTER] — karakter sayfası promptu

`karakter_sayfasi.md` içindeki tasarım kurallarıyla doldurun:

```
Character turnaround sheet of an original cartoon character for a stylized 3D animated short: {KİM: one-line concept, e.g. "a scrawny desert scavenger"}. Very dark desaturated plum-black skin (value very dark, like #362a38), smooth and matte. Huge round white eyes taking almost half the face (#faf4eb) with tiny pinpoint black pupils and a thick dark eyelid rim. Narrow mouth, can stretch into a wide grin with big white teeth. Long thin neck, thin limbs, oversized gloved hands with four fingers, pointy feet with {RENK} tips. Small warm accent: {pink/rust} cheeks or ear patches. Costume in 4-5 colours from the palette: {e.g. teal sleeves, cream cuffs, mustard-yellow high collar, rust leather strap and pouch, plum-grey knee pads}. Front, three-quarter, side and back views plus 6 facial expressions (neutral, sly half-lidded grin, wide-eyed shock, worried, panicked open mouth, smug). Plain light warm-grey background.
[STİL]
```

Bir karakter sayfasından en iyi görseli seçin, kaydedin (`karakterler/<ad>.png`) ve bütün planlarda referans olarak verin. Karakterin rengi ve kostümü planlar arasında kayarsa, sayfayı yeniden üretmek yerine referans görselin ağırlığını artırın.

---

## [PLAN] — plan türlerine göre anahtar kare blokları

`{…}` alanlarını doldurun, sonra `[SAHNE]` ve `[STİL]` ekleyin.

**A. Alttan kahraman / arzu planı (açılış)**
```
Extreme low-angle wide shot from ground level, framed between two out-of-focus foreground objects very close to the lens ({e.g. hanging fruits}), {KARAKTER} looming above against the bright sky, backlit by the sun with a soft glowing halo behind them, character partly in silhouette, eyes glowing white. {NE YAPIYOR}.
```

**B. Vurgu planı (0,8-1 sn'lik araç / parlama)**
```
Close-up, slightly low angle, {KARAKTER} holding {NESNE} up beside the face, a single small four-point sparkle glint on the {NESNE}, sly half-lidded grin, background soft.
```

**C. Yakın plan ifade (itme yapılacak)**
```
Close-up of {KARAKTER}'s face and hands filling the frame, {NESNE} in the hands in the foreground, background softly blurred desert and sky, expression: {İFADE}.
```

**D. Geniş aksiyon planı (yan profil)**
```
Wide side-on shot, full bodies, {KARAKTER} on the right third, {KARŞI ÖĞE} on the left, horizon at 58% of frame height, big pale teal sky, ochre sand foreground with dry-brush marks and small grass tufts, soft shadows cast to the {left/right}. {AKSİYON}.
```

**E. Ters köşe / canlanan dünya**
```
Same wide framing as before, {KARŞI ÖĞE} suddenly reveals a huge mouth lined with {e.g. small dark-red berry teeth}, inside a deep crimson-maroon (#23030c), {KARAKTER} caught mid-motion in a stretched pose.
```

**F. Sessiz duraklama (geniş, simetrik)**
```
Wide static shot, {KARAKTER} sitting dazed on the sand in the foreground right, {KARŞI ÖĞE} calm in the background left, scattered {props} on the ground, everything still, deadpan comedic pause.
```

**G. Güneşli alçak orta plan (ikinci deneme)**
```
Low medium shot near the ground, {KARAKTER} reaching a big gloved hand towards {NESNE} lying on the sand in the foreground, sly grin, the sun disc partly visible in the top-right corner with a soft cream halo, distant pink mesas on the left.
```

**H. Final tepki (sabit yakın-orta)**
```
Medium close-up, centred, static, {KARAKTER} looking straight at camera with huge white eyes, {DURUM: e.g. something coiled around the neck}, deadpan, {KARŞI ÖĞE} blurred in the background left, sand and sky behind.
```

## [SAHNE] — dünya bloğu (her projede bir kez yazın, sonra sabit tutun)

```
Setting: {e.g. a flat sunny desert of ochre sand dotted with small lilac flowers, a few round mustard-olive bushes, a distant pale teal-green plain and faded pink-red mesas on the horizon}.
```

---

## [HAREKET] — görselden videoya promptları

Video modelleri kamerayı kendiliğinden gezdirmeye meyillidir. Stil, **sabit ya da çok yavaş** bir kamera istiyor. Her hareket promptu kamera cümlesiyle başlar:

| Plan | Kamera cümlesi |
|---|---|
| Sabit | `Locked-off static camera, no camera movement.` |
| Yavaş itme | `Very slow steady push-in on the face, barely noticeable.` |
| Yavaş çekme | `Slow steady pull-back revealing the situation.` |
| Darbe | `Static camera with a short camera shake on the impact.` |

Ardından karakter aksiyonunu **poz poz** yazın:
```
{Kamera cümlesi} {KARAKTER} {1. poz}, then {2. poz}, then {3. poz}. Snappy cartoon timing: quick moves between clear held poses, motion-blur smears on fast moves, squash and stretch on impacts. Expression changes: {ifade 1} → {ifade 2} → {ifade 3}. Background stays still. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

Kurallar:
- 3-5 sn üretin. Kurguda 0,9-4 sn'ye kırpacaksınız. Video modelleri en iyi hareketi genellikle ilk 3 sn'de veriyor.
- Bir planda en fazla 2-3 poz değişikliği ve 2-4 ifade değişikliği olsun.
- Sakin planlarda (`F`, `H`) karakterin **durmasını** açıkça yazın: `the character stays completely still except for blinking and eye darts`.
- Aracınız "motion strength" benzeri bir ayar veriyorsa sakin planlarda düşük, aksiyonda orta-yüksek seçin.
- Ses üretme seçeneği varsa kapalı tutun. Ses ayrı hazırlanır (`ses_plani.md`).

---

## Kalite kontrolü (her anahtar karede)
- [ ] Siyah kontur yok mu?
- [ ] Gök teal mi (mavi değil)? Bitkiler hardal-zeytin mi (yeşil değil)?
- [ ] Karakter sahnenin en koyu öğesi mi, gözler en açığı mı?
- [ ] Gölgeler sıcak/zeytin mi, mavi değil mi? Güneş yönü önceki planla tutarlı mı?
- [ ] En fazla bir doygun vurgu nesnesi mi var?
- [ ] Kostüm renkleri karakter sayfasıyla aynı mı?

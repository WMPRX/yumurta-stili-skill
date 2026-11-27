# boyali-cizgi-stili

**Elle boyanmış dokulu 3B çizgi film görünümünde, sessiz komedi kısa filmleri için ölçülmüş stil + araç seti (Claude skill).**

Bir referans videonun (1920×1080, 25 fps, 29,8 sn) tasarımı ölçülerek sayılara döküldü: renk paleti, ton ve kontrast, ışık, karakter tasarım dili, plan süreleri, kamera hareketi, smear kesmeler, ses yüksekliği. Skill bu sayılarla kendi hikâyelerinizi üretmenizi ve sonucu aynı ölçülerle kontrol etmenizi sağlar. Referans videonun kendisi repoda yok. Yalnızca ölçümler ve paletler var.

## İçindekiler

| Yol | Ne |
|---|---|
| `SKILL.md` | Claude için skill: kurallar ve 9 adımlık iş akışı |
| `STIL_KITABI.md` | Ölçülmüş stil: format, yüzey, değer, renk, ışık, derinlik, karakter, kurgu, kamera, hareket, ses, hikâye yapısı, dikey uyarlama, yapılmayacaklar |
| `analiz/plan_listesi.md` | Referansın 12 planı, plan plan ölçümleriyle |
| `analiz/veri/referans_olcum.json` | Ham ölçüm (kare başına dahil) |
| `analiz/veri/hedefler.json` | 27 ölçü için hedef aralıklar |
| `analiz/veri/renk_hedef.json` | Ton yüzdelikleri ve bölünmüş ton (gölge/orta/ışık a-b) |
| `referans/` | Palet (genel + öğe öğe) ve ritim panoları |
| `sablonlar/` | Prompt blokları (stil, negatif, karakter, 8 plan türü, hareket), karakter formu, senaryo şablonu, ses planı, örnek `kurgu.json` |
| `tools/` | `olc.py`, `karsilastir.py`, `renk_esle.py`, `kurgu.py`, `kontakt.sh`, `pano.py`, `promptla.py` |
| `projeler/kum-balikcisi/` | İlk proje: senaryo, karakterler, hazır promptlar, kurgu ve ses planı; kodla iki taslak: `taslak/` (2B) ve `taslak25/` (2.5D), videoları `kum-balikcisi_taslak.mp4` ve `kum-balikcisi_25d.mp4` |

## Kurulum

1. Python 3.10+, ffmpeg/ffprobe.
2. `pip install -r requirements.txt`
3. **Claude Code:** bu klasörü `~/.claude/skills/boyali-cizgi-stili/` altına kopyalayın ve şöyle söyleyin: *"boyalı çizgi stiliyle … hakkında sessiz bir kısa film yapalım"*.

## Hızlı kullanım

```bash
# bir videoyu ölç ve stile ne kadar uyduğunu gör
python tools/olc.py video.mp4 olcum.json
python tools/karsilastir.py olcum.json

# klipleri kurgula, rengi eşle, ölç
python tools/kurgu.py projeler/ornek/kurgu.json kurgu.mp4
python tools/renk_esle.py kurgu.mp4 son.mp4
python tools/olc.py son.mp4 son.json && python tools/karsilastir.py son.json
```

## Özet ölçüler

| | Referans |
|---|---|
| Plan | 12 plan, ort 2,48 sn (0,88-4,08), kesmelerin %36'sı smear |
| Kamera | karelerin %39'u sabit; itme/çekme ≤ 0,21 %/kare; plan başına −12 … +8 % |
| Ton | L ort 56,6 · p1 8,6 · p99 89 · RMS kontrast 19,7 · en koyu #221a1f |
| Renk | HSV S 0,40 · kroma 24,5 · sıcak %58 / soğuk %39 · turuncu %36, cyan %31, yeşil %0,4, mavi %0 |
| Doku | kontur ‰1 · gren 0,54 |
| Ses | −20,8 LUFS · LRA 15,2 · TP −1,6 dBFS · konuşma yok |

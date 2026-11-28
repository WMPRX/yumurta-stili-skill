# sepya-sohbet

**Gece, sepya bir ışıkta iki hayvan karakterin sohbeti: bilge bir akıl hocası ve genç bir öğrenci. Claude ile, koddan, kare kare.**

Bu klasör, "Bazen ..." diye başlayan, iki hayvan karakterin karşılıklı konuştuğu duygusal dikey videoların görsel dilini ölçüp yeniden üreten bir skill:

- Sahneler ve karakterler Canvas 2D ile çiziliyor.
- Sepya renk, CRT tarama çizgileri ve vinyet tek bir WebGL geçişinde ekleniyor.
- Kareler Puppeteer ile tek tek yakalanıyor, ffmpeg ile birleştiriliyor.

Ses için iki yol var: taslak ses yerel TTS ile üretiliyor; kendi kaydınız varsa iki karakterin sesi perde kaydırmayla ayrılıyor. Müzik numpy ile sentezleniyor. Altı referans videodan alınan her ölçü `tools/olc.py` ile kendi videonuzda da kontrol edilebiliyor.

Örnek: **Soğuk Çay** (`stories/soguk-cay/`). Kirpi üç haftadır eski bir arkadaşına "Seni özledim" yazıp siliyor; Baykuş ona önündeki soğumuş çayı gösteriyor. 85 sn, 1080×1920, 30 fps.

▶ **Bitmiş video:** [`ornek/soguk-cay.mp4`](ornek/soguk-cay.mp4) · karakter sayfası: [`ornek/karakterler.png`](ornek/karakterler.png)

## İçindekiler

| Yol | Ne |
|---|---|
| `SKILL.md` | Claude için skill: iş akışı, kurallar, tuzaklar |
| `STIL_KITABI.md` | Altı referans videodan ölçülen sayıların özeti: metin, kurgu, kamera, renk, doku, karakter, yazı, ses |
| `analiz/` | Altı ayrıntılı rapor (metin, kurgu, renk, karakter, altyazı, ses) ve `veri/` altında ham ölçümler (JSON) |
| `engine/` | `render.mjs` (kare yakalama, kontrol kolajları), `faces.mjs` (karakter sayfası), `src/chars.js` (Baykuş, Kirpi: 9 ifade, 5 poz), `src/sets.js` (kafe, sokak, oda), `src/props.js` (telefon, çay, fotoğraf, pencere), `src/fx.js` (kar, yağmur, toz, buhar, hale, huzme, şimşek), `src/post.js` (sepya, vinyet, tarama çizgileri), `src/overlay.js` (altyazı, filigran, kapanış yazısı), `src/main.js` (plan seçimi, kamera, ağız senkronu, kapanış kartı) |
| `tools/` | `kelime_saat.py` (ses → konuşmacılı kelime saatleri), `taslak_ses.py` (yerel TTS ile taslak ses), `perde.py` (tek kayıttan iki karakter sesi), `zarf.py` (ağız senkronu), `olc.py` (videoyu referanslarla aynı yöntemle ölçer) |
| `audio/mix.py` | Sentez piyano + ambiyans + miks, −14 LUFS |
| `stories/soguk-cay/` | Örnek hikâye: `voice/script.txt`, `story.js`, ses ve kelime saatleri |
| `ornek/` | Örnek video ve karakter sayfası |

## Kurulum

1. Gerekenler: Node 18+, Python 3.10+, ffmpeg (rubberband filtresiyle; çoğu dağıtımda var), Google Chrome ya da Chromium (`CHROME_PATH` ile de verilebilir).
2. Paketler:
   ```bash
   cd engine && npm install
   pip install -r requirements.txt
   ```
3. Taslak ses için Türkçe Piper sesi (bir kez, ~63 MB):
   ```bash
   cd tools
   curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx
   curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json
   ```
4. **Claude Code:** bu klasörü `~/.claude/skills/sepya-sohbet/` altına kopyalayın ve şunu söyleyin: *"sepya sohbet stiliyle … hakkında bir video yap"*.
   **Başka bir ajan:** klasörü açıp *"SKILL.md'yi oku, sepya sohbet stiliyle … hakkında bir video yap"* deyin.

## Hızlı kullanım

```bash
# 1. Metin: stories/<ad>/voice/script.txt, her satır "ETİKET: cümle"; son satırı akıl hocası söyler
# 2. Ses (taslak ya da kendi kaydınız)
python tools/taslak_ses.py stories/<ad>/voice/script.txt stories/<ad>/voice/voice.wav --hiz=0.85
#    kendi kaydınız (iki rolü tek seferde okuyun):
#    python tools/kelime_saat.py ham.wav script.txt ham.json && python tools/perde.py ham.wav ham.json voice.wav '{"HOCA": -4, "CIRAK": 8}'
python tools/kelime_saat.py stories/<ad>/voice/voice.wav stories/<ad>/voice/script.txt stories/<ad>/voice/words.json
python tools/zarf.py stories/<ad>/voice/voice.wav stories/<ad>/voice/env.json
# 3. Planlar: stories/<ad>/story.js (örneği kopyalayın), sonra kontrol kolajı
cd engine && node render.mjs <ad> --shots --scale=0.5
# 4. Ses miksi ve video
node render.mjs <ad> --cues && python ../audio/mix.py ../stories/<ad> && node render.mjs <ad>
# 5. Ölçüm: her satır OK olmalı
python ../tools/olc.py ../stories/<ad>/out/<ad>.mp4
```

Kanal adınızı `story.js` içinde `BRAND.ad` olarak yazın: tepedeki filigran ve kapanıştaki altın yazı odur. Kapanış cümlesi (imzanız) metnin son satırıdır.

## Ölçülmüş stil

Altı referans video (77,6 – 94,8 sn) kare kare ölçüldü: kesmeler, plan süreleri, kameranın itme miktarı ve eğrisi, plan türleri, parlaklık, Lab renk değerleri, vinyet, tarama çizgilerinin periyodu, genliği ve kayma hızı, altyazının yeri ve boyu, filigran, kapanış kartının zamanlaması, konuşma hızı, iki sesin perdesi, müzik yatağının seviyesi, ses yüksekliği, diyaloğun yapısı.
Örnek videonun aynı araçla ölçümü [`analiz/README.md`](analiz/README.md) sonunda.

## Telif

Kod ve belgeler MIT lisanslı (repo kökündeki `LICENSE`). Bangers ve Cinzel yazı tipleri SIL Open Font License ile (`engine/fonts/OFL-*.txt`).
Referans videolar ve onların karakterleri, kanal adı, kapanış sözü ve metinleri sahiplerinindir; repoda yer almazlar. Skill yalnızca ölçülen sayıları ve yapıyı kullanır, karakterler ve metin sizin olmalıdır.

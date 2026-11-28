---
name: sepya-sohbet
description: Make a 75-95 s vertical "sepia dialogue" Short - two flat 2D animal characters in clothes (a calm, half-lidded mentor and a wide-eyed young one) talk at night in one warm-lit set; sepia grade, CRT scanlines, heavy vignette, slow push-in on every shot, hard cuts, one-word italic comic captions, a gold serif watermark and an end card where the lights go down and the mentor's eyes glow under the channel name. Canvas 2D + WebGL grade + puppeteer frame capture. Use when the user asks for a "sepya sohbet" / "bilge hayvan diyaloğu" / "Bazen ..." style motivational dialogue Short, or for videos "like the fox and rabbit ones".
---

# Sepia dialogue Short (Canvas 2D, frame capture)

Sample: `stories/soguk-cay/` (79 s of voice + end card, Turkish, an owl mentor and a hedgehog; draft voice from local Piper TTS).
Finished video: `ornek/soguk-cay.mp4`.

Measured style targets: `STIL_KITABI.md` (summary) and `analiz/` (six reports, raw numbers in `analiz/veri/`). Read the style book before writing anything.
Everything there was measured on six reference Shorts (77-95 s, 720×1280, 30 fps) with `tools/olc.py`, the same tool you run on your own render.

## Rules

- **Our own cast, name and words.** The references belong to another channel. Never reproduce their characters (a fox in a brown suit and red tie, a rabbit with round glasses and a green vest), their channel name or logo, their sign-off line, or their scripts. Take only the numbers and the structure. The default cast here is our own (`baykus` mentor, `kirpi` young one); add new species in `engine/src/chars.js`. The user's channel name goes in `BRAND.ad`; their own sign-off line ends every video.
- **One set per video**, at night, lit by practical warm lights (a pendant lamp, lit windows, a street lamp) against a cool night. Inserts of the story's key object are the only other pictures (6/6 references).
- **Structure** (`analiz/metin.md`): the young one confesses or complains at 0.0 s; the mentor answers with a 2-4 word question; 2-4 Socratic questions, each pinned to a concrete object; the young one protests ("Ama ...") and finally asks "Yani ...?"; that last line of the young one lands at 42-55 % of the speech; after it the mentor speaks alone to the end: a metaphor through the object, 3-6 short aphorisms built on antithesis, "Unutma, ..." and the sign-off line.
- **Pace**: 105-150 words, 77-95 s, 4.1 syllables/s while talking (3.8-4.6), about 0.7 s between turns. Slow and calm. `kelime_saat.py` prints both numbers.
- **Voices**: the mentor deep (≈ 88 Hz), the young one high (≈ 245 Hz). One person can voice both: `tools/perde.py` shifts each line's pitch by speaker.
- **Every shot and every expression is pinned to a word or a line** (`W('kelime')`, `L(i).start`). Never type seconds.
- **Shots**: median 3.8 s (3.4-5.2), hard cuts only, about 13 per minute. Cut on the speaker change, 0.2-0.25 s before the line starts. Mix: mentor singles 35 %, young-one singles 30 %, inserts 24 %, two-shots 11 %. The last shot is always the mentor (6/6); it carries the end card.
- **The camera never stops**: every shot pushes in about 3.8 % in total (`push: .05`, default), centred, eased in and out. About one shot in ten makes a big move (`push: .15-.35`, or a pull-out with a negative value). No pans, no handheld.
- **Characters do not idle.** No breathing, no bob. They blink (every 0.9-2.4 s, four frames, and once across every expression change), the speaker's mouth moves with the voice (shapes held two frames), expressions change on words, and a gesture (`poz`) now and then. The camera push is the only constant motion.
- **The look comes from the grade** (`engine/src/post.js`): paint sets and characters in ordinary colours; the grade makes them sepia. Do not paint sepia by hand. Change `LOOK` only after measuring (see step 7).
- **Captions**: one word at a time, Bangers, white with a dark outline and drop shadow, centre at 76.4 % of the height, cap height 2.8 % of the height, upper case with Turkish rules. Faces must stay above 70 %.
- **End**: on the sign-off line the lights go down over 4 s, the mentor's eyes start to glow at +1.2 s, the watermark fades at +3.6 s and the gold title (the channel name) appears at +4.2 s above the eyes; the camera pulls back 7 %; the picture fades to black over the last 1.3 s. Total ≈ 7.8 s from the start of the fade.

## Pipeline

1. **Targets.** Read `STIL_KITABI.md`, then `analiz/metin.md` before writing and `analiz/kurgu.md` before planning shots.
2. **Topic.** One everyday emotional situation (a parent, a friend, a habit, a fear) and ONE concrete object that becomes the metaphor (a cold glass of tea, an unsent message, a fishbowl, a photo). The object must be drawable as an insert.
3. **Script** `stories/<name>/voice/script.txt`, one spoken line per row, `TAG: text`:
   ```
   CIRAK: Üç haftadır aynı mesajı yazıp siliyorum.
   HOCA: Kime?
   ```
   The speaker of the LAST line is the mentor (the sign-off). Beats as in Rules → Structure. Check it against `analiz/metin.md`: length, the young one's last line at about 45 %, short mentor questions, aphorisms.
4. **Voice.**
   - Draft first (so shots can be timed before recording): `python tools/taslak_ses.py script.txt voice.wav --hiz=0.85` (local Piper TTS; download the voice once, see README).
   - Own recording, both roles in one take: `python tools/kelime_saat.py raw.wav script.txt raw_words.json` → `python tools/perde.py raw.wav raw_words.json voice.wav '{"HOCA": -4, "CIRAK": 8}'` (male voice; for a female voice try -12 / +3).
   - Then always: `python tools/kelime_saat.py voice.wav script.txt words.json` (keeps the script's spelling, adds speaker and line to every word; prints words/s and syllables/s) and `python tools/zarf.py voice.wav env.json` (lip-flap envelope).
5. **Story file** `stories/<name>/story.js` (copy the sample). It exports `NAME`, `FPS`, `BRAND { ad }`, `CAST { TAG: { tur, renk } }`, `MENTOR`, `MUSIC { key, bpm }` and `build({ W, L })` returning `{ shots, expr, poz, end: { at }, look }`.
   - **Shot**: `{ at, set, kind, who, ots, push, focus, pose, prop, opts, fx, flash, look }`.
     - `push`: total push-in over the shot (default `.05`); `0` holds; a negative value pulls out (starts that much closer, opens to the framing).
     - `kind`: `ikili` (both at the table; mentor left, young one right), `tek` (one character, head 58 % of the width, eyes at 42 %), `yakin` (close-up, head 88 %), `genis` (the two-shot from further away), `nesne` (insert).
     - `ots`: in a single, the other character as a soft out-of-focus shoulder in the lower corner (about a third of the singles in the references).
     - `set`: `kafe` (window on the night city, pendant lamp, round table with tea), `sokak` (apartment facade with lit windows, street lamp, snowy ledge, snow), `oda` (wallpaper, glass cabinet with cups, floor lamp, curtains, rainy window). New sets: add to `engine/src/sets.js` (`back(canvas)` paints once, `fore(g, W, H, k, kind)` draws the table/ledge, `lights` gives the glows).
     - `prop` for inserts: `cay` (`{ buhar, dolu, el }`), `telefon` (`{ kimden, mesajlar: [{ ben, metin } | { taslak: true, metin }], saat, metin, el, kol }`), `fotograf` (`{ kafalar }`), `pencere` (`{ kim }`), or your own function `(g, t, W, H, opts) => {}`.
     - `fx`: `kar`, `yagmur`, `toz` (default from the set). `flash: [t]`: a lightning double-flash at t (`mix.py` adds thunder).
   - **Expressions** `{ at, who, expr }`: `notr`, `bilge` (the mentor's default half-lid), `gulumse`, `uzgun`, `endiseli`, `saskin`, `dusunceli`, `kizgin`, `utangac`. They land two frames before their word. Change the young one's face at least once per line of theirs.
   - **Poses** `{ at, who, pose }`: `yan`, `masa` (default at a table), `el` (hand raised), `cene` (hand on chin), `telefon` (phone in both hands).
   - Look at every species × expression × pose on one page: `node faces.mjs` → `out/faces.png`.
6. **Stills before video.**
   ```bash
   cd engine
   node render.mjs <story> --shots --scale=0.5      # first / middle / last moment of every shot
   ```
   Check: faces above the caption band (70-84 %); nothing important cut by the frame; the speaker on screen during their line or a deliberate listener / insert shot; a phone or photo text readable; the over-the-shoulder shape only a soft edge; the mentor in the last shot.
7. **Measure.** Render, then compare with the references:
   ```bash
   node render.mjs <story> --cues && python ../audio/mix.py ../stories/<story> && node render.mjs <story>
   python ../tools/olc.py ../stories/<story>/out/<name>.mp4
   ```
   Every row should read OK. Typical fixes: shots too short → fewer shots; push too small → raise `push`; colour off → change `LOOK` in `post.js` (or `look` in the story) one value at a time; length low → the script is too short.
   For a quick colour check without a full render use `--stills` with 20 times across the story and look at the sheet.
8. **Sound** (`audio/mix.py`): a soft minor piano bed (i-VI-III-VII, `MUSIC.key`, `MUSIC.bpm`), synthesized, about 7 dB under the voice and ducked 3 dB while someone speaks; room tone / wind / rain per set; a low note when the title appears; two-pass loudnorm to -14 LUFS (all six references: -14.1). `--muzik=track.mp3` uses a licensed track instead.
9. **Final**: `node render.mjs <story>` → `stories/<story>/out/<name>.mp4` (1080×1920, 30 fps, crf 16, AAC 256k). About 3 frames/s on a laptop CPU.

## Gotchas

- **The mentor is the last speaker.** `taslak_ses.py` and `perde.py` pick the mentor as the speaker of the last line. If your video ends on the young one, pass the pitches explicitly.
- **Turkish word lookups.** `W()` lower-cases with Turkish rules and ignores punctuation except the apostrophe; `W('soğudu.')` and `W('soğudu')` are the same. Repeated words need `W('Ama', 2)`. A missing word throws with its name.
- **Saturated clothes break the sepia.** The grade keeps 12 % of the original colour (`sat`). A strongly saturated garment pushes chroma p90 over the references (19.3 max); keep paints mid-saturated.
- **Phone screens clip.** A white screen plus the glow goes to pure white after the grade; screens are painted grey-beige (`#cfc6b8`).
- **Over-the-shoulder size.** A big foreground head covers the speaker. The shape sits at 80 % out to the side and only its edge shows.
- **Old mix muxed.** `render.mjs` muxes `audio/mix.wav` if it exists. After changing the voice, run `--cues` and `mix.py` BEFORE the final render.
- **Font loading.** Captions and titles wait for `document.fonts.load`; a custom font must be declared in `engine/index.html`.
- **Swiftshader.** Without a GPU, Chromium renders WebGL in software (`--use-angle=swiftshader`). It is slower but exact.

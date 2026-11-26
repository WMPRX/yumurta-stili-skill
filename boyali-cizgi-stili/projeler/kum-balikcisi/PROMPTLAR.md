# Kum Balıkçısı: hazır promptlar

Bu sayfa `tools/promptla.py` ile `planlar.json` dosyasından üretildi; promptları değiştirmek için o dosyayı düzenleyip yeniden çalıştırın.

Her plan için:
1. **Anahtar kare** promptunu görsel üreticiye verin. `Referans` satırındaki görselleri ekleyin. Negatif alan varsa `Negatif` metnini girin.
2. Seçtiğiniz kareyi `kareler/NN.png` olarak kaydedin.
3. Kareyi ve **hareket** promptunu görselden videoya üreticisine verin. Belirtilen sürede üretip `klipler/<ad>.mp4` olarak kaydedin.

**Negatif (bütün anahtar kareler):**
```
black outlines, ink lines, cel shading, anime, manga, comic book, photorealistic, glossy plastic, specular highlights, PBR, lens flare streaks, neon colors, green grass, blue sky, deep blue, night, dark moody grade, pure black shadows, blue shadows, film grain, noise, vignette, chromatic aberration, text, subtitles, watermark, logo, extra fingers, deformed hands, multiple suns
```

## Plan 1: `01_arzu` (tür A, kurguda 2.6 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`

**Anahtar kare:**
```
Extreme low-angle wide shot from the surface of the sand lake, the camera lying on the sand. Very close to the lens and out of focus: the bright orange fishing float (#e07a10) on the left and a curling sand ripple crest on the right, framing the shot. Above them Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) sits on his folding stool on the shore, leaning forward, gripping the curved bamboo rod with both hands, the fishing line running taut down towards the lens. He is backlit by the sun with a soft glowing cream halo behind his hat, his body partly in silhouette, his big white eyes glowing.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. Tikir leans slowly forward over the rod, then gives the rod one small confident flick, then holds still, staring down at the float. The fishing line tightens. Snappy cartoon timing between clear held poses. Expression: determined, eyes narrowing slightly. Background stays still. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 2: `02_arac` (tür B, kurguda 0.9 sn, 3 sn üretin)

**Referans:** yok

**Anahtar kare:**
```
Extreme close-up of the bright orange fishing float (#e07a10) resting on the pale rippled sand of the sand lake, a thin taut fishing line rising out of frame, a small ring of sand ripples around it, soft background, warm sunlight with a soft shadow beside the float, one tiny four-point sparkle glint on the top of the float.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. The orange float twitches twice, tick tick, then is pulled straight down into the sand like into water, leaving a small ring of sand ripples spreading outwards. Quick snappy timing. Keep the painterly matte look, no outlines.
```

## Plan 3: `03_zafer` (tür C, kurguda 3.5 sn, 5 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_baligi.png`

**Anahtar kare:**
```
Close-up of Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders)'s face and gloved hands filling the frame, proudly holding up the small grumpy sand fish from the reference image (flat ochre body, rust fins, two small white eyes on top) right next to his face, the fish's tail flopping, sand grains falling from it. Background softly blurred sand lake and teal sky. Expression: proud wide grin with big white teeth.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Very slow steady push-in on the face, barely noticeable. Tikir holds the fish up proudly with a big grin, then the fish spits a puff of sand straight into his face, then Tikir blinks rapidly with sand on his face, then grins smugly again as if nothing happened. Snappy cartoon timing: quick moves between clear held poses. Expression changes: proud grin → wide-eyed shock → rapid blinking → smug half-lidded grin. Background stays still. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 4: `04_tirmanma` (tür D, kurguda 2.0 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`

**Anahtar kare:**
```
Wide side-on shot, full bodies. Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) on the right third of the frame leaning far back on his heels in his waders, pulling the bamboo rod which is bent like a bow; the taut line runs left across the sand lake to the foot of the round dune on the left, where the line disappears into the sand. The tin bucket beside him. Horizon at 58% of frame height, big pale teal sky, ochre sand foreground with dry-brush marks and small grass tufts, soft shadows cast to the right.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Static camera with a short camera shake on each hard pull. Tikir braces his boots in the sand and yanks the rod twice with all his strength, the rod bending further each time, sand spraying from his heels. Snappy cartoon timing, squash and stretch on the pulls. Expression: strained, gritted teeth, eyes squeezed. The dune stays still. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 5: `05_terskose` (tür E, kurguda 1.6 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_balinasi.png`

**Anahtar kare:**
```
Wide side-on shot, the same place as the fishing scene: the round dune on the left is rising up, revealing it is the giant sand whale from the reference image (back made of ochre sand with grass tufts and lilac flowers, cream grooved belly, huge maroon mouth), its huge sandy back lifting out of the ground with sand pouring off it like waterfalls, its small sleepy white eye opening, Tikir's fishing line hooked in the corner of its enormous mouth. Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) small on the right, frozen mid-pull in a stretched pose, eyes huge.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Slow steady pull-back revealing the situation. The dune heaves up and the giant sand whale surfaces, sand cascading off its back in waterfalls, its eye opening slowly; Tikir stays frozen in his pulling pose, only his eyes growing wider. Heavy, slow movement for the whale, frozen stillness for Tikir. Keep the painterly matte look, no outlines.
```

## Plan 6: `06_bedel_a` (tür D, kurguda 1.8 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_balinasi.png`

**Anahtar kare:**
```
Wide shot, centred: the tail of the giant sand whale from the reference image (back made of ochre sand with grass tufts and lilac flowers, cream grooved belly, huge maroon mouth) diving into the sand on the left, sand spraying high; Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) yanked off his stool, flying horizontally through the air towards the left, clinging to the bent rod with both hands, legs flapping, hat flying off; the stool tumbling on the sand.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. The whale dives into the sand and Tikir is yanked off his stool and flies horizontally across the frame clinging to the rod, legs flailing, the stool tumbling behind. Fast motion with motion-blur smears, squash and stretch. Expression: panicked open mouth. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 7: `07_bedel_b` (tür C, kurguda 2.5 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`

**Anahtar kare:**
```
Medium shot from the front, Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) being dragged through the sand on his boots like water-skiing, leaning back, clutching the rod with both hands, two big fans of sand spraying up on either side of him, the taut line pulling ahead out of frame, desert sky behind.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Slow steady pull-back. Tikir is dragged through the sand on his boots like water-skiing, sand fanning up on both sides, bouncing over small bumps. His expression switches rhythmically: a delighted grin, then terror, then a delighted grin again, then terror. Snappy cartoon timing, held poses between bumps. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 8: `08_duraklama` (tür F, kurguda 4.0 sn, 5 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_balinasi.png`

**Anahtar kare:**
```
Wide static shot. In the foreground right Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) is buried in the sand up to his neck, only his head with the crooked straw hat sticking out, his bamboo rod knotted like a pretzel sticking out of the sand next to him. In the background left the tail of the giant sand whale from the reference image (back made of ochre sand with grass tufts and lilac flowers, cream grooved belly, huge maroon mouth) rises out of the sand. The flat desert, calm sky, everything else still. Deadpan comedic pause.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. In the background the whale's tail slaps once and sinks slowly into the sand and disappears. A tin bucket drops from above and lands upright next to Tikir's head with a bounce. Then everything stays completely still; Tikir only blinks twice and his eyes dart sideways. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 9: `09_ikinci` (tür G, kurguda 2.0 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`

**Anahtar kare:**
```
Low medium shot near the ground. Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders), covered in sand, hat crooked, sits on the sand with legs stretched out, the tin bucket standing behind him on the right, threading a tiny pink worm onto the hook with his big gloved fingers; the bright orange fishing float (#e07a10) lies on the sand in the sharp foreground. The sun disc is partly visible in the top-right corner with a soft cream halo; faded pink mesas on the left. He looks at the camera with a sly half-lidded grin.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. Tikir slowly threads the tiny worm onto the hook, then turns his head to the camera and gives a sly half-lidded grin, then holds the pose. Small, sneaky movements. Behind him the bucket rattles and wobbles once, as if something inside moved. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 10: `10_terskose2` (tür C, kurguda 2.8 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_baligi.png`

**Anahtar kare:**
```
Medium close-up of Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) recoiling backwards, the small grumpy sand fish from the reference image (flat ochre body, rust fins, two small white eyes on top) clamped onto his nose with its teeth, the fish's body hanging and flapping, sand flying from the overturned bucket behind him.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Slow steady pull-back. The small sand fish leaps out of the bucket and clamps onto Tikir's nose; Tikir jerks backwards, his eyes bulging, arms flung up, the fish dangling and flapping from his nose. Snappy cartoon timing with motion-blur smears on the leap, squash and stretch on the bite. Expression changes: sly grin → shock → pain. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 11: `11_panik` (tür C, kurguda 2.0 sn, 4 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_baligi.png`

**Anahtar kare:**
```
Medium shot, Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) spinning in panic, pulling at the small grumpy sand fish from the reference image (flat ochre body, rust fins, two small white eyes on top) that is biting his nose; his nose stretched long like rubber, eyes watering, hat askew, teal sky behind.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Static camera with a short camera shake on each yank. Tikir spins around and yanks at the fish with both hands three times; each time his nose stretches like rubber and snaps back, the fish refuses to let go. Fast cartoon timing, squash and stretch, motion-blur smears. Expression: panicked, eyes watering. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

## Plan 12: `12_final` (tür H, kurguda 4.0 sn, 5 sn üretin)

**Referans:** `karakterler/tikir.png`, `karakterler/kum_baligi.png`, `karakterler/kum_balinasi.png`

**Anahtar kare:**
```
Medium close-up, centred, static. Tikir (the scrawny dark plum-skinned fisherman from the reference image: huge white eyes with pinpoint pupils, mustard straw hat, faded teal vest, cream shirt, rust-orange waders) looks straight at the camera with huge white eyes, deadpan, a red sore nose; the small grumpy sand fish from the reference image (flat ochre body, rust fins, two small white eyes on top) is curled up comfortably on top of his straw hat. Behind him, blurred in the background, the round sandy dune with grass tufts and lilac flowers, the desert and the teal sky.
Setting: a flat sunny desert. In the middle a round 'sand lake': a shallow circular hollow of finer, paler sand (#e0c98a) with concentric ripple rings like water, its rim slightly darker. Behind the lake a round sand dune with tufts of mustard dry grass and a few small lilac flowers. Small lilac flowers dotted on the ochre sand, a distant pale teal-green plain and faded pink-red mesas on the horizon. Tikir's folding stool and teal-grey tin bucket on the shore.
Stylized 3D animated film still with hand-painted textures, painterly matte surfaces, visible gouache-like brush texture on sand, foliage and fabric, NO outlines, NO cel-shading lines. Soft warm late-morning sunlight from behind and to the side, one sun, soft-edged cast shadows on the ground, cool teal sky fill light. Palette: dusty teal sky (#72afb7–#8abec0), ochre sand (#d1b974), mustard-olive foliage (#9e803b), warm cream highlights (#eeebd2), rust and burnt orange accents, very dark plum-black for the darkest tones (#1a111c), never pure black. Shadows keep the surface hue and go darker and duller (olive, plum), never blue or grey. Medium-low saturation, dusty pastel world with ONE saturated accent object. Gentle atmospheric perspective: distant plain pale teal-green, distant mesas faded pink-red. Shallow but soft depth of field. Clean image, no film grain, no vignette. 16:9 cinematic framing.
```

**Hareket:**
```
Locked-off static camera, no camera movement. Tikir stays completely still and stares at the camera deadpan; then only his eyes roll up towards the fish on his hat; then his eyes slide sideways. In the blurred background a small sleepy white eye slowly opens in the dune. No other movement. No talking, no lip sync. Keep the painterly matte look, no outlines.
```

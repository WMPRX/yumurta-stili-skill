# Stil Kitabı: Boyalı Çizgi (painterly 3D, sessiz komedi)

Bu kitaptaki sayılar tek bir referans videonun ölçümünden geliyor: 1920×1080, 25 fps, 29,8 sn, H.264 ~7,5 Mbit/s, AAC 44,1 kHz stereo. Ölçüm aracı `tools/olc.py`, ham veri `analiz/veri/referans_olcum.json`, hedef aralıklar `analiz/veri/hedefler.json`. Panolar `referans/` klasöründe.

Kısaca stil şu: elle boyanmış dokulu, konturu olmayan, mat bir 3B çizgi film. Gündüz bir çölde teal gökyüzü okra kumla karşı karşıya. Çok koyu, mor-siyah tenli ve kocaman beyaz gözlü bir karakter bu açık zeminde siluet gibi okunur. Diyalog yoktur. Hikâye pandomim, yüz ifadesi ve ses efektiyle anlatılır. Planlar 2,5 sn civarındadır, kamera çoğunlukla sabittir ya da yavaşça iter/çeker, darbelerde sarsılır.

---

## 1. Görüntü formatı

| Ölçü | Referans | Kural |
|---|---|---|
| Çözünürlük | 1920×1080 (16:9) | Yatay ana format. Dikey (9:16) gerekiyorsa bölüm 9'a bakın |
| Kare hızı | 25 fps | 24 ya da 25. 30/60 fps hareketi "oyun" gibi akışkan yapar |
| Süre | 29,8 sn | 25-40 sn: tek bir şaka zinciri |
| Bit hızı | 7,5 Mbit/s | Teslimde ≥ 8 Mbit/s, `-crf 16-18` |
| Ses | AAC 44,1 kHz stereo, 128 kbit/s | Teslimde 192 kbit/s |

## 2. Görsel dil

### 2.1 Yüzey ve doku
- **Kontur çizgisi yok.** Ölçülen ince koyu çizgi yoğunluğu ‰1 (7 px black-hat > 40). Biçimleri renk ve değer farkı ayırır. Göz kenarı, ağız ve parmak araları gibi koyu "çizgi" görünen yerler aslında boyanmış biçimlerdir.
- **Elle boyanmış dokular.** Kumda kuru fırça lekeleri ve küçük ot tutamları var. Çalı, tek tek yaprak biçimlerinden oluşan kümeler hâlinde boyanmış. Kumaş ve deride hafif fırça izi ve aşınmış kenarlar görülüyor. Doku fırça izinden gelir, film greninden değil: gren 0,54 (neredeyse sıfır).
- **Mat gölgelendirme.** Yüzeylerde parlak yansıma yok. İstisnalar tek bir yumuşak beyaz parlama noktası taşır: meyvenin cam gibi "gözü" ve bıçak ağzı (yıldız parıltısı bir kez, bir vurgu planında).
- **Formlar yuvarlak ve abartılı:** uzun ince boyun ve bacaklar, iri eller (4 parmak, eldivenli), sivri uçlu ayaklar, yuvarlak kask.

### 2.2 Değer (açık-koyu) yapısı
Stilin en ayırt edici ölçüsü şu: **karakter sahnenin en koyu şeyi.**

| Öğe | Lab L | Not |
|---|---|---|
| Ten (gölge / orta / ışık) | 6 / 19 / 24 | Mor-siyah, kroma ~11 |
| Göz akı | 96,5 | Sahnenin en açık yüzeyi, sıcak beyaz #faf4eb |
| Gök | 68-74 | Ufka doğru biraz açılıyor |
| Kum (ışık / gölge) | 76 / 47 | Gölge/ışık oranı 0,62 |
| Ortalama kare | 56,6 | Geniş planlar 61-64, yakın planlar 34-48 |

- Göz akı ile ten arasında 70+ L fark var. Yüz uzaktan bile iki beyaz diskten okunur.
- Koyu uç p1 = L 8,6, açık uç p99 = L 89. En koyu RGB #16 0f 13 (mor-siyah). Saf siyah (RGB<8) yalnızca ağız içinde, karelerin %4'ünde.
- RMS kontrast 19,7. Geniş planlar 12-16 (havadar, düşük kontrast), yakın planlar 26-28.

### 2.3 Renk
Paletin ekseni **teal ↔ turuncu**. Kroma ağırlıklı ton aileleri şöyle:

| Aile | Pay | Nerede |
|---|---|---|
| Turuncu (15-45°) | %35,7 | Kum, meyve, deri, çanta, çalı |
| Cyan (165-195°) | %30,7 | Gök, kask, kol |
| Sarı | %13,5 | Yelek, krem, güneş halesi |
| Kırmızı | %8,8 | Uzak kayalar, yanak, kask benekleri, ağız |
| Yeşil-cyan | %7,4 | Uzak ova (gökle kum arasındaki köprü) |
| Yeşil, mavi, mor, magenta, pembe | toplam < %3 | Küçük çiçekler (lila), tek tük mavi bitki |

- Sıcak %58, soğuk %39. Arada denge var: hiçbir plan tek renk ailesine düşmüyor.
- **Saf yeşil yok** (%0,4). Bitkiler hardal-zeytin rengi (#9e803b, #a68b42). Yeşil çimen ya da yeşil yaprak bu stilin dışında.
- **Saf mavi yok.** Gök teal (#72afb7 – #8abec0, ton 183-187°), lacivert değil.
- Doygunluk orta düzeyde: HSV S 0,40, Lab kroma ort. 24,5, p90 44. Tozlu-pastel bir dünya. En doygun öğe tek bir vurgu nesnesi (meyve #d57906, kroma 72). **Her planda en fazla bir doygun vurgu** olur.
- **Bölünmüş ton (ölçülen):** gölgeler (L<30) mor-erik (a +7, b +3,5), orta tonlar okra (b +16), ışıklar teal (a −14,5). Klasik "teal gölge / turuncu ışık" grade'inin tersi: gölgeler sıcak mor, ışıklar soğuk teal.
- **Gölge rengi:** gölge, yüzeyin tonunu korur (kum gölgesi de 45°). Değeri yaklaşık 0,62'ye iner, kroması yarıya düşer. Gölge mavi ya da gri olmaz, kirli-zeytin olur.
- Atmosfer perspektifi: uzak ova yeşilimsi teal ve açık (#8ebcb1, L 73), uzak kayalar soluk pembe-kırmızı (#bb8180). Uzaklaştıkça kontrast ve kroma düşer, gök rengine yaklaşır.

Palet panoları: `referans/palet_genel.png`, `referans/palet_ogeler.png`.

### 2.4 Işık
- **Tek anahtar ışık var: güneş.** Sıcak beyaz, yüksekten ve çoğunlukla arkadan-yandan gelir. İki planda güneş diski kadrajın içinde, köşede kırpılmış olarak görünür (#fdfef4) ve geniş yumuşak bir hale taşır (#eeebd2). Açılış planı tam ters ışıktadır: karakterin ardında hale var, karakter yarı siluet.
- **Dolgu ışığı gökten gelir:** teal, yumuşak, yönsüz. Bu yüzden gölgeler simsiyah olmaz.
- **Gerçek düşen gölgeler:** karakterler ve nesneler kuma belirgin ama kenarı yumuşak gölge düşürür (yön tutarlı). Gölge/ışık değer oranı yaklaşık 0,6.
- Rim ışığı ya da renkli efekt ışığı yok. Gece yok, iç mekân yok.

### 2.5 Derinlik ve lens
- Belirgin ama yumuşak alan derinliği (dof ölçüsü 1,24; 0,66-2,1 arası). Yakın planlarda arka plan flu ama tanınır, geniş planlarda neredeyse her şey net.
- **Ön plan çerçeveleme:** açılış planı kameraya çok yakın, flu iki nesnenin arasından çekiliyor (alttan, geniş açı). Bunu en az bir planda kullanın.
- Ufuk geniş planlarda kadrajın %55-60 yüksekliğinde. Gök kadrajın üst yarısını doldurur.
- Vinyet yok (köşe/merkez parlaklık 1,25; köşeler gök olduğu için açık).

## 3. Karakter tasarım dili

Referanstaki karakteri kopyalamayın. Kendi karakterlerinizi aşağıdaki **kurallarla** tasarlayın:

1. **Değer:** ten çok koyu ve doymamış (L 15-25, kroma ≤ 12, mor/erik/kahve-mor). Açık gökyüzü önünde siluet olarak okunmalı.
2. **Gözler:** yüzün yarısına yakın, iki büyük beyaz disk. Göz bebekleri iğne ucu kadar küçük ve siyah. Kalın, koyu bir göz kapağı kenarı var. İfadenin %80'ini gözler taşır: disk büyür, küçülür, kapak iner (sinsi yarım kapak), bebek kayar.
3. **Ağız:** dar, ince. Ya düz bir çizgi ya da geniş bir sırıtma (beyaz, iri dişler). Panikte büyük açık oval olur (ağız içi #23030c).
4. **Oranlar:** uzun ince boyun, ince uzuvlar, iri eller (eldiven), sivri ve renkli uçlu ayaklar. Gövde kostümle hacimlenir.
5. **Kostüm:** paletten 4-5 renk (teal, krem, hardal-sarı, pas/deri, mor-gri). Bir küçük sıcak vurgu: yanak/kulak pembesi #ac594f, kask benekleri #d6837d. Kostüm rengi gök teal'iyle akraba ama ondan koyu (kol teal L 35, gök L 68). Böylece karakter gökten ayrılır.
6. **Aksesuar:** hikâyenin nesnesi (referansta bir bıçak ve bir meyve). Sahnenin tek doygun vurgusu bu olabilir.
7. **Canlı sahne öğeleri karakter gibi davranır:** ağzı olan çalı, gözlü meyve, kırkayak. Tasarımları dünyanın paletinden çıkar (hardal çalı, kırmızı-bordo ağız içi, turuncu meyve).
8. **İfade sıklığı:** konuşma olmadığı için ifade sık değişir. Yakın planda yaklaşık her 0,5-1,0 sn'de bir (sırıtma → şaşkın → endişeli → sırıtma). Komik geri dönüşler (bir sırıtma, bir korku) ritimli olur.

`sablonlar/karakter_sayfasi.md` bu kuralları bir karakter sayfası promptuna çevirir.

## 4. Kurgu ve ritim

| Ölçü | Referans | Hedef |
|---|---|---|
| Plan sayısı | 12 / 29,8 sn | 30 sn başına 10-14 |
| Plan süresi ort / medyan | 2,48 / 2,28 sn | 1,9-3,1 sn |
| En kısa | 0,88 sn (vurgu: bıçak parlaması) | 0,6-1,4 |
| En uzun | 4,08 sn (sessiz şaşkınlık duraklaması) | 3,2-5,0 |
| Smear ile giren kesme | 4/11 (%36), 1-5 kare | %20-60 |

- **Kesme türü:** çoğunlukla düz kesme. Aksiyonun ortasında kesilen planlar (yutulma, fırlatılma, saldırı) 1-5 karelik **smear** ile girer: bulanık, yönlü bir hareket karesi. `tools/kurgu.py` bunu `"gecis": "smear"` ile yapar.
- **Plan ölçeği dağılımı (12 plan):** 4 yakın (yüz ya da yüz+el), 3 orta (bel üstü), 4 geniş (tüm vücut + çevre), 1 alttan kahraman planı. Ölçek her kesmede değişir. Aynı ölçek arka arkaya en fazla 2 kez gelir.
- **Ritim eğrisi** (`referans/ritim.png`): giriş sakin, ses kısık (0-7 sn) → aksiyon ve ilk büyük ses (9-10 sn) → yutulma ve çırpınma → tükürülme → **3 sn'lik sessiz duraklama** (16-19 sn; ses neredeyse sıfır) → ikinci deneme → ikinci felaket → son tepki planı (en uzun ikinci plan, 3,96 sn).
- 11 kesmenin 7'si ±0,1 sn içinde bir ses vuruşuna denk geliyor. **Kesmeyi sese, sesi aksiyona oturtun.**

## 5. Kamera

| Ölçü | Referans |
|---|---|
| Fiilen sabit kare oranı | %39 |
| Öteleme hızı medyan / p90 | 0,41 / 2,3 px/kare (1920 genişlikte) |
| Zoom hızı p90 | 0,21 %/kare |
| Plan başına toplam itme/çekme | −12 … +8 % (çoğu ±0-3 %) |
| Dönme | ~0 (dutch açı yok) |
| Sarsıntı (darbe planları) | 1,1-2,5 px ortalama |

- Kamera **çoğunlukla kilitli** ya da çok yavaş itiyor/çekiyor. Whip pan, whip zoom ya da orbit yok.
- **Yavaş itme:** bir karakter planı (yakın) boyunca +8 % (3,5 sn). İfadenin "anlamını" büyütür.
- **Yavaş çekme:** felaket anında −7 … −12 % (2,5-2,8 sn). Durumu ortaya serer.
- **Darbe sarsıntısı:** çekiştirme, yutulma ve çırpınma anlarında, 0,3 sn'de sönen 4-8 px titreme.
- **Açılar:** göz hizası ağırlıklı. Bir açılış planı çok alttan, geniş açıyla ve ön plan nesneleri arasından çekilmiş. Karakter geniş planlarda sağ üçte birde, yakın planlarda ortada.

## 6. Hareket ve animasyon
- Animasyon "AI-3B" akıcılığında ama **poz-poz okunur**: büyük ve net pozlar, arada hızlı geçişler. Hızlı hareketlerde hareket bulanığı var (smear, uzayan uzuvlar).
- Kamera hareketi çıkarıldıktan sonra kalan özne hareketi plan başına 0,6-4,7 (ortalama kare farkı, 0-255). Sakin planlarda karakter de sakindir (0,6 - 1,3) ve **gerçekten durur**. Komik duraklamada yalnızca gözler kıpırdar.
- Squash & stretch: çırpınma ve fırlatmada abartılı. Duruşta yok.

## 7. Ses

| Ölçü | Referans |
|---|---|
| Entegre yükseklik | −20,8 LUFS |
| Yükseklik aralığı (LRA) | 15,2 LU (çok dinamik) |
| True peak | −1,6 dBFS |
| Bant dağılımı | 20-150 Hz −3 dB · 150-500 −5 · 500-2k −7 · 2-6k −15 · 6-8k −26 |
| Konuşma | Yok (yalnızca nida: "Oh", çığlık, inleme) |

- **Diyalog ve anlatıcı yok.** Ses = ortam (rüzgâr, hafif çöl ambiyansı) + foley (ip gerilmesi, yaprak hışırtısı, yutma, tükürme) + karakter nidaları + kısa müzik vurguları.
- Ses ağırlıkla alt frekanslarda: tok darbeler ve gövdeli foley. Tiz parlaklık az.
- **Sessizlik bir araçtır:** 16-19 sn'de ses −40 dB'nin altına iner. Komik duraklama sessiz geçer, sonra ses geri gelir.
- Kesmelerin %64'ü bir ses vuruşuyla aynı anda (±0,1 sn).

## 8. Hikâye yapısı (sessiz gag, ~30 sn)

Referansın akışını genelleştirince şu yapı çıkıyor. Kendi hikâyenizi bu kalıpla yazın:

| # | Vuruş | Süre | Plan |
|---|---|---|---|
| 1 | **Arzu:** karakter ve istediği şey tek karede (alttan, ön plan çerçeveli) | 2-3 sn | 1 |
| 2 | **Araç / plan:** kısa vurgu (parlama, göz kırpma) | 0,8-1 sn | 1 |
| 3 | **Küçük zafer + kibir:** yakın planda yavaş itme, ifade 3-4 kez değişir | 3-4 sn | 1 |
| 4 | **Tırmanma:** daha büyüğünü ister, çaba (geniş, sarsıntı) | 2 sn | 1 |
| 5 | **Ters köşe 1:** dünya geri ısırır (smear ile) | 1,5-2 sn | 1 |
| 6 | **Bedel:** yutulma / sıkışma, çırpınma (geniş → orta, çekme) | 4-5 sn | 2 |
| 7 | **Sessiz duraklama:** bön bakış, ses yok | 3-4 sn | 1 |
| 8 | **İkinci deneme:** ders alınmamış, sinsi sırıtma (sıcak ışık, güneş kadrajda) | 2 sn | 1 |
| 9 | **Ters köşe 2:** daha küçük ama daha komik felaket (smear) | 2-3 sn | 1-2 |
| 10 | **Final tepkisi:** sabit kamera, ifade ritmi, döngüye bağlanabilir | 3-4 sn | 1 |

`sablonlar/senaryo_sablonu.md` bu tabloyu doldurulacak forma çevirir.

## 9. Dikey (9:16) uyarlama
Referans yataydır. Dikey üretimde:
- Geniş planlarda ufuk %62-68 yükseklikte. Karakter alt üçte bire, gök üstte geniş kalır.
- Yakın planlarda göz hattı yükseklikte %35-42.
- Plan süreleri aynı kalır. Kamera kuralları aynıdır.
- `kurgu.json` içinde `"boyut": [1080, 1920]` verin. `olc.py` ölçüleri de çalışır, yalnız px/kare değerleri 1080 genişliğe göre yorumlanmalı.

## 10. Yapılmayacaklar
- Siyah kontur, cel-shading çizgisi, anime göz parlaması.
- Parlak plastik ya da gerçekçi PBR yüzeyler, ıslak yansımalar, lens flare zinciri.
- Yeşil çimen, mavi gök, neon renk, gece sahnesi, karanlık grade.
- Saf siyah gölgeler, mavi gölgeler.
- Whip pan, hızlı orbit, drone sallantısı, 30/60 fps.
- Diyalog, altyazı, anlatıcı (bu stil pandomimdir).
- Film greni ve VHS gibi bozulma efektleri.
- Referanstaki karakteri, meyveyi, çalıyı ya da kurguyu birebir kopyalamak.

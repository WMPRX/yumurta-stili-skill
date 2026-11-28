# Karakterler

Yöntem: tam çözünürlükte yakın, bel üstü ve ikili plan karelerinden %10'luk ızgarayla ölçüldü; kontur kalınlığı koyu piksellerin
uzaklık dönüşümünün sırtından (1080 genişliğe çevrildi). Karakterlerin kendisi referans kanalın; buradaki sayılar yalnızca
**bizim** karakterlerimizi aynı görsel dile oturtmak için.

## Ortak çizim dili

| Öğe | Ölçü / gözlem |
|---|---|
| Kontur | koyu kahve, siyah değil (≈ #2a1a12 düzeltmeden sonra); her parçanın etrafında |
| Kontur kalınlığı | ikili planda ~4,6 px, tek planda ~7 px, yakın planda ~10 px (1080 genişlikte): çizgi figürle büyüyor ama yarı oranda. Bizde `lw = 3,1 + 0,0076 × kafa genişliği (px)` |
| Boyama | düz renk + tek ton gölge bandı (cel), ışığın gelmediği yanda yumuşak geçişle |
| Duruş | önden, simetrik, kameraya bakan; omuzlar yuvarlak, gövde dikdörtgen |
| Kollar | kalın tüp (kafa genişliğinin ~%20'si), dirsekte kıvrım çizgisi, eldiven gibi eller |
| Kıyafet | ayrıntılı ama sade: yaka, kravat / papyon, cep, düğme, örgü deseni |
| Boy | kadrajda göğüs hizasından kesiliyor; bel altı neredeyse hiç görünmüyor |

## Kadrajda yer

| Plan | Kafa genişliği / kare genişliği | Göz hizası (yükseklik) |
|---|---|---|
| İkili | ~%27 (her biri) | %40 – 47 |
| Tek (bel üstü) | ~%58 | ~%42 |
| Yakın | ~%88 | ~%40 |

Altyazı %76'da duruyor: yüzler her zaman onun üstünde, altyazı göğsün üstüne düşüyor.

## İki rol

| | Akıl hocası | Öğrenci |
|---|---|---|
| Göz | hep yarı kapalı kapaklar; iris küçük, sakin | iri yuvarlak, parlak göz bebekleri (iki ışık noktası) |
| Varsayılan ifade | bilge, hafif gülümseyen, biraz alaycı | endişeli / meraklı |
| İfade değişimi | az: gülümseme, gözleri kapatıp açma | her satırda: şaşkınlık, üzüntü, utanç, kızgınlık |
| Kıyafet | koyu takım elbise, kravat | yelek / kazak, gömlek |
| Ses | ≈ 88 Hz | ≈ 245 Hz |
| Ekranda | %35 | %30 |
| Yer (ikili) | solda | sağda |

## Hareket

- Konuşanın ağzı sesle açılıp kapanıyor; şekiller iki kare duruyor (ağız bölgesinde kare farkları çift çift geliyor).
- Göz kırpma; ifade değişimleri kelimede.
- Arada bir el hareketi: el kaldırma, işaret etme, başını kaşıma, telefonu tutma, bardağı tutma.
- Boşta hareket yok: nefes, sallanma, salınım yok. Sahnedeki tek sürekli hareket kameranın itmesi.

## Bizim karakterlerimiz (`engine/src/chars.js`)

| | Baykuş (`baykus`) | Kirpi (`kirpi`) |
|---|---|---|
| Rol | akıl hocası | öğrenci |
| Kafa | geniş, kulak tüyleri, iki açık yüz diski | krem yuvarlak yüz, arkada diken tacı, küçük kulaklar |
| Göz | iri kehribar diskler, yarı kapalı kapak (`bilge`) | beyaz göz, iri bebek, iki ışık noktası, kirpik |
| Ağız | gaga; konuşurken alt gaga iniyor | küçük ağız; konuşurken dil görünüyor; allık |
| Kıyafet | zeytin tüvit ceket, yelek, gömlek, hardal papyon, mendil | hardal çizgili örgü kazak, bisiklet yaka |
| İfadeler | `notr` `bilge` `gulumse` `uzgun` `endiseli` `saskin` `dusunceli` `kizgin` `utangac` | aynı |
| Pozlar | `yan` `masa` `el` `cene` `telefon` | aynı |

Hepsi tek sayfada: `cd engine && node faces.mjs` → `out/faces.png`.
Yeni tür eklemek: `SPECIES` içine renkler, `body()` içine kafa ve gövde çizimi; `eyes()` göz yerlerini kapanış kartına veriyor.

# Kurgu ve kamera

Yöntem: her kare 180 × 320'ye küçültüldü. Kesme: kare farkı yerel ortancanın 4 katını ve 12'yi aşıyor, renk histogramı da sıçrıyor
(Bhattacharyya > 0,12); 8 kareden kısa aralıkla gelen sıçramalar (şimşek, ışık çakması) kesme sayılmadı. Bütün kesmeler kare şeridinde
gözle doğrulandı. Planın içindeki kamera hareketi: planın ilk ve son karesi (ayrıca dörtte bir, yarı, dörtte üç) ECC ile hizalandı;
tarama çizgileri sayılmasın diye kareler önce bulanıklaştırıldı, altyazı bandı maskelendi. Plan türleri 115 planın orta karesinden elle etiketlendi.
Ham sayılar: [`veri/kurgu_referans.json`](veri/kurgu_referans.json), [`veri/olc_referans.json`](veri/olc_referans.json).

## Planlar

| Video | Plan | Plan süresi ortanca (sn) | Kesme / dk | İtme ortanca (%) | İçeri iten plan | Büyük hareket |
|---|---|---|---|---|---|---|
| r1 | 20 | 3,83 | 13,2 | 3,9 | %95 | 2 |
| r2 | 15 | 5,23 | 13,0 | 4,4 | %100 | 1 |
| r3 | 21 | 3,70 | 14,7 | 3,3 | %81 | 1 |
| r4 | 24 | 3,40 | 15,9 | 3,2 | %79 | 1 |
| r5 | 17 | 3,87 | 12,9 | 4,7 | %82 | 6 |
| r6 | 18 | 4,12 | 13,3 | 3,7 | %94 | 1 |

- Bütün planlarda süre: %10'luk dilim 2,05 sn, %25'lik 2,67, ortanca 3,77, %75'lik 5,33, %90'lık 6,65, en uzun 9,5 sn.
- **Yalnızca sert kesme.** Kararma, çapraz geçiş, kaydırma yok. Tek "geçiş" videonun sonundaki kararma.
- Kesme, konuşmacı değişirken; yeni satır başlamadan hemen önce.

## Kamera

| Ölçü | Değer |
|---|---|
| İçeri iten planlar (> %1) | %88 |
| Geri çeken (< −%1) | %4 |
| Duran (±%1) | %8 |
| Plan başına toplam itme | %10'luk 0,8, %25'lik 2,5, ortanca 3,6, %75'lik 5,1, %90'lık 9,5 |
| Kare başına | ortanca %0,035 (yumurta kafa stilinin sekizde biri) |
| Eğri | hareketin %12'si ilk çeyrekte, %54'ü yarıda, %93'ü dörtte üçte: yumuşak başlayıp yumuşak biten (kübik) |
| Yana kayma | ortanca 0,08 px/kare; %90'lık dilim 0,42 px/kare (1080 genişlikte): pan yok |
| Büyük hareket | 115 planın 12'si (%10): %15 – 38 itme (pencereye, nesneye) ya da %20 – 31 geri çekilme (mekânı açma) |

Kural: her plan merkeze doğru yavaşça iter (`push` varsayılanı 0,05; ilk ve son karede ölçülen ~%3,8). Her on planda bir, hikâyenin
ağır cümlesinde büyük bir hareket (`push: .15 – .35`).

## Plan türleri (115 plan, elle)

| Tür | Pay | Not |
|---|---|---|
| Akıl hocası tek (bel üstü / yakın) | %35 | gözler yüksekliğin ~%40 – 42'sinde |
| Öğrenci tek | %30 | aynı |
| Nesne / ara plan | %24 | telefon, çay bardağı, fincanlar, fotoğraf, pencere, araba, fanus; çoğu sığ alan derinliği ve bokeh ile |
| İkili | %11 | ikisi yan yana, önlerinde masa ya da korkuluk; akıl hocası solda (6/6) |

- **İlk plan**: ikili (r1, r2, r3), öğrencinin yakını (r4, r5), nesne (r6: kilit ekranında bir mesaj).
- **Son plan**: akıl hocası (6/6). Işıklar onun üstünde kararıyor.
- **Omuz üstü**: tek planların yaklaşık üçte birinde öbür karakterin bulanık omzu / kulağı alt köşede.
- **Dinleyen planı**: akıl hocasının uzun monoloğunda, öğrencinin dinleyen yüzü ve nesne planları araya giriyor.

## Mekân ve ışık

- Video başına tek mekân, gece (6/6): balkon / kafe önü, yağmurlu otobüs durağı, fotoğraf stüdyosu, büfeli oturma odası, fanuslu salon, karlı sokak.
- Işık her zaman görünen sıcak kaynaklardan: sarkıt lamba, ayaklı lamba, aydınlık pencereler, sokak lambası huzmesi.
- Hava: yağmur (r2, r5), kar (r6), çaydan buhar (r4). r2'de şimşek: iki hızlı çakma (0,07 sn + 0,1 sn arayla), sonra yavaş sönme.

## Kapanış

| Ölçü | Değer |
|---|---|
| Kararmanın başı | imza cümlesinin ilk kelimesi |
| Karanlığa iniş | ~4 sn |
| Gözlerin parlaması | kararmanın ~1,5. saniyesinden itibaren |
| Kanal adının çıkışı | kararmanın ~4,5. saniyesi, ~0,5 sn'de beliriyor |
| Kanal adı + gözler | ~3,5 sn bekliyor |
| Son kararma | ~0,5 sn; sonda ~1 sn siyah |
| Kararmadan sona | 7,3 – 8,3 sn (7,85) |
| Kamera | kapanış boyunca ~%7 geri çekiliyor |

## Örnek videoda (Soğuk Çay)

Bkz. [README.md](README.md) sonundaki tablo.

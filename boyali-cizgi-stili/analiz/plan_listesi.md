# Referansın plan plan dökümü

Kesmeler kontakt sayfalarında kare kare doğrulandı (`olc.py --plan` ile ölçüldü). Değerler: süre (sn), toplam itme/çekme (%), sarsıntı (px), özne hareketi (kamera telafili kare farkı, 0-255), ortalama L, RMS kontrast, Lab kroma, alan derinliği.

| # | Başlangıç | Süre | Ölçek / açı | Ne oluyor (genel) | Giriş | İtme | Sarsıntı | Özne | L | Kontrast | Kroma | DoF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0,00 | 2,64 | Alttan geniş açı, iki flu ön plan nesnesi arasından, güneş arkada | Karakter arzuladığı şeye tepeden bakar | — | −0,3 | 0,9 | 4,0 | 47,5 | 27,2 | 23,1 | 1,53 |
| 2 | 2,64 | 0,88 | Yakın, hafif alttan | Araç gösterilir: bıçak parlaması, sinsi sırıtma | kesme | −0,7 | 0,7 | 2,5 | 34,1 | 26,6 | 19,1 | 1,17 |
| 3 | 3,52 | 3,52 | Yakın (yüz + eller + nesne) | Küçük zafer: ödülü alır; ifade 4 kez değişir | kesme | **+8,0** | 0,2 | 2,8 | 40,0 | 27,0 | 21,9 | 0,86 |
| 4 | 7,04 | 2,00 | Geniş, yan profil | Daha büyüğünü ister, ip ile çekiştirir | kesme | +0,9 | **2,5** | 3,4 | 61,5 | 15,4 | 26,0 | 0,66 |
| 5 | 9,04 | 1,60 | Geniş | Ters köşe: nesne canlanır, ağzını açar | **smear (1)** | −3,4 | 0,5 | 4,7 | 56,2 | 19,6 | 25,3 | 0,77 |
| 6 | 10,64 | 1,76 | Geniş, merkezde | Yutulmuş; yalnızca kollar dışarıda, sabit kamera | **smear (1)** | 0 | 0,2 | 0,6 | 63,5 | 12,5 | 26,6 | 1,53 |
| 7 | 12,40 | 2,48 | Orta | İçeride çırpınma; içeri çekilip çıkma (ifade ritmi) | kesme | **−11,7** | 1,1 | 2,4 | 61,8 | 15,5 | 27,9 | 1,23 |
| 8 | 14,88 | 4,08 | Geniş | Tükürülür, yere oturur; **sessiz duraklama** | **smear (5)** | −1,9 | 0,3 | 1,3 | 62,1 | 15,7 | 31,2 | 1,23 |
| 9 | 18,96 | 2,00 | Alçak orta, güneş kadrajda | İkinci deneme: yerdeki ödüle uzanır, sırıtır | kesme | −1,7 | 0,2 | 1,8 | 57,6 | 21,8 | 23,5 | 0,94 |
| 10 | 20,96 | 2,80 | Yakın-orta | Ters köşe 2: küçük yaratık kafaya sıçrar, çırpınma | **smear (1)** | −6,8 | 1,2 | 3,1 | 63,5 | 17,6 | 21,3 | 2,10 |
| 11 | 23,76 | 2,08 | Orta, hafif yatık | Panik dansı (giysinin içinde) | kesme | −0,1 | 0,8 | 4,5 | 60,3 | 19,8 | 21,3 | 1,20 |
| 12 | 25,84 | 3,96 | Yakın-orta, sabit | Final: boynunda sarılmış yaratık, bön ifade dizisi | kesme | +0,2 | 0,8 | 3,9 | 61,1 | 19,5 | 22,6 | 1,37 |

## Gözlemler
- **Yakın planlar koyu ve kontrastlı** (L 34-48, RMS 27), **geniş planlar açık ve yumuşak** (L 56-64, RMS 12-16). Bunun sebebi koyu tenli karakterin kadrajı doldurması. Grade aynı kalır, değişen kompozisyondur.
- Kroma en yüksek değerine geniş çöl planlarında çıkar (kum + gök + meyve). Yakın planlarda karakterin doymamış teni yüzünden düşer.
- Plan 7'deki −11,7 %'lik çekme hikâyenin "bedel" anına denk gelir. Plan 3'teki +8 %'lik itme "kibir" anına.
- Plan 6 ve 8: kamera ve karakter durur. Komik etkiyi hareketsizlik yaratır.
- Sesin en yüksek olduğu yer plan 5 (ağız açılması). Sessiz geçen yer plan 8'in ikinci yarısı.

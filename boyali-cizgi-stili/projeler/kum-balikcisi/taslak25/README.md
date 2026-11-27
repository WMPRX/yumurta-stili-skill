# Kum Balıkçısı: 2.5D taslak

Aynı senaryo, aynı 12 plan ve aynı ses; ama düz 2B yerine tek bir tutarlı 3B dünyada, gerçek kamerayla. Karakterler ve nesneler hâlâ 2B çizilmiş kartlar (`../taslak/boya.py`, `../taslak/tikir.py`), ama:

| Özellik | 2B taslak | 2.5D taslak |
|---|---|---|
| Zemin | Ekrana çizilmiş düz gradyan | Piksel başına ışın-düzlem kesişimi: perspektifli, dünyaya sabit boyalı kum dokusu (mip seviyeli), büyük ölçekli renk lekeleri, analitik kum gölü ve halkalar, uzaklık pusu (uzak ova kendiliğinden teal-yeşile döner) |
| Kamera | Sabit; itme/çekme kurguda dijital zoom | Gerçek dolly/truck/takip: plan 1, 3, 4, 5, 6, 7, 10'da kamera dünyada hareket eder, katmanlar paralaksla kayar |
| Nesne yerleşimi | Ekran koordinatı | Dünya koordinatı (metre); ölçek derinlikten gelir, ot ve çiçekler derinliğe göre küçülür |
| Işık | Dolgu başına doğrusal gradyan | Hacimli ışık: her parçanın kimlik tamponundan uzaklık dönüşümü → şişirilmiş yükseklik → normal; güneş + gök dolgusu + kum yansıması + ters ışıkta kenar ışığı |
| Gölge | Ekranda kaydırılmış siluet | Kart alfası güneş yönünde zemine homografiyle izdüşer (perspektife uygun) |
| Alan derinliği | Katman başına sabit | Odak uzaklığı + diyafram: zemin piksel başına, kartlar nesne başına bulanıklaşır |
| Güneş | Ekrana çizilmiş disk | Güneş yönünden izdüşen disk ve hale; 1. ve 9. planda ışık yönü diskle aynı (ters ışık) |

## Dünya
- **Mekân 1 (plan 1-7):** kum gölü (0, 12.5) yarıçap 4×2.6 m; arkasında gömülü balina (-2, 18.5), 9 m; kıyıda Tıkır (4.6, 13), kova, tabure.
- **Mekân 2 (plan 8-12):** sürüklendiği düzlük; balina (-1.5, 24)'te yeniden gömülür ve finalde arkada gözünü açar.
- Güneş yönü (0.42, 0.72, 0.55): sağ-arka-yukarı; gölgeler kameraya ve sola düşer.

## Dosyalar
| Dosya | Ne |
|---|---|
| `derin.py` | 2.5D motor: kamera, gök, zemin, hacimli ışık, gölge homografisi, DoF, uzak kayalıklar |
| `sahne25.py` | 12 plan (kamera anahtarları, dünya konumları, pozlar ve ifadeler) |
| `render25.py` | `python render25.py kare --olcek 0.5 --plan 3 --t 1.0` önizleme; `python render25.py hepsi` → `../klipler25/` |
| `kurgu25.json` | Birleştirme: smear geçişleri ve darbe sarsıntıları (itme/çekme yok, kamera gerçek) |

## Baştan üretmek
```bash
pip install pycairo numpy opencv-python-headless scipy pillow
cd projeler/kum-balikcisi/taslak25
python render25.py hepsi                   # 4 çekirdek, ~20 dk
python ../taslak/ses.py                    # ses 2B taslakla aynı (aynı kesme saatleri)
python ../../../tools/kurgu.py kurgu25.json ../kurgu25.mp4
python ../../../tools/renk_esle.py ../kurgu25.mp4 ../kum-balikcisi_25d.mp4
python ../../../tools/olc.py ../kum-balikcisi_25d.mp4 ../olcum_25d.json --plan "2.6,3.52,7.04,9.04,10.64,12.44,14.96,18.96,20.96,23.76,25.76"
python ../../../tools/karsilastir.py ../olcum_25d.json
```

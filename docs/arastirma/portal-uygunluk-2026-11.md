# Portal uygunluk listesi: reklam kancası olmayan 13 oyun (2026-11-18, G-029)

Kapsam: midgame reklam yeri ve ödüllü kanca **olmayan** 13 oyun. Reklam yeri birleşmiş 8 oyun (Peri Golf, Dolmuş, Kale
Savunması, Çay Ocağı, Pamukkale, Çarşı Kaçışı, Kırkpınar, Simit Fırını) burada yok.
Hedef portal: CrazyGames 18 Kas'ta iptal edildi (kullanıcı kararı); sıradaki aday Poki / Playgama (G-033). Paketleme
`arena-core/tools/portal.mjs` ile: Google Fonts pakete gömülür, three.js ve eklentileri yerel kopyalanır, sayaç çıkar,
dış bağlantılar engellenir (#9). Aşağıdaki "dış bağlantı" sütunu bu yüzden engel değil, yalnız bilgi.

Ölçüm: paket boyutu `du` (git, docs, tools, prompts hariç); döngü ve molalar README'den; hepsinde dokunmatik var.

## Sıralama

| Sıra | Oyun | Boyut | Döngü (mola noktası) | Midgame yeri | Ödüllü kanca adayı | Uygunluk |
|---|---|---|---|---|---|---|
| 1 | Martı | 1,3 MB | Sonsuz koşu, ölünce biter | Koşu sonu (ölüm ekranı) | **Devam et**: 1 tüy geri, aynı yerden sür | Yüksek: kısa oturum, portalın en çok oynanan türü |
| 2 | Çini Ustası | 1,5 MB | 30 bölüm, 3 bölüm grubu + günlük tahta | Bölüm sonu (yıldız ekranı) | **İpucu** (bölüm başı 3 ipucu bitince +1) | Yüksek: bulmaca, net mola, ipucu hazır mekanik |
| 3 | Fay Hattı | 0,5 MB | Günlük harita + sonsuz bölümler | Sonsuz modda bölüm sonu | **Geri al / deprem önizleme** | Yüksek: en küçük paket, 2D, dış istek yok |
| 4 | Karagöz | 0,3 MB | 24 sahne | Sahne sonu | **İpucu** (doğru figür yerini göster) | Yüksek |
| 5 | Topkapı Gecesi | 0,4 MB | 9 gece görevi | Görev sonu | **Yakalanınca devam** (son kontrol noktası) | Orta-yüksek: görev sayısı az, oturum uzun |
| 6 | Mehter | 2,0 MB | Şarkı şarkı ritim | Şarkı sonu | **Çarpanı koru** (kombo kırılınca bir kez) | Orta: ses saatine bağlı; reklam sonrası ses bağlamı yeniden başlamalı |
| 7 | Kapadokya Balonu | 0,6 MB | 12 uçuş, 5 hedef türü | Uçuş sonu | **Rüzgâr tablosunu göster** (uçuş başında) | Orta |
| 8 | Boğaz Vapuru | 0,4 MB | 8 vardiya + sonsuz | Vardiya sonu | **Gecikme cezasını sil** (vardiya sonu) | Orta |
| 9 | Mimar Sinan | 0,4 MB | 15 eser, 3 dönem, deprem testi | Eser sonu / deprem testi sonrası | **Testten önce bir kez güçlendir** | Orta |
| 10 | Hamsi | 0,4 MB | 30 günlük sezon, gün sonu özeti | Gün sonu (limanda uyku) | **Avı taze sat** (gün sonu satış x1,5) | Orta-düşük: sezon uzun, ekonomi dengesi bozulabilir |
| 11 | Kervan | 1,6 MB | Günler, 150-210 günlük koşu | Mevsim değişimi | **Haydut saldırısını atlat** | Düşük-orta: çok uzun oturum |
| 12 | Lale Bahçesi | 0,3 MB | 30 günlük mevsim + bayram | Mevsim sonu bayramı | **Tohumu hızlandır** | Düşük-orta: yavaş tempo |
| 13 | Ebru | 0,7 MB | Serbest yaratım / desen bulmacası | Kâğıt basıldıktan sonra | Yok (yaratım oyunu; ödül zorlaması kötü deneyim) | Düşük: portal yerine vitrin oyunu |

## Notlar

- **Kural:** reklam yalnız doğal molada; oynanış ortasında kesinti yok. Ödüllü kanca isteğe bağlı, reddedince oyun aynen sürer.
  Portal SDK'sı yoksa kanca senkron devam eder (8 oyundaki "portal yoksa eylem senkron" deseni, örn. kale-savunmasi #22).
- **Toplu değişiklik kuralı:** kancaları 13 depoya yaymak toplu değişikliktir: önce tek oyunda pilot (öneri: Martı, en yüksek
  potansiyel ve en basit mola), sonra `schema/degisim.py` kapısı, sonra kullanıcı onayı.
- **Ölçü:** pilotta `?auto` botuyla ölüm/bölüm sonu sayısı ve reklam çağrısı sayısı eşleşmeli; reklam sonrası ses ve duraklatma
  geri gelmeli (Mehter için ayrıca ses saati kayması ölçülmeli).
- **Paket boyutu:** hepsi 2,1 MB altında; portal sınırları (Poki ilk yük ~5-8 MB önerisi, görülmedi, doğrulanmadı) için sorun beklenmiyor.

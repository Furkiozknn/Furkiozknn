# Proje panosu

<!-- yonetim/pano.py uretti; elle duzenleme: kaynak yonetim/gorevler.json -->

Güncellendi: 2026-11-17 19:40 UTC

| Devam Ediyor | Test Ediliyor | Bekliyor | Engellendi | Tamamlandı |
|---|---|---|---|---|
| 3 | 3 | 9 | 3 | 20 |

**Sıradaki iş:** G-038 (P2) Performans ölçümünü haftalık yenile (Buffer -> performans.json)

## Kalıcı kullanıcı onayları

- 2026-11-17: Rutin kod, refaktör, test, hata düzeltme, doküman, sürüm işleri onaysız; ortak altyapı değişikliği pilot + toplu değişiklik kapısından (schema/degisim.py) geçince kontrollü yayılır. Hesap, ödeme, geri alınamaz silme ve dış dünyada önemli sonuç doğuran işler Engellendi olarak kaydedilir.

## Aktif işler

| Id | Öncelik | Durum | İş | Alan | Bağımlı | Not |
|---|---|---|---|---|---|---|
| G-020 | P0 | Devam Ediyor | Video kuyruğu: Kale Savunması, Hamsi | video |  | toplu.sh; 2 sa arka plan sınırında yeniden başlatılır |
| G-025 | P1 | Devam Ediyor | Instagram takvimi: Dolmuş reels, Ebru reels v3, sonra Çay Ocağı, Peri Golf, Mehter, Kırkpınar, Çarşı Kaçışı ... günde 2 oyun | sosyal |  | Buffer ücretsiz plan en çok 10 zamanlanmış gönderi |
| G-029 | P2 | Devam Ediyor | Portal sırası: kalan oyunlar için uygunluk/potansiyel listesi, midgame + ödüllü kancalar (Dolmuş, Kale Savunması ...) | portal | G-024 | reklam yeri birleşti: Peri Golf, Dolmuş, Kale Savunması, Çay Ocağı, Pamukkale, Çarşı Kaçışı (#23); Kırkpınar #23 ve Simit Fırını #22 CI/birleştirme döngüsünde. Hepsi tarayıcı testli (site taban ile aynı hız, paket adEnd sonrası) |
| G-039 | P0 | Test Ediliyor | Profil deposunda 26 Dependabot uyarısı: politika fikstürlerindeki vite@7.1.0 | güvenlik |  | Furkiozknn #48 birleşti (72a47f7): vite@7.1.0 fikstürden çıktı, 58 test OK. Uyarıların kapandığı Security sekmesinden görülmeli (alerts API 403) |
| G-023 | P1 | Test Ediliyor | video-studio #15 (dalış/sis/başlık motoru) birleştir | video | G-021 | yeniden çekimler kare kare temiz çıkınca |
| G-037 | P1 | Test Ediliyor | Reels açılışı: 0. karede hareketli oynanış + tek iddia satırı (kurallar v2.1); ortalama izleme 2.5-3.5 sn | video |  | uygulandı (video-studio sahne-dalis-acikligi); yeni sırayla ilk yayınlardan sonra performans.json ile önce/sonra ölçülecek |
| G-021 | P0 | Bekliyor (hazır değil) | Yeni motorla yeniden çekim: Dolmuş, Çay Ocağı, Ebru, Pamukkale, Mimar Sinan, Kapadokya Balonu, Kervan, Simit Fırını | video | G-020 |  |
| G-022 | P1 | Bekliyor (hazır değil) | Fay Hattı hikâye + reels (hiç çekilmedi) | video | G-021 |  |
| G-026 | P1 | Bekliyor (hazır değil) | Peri Golf portal kapakları (vitrin) | portal | G-020 |  |
| G-044 | P1 | Bekliyor (hazır değil) | Portal paketleri: reklam yeri hazır 8 oyunun CrazyGames paketlerini indirilebilir yayımla | portal | G-029 | tools/portal.mjs; kapaklar G-026 (vitrin) ile |
| G-038 | P2 | Bekliyor | Performans ölçümünü haftalık yenile (Buffer -> performans.json) | sosyal |  | G-037 sonrası önce/sonra karşılaştırması |
| G-040 | P2 | Bekliyor (hazır değil) | Oyun bölümünde hareket ölçümü: durağan oynanış çekimlerini yakala (ör. Peri Golf ilk 12 sn) | video | G-021 |  |
| G-032 | P3 | Bekliyor | Meta-ilerleme (TOP 10 #6): yıldız, harita, kozmetik açılımlar | oyunlar | G-024 |  |
| G-033 | P3 | Bekliyor (hazır değil) | Poki / Playgama paketleri (Playgama bridge dosyası, Poki pitch) | portal | G-027 |  |
| G-034 | P3 | Bekliyor | 4 oyunda dil yedeği 'tr' kenar durumu (boş/geçersiz dil) | oyunlar |  |  |

## Engellenen işler

| Id | Öncelik | İş | Gerçek neden | Gereken |
|---|---|---|---|---|
| G-027 | P1 | Peri Golf'ü CrazyGames'e gönder | CrazyGames geliştirici hesabına erişim yok; yükleme ve gönderim hesap sahibinin işlemi | Kullanıcı developer.crazygames.com hesabıyla paketi (peri-golf-crazygames.zip, 0,77 MB) ve kapakları yükler |
| G-035 | P3 | Instagram PDF reel analizi | Reel içeriği ücretli PDF'e bağlı; ücretsiz kısım için açıklama metni/ekran görüntüsü yok | Kullanıcı reel açıklamasını ya da ekran görüntülerini paylaşır |
| G-036 | P3 | Profilde 4 depoyu sabitle | GitHub sabitleme API'si bu oturumdan kapalı (yalnız profil sahibi arayüzden) | Kullanıcı github.com/Furkiozknn > Customize your pins |

## Portföy

| Oyun | Kit | Video (TR hikâye+reels) | Instagram | Portal |
|---|---|---|---|---|
| bogaz-vapuru | 1.3.2 | hazır | zamanlandı 20 Kas 19:00/20:00 | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| carsi-kacisi | 1.3.2 | hazır | sırada | reklam yeri var (midgame); kapak + paket bekliyor |
| cay-ocagi | 1.3.2 | yeniden çekim (tarama, minyatür) | sırada | reklam yeri var (midgame); kapak + paket bekliyor |
| cini-ustasi | 1.3.2 | hazır | zamanlandı 18 Kas 19:00/20:00 | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| dolmus | 1.3.2 | yeniden çekim (tarama) | hikâye 19 Kas 19:00; reels bekliyor | reklam yeri var (midgame); kapak + paket bekliyor |
| ebru | 1.3.2 | yeniden çekim (dalış sonu) | zamanlandı 19 Kas 12:00/13:00 (reels eski sürüm) | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| fay-hatti | 1.3.2 | yok | - | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| hamsi | 1.3.2 | kuyrukta | sırada | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| kale-savunmasi | 1.3.2 | çekiliyor | sırada | reklam yeri var (midgame); kapak + paket bekliyor |
| kapadokya-balonu | 1.3.2 | yeniden çekim | sırada | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| karagoz | 1.3.2 | hazır | yayımlandı 17 Kas | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| kervan | 1.3.2 | yeniden çekim (gündüz) | sırada | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| kirkpinar | 1.3.2 | hazır | sırada | reklam yeri PR'da (CI) |
| lale-bahcesi | 1.3.2 | hazır | yayımlandı 16 Kas | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| marti | 1.3.2 | hazır (reels v2) | yayımlandı 17 Kas | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| mehter | 1.3.2 | hazır | sırada | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| mimar-sinan | 1.3.2 | yeniden çekim (sis, dalış) | sırada | kit 1.3.1 hazır; oyun içi reklam kancaları yok |
| pamukkale | 1.3.2 | yeniden çekim (sis) | sırada | reklam yeri var (midgame); kapak + paket bekliyor |
| peri-golf | 1.3.2 | hazır | sırada | hazır: CrazyGames paketi 0,77 MB; gönderim hesap bekliyor |
| simit-firini | 1.3.2 | yeniden çekim (gündüz) | sırada | reklam yeri PR'da (CI) |
| topkapi-gecesi | 1.3.2 | hazır | zamanlandı 18 Kas 12:00/13:00 | kit 1.3.1 hazır; oyun içi reklam kancaları yok |

## Geçmiş (tamamlanan, en yeni önce)

- **G-043** 2026-11-17 · Reklam yeri: portal yoksa eylem senkron (Peri Golf, Dolmuş, Kale Savunması, Çay Ocağı)
  - peri-golf #21, dolmus #27, kale-savunmasi #22, cay-ocagi #23: doğrulamalı birleşti (4 kontrol + gate RESULT OK)
  - Tarayıcı testleri (site + paket) dördünde TAMAM
- **G-042** 2026-11-17 · inject.mjs için test yok (eski inject.py'nin 7 testi taşınmadı)
  - arena-core #8: tests/inject.test.mjs (yerleşim, --kit-only/--core-only/--check, CRLF, eksik blok); CI ok
  - Mutasyon: CRLF koruması ya da çekirdek yerleşimi bozulunca kırılıyor
- **G-041** 2026-11-17 · arena-kit v1.3.2: reklam 'adstart'/'adend' yayar, 'pause' değil (17 oyun pause'da kilitleniyordu)
  - arena-core #5 (d1c5cd1); pilot kale-savunmasi #21 (gate RESULT OK, tarayıcı: reklamdan sonra dalga 2 başlıyor)
  - degisim.py 20/20 PASS; 20 PR doğrulamalı birleşti (bütün kontroller success + gate RESULT OK)
- **G-031** 2026-11-17 · arena-core testleri CI'da koşsun (şu an yalnız yerelde)
  - arena-core #6: test.yml her push/PR; her dosya ": ok" basmalı
  - arena-core #7: node:test adımı taban 18
- **G-030** 2026-11-17 · furkiozknn/arena-kit (eski v1.1.0 kopya) ile arena-core tek kaynakta birleşsin
  - arena-core #7: 18 kit testi taşındı, v1.3.2 üstünde 18/18 (CI taban 18)
  - furkiozknn/arena-kit (v1.1.0 kopya) ve CI adımı kaldırıldı; tek kaynak arena-core
- **G-028** 2026-11-17 · Yayın performansını kaydet (Buffer ölçümleri) ve içeriğe geri besle
  - video-studio (özel depo) kutuphane/uretim/performans.json + oyun-araclari/performans/performans.py: 20 gönderi
  - Ortalama: Instagram reels ~290 izlenme, izleme süresi 2.5-3.5 sn; hikâye ~40 izlenme; X ~0 (ayrıntı özel depoda)
  - Bulgu -> G-037
- **G-024** 2026-11-17 · arena-kit v1.3.1'i kalan 20 oyuna yay
  - 20 PR doğrulamalı birleşti (her biri bütün kontroller success + gate RESULT OK): bogaz-vapuru #20, carsi-kacisi #21, cay-ocagi #20, cini-ustasi #18, dolmus #24, ebru #19, fay-hatti #10, hamsi #17, kale-savunmasi #20, kapadokya-balonu #20, karagoz #19, kervan #21, kirkpinar #21, lale-bahcesi #21, marti #19, mehter #21, mimar-sinan #23, pamukkale #24, simit-firini #20, topkapi-gecesi #19
  - Pilot peri-golf #18; degisim.py 20/20 PASS
- **G-013** 2026-11-17 · İngilizce varsayılan + Türkçe otomatik algılama (TOP 10 #4)
  - 21 oyunda navigator.language kontrolü mevcut (tarama 17 Kas)
- **G-012** 2026-11-17 · Dalış kamerası: kapalı/düz kadraj ölçümü, kahraman odağı, sis kaydırma, yörünge kontrolü
  - video-studio dal sahne-dalis-acikligi (taslak #15)
  - Dolmuş 1/0/0/0/5 -> 13-18 %; Martı v2 yayımlandı
- **G-011** 2026-11-17 · Instagram hikâye kodlaması (yuv420p, ~5 Mbps, AAC 128k, tepe <= -1 dBTP)
  - social-videos ef165c2
  - Martı hikâyesi medya hatasından sonra yeni kodlamayla gönderildi (17 Kas 17:19 UTC)
- **G-010** 2026-11-17 · Peri Golf: suya düşünce ödüllü reklamla cezayı geri al
  - peri-golf #19 (875de69): smoke 3 tarayıcı, gate RESULT OK
  - tarayıcı: vuruş 5 -> 4; mutasyon 'strokes 5 -> 5' ile kırılıyor
  - Pages dağıtımı 875de69 success
- **G-009** 2026-11-17 · Peri Golf portal pilotu: kit 1.3.1 + delikler arası reklam
  - peri-golf #18 (9863c52): smoke 3 tarayıcı, gate RESULT OK
  - tarayıcı: reklam bitmeden ilerlemiyor; mutasyon testi kırıyor
- **G-008** 2026-11-17 · Portal paketleyici tools/portal.mjs + kit v1.3.1 (portalda çapraz tanıtım yok, dış bağlantılar gizli)
  - arena-core #3, #4
  - node tests/portal.test.mjs ok; tarayıcı: sitede dış bağlantı 2, pakette 0
- **G-007** 2026-11-17 · arena-kit v1.3: Arena.portal adaptörü (CrazyGames v3, Poki, Playgama)
  - arena-core #2
  - node tests/kit-portal.test.mjs ok; mutasyon: aralık/ses askısı kaldırılınca kırılıyor
- **G-006** 2026-11-17 · İlk oturum: Peri Golf, Kale Savunması, Pamukkale anında başlama
  - peri-golf #17
  - kale-savunmasi #19
  - pamukkale #23 (81ff565), gate RESULT OK
- **G-005** 2026-11-17 · Yazı denetimi: 21 oyunda taşan/kesik/üst üste binen yazılar
  - oyun PR'ları, düzen kapısı 390x844 / 360x740 / 412x915
- **G-004** 2026-11-17 · GitHub profili: öne çıkan dört oyun
  - furkiozknn #46
- **G-003** 2026-11-17 · arena-kit v1.2.0 21 oyunda (günlük v2, seri dondurma, oynama süresi ölçümleri)
  - 13 PR; her biri 4 kontrol + gate RESULT OK ile birleşti (kit-birlestir2.sh)
- **G-002** 2026-11-17 · Vitrin: portal kapakları ve önizleme videosu aracı
  - video-studio #12 (oyun-araclari/vitrin)
- **G-001** 2026-11-17 · Sahne Motoru: oyunun motorundan bot oynarken çekim, katmanlar, ses, hikâye 20 sn / reels 40 sn
  - video-studio #11 (sahne-toplu), #13 (kaldığı yerden devam), #14
  - Lale Bahçesi örnek videolar 16 Kas

# Proje panosu

<!-- yonetim/pano.py uretti; elle duzenleme: kaynak yonetim/gorevler.json -->

Güncellendi: 2026-11-18 03:45 UTC

| Devam Ediyor | Test Ediliyor | Bekliyor | Engellendi | Tamamlandı |
|---|---|---|---|---|
| 3 | 2 | 6 | 1 | 29 |

**Sıradaki iş:** G-045 (P1) Sahne motoru: rayAc kör noktaları (hareketli odak ve dokulu düz yüzey)

## Kalıcı kullanıcı onayları

- 2026-11-17: Rutin kod, refaktör, test, hata düzeltme, doküman, sürüm işleri onaysız; ortak altyapı değişikliği pilot + toplu değişiklik kapısından (schema/degisim.py) geçince kontrollü yayılır. Hesap, ödeme, geri alınamaz silme ve dış dünyada önemli sonuç doğuran işler Engellendi olarak kaydedilir.

## Aktif işler

| Id | Öncelik | Durum | İş | Alan | Bağımlı | Not |
|---|---|---|---|---|---|---|
| G-025 | P1 | Devam Ediyor | Instagram takvimi: Dolmuş reels, Ebru reels v3, sonra Çay Ocağı, Peri Golf, Mehter, Kırkpınar, Çarşı Kaçışı ... günde 2 oyun | sosyal |  | Buffer 10/10 dolu. 18 Kas 10:10Z hatırlatması yer açıldıkça sırayla zamanlar: Hamsi, Kale, Çay, Mimar Sinan, Pamukkale, Simit, Kapadokya, Kervan, Kırkpınar (+ Mehter/Çarşı yeni reels, daha önce gönderilmediyse) |
| G-029 | P2 | Devam Ediyor | Portal sırası: kalan oyunlar için uygunluk/potansiyel listesi, midgame + ödüllü kancalar (Dolmuş, Kale Savunması ...) | portal | G-024 | reklam yeri 8 oyunda birleşti: Peri Golf, Dolmuş, Kale Savunması, Çay Ocağı, Pamukkale, Çarşı Kaçışı, Kırkpınar (#23), Simit Fırını (#22). Sıradaki: kalan 13 oyun için uygunluk listesi |
| G-035 | P3 | Devam Ediyor | Instagram reels büyüme rehberi: ücretli PDF yerine ücretsiz/birincil kaynaklardan | araştırma |  | Kullanıcı 18 Kas: PDF'e bağlı kalma, aynı bilgiyi ücretsiz kaynaklardan derle. Reel içeriğine giriş olmadan erişilemedi; rehber Instagram/Meta resmi kaynakları + veri çalışmalarından, kutuphane'ye yazılacak ve kurallar.md ile karşılaştırılacak. |
| G-039 | P0 | Test Ediliyor | Profil deposunda 26 Dependabot uyarısı: politika fikstürlerindeki vite@7.1.0 | güvenlik |  | Furkiozknn #48 birleşti (72a47f7): vite@7.1.0 fikstürden çıktı, 58 test OK. Uyarıların kapandığı Security sekmesinden görülmeli (alerts API 403) |
| G-037 | P1 | Test Ediliyor | Reels açılışı: 0. karede hareketli oynanış + tek iddia satırı (kurallar v2.1); ortalama izleme 2.5-3.5 sn | video |  | uygulandı (video-studio sahne-dalis-acikligi); yeni sırayla ilk yayınlardan sonra performans.json ile önce/sonra ölçülecek |
| G-045 | P1 | Bekliyor | Sahne motoru: rayAc kör noktaları (hareketli odak ve dokulu düz yüzey) | video |  | rayAc yalnız çekim başındaki odakla ölçüyor (Dolmuş: dolmuş ilerleyince yörünge binalara girdi, ölçüm %18-36 dedi) ve sıvalı duvar dokusunu ayrıntı sayıyor (Ebru: düz hardal duvar %29-44). Öneri: ölçümü kayıt sırasında da yap (her saniye bir kare), ayrıntıyı renk çeşitliliği + büyük ölçekli kenarla ölç; düz kare oranı eşiği aşarsa planı uyar/yeniden dene. Geçici çözüm: dolmus.json odak sahne, ebru.json minyatür yayı (video-studio #15). |
| G-038 | P2 | Bekliyor | Performans ölçümünü haftalık yenile (Buffer -> performans.json) | sosyal |  | G-037 sonrası önce/sonra karşılaştırması |
| G-040 | P2 | Bekliyor | Oyun bölümünde hareket ölçümü: durağan oynanış çekimlerini yakala (ör. Peri Golf ilk 12 sn) | video | G-021 | Örnek: Kervan oynanış bölümü harita görünümü, 11 sn neredeyse durağan (2026-11-18 kare kontrolü) |
| G-032 | P3 | Bekliyor | Meta-ilerleme (TOP 10 #6): yıldız, harita, kozmetik açılımlar | oyunlar | G-024 |  |
| G-033 | P3 | Bekliyor | Poki / Playgama paketleri (Playgama bridge dosyası, Poki pitch) | portal |  | G-027 (CrazyGames) iptal edildi; Poki/Playgama artık ona bağlı değil. |
| G-047 | P3 | Bekliyor | video-studio: 3 CSS transition uyarısı (mascot/Captions, mascot/layouts/Lead, ELightPromo) | video | G-046 | Remotion kareleri ayrı çizer; transition kaldırılınca görüntü değişebilir, bu yüzden kare karşılaştırmasıyla yapılmalı. |

## Engellenen işler

| Id | Öncelik | İş | Gerçek neden | Gereken |
|---|---|---|---|---|
| G-036 | P3 | Profilde 4 depoyu sabitle | GitHub sabitleme API'si bu oturumdan kapalı (yalnız profil sahibi arayüzden) | Kullanıcı github.com/Furkiozknn > Customize your pins (kullanıcı 18 Kas: 'birazdan hallederim') |

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

- **G-046** 2026-11-18 · video-studio main'de eski lint/tip hataları (eslint 10 hata, tsc 47 hata)
  - video-studio #17 birleşti (77daf39)
  - tsc --noEmit exit 0 (önce 47 hata: tsconfig lib es2015 ↔ hedef ES2018 çelişkisi + 4 kullanılmayan bağ)
  - pnpm lint exit 0, 0 hata (önce 10); main üzerinde birleşme sonrası yeniden koşuldu
  - Regresyon: 4 promo şablonu + çini promo + Ep30-v3-en 3 kare dal/main bayt bayt aynı (7/7 md5)
- **G-027** 2026-11-18 · Peri Golf'ü CrazyGames'e gönder
  - Kullanıcı 18 Kas: 'CrazyGames i es geçelim o sorun yaratıyor'
- **G-026** 2026-11-18 · Peri Golf portal kapakları (vitrin)
  - vitrin.py ile Peri Golf kapakları: 1920x1080, 800x1200, 800x800, itch 630x500 (ffprobe ile boyut doğrulandı); göz kontrolü pano.jpg
  - social-videos portal-paketleri 6659bcf (crazygames/2026-11-17/peri-golf-kapaklar/), kullanıcıya teslim edildi
- **G-023** 2026-11-18 · video-studio #15 (dalış/sis/başlık motoru) birleştir
  - video-studio #15 birleşti (39438d4)
  - CI yok; yerel kanıt: pnpm lint ve tsc dal ile main'de birebir aynı (eslint 13 sorun, tsc 47 hata, liste diff boş); src/sahne içinde 0 tsc hatası; cek.mjs node --check ok; o anki 20 oyun json okunuyor (Fay Hattı #16 ile 21. oldu)
- **G-022** 2026-11-18 · Fay Hattı hikâye + reels (hiç çekilmedi)
  - video-studio #16 birleşti (8c49a78): sahne/motor/iki_boyut.py, fay-hatti.json, tekPrompt/ikiBoyut
  - social-videos sahne-videolar c7f774b: 2026-11-18-fay-hatti-{hikaye-ig,reels}-tr.mp4; raw URL'ler 200
  - kontrol.py: reels -14.0 LUFS / -1.1 dBTP, hikâye -14.3 / -1.5; IG hikâye kodlaması -14.7 / -2.9
  - Regresyon: dolmus-reels-tr kare 15 ve 400 dal ile main arasında bayt bayt aynı (md5 35f57f56…)
  - Kare kare QA: fps=1 temas sayfaları (HUD gizli, tahta yazı alanının altında, --kaydir 260)
- **G-021** 2026-11-18 · Yeni motorla yeniden çekim: Dolmuş, Çay Ocağı, Ebru, Pamukkale, Mimar Sinan, Kapadokya Balonu, Kervan, Simit Fırını
  - 8 oyun yeni motorla yeniden çekildi; her hikâye+reels 1 kare/sn tabakada kontrol edildi, kontrol.py -14 LUFS / tepe ≤ -1 dBTP (Pamukkale kaynak hikâye -0.9 -> IG kodlaması -2.3)
  - Kare kontrolünde bulunan ve düzeltilen kusurlar: Dolmuş (şehirde yörünge binadan geçiyordu -> odak sahne), Ebru (kapalı oda minyatürü duvar arkası -> açık yay), Pamukkale (bulut katmanı -> alçak açık yay), Kapadokya (düz zemin, kahraman yok -> oyun kamerası), Kervan (geceye taşma -> hep gündüz kancası), Kırkpınar reels (boş çim dalış -> oyun kamerası, minyatür ön yay)
  - social-videos sahne-videolar: Dolmuş 3cb3513, Çay e2604fb, Ebru 28021c1, Pamukkale 3c7d02c, Mimar Sinan d7b8ee5, Kapadokya db814d0, Kervan 9626767, Simit 80a54a6; reels yeniden kurgu: Mehter 85683da, Çarşı aab25cb, Kırkpınar fdc8741
  - Buffer: Dolmuş ve Ebru gönderileri v3 ile değiştirildi, Dolmuş reels 19 Kas 17:00Z zamanlandı
- **G-044** 2026-11-17 · Portal paketleri: reklam yeri hazır 8 oyunun CrazyGames paketlerini indirilebilir yayımla
  - Tarayıcı çevrimdışı denetimi 7 pakette fonts.googleapis.com isteği buldu -> arena-core #9 (8c67679): Google Fonts pakete katılır, test + 2 mutasyon
  - Yeniden paketleme sonrası çevrimdışı denetim RESULT OK (8): dış istek, eksik dosya, sayfa hatası, yazı tipi hatası, boş ekran yok
  - Mola/ödül tarayıcı testleri 8/8 TAMAM (site ve paket karşılaştırmalı)
  - Zip: unzip -t hatasız, index.html kökte; social-videos dalı portal-paketleri 8e1d1a9 (crazygames/2026-11-17/), raw URL 200
  - GitHub release oluşturma bu oturum türünde 403; bu yüzden dal + doğrudan dosya teslimi
- **G-043** 2026-11-17 · Reklam yeri: portal yoksa eylem senkron (Peri Golf, Dolmuş, Kale Savunması, Çay Ocağı)
  - peri-golf #21, dolmus #27, kale-savunmasi #22, cay-ocagi #23: doğrulamalı birleşti (4 kontrol + gate RESULT OK)
  - Tarayıcı testleri (site + paket) dördünde TAMAM
- **G-042** 2026-11-17 · inject.mjs için test yok (eski inject.py'nin 7 testi taşınmadı)
  - arena-core #8: tests/inject.test.mjs (yerleşim, --kit-only/--core-only/--check, CRLF, eksik blok); CI ok
  - Mutasyon: CRLF koruması ya da çekirdek yerleşimi bozulunca kırılıyor
- **G-041** 2026-11-17 · arena-kit v1.3.2: reklam 'adstart'/'adend' yayar, 'pause' değil (17 oyun pause'da kilitleniyordu)
  - arena-core #5 (d1c5cd1); pilot kale-savunmasi #21 (gate RESULT OK, tarayıcı: reklamdan sonra dalga 2 başlıyor)
  - degisim.py 20/20 PASS; 20 PR doğrulamalı birleşti (bütün kontroller success + gate RESULT OK)
- **G-034** 2026-11-17 · Dil yedeği kenar durumu (boş/geçersiz dil): 10 oyunda düzeltildi
  - Tarayıcı dil denetimi 21 oyun x 4 senaryo (normal, boş navigator.language, ?lang=de, kayıtlı lang:de)
  - origin/main'de 10 oyun FAIL: boş dil Türkçe (Boğaz, Çay, Hamsi), ?lang=de Türkçe (Çay, Çini, Kervan, Lale), kayıtlı 'de' ile çökme (Martı, Mehter, Peri Golf: TypeError) ya da 'undefined' (Boğaz) ya da Türkçe (Simit)
  - Düzeltme sonrası aynı denetim 21/21 OK
  - PR: kervan#23, hamsi#19, lale-bahcesi#23, cini-ustasi#20, mehter#23, simit-firini#23, cay-ocagi#24, marti#21, peri-golf#22, bogaz-vapuru#22; hepsi 4 kontrol success + gate RESULT OK
  - Çay Ocağı, Peri Golf, Simit Fırını portal paketleri düzeltmeyle yenilendi (social-videos portal-paketleri a6ac251), yeniden test OK
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
- **G-020** 2026-11-17 · Video kuyruğu: Kale Savunması, Hamsi
  - Kale Savunması hikâye -14.0 LUFS/-1.5 dBTP, reels -14.3/-1.5 (kontrol.py TAMAM)
  - Hamsi hikâye -14.0/-1.1, reels -14.3/-1.5 (TAMAM); kareler pano görüntüsünde kontrol edildi
  - social-videos e9683db: 4 video + IG hikâye kodlaması (-2.9 / -2.1 dBTP), raw URL 200
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

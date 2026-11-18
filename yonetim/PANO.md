# Proje panosu

<!-- yonetim/pano.py uretti; elle duzenleme: kaynak yonetim/gorevler.json -->

Güncellendi: 2026-11-18 03:45 UTC

| Devam Ediyor | Test Ediliyor | Bekliyor | Engellendi | Tamamlandı |
|---|---|---|---|---|
| 4 | 2 | 4 | 3 | 35 |

**Sıradaki iş:** G-049 (P2) Instagram rehberi önerilerini teyit edip kurallara işle: YZ etiketi aracı, hikâye A/B, sıklık cümlesi, kenarlık denemesi, 5 hashtag + anahtar kelime, Hesap Durumu kontrolü

## Kalıcı kullanıcı onayları

- 2026-11-17: Rutin kod, refaktör, test, hata düzeltme, doküman, sürüm işleri onaysız; ortak altyapı değişikliği pilot + toplu değişiklik kapısından (schema/degisim.py) geçince kontrollü yayılır. Hesap, ödeme, geri alınamaz silme ve dış dünyada önemli sonuç doğuran işler Engellendi olarak kaydedilir.

## Aktif işler

| Id | Öncelik | Durum | İş | Alan | Bağımlı | Not |
|---|---|---|---|---|---|---|
| G-025 | P1 | Devam Ediyor | Instagram takvimi: Dolmuş reels, Ebru reels v3, sonra Çay Ocağı, Peri Golf, Mehter, Kırkpınar, Çarşı Kaçışı ... günde 2 oyun | sosyal |  | Buffer 10/10 dolu. 18 Kas 10:10Z hatırlatması yer açıldıkça sırayla zamanlar: Hamsi, Kale, Çay, Mimar Sinan, Pamukkale, Simit, Kapadokya, Kervan, Kırkpınar (+ Mehter/Çarşı yeni reels, daha önce gönderilmediyse) |
| G-048 | P1 | Devam Ediyor | Kalite taramasında kusurlu çıkan çekimleri yeniden çek: Kale Savunması, Çay Ocağı (durgun oynanış), Hamsi (karanlık boş deniz); sonra Peri Golf oyun, Çini tarama, Martı minyatür, Lale dalış | video | G-045, G-040 | Kale ve Çay yeniden çekildi (social-videos 5089b2f; reels 0/40 düz, 0/39 durgun); Kale Buffer'da 20 Kas 09:00/10:00, Çay 18 Kas 17:10Z hatırlatmasıyla sıraya girecek. Çini Ustası tarama yeniden çekildi (59e2af2; yeni rayAc ölçüsü varsayılan yolu düz bulup 180° çevirdi, tarama 0/9 düz, reels 1/40) ve 18 Kas 16:00/17:00 Buffer gönderilerinin videosu değiştirildi. video-studio #22 birleşti (0e32744). Hamsi beklemede: ham çekimler iyileşti (oyun/tarama/dalis OK) ama reels'te kur ve minyatür bölümü 16/40 düz (kurgu efektleri karanlık denizi eşiğin altına itiyor); sıradaki deneme: bu iki bölümde tekneye yakın kamera. Kalan: Peri Golf oyun (11/11 durgun), Martı minyatür, Lale dalış başı. |
| G-038 | P2 | Devam Ediyor | Performans ölçümünü haftalık yenile (Buffer -> performans.json) | sosyal |  | 18 Kas elle yenilendi: video-studio #20 (b485b66), 40 gönderi; IG reels n=15 ort. izlenme 503. Haftalık otomatik görev daha önce izin denetiminden geçmedi; sıradaki elle yenileme 25 Kas. |
| G-032 | P3 | Devam Ediyor | Meta-ilerleme (TOP 10 #6): yıldız, harita, kozmetik açılımlar | oyunlar | G-024 | 18 Kas denetimi: Peri Golf (12 delik, yıldız, delik seçimi) ve Pamukkale (23 bölüm, 5 bölge haritası) meta-ilerlemeye zaten sahip; Dolmuş ve Çay'da yıldız var, seçim ekranı yok; Kale'de yoktu. Pilot: kale-savunmasi #23 birleşti (2a27eb9) zaferde kalan cana göre 1-3 yıldız, ödülsüz (Playwright 9/9, kapı RESULT OK). Sıradaki: Dolmuş vardiya seçimi ızgarası (faz3 dolmus.md:45), Çay rütbe -> görünür süs (cay-ocagi.md:61). |
| G-039 | P0 | Test Ediliyor | Profil deposunda 26 Dependabot uyarısı: politika fikstürlerindeki vite@7.1.0 | güvenlik |  | Furkiozknn #48 birleşti (72a47f7): vite@7.1.0 fikstürden çıktı, 58 test OK. Uyarıların kapandığı Security sekmesinden görülmeli (alerts API 403) |
| G-037 | P1 | Test Ediliyor | Reels açılışı: 0. karede hareketli oynanış + tek iddia satırı (kurallar v2.1); ortalama izleme 2.5-3.5 sn | video |  | uygulandı (video-studio sahne-dalis-acikligi); yeni sırayla ilk yayınlardan sonra performans.json ile önce/sonra ölçülecek 18 Kas ara ölçüm: yeni motor reels'leri (Lale, Karagöz, Martı) ort. izlenme 3,16 sn vs eski 8 reels 3,51 sn; ancak ölçüm 9-33 saatlik ve asıl açılış değişikliği Dolmuş/Ebru v3 ile 19 Kas'ta çıkıyor. Erişim 14-15 Kas ~1000'den 16-17 Kas 150-270'e düştü. |
| G-049 | P2 | Bekliyor | Instagram rehberi önerilerini teyit edip kurallara işle: YZ etiketi aracı, hikâye A/B, sıklık cümlesi, kenarlık denemesi, 5 hashtag + anahtar kelime, Hesap Durumu kontrolü | sosyal | G-035 | Birincil sayfalar (about.fb.com, help.instagram.com, transparency.meta.com, buffer.com) bu oturumun ağında kapalı. Ortama bu alan adları eklenirse teyit edilebilir; Instagram uygulamasındaki 'AI etiketi' ve 'Hesap Durumu' kontrolü kullanıcı hesabında. |
| G-051 | P2 | Bekliyor | Test bayrakları oyuncu kaydına yazıyor: Dolmuş ve Pamukkale ?auto/?nosave'i yok sayıyor, Peri Golf ?auto'da, Kale ?nosave'de yazıyor (KARARLAR #3) | oyunlar |  | 18 Kas G-032 denetiminin yan bulgusu (dolmus lsSet 3013, pamukkale writeJSON 1703, peri-golf store.set 2571, kale store.set 2037). 4 depo: önce tek oyunda pilot. |
| G-053 | P3 | Bekliyor | Playgama paketleri: playgama-bridge.js ve config (üçüncü taraf kod) incelenip sabitlenerek pakete eklenir | portal | G-033 | portal.mjs --portal playgama hazır; köprü dosyası Playgama SDK'sından, sürüm sabit ve SHA ile. |
| G-054 | P3 | Bekliyor | Oyun CI: smoke (webkit) Ubuntu paket aynası yavaşlığında 15 dk sınırına takılıyor | altyapı |  | 18 Kas marti #22 ve kale #23'te testlerden önce apt kurulumunda iptal; tek yeniden çalıştırmada geçti. Öneri: webkit bağımlılıklarını önbellekle ya da timeout'u 25 dk yap. |

## Engellenen işler

| Id | Öncelik | İş | Gerçek neden | Gereken |
|---|---|---|---|---|
| G-050 | P2 | Reklam kancası pilotu: Martı (koşu sonu midgame + 'devam et' ödüllü), sonra toplu değişiklik kapısı ve kullanıcı onayı ile 12 oyuna | Pilot tamam (marti #22 birleşti bf78ddd: koşu sonu midgame + ödüllü devam; sahte Poki SDK testi 15/15, kapı RESULT OK, 4/4 kontrol). CLAUDE.md: 12 oyuna yaymak toplu değişiklik, schema/degisim.py kapısı ve kullanıcı onayı gerekiyor. | Kullanıcı onayı: kalan 12 oyuna (sıra docs/arastirma/portal-uygunluk-2026-11.md) aynı desenle reklam kancası |
| G-052 | P2 | Poki'ye gönderim | Poki for Developers geliştirici hesabı ve başvurusu kullanıcının işlemi | Kullanıcı Poki geliştirici hesabı açar; paketler social-videos portal-paketleri poki/2026-11-18/ |
| G-036 | P3 | Profilde 4 depoyu sabitle | GitHub sabitleme API'si bu oturumdan kapalı (yalnız profil sahibi arayüzden) | Kullanıcı github.com/Furkiozknn > Customize your pins (kullanıcı 18 Kas: 'birazdan hallederim') |

## Portföy

| Oyun | Kit | Video (TR hikâye+reels) | Instagram | Portal |
|---|---|---|---|---|
| bogaz-vapuru | 1.3.2 | hazır | zamanlandı 20 Kas 19:00/20:00 | reklam kancası yok; uygunluk sırası 8/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| carsi-kacisi | 1.3.2 | hazır | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| cay-ocagi | 1.3.2 | yeniden çekim (tarama, minyatür) | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| cini-ustasi | 1.3.2 | hazır | zamanlandı 18 Kas 19:00/20:00 | reklam kancası yok; uygunluk sırası 2/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| dolmus | 1.3.2 | yeniden çekim (tarama) | hikâye 19 Kas 19:00; reels bekliyor | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| ebru | 1.3.2 | yeniden çekim (dalış sonu) | zamanlandı 19 Kas 12:00/13:00 (reels eski sürüm) | reklam kancası yok; uygunluk sırası 13/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| fay-hatti | 1.3.2 | yok | - | reklam kancası yok; uygunluk sırası 3/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| hamsi | 1.3.2 | kuyrukta | sırada | reklam kancası yok; uygunluk sırası 10/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| kale-savunmasi | 1.3.2 | çekiliyor | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| kapadokya-balonu | 1.3.2 | yeniden çekim | sırada | reklam kancası yok; uygunluk sırası 7/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| karagoz | 1.3.2 | hazır | yayımlandı 17 Kas | reklam kancası yok; uygunluk sırası 4/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| kervan | 1.3.2 | yeniden çekim (gündüz) | sırada | reklam kancası yok; uygunluk sırası 11/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| kirkpinar | 1.3.2 | hazır | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| lale-bahcesi | 1.3.2 | hazır | yayımlandı 16 Kas | reklam kancası yok; uygunluk sırası 12/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| marti | 1.3.2 | hazır (reels v2) | yayımlandı 17 Kas | reklam kancası yok; uygunluk sırası 1/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| mehter | 1.3.2 | hazır | sırada | reklam kancası yok; uygunluk sırası 6/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| mimar-sinan | 1.3.2 | yeniden çekim (sis, dalış) | sırada | reklam kancası yok; uygunluk sırası 9/13 (docs/arastirma/portal-uygunluk-2026-11.md) |
| pamukkale | 1.3.2 | yeniden çekim (sis) | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| peri-golf | 1.3.2 | hazır | sırada | paket hazır (0,77 MB); CrazyGames iptal (18 Kas), Poki/Playgama bekliyor (G-033) |
| simit-firini | 1.3.2 | yeniden çekim (gündüz) | sırada | reklam yeri var (midgame); paket bekliyor (Poki/Playgama, G-033) |
| topkapi-gecesi | 1.3.2 | hazır | zamanlandı 18 Kas 12:00/13:00 | reklam kancası yok; uygunluk sırası 5/13 (docs/arastirma/portal-uygunluk-2026-11.md) |

## Geçmiş (tamamlanan, en yeni önce)

- **G-047** 2026-11-18 · video-studio: 3 CSS transition uyarısı (mascot/Captions, mascot/layouts/Lead, ELightPromo)
  - video-studio #21 birleşti (f6f97c8): 3 CSS transition kaldırıldı
  - pnpm lint exit 0, 0 hata 0 uyarı
  - Regresyon: VanCat-pilot 60/120, VanCat-lead 60/150, Promo-elight 200 dal/main bayt bayt aynı (5/5)
- **G-046** 2026-11-18 · video-studio main'de eski lint/tip hataları (eslint 10 hata, tsc 47 hata)
  - video-studio #17 birleşti (77daf39)
  - tsc --noEmit exit 0 (önce 47 hata: tsconfig lib es2015 ↔ hedef ES2018 çelişkisi + 4 kullanılmayan bağ)
  - pnpm lint exit 0, 0 hata (önce 10); main üzerinde birleşme sonrası yeniden koşuldu
  - Regresyon: 4 promo şablonu + çini promo + Ep30-v3-en 3 kare dal/main bayt bayt aynı (7/7 md5)
- **G-045** 2026-11-18 · Sahne motoru: rayAc kör noktaları (hareketli odak ve dokulu düz yüzey)
  - video-studio #18 birleşti (32dc2f1): rayAc alan ortalamalı küçültme + tek renk cezası; sahne/motor/kalite.mjs
  - Etiketli kareler: Ebru duvarı eski ölçüyle 14-40 (yanlış 'ayrıntılı'), yeni ölçüyle 4,9-11,8 (düz); iyi kareler 12,6+
  - Gerçek çekim: Çini Ustası tarama varsayılan yolu yeni ölçüyle %1-7 bulundu, ray 180° döndü, çekim 0/9 düz (yayındaki 9/9 düz duvar)
  - Hareketli odak kör noktası: kayıt sonrası saniyede bir kare ölçülüyor, düz kare oranı json'a yazılıyor ve %15 üstünde UYARI
- **G-040** 2026-11-18 · Oyun bölümünde hareket ölçümü: durağan oynanış çekimlerini yakala (ör. Peri Golf ilk 12 sn)
  - video-studio #18: kalite.mjs durgunluk ölçümü (saniyeler arası parlaklık farkı < 1,5), motor her çekimde çalıştırır; node sahne/motor/kalite.mjs <mp4> tek başına
  - 105 mevcut çekim tarandı: Peri Golf oyun 11/11, Kale Savunması 10/11, Çay Ocağı 8/11 sn durgun; Kervan 3/11 (örnekler yakalandı)
  - Düzeltmeler G-048'de
- **G-035** 2026-11-18 · Instagram reels büyüme rehberi: ücretli PDF yerine ücretsiz/birincil kaynaklardan
  - video-studio #19 birleşti (0b694b4): kutuphane/arastirma/instagram-reels-2026-11.md (kanıt gücü işaretli, kurallarla 17 satır karşılaştırma)
  - Sınır: resmi sayfalar ağ izin listesi yüzünden açılamadı ([R] maddeler ikincil); kurallar.md değişmedi, öneriler teyit bekliyor (G-049)
- **G-033** 2026-11-18 · Poki / Playgama paketleri (Playgama bridge dosyası, Poki pitch)
  - arena-core #10 birleşti (397c224): paket yüklenince Arena.portal.loading(false) -> PokiSDK.gameLoadingFinished (önce hiç gitmiyordu); portal.test ok, değişiklik geri alınınca düşüyor
  - 8 Poki paketi social-videos portal-paketleri 85bda9e poki/2026-11-18/ (NOTLAR.md); sahte Poki SDK çevrimdışı denetim 8/8 OK, SDK kaydı init+loaded
  - Gönderim G-052, Playgama G-053
- **G-029** 2026-11-18 · Portal sırası: kalan oyunlar için uygunluk/potansiyel listesi, midgame + ödüllü kancalar (Dolmuş, Kale Savunması ...)
  - docs/arastirma/portal-uygunluk-2026-11.md: 13 oyun sıralı (boyut, mola noktası, midgame yeri, ödüllü kanca adayı, uygunluk)
  - portfoy.json portal sütunu güncellendi (CrazyGames iptali, Kırkpınar/Simit birleşmiş reklam yeri)
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

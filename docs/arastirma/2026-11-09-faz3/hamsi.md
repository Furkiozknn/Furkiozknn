# Hamsi — faz 3 araştırması

Repo: `/home/user/hamsi` (dal `claude/cloud-session-research-analysis-dufc2b` = origin/main, HEAD `80bbff7`, `git status` temiz).
Etiketler: **D** = doğruladım/ölçtüm · **T** = tahmin/çıkarım · **K** = dış kaynak.
Ölçüm ortamı: headless Chromium + SwiftShader, makine paylaşımlı (load avg 20-40), bu yüzden fps değerleri performans kanıtı değildir.
Geçici dosyalar: `scratchpad/arastirma/_hamsi/` (`run.cjs`, `season-head.json`, `season-pre.json`, ekran görüntüleri).

## 1. Şu anki durum

- **D** Tek dosya `index.html` (2852 satır, 250 KB), Three.js r170, importmap + SRI (s.637), ARENA-KIT bloğu s.283-636. Kayıt anahtarları: `arena.hamsi.settings|save|best` (s.816). Kayıt `v:2`, `v:1` de yükleniyor (s.1612-1621).
- **D** Döngü: liman (pazar/geliştirme/ikmal/tersane) → denize çık → sonarda sürü bul → ağı at, sürünün çevresinde daire çiz, çek → yanaş, sat → uyu. 30 gün, kredi 110.000 ₺, faiz %0,6/gün (s.1007), hedef: krediyi kapatıp "reis" olmak. Günlük hedef 5 türden biri (s.1278-1288).
- **D** İmza mekaniği (`4dde3aa`): tekne sınıfları sandal→taka→trol→gırgır (s.988-997) ve 24 dakikalık gün-gece döngüsü (s.1009-1019). Gece hamsi yüzeye çıkıyor, sonar +%25 menzil, çarpma +%60 hasar.
- **D** Arena-kit entegre: günlük meydan okuma (1 gün, sandal, skor = günün satışı, s.2593-2597), paylaş, rozetler (`hamsi-girgir`, `hamsi-reis`, `hamsi-3star`), Reduce-motion → `G.reduced` (s.2633).
- **D** Bugün 3 "relay" commit'i (gemini-3.5-flash-lite) eklendi: `efbd960` "lidaki" kuralı + terim değişiklikleri, `2a49d37` titreşim + ekran flaşı, `d0d50d2` PWA manifest + service worker. Üçü de sorunlu (bkz. §3).
- **D** `?auto` bot 30 günlük sezonu bitiriyor, 0 JS hatası (HEAD: reis, net değer 274.044 ₺, 2 yıldız, 59 s; `9fec716` (relay öncesi): reis, 304.943 ₺, 3 yıldız). Konsolda yalnız botun kullanıcı jesti olmadan açtığı AudioContext uyarısı var (zararsız).
- **D** Açılış: 960×540 ve 390×844'te konsol hatası yok, `window.hamsi.errors` boş. Liman ekranı ilk karede açılıyor; denize çıkışta klavye ipucu toast'u + sis toast'u.
- **D** Telefon (390×844, dokunmatik): yatay taşma yok (scrollWidth 390). Sonar tuvali 140×80 px'e küçülüyor (s.150-153 portrait kuralı), etiketler okunamıyor.
- **D** Testler: `tools/smoke.mjs` + `.github/workflows/smoke.yml` (3 tarayıcı, SHA pinli, `permissions`, `timeout-minutes` var). Ekonomi/bot için otomatik test yok; `project-meta.json` `tests: null`.

## 2. Güçlü yanlar (korunmalı)

- Gerçek bir beceri mekaniği: ağın kapanma boşluğu (`gap`), sürünün ağın altından kaçması (derinlik, s.1395-1397), türlere göre ürkeklik (`skit`, `slip`). Bot da yalnız sonar verisiyle oynuyor (s.2770).
- Okunabilir zaman/risk gerilimi: fırtına uyarısı → fırtına penceresi, yakıt, tazelik/buz, sahil güvenlik çekmesi. Dredge'in "çık, tut, sat, geliştir, gece yakalan" döngüsüyle aynı ilke (K: Game Developer röportajı).
- Tekne sınıfları + taşınan geliştirmeler + takas/kredi dengesi: orta oyunda net bir hedef veriyor (bot gün 3-4'te taka, gün 18'de trol alıyor, **D**).
- Ekonomi seed'li ve deterministik hava/pazar (s.1214, s.1244), günlük meydan okuma aynı denizi veriyor.
- Prosedürel her şey (ses dahil, 7/8 horon), asset yok. Smoke testi ve SRI pilot projesi.
- Kayıt geriye uyumlu (v1 → taka, s.1618).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)

1. **"Lidaki" kuralı ekonomiyi bozuyor (HATA, D).** `sellSpecies` (s.1259-1260): gün ≤ 10 ve ambardaki hamsi < 250 kg ise gelir %80 kesiliyor.
   - Adım: Yeni sezon → ambara 150/249/251 kg hamsi → Sat. Ölçüm: ekranda ₺3.909 / ₺6.100 / ₺6.141 yazıyor; ödenen ₺782 / ₺1.220 / ₺6.141. **249 kg, 251 kg'ın beşte birine satılıyor** (keskin uçurum).
   - Sandalın ambarı 150 kg (s.989): ilk 10 günde sandalla tutulan hamsinin tamamı her zaman cezalı. **Günlük meydan okuma** gün 1 + sandal olduğu için hamsi orada hep %80 eksik satılıyor, skor bundan doğrudan etkileniyor.
   - "Boy" (balık uzunluğu) kuralı miktar (kg) üzerinden kurulmuş; gerçekte hamsi için asgari boy 9 cm (K). "Lidaki" kelimesini ve "açıkgöz" eşleşmesini hiçbir kaynakta doğrulayamadım; palamudun boy adları vanoz/çingene/palamut/torik/sivri/altıparmak (K).
   - Bot etkisi: gün 1 satışı 3.613 ₺ → 729 ₺; sezon sonu 3 yıldız → 2 yıldız (tek koşu, okyanus rastgele, n=1, **D** ama örneklem küçük).
   - `expectedValue` (s.2481) cezayı bilmiyor, pazar ekranı 5 kat fazla gösteriyor. `sellAll` sessiz çağırdığı için (s.1270) "Hepsini sat"ta uyarı toast'u hiç çıkmıyor; ceza görünmez.
   - Toast metni `L` sözlüğünde değil, sabit TR/EN dalı (s.1265).
2. **Terim gerilemesi (D).** `efbd960`: `rank2` "Reis" → "ağ ustası" (küçük harf), ama `end_reis` "Limanın reisi oldun!", `toast_start` "hayırlı olsun reis!", başlık metni ve README hep "reis" diyor; oyunun prompt'u "become reis of the harbour" istiyor. `b_trol` "vantrik" (kaynakta bulunamadı, K), İngilizcede de çevrilmeden küçük harfle "vantrik", "gırgır"; başlık açıklaması hâlâ "trol" diyor. Liman başlığı "Balıkçı Limanı · vantrik" (küçük harf).
3. **PWA commit'i ölü kod (D+K).** Service worker `blob:` URL'den kaydediliyor (s.639); spesifikasyon yalnız http/https kabul ediyor, ölçümde `getRegistrations()` = 0. Worker hiçbir şeyi cache'e koymuyor. Manifest `data:` URL, ikon yok, `start_url` "." data URL'ye göre çözülüyor: yüklenebilir değil (**T**). Commit mesajı var olmayan bir özelliği ilan ediyor.
4. **Telefon dikey düzeni (D, ekran görüntüsü `head-phone-sea.png`).** Sonar 140×80 px, fish-finder etiketleri ~5 px; oyunun ana bilgi kaynağı telefonda okunamıyor. Toast'lar hız göstergesinin üstüne biniyor. Dokunmatikte klavye ipucu toast'u ("W/S gaz · A/D dümen…", s.1553) gösteriliyor. `body.touch #actions .hint{display:none}` (s.124) yüzünden telefonda "daireyi kapat, sonra çek (N m ağ)" ipucu hiç görünmüyor.
5. **İlk deneyim (T).** Tek öğretim: başlıktaki bir paragraf + klavye toast'u. Ağı "daire çizerek" atmak oyunun en zor ve en özgün becerisi; geri bildirim yalnız "Ağ boş kaldı" / "X kg yakalandı". Neden az tutulduğu (boşluk mu, derinlik mi, kaçış mı) söylenmiyor, oysa veri var (`n.gap`, `n.members`, `G.today.gaps`).
6. **Erişilebilirlik (D).** Yeni `canvas#gl.flash` (parlaklık 1.6, 0,3 sn, her çekişte) ve `hurtFlash` (s.2320) Arena "Reduce motion" anahtarına bağlı değil (s.280 yalnız `#lens`, `#wcard.warn`). OS `prefers-reduced-motion` CSS kuralı animasyonu kısaltıyor ama Arena anahtarı kısaltmıyor. Titreşimin kapatma ayarı yok.
7. **GoatCounter (D, T).** `gc.zgo.at/count.js` (s.638, `a4bf512` ile geldi) brief'teki "harici ağ çağrısı yok / veri toplanmaz" kısıtıyla çelişiyor. Çerezsiz sayaç ama yine de harici istek. Sahip kararı gerekiyor; smoke testi bunu bilerek yok sayıyor.
8. **Tekrar oynanabilirlik (T).** Sezon bitince aynı 30 gün; tohum değişiyor ama hedef, tekneler, türler aynı. Bot kredisini gün 26-27'de kapatıyor, son günler hedefsiz.
9. Küçük: README hız için hem "x1/x2/x4" (s.74) hem "x1/x2/x3" (s.79) diyor; kod x4 (s.2615).

## 4. EKLENMELİ — yüksek değer

**4.1 Ağ çekiş karnesi (circle report)**
- Ne: Her çekişten sonra kısa bir kart/toast: kapanma boşluğu (m), yakalanan / kaçan (boşluktan) / alttan kaçan sayısı, "ağ derinliği yetmedi" uyarısı. Sonarda ağın başlangıç şamandırasını belirgin halka + "kapanmaya X m" göstergesi.
- Neden: Oyunun özgün becerisi ağın kapanışı; öğretim tutundurmanın ilk dakikalarında en etkili şey ve sonuç üzerinden öğretmek metinden hızlı (K: Google Play onboarding, Roblox FTUE). Dredge'de de oyuncu neden başarısız olduğunu görüyor.
- Nasıl: `startHaul` (s.1385-1407) zaten `gap`, `members` hesaplıyor; kaçış nedenini (gap / depth) iki sayaçla say, `finishHaul`'da bir toast ya da HUD içi küçük kart. Sonar çiziminde (s.2421) `G.net.pts[0]`'a halka. i18n anahtarları `L`'ye.
- Maliyet S. Risk düşük (yalnız UI; kayıt ve bot etkilenmiyor). Kısıta uyuyor.

**4.2 İlk sefer rehberi (yaparak öğretme)**
- Ne: İlk sezonun 1. gününde 5 adımlı bağlamsal rehber: Denize çık → sonardaki noktaya git → Ağı at → daireyi kapat → çek → yanaş + sat. Adım tamamlanınca bir sonraki çıkıyor; atlanabilir; `localStorage`'da `tutDone`.
- Neden: Bugün öğretim bir paragraf + klavye satırı; telefonda ipucu satırı tamamen gizli (s.124). Portallar oyuncunun hemen oynamaya geçmesini ve oyun içinde kısa bir öğretimi bekliyor (K: CrazyGames gereksinimleri).
- Nasıl: mevcut `actHint` metinlerini (s.2369-2374) yeniden kullan; dokunmatikte ipucunu `#actions` üstünde tek satır göster (s.124'ü kaldır ya da kısalt). Dokunmatikte klavye toast'u yerine "kolu yukarı it, dümeni çevir".
- Maliyet S-M. Risk: bot (`G.auto`) ve günlük meydan okuma için kapalı olmalı. Kayıt anahtarı yeni olduğu için eski kayıtlar etkilenmez.

**4.3 Telefon dikey sonar düzeni**
- Ne: Dikeyde sonar ile fish-finder'ı ayır ya da sonara dokununca büyüyen (yarım ekran) bir görünüm; etiket fontunu ekrandaki piksel boyutuna göre ölçekle.
- Neden: Telefonda ana bilgi okunamıyor (**D** 140×80 px). Mobil oyuncu çoğunluk; brief telefon desteğini zorunlu sayıyor.
- Nasıl: s.150-153 kuralını değiştir (ör. sonar üstte tam genişlik `min(370px, 100vw-20px)`, gauge'lar sıkışık satır); `drawSonar` font boyutunu `sonarC.clientWidth`'a göre ayarla. Toast kutusunu dikeyde göstergelerin altına taşı.
- Maliyet S-M. Risk: düzen kırılması; 390×844, 360×740, 500×900'de ekran görüntüsüyle doğrulanmalı.

**4.4 Sezon sonu sonrası hedef: "zor sezon" seçenekleri**
- Ne: Sezonu bitirince açılan 2-3 değiştirici (daha büyük kredi, daha sık fırtına, sandalda kal…) ve her biri için ayrı en iyi skor.
- Neden: Tekrar oynama nedeni yok (bot gün 26'da krediyi kapatıyor). Değiştiriciler mevcut sistemlerin parametreleri (`START_LOAN`, `pickStormDays`), içerik maliyeti düşük.
- Nasıl: `freshRun` (s.1527) bir `mod` nesnesi alır; kayda `mod` alanı ekle (yoksa varsayılan = eski kayıt). Best anahtarı `arena.hamsi.best` yanında `arena.hamsi.best.<mod>`.
- Maliyet M. Risk: kayıt uyumu (alan opsiyonel tutulursa düşük), bot varsayılan modda kalır.

## 5. EKLENEBİLİR — orta değer / koşullu

- **Seyir defteri / av kayıtları (S):** En büyük tek çekiş, tür başına toplam, en dar kapanış. `G.log` zaten var (s.1588). Rozet sistemiyle çakışmamalı (Arena rozetleri ayrı).
- **Gece ışıkçı geliştirmesi (M):** Hamsi ışığa geliyor zaten (s.1338); gece için "lamba gücü" yükseltmesi sürünün yüzeye çıkışını artırır. Mevcut 6 eksene 7. eklemek UI ve kayıt (`G.up`'a alan, `Object.assign` ile eski kayıt güvenli) gerektirir. Koşul: §3.1 düzeltildikten sonra, ekonomi yeniden ölçülerek.
- **Hal olayları (S-M):** Ara sıra "bugün palamut talebi yüksek" günü; `refreshMarket` içinde seed'li. Hava tahmini gibi bir önceki günün özetinde duyurulur.
- **Rakip tekneler sürü kapsın (M):** `aiBoats` görsel olarak var (s.1974); yakındaki sürüleri yavaşça küçültmeleri aciliyet katar. Risk: bot dengesi, performans; ölç.
- **Titreşim/flaş ayarı (S):** Ayarlarda "titreşim" anahtarı; flaşlar `G.reduced`'a bağlı.

## 6. EKLENMEMELİ

- **Gerçek PWA / çevrimdışı mod:** Ayrı `sw.js` ve ikon dosyası ister; tek-dosya kısıtını aşar. Blob/data URL ile yapılamaz (K: MDN). Mevcut ölü kod da kaldırılmalı.
- **Çevrimiçi skor tablosu, hesap, bulut kayıt, canlı balık fiyatı API'si:** sunucu/harici ağ kısıtını aşar.
- **Miktara ya da güne bağlı keskin ceza eşikleri** ("lidaki" gibi): görünmeyen, açıklanmayan uçurumlar oyuncuyu cezalandırıyor ve gerçek boy kuralını yanlış öğretiyor. Gerçekçilik isteniyorsa boy/kota, sonarda görülen ve oyuncunun seçebildiği bir şey olmalı.
- **Doğrulanmamış "otantik" terimler** (vantrik, lidaki/açıkgöz): kaynak gösterilmeden eklenmemeli; Türk oyuncu yanlış terimi hemen fark eder.
- **Tam ekran parlak flaş / sarsıntı efektleri çoğaltmak:** erişilebilirlik ilkelerine ters (K: Game Accessibility Guidelines, Xbox XAG 118).
- **Ağır görsel ekler** (post-processing, gerçek su yansıması, gölge çözünürlüğü artışı): UHD 620 bütçesi; README 18-56 draw call ölçmüş, mevcut ölçümüm (43 call) bunu bozmuyor, artırmaya gerek yok.
- **Gerçek bir oyunun (Dredge, Fishing Planet vb.) adı, korku teması, karakteri, müziği:** yalnız ilke alındı.
- **Reklam, ödüllü reklam, ücretli içerik:** ücretsiz/hesapsız ilkesine aykırı.

## 7. Düzeltilmeli

| # | Ne | Kanıt | Maliyet |
|---|----|-------|---------|
| 1 | "Lidaki" kuralını kaldır (s.1259-1260, 1265) ya da tamamen yeniden tasarla (görünür, i18n'de, `expectedValue` ile tutarlı, eşiksiz, günlük meydan okumayı bozmayan) | §3.1, ölçüm | S |
| 2 | `rank2` → "Reis"/"Reis" (TR/EN), `b_trol` → "Trol teknesi"/"Trawler", `n_trol` eski haline, EN'de `b_girgir` "Purse seiner" | §3.2, `git show efbd960` | S |
| 3 | s.639 blob service worker ve s.19 data manifest satırını kaldır | §3.3, `getRegistrations()=0` | S |
| 4 | `canvas#gl.flash` ve `hurtFlash`'ı `G.reduced`'a bağla; s.280'e `#gl.flash` ekle | s.29-30, 1420-1422, 2320 | S |
| 5 | Dokunmatikte klavye ipucu yerine dokunmatik ipucu; s.124 `hint{display:none}` gözden geçir | ekran görüntüsü | S |
| 6 | Dikeyde toast kutusu göstergelerle çakışıyor | `head-phone-sea.png` | S |
| 7 | README hız tutarsızlığı (x3 → x4) | README s.79 | S |
| 8 | GoatCounter: sahip kararı (kaldır ya da brief kısıtını açıkça istisna yap) | s.638 | S |
| 9 | Ekonomi regresyon testi: `?auto` sezonunu 3 tohumla koşup reis + yıldız sayısını kontrol eden küçük bir `tools/` betiği (bugünkü hata smoke'tan geçti çünkü smoke yalnız yükleme hatası arıyor) | §3.1 | S-M |

## 8. Önerilen ilk 3 iş

1. **Bugünkü relay commit'lerinin hatalarını geri al (§7.1-7.4).** Neden ilk: oyun şu an gösterdiği fiyatın beşte birini ödüyor, günlük meydan okuma skoru bozuk, ana hedef ("reis") metinlerde çelişiyor, ölü PWA kodu yanlış iddiada bulunuyor. Hepsi S; `9fec716` ile karşılaştırma ve `?auto` sezonu ile doğrulanır (relay öncesi: reis, 3 yıldız). Bu düzelmeden ekonomi üzerine yeni özellik ölçülemez.
2. **Ağ çekiş karnesi + sonarda başlangıç şamandırası (§4.1).** Oyunun özgün becerisini öğreten, en ucuz ve en yüksek getirili ekleme; kayıt/bot riski yok.
3. **Telefon dikey düzeni + dokunmatik ipuçları (§4.3 ve §4.2'nin dokunmatik kısmı).** Telefonda sonar okunamıyor ve "daireyi kapat" ipucu gizli; mobil oyuncu için çekirdek döngü şu an öğrenilemiyor. Sonra tam ilk sefer rehberi (§4.2) gelir.

## 9. Doğrulanmayanlar / açık sorular

- "Lidaki" ve "vantrik" kelimelerinin yerel bir kullanımı olabilir; web aramasında bulamadım. Sahip ya da bir Karadeniz balıkçısı doğrulamalı. Doğru olsalar bile mevcut uygulama (kg eşiği) yanlış.
- Bot sezonu her sürüm için yalnız 1 kez koşuldu (sürü konumları `Math.random`); 3 → 2 yıldız farkının ne kadarı lidaki, ne kadarı şans, bilinmiyor. Gün 1 farkı (3.613 → 729 ₺) ise doğrudan kurala bağlı.
- Gerçek Intel UHD 620 ve gerçek telefon ölçümü yapılmadı (SwiftShader + yüklü makine: 10 fps, anlamsız). 43 draw call ölçüldü (denizde, liman yakını).
- `data:` manifest'in Chrome'da hiç işlenip işlenmediği ölçülmedi (T); SW'nin kaydolmadığı ölçüldü.
- GoatCounter'ın brief'teki "veri toplanmaz" kısıtına girip girmediği sahip kararı.
- Firefox/WebKit'te yeni flaş/titreşim davranışı denenmedi.

## Kaynaklar

- Black Salt Games, Dredge döngüsü: https://www.gamedeveloper.com/design/trawling-in-the-deep-how-black-salt-games-made-spooky-fishing-rpg-i-dredge-i-
- GameSpot Dredge incelemesi (risk dengesi): https://Gamespot.com/reviews/dredge-review-grant-us-eels/1900-6418049/
- CrazyGames oyun gereksinimleri (hemen oyuna giriş, kısa oyun içi öğretim): https://docs.crazygames.com/requirements/gameplay/ ve https://docs.crazygames.com/requirements/quality/
- Google Play, onboarding ve ilk dakikalar: https://medium.com/googleplaydev/the-user-journey-onboarding-and-activation-be5ebdfc0354
- Roblox FTUE / onboarding: https://create.roblox.com/docs/production/game-design/onboarding
- Game Accessibility Guidelines, titreşen görüntüler: https://gameaccessibilityguidelines.com/avoid-flickering-images-and-repetitive-patterns/
- Xbox Accessibility Guideline 118 (fotosensitivite): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/118
- MDN `ServiceWorkerContainer.register()` (yalnız http/https): https://developer.mozilla.org/docs/Web/API/ServiceWorkerContainer/register
- Hamsi asgari boyu 9 cm: https://yemek.com/yasalara-gore-avlanabilir-balik-boylari-hangi-balik-kac-santimetre-olmali/ ve https://www.tarimorman.gov.tr/Haber/4884/Basin-Aciklamasi-Hamsi-Avciligi-Kismi-Olarak-Durdurulmustur
- Palamut boy adları: https://istanbulansiklopedisi.org/handle/rek/11450
- Gırgır ağı çalışma ilkesi: https://dergipark.org.tr/tr/download/article-file/252294

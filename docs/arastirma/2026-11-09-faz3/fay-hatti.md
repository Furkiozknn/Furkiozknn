# Fay Hattı — faz 3 araştırması

Kapsam: `/home/user/fay-hatti` (dal `claude/cloud-session-research-analysis-dufc2b`, HEAD 480e9cb), `index.html` 6152 satır / 364 KB, 2D canvas, Three.js yok.
Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak. Geçici dosyalar ve ekran görüntüleri:
`/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_fay-hatti/`. Repo değiştirilmedi (`git status` temiz, D).

## 1. Şu anki durum
- **D** Motor sağlam: `node tools/sim.mjs 20261109 14 12` → 26/26 bulmacayı iki bot da çözdü, ortalama par 4,23, A = par, B 7,46, üretim ortalaması 74 ms, en kötü 441 ms. `node tools/cardcheck.mjs` → PASS (7/7 günlük tohum `cards=none` ile `all` arasında aynı).
- **D** Bot: `?auto` günlük 20261109 → 4 hamle = par, 3 yıldız; `?auto&level=9` → 4 = par; `?auto&demo=b&seed=20261111` → 15 hamle (par 5). Konsol/sayfa hatası 0, ağ isteği 0 (file:// dışı istek yok).
- **D** Zorluk eğrisi: günlük, haftanın gününe göre K (`dailyConfig`, satır 1435-1441: Pzt 4 … Paz 6). Sonsuz Normal'de K, 8. seviyede 6'ya ulaşıp sabitleniyor (`endlessConfig`, 1468). Sonrasında par 4-5 arasında kalıyor (sim: seviye 7-12 par 4-5). Yalnız harabe ve çifte fay döngüsü değişiyor (1475). Rozetler 50. seviyeye kadar sürüyor (5107-5112).
- **D** Kayıt: `localStorage` `fayhatti.*` (1492-1495). Normal kademe eski `endless` anahtarını koruyor (2422-2423). Eski kayıt (`endless=7`, `daily.20261108`) testte "Normal · Level 7" olarak yüklendi. Bu kayıttaki seri ise 0 gösterildi, çünkü seri ayrı `fayhatti.streak` anahtarında tutuluyor.
- **D** Açılış akışı (6148): tohum parametresi yoksa günlük tahta kuruluyor ve **menü hemen açılıyor**. İlk ziyarette eğitim baloncuğu (`tutTip.on`) menünün arkasında da açık. "Günün bulmacası"na basınca 5 maddelik Yardım penceresi, ardından 3 adımlı eğitim geliyor (5913-5920). İlk tahtaya ulaşmadan önce 3 katman var.
- **D** Telefonda (390×844) düzen taşmıyor (`scrollWidth` 390). Araç çubuğu düğmeleri 64×50 px. Sürükleme ve kaydırma hamlesi çalışıyor (hamle 0→1). Menü paneli 24 düğme içeriyor; `scrollHeight` 1201 px, görünen 812 px.
- **D** i18n: EN ve TR anahtar sayısı 180/180, eksik yok. `aria-label`'ların çoğu dile göre güncelleniyor (5033-5085).
- **D** Telemetri yalnız yerelde: halka tampon + `CustomEvent` (2371-2392). `fetch`/`sendBeacon` yok, kısıta uyuyor.
- **D** Kare maliyeti düşük: `frame()` JS süresi p50 0,4 ms, p95 1,1-1,8 ms (masaüstü ve 2×DPR telefon). Döngü ise modallar açıkken de her kare tam çiziyor (4428-4469).
- **D** "Kart açma" sistemi (18 kart, 1712-1910) hiçbir şeyi kilitlemiyor. `hasCard()` oyun kodunda hiç çağrılmıyor (yalnız API, 6000). Temalar menüde her zaman seçilebilir, oynanış kartları her zaman açık.

## 2. Güçlü yanlar (korunmalı)
- Tersine karıştırma (ters hamle + ters deprem) sayesinde her bulmaca çözülebilir. Par en iyi çözümden geliyor (1355-1433, sim D). Bu, oyunun güveninin temeli.
- Deprem bir hamle önceden haber veriliyor: kırmızı bant, kesik çerçeve, ok ve metin (4480-4490, ekran görüntüsü D). Hamle haritayı çözerse deprem olmuyor (2966). Okunaklı ve adil bir ritim.
- Tek dosya, harici istek yok, `?auto`/`?demo`/`?seed`/`?level`/`?nosave` bayrakları ve zengin `window.fayHatti` API'si test ve video için çok değerli.
- Erişilebilirlik temeli: klavyeyle tam oynanış (WASD + oklar, 4996-5018), canlı bölge duyuruları, yüksek kontrast modu, az hareket desteği, 44 px kenar hedefleri (4951) ve kaydırma eşiğiyle kaza koruması (4971-4975).
- Paylaşım: spoiler'sız metin ve PNG kart, `navigator.share` ile dosya. Daha önce tek dosyaya ulaşıp ağ çağrısı yapmıyor.
- "Köylüler" imza mekaniği: deprem sonrası "Sağ mı?" raporu, isimler yerel (2570-2657, D: rapor üretildi).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **HATA, D — bölge kartı haftalık rotasyonu kalıcı olarak donduruyor.** Adımlar: `fayhatti.cards` = bölge-ege dışında hepsi → `?seed=20261109` haritasını çöz → kart seçimi → "Ege"yi seç. Sonuç: `fayhatti.biome="ege"` yazılıyor. O anki Kapadokya haritası sonuç ekranında Ege'ye dönüyor. `?seed=20261130` (Bozkır haftası olmalı) da `ege` açılıyor. Neden: kartın `apply` çağrısı `applyBiome('ege')` ve bu varsayılan olarak `save=true` (1565, 2108-2113). `getBiome` ilk satırda bu ayarı döndürüyor (2085). Arayüzde ayarı silen bir yol yok (`applyBiome(` yalnız 1541/1553/1565/5090/5091/5995'te geçiyor).
2. **D — kart döngüsü boş bir ödül.** Her galibiyette kart teklif ediliyor (3116-3121; `boardsSinceCard` artıyor ama hiçbir yerde koşul olarak okunmuyor). Teaser her zaman "Sıradaki kart 1 tahta sonra" (2038). Kartlar hiçbir şeyi açmıyor (bkz. §1). "Gece/Kâğıt" kartını seçmek temayı zorla değiştiriyor (`apply: applyTheme`). İlk 17 galibiyet sonuç ekranının önüne fazladan bir modal ekliyor.
3. **D — ilk deneyim ağır.** Bunun için 3 katman (menü → yardım → eğitim) ve 24 düğmeli, kaydırılan bir menü var. İlk tahtada "0 gün seri" hapı görünüyor; yeni oyuncu bir kayıpla karşılanıyor (ekran görüntüsü 02b). Eğitim baloncuğu telefonda alt kenar oklarının üstünü kapatıyor (tutTip y 605-761; tahtanın altındaki sütun okları görünmüyor, ekran görüntüsü D).
4. **D — "Tohum Doğrulama" ana iş parçacığını donduruyor.** `runSeedVerification('20261130','20261231')` 32 bulmacayı eşzamanlı üretip çözüyor (5329-5356). Headless'ta 16,8 s ölçüldü. Gerçek donanımda bunun birkaç kat kısa olması beklenir ama yine de saniyeler sürer (T). Aralık sabit kodlanmış: bugünü (9-29 Kasım) kapsamıyor ve 1 Ocak 2027'den sonra menüdeki "31 Aralık'a kadar onaylandı" yazısı bayatlıyor. Bir geliştirici aracı oyuncu menüsünde duruyor.
5. **D — sonsuz modda zorluk 8. seviyede düzleşiyor.** 50 seviyelik rozet yolunun 42 seviyesi aynı K=6 ve benzer par ile geçiyor. Çeşitlilik yalnız harabe ve çifte fayda.
6. **T — günlükte takılan oyuncunun yardımı yok.** İpucu günlükte kapalı (`isHintActive`, 2661). Yalnız geri alma ve baştan başlama var. Par 3-5 olsa da depremler zihinsel yükü artırıyor. Oyuncu verisi yok, doğrulanmadı.
7. **D — paylaşım metni hikâye anlatmıyor.** Metin "Fay Hattı 2026-11-09 ⭐⭐⭐ 4 hamle + URL" biçiminde (5383-5387). Wordle'ın ızgarası denemenin "hikâyesini" taşıyor (K).
8. **D, küçük — az hareket ayarı sonradan açılınca süreler değişmiyor.** `DUR` yüklemede bir kez hesaplanıyor (3131). Arena paneli `RM`'i canlı değiştiriyor (6127), ama kaydırma ve deprem süreleri sayfa yenilenene kadar uzun kalıyor.
9. **D, küçük — modal açıkken bile her kare tam çizim.** Pil ve ısı açısından gereksiz (T). Headless'ta menü açıkken kompozisyon çok yavaşladı; bu ortama bağlı olabilir (T).
10. **T — iki ayrı seri sistemi var.** Oyunun `fayhatti.streak` serisi ve arena-kit'in `Arena.daily` serisi. İkisi farklı sayılar gösterebilir; oyunun serisi eski günlük kayıtlardan geriye dönük hesaplanmıyor (D: eski kayıtla seri 0).

## 4. EKLENMELİ — yüksek değer
**4.1 Bölge kartı hatasını düzelt + kartları gerçek "açılış" yap ya da sadeleştir**
- Ne: Kart `apply`'ı kalıcı biome ayarı yazmamalı. Ya kartlar gerçekten bir şey açmalı (ör. Gece/Kâğıt teması kart alınana kadar menüde kilitli) ya da teklif her N tahtada bir gelmeli (`boardsSinceCard >= 3`) ve teaser gerçek sayıyı göstermeli.
- Neden: Şu an ödül anlamsız, akış uzuyor ve hata rotasyonu bozuyor.
- Nasıl: `applyBiome(b, false)` ile yalnız önizleme yap. `fayhatti.biome` ayarını yalnız menüdeki açık bir "Bölge: otomatik/…" seçicisi yazsın, "otomatik" `null` olsun. Eski kayıtlar için açılışta bir kez göç gerekiyor: `cards` içinde region-* varsa ve `biome` ayarlıysa sil. Bu, tek seferlik bir kayıt düzeltmesi. Hamle, par ve skora dokunulmuyor; `cardcheck.mjs` bunu korur.
- Maliyet S. Risk düşük (kayıt göçü dikkat ister). Kısıtlara uyuyor.

**4.2 İlk deneyimi tek akışa indir ("oynayarak öğret")**
- Ne: İlk ziyarette menüyü ve 5 maddelik yardımı atla. Doğrudan, 1-2 hamlelik, depremsiz ya da tek depremli bir "ilk harita" aç (Kolay kademe 1. seviyesi buna uygun: K=2, sakin turlar). Eğitimin 3 adımı bu haritanın üstünde, oyuncunun hamlesiyle ilerlesin. Yardım menüde kalsın.
- Neden: Metinli eğitimler zayıf kalıyor. Tek mekanikli, kaybedilmesi neredeyse imkânsız ilk bölüm öneriliyor (K: GDevelop, Puzzledorf, Zachtronics alıntısı). Portal'ların (CrazyGames) "yeni oyuncuyu hemen oynanışa sok" beklentisi var (K).
- Nasıl: Açılışta `!store.get('help') && !store.get('tutDone')` ise `startPuzzle('endless', 1)` ile Kolay kademeyi geçici aç ya da `loadBridgeDemo` benzeri sabit bir tanıtım tahtası kullan. Menüyü (6148) yalnız eski oyunculara aç. Eğitim baloncuğu telefonda üstte (HUD altında) dursun, böylece alt okları kapatmaz.
- Maliyet M. Risk: `?auto` yolu değişmemeli (BOT dalı ayrı, 6147 → korunuyor). Günlük tohum aynı kalmalı.

**4.3 Menüyü sadeleştir**
- Ne: Ana menüde Günlük, Sonsuz (+kademe), Maraton ve Nasıl oynanır kalsın. Rozetler, tema, köylü isimleri, kontrast, haptik ve el yönü "Ayarlar" alt paneline taşınsın. "Tohum Doğrulama" yalnız `?debug` ile görünsün.
- Neden: Telefonda 24 düğme ve 1201 px'lik kaydırılan bir panel var; oyuncunun ilk kararı gömülüyor (D).
- Nasıl: `fillMenu` içinde iki `<details>` grubu (mevcut `villBox` deseni zaten kullanılıyor, 895). Doğrulama düğmesini `DEBUG` koşuluna bağla.
- Maliyet S-M. Risk düşük.

**4.4 Wordle tarzı "deprem hikâyesi" satırı ekle**
- Ne: Paylaşım metnine her hamle için bir emoji satırı ekle. Örnek: bağlı köy sayısına göre 🟫/🟦/🟩, depremin bağlantı kopardığı hamlede 🔴, son hamle 🟩. Spoiler vermiyor, denemenin akışını anlatıyor.
- Neden: Wordle'ın yayılmasında ızgaranın "denemenin hikâyesini" taşıması belirleyici oldu (K: Wardle, GDC). Mevcut metin yalnız skor veriyor.
- Nasıl: `doMove` sonrası `countLinked()` (2548) zaten var; hamle başına `{linked, quaked}` dizisi tut ve `shareText()` (5383) bu satırı eklesin. Günlükte de güvenli, çünkü harita bilgisi sızmıyor.
- Maliyet S. Risk düşük (bot ve kayıt etkilenmez).

**4.5 Günlükte "nazik yardım" ama skor bedelli**
- Ne: Günlükte de ipucu olsun. Ama kullanılırsa sonuç ve paylaşım "💡" ile işaretlensin ve en fazla 2 yıldız verilsin (sonsuz moddaki 1 yıldız kuralına benzer).
- Neden: Takılmayı çözmek, oyunu bırakmaktan iyidir. GAG "assisted progress / skip" öneriyor (K).
- Nasıl: `isHintActive` (2661) günlüğü kapsasın. Yıldız hesabı (2979, 3044) mod bazında olsun. `cardcheck` "ipucusuz skor aynı" kontrolünü korur.
- Maliyet S. Risk: günlük adaleti → kararı kullanıcıya bırak.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Geçmiş günler arşivi** (M): Menüde son 14-30 günün takvimi, `?seed=YYYYMMDD` ile zaten çalışıyor. Çözülenler `daily.*` anahtarından işaretlenir. NYT Wordle/Connections arşivi kaçırılan günleri telafi için eklendi (K). Kısıt: üretim ana iş parçacığında ~0,1-0,4 s, kabul edilebilir (D: sim). Seri yalnız bugünün çözümüyle artmalı.
- **Seri koruması** (S): Ayda 1 "dinlenme günü"; kaçırılan tek gün seriyi bozmasın. Duolingo'nun Streak Freeze'i kayıp korkusunu yumuşatmak için var (K). "0 gün seri" hapını seri ≥1 olana dek gizle (D sorunu).
- **Sonsuz mod için eğri uzatma** (M): K=6'da kalırken 8+ seviyelerde `minPath`, `nv`, `blocked` ve `P` (deprem döngüsü 5→4) yavaşça sıkılabilir. Solver maliyetini sim ile ölç; `minPar` artışı üretim süresini katlayabilir (T, sim'de ≤441 ms).
- **Doğrulamayı arka plana al** (S): `runSeedVerification` için tahta başına `setTimeout`/`requestIdleCallback` dilimleri ve bir ilerleme çubuğu. Aralık `todaySeed()`'den başlasın. Yalnız `?debug` ile görünsün.
- **Modal açıkken çizimi azalt** (S): `document.querySelector('.ov.on')` ise 4 karede 1 çiz ya da yalnız animasyon sürerken çiz. Bu Intel UHD ve telefon pili için iyi (T).
- **Oyun serisini arena serisiyle eşitle** (S): Tek seri gösterilsin, ya da oyunun serisi `daily.*` kayıtlarından geriye dönük hesaplansın (eski kayıtlar için).

## 6. EKLENMEMELİ
- **Daha fazla "kart"/kozmetik tema/bölge**: Zaten 18 kart, 4 bölge ve 3 tema var; menü ve akış şişmiş durumda (D). Önce mevcutlar anlamlı hâle gelmeli.
- **Günlükte süre ölçümü veya süreye dayalı yıldız**: Günlük "düşün ve çöz" bulmacası. Süre baskısı par mekaniğini bulanıklaştırır ve erişilebilirliği düşürür (GAG, K).
- **Liderlik tablosu / çevrimiçi karşılaştırma / bulut kayıt**: Sunucu ve hesap ister, kısıtı aşar.
- **Gerçek reklam, Poki/CrazyGames SDK'sı veya analitik gönderimi**: Harici ağ çağrısı ve kullanıcı verisi demek, kısıtı aşar.
- **Deprem RNG'sini hamleye bağlı/rastgele yapmak**: Telegraf edilen, sabit döngü adaletin temeli. Par ve bot uyumunu bozar.
- **5×5'ten büyük ızgara**: Telefonda hücre ~60 px'e iner, IDDFS çözücü katlanır (T). DESIGN.md de 5×5'i koruyor.
- **Gerçek bir oyunun adı/görseli ile tema** (ör. tanınmış harita oyunlarının sanatı): Yasak; mevcut Anadolu motifleri yeterli.

## 7. Düzeltilmeli
- Bölge kartı → kalıcı biome ayarı (§3.1) ve kayıt göçü. **Öncelik 1.**
- `boardsSinceCard` kullanılmıyor, teaser yanlış (`cardTeaserPlural` hiç kullanılmıyor; 3116, 2038).
- İlk ziyarette eğitim menünün arkasında başlıyor (6148 + 2942): menü açıkken `showTut` erteleyin.
- Telefonda eğitim baloncuğu alt okları kapatıyor (CSS 237, `bottom:10px`).
- "0 gün seri" hapı (2507-2512): seri 0 iken gizle.
- `DUR` sabiti (3131): `RM` değişince yeniden hesapla (Arena `settings` olayında).
- "Tohum Doğrulama": eşzamanlı 16,8 s (headless), aralık sabit; `?debug`'a taşı ya da dilimle.
- `computeHint` ana iş parçacığında 1e7 düğüme kadar arıyor (2674-2675 yorumu: en kötü ~2 s). İpucu düğmesinde bir "düşünüyor…" durumu ya da daha düşük düğüm sınırı gerekli (T).
- `DESIGN.md` içinde `file:///D:/...` yerel Windows yolu var (satır 224, 267); bu yerel yollar repoda kalmamalı.
- README "Ultra-lean … zero dependencies" diyor ama dosya 364 KB ve 6152 satır; iddia yumuşatılmalı (kozmetik).

## 8. Önerilen ilk 3 iş
1. **Bölge kartı hatası + kart döngüsünü dürüst yap (§4.1, §7).** Gerçek bir hata, oyuncu kaydını kalıcı bozuyor ve her galibiyette görünen bir modalı ilgilendiriyor. S maliyet, kanıt hazır (D). Doğrulama: `cardcheck.mjs` + tarayıcıda "kart seç → başka haftanın tohumu doğru biome" testi.
2. **İlk deneyim + menü sadeleştirme (§4.2, §4.3).** Tutundurmanın en büyük kaldıracı ilk 30 saniye. Şu an 3 katman ve 24 düğme var (D), portal ve tasarım kaynakları "hemen oynat" diyor (K). `?auto` dalına dokunulmadan yapılabilir.
3. **Wordle tarzı deprem hikâyesi paylaşım satırı (§4.4).** Ucuz (S), günlük döngünün sosyal yayılımını doğrudan artırır (K), motor ve kayıt riskine sıfır yakın.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek Intel UHD dizüstü ve telefonda fps ölçülmedi. Headless swiftshader/yazılım render'ında fps 8-56 arasında oynadı; JS kare maliyeti ise düşük (0,4 ms p50). Menü açıkken düşük kare hızı bu ortama özgü olabilir.
- Doğrulama donmasının gerçek cihazdaki süresi ölçülmedi (yalnız headless 16,8 s).
- Günlük zorluğun gerçek oyuncu için uygunluğu bilinmiyor (oyuncu verisi yok). Telemetri yerel, toplanmıyor.
- Arena-kit seri/pasaport panelinin oyunun seri hapıyla nasıl yan yana göründüğü görsel olarak kontrol edilmedi.
- docs.crazygames.com bu oturumun ağ izinlerinde yok (WebFetch ENOTFOUND); CrazyGames gereksinimleri arama özetinden alındı.
- Ses ve titreşim headless'ta denetlenmedi.

## Kaynaklar
- Kod: `/home/user/fay-hatti/index.html` (satırlar metinde), `tools/sim.mjs`, `tools/cardcheck.mjs`, `DESIGN.md`, `CHANGELOG.md`, `git log`.
- Ekran görüntüleri: `_fay-hatti/02-phone-first-tr.png`, `02b-phone-board-tr.png`, `03-phone-after-move.png`, `05-auto-result.png`; ölçüm: `_fay-hatti/results.json`.
- Josh Wardle, paylaşım ızgarası — https://www.gamedeveloper.com/marketing/josh-wardle-reflects-on-the-the-unconventional-road-to-wordle-s-success
- Wordle yayılım analizi — https://medium.com/ipg-media-lab/five-lessons-that-marketers-can-learn-from-wordle-ad513845378d
- Metin eğitimleri ve oynayarak öğretme — https://gdevelop.io/blog/improve-game-tutorials ; https://www.gamedeveloper.com/game-platforms/tutorial-design-in-puzzledorf-reflections ; https://www.pcgamer.com/how-developers-build-the-tutorials-you-skip
- CrazyGames gereksinimleri — https://docs.crazygames.com/requirements/technical/ ; https://docs.crazygames.com/requirements/gameplay/ (arama özeti) ; Poki — https://sdk.poki.com/requirements
- Game Accessibility Guidelines (atlama/yardım) — https://gameaccessibilityguidelines.com/offer-a-means-to-bypass-gameplay-elements-that-arent-part-of-the-core-mechanic-via-settings-or-in-game-skip-option/ ; IGDA GA-SIG Top Ten — https://igda-gasig.org/?p=42
- Duolingo seri/Streak Freeze — https://blog.duolingo.com/how-duolingo-streak-builds-habit
- NYT Wordle arşivi — https://techcrunch.com/2024/05/07/nyt-games-launches-a-wordle-archive-with-access-to-more-than-1000-past-puzzles/

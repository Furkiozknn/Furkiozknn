# Topkapı Gecesi — faz 3 araştırması

Repo `/home/user/topkapi-gecesi`, HEAD `299e5cd` (origin/main ile eşit), `git status` temiz. Satır numaraları `index.html` (4693 satır) içindir.
Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Çalıştırma: headless Chromium (swiftshader), CDN yerel kopyadan. Makine yükü ölçüm sırasında 70-78 (4 çekirdek), bu yüzden fps ve süre değerleri performans kanıtı sayılmaz. Betik ve çıktılar: `_topkapi-gecesi/` (run.cjs, aim.cjs, core.cjs, res12.json, 01/02/03 png).

## 1. Şu anki durum
- **D** Mimari: saf `CORE` IIFE (1785-2729: ızgara, ışık, görüş, ses, muhafız FSM'si, uzay-zaman A* planlayıcı, bot), ardından Three.js modülü (2732-4691). Sabit adım 1/60 s, kare başına en fazla 12 adım (4612-4631). Kural seti DOM'suz olduğu için node'da çalışıyor (`core.cjs` çıkarıldı, `require` ile koştu).
- **D** İçerik: 3 bölümde 9 görev (1836-2097). Her görevde ipucu, çıkış ya da kaide, isteğe bağlı hedef (lale, mektup, hayalet), hedef süre `par` ve 420 sn şafak sınırı var. Toplam 27 yıldız (sonuç kodu 2299-2303). Yakalanınca son çeşmeye dönülüyor ve muhafızlar sıfırlanıyor (2437-2444).
- **D** Zorluk ve sistemler: 4 muhafız tipi (1794-1799), ışığa göre görüş menzili (2424), şüphe, alarm, arama ve dönüş durumları (2494-2533), arkadaşları çağırma (13 m), söndürülen feneri muhafızın geri yakması (2448-2451). İmza mekaniği Adım Sesi Halkası: NOISE tablosu, duvar sönümü, gıcırtılı tahta (1800-1811, 2155-2184).
- **D** Kayıt: `arena.topkapi.settings|save|best`, `load()` içinde `Object.assign(def, JSON.parse)` ile ileriye uyumlu (2769-2780). `?auto` ve `?nosave` kaydetmiyor.
- **D** Bot: `?auto&low` ile `topkapiSim(150)` sonucu görev 1/2/3 tamam, hepsi `111` yıldız, 0 alarm, 0 hata (30.5 / 64.2 / 28.5 sn). Ekran görüntüsü: `03-auto.png`.
- **D** Arena-kit bağlı: perf (2879), günlük meydan okuma (4330-4335), paylaş, rozet, erişilebilirlik paneli, otomatik duraklatma (4577-4583). Kitin `Arena.hint` ve `Arena.endCard` işlevleri kullanılmıyor (grep).
- **D** Son iki commit dışarıdan, "relay" ile (gemini) geldi ve smoke'tan geçirilmeden main'e birleşti: `5e8e08b` (dokunmatikte otomatik nişanlı taş) ve `e2ae8e1` (PWA service worker ve manifest). İkisi de bozuk, ayrıntı §3'te.
- **D** Dış ağ: Google Fonts ve GoatCounter (`gc.zgo.at/count.js`, 1483, commit 7ca0935 "page counter") her açılışta istek atıyor. Yeni gelen kod ayrıca `sw.js` istiyor ve 404 alıyor.
- **D** Telefon (390×844, dokunmatik) ekran görüntüsü: `02-phone-play.png`. Sanal çubuk ve 6 düğme (56 px) düzgün yerleşiyor, ama üst görev çubuğunun sağ ucu kesiliyor (§3).

## 2. Güçlü yanlar (korunmalı)
- **D** Kurallar ile çizim ayrı ve sim deterministik (`rnd` tohumlu). Bot, testler ve bir gün tekrar oynatma (replay) aynı kodla çalışabilir. Bu ayrım hiçbir öneride bozulmamalı.
- **D** Planlayıcı botu 9/9 görev, 27/27 yıldız ve 0 alarm ile bitiriyor. Böylece her görev "çözülebilir" diye kanıtlanıyor; yeni bir görev ya da kural eklendiğinde aynı kapı kullanılabilir.
- **D** Gizlilik bilgisi okunaklı. Zeminde görüş konileri iki katmanlı (4454), ses halkası görünür, badem göz görünürlük göstergesi var, HUD'da "taş · ses 1.2 m" yazıyor, muhafızın durumunu `?`/`!` simgesi ve müzik temposu bildiriyor. Bu, Mark of the Ninja'nın "okunabilir gizlilik" ilkesiyle örtüşüyor (K: Game Developer, PC Gamer).
- **D** Kademeli fark etme (`sus` 0.3'te şüphe, 1'de alarm), son görülen konuma gitme ve arama durumu, türün kabul görmüş modeliyle aynı (K: GMTK School of Stealth).
- **D** Varlık dosyası yok, ses tamamen Web Audio (4010-), tek dosya. `?low` modu var, telefonda varsayılan kalite düşük (2774).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Telefonda taş atma tamamen bozuk (D, kritik).** `throwPebble()` (3964-3995) modül kapsamında olmayan `S` değişkenini kullanıyor. Doğrusu `G.S`. Adımlar: `?mission=1&nosave&low`, 390×844 hasTouch, tuvale dokun, sonra Taş düğmesine dokun. Sonuç: `pebbles` 3'te kalıyor, `__errs = ["Uncaught ReferenceError: S is not defined"]` (`res12.json`). Hata, eski yoldaki `INP.throwQ = true` satırına inmeden fırlıyor, yani dokunmatikte hiç taş atılamıyor. Bu düzelse bile ikinci bir hata bekliyor: `C.ev` CORE dışına aktarılmıyor (2728'deki return listesinde `ev` yok), bu yüzden `C.ev(...)` TypeError verir (T, kod okuması).
2. **Otomatik nişan tasarım olarak zararlı (D, node simülasyonu).** Kod, oyuncuya en yakın, 1 m'den uzak ve hiçbir koninin içinde olmayan yürünebilir hücreyi seçiyor. Botun 9 görevdeki rotası boyunca 42 örnek aldım: 38'inde taş oyuncunun ≤2.2 m yakınına düşüyor, 23'ünde bir muhafız sesi duyuyor ve oyuncunun dibine yürüyor, 1'inde duvarın öbür yanına atıyor (`aim.cjs`). Bunun yanında: atış CORE'un duvar ışını kontrolünü (2353-2361) atlıyor; saklanırken, duraklatılmışken ya da yakalanma anında da atış yapıyor; bot ve testler bu yolu görmüyor; README'deki "Pebble button (throws ahead)" açıklaması artık yanlış.
3. **PWA eki çalışmıyor ve kısıtları aşıyor (D).** (a) Sayfa her açılışta `sw.js` istiyor ve 404 alıyor; konsolda "A bad HTTP response code (404)…" hatası çıkıyor (3 açılışın 3'ünde görüldü). `tools/smoke.mjs` konsol hatalarını FAIL sayıyor, dolayısıyla smoke CI'ı main'de kırmızı olmalı (T, smoke'u ayrıca koşmadım, aynı dinleyiciyle hatayı gördüm). (b) Blob URL'den service worker kaydı spesifikasyon gereği reddediliyor; hata `catch(()=>{})` ile yutuluyor (K: MDN register()). (c) Manifest blob'a çevriliyor, `icons: []` olduğu için kurulabilir değil (T). (d) Gerçek bir `sw.js` eklense bile önbellek önce kendine bakıyor ve adı sabit `v1`; eski index.html hiç güncellenmez, GoatCounter dahil her yanıtı önbelleğe yazar (T). Tek dosya kuralını da delmiş oluyor.
4. **Telefonda HUD (D, ekran görüntüsü).** 390 px genişlikte görev çubuğu taşıyor ve üçüncü yıldız kesiliyor. Görünürlük paneli yaklaşık 200×162 px ile sol alt çeyreği kaplıyor. "noise 1.2 m" metni 3 satıra bölünüyor. Dikey kamerada başlangıç karesinde hiç muhafız görünmüyor; ekranın çoğu sur dışı boşluk.
5. **Dokunmatikte etkileşim istemi hep `E` gösteriyor (D, 1586: sabit `<kbd>E</kbd>`).** Telefonda "Kullan" düğmesi ya da simgesi gösterilmeli.
6. **Tekrar oynanabilirlik ince (D/T).** 9 görev sabit. Günlük meydan okuma bu 9 görevden birini değişiklik yapmadan seçiyor (4330), en kötü durumda 9 günde bir aynı içerik geliyor. Görev başına en iyi süre kaydediliyor (`PROG.times`, 4300) ama haritada ve brifingde gösterilmiyor (4243-4252). Görevler bitince "sonraki hedef" kalmıyor.
7. **Zorluk ve yardım seçeneği yok (D).** Kitin paneli metin boyutu, kontrast, hareket, titreşim ve otomatik duraklatma sunuyor. Görüş menzili, şafak süresi gibi oyuna özgü ayarlar yok. Erişilebilirlik kılavuzları zorluğun ayarlanabilmesini öneriyor (K: GAG, Xbox XAG 108).
8. **Dış ağ ve veri kuralı (D).** GoatCounter her açılışta sayaç isteği atıyor; brifteki "kullanıcı verisi toplanmaz, harici ağ çağrısı yok" kuralıyla çelişiyor. Bilinçli bir sahip kararı olabilir (§9).
9. **Draw call farkı (D, ama ortam şüpheli).** Başlık ekranında `?low` ile 83 draw call ve 83k üçgen ölçtüm; README başlık ekranı için 39-47 diyor. Swiftshader ve yük altındaki ölçüm olduğu için yalnız açık soru olarak duruyor.

## 4. EKLENMELİ — yüksek değer
**4.1 Dokunmatik taşı sürükleyerek nişanlama (relay ekinin yerine).**
- Ne: Taş düğmesine basılı tut, başparmağını sürükle; zeminde mevcut nişangâh halkası (`WORLD.reticle`, 3801/4507) ve düşüş noktası görünür. Bırakınca atar. Sürüklemeden kısa dokunuş eski davranışı korur ("7 m ileri").
- Neden: Telefonda dikkat dağıtma mekaniği şu an yok (§3.1). Otomatik nişan oyunu bozuyor (§3.2). Erişilebilirlik kılavuzları otomatik nişanı yalnız isteğe bağlı bir yardım olarak öneriyor (K: GAG basic).
- Nasıl: `throwPebble` tümüyle kaldırılır; düğme yalnız `INP.aimTouch = {dx,dy}` yazar, bırakınca `INP.throwQ = true`. `readInput` (3880-3885) hedefi kamera yönüne göre çevirir. Atış yalnız CORE yolundan (`I.throwAt`, 2353) geçer, böylece duvar kontrolü, saklanma ve duraklatma kuralları korunur.
- Maliyet S-M. Risk düşük: CORE'a dokunulmuyor, bot etkilenmiyor, kayıt değişmiyor.
- Kanıt: `res12.json`, `aim.cjs` çıktısı.

**4.2 PWA ekini geri al.**
- Ne: 1697 sonrasındaki SW/manifest bloğunu ve `<link rel="manifest" href="manifest.json">` satırını kaldır.
- Neden: §3.3; tek dosya ve "harici ağ yok" kısıtlarını aşıyor, smoke'u kırıyor.
- Maliyet S. Risk yok.
- Not: Çevrimdışı oynama gerçekten isteniyorsa ayrı bir `sw.js` dosyası, sürümlü önbellek ve önce ağ stratejisi gerekir; bu da kısıtı aşar (§6).

**4.3 Görev başına kişisel rekor ve "gölge" hedef.**
- Ne: Harita brifinginde ve sonuç ekranında görev başına en iyi süre gösterilsin (`PROG.times` zaten tutuluyor). Görev sırasında HUD'da hedef süreye ve rekora göre ±fark yazsın.
- Neden: 27 yıldızdan sonra oyuncuya yeni hedef kalmıyor. Sürat koşusu kitlesi sabit düzenli gizlilik oyunlarında doğal tutundurma kaynağı (T).
- Nasıl: `buildMap` 4252'ye bir satır, `fillResult`'a rekor farkı, HUD'a küçük bir metin. Kayıt biçimi değişmez.
- Maliyet S. Risk yok.

**4.4 Günün meydan okumasına deterministik "gece koşulu".**
- Ne: Günün tohumuna göre görev ile birlikte bir koşul seçilsin: "çakıl yok", "tüm fenerler yanık ve söndürülemez", "kedi iki kat", "şafak 4 dk", "muhafızlar %15 hızlı".
- Neden: Şu an günlük mod 9 içeriğin tekrarı (§3.6). Günlük koşul, aynı haritayı yeni bir bulmacaya çeviriyor (T).
- Nasıl: `newSim(idx, opts)` zaten `opts` alıyor (2240) ama kullanmıyor. Koşullar CORE'da `opts.mod` olarak uygulanır (GT kopyası, limit, `pebbles`). Bot aynı sim ile plan yaptığı için uyumlu kalır. Kampanya kaydına dokunulmaz (4296'daki mevcut ayrım).
- Doğrulama: her koşul × 9 görev node'da botla koşulur; çözülemeyen kombinasyon listeden çıkarılır.
- Maliyet M. Risk: çözülemeyen kombinasyon; bot kapısı bunu yakalar.

**4.5 Telefon HUD sıkılaştırma.**
- Ne: 390 px'te görev çubuğu iki satıra insin ya da yıldızlar ayrı satıra geçsin. Görünürlük paneli göz ve tek satıra küçülsün ("taş · 1.2 m"). Dokunmatikte istemde `E` yerine el simgesi gösterilsin. Dikey kamerada muhafızları gösterecek kadar uzaklaşılsın (3897'deki katsayı) ya da ekran dışındaki muhafız için kenarda ok gösterilsin.
- Neden: §3.4, §3.5. Portallar telefonda dokunmatik ve dikey düzen bekliyor (K: CrazyGames teknik gereksinimleri).
- Maliyet S-M. Risk: CSS gerilemesi; 390×844, 844×390 ve 1280×720 ekran görüntüleriyle kontrol edilmeli.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Son görülen konum hayaleti (S):** Muhafız alarm ya da arama durumundayken `g.tx/tz` noktasına soluk bir oyuncu silueti çizilsin. Splinter Cell ve Mark of the Ninja'daki ipucunun karşılığı (K: GMTK transkripti, Game Developer). Yalnız görsel değişiklik; CORE'a dokunmaz.
- **Yardım ayarları (M):** "Muhafız görüşü −%20", "şafak +2 dk", "yakalanınca ceza yok". Kılavuzlar bunu öneriyor (K: GAG, XAG 108). Yardımla alınan sonuç ayrı işaretlenmeli; "Görünmeden" yıldızı ve rekor sayılmamalı. Risk: kayıtta bayrak alanı gerekir; ileriye uyumlu biçimde eklenebilir.
- **Kendi en iyi koşunun tekrarı (M-L):** Sim deterministik olduğu için girişleri kaydedip "dünkü ben" hayaleti oynatılabilir. Değeri yüksek, ama girdi kaydı localStorage'da 7 dakikaya kadar yer tutar (T). İlk 3 iş bittikten sonra düşünülmeli.
- **İlk 30 saniye ipuçları için `Arena.hint` (S):** Görev 1'de "çömel", "gölge", "taşı muhafızın arkasına at" gibi tek seferlik ipuçları. Kitte hazır, kullanılmıyor.
- **Sonraki hedef satırı (S):** Sonuç ekranında eksik yıldız için tek cümle ("Hayalet ol: kediye görünme").

## 6. EKLENMEMELİ
- **Blob service worker / PWA:** Spesifikasyon blob SW'yi yasaklıyor (K: MDN). Gerçek bir SW ayrı dosya ister, tek dosya kuralını aşar. Sabit önbellek eski sürümü kilitler.
- **En yakın güvenli hücreye otomatik taş:** Ölçülen etki ters; muhafızı oyuncuya çekiyor (§3.2).
- **Çevrimiçi skor tablosu, hesap, bulut kayıt:** Sunucu ve hesap kısıtını aşar.
- **Prosedürel ya da rastgele haritalar:** El yapımı rota ve zamanlama tasarımı, `par` değerleri ve botun 27/27 kanıtı anlamını yitirir. Günlük çeşitlilik §4.4'teki koşullarla sağlanabilir.
- **Muhafızları etkisiz bırakma ya da dövüş:** Tonu (çocuk iç oğlanı, "kimse bir şey görmedi") ve ışık-ses bulmacasını bozar.
- **Ağır post-processing (bloom, SSAO), dinamik nokta ışık gölgeleri:** UHD dizüstünde ve telefonda kare hızını riske atar. Fener ışığı bilinçli olarak pişirilmiş (README).
- **Gerçek oyunlardan isim, karakter ya da sanat** (örn. tanınır bir suikastçı serisi teması): kopya kuralı.

## 7. Düzeltilmeli
- `throwPebble` içindeki `S` → `G.S` ve `C.ev`; tercihen tüm bloğu kaldır (§4.1). **D**
- `sw.js` 404 ve konsol hatası; manifest bağlantısı (§4.2). **D**
- README'deki "Pebble button" satırını yeni davranışa göre güncelle. **D**
- Telefonda kesilen yıldızlar, 3 satırlık ses metni, `E` istemi (§4.5). **D**
- Oyun toast'ları (`#toasts`, 1600) `aria-live` taşımıyor; kitin canlı bölgesi yalnız kendi metinleri için (1317). `role="status"` eklenebilir. **D**
- `.redflash.on` kenar parlaması (1099) azaltılmış harekette de kalıyor, yalnız geçişi kapanıyor (1104). Tam ekran flaş değil, ama kontrol edilmeli. **T**
- Relay birleştirmeleri (`verify_merge.py`) smoke'u koşmadan main'e girdi. Süreç sorunu; birleştirmeden önce `node tools/smoke.mjs` ve `?auto` dokunmatik testi zorunlu olmalı. **D** (commit geçmişi, hata)

## 8. Önerilen ilk 3 iş
1. **Relay eklerini temizle ve dokunmatik taşı geri getir:** PWA bloğunu sil, `throwPebble`'ı kaldır, geçici olarak eski "ileri at" yoluna dön. En kritik iş bu: telefonda temel bir mekanik şu an çalışmıyor ve smoke kırmızı olmalı. Maliyet S. Kanıt kapısı: smoke chromium 0 hata, dokunmatik testte `pebbles` 3→2 ve `__errs` boş.
2. **Sürükleyerek nişanlama (§4.1) ve telefon HUD sıkılaştırma (§4.5):** Dokunmatik oyuncu için dikkat dağıtma mekaniğini gerçekten kullanılabilir yapar. CORE'a dokunmaz, bot ve kayıt güvende kalır.
3. **Günlük gece koşulu (§4.4) ve rekor gösterimi (§4.3):** 27 yıldızdan sonra tutundurmanın tek kaynağı günlük mod; ona içerik verir. CORE'daki `opts` kancası hazır, bot kapısı her kombinasyonu doğrular.

## 9. Doğrulanmayanlar / açık sorular
- `tools/smoke.mjs`'i bu turda koşmadım (makine yükü). FAIL vereceği çıkarım: aynı konsol hatası dinleyicisiyle 404 hatasını gördüm.
- Fps, hazır olma süresi (43.8 sn) ve draw call değerleri swiftshader'da, yük 70+ altında ölçüldü. Gerçek UHD ya da telefonda ölçülmedi.
- `?auto` yalnız ilk 3 görev için tarayıcıda koşuldu (hepsi 111). 9/9 sonucu son commit mesajından alındı; relay commit'leri CORE'a dokunmadığı için değişmemiş olmalı (T).
- GoatCounter sayacı sahibin bilinçli kararı mı? Brifteki "veri yok / dış ağ yok" kuralıyla çelişiyor; karar sahibinde.
- Gerçek iOS Safari'de `pointerdown` ile `preventDefault` ve çift dokunuşla yakınlaştırma davranışı test edilmedi.
- Otomatik nişan analizi, botun rotasındaki anlara göre yapıldı. İnsan oyuncunun durduğu yerlerde dağılım farklı olabilir; ama algoritma her durumda en yakın hücreyi seçiyor (D, kod).

## Kaynaklar
- MDN, ServiceWorkerContainer.register(): https://developer.mozilla.org/docs/Web/API/ServiceWorkerContainer/register
- W3C public-webapps (blob SW yasağı tartışması): https://lists.w3.org/Archives/Public/public-webapps-github/2015Nov/0332.html
- Mark of the Ninja'nın beş gizlilik kuralı: https://gamedeveloper.com/design/-i-mark-of-the-ninja-i-s-five-stealth-design-rules
- PC Gamer, Nels Anderson gizlilik kuralları: https://pcgamer.com/stealth-game-design-mark-of-the-ninja
- Designing Sound, Mark of the Ninja ses dinamikleri: https://designingsound.org/2013/06/the-dynamics-of-mark-of-the-ninja
- GMTK School of Stealth bölüm 1 (transkript): https://amara.org/subtitles/4SwBdOk0E4LH/en/1/download/How%20Stealth%20Game%20Guards%20See%20and%20Hear%20%20School%20of%20Stealth%20Part%201.en.txt
- GMTK transkriptleri (son görülen konum): https://huggingface.co/datasets/taesiri/GMTK-Transcripts/viewer/default/train?p=24
- Game Accessibility Guidelines, orta düzey: https://gameaccessibilityguidelines.com/intermediate/
- Xbox Accessibility Guideline 108 (zorluk seçenekleri): https://devdocs.xbox.com/gaming/accessibility/xbox-accessibility-guidelines/108
- PC Gamer, erişilebilirlik ve kolay mod: https://www.pcgamer.com/accessibility-means-more-than-just-an-easy-mode
- CrazyGames teknik gereksinimler: https://docs.crazygames.com/requirements/technical/
- CrazyGames oynanış gereksinimleri: https://docs.crazygames.com/requirements/gameplay/
- CrazyGames ilk kareye ulaşma: https://docs.crazygames.com/resources/getting-to-the-first-frame/

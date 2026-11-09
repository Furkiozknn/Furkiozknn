# Martı — faz 3 araştırması

Repo: `/home/user/marti` @ `654f388` (origin/main). Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Çalıştırma: headless Chromium (swiftshader), CDN yerelden, 3 bağlam (masaüstü 960×600, `?auto` sim, telefon 390×844 dokunmatik). Makine yük ortalaması 35-48 idi (4 çekirdek); **gerçek zamanlı FPS ve dokunma süreleri bu yüzden güvenilmez**, sim (`martiSim`) ve kod okuması belirleyici kanıttır. Betik + çıktılar: `_marti/run.js`, `_marti/result.json`, `_marti/*.png`.

## 1. Şu anki durum
- **D** Son 3 commit, bugünkü arena-kit/imza işinden *sonra* gelen "relay" (gemini-3.5-flash-lite) değişiklikleri: dokunmatik dalış (`9e3315b`), ölüm sebebi + ipucu (`2acda2c`), PWA/Service Worker (`b5f982e`). Üçü de doğrudan main'e birleşmiş; üçünde de hata var (bkz. §3).
- **D** Döngü: `renderFrame` (3958) → `frameLogic` (2967) → `simStep` (2881, dt ≤ 0,05 s). Hız `baseSpeed` 27→58 (2387), zorluk `diffK` 30-180 s (2388), geç rampa `lateK` 180-420 s (2390).
- **D** İlerleme: 3 tüy + enerji (2950), kombo x5'e kadar (2492), sürü (imza mekaniği, 2393-2491, 12 martı, x1,30), çatı yuvası → yavru 4 evre (2806-2829, `META.chick`), günlük 3 görev / 5 tanımdan (1625, 3426).
- **D** Kayıt: `arena.marti.settings|best|save` (1604), eski `marti.*` anahtarları bir kez taşınıyor (1608-1617). Koşu geçmişi (`S.runs`) kalıcı değil; yüksek skorlar sebep saklamıyor → yeni sebep anahtarları eski kayıtları bozmaz.
- **D** Bot: `botThink` (3286) 0,3 s'de bir aday şerit seçer, **hiç dalmaz** (3332). `?auto&noassets` + `martiSim(900)`: 1 koşu, 323,5 s, 17,3 km, 28 134 puan, sebep `ship`, sayfa hatası 0 (yalnız sw.js 404 + AudioContext uyarısı).
- **D** i18n: TR/EN `I18N` (1516-1585), `tx` eksik anahtarda `undefined` döndürür (1623).
- **D** Mobil: dokunmatik göreli sürükleme ile yön (3233), kaba işaretçide kalite varsayılan `low` (1607). 390×844'te yatay taşma yok (scrollWidth 390).
- **D** Ses: Web Audio ile sentez müzik (124 BPM) ve efekt (3473-3660); harici ses dosyası yok.
- **D** Performans: masaüstü ilk kare 32 draw call, 45k üçgen (debug HUD ekran görüntüsü). FPS ölçümü yük yüzünden geçersiz (oyun içi t 6 sn duvar saatinde 0,2 s ilerledi).
- **D** Harici çağrılar: GoatCounter analitik (4068, v2'den beri, `22f06c8`) ve Google Fonts (preconnect + stylesheet); `smoke.mjs` ikisini de bilerek yok sayıyor.

## 2. Güçlü yanlar (korunmalı)
- Güçlü yer kimliği: Boğaz, köprü, Galata/Kız Kulesi, vapurdan simit, sürü; afternoon→gün batımı→havai fişek gecesi döngüsü (D, ekran görüntüsü).
- Oturumlar arası bağ: yavru 4 evre ve stage 4'te yanında uçan, bir darbe alan genç martı (D, 2825, 3346). Bu tür "kalıcı arkadaş" sonsuz koşucuda nadir; korunmalı.
- Sürü mekaniği risk/ödül dengesi: büyüdükçe uçurtma ipini koparır, rakipleri kovar, darbede %40 dağılır (D, 2394-2440).
- Adil erken oyun: ilk 30 sn uçurtma/sürü/fırtına yok (D, 2553-2562); ipuçları bir kez ve yalnız insan oyuncuda (3768).
- Test kancaları zengin: `?auto ?sim ?debug ?t0 ?chick ?noassets ?run`, `window.martiSim`; bot hatasız 5+ dk uçuyor (D).
- Erişilebilirlik temeli: odak yönetimi (3836), aria-label'lar (3690), arena-kit paneli, CDN yüklenemezse açıklayıcı mesaj (1450).
- Günlük rota `SRND` ile tohumlu (1482) → herkes aynı rotayı uçar.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **KRİTİK: Alçakta dalmak anında oyunu bitiriyor (tüy/kalkan/yavru yok sayılır).** `checkHits` başına `if (G.y <= 1.8) return gameOver('water')` eklenmiş (2681). Ama `G.y` tasarım gereği `YMIN-1 = 1,4`'e kadar iniyor (2904, 2908): dalış hedefi `tyBase − 9`. Yani `tyBase < ~10,8` iken dalan her oyuncu ölür. Oyun ise balık için dalmayı açıkça istiyor (1521, 1539; balık tepe y 4,5-10, 2599) ve su sıçraması efekti `G.y < 2.6`'da dalış bekliyor (2957).
   *Adım (D):* `?run&noassets&lang=en` → `marti.tyBase = 8; marti.diveHold = true; martiSim(3)` → koşu **t = 0,8 s'de** `reason: "water"` ile bitti, `lives: 3` (hiç tüy kaybetmeden). Karşılaştırma: `tyBase = 12` + dalış → `G.y` min 3,0, koşu sürdü (D). Bot dalmadığı için `?auto` testleri bunu **yakalamıyor** (D, 3332).
2. **Ölüm kartında "undefined".** Yeni sebepler (`water`, `cable`, `ship`, `kite`, `obstacle`) için `I18N` anahtarı yok; `tx()` `undefined` döndürür. *D:* kart metni `"undefined — Tip: Do not get too close to the water surface."`. Son tüy kablo/gemi/uçurtmada giderse de aynı (önceden "Üç kez çarptın"). `stamina` sebebi HUD etiketi "Enerji/Stamina"yı gösterir ("Enerjin bitti" yerine) (D, kod). Dil değiştirince `applyLang` (3711) ipucunu siler (T, kod; tarayıcıda boş kartta denendi, kesin değil).
3. **Service Worker eklemesi işlevsiz ve zararlı.** (a) `./sw.js` ve `manifest.webmanifest` repoda yok (D, `ls`); sayfa her açılışta **konsol hatası** veriyor: "A bad HTTP response code (404) was received when fetching the script." (D, 3 bağlamın hepsinde). `tools/smoke.mjs` konsol hatasında `load` adımını FAIL eder → smoke CI kırmızı olur (T; mantık D, smoke'u ayrıca koşmadım). (b) Blob URL ile kayıt tarayıcıda reddediliyor: `TypeError: ... The URL protocol of the script ('blob:...') is not supported.` (D; K: MDN, W3C). (c) Çalışsaydı bile cache-first strateji, sürüm adı sabit `marti-v1` ile oyuncuları eski `index.html`'de dondururdu (T). Kısıtı aşar (tek dosya; eklenen ama olmayan iki dosyaya bağımlılık).
4. **Dokunmatik dalış bozuldu.** `9e3315b` sonrası (3240-3281): (a) Kısa dokunuş (<150 ms) artık dalmıyor; eski kural "<350 ms ve <12 px hareket = dalış"tı (D, kod; çalışmada yük yüzünden "hızlı" dokunuş 514 ms sürdü, çalışma zamanında doğrulanamadı). Oysa ipucu metni hâlâ "dokun" diyor (1539). (b) 150 ms'den uzun ve 25 px'ten kısa her sürükleme dalışa dönüşüyor: 20 px'lik yön sürüklemesi `diveTimer 0.8` verdi (D). Alçakta ince ayar yapan oyuncu → §3.1 ile birleşince anında ölüm (T). (c) "Sağ alt dalış bölgesi" görünmez ve arena-kit ♿ düğmesiyle (340,794,40×40) çakışıyor: sağ alta dokunmak oyunu duraklatıp erişilebilirlik panelini açtı (D, `phone_play.png`). Kod yorumu (4043) "o köşede oyun kontrolü yok" diyor.
5. **Hareketi azalt ayarı kamerayı etkilemiyor.** Kamera sarsıntısı (3120-3123), hız çizgileri, fırtına itmesi `Arena.settings.reducedMotion`'ı okumuyor; ayar yalnız CSS animasyonlarını kısıyor (D, grep). K: Xbox AG 117 kamera sarsıntısının kapatılabilmesini öneriyor.
6. **Günlük rota tam tohumlu değil.** Geç rampa rüzgârının zamanlaması/yönü `rnd`/`Math.random` (3777, 3782) → günlükte oyuncular farklı rüzgâr görür (D, kod). Küçük adalet sorunu.
7. **Harici analitik kısıtla çelişiyor.** GoatCounter (4068) "kullanıcı verisi toplanmaz / harici ağ çağrısı yok" kısıtının lafzına aykırı (çerezsiz olsa da sayfa görüntülemesi gönderiyor). Sahibinin bilinçli kararı olabilir → §9.
8. **Telefon başlık kartı uzun.** 390×844'te "Günün Meydan Okuması" düğmesi y=804-848, ekranın altında kesiliyor; kart dört kutulu talimat metniyle dolu (D, `phone_title.png`). Poki: ilk kez gelene başlık/menü engeli azaltılmalı (K).
9. **Görev çeşitliliği dar.** 5 tanımdan her gün 3'ü (1625) → aynı görevler sık tekrar eder; imza mekaniği (sürü), yuva, near-miss için görev yok (D).
10. `S.deathCause` yazılıyor ama hiç okunmuyor (2953, 3385) — ölü kod (D).

## 4. EKLENMELİ — yüksek değer
**4.1 Görünür dalış düğmesi + "dokun = dal" geri dönüşü (telefon)**
- Ne: Sol altta (♿ düğmesinden uzak) yarı saydam, ≥56 px "Dal" düğmesi; basılı tutunca `diveHold`. Ekranın geri kalanında eski kural: kısa dokunuş (<300 ms, <12 px) = 0,8 s dalış, sürükleme = yalnız yön.
- Neden: Bugünkü görünmez bölge keşfedilemez ve duraklatma düğmesiyle çakışıyor (§3.4). Tek dokunuşlu koşucularda kontrolün "beklendiği anda" tepki vermesi tutundurmanın çekirdeği (K: Game Developer 1TER, dev.to Echo Runner).
- Nasıl: `#diveBtn` (yalnız `pointer:coarse`), `isUI` zaten butonları dışlıyor; pointerdown/up'ta `S.diveHold`. 3244-3278 eski mantığa döner. `?auto` etkilenmez.
- Maliyet S · Risk: düşük (HUD yerleşimi; güvenli alan `env(safe-area-inset-bottom)`).

**4.2 Doğru yapılmış "koşu özeti" (ölüm sebebi + tek ipucu)**
- Ne: Mevcut `DEATH_TIPS` altyapısını düzelt: her sebebe TR/EN etiket ("Köprü kablosuna çarptın", "Gemi direğine çarptın"…), son darbenin sebebi; ipucu `applyLang`'da da yenilenir. Ek olarak kartta "yakın geçiş N · en büyük sürü N" satırı (veri zaten `run`/`S`'de).
- Neden: Haksız hissettiren kayıp tutundurmayı düşürür; neden öldüğünü bilmek "bir daha" isteğini artırır (K: dev.to fizik/adalet yazısı — nicel veri yok).
- Nasıl: `I18N` + `reasons` sözlüğü, `tx` yerine güvenli `reasonText(run)`; `hitPlayer(cause)` korunur, `water` kaldırılır (§7.1).
- Maliyet S · Risk: yok; eski kayıtlar sebep tutmuyor.

**4.3 Günlük rotada "dünkü/en iyi martı" hayaleti**
- Ne: Günün Meydan Okumasında oyuncunun o günkü en iyi koşusunun yolunu yarı saydam bir martı olarak çiz (yalnız yerel, kendi koşusu).
- Neden: Günlük modda şu an kovalanacak görünür bir hedef yok; hayalet "nerede daha iyi yapabilirim"i gösterir (K: itch.io daily-seed/ghost tartışmaları — oyuncu talebi, anekdot).
- Nasıl: Girdi tekrarı değil (dt değişken, rüzgâr tohumsuz) **konum örneklemesi**: her 4 m'de `(x,y)` → Int8 ölçekli, ~17 km'de ~4k örnek ≈ 8 KB, base64 ile `arena.marti.save.ghost = {day, d[]}`; yalnız aynı `S.daily` gününde kullan, ertesi gün sil. Çizim: mevcut `WM` havuzundan bir martı (instanced, ek draw call yok ya da +1).
- Maliyet M · Risk: kayıt boyutu (küçük), alçak uçuşta görsel kalabalık; botta kapalı tut. §3.6 (rüzgâr tohumu) önce çözülmeli.

**4.4 Hareketi azalt → oyun içi hareket + dokunsal geri bildirim**
- Ne: `Arena.settings.reducedMotion` açıkken kamera sarsıntısı 0, hız çizgileri ve FOV genişlemesi yarıya; darbede `navigator.vibrate(60)` (arena-kit titreşim ayarını zaten sarmalıyor, 170).
- Neden: K: Xbox AG 117; Candy Crush/LEGO örnekleri. Telefon oyuncusu için çarpışma hissi.
- Maliyet S · Risk: yok.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Görev havuzunu genişlet** (5 → ~9): "sürüne 6 martı kat", "bir yavruyu besle", "5 yakın geçiş", "bir uçurtma ipini sürüyle kopar". Veri hazır (`S.flockMax`, `S.feeds`, `S.nearMiss`, `S.kitesCut`). S. Risk: `META.p` biçimi aynı kalır, eski kayıt uyumlu.
- **Telefonda kısa başlık kartı:** talimat kutularını tek satır ikonlu özete indir, Başla + Günlük ilk ekranda; ayrıntı "Nasıl oynanır" açılırında. K: Poki ilk oynamada menü sürtünmesini azaltmayı öneriyor. S.
- **Yavru için isim/kıyafet yok — yalnız ilerleme göstergesi:** başlık kartında "sonraki evreye 3 besleme". S, düşük risk.
- **Gece bölümüne küçük olay:** vapur düdüğü + havai fişek sırasında 10 sn'lik "ışıklı simit" serisi (mevcut altın simit ağını yeniden kullanır). M; performans: yeni geometri yok.
- **Erken koşu için "sakin kıyı" sinyali:** ilk koşuda alçak dalışı göstermek için tek balık sürüsünü merkeze koy (tutRing gibi). S. Koşul: §7.1 düzeltilmeden eklenmemeli.

## 6. EKLENMEMELİ
- **Service Worker / PWA çevrimdışı önbellek:** tek dosya kısıtını aşar (ayrı `sw.js`, manifest), blob kaydı imkânsız (K, D), cache-first güncellemeleri dondurur. GitHub Pages + CDN modülleriyle zaten çevrimdışı tam çalışmaz.
- **Suya değince anında ölüm** ya da tüy sistemini atlayan her yeni "anında bitiş": oyunun dalış mekaniğini cezalandırır (§3.1).
- **Görünmez dokunma bölgeleri:** keşfedilemez, sistem/kit düğmeleriyle çakışır (D).
- **Çevrimiçi skor tablosu / hesap / hayaletin paylaşılması:** sunucu ister, kısıtı aşar (K: hayalet tabloları sunucu doğrulaması gerektiriyor).
- **Jiroskop/eğme kontrolü:** iOS izin istemi, mide bulantısı riski, dikey tutuşta yorucu (T).
- **Kalıcı yükseltme dükkânı / para birimi:** skor dengesini ve günlük adaleti bozar, yavru-sürü ilerlemesini gölgeler (T).
- **Daha fazla engel türü** (helikopter, köprü inşaatı vb.) — kontroller düzelmeden zorluk eklemek kayıpları "haksız" kılar (T). Ayrıca gerçek bir oyunun karakter/bölümünü taklit eden temalar.
- **Ek analitik/izleme** (zaten GoatCounter var; §9).

## 7. Düzeltilmeli
1. `index.html:2681` `G.y <= 1.8 → gameOver('water')` satırını kaldır (ya da `YMIN-1` altını yalnız görsel sıçrama say). Regresyon testi: `?run&noassets` + `tyBase=8, diveHold=true, martiSim(3)` → `state === 'playing'`.
2. Ölüm sebebi metinleri: I18N'e `water|cable|ship|kite|obstacle` (ya da sebebi `crash`'e eşle), `stamina` için "Enerjin bitti"; `applyLang` (3711) ipucunu da yazsın. Kullanılmayan `S.deathCause` kaldırılsın.
3. `index.html:16` manifest linki ve 4069-4097 iki SW betiğini sil (404 konsol hatası, smoke FAIL riski).
4. Dokunmatik: 3244-3278'de sağ alt bölgeyi kaldır, eski "kısa dokunuş = dalış" eşiğini geri getir (§4.1); `hDive` metni ile davranış uyumlu olsun.
5. `gustTick` (3777, 3782) günlükte `SRND` kullansın (efektler `Math.random` kalabilir).
6. Kamera sarsıntısı `reducedMotion`'a bağlansın (3120).
7. Telefon başlık kartında Günlük düğmesi ekran içine (y < 844) alınsın.
8. Süreç: relay commit'leri PR + smoke olmadan main'e girmiş (`654f388` "verified by verify_merge.py"); bu doğrulama üç hatayı da kaçırdı. Bot dalmadığı için bir "dalış senaryosu" sim testi eklenmeli (ör. `?auto&dive` ile botun balığa dalması).

## 8. Önerilen ilk 3 iş
1. **Relay regresyonlarını geri al/düzelt (§7.1-7.3):** anında su ölümü, "undefined" ölüm kartı, SW/manifest 404. En yüksek oyuncu etkisi (her dalan oyuncu ilk saniyelerde ölebilir), maliyet S, risk yok; smoke CI'yı yeşile döndürür. Kanıt: `waterSim` (lives 3, t 0,8 s), kart metni, 404 konsol hatası.
2. **Dokunmatik dalışı düzelt + görünür dalış düğmesi (§4.1, §7.4):** telefon ana platformlardan biri; bugünkü sağ alt bölge oyunu duraklatıyor (D). S.
3. **Koşu özeti + reducedMotion/titreşim (§4.2, §4.4):** 1. iş sırasında dokunulan kodun hemen yanında, ucuz, kayıp hissini adilleştirir ve erişilebilirlik açığını kapatır. Ardından (4.) günlük hayalet (§4.3), önce rüzgâr tohumu (§7.5).

## 9. Doğrulanmayanlar / açık sorular
- Gerçek FPS (Intel UHD hedefi) ölçülemedi: makine yükü 35-48; ölçülen 20-27 FPS geçersiz. README'deki 60 FPS iddiası bu turda teyit edilmedi.
- Kısa dokunuşun (<150 ms) dalmaması kod okumasından (D-kod); CDP dokunuşları yük altında 514 ms sürdü, çalışma zamanında doğrulanamadı.
- `tools/smoke.mjs` ayrıca koşulmadı (tools/node_modules yok); FAIL tahmini, gözlenen konsol hatasına ve smoke'un kuralına dayanıyor.
- GoatCounter ve Google Fonts kısıtla çelişiyor mu, yoksa bilinçli istisna mı? Sahibi karar vermeli.
- Klavye ile su ölümü gerçek zamanlı denemesi yük yüzünden sonuçsuz kaldı (oyun saati ~0,2 s ilerledi); deterministik sim kanıtı yeterli kabul edildi.
- Firefox/WebKit'te davranış denenmedi (yalnız Chromium).
- Dil değiştirince ölüm kartındaki ipucunun silinmesi kodla gösterildi, ekranda değil.

## Kaynaklar
- MDN, ServiceWorkerContainer.register(): https://developer.mozilla.org/docs/Web/API/ServiceWorkerContainer/register
- W3C webapps (blob URL SW betiği olamaz): https://lists.w3.org/Archives/Public/public-webapps-github/2015Nov/0332.html
- Xbox Accessibility Guideline 117 (kamera sarsıntısı/hareket): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117
- Coherent Labs, Motion sickness & reduced motion: https://guide.coherent-labs.com/polishing/localization--accessibility/accessibility/motion-sickness/
- Game Developer, Endless runner design (1TER): https://www.gamedeveloper.com/disciplines/endless-runner-games-how-to-think-and-design-plus-some-history-
- dev.to, Echo Runner (girdi tepkisi, öğreticisiz başlangıç): https://dev.to/getinfotoyou/the-architecture-of-simplicity-building-echo-runner-for-android-3f5i
- dev.to, fizik ve tutundurma (anekdot): https://dev.to/krishanvijay/how-game-physics-shape-player-engagement-in-casual-mobile-games-58c7
- Poki for Developers, easy access (başlık ekranını atla, dikey): https://developers.poki.com/guide/easy-access
- Poki requirements: https://sdk.poki.com/requirements
- Günlük tohum / hayalet tartışmaları: https://dev.to/yurukusa/5-lines-of-code-that-made-my-roguelike-worth-playing-every-day-3klj , https://itch.io/post/13549748

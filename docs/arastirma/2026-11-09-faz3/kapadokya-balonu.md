# Kapadokya Balonu — faz 3 araştırması

Kapsam: `/home/user/kapadokya-balonu` @ f230a4e (origin/main ile aynı, `git status` temiz kaldı). `index.html` 5222 satır / 296 KB.
Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak. Geçici dosyalar ve ekran görüntüleri:
`/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_kapadokya-balonu/`
(`probe.cjs`, `core.cjs`, `res-*.json`, `desktop-burning.png`, `desktop-flight.png`, `phone-flight.png`, `phone-title.png`, `phone-vf.png`).

## 1. Şu anki durum
- **D** Mimari: simülasyon çekirdeği (`CORE`, satır 2297-2857) DOM'suz, sabit adımlı (1/30 s, `stepFixed` 3924, `update` 5054). Fizik: zarf sıcaklığı → kaldırma, 3,5 s gecikme (`P`, 2547; `physStep` 2563). Rüzgâr 4 katman, katman geçişi ±10 m'de yumuşak (`windAt` 2530). Render-side: pibal, rüzgâr kılavuzu, ani esinti uyarısı, Altın Saat vizörü.
- **D** İlerleme: 3 bölgede 12 uçuş (`FLIGHTS` 2334), 5 hedef türü, uçuş başına 3 yıldız (hedefler, yakıt eşiği, iniş puanı ≥65; `finish` 2655). Kilit doğrusal (`unlocked` 4062). 3. uçuştan itibaren üst katmanlar `?` ile gizli (`hiddenLayers` 3721).
- **D** Kayıt: `arena.kapadokya.{settings,save,best,daily,album}`, `load()` `Object.assign(def, parsed)` ile eksik alanları varsayılanla doldurur (2896). Eski biçimli bir kayıtla (notes/haptics/album yok, `lang:'en'`) açtım: 0 hata, "Continue" göründü, "Best: 6/36 · 3/12" yazdı, koç kapalıydı (`res-oldsave.json`).
- **D** Bot: Node'da CORE'u ayrıca çalıştırdım, 12/12 uçuş, 36/36 yıldız, hasar 0. Uçuş süreleri 122-424 sim-s, toplam 215 s duvar saati (`core.cjs`). Tarayıcıda `?auto&low` ile 3. uçuşa kadar izledim: 1. uçuş 91 puan, 2. uçuş 77 puan, Node ile birebir aynı ve 0 hata.
- **D** İlk 30 saniye (1280×800, headless + swiftshader): başlıkta Play 14-17 s sonra etkin oluyor (yazılım GL'de; gerçek GPU'da ölçmedim). Play ile tek tıkta 1. uçuş başlıyor. 4 adımlı koç şeridi açılıyor, sağda hedef paneli, solda rüzgâr merdiveni. Sürekli brülörde **kalkış 6,6 s, 50 m AGL'ye çıkış 17,9 s** (Node). Konsolda yalnız swiftshader uyarısı var, sayfa hatası 0.
- **D** Telefon 390×844 (touch): yatay taşma yok (scrollW 390). Brülör 78×46 px, supap 56×46 px. Koç şeridi alt panelin üstüne yerleşiyor. Örtüşme var, bkz. §3.
- **D** Performans: low kalitede 29-33 çizim çağrısı, ~146k üçgen (`exportState` alanları). README'deki "36k terrain triangles" yalnız arazinin üçgenleri. Kalite ayarı pixel ratio ≤1,5 ve gölge açma/kapama. Arena.perf bağlı (3070).
- **D** i18n: TR/EN sözlüğü 2950-3060, `data-t`/`data-tt` ile uygulanıyor (`applyTexts` 4730). İkon düğmelerine `aria-label` veriliyor.
- **D** Ses: tamamen Web Audio (Uşşak benzeri tel, 9/8 aksak, drone, uzak ezan pad'i). Gizli sekmede ses ve döngü askıya alınıyor (5192 civarı, `frame` 5204).
- **D** Son iki commit Gemini relay'inden geliyor ve ikisi de denetimsiz: `02a1f07` titreşim, `7c7e51c` zarf parlaması. Altın Saat (K) README'de hiç geçmiyor (`grep -ci golden README.md` = 0).

## 2. Güçlü yanlar (korunmalı)
- Asıl mekanik özgün ve öğretici: dümen yok, yalnız dikey kontrol, yön seçimi rüzgâr katmanıyla. Merdivende "yeşil ok = hedefe eser" ipucu (4232) gerçek balon pilotluğunu sadeleştiriyor. **K** Aynı türdeki Windward Balloon da bantları ve kenar oklarını görünür yapıyor (dinogame.gg), yani yön doğru.
- Çekirdek DOM'suz ve deterministik. Bot oyuncuyla aynı girdilerle uçuyor; Node'da test edilebilir. Bu, gelecekteki her denge değişikliğinin ölçülebilmesini sağlıyor.
- Koç adımları süreyle değil gerçek girdiyle işaretleniyor (`coachStep` 3964). Bu, FTUE için iyi uygulama (**K** Roblox onboarding: "teach through play").
- Bilgi okunaklı: ladder, pusula, hedef oku, `hover`/ısınıyor/soğuyor notu, teq işaretçisi, gust kaması.
- Kayıt uyumu sağlam, kayıt anahtarları ayrık. Günlük uçuş PROG'a dokunmuyor (`onFlightEnd` 4026).
- Prosedürel dünya (asset yalnız 2 maskot PNG'si), `?noassets`, `?low`, `?nosave`, `?debug` bayrakları ve `window.kapadokya` durum dışa aktarımı test için çok değerli.
- Erişilebilirlik temeli var: azaltılmış hareket (sarsıntı ve flaş kapalı), klavye ile tam oynanış, odak yönetimi.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Zarf parlaması görsel regresyonu (D).** `7c7e51c` satır 5093: `emissiveIntensity = (burning ? 0.85 : 0.05) + heat*0.45 + …` ile değer en fazla ~1,4'e çıkıyor (eskiden ≤0,33). Emissive rengi turuncu 0xff7a20 (3477). Sonuç: brülör yanarken gore çizgileri ve krem paneller kayboluyor, zarf düz neon turuncuya dönüyor (`desktop-burning.png` ile `desktop-flight.png` karşılaştırması). Brülör ise oyunun en sık kullanılan girdisi, yani bu görüntü sürekli ekranda. Ayrıca kırpışmadan geçiş anlık (eşik 0,05→0,85). Fotoduyarlılık açısından tam ekran değil ama sert bir parlaklık sıçraması.
   Adımlar: `?flight=1&low` → Space'i basılı tut → zarf düz turuncu.
2. **Telefonda Altın Saat düğmesi alet panelinin üstüne biniyor (D).** 390×844'te `#inst` x 8-233 ile `#c-golden` x 175-238 (y 792-838) örtüşüyor. "YAKIT 98%" ve "Hasar" satırı kapanıyor (`phone-flight.png`). Örtüşmeyi Altın Saat commit'i getirdi (0c9ee93: ctl'ye ikinci satır).
3. **Titreşimin kapatma ayarı yok (D) + iOS'ta çalışmıyor (K).** `SET.haptics` varsayılanı `true` (2899), ama Ayarlar'da düğmesi yok (yalnız 4013 ve 4524'te okunuyor). Basılı tutulan brülör/supap düğmesinin her `pointerdown`'unda titriyor. "Hareketi azalt" da titreşimi kapatmıyor. **K** Game Accessibility Guidelines ve Xbox XAG 110: dokunsal geri bildirim her zaman kapatılabilmeli. **K** W3C uygulama raporu: Safari/WebKit `navigator.vibrate`'i uygulamıyor, yani iOS oyuncuları bundan hiç yararlanmıyor.
4. **Telefonda vizör açıkken brülör ve supap yok (D/T).** `#ui.vf-on .ctl { visibility:hidden }` (1008). Masaüstü yardımı "brülör ve supap çalışır" diyor (2997), ama dokunmatikte `.vf-help` gizli (1016) ve kumanda yok. 12 s ağır çekim bitince balon normal hızda süzülüyor; dokunmatik oyuncu kadraj kurarken irtifa kaybedip peribacasına çarpabilir (**T**, uçuşta denemedim).
5. **Klavye metni dokunmatikte (D).** `liftHint` "Brülörü basılı tut (Boşluk)" ve `howto` "B ile pilot balonu bırak" telefonda da gösteriliyor (`phone-title.png`). Küçük ama ilk 10 saniyedeki ilk talimat bu.
6. **Telefonda üst çubukta yıldızlar kırpılıyor (D, görsel).** `phone-flight.png`'de sağdaki 3 yıldızın ancak 1,5'i görünüyor.
7. **Uçuşlar uzun (D).** Bot süreleri 2. uçuşta 408 s, 10. uçuşta 424 s; en kısası 1. uçuşta 122 s. İnsan oyuncu muhtemelen daha uzun sürer (**T**). 2×/4× hız düğmesi var ama keşfedilmesi zor (yalnız `1×` ikonu). **K** Poki'nin ölçüt aralığı ortalama 5+ dk oyun süresi, yani uçuş başına 7 dk tek oturum için ağır.
8. **Günlük Uçuş yeni oyuncuya zor uçuş verebilir (D/T).** Günlük herkese ilk ziyaretten açık ve `hiddenLayers()` günlükte her zaman `true` (3721). Bugünün günlüğü "Öğle Termikleri" (8. uçuş tabanlı), yani 1. uçuşu bile görmemiş biri gizli katmanlı termik uçuşuna düşebiliyor.
9. **README eksik (D).** Altın Saat, Album ve titreşim belgelenmemiş, `key_features` güncel değil.
10. **Ekran okuyucu (D).** Oyun toast'larında (`#toasts`) `aria-live` yok. Hedef tamamlandı, yakıt azaldı, esinti gibi kritik olaylar sesli okunmuyor (kitin kendi live bölgesi yalnız kit mesajları için, 1854).
11. **HUD DOM yükü (D, küçük).** `updateHUD` 12,5 Hz'de pusulanın SVG'sini ve yıldızları `innerHTML` ile baştan kuruyor (4243, 4211). UHD 620'de büyük ihtimalle sorun değil (**T**).

## 4. EKLENMELİ — yüksek değer
**4.1 Sürüklenme öngörüsü (drift forecast), ilk uçuşlarda ve isteğe bağlı**
- Ne: Balonun önünde, şu anki irtifada ortalama rüzgârla 20-30 s sonra nereye varacağını gösteren kesikli bir çizgi. İsteğe bağlı ikinci çizgi, hedef katmana çıkılırsa izlenecek yolu gösterir.
- Neden: Asıl zorluk "hangi katman beni hedefe götürür" sorusunun cevabını 3,5 s gecikmeyle birlikte kafada kurmak. Merdivendeki yeşil ok yalnız yönü veriyor, mesafe ya da sapma göstermiyor. Bot bu öngörüyü kullanıyor (`simPlan`), oyuncu kullanamıyor. **K** FTUE kaynakları ilk dakikalarda oyuncunun "neden-sonuç" ilişkisini hızla görmesini öneriyor (Google Play, Roblox).
- Nasıl: Render tarafında `C.windAt(F,x,y,z,t,true)` ile 0,5 s adımlarla 60 nokta hesaplanır. Sonuç tek bir `THREE.Line` (BufferGeometry, her 0,25 s'de güncellenir). 1-4. uçuşlarda açık, sonra Ayarlar'da "Rüzgâr öngörüsü: açık/kapalı". CORE'a ve bota dokunmaz, kayda yalnız `SET.forecast` eklenir.
- Maliyet S-M. Risk düşük: 1 çizim çağrısı ve ek 60 `windAt` çağrısı; yıldız dengesi ilk uçuşlarda biraz kolaylaşabilir. Kısıtlara uyuyor.

**4.2 Uçuş içi "kısa yol" hız ipucu + 4× seyir otomatiği**
- Ne: İki katman arasında uzun süzülme varken HUD'da "Seyir 4× (T)" yongası belirir ve yere 60 m yaklaşınca ya da bir hedefe 150 m kalınca hız kendiliğinden 1×'e döner.
- Neden: Uçuşlar 2-7 dk (D). Boş süzülme süresi uzun, ama en zor anlar (iniş, işaret bırakma) 1× ister. Mevcut hız düğmesi seyir otomatiği yapmıyor.
- Nasıl: `G.speed`'i bir `cruise` bayrağına bağla, `update()` içinde mesafe/AGL eşiklerinde 1×'e indir. CORE değişmez (`G.acc` ölçeği zaten var, 5058).
- Maliyet S. Risk: düşük. Bot `?speed` ile ayrı çalışıyor. VF ağır çekimle çakışmaması için `vfSlowRate` önce değerlendirilmeli.

**4.3 Kendi en iyi uçuşunun hayaleti (yerel ghost)**
- Ne: Bir uçuşun en iyi denemesindeki (x,y,z) izi, yarı saydam küçük bir balon olarak yeniden oynatılır. Günlük Uçuş'ta da günün kendi en iyisi gösterilir.
- Neden: 36 yıldızdan sonra tekrar oynama nedeni zayıf (yalnız puan). Hayalet "nerede daha iyi katman seçtim" sorusunu görünür kılıyor. **K** Async ghost'lar günlük mod ve tekrar oynanış için yaygın bir kalıp, ve günlük en iyiyi normal en iyiden ayrı tutmak öneriliyor (Ghost Pro Racing HN, typevelocity yazısı).
- Nasıl: 1 Hz örnekleme (uçuş başına ≤500 nokta × 3 sayı, ~6 KB). Kayıt `arena.kapadokya.ghost.<i>` altında, yeni bir anahtar; eski kayıtlar etkilenmez. Oynatmada `CROWD` instanced mesh'lerinden biri yeniden kullanılır (çizim çağrısı eklemez). Sunucu yok, paylaşım yok, yalnız yerel.
- Maliyet M. Risk: localStorage kotası (12 uçuş × 6 KB, sorun değil). `FLAG.auto`/`nosave` için `store` zaten yazmıyor.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Günlük Uçuş'u yeni oyuncu için yumuşatma:** `PROG.done` sayısı 4'ün altındaysa günlüğün tabanı yalnız 1-4. uçuşlardan seçilsin ya da katmanlar gizlenmesin. Dikkat: günlük, oyuncular arasında aynı olmalı. Alternatif: zor günlükte "önce 2 uçuş bitir" notu. S.
- **Altın Saat'e "tema" görevi:** "Kale + balon aynı karede" gibi günlük bir kompozisyon hedefi; `scoreFrame` zaten konu türlerini sayıyor. S-M. Mevcut imza mekaniğini derinleştirir, yeni sistem eklemez.
- **İniş tarlasında rüzgâr tulumu/duman yönü + son yaklaşma çizgisi:** İniş puanının %30'u yakınlıktan geliyor. Tarla tulumları var (`SOCK`), ama yaklaşırken HUD'da "tarlaya X m, rüzgâr seni Y° sapıtıyor" satırı yok. S.
- **Serbest uçuş / fotoğraf turu (yıldızsız):** 12 uçuş bittikten sonra hedefsiz, yakıtı bol uçuş; Altın Saat albümüyle doğal bir eşleşme. M. Risk: içeriği tekrar kullanıyor, yeni varlık gerekmez.
- **Toast'lara `role="status"`/`aria-live="polite"`:** tek satırlık değişiklik (bkz. §7).
- **Uçuş sonunda "katman zaman çizelgesi":** hangi katmanda ne kadar kaldın, yakıtı nerede harcadın. Öğretici, M; bir sonraki denemeyi doğrudan iyileştirir (**T**).

## 6. EKLENMEMELİ
- **Çevrimiçi skor tablosu / paylaşılan ghost:** sunucu ve kullanıcı verisi ister, kısıtı aşar. Arena paylaş düğmesi metin paylaşımı için yeterli.
- **Yatay dümen, ok tuşlarıyla yön veya "rüzgâra karşı itiş":** oyunun tek fikrini yok eder (README: "never steer sideways").
- **Daha fazla gerçek zamanlı ışık ve parlaklık efekti (bloom, post-processing):** UHD 620'de çizim çağrısı ve dolgu maliyeti getirir. `7c7e51c` gibi "juice" denemeleri görüntüyü zaten bozdu.
- **Zorunlu reklam benzeri ödül/enerji sistemi ya da günlük "kaçırırsan kaybedersin" baskısı:** ücretsiz, hesapsız oyunun tonuna aykırı. **K** Günlük meydan okuma kaynakları da öğütme yerine ritüeli öneriyor.
- **Gerçek bir balon şirketinin logosu/adı ya da gerçek bir oyunun haritası:** kısıt dışı.
- **Titreşimi daha fazla olaya yaymak** (her rüzgâr geçişi, her toast): kapatma ayarı yokken erişilebilirliği daha da kötüleştirir. iOS'ta da hiç çalışmaz.
- **CORE fizik sabitlerini oyuncu deneyimi için gelişigüzel değiştirmek:** hedef konumları bu sabitlerle uçurularak yerleştirildi (README "Flights as data"). Yeniden yerleşim ve bot testi gerekir.

## 7. Düzeltilmeli
1. **Zarf parlaması (5093):** Eski kısa formüle dön, ya da `burning ? 0.85` sabitini kaldır ve en fazla ~0,35'e kenetle (`heat*0.3 + clamp(..)*0.05`). İstenen "iç ışık" etkisi, alt banttan yukarı solan bir gradyanla shader'da (`shadeEnvelope`) daha doğru olur. Doğrulama: masaüstünde yanarken ve yanmazken kare karşılaştırması; gore çizgileri görünmeli.
2. **Telefon kumanda yerleşimi:** `@media (max-width:760px)` (1530) içinde `#c-golden`'ı üst satıra (Foto/İşaret/Pibal/Takip yanına) taşı ya da `.inst` genişliğini `ctl` soluna kadar sınırla. Doğrulama: 390×844 ve 360×740'ta `getBoundingClientRect` ile örtüşme 0 olmalı (`probe.cjs` bunu yapıyor).
3. **Titreşim ayarı:** Ayarlar'a "Titreşim açık/kapalı" segmenti ekle (`seg-tips` kalıbıyla). Varsayılanı `isPhone` olsun, ve `G.reduced` açıkken titreşmesin. Ayrıca `navigator.vibrate` her basılı tutma başlangıcında değil, yalnız anlamlı olaylarda (çarpma/sert iniş) çağrılsın. `SET.haptics` alanı korunmalı, böylece eski kayıtlar uyumlu kalır.
4. **Vizörde dokunmatik kumanda:** `#ui.vf-on` iken `#c-burn` ve `#c-vent` görünür kalsın (yalnız o iki düğme), ya da vizör açıkken balon otomatik "hover" tutsun. Basit olanı ilki.
5. **Dokunmatik metinleri:** `isPhone` (ya da `pointer:coarse`) iken `liftHint` ve `howto` için tuş adı içermeyen varyant kullanılsın ("Brülör düğmesini basılı tut").
6. **Üst çubukta yıldız kırpması (dar ekran):** `.stats` içinde yıldız yongası `flex-shrink:0` olsun ya da telefonda yakıt yüzdesi gizlensin.
7. **`#toasts`'a `aria-live="polite"`** ekle (HTML 2131 civarı, tek öznitelik).
8. **README:** Altın Saat (K, vizör, puanlama, Album, `arena.kapadokya.album` anahtarı) ve titreşim belgelensin, `project-meta.json` `key_features` güncellensin.
9. **Relay denetimi:** `02a1f07` ve `7c7e51c` insan/ajan incelemesi olmadan main'e girdi. Bu turda bu iki değişiklik göz ile ve ekran görüntüsüyle yeniden doğrulanmalı.

## 8. Önerilen ilk 3 iş
1. **Zarf parlamasını geri al/kenetle + titreşime ayar ve azaltılmış-hareket bağı (§7.1, §7.3).** S. Gerekçe: bugün main'de olan, her uçuşta görünen bir regresyon ve bir erişilebilirlik açığı. İkisi de son 24 saatte denetimsiz relay ile girdi; önce zemin düzeltilmeli. Kanıt: `desktop-burning.png`; satır 5093, 2899, 4013, 4524.
2. **Telefon kumanda yerleşimi ve vizörde brülör/supap (§7.2, §7.4, §7.5).** S. Gerekçe: telefon kısıtın parçası; imza mekaniği (Altın Saat) telefonda hem HUD'u örtüyor hem de oyuncuyu kumandasız bırakıyor. Doğrulama `probe.cjs phone` ile örtüşme listesinin boş çıkması.
3. **Sürüklenme öngörüsü (§4.1), ardından seyir otomatiği (§4.2).** S-M. Gerekçe: oyunun tek zor kavramını (gecikmeli dikey kontrol → yatay sonuç) görünür kılan en yüksek değerli ekleme; render-side olduğu için CORE, bot ve kayıtlar etkilenmez. Seyir otomatiği uzun uçuş süresini (2-7 dk) kısaltır. Ardından Node'da `core.cjs` ile botun 36/36'yı koruduğu ve tarayıcıda `?auto` ile 0 hata kaldığı tekrar gösterilmeli.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek GPU'da (UHD 620) yükleme süresi ve FPS ölçülmedi. Headless swiftshader'da Play 14-17 s'de etkinleşiyor ve FPS ~20, ama bu yazılım render'ı yansıtıyor.
- Vizörde dokunmatik oyuncunun irtifa kaybedip çarptığı senaryo uçuşta denenmedi (yalnız CSS ve kod okuması).
- Firefox/WebKit'te koşmadım (yalnız Chromium; CI bunları kapsıyor).
- `navigator.vibrate`'in iOS 18 Safari'deki durumu tartışmalı (**K**: bir MDN BCD issue'su "çalışıyor" diyor, W3C raporu "yok" diyor). Her iki durumda da ayar gerekli.
- Gerçek oyuncu uçuş süreleri ve takıldıkları uçuşlar bilinmiyor; analytics olarak yalnız goatcounter sayfa sayacı var, oyun içi telemetri yok ve eklenmemeli. Tahminler bot verisine dayanıyor.
- Hayalet önerisinde örnekleme sıklığı ve görsel netlik (1 Hz yeterli mi) prototiple denenmeli.
- Tam 12 uçuşu `?auto` ile tarayıcıda koşmadım (makine paylaşımı); Node'da CORE ile 12/12, tarayıcıda 1-2. uçuş + 3. uçuşun başı.

## Kaynaklar
- Windward Balloon (irtifa bantları, kenar okları): https://dinogame.gg/games/balloon-game/
- Gas Giant Airship, Ludum Dare 57 (katmanlı akımlar): https://jcourt325.itch.io/gas-giant-airship
- Game Accessibility Guidelines — haptikler için aç/kapa/kaydırıcı: https://gameaccessibilityguidelines.com/include-toggle-slider-for-any-haptics/
- Xbox XAG 110 Haptic feedback: https://devdocs.xbox.com/build/game-principles/accessibility/xag-deep-dives/xag-110-haptic-feedback
- IGDA GASIG, controller vibration: https://igda-gasig.org/?p=1308
- Vibration API uygulama raporu (W3C): https://w3c.github.io/vibration/reports/implementation.html
- caniuse navigator.vibrate: https://caniuse.com/mdn-api_navigator_vibrate
- MDN BCD issue (iOS çelişkili rapor): https://github.com/mdn/browser-compat-data/issues/29166
- CrazyGames teknik gereksinimler: https://docs.crazygames.com/requirements/technical/
- CrazyGames oynanış gereksinimleri: https://docs.crazygames.com/requirements/gameplay/
- Poki SDK gereksinimleri: https://sdk.poki.com/requirements
- Defold Poki en iyi uygulamalar (5+ dk oyun süresi, %65 play conversion): https://defold.com/extension-poki-sdk/best-practices
- Roblox onboarding (FTUE): https://create.roblox.com/docs/production/game-design/onboarding
- Google Play, kullanıcı yolculuğu ve onboarding: https://medium.com/googleplaydev/the-user-journey-onboarding-and-activation-be5ebdfc0354
- Günlük meydan okuma tasarımı: https://bugnet.io/blog/how-to-design-daily-challenges-that-keep-players-coming-back
- Async ghost yarışı (HTML5): https://hn.svelte.dev/item/45490844
- Günlük ve ghost'u ayrı tutma: https://typevelocity-nu.vercel.app/daily-challenge-launch

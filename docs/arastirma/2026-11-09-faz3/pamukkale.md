# Pamukkale — faz 3 araştırması

Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Repo: `/home/user/pamukkale` @ `de813d4`, `index.html` 2650 satır, `git status` temiz (D).
Ölçüm araçları (repo dışı): `_pamukkale/probe.mjs` (tek araçlı çözüm taraması), `_pamukkale/three.mjs` (par içinde "taşma yok" araması), `_pamukkale/run.cjs` (headless Chromium, swiftshader). Ekran görüntüleri: `_pamukkale/01-title.png`, `02-level1.png`, `05-phone-level1.png`.
Not: Tarayıcı koşusu sırasında makinenin yük ortalaması 50 civarındaydı ve fps 0-2 ölçüldü. Bu yüzden fps ya da bot hızı hakkında hiçbir iddia yok (D).

## 1. Şu anki durum
- **Oyun:** su ızgara otomatı (`PSim`, satır 867-1021). 23 seviye, 5 bölge (satır 1024-1048). Araçlar taş/set/ayırıcı, son 3 seviyede savak kapağı. Seviye başına 3 yıldız: dolu, taşma yok, par (D).
- **İmza mekaniği:** "Kalsiyum Zamanı" savak kapakları (commit `1438d8f`). Kapak su akarken açılıp kapatılabiliyor, bot `gsol` tick'lerinde açıp kapatıyor (satır 2008-2010). ARENA-KIT v1.0.0 (satır 22-375) entegre: perf (1209), günlük (2147), paylaş (2157), rozet (2170). Günlük meydan okuma, sabit 23 seviyeden `seed % 23` ile birini seçiyor (D).
- **Döngü:** dt 0,05 sn ile sınırlı. Kare başına en fazla 120 tick. Tick = 0,05 sn, yani 1x hızda bir seviye 10-19 sn oyun süresi (`time` 200-385 tick) (D, satır 1059, 2556-2564).
- **Kayıt:** `arena.pamukkale.save|settings|best`. `readJSON`, eksik alanları `Object.assign` ile varsayılandan dolduruyor, bu yüzden eski kayıtlar yüklenir (D, 1063-1080).
- **Bot:** `?auto` her seviyede `sol` yerleştirip 3x hızda koşuyor. Kaybedince duruyor (D, 2527-2549). 25 sn'lik kısa koşuda 0 JS hatası oldu, 1. seviye sonuç ekranına ulaştı. Yük yüzünden daha fazlası ölçülemedi (D).
- **i18n:** TR/EN sözlük (1084-1143). Seviye adı, ipucu ve bölge adı ayrı tablolarda (1144-1176) (D).
- **Mobil:** coarse pointer'da kalite varsayılanı `low`. Uzun basış siler, iki parmak orbit/pinch yapar (2311-2369). 390×844'te yatay kaydırma yok (`scrollWidth` 390) (D).
- **Konsol:** masaüstü, telefon ve `?auto` açılışlarında 0 hata, 0 uyarı, 0 başarısız istek. CDN yerelden, font/analitik boş yanıtla servis edildi (D).
- **Ses:** tamamen sentez (saz, flüt, şırıltı, kuş). Arena `pause/resume` ile AudioContext askıya alınıyor (D, 1754-1860, 2477-2480).

## 2. Güçlü yanlar (korunmalı)
- Deterministik, DOM'dan bağımsız simülasyon bloğu (`SIM-BEGIN/END`). `tools/solve-levels.mjs` aynı kodu çalıştırıyor, bu da her seviye değişikliğini çevrimdışı doğrulanabilir kılıyor (D).
- "Durgun su kalsiyum örer" ve savak kapağı gerçek yerle bağlantılı, özgün bir mekanik çifti. Seviye 23 (sızan havuzu kapakla kapatıp kenar ördürme) tasarım olarak en güçlü bulmaca (D, satır 1174).
- Geri al (Z), anında sıfırla (R), hızlı ileri (F) zaten var. Dış kaynaklar bunları deneme-yanılma bulmacalarında hayal kırıklığını azaltan temel öğeler sayıyor (K: itch.io devlog'ları, Puddle incelemesi).
- Hafif sahne: oyunda 19 draw call ve 29,3k üçgen (1. seviye, D). Gölge `low`'da kapalı, partikül 120/240 (D, 1211, 1472).
- Saklama erişimleri try/catch içinde. Günlük koşu kampanya kaydına dokunmuyor (D, 2044-2048).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Birçok seviyede 3. yıldız matematiksel olarak imkânsız (statik yerleştirmeyle) (D).** `three.mjs`, par içindeki bütün tek ve ikili araç kombinasyonlarını tam taradı. 2, 5, 6, 8, 11, 12 ve 16. seviyelerde "taşma yok + par" birlikte sağlanamıyor. 9, 15 ve 17-20 taranmadı (par 3-4, kombinatorik pahalı). Bot da 23 seviyede yalnız 52/69 yıldız alıyor (README). Oyun su akarken araç koymaya izin veriyor (`placeAt` `running` kontrol etmiyor, 1942), bu yüzden zamanlamayla mümkün olabilir. Bu doğrulanmadı (§9). Oyuncuya bir hedef gösterip ulaşılamaz bırakmak, dış kaynakların en çok uyardığı star tasarım hatası (K: Frustration Factory "every level possible to 3-star", haiyoooo post-mortem).
2. **Dil değişince seviye adı, ipucu ve bölge adı eski dilde kalıyor (D).** `const L` açılışta bir kez hesaplanıyor (1179) ve `levelName`, `levelHint`, `AREA_NAMES[..][L]` onu kullanıyor. Adımlar: TR açılış → Oyna → `L`. Sonuç: HUD "LEVEL 1/23 · **İlk Damla**", bölge "**ALT HAVUZLAR**", buton "Start water". Karışık dil, kurallardaki "kesimleri karıştırma" ilkesine de ters.
3. **Süre sınırı görünmüyor (D).** `def.time` yalnız `advance()` içinde kullanılıyor (2028). HUD'da kalan süre yok, "Su" yalnız akan litreyi gösteriyor. Oyuncu "Süre doldu"yu habersiz yaşıyor. Gerekli olmayan zaman sınırlarının ayarlanabilir ya da görünür olması bir erişilebilirlik ilkesi (K: XAG 116).
4. **Telefonda tahta ekrana sığmıyor, HUD kırpılıyor (D, `05-phone-level1.png`).** Kamera dikeyde sabit 1.35 çarpanı kullanıyor (1729). 390×844'te sol havuz kenarda kesiliyor. Stats-pill'de "ARAÇ" değeri ve yıldızlar actions-pill'in altında kalıyor.
5. **Okunabilirlik: beyaz üstüne beyaz arazi (D/T).** 1. seviye ekranında basamak yükseklikleri ve hücre sınırları neredeyse ayırt edilemiyor (`02-level1.png`). Izgara çizgisi yok. Dokunmatikte hayalet önizleme yok, `pointerType==='mouse'` koşulu var (2354). Su yolunu tahmin etmek zor, bu da deneme-yanılmaya itiyor (K: "puzzle should be logically explainable").
6. **Ölü ve riskli Service Worker kodu (D).** Blob URL ile kayıt yapılıyor (2635-2647). Chromium bunu reddediyor ("The URL protocol of the script ('blob:…') is not supported", ölçüldü, kayıt sayısı 0). Hata `.catch` ile yutuluyor. Çalışsaydı bile sürümsüz cache-first `index.html` güncellemeleri kalıcı olarak bayatlatırdı. Gemini relay commit'i `0e3c33f` ile geldi.
7. **İpucu metinleri seviyelerle uyuşmuyor (D).** S19 ipucu "Altı havuz" diyor ama seviyede 5 havuz var (1170 ve 1043). S1 "bir taş koy" diyor, kayıtlı çözüm set ve taşmasız tek çözüm de set (probe: 1 taşmasız çözüm, `dam` hücre 37). S5 "ayırıcı" diyor, oysa ayırıcıyla tek çözüm var ve bot set kullanıyor.
8. **Meta açıklaması "20 levels" diyor, oyunda 23 var (D, satır 8, 11).** README'nin "20/20, 46/60" ifadeleri de eski.
9. **Zorluk eğrisi düz ve gevşek (D/T).** 1-7. seviyelerin hepsi tek araçla çözülüyor (probe: 2-11 farklı tek-araç çözümü). Envanter her seviyede fazla (5-6 taş + set + ayırıcı, par 1-4). 23 seviyenin 20'sinin çözümü "bir set + birkaç taş" kalıbında (1025-1044). Ayırıcı yalnız S3 çözümünde var.
10. **Günlük meydan okuma yeni içerik üretmiyor (D).** Çözülmüş sabit bir seviyeyi tekrar açıyor (2147). Seri tutundurması zayıf kalıyor (T).
11. **Küçük:** 1024×600'de başlık kartının alt satırı (TR/EN) footer'a sıkışıyor (D, `01-title.png`). Havuzun "doldu" durumu esas olarak halkanın rengi turkuaza dönerek gösteriliyor, oysa ilke rengin yedek olmasını istiyor (T: renk dönüşümü kodda doğrulanmadı; K: GAG colour).

## 4. EKLENMELİ — yüksek değer
**4.1 Yıldız tutarlılığı: her seviye 3 yıldıza ulaşılabilir olsun**
- Ne: Ya seviye verisi (par/envanter/havuz) ayarlanır ya da 3. yıldız kuralı "taşma ≤ eşik" olur (seviye başına `spillMax`).
- Neden: §3.1. Ulaşılamaz yıldız, yıldız peşindeki oyuncuyu kaçırır (K).
- Nasıl: `solve-levels.mjs`'e "taşma yok + par" araması eklenir (tamamı `three.mjs` mantığı). Tasarımcı bunu her seviye için yeşil görmeli. Seviyeye `spillMax` (varsayılan 0.01) eklenir ve `starState` (1877) onu okur. `sol` bot için kalır, gerekirse yanına `sol3` eklenir. Kayıt biçimi değişmez (yıldız sayısı max ile korunur).
- Maliyet: M. Risk: düşük. Bot: `sol` değişmezse etkilenmez. Kısıta uyar.

**4.2 Görünür süre ve su bütçesi**
- Ne: HUD'da kalan süreyi gösteren ince bir halka/çubuk ya da "Su x/y L" (emitted / rate*time).
- Neden: §3.3, XAG 116 (K).
- Nasıl: `renderHUD` (2240) içinde `G.st.tick / G.def.time`. Bir `<div>` eklenir, %80'den sonra renk ve metin ("son 3 sn") ile uyarır. Kısıt dostu, S.
- Risk: dar telefon HUD'unda yer. `.hide-s` olan "Su" kutusunun yerine konabilir.

**4.3 Akış önizlemesi ("kuru koşu" yolu)**
- Ne: Su başlamadan önce, yerleştirilen araçlarla suyun ilk N tick'te izleyeceği yolu yarı saydam okla/izle gösteren bir buton ya da sürekli açık mod. Önizleme taşan hücreyi kırmızı kenarla işaretler.
- Neden: §3.5. Oyuncunun deneme-yanılma yerine akıl yürütmesini sağlar (K: "testing tool to see where water can travel", "logically explainable"). Beyaz-beyaz okunabilirlik sorununu da kısmen çözer.
- Nasıl: `PSim.create` + `place` kopyasında 60-100 tick `step` koşulur. Saf, render dışı, ~1 ms (T). `w>EPS` hücreleri tek bir `InstancedMesh` ya da `Points` ile çizilir, ek draw call 1 olur. Yalnız `G.dirty` olunca yeniden hesaplanır. Dokunmatikte seçili hücreyi gösteren ikinci dokunuşla onay ("dokun = seç, tekrar dokun = koy") ya da hücre vurgusu eklenir.
- Maliyet: M. Risk: önizleme bulmacayı fazla kolaylaştırabilir. Çözüm olarak yalnız ilk 2-3 sn gösterilir ya da 3. yıldızı etkilemeyen bir "ipucu" sayılır. Bot etkilenmez.

**4.4 Dil değişiminin tamamı (hata düzeltmesi ama yüksek değer)**: §7.1.

**4.5 Telefona sığan kamera**
- Ne: Tahtanın köşelerini dikey ve yatay FOV'a göre sığdıran mesafe.
- Nasıl: `updateCamera` (1727) içinde sabit 1.35 yerine `dist = max(boardRadius / tan(vFov/2), boardRadius / (tan(vFov/2)*aspect)) * 1.1`. HUD için stats-pill ≤ 400 px'te iki satıra ya da yıldızları gizlemeye geçer.
- Maliyet: S. Risk: masaüstü kadrajı değişir, ekran görüntüleriyle karşılaştırılmalı.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Başarısızlık sonrası kademeli ipucu:** 2-3 başarısız denemeden sonra çözümün ilk aracı yanıp sönen hücreyle gösterilir. `sol` zaten var (K: "hint after repeated failure"). S. Risk: yok, bot etkilenmez.
- **Ayırıcı ve kalsiyumu gerçekten gerektiren yeni seviyeler (24-26):** §3.9'a cevap. `solve-levels.mjs`'in "boş tahta başarısız, X olmadan başarısız" kontrolleriyle üretilir. M. Kayıt: `unlocked` sayısal, yeni seviyeler sona eklenirse eski kayıt uyumlu kalır (D, 2047). Bot için `sol` ve `gsol` zorunlu.
- **Günlük meydan okumaya değişiklik:** aynı seviye ama "envanter −1" ya da "kapak başka başlangıç" gibi küçük bir kural, `Arena.daily().rng` ile. Her değişiklik `solve-levels` mantığıyla tarayıcıda doğrulanamaz. Bunun yerine önceden doğrulanmış 23×k varyant tablosu kullanılır. M.
- **Hücre ızgarası/yükseklik konturu:** yalnız oyun ekranında, terrain vertex rengine hafif çizgi olarak eklenir. Ek draw call yok. S. Önizleme (4.3) gelirse önceliği düşer.
- **Seviye sonu "sonucu tekrar izle":** son koşuyu 3x hızda yeniden oynatma (deterministik, yalnız araç listesi). S-M.

## 6. EKLENMEMELİ
- **Service Worker / PWA önbelleği:** tek dosya ve blob kayıt zaten çalışmıyor. Ayrı `sw.js` dosyası tek dosya kısıtını aşar. Cache-first, yayın güncellemelerini bozar (§3.6).
- **Serbest seviye editörü + paylaşım kodu ile çevrimiçi galeri:** sunucu gerektirir, kısıtı aşar. Yalnız URL'de kodlanan yerel bir editör olabilir, ama doğrulanmamış (çözülemez) seviyeler üretir. Önce 4.3 gelmeli.
- **Gerçek zamanlı su fiziği (SPH/shader sıvı):** UHD 620'de ve telefonda maliyetli. Deterministik ızgarayı ve çözücüyü bozar.
- **Daha sıkı süre sınırı ya da "hız" yıldızı:** sakin bulmaca kimliğine ve erişilebilirliğe ters (K: XAG 116).
- **Liderlik tablosu, hesap, bulut kaydı:** sunucu ve kullanıcı verisi demek, kısıtı aşar.
- **Mevcut seviyelerin `rows`/`pools` değerlerini sessizce değiştirmek:** `progress.stars[idx]` seviye sırasına bağlı. Sıra ya da anlam değişirse eski yıldızlar yanlış seviyeye kalır. Değişiklik yalnız par/envanter/eşik düzeyinde olmalı.

## 7. Düzeltilmeli
1. **Dil:** `L`'yi fonksiyona çevir (`const L = () => settings.lang === 'en' ? 1 : 0`) ve 1180, 1181, 2182, 2245 satırlarını güncelle. `applyI18n` hint-bar'ı da yeniden yazsın (D hata, S).
2. **Service Worker bloğunu kaldır** (2635-2647) ve manifest'i olduğu gibi bırak. S. Kanıt: tarayıcıda kayıt hatası alındı.
3. **Metinler:** meta/og açıklamasında "20 levels" → 23 (8, 11). S19 ipucu "Altı havuz" → beş. S1/S5 ipuçları gerçek çözümle uyumlu olsun ya da araç adı vermesin. README'deki "20/20, 46/60" ifadeleri güncellensin.
4. **Telefon HUD'u:** ≤400 px'te stats-pill taşması (D). Yıldızlar ya da "Araç" görünür olmalı.
5. **Başlık kartı alçak ekranlarda** (≤600 px yükseklik) kaydırılabilir olsun ya da TR/EN satırı yukarı alınsın.
6. **Havuz doluluk göstergesi:** renge ek olarak şekil, ör. halkada ✓ ya da dolum yayı (K: GAG colour).
7. **A11y:** `#hud-stars aria-label="stars"` sabit İngilizce. Canvas için seviye durumunu `Arena` announce ya da `#toasts` üzerinden okutmak yeterli, `#toasts` zaten `aria-live` (D).
8. **Gate seviyelerinde par 0 ama S22'de 1 taş envanteri var (D, 1047).** Taş kullanan oyuncu 3. yıldızı kaybediyor ama bu belirtilmiyor. HUD "0/0 ★" bunu kısmen gösteriyor. İpucunda belirtilmeli.

## 8. Önerilen ilk 3 iş
1. **Dil hatası, SW kaldırma ve metin düzeltmeleri (§7.1-7.3):** S, risksiz, doğrudan doğrulanabilir (`L` sonrası HUD metni, SW bloğu yok). Kalan her iş bunun üzerine güvenle kurulur.
2. **Yıldız tutarlılığı (4.1):** önce `solve-levels.mjs`'e "3 yıldız mümkün mü" kontrolü eklenir, sonra 2, 5, 6, 8, 11, 12, 16 (ve taranmamış 9, 15, 17-20) için par, envanter ya da `spillMax` ayarı yapılır. Oyunun ödül sistemi şu anda bozuk sinyal veriyor. Bot `sol` ile etkilenmeden kalır.
3. **Görünür süre ile telefon kamerası/HUD (4.2 + 4.5):** ikisi de S. Telefon oyuncusunun ilk 30 saniyesini doğrudan iyileştirir (havuz ekranda, kalan süre görünür). Ardından tur kalırsa 4.3 (akış önizlemesi) gelir.

## 9. Doğrulanmayanlar / açık sorular
- Su akarken araç koyarak (zamanlamayla) §3.1'deki seviyelerde 3 yıldız alınabilir mi? Arama yalnız başlangıçta yerleştirmeyi kapsadı. Bu oyunun bilinçli bir tasarımı mı, yoksa açık mı?
- 9, 15 ve 17-20. seviyelerde 3 yıldızın mümkün olup olmadığı taranmadı (par 3-4).
- fps ve bot süresi bu makinede ölçülemedi (yük ~50). README'deki "23/23, 52/69" bu oturumda yeniden doğrulanmadı.
- Firefox ve WebKit'te Service Worker davranışı denenmedi (Chromium'da reddedildi).
- Havuz halkasının dolunca yalnız renk mi değiştirdiği kodda satır satır doğrulanmadı.
- Gerçek telefonda uzun basma (520 ms) ile pinch çakışması ve yanlış yerleştirme oranı denenmedi.

## Kaynaklar
- Puddle incelemesi (deneme-yanılma, anında yeniden başlatma): https://www.pocketgamer.co.uk/puddle/puddle/
- Flowerdrops seviye tasarım süreci (su yolu test aracı): https://natikatz.itch.io/flowerdrops/devlog/100849/flowerdrops-level-design-process-also-v11-is-out
- Yeni başlayanın bulmaca tasarımı (mantıkla açıklanabilir, deneme-yanılmayla değil): https://itch.io/devlog/285457/a-beginners-approach-to-puzzle-design.amp
- Spring Falls incelemesi: https://148apps.com/reviews/spring-falls-review
- Her seviyenin 3 yıldıza ulaşılabilir olması: https://frostedaxe.itch.io/frustration-factory/devlog/940141/ensuring-every-level-is-possible-to-3-star
- 3 yıldız post-mortem: https://haiyoooo.itch.io/icecream/devlog/237441/post-mortem-3-star-ratings
- İkincil hedeflerin tutundurmaya etkisi (A/B çalışması): https://grail.cs.washington.edu/projects/game-abtesting/fdg2011/fdg2011.pdf
- Poki gereksinimleri ve kalite rehberi (mobil, hızlı oyuna giriş, dikey): https://sdk.poki.com/requirements , https://sdk.poki.com/poki-quality-guidelines , https://developers.poki.com/guide/easy-access
- Game Accessibility Guidelines, renk: https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/
- Xbox Accessibility Guideline 116, zaman sınırları: https://devdocs.xbox.com/build/game-principles/accessibility/xag-deep-dives/xag-116-time-limits.md

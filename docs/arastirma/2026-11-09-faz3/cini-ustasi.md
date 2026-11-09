# Çini Ustası — faz 3 araştırması

Kanıt etiketleri: **D** = doğruladım/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Repo: `/home/user/cini-ustasi` @ `09fca98` (dal `claude/cloud-session-research-analysis-dufc2b`). Repoda hiçbir şey değişmedi (`git status` temiz).
Çalıştırma notu: makine yük ortalaması 60-78 (4 çekirdek, başka ajanlar) iken headless Chromium + SwiftShader, `?low` ile. FPS ve süre ölçümleri bu yüzden performans kanıtı **değil**; düzen, hata ve durum ölçümleri geçerli.
Geçici dosyalar ve ekran görüntüleri: `scratchpad/arastirma/_cini-ustasi/` (`phone-2-level1.png`, `phonecheck-kiln.png`, `phone-4-complete.png`, `phone6-level30.png`).

## 1. Şu anki durum
- **D** Tek dosya `index.html` (3797 satır, 284 KB), Three.js r170 import map + SRI (satır 938-940), ARENA-KIT v1.0.0 bloğu 584-937. 3 GLB + 6 webp varlık, 8 sn'de gelmezse prosedürel yedek (2477-2530, 3789).
- **D** İlerleme: 30 seviye / 3 bölüm (`LEVEL_DEFS` 1016-1028): Bölüm 1 yalnız döndürme (3×3→5×5), Bölüm 2 + yer değiştirme, Bölüm 3 + sabit ve çift yüzlü taşlar (6×6'ya kadar). Günlük 4×4 tahta (1029-1033), tek günlerde "kazı" varyantı. Desen Atölyesi (kendi deseni, `#p1=` linki, 1252-1341, 3236-3376) imza mekaniği olarak eklenmiş.
- **D** Çekirdek: tahta çözülmüş üretilir, sonra karıştırılır; par = başlangıçtan ev çözümüne plan uzunluğu (1134, 1231-1246). İpucu ve bot O(N), asla başarısız olmaz (2787-2806, 3684-3710). Yıldız: ≤par 3, ≤ceil(1.6·par)+2 → 2 (1247).
- **D** `node tests/core.test.mjs` → `TESTS PASSED 358/358` (bugün koştum). Testler yalnız saf çekirdeği kapsar; DOM/3D/mobil düzen test edilmiyor.
- **D** Kayıt: `arena.cini.settings` + `arena.cini.save`, eski `cini-ustasi-v1` anahtarından tek seferlik göç (962-990). Koleksiyon resimleri kayıttaki `seed` + **güncel** `LEVEL_DEFS` ile yeniden üretiliyor (3019-3027) → `LEVEL_DEFS`/üretici değişirse eski panolar başka resim olur.
- **D** Telefon 390×844: ilk açılış konsol hatasız, `__ciniErrors` boş; Seviye 1'de koç balonu ilk yanlış taşın üstünde ("Tap to rotate…"), dokunma döndürüyor (hist 0→1). Plan uygulanınca fırın adımı → tamamlama kartı → kayıt doğru (`L1: 3 yıldız, 22 hamle`).
- **D** `?auto` botu başlığı geçip Seviye 1'e girdi, hata yok; aşırı yük nedeniyle 30 seviyelik tam koşu yapılmadı (bkz. §9).
- **D** Son commit `9c8ce9a` (relay, gemini flash-lite) ≤400 px genişlikte üst çubuğun sağ düğmelerini ekranın altına sabitledi (CSS satır 328-333). Bu, fırın ve tamamlama ekranlarında çakışma getirdi (§3.1).
- **D** Klavye: P/Esc, M, X, L, Z, H, R, F (yalnız fareyle üzerine gelinen taş) var (3472-3491); **taş seçme/döndürme/yer değiştirme klavyeyle yapılamıyor**.

## 2. Güçlü yanlar (korunmalı)
- **D** Deterministik, test edilmiş çekirdek + "ipucu asla başarısız olmaz" garantisi; bot ve oyuncu aynı `performMove`'u kullanıyor (2646-2650).
- **D** Öğretici duvarı yok: bölüm başına tek satırlık koç balonu, hedef taş altın nabızla parlıyor (2833-2866, 3607). İlk 30 sn'de oyuncu doğrudan tahtada.
- **D** Kenar eşleşince altın parıltı, taş tamamlanınca sır parlaması, yıldız eşiği geçilince yumuşak uyarı (2753-2773) — sakin ama okunaklı geri bildirim.
- **D** Fırın + sır derecesi (mat/parlak/usta) ve duvardaki galeri: çözümün sonunda zanaat hissi, koleksiyon motivasyonu.
- **D** Gölge haritası yalnız bir şey hareket ettiğinde yeniden çiziliyor (1847, 3747); Low katmanında DPR 1, gölge yok, toz 80 parçacık (3391-3401). Draw call: başlık 29-32, 3×3 seviye 38, tamamlama 21 (debug sayacı, D).
- **D** Kayıt göçü, `?fresh/?fill/?level/?daykey/?nokiln` gibi test bayrakları, `window.cini.api` test API'si.
- **K** Döndürme bulmacalarının ilgi kaynağı "bir sonraki simetrik/güzel deseni görmek" ve kısa günlük seanslar ([AmalgamA geliştirici notu](https://diogocosta738.github.io/amalgama.html)); Çini Ustası'nın panoyu duvara asması tam bu motivasyona oturuyor.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Telefon alt çubuğu fırın ve tamamlama ekranlarını örtüyor (regresyon, D).** Adım: 390×844, `?level=1`, tahtayı çöz → fırın kartı. Ölçüm: alt çubuk y=779-844 (z-index 100); `btnKilnFire`/`btnKilnSkip` y=754-796 → düğmelerin alt ~17 px'i çubuğun altında, kart altı y=826 (`phonecheck-kiln.png`). Tamamlama ekranında da ipucu rozeti "3", geri al, yeniden başlat, menü düğmeleri görünür ve basılabilir ama işlevsiz (`useHint`/`undo` `screen!=='playing'` ise sessizce döner, 2739/2745/2788). Kaynak: `9c8ce9a` + `hideAll()` üst çubuğu gizlemiyor (3061).
2. **Klavyeyle oynanamıyor (D, kod).** Taş seçimi yalnız işaretçiyle (3501-3576); ok tuşu/odak imleci yok. WCAG 2.1.1 ve Xbox XAG 107 "oynanış dahil tüm işlevler klavyeyle" ister (**K**). Ekran okuyucu için tahta durumu da duyurulmuyor (`Arena.announce` kullanılmıyor).
3. **Eşleşme renge dayanıyor (D, ölçtüm).** Motif kimliği = şekil×renk (1011-1013); `pickPalette` 5+ motifte aynı şekli farklı renkle tekrar kullanıyor. 30 seviyenin **28'inde** aynı şekil-farklı renk çifti var; Seviye 1'de bile `lale: turkuaz/mercan`, Seviye 4'te `rozet: kobalt/turkuaz/mercan`, birçok seviyede `mercan/zümrüt` (kırmızı-yeşil). Renk körü oyuncu bu kenarları ayırt edemez; renk dışı ikinci bir işaret yok. **K**: "esas bilgiyi yalnız renkle verme" ([GAG](https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/)); Tint/Linx/Chuzzle renk başına desen/simge ekliyor.
4. **6×6 tahta telefonda küçük (D).** Seviye 30, 390×844: yatay taş aralığı 40 px, dikey (perspektif) ~30 px; tahta ekranın ~%25'i, altta ~190 px boş zemin (`phone6-level30.png`). Yakınlaştırma en fazla 1.3 (3539, 3578). 44-48 px dokunma hedefinin altında; uzun basma (çevir) ve sürükleme (yer değiştir) bu boyutta hataya açık (**T**).
5. **Fırın adımı zaman baskılı ve tek seferlik (D).** İğne 3.2 sn'de geçiyor, sona varınca otomatik "mat" (2921, 2957). Hareketi azalt / erişilebilirlik ayarı bunu etkilemiyor (yalnız CSS animasyonları, 760; oyun yorumu 3753-3754). Ceza yok (en iyi sır korunuyor) ama motor güçlüğü olan oyuncu "usta sır" rozetine hiç ulaşamaz. **K**: XAG 107 kontrol hızını ve zorunlu zamanlamayı ayarlanabilir yapmayı önerir.
6. **Tamamlama kartında istatistik satırı taşıyor (D).** 390 px'te `.scoreRow` scrollWidth 338 > clientWidth 310; "MOVES" ve "GLAZE" kutuları kesik (`phone-4-complete.png`). Neden: 4×`min-width:84px` + boşluklar (CSS 250-251, 366, 398).
7. **Günlük gün anahtarı ile seri gün anahtarı farklı saat diliminde (D, kod).** Oyunun günlük tahtası yerel tarih (`dailyKey` 1249), Arena serisi UTC (`core.dayKey` 611-614, `daily()` 834). Türkiye'de 00:00-03:00 arasında oynanan günlük, serinin bir önceki UTC gününe yazılır: aynı UTC gününe iki farklı günlük düşebilir ve ertesi gün seri "atlanmış gün" diye sıfırlanabilir (**T**, senaryo kodla izlendi, tarayıcıda denenmedi).
8. **Başlıktaki üst çubuk tamamlama kartının üstünde kalıyor (D).** `topbar visible on complete: true`; kartın üstü çubukla örtüşüyor (ekran görüntüsü).
9. **Döndürme tek yönlü (D).** Yalnız saat yönü; par bunu sayıyor (L1 par 22; 4 taş 3'er tık). Oyuncu açısından 3 tık = boş iş (**T**). Tatham'ın Net'i sol/sağ tık ile iki yön + klavye A/D sunuyor (**K**).
10. **Günlük kayıtlar sınırsız büyüyor (T).** Her günlük koleksiyona ekleniyor (2896-2897); `renderCollection` hepsini her açılışta yeniden üretip çiziyor (3190-3198), `pictureCache` 60 ile sınırlı. Bir yıl sonra ~365 tahta üretimi + canvas çizimi.

## 4. EKLENMELİ — yüksek değer
**4.1 Telefon alt çubuğunu yalnız oynarken göster** — Ne: `#topbar .right` alt çubuğu ve üst çubuk `playing` dışındaki ekranlarda (fırın, tamamlama, sekans) gizlensin ya da fırın/tamamlama kartı alt çubuk + `safe-area` kadar yukarı itilsin. Neden: §3.1, §3.8 regresyonu. Nasıl: `hideAll()`/`openKilnStep()`/`showComplete()` içinde `body` üzerinde `data-screen` sınıfı; CSS'te `@media (max-width:400px) body:not([data-screen=playing]) #topbar .right{display:none}`; kiln/complete kartına `max-height: calc(100dvh - …)` + `margin-bottom`. Maliyet **S**. Risk: düşük; `?auto` etkilenmez; 844×390 yatayı da kontrol et. Kanıt: §3.1 ölçümleri.

**4.2 Klavyeyle tam oynanış (odak imleci)** — Ne: ok tuşlarıyla taş imleci, Boşluk/Enter = döndür, F = çevir, X/Shift+Enter ile "al-bırak" yer değiştirme; imlecin tahtada altın çerçevesi; her hamlede `Arena.announce("Satır 2, sütun 3: 2/4 kenar eşleşti")`. Neden: §3.2; masaüstü portal oyuncularının önemli bölümü klavye kullanır (**T**), WCAG 2.1.1 (**K**). Nasıl: `G.cursor` (slot), `keydown`'a ok tuşları; mevcut `performMove({type:'rot'|'swap'|'flip'})` çağrılır — bot ve kayıt değişmez; imleç için mevcut `coach` emissive nabzı yeniden kullanılabilir (3607), ek draw call yok. Maliyet **M**. Risk: H/R/Z/M kısayollarıyla çakışma (F hem kiln hem çevirme — `G.kiln` önce kontrol ediliyor, sorun yok); ilk dokunuşta imleci gizle.

**4.3 Renkten bağımsız eşleşme işareti ("desen işareti" ayarı)** — Ne: her renge sabit küçük bir işaret (ör. kobalt = nokta, turkuaz = çift çizgi, mercan = üçgen, zümrüt = halka) motifin dibine, kenar ortasına çizilsin; ayarlardan aç/kapa, varsayılan kapalı ya da yalnız yüksek karşıtlıkta açık. Neden: §3.3 (28/30 seviye). Nasıl: yalnız `drawEdgeMotif`/`paintTile` (1564-1645) — CORE'a dokunmaz, tohumlar/par/kayıt aynı kalır; doku önbelleği anahtarına ayar eklenir (`textureCache`). Yeni ayar `arena.cini.settings` içine eklenebilir (eski kayıtlar alanı bilmez → varsayılan). Maliyet **S-M**. Risk: 128 px Low dokuda işaret okunaksız olabilir (**K**: koyu renk/küçük blokta desen zor görünür) → işaret beyaz kenarlı ve kenar ortasında büyük. Kaynak: GAG, Tint, Linx örnekleri.

**4.4 Portre kamerada büyük tahtaları büyüt** — Ne: telefon dikeyde n≥5 için kamerayı daha dik (polar ~30-34°) ve yakın yap, tahta ekran genişliğinin ~%95'ine otursun; boş zemin yerine tahta. Neden: §3.4 (40×30 px taşlar). Nasıl: `updateCamera()` (1859-1874) portre dalında `G.pz.n`'ye göre `dist/polar`; mevcut 1.3 yakınlaştırma üst sınırı n=6'da 1.6'ya. Hedef ölçüm: 6×6'da dikey aralık ≥44 px. Maliyet **S-M**. Risk: duvardaki galeri/fırın kadrajı (sekans `CAM.focus` kullanıyor, etkilenmemeli — fırın geçişini 390×844'te tekrar çek); performans nötr.

**4.5 Fırın adımını erişilebilir yap** — Ne: iğne sona gelince otomatik mat yerine 2 kez gidip gelsin (ping-pong), "Hareketi azalt" açıkken veya yeni "Rahat fırın" ayarında hız yarıya insin ya da iğne çekirdekte 0.5 sn dursun. Neden: §3.5; usta sır rozeti şu an refleks gerektiriyor. Nasıl: `updateSequence` kiln dalı (2955-2961): `k.pct` üçgen dalga; `KILN_RISE` çarpanı `Arena.settings.reducedMotion`'a bağlı. `glazeFor` saf kalır, testler değişmez. Maliyet **S**. Risk: düşük; `?auto` ve `ciniSim` zaten fırını atlıyor (2986).

## 5. EKLENEBİLİR — orta değer / koşullu
- **Ters yön döndürme** (klavyede Q/E, farede Shift+tık; telefonda Bölüm 1-2'de iki parmak dokunuşu değil, *taş üzerinde sola kaydırma* olabilir — Bölüm 2'de sürükleme yer değiştirme olduğu için yalnız klavye/fare). Koşul: par'ı ters yönle yeniden hesaplamak (`min(k,4-k)`) yıldız eşiklerini değiştirir; eski rekorlar yıldız olarak kalır ama yeni par daha sıkı olur. Ya par aynı bırakılıp ters yön 1 hamle sayılır (3 yıldız kolaylaşır) ya da yalnız Bölüm 3'te açılır. Maliyet M, risk: test + par tutarlılığı. **K**: Tatham Net.
- **Taşı kilitle / "emin işareti"** (Net'teki kilit): büyük tahtalarda yanlışlıkla döndürmeyi önler; hamle sayılmaz, kayıtta tutulmaz. Maliyet S.
- **Son 7 günün günlüğü** (arşiv şeridi): tohumlar tarihle deterministik, `?d=`/`?daykey` zaten var; seriye sayılmaz, yalnız koleksiyona. **K**: NYT Wordle arşivi, kaçan günü oynama talebi. Maliyet M. Risk: koleksiyon büyümesi (§3.10) önce çözülmeli.
- **Serbest tahta / sonsuz mod**: `randomPattern` (1336) zaten var; Atölye'nin "Rastgele"si ile 1 tık "Yeni tahta". 30 seviye bitince devam yolu. Maliyet S. Risk: kayıt anahtarı `pattern` sınırına (40 kayıt) tabi.
- **Yanlış kenar vurgusu** ayarı (ipucu harcamadan, eşleşmeyen kenarlarda soluk kırmızı çizgi): glow geometrisi zaten kenar başına; ikinci bir drawRange. Bulmacayı kolaylaştırır → yalnız isteğe bağlı. Maliyet S-M.
- **Galeri seçimi**: duvarda hangi 12 panonun asılacağını oyuncu seçsin (şu an en yeni 12). Maliyet S.

## 6. EKLENMEMELİ
- **Süre sınırı / zamana karşı mod, can/enerji sistemi**: oyunun "sakin atölye" kimliğini bozar; zaten tek zamanlı öğe (fırın) erişilebilirlik sorunu.
- **Çevrim içi sıralama, bulut kaydı, hesap**: kısıtı aşar (sunucu/hesap/veri toplama).
- **`LEVEL_DEFS`, `levelSeed`, `generateLevel`, `pickPalette` değişikliği** (ör. renk sorununu üreticide çözmek): koleksiyon resimleri ve rekorlar mevcut tohum + tanımdan yeniden üretiliyor (3019-3027); eski panolar başka desene dönüşür, par/yıldız anlamı kayar. Renk sorunu §4.3 gibi yalnız çizimde çözülmeli. Yeni seviye gerekiyorsa sona eklenmeli (L31+), mevcutlar değişmemeli.
- **Daha fazla 3D dekor/ışık/parçacık**: seviye 10'da 58 draw call (README); Intel UHD + telefon bütçesi; iyileştirme tahtanın okunurluğuna gitmeli, dekora değil.
- **Öğretici duvarı / zorunlu tanıtım videosu**: v2 bilinçli olarak kaldırdı; koç balonu yeterli.
- **Gerçek oyunlardan kopya** (Infinity Loop/Net görselleri, adları): yalnız ilke alındı.
- **ARENA-KIT bloğunu oyuna göre düzenlemek** (ör. UTC→yerel): kısıt; düzeltme oyun tarafında yapılmalı (§7).

## 7. Düzeltilmeli
- **Alt çubuk/üst çubuk çakışması** (§3.1, §3.8) — S, ilk iş.
- **`.scoreRow` taşması** 390 px'te: `min-width` 64 px, `flex-wrap` ya da 2×2 ızgara (CSS 250-251, 366, 398) — S. Doğrulama: `scrollWidth <= clientWidth`.
- **Günlük seri gün anahtarı**: oyun tarafında `Arena.daily()` yerine günlük tamamlanınca `?d` eşdeğeri yerel gün geçmek mümkün değil (kit `d` parametresini URL'den okuyor); seçenek: oyunun günlük anahtarını UTC'ye çekmek (yerel saatle 03:00'te değişir, Türkiye için kabul edilebilir ama eski `D<yerel tarih>` kayıtları korunur) ya da kit'in sonraki sürümüne `daily(game, dayKey)` parametresi önermek. Karar kullanıcıda — **T**.
- **Hareketi azalt** 3D tarafa uygulanmıyor: `CAM.shake` (2939, 2985), taş zıplaması, toz ve kedi animasyonları `Arena.settings.reducedMotion` ile kısılmalı; `Arena.on('settings', …)` var — S.
- **Koleksiyon ızgarasında günlükler**: son N (ör. 30) günlüğü göster, gerisini sayı olarak; çizimi ekran görünür olunca yap — S.
- **Tamamlama kartında ipucu rozeti/çubuk**: oyun bitince gizle (4.1 ile birlikte).
- **project-meta.json** `ci.workflows: []` ama `.github/workflows/smoke.yml` var — metadata eksik (D) — S.
- **README "locked 60 fps" ve draw call iddiaları** 10-28 Ekim ölçümü; son relay CSS değişikliğinden sonra yeniden ölçülmedi (bkz. §9).

## 8. Önerilen ilk 3 iş
1. **Telefon HUD regresyonunu düzelt + skor satırı taşması (4.1, §7)** — S. Son relay commit'i kullanıcıya görünen bir hata getirdi (Ateş düğmesi kısmen örtülü, bitmiş seviyede işlevsiz düğmeler). En ucuz, en görünür kazanç; doğrulama: 390×844 ve 844×390'da `elementFromPoint` + ekran görüntüsü, `?auto` koşusu.
2. **Renkten bağımsız eşleşme işareti (4.3)** — S-M. 30 seviyenin 28'i renk ayrımı gerektiriyor; yalnız doku çizimine dokunur, kayıt/par/bot değişmez. Erişilebilirlik panelinin yanına tek anahtar.
3. **Klavye oynanışı + ekran okuyucu duyurusu (4.2)** — M. Masaüstünde oyunun tek erişilebilirlik boşluğu; mevcut `performMove` ile yapılır, bot ve testler etkilenmez. Ardından 4.4 (portre kamera) ve 4.5 (fırın) gelir.

## 9. Doğrulanmayanlar / açık sorular
- **Performans**: makine yükü 60-78 iken FPS 10-11 (SwiftShader) ölçüldü; bu oyunun değil ortamın sınırı. Intel UHD'de 60 fps iddiası yeniden ölçülmedi.
- **`?auto` tam koşu**: bot Seviye 1'e girdi, hata yok; ama başlıkta ~75 sn bekledi — aşırı yükte rAF/`evaluate` gecikmesi mi yoksa gerçek gecikme mi ayırt edilemedi. Yük düşükken `?auto&debug` ile 30 seviye koşusu önerilir.
- Firefox/WebKit ve gerçek dokunmatik cihazda uzun basma (520 ms) + 6×6 hassasiyeti denenmedi.
- Günlük/UTC seri senaryosu yalnız kod okumasıyla; saat dilimi taklidiyle (`timezoneId: 'Europe/Istanbul'`, 00:30) tarayıcıda denenmeli.
- 844×390 yatay telefonda yeni alt çubuk CSS'i (`max-width:400px` sorgusu yatayda tetiklenmez) etkisiz olmalı — denenmedi.
- Dış kaynaklardan poki.com ve gameaccessibilityguidelines.com sayfaları bu oturumun ağ izinlerinde olmadığı için açılamadı; bilgiler arama özetlerinden.

## Kaynaklar
- [Game Accessibility Guidelines — renk tek başına bilgi taşımasın](https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/)
- [W3C — WCAG 2.1.1 Keyboard](https://w3.org/WAI/WCAG21/Understanding/keyboard)
- [Xbox Accessibility Guideline 107: Input](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107)
- [Tint — renk + desen (Assistive Technology Blog)](https://assistivetechnologyblog.com/puzzle-game-tint-combines-colors-and-patterns-for-color-blind-players)
- [Grindstone renk körü çözümü (Vice)](https://vice.com/en/article/how-grindstone-a-game-about-matching-colors-solved-its-colorblind-issue)
- [Simon Tatham — Net kontrolleri](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/net.html), [sgt-net man sayfası](https://manpages.ubuntu.com/manpages/noble/man6/sgt-net.6.html)
- [AmalgamA — Infinity Loop üzerine geliştirici notu](https://diogocosta738.github.io/amalgama.html)
- [Room 8 Studio — karo bulmaca seviye tasarımı](https://room8studio.com/news/smart-casual-the-state-of-tile-puzzle-games-level-design-part-1/)
- [NYT Wordle arşivi (TechCrunch)](https://techcrunch.com/2024/05/07/nyt-games-launches-a-wordle-archive-with-access-to-more-than-1000-past-puzzles/), [NYT yardım — seri kuralı](https://thenewyorktimeshelpcenter.helpjuice.com/24611727334932-Wordle)
- [CrazyGames — ilk kareye ulaşma](https://docs.crazygames.com/resources/getting-to-the-first-frame/), [Poki SDK gereksinimleri](https://sdk.poki.com/requirements)

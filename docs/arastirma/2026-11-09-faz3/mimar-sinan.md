# Mimar Sinan — faz 3 araştırması

Repo: `/home/user/mimar-sinan` (dal `claude/cloud-session-research-analysis-dufc2b`, origin/main'e eşit, `git status` temiz).
Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Ham çıktılar ve ekran görüntüleri: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_mimar-sinan/` (`run.cjs`, `run.log`, `01-title-desktop.png`, `03-after-collapse.png`, `04-phone-play-l2.png`).

## 1. Şu anki durum
- **D** Tek `index.html` (3187 satır, 232 KB). Sim (`canPlace`/`simulate`/`evaluate`, 1857-2018) `sim.js` ile birebir aynı; index yalnız `failingSim/topFailures/firstFailures` (2020-2030) ekliyor. `node test-levels.js`: 15/15 referans çözüm yerçekimi + deprem altında PASS.
- **D** Akış: başlık → dönem haritası (3×5, kilitli) → brief → kurma → Tahmin-Test (`openPredict` 2799, imza mekaniği "ustalık puanı") → iskele iner → yerçekimi → (ön-deprem → deprem) → sonuç (`finishTest` 2868). 3 yıldız: kubbe boyu, artan taş (`budget*par`), güvenlik payı (≤%80, depremde ≤%90).
- **D** Kayıt: `arena.mimar.settings|save|best`, ustalık ayrı anahtar (1500-1517); `load()` `Object.assign(def, …)` ile eksik alanları varsayılanla doldurduğu için eski kayıtlar yükleniyor (yeni `colorblind` alanı da böyle geldi).
- **D** `?auto` botu: `mimarSim` hızlı ileri sarma ile 15/15 sipariş, 45/45 yıldız, 0 hata, 0 yerleştirme hatası, ~1 sn (run.log).
- **D** Konsol: masaüstü (960×540, `?low`), telefon (390×844, dokunmatik) ve bot koşularında 0 hata/uyarı. Telefonda tek dokunuş parçayı koydu (`pieces:1`).
- **D** Son 3 commit dış relay'den (gemini-flash-lite): "Failure Diagnostics Panel" (3a49059), "Slow-mo Collapse Camera" (b29c4da), "Colorblind Stress Pattern Overlay" (95382c6). Üçünde de hata var (bkz. §3).
- **D** i18n: TR/EN 164'er anahtar, eksik yok; ama relay kodundaki metinler I18N dışında kalmış (2785-2793, 2957-2958).
- **D** Arena-kit entegrasyonu: `Arena.perf.attach` (2105, en fazla 1.5 DPR), otomatik duraklatma (2669), günlük (2710), paylaş (2718), rozetler (2730), "başka oyun" (2920), a11y paneli (`bA11y`, 3067). Kitin `reducedMotion` ayarı oyunda **kullanılmıyor**.
- **D** SwiftShader'da 1. siparişte 31 draw call, 26,7 bin üçgen (fps 10, yazılım GL'de anlamsız). README'deki "UHD 620'de 60 fps" iddiasını bu makinede doğrulayamadım (**K**/README).

## 2. Güçlü yanlar (korunmalı)
- **D** Gerçek, deterministik, test edilmiş statik model (orta üçte bir, itki vektörleri); her siparişin referans çözümü hem testte hem açılışta (`loadStep` 3174) doğrulanıyor. Bu, eklenecek her içeriğin güvenlik ağı.
- **D** Çöküşün öğretici olması: sonuç kartı başarısızlık nedenini parça ve koordinatla söylüyor ("İtki çizgisi orta üçte birden çıktı: Ayak (2,2)…", 03-after-collapse.png). `V` ile itki çizgisi + çekirdek (kern) çizimi (`drawLines` 2580).
- **D** Tahmin-Test + ustalık puanı: "duracak mı / ilk hangi parça düşer" sorusu oyuncuyu modeli okumaya zorluyor; bot da aynı yoldan geçiyor.
- **D** Tarihsel ders zinciri (payanda → ağırlık kulesi → yarım kubbe → 8 ayak) ve büyüyen silüet (`buildSkyline` 2638); bitirilen yerleşimler silüete giriyor.
- **D** Telefon: 12 düğmenin hiçbiri 44 px'ten küçük değil, yatay taşma yok (`scrollW 390`), telefonda otomatik Low kalite.
- **D** Sıfır varlık dosyası, sentezlenmiş ses/müzik, SRI'lı CDN, 3 tarayıcılı smoke CI.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Çöküş anında üst üste 6 tam ekran panel açılıyor ve çöküşü örtüyor (D).** `stepTest` 2856-2860: koşul `T.t === dt || T.t < dt*2`, ağır çekim `T.t`'yi kare başına 0.3·dt artırdığı için ~7 kare boyunca doğru. Adım: `?level=4&nosave`, buttress/tower olmadan referansı kur, test et → `#collapseOverlay` sayısı en fazla **6** (run.log `maxOverlays:6`). Panel `z-index 2147483999`, `backdrop-filter: blur`, 3 sn: oyunun en öğretici anını (parçanın devrilmesini) bulanıklaştırıyor. Metin TR'de bile İngilizce ("tipped: thrust > resist", ham `pier (2,2)`); `window.mimarSim.pieceName` yok (mimarSim bir fonksiyon), `window.simState` global sızıntı. Sonuç kartı aynı bilgiyi zaten düzgün veriyor, yani panel gereksiz.
2. **Ağır çekim çalışmıyor, kamera kayık kalıyor (D).** `stepCollapse(dt)` gerçek `dt` alıyor (2860), yalnız `T.t` yavaşlıyor: animasyon hızı değişmiyor, sadece kamera hedefi kayıyor. Deprem çöküşünde `T.t` 2.2'den başladığı için (`collapseT 2.27…`) ağır çekim de panel de hiç devreye girmiyor (tutarsızlık). "Onar" sonrası `camTarget` `[-0.17,0.8,-0.17]` kalıyor (önce `[0,1.2,0]`), çünkü `beginPlay` `frameLevel` çağırmıyor.
3. **Renk körlüğü deseni yanlış eşikte (D).** Desen `s ≥ 0.6`'da başlıyor (2520), yıldız eşiği 0.8. 4. siparişin 3 yıldızlı referans çözümünde 9 parçanın 9'u taranmış görünüyor (bütün gerilmeler 0.78), yani "güvenli" ile "sınırda" ayrılmıyor. Tarama, taş dokusunu tamamen siliyor. `applyTints` her yerleştirmede bütün mesh'lerde `needsUpdate = true` yapıyor (**T**: program yeniden kontrolü, büyük siparişte gereksiz maliyet). "Kapalı/Açık" etiketleri I18N dışında, lejant desenleri açıklamıyor, düğmelerde `aria-pressed` yok.
4. **390×844 telefonda parça tepsisi gerilme lejantıyla çakışıyor (D).** tools `[98,716,195×120]`, legend `[212,715,170×121]`: 81 px yatay örtüşme (04-phone-play-l2.png'de "SINIR" ve "itki çizgileri" tepsinin altında). Gereksinim çipi ("Harimi ört: 3 hücre açık") HUD'daki gerilme satırının üstüne biniyor. README yalnız 500×900'ü test ettiğini söylüyor.
5. **Günün meydan okuması kilidi atlıyor ve neyi açtığını söylemiyor (D).** `d.seed % 15` (2710); önümüzdeki 30 günde 30 günün 24'ünde 3. siparişten sonraki bir sipariş, 22'sinde 6. ve sonrası çıkıyor. Yeni oyuncu ilk gün Selimiye'yi, dersleri görmeden alabilir. Düğme metni yalnız "(seri 0 · en iyi 0)" diyor, siparişin adını vermiyor.
6. **İpucu çözümü bedavaya veriyor ve alternatif çözümleri "yanlış" sayıyor (D).** `showHint` (3001): referansın bir sonraki parçasını tam konumuyla gösteriyor, yıldız cezası yok (45 yıldız ipucuyla toplanabilir, **T**). Referansta olmayan ama geçerli bir parça "bu parça çözümde yok, kaldır" diye işaretleniyor; bu, simülasyonun serbest çözüm vaadiyle çelişiyor.
7. **Azaltılmış hareket desteklenmiyor (D).** `G.shake` (2660), deprem saha sallanması (2843) ve kamera kayması, kitin `reducedMotion` ayarına da `prefers-reduced-motion`'a da bakmıyor (**K**: GAG/IGDA, kamera sarsıntısı kapatılabilmeli).
8. Küçük: telefonda ilk toast "Sağ tık ya da boş alana sürükle" diyor (1550, dokunmatikte sağ tık yok). Bitiş kartında yerleşim sayısı "Kubbe" etiketiyle görünüyor ve "Yıldız/Stars" seçimi `star_dome` metnini bölerek yapılıyor (2919, kırılgan).

## 4. EKLENMELİ — yüksek değer
**4.1 "Neden çöktü → Sinan ne yapardı" onarım rehberi**
- *Ne:* Sonuç kartında her başarısızlık nedeni için bir çare cümlesi: `thrust` ise "itki {yön}e kaçıyor: o tarafa payanda ya da ayağın üstüne ağırlık kulesi"; `crush` ise "daha az yük ya da ayak"; `needsPiers`/`uneven` için kendi cümleleri. "Onar"a basınca ilk düşen parça 3 sn vurgulanıyor ve itki çizgisi kendiliğinden açılıyor.
- *Neden:* Oyunun değeri modeli öğretmesinde. Bugün sonuç kartı neyin kırıldığını söylüyor ama ne yapılacağını söylemiyor; ipucu ise doğrudan cevabı veriyor. Arada bir basamak eksik (**T**). Poki rehberi de öğreticinin oyunu bloklamadan mekaniği öğretmesini istiyor (**K**).
- *Nasıl:* `r.dir` ve `r.reason` zaten `simulate`'te var (1965). I18N'ye `fix_thrust/fix_crush/...` anahtarları; `finishTest` 2898'deki `note` satırına ekleme; `retryLevel`'da `G.showLines` için 3 sn zamanlayıcı ve `firstFailures` ile vurgu. Sim değişmiyor.
- *Maliyet:* S. *Risk:* düşük; bot sonuç kartını okumuyor, kayıt etkilenmiyor.

**4.2 Kademeli ipucu (açıkla → işaret et → göster)**
- *Ne:* 1. basış: en kötü ayağı ve itki yönünü gösterir (çizgiler açılır). 2. basış: hangi parça tipinin eksik olduğunu söyler. 3. basış: bugünkü "şuraya koy" gösterimi. Sonuçta ipucu kullanıldıysa yıldızların yanında küçük bir "ipuçlu" işareti çıkar ve "ipucusuz 3 yıldız" rozeti (arena `award`) verilir. "Çözümde yok, kaldır" uyarısı yalnız yerleşim başarısızsa gösterilir.
- *Neden:* §3.6. İpucu öğrenme aracı olarak kalır, otomatik çözücüye dönmez.
- *Nasıl:* `G.hintLevel` sayaç (`beginPlay`'de sıfırlanır), `showHint` 3 dala ayrılır. İpucu işareti `PROG.hinted[li]` olarak ayrı alanda tutulur; eski kayıtlarda alan yok, `Object.assign` ile `{}` gelir. Yıldız hesabı değişmez.
- *Maliyet:* M. *Risk:* kayıt uyumu iyi; bot ipucu kullanmıyor.

**4.3 Sinan'a karşı taş (referans kıyası + kişisel rekor)**
- *Ne:* Sonuç kartında "Sinan'ın çözümü: 20 taş · seninki: 22 · rekorun: 21". Haritada her siparişte en az taş rekoru. Referanstan az taşla 3 yıldız alınca rozet.
- *Neden:* Zachtronics histogramlarının sunucusuz karşılığı. Hesapsız bir hedef, çözülmüş bulmacaya geri dönme sebebi verir (**K**: SpaceChem postmortem'inde oyuncular histogramı görünce kendine hedef koyup tekrar oynuyor). Referans kullanımı zaten `evaluate(L, L.ref).used`.
- *Nasıl:* `PROG.minStone[li]`, yalnız `complete` olunca yazılır. Referans kullanımı açılışta `loadStep`'te hesaplanıp önbelleğe alınır.
- *Maliyet:* S. *Risk:* düşük. Referanstan iyi bir çözüm sim'in açığını gösterebilir; bu da yararlı bir veri (**T**).

**4.4 Günlüğü anlamlı yapmak**
- *Ne:* (a) Seçim yalnız açılmış siparişler arasından yapılır (yeni oyuncu için 1-5); düğme siparişin adını gösterir. (b) Günün kuralı: tohumdan bir kısıt. Örnekler: bütçe = referans kullanımı + %5, ya da tek bir parça tipi yasak, ya da deprem şiddeti +%20. Kısıt yalnız referans çözüm (ya da tanımlı bir alternatif) onu da geçiyorsa seçilir.
- *Neden:* §3.5. Bugün günlük, 15 sabit siparişten birinin yeniden oynanması; çözülmüşse ikinci kez ilginç değil (**T**).
- *Nasıl:* `dailyInfo` 2710: `li = unlocked[seed % unlocked.length]`. Kısıt `G.daily.rule` olarak tutulur; `L`'nin kopyasına uygulanır (`{...L, budget}`); doğrulama `evaluate(Lmod, L.ref).complete`, geçmezse sıradaki kural denenir. Kampanya kaydına dokunmaz (bugün de dokunmuyor, 2871).
- *Maliyet:* M. *Risk:* kural sim'i bozmaz, yalnız seviye verisinin kopyasını değiştirir. Bot günlüğü oynamıyor.

**4.5 Azaltılmış hareket**
- *Ne/Nasıl:* `const calm = Arena.settings.reducedMotion || matchMedia('(prefers-reduced-motion: reduce)').matches`. Bu açıkken `G.shake` sıfır, deprem genliği ×0.3 (kalıcı ama yumuşak), çöküş kamera kaydırması yok.
- *Maliyet:* S. *Risk:* yok. *Kaynak:* **K** GAG, IGDA GA-SIG.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Yerleşimi bağlantıyla paylaşma** (`#l=` + parça listesi, base64): "benim Süleymaniye'm" bağlantısı, açan kişi aynı yerleşimi izleme modunda görür. Ağ çağrısı yok, `Arena.share` zaten var. Maliyet M. Risk: URL'den gelen veri `canPlace` ile doğrulanmalı. Kayıt etkilenmez. (**K** share-code deseni: Ultimate Chicken Horse, Platformer Playground.)
- **Serbest atölye** (15 sipariş bittikten sonra açılır): seçilen ızgara, bütçe yok, deprem şiddeti kaydırıcısı. Maliyet M. Risk: performans (büyük ızgarada çok sayıda mesh), sınır koyulmalı (ör. en fazla 13×13).
- **Yerleştirmeden önce gerilme önizlemesi**: hayalet parça üzerindeyken `evaluate(G.L, [...G.pieces, ghost])` ile en kötü gerilme değişimi ("+%18") gösterilir. Sim küçük ve hızlı (**T**), ama zayıf telefonda hover başına ölçülmeli; sınırla (ör. hücre değişince bir kez). Maliyet S-M. Tahmin-Test'in sürprizini azaltabilir, ayardan kapatılabilmeli.
- **Tahmin akışını hızlandırma**: `Space` iki kez = tahmin atla. İmza mekaniği zorunlu kalır, yalnız tekrar testlerde sürtünme azalır. Maliyet S.
- **Gerçek ağır çekim + "tekrar izle"**: `stepCollapse(simDt)` ile ilk 1 sn %30 hız, sonuç kartında "çöküşü tekrar izle" (anlık görüntüden `startCollapse` yeniden). Yalnız §7.1 düzeltildikten sonra. Maliyet S.
- **İlk 30 sn rehberi** (`Arena.hint`, 1. siparişte tek seferlik): "tepsiden duvar seç → köşe hücresine dokun → kubbe → iskeleyi kaldır". Bugün yalnız yörünge toast'ı var. Maliyet S.

## 6. EKLENMEMELİ
- **Hazır fizik motoru** (cannon/ammo/rapier): CDN dışı bağımlılık, determinizm ve `test-levels.js`/bot garantisi kaybolur, UHD'de maliyetli. Oyunun özü kendi statik modeli.
- **Sunucu tabanlı sıralama ya da histogram**: kısıtı aşar (sunucu, kullanıcı verisi). Yerine §4.3.
- **Referans çözümü olmayan prosedürel siparişler**: "her siparişin geçen bir çözümü var" garantisini ve botu bozar. Günlük kısıtlar yalnız doğrulanmış seviyelere uygulanmalı (§4.4).
- **Süre baskısı, can/enerji, reklam**: düşünmeye dayalı bir bulmacada sıkıntı verir; tür beklentisine ters (**T**).
- **Ekranı kaplayan yeni modal paneller** (relay'in çöküş paneli gibi): oyuncunun izlemesi gereken anı örtüyor. Bilgi sonuç kartına ya da küçük, kenarda bir toast'a gitmeli.
- **Poly Bridge vb. bir oyunun arayüzünü, araç/seviye tasarımını kopyalamak**. Bütçe + yük testi türü serbest, kopya değil.
- **Mevcut ipucunu daha da otomatikleştirmek** ("tümünü çöz" düğmesi): öğrenmeyi ve yıldızların anlamını öldürür.

## 7. Düzeltilmeli
1. `displayCollapseOverlay` (2783-2797) ve çağrısını (2856-2859) kaldır ya da tek seferlik, I18N'li, kenarda duran, bulanıklaştırmayan bir toast'a çevir. `window.simState` sızıntısını sil. Sonuç kartı zaten aynı bilgiyi veriyor. (§3.1, D)
2. Ağır çekim: `stepCollapse(simDt)` kullan, deprem çöküşünde de `T.t = 0` yap (2846), `retryLevel`/`beginPlay`'de `frameLevel()` ya da kamera hedefini geri yükle. Ya da özelliği tamamen kaldır. (§3.2, D)
3. Renk körlüğü: desen eşiklerini yıldız/sınır eşikleriyle hizala (≥0.8 çizgili, ≥1.0 çapraz). Haritayı yalnız değiştiğinde ata, `needsUpdate`'i yalnız o zaman koy. Etiketleri I18N'ye taşı, `aria-pressed` ekle, lejanta desen örneği koy. (§3.3, D)
4. 390 px telefon düzeni: legend'i dikey telefonda daralt ya da tepsi açıkken gizle/tepsinin üstüne taşı; gereksinim çipini HUD'un altına it. 360×740 ve 390×844'te ekran görüntüsüyle doğrula. (§3.4, D)
5. Telefonda yörünge toast'ı: dokunmatik için ayrı metin ("boş alanı sürükle, iki parmakla yakınlaştır/çevir"). (§3.8, D)
6. Bitiş kartı etiketleri: yerleşim sayısı için ayrı anahtar, "Yıldız/Stars" için I18N anahtarı. (§3.8, D)
7. Ayarlar ve smoke: relay commit'leri smoke'tan geçti ama davranış hatası taşıyor. Smoke'a "çöküş testi: `#collapseOverlay` sayısı ≤1, konsol 0 hata" ve 390×844 düzen örtüşme kontrolü eklenebilir. (**T**)

## 8. Önerilen ilk 3 iş
1. **Relay regresyonlarını temizle (§7.1-7.3).** Gerekçe: ölçülmüş hatalar oyunun en öğretici anını (çöküşü) bozuyor, TR oyuncuya İngilizce ham metin gösteriyor, renk körlüğü modu güvenli yapıyı "tehlikeli" gösteriyor. Maliyet S, sim'e dokunmaz; `test-levels.js` + bot + smoke ile doğrulanır.
2. **Onarım rehberi + kademeli ipucu (§4.1 + §4.2).** Gerekçe: oyunun vaadi Sinan'ın derslerini öğretmek. Bugün başarısızlık ile cevap arasındaki basamak eksik. Tahmin-Test imza mekaniğini güçlendirir, kayıt uyumlu.
3. **390 px telefon düzeni + azaltılmış hareket + anlamlı günlük (§7.4, §4.5, §4.4a).** Gerekçe: telefon desteği kısıtlarda zorunlu ve bugün çakışma var. Günlüğün kilitli geç siparişleri yeni oyuncuya açması, ilk oturumda en zor içeriğe yönlendiriyor. Hepsi S; §4.4b (günün kuralı) ve §4.3 sonraki tura kalabilir.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek Intel UHD/telefon GPU'sunda fps ölçülmedi; SwiftShader sayıları (fps 10) anlamsız, makine yükü 50-70 idi. README'deki 60 fps iddiası **K** olarak kaldı.
- Renk körlüğü `needsUpdate` maliyetinin büyük siparişte (Süleymaniye, ~70 parça) kare süresine etkisi ölçülmedi (**T**).
- İpucuyla 45 yıldız toplanabildiği çıkarım (`showHint` kodu); oyuncu verisi yok.
- Firefox/WebKit'te koşmadım (CI'da var). 360 px ve yatay telefon düzeni kontrol edilmedi.
- Arena-kit'in `reducedMotion` ayarının diğer oyunlarda nasıl kullanıldığına bakmadım. Ortak bir yardımcı mı olmalı, oyun başına mı?
- Günlük dağılımı `hash('mimar-sinan:'+gün)%15` ile hesaplandı. GitHub Pages'te `gameId`'nin `mimar-sinan` çözüldüğünü varsaydım (yol ya da meta).

## Kaynaklar
- Game Accessibility Guidelines, renk tek başına bilgi taşımamalı: https://gameaccessibilityguidelines.com/?p=21 ; ilgili sayfa: https://gameaccessibilityguidelines.com/?p=3102
- IGDA GA-SIG Top Ten (renge ek olarak desen/şekil; kontrol dışı kamera hareketi, ekran sarsıntısı): https://igda-gasig.org/?p=3480 , https://igda-gasig.org/?p=42
- Xbox Accessibility Guideline 103 (renk): https://learn.microsoft.com/da-dk/gaming/accessibility/xbox-accessibility-guidelines/103
- SpaceChem postmortem (histogram, sıralama yerine kişisel hedef): https://gamedeveloper.com/design/postmortem-zachtronics-industries-i-spacechem-i-
- Opus Magnum histogramları ve çok amaçlı optimizasyon: https://pcgamer.com/perfectly-solving-opus-magnums-puzzles-is-impossible-but-thats-ok
- Poly Bridge (bütçe + yük testi türü): https://en.wikipedia.org/wiki/Poly_Bridge_(video_game)
- Poki geliştirici rehberi (öğretici oynanışı bloklamamalı, mobil erken düşünülmeli): https://developers.poki.com/guide/easy-access
- CrazyGames kalite gereksinimleri ve Basic Launch ölçüleri: https://docs.crazygames.com/requirements/quality/ , https://docs.crazygames.com/resources/basic-launch-metrics/
- Paylaşım kodu deseni: https://ultimate-chicken-horse.fandom.com/wiki/Custom_Levels , https://mindwiredlabs.itch.io/platformer-playground

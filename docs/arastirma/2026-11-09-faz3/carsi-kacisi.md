# Çarşı Kaçışı — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm (kod satırı, Playwright çıktısı ya da betik), **T** = tahmin/çıkarım, **K** = dış kaynak.
Ölçüm ortamı: headless Chromium + SwiftShader, CDN yerel kopyadan; makine çok yüklüydü (load average 70-80), bu yüzden **gerçek zamanlı fps ve zamanlama ölçümleri güvenilir değil**. Mantık testleri `carsi.sim()` (senkron simülasyon) ile yapıldı. Betikler ve ekran görüntüleri: `_carsi-kacisi/` (`run1.cjs`, `run2b.cjs`, `p1-title.png`, `p2-play.png`). Repo değiştirilmedi (`git status` temiz).

## 1. Şu anki durum
- **D** Tek dosya `index.html` (3031 satır, 167 KB), Three.js r170 importmap + SRI (660-665), ARENA-KIT bloğu 306-659. Bağımlılık yok, build adımı yok.
- **D** Oyun döngüsü: sabit adım `STEP = 1/120` (1064), kare başına en fazla 12 adım, `dt` 0.05 ile sınırlı (2942-2972). Fizik: kutu + kubbe yükseklik alanı (`groundAt` 1296), duvar itme (1389), çift zıplama, kubbe kayması, çamaşır ipi, kayan tahta, kırılan çini, rüzgâr.
- **D** İlerleme: 10 el yapımı bölüm, layout dizgeleri (1002-1025), sırayla açılır (`unlocked` 2557); bölüm başına 3 yıldız (süre ≤ uzunluk/5, lokumun %80'i, 0 düşme; `starsOf` 2558); numaralı kapı ara zamanları, bölüm başına 1 lonca işareti, imza mekaniği **Zincir Tezgâh** (devrilen tezgâh kediyi yavaşlatır, ×N kombo; 1497-1509, commit f3eac74).
- **D** Kayıt: `arena.carsi.settings`, `arena.carsi.save` (`done[]`, `signs[]`, `seen{}`), `arena.carsi.best` (`lv[i] = {stars,time,lok,falls,splits}`); `lsGet` eksik alanı varsayılanla doldurur, eski kayıtlar yüklenir (899-923).
- **D** Bot (`?auto`, 1607-1635): `carsi.sim` ile 10/10 bölümü **0 düşüşle** bitirdi (43.8-56.8 sn oyun süresi); yıldızlar `101` ×7, `111` ×3 (bot lokum toplamaya çalışmıyor). 0 JS hatası. **Ama** bu geçiş aşağıdaki coyote hatası yüzünden fazla bağışlayıcı (bkz. 3.1).
- **D** i18n: `TX.tr/en` (926-991), `L` tuşu, `?lang=`; varsayılan tarayıcı diline göre.
- **D** Ses: tamamen Web Audio; tek 16 adımlık hicaz döngüsü 96 BPM (2463-2550), bölüm ya da tempo değişmiyor.
- **D** Performans: başlangıçta 49 draw call, **~868 000 üçgen** (`?debug` çıktısı, 390×844 ve 960×540). Gölge 1024², düşük kalitede gölge yok, pixel ratio ≤1.5, arena-kit dinamik çözünürlüğü bağlı (2781-2787).
- **D** Mobil: dokunmatik cihazda `autoRun` varsayılan açık (908), bu durumda sanal çubuk ve butonlar **hiç görünmüyor** (2901-2902; ölçüm: `#touch` computed `display:none`). Kontrol: ekranın sağ yarısına dokun = zıpla, basılı tut = kay.
- **D** Son iki "relay" commit'i (e539316 coyote/jump buffer, 167c7f8 tek el auto-run) Gemini Flash-Lite ile yapıldı; aşağıdaki en ciddi iki hata bu commit'lerden geliyor.

## 2. Güçlü yanlar (korunmalı)
- **D** Sabit adımlı deterministik simülasyon + `window.carsi`/`carsiSim` test kancaları: bot doğrulaması 10 bölümü saniyeler içinde koşuyor (bölüm başına 72-1327 ms).
- **D** Çizim bütçesi disiplini: statik dünya tek birleşik mesh + tek mürekkep mesh'i, tezgâhlar/lokum/tente InstancedMesh, kapı numaraları tek atlas (1120-1128, 2017-2024, 2054-2074).
- **D** İlk karşılaşma ipuçları engelin üstünde, tür başına bir kez, hareketi engellemiyor (2362-2410). **K** Poki'nin "10 saniyede eğlence" ölçütüne uygun bir yapı.
- **D** Zincir Tezgâh dengesi güvenli: kedi hiçbir zaman 5 birimden yakına gelmiyor (1527-1528), tezgâhların çarpışması yok — yol tıkanmıyor.
- **D** Kayıt dayanıklılığı: her erişim try/catch, `persistProgress` bilinmeyen alanları koruyor (921-922).
- **D** Kimlik: cel-shading, mürekkep çizgileri, Van kedisi, kaynaklı lonca bilgileri (1028-1047, her biri URL'li).
- **D** Kayan tahtada düz koşan oyuncu her zaman tahtanın üstünde kalıyor (tahta yarı genişliği 2 > salınım 1.5), yani yan kontrol olmadan da geçilebiliyor.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Coyote süresi duvar saatine bağlı → üçlü zıplama ve sınırsız coyote (D).** `stepPlayer` (1331-1333) `performance.now()` kullanıyor; sabit adımlı simülasyonda oyun zamanı yerine gerçek zaman. Yerden ayrıldıktan sonraki 0.12 sn *gerçek zaman* boyunca coyote her adımda yeniden doluyor. Ayrıca 1351'deki ek koşul (`P.y <= h + SNAP + 0.5`) yükselirken de zemin zıplamasına izin veriyor.
   - Kanıt (sim, `run1.cjs sim`): zıplamadan 0.05 / 0.3 / 0.6 sn sonra ikinci basışta `vy` her seferinde **10.9** (tam yer zıplaması 11.4, çift zıplama 9.6 olmalı). 0.3 sn arayla toplam yükselme **4.15**; doğru çift zıplamayla tepe ≈ 3.7.
   - Gerçek oyunda (60 fps) ilk ~0.12 sn içindeki ikinci basış tam zıplama verir ve `airJump=1` kaldığı için üçüncü zıplama da gelir (T, kod okuması; yük nedeniyle gerçek zamanda ölçülemedi). Düşük fps'de (her karede 6 adım, aynı `now`) pencere daha da büyür (T).
   - `carsiSim` içinde duvar saati neredeyse durduğu için havadayken coyote **hiç bitmiyor**: botun "10/10, 0 düşme" sonucu oyuncunun gerçek kurallarıyla elde edilmiyor. README'deki doğrulama iddiası bu yüzden zayıf.
   - Kaynak: e539316 (relay). Kayıt uyumu: etkisi yok.
2. **Telefonda auto-run kapatılınca oyun oynanamaz hale geliyor (D).** `touchUi` (2901) auto-run'ı yalnız sayfa yüklenirken okuyor ve `#touch`'a satır içi `display:none` yazıyor. Ayarlardan auto-run kapatılınca: `autoRun:false`, `#touch` hâlâ `display:none`, oyuncu `vz=0` (ölçüm `run2b.cjs`: `AUTORUN OFF {"autoRun":false,"touchDisplay":"none", ... "vz":0}`). İleri gidecek kontrol yok; sayfa yenilenene kadar takılı kalıyor. Masaüstünde açınca tersi: auto-run açık ama dokunma dinleyicisi yok (sorun değil, klavye var).
3. **Telefonda yanal kontrol yok (D).** Auto-run açıkken çubuk gizli; sol yarı yalnız kamerayı döndürüyor ve `readInput` hareket yönü için `camManual`'ı değil `camYaw`'ı kullanıyor (1597). Ölçüm: sol yarıda 1.5 sn sürükleme → `x` 0'da kaldı. Sonuç: telefonda tezgâh (x = -1.6/0/1.6) ve kenardaki lokum hedeflenemiyor; Zincir Tezgâh (imza mekaniği) ve lokum yıldızı büyük ölçüde şansa kalıyor (T). Bot bile lokum yıldızını 10'da 7 bölümde kaçırıyor ve yanal yönlendirme kullanıyor (D).
4. **Basılı tutup kaydıktan sonra bırakınca istem dışı zıplama (D).** 2907: zamanlayıcı ateşlendikten sonra `touchHoldTimer` sıfırlanmıyor, 2913'te bırakışta `jumpQ = true`. Ölçüm: 450 ms basılı tutma → bırakınca zıplama (`firstJumpMs` kaydedildi). Kayma her zaman zıplamayla bitiyor; kubbe/tezgâh kaymasında düşmeye yol açabilir (T).
5. **Zıplama bırakışta (pointerup) tetikleniyor (D, 2910-2914):** dokunma süresi kadar gecikme ekliyor; koşu oyununda zıplama basışta olmalı (T/K).
6. **Bölüm içeriği tekrarlıyor (D, layout analizi).** Her bölüm iki yarıdan oluşuyor (1003); 20 yarının **16'sı** başka bir bölümde birebir ya da %85+ aynı: B1-2.yarı = B4-1.yarı (38/38 token), B1-1 = B8-2, B2-2 ≈ B5-1, B2-1 = B9-2, B3-1 = B10-2, B4-2 ≈ B7-1, B6-2 ≈ B9-1, B7-2 = B10-1. Yaklaşık 12 benzersiz segment var. Oyuncu B4'e girince B1'in ikinci yarısını yeniden oynuyor; son bölüm (B10) tamamen eski parçalar. Ayrıca zorluk eğrisi düz: bölüm uzunluğu 346-443, kubbe/çini/ip sayıları dalgalı, yeni tehlike B5'ten sonra gelmiyor (D sayım).
7. **Rüzgâr neredeyse etkisiz (T, sabitlerden hesap).** Rüzgâr ivmesi en fazla 19 (1312); hareket girdisi varken `approach` ivmesi yerde 55, havada 22 (1341) ve yatay hedef hız 0 olduğu için sürüklenme her adımda sıfırlanıyor. Auto-run'da hareket hep var → "rüzgâra karşı yön tut" ipucu (950) karşılıksız. Yalnız havada hiç tuşa basılmadığında (ivme 4) itiyor.
8. **Telefon HUD'u taşıyor (D, `p2-play.png`).** 390 px genişlikte sağ grupta dil düğmesi (EN) kesik; ayrıca tezgâh sayacı görünür olunca daha da genişleyecek (T).
9. **Telefonda başlık kartı klavye tuşlarını anlatıyor (D, `p1-title.png`)**; dokunma kontrolünü (sağa dokun = zıpla, basılı tut = kay) anlatan hiçbir şey yok. İpuçlarındaki `keyName` (2367-2372) `#touch.hidden`'a baktığı için "Zıpla"/"Kay" diyor ama ekranda buton yok (D).
10. **Erişilebilirlik bağlantıları eksik (D).** Arena paneli "hareketi azalt" ve "yazı boyutu" sunuyor ama oyun: hız FOV'unu yalnız CSS medya sorgusuna göre kapatıyor (2201), `--arena-text-scale` oyunun CSS'inde hiç kullanılmıyor (grep: yalnız ARENA-KIT bloğunda). Oyunun kendi `visibilitychange` dinleyicisi (2929) arena "sekme değişince duraklat" kapatılsa da duraklatıyor.
11. **Lonca bilgileri tekrarlıyor (D, 1540):** 10 işaret, 6 bilgi (`FACTS[i % 6]`); B7-B10 aynı bilgileri gösteriyor.
12. **Arka plan üçgen yükü (D/T):** ~868k üçgen; büyük kısmı arka plandaki 2360 kubbe + mürekkep kopyası (1663-1709). Kubbesiz %25 hücre 0.0001 ölçekle yine çiziliyor (1692-1694). UHD 620'de fill/vertex maliyeti (T; gerçek GPU'da ölçülmedi).
13. **Müzik tekdüze (D):** tek döngü; bölüm, gece, kedi yakınlığı ya da kombo ile değişmiyor.
14. Küçük (D): auto-run düğmesi `applyQuality()` çağırıyor (2831) → tüm materyaller `needsUpdate`, gereksiz shader derleme takılması (T). `autoRun` dokunmatik dizüstünde de varsayılan açık (`'ontouchstart' in window`, 908).

## 4. EKLENMELİ — yüksek değer
**4.1 Coyote/jump-buffer'ı oyun zamanına taşı (hata düzeltmesi, ama değeri yüksek)**
- Ne: `groundTime`'ı `L.time` (ya da adım sayacı) ile tut; zıplayınca coyote'u kapat; 1351'deki ek koşulu yalnız `P.vy <= 0` iken geçerli yap.
- Neden: üçlü zıplama boşluk tasarımını delip geçiyor; bot doğrulaması gerçek kuralları test etmiyor.
- Nasıl: `P.coyote = wasG ? COYOTE : Math.max(0, P.coyote - dt)` (relay öncesi hal) + `jumpBuf` için yalnız düşerken zemin yakınlığı. Sonra `?auto` + `carsi.sim` ile 10 bölümü yeniden koş; bir bölüm düşerse layout'u değil botu düzelt.
- Maliyet S. Risk: bot bazı bölümlerde düşebilir (önceki doğrulama coyote'suz yapılmıştı, T). Kayıt: etkisiz. **K** Celeste/Maddy Thorson: coyote ve buffer *kısa* pencerelerdir (≈5-7 kare).

**4.2 Telefon kontrol şemasını yeniden kur: auto-run + yanal kaydırma (lane-swipe benzeri)**
- Ne: auto-run açıkken sol yarıda yatay sürükleme = yanal hareket (`INPUT.touchX`), sağ yarı basış = zıpla (pointerdown'da), aşağı kaydırma ya da ikinci buton = kay. Auto-run kapalıyken mevcut çubuk + butonlar. Ayar değişince dinleyiciler ve `#touch` görünürlüğü anında güncellensin (satır içi `display` yerine `hidden`/sınıf).
- Neden: 3.2-3.5'teki dört hata; imza mekaniği telefonda hedeflenebilir olur. **K** auto-runner'larda tek el "bir taraf hareket, diğer taraf zıpla" ve swipe kalıpları yaygın; sürekli buton tutmak yorucu, auto modlar çözüm.
- Nasıl: `touchUi`'yi `S.autoRun`'a her olayda bakan tek dinleyici setine çevir; `slideQ` sonrası `touchHoldTimer = null`; kısa bir dokunma talimatı kartı ("Sağa dokun: zıpla · basılı tut: kay · solda kaydır: yön").
- Maliyet M. Risk: bot etkilenmez (`botInput` ayrı). Mobil test 390×844 ve yatayda şart.

**4.3 Telefon HUD ve başlık kartı düzeni**
- Ne: ≤420 px'de dil düğmesini HUD'dan çıkar (ayarlarda zaten var) ya da iki satıra böl; başlık kartında `keys` yerine dokunmatik cihazda dokunma talimatı.
- Neden: 3.8-3.9 (D ekran görüntüsü). **K** Poki: portrait oynanabilirlik oyuncuların oyuna girişini artırıyor ve zorunlu.
- Maliyet S. Risk düşük.

**4.4 Kişisel en iyi "hayalet" (ghost) koşucu**
- Ne: bölüm başına en iyi koşunun konumlarını 10 Hz örnekle (`z,x,y` ≈ 60 sn × 10 × 3 = 1800 sayı, int16'ya yuvarlanınca ~3-4 KB/bölüm) `arena.carsi.ghost` altına kaydet; yeniden oynarken yarı saydam tek mesh olarak göster. Kapı ara zamanları zaten var; hayalet onları görünür kılar.
- Neden: oyunun asıl tekrar döngüsü yıldız + süre; 10 bölümlük içerikte tekrar değeri en ucuz böyle artar. **K** Super Mario Galaxy / Messenger Mouse: kendi en iyi koşuna karşı yarış, oyuncu yorumlarında "geçmiş kendinle yarış" (anekdot, tutundurma verisi yok).
- Nasıl: yeni anahtar (eski kayıtlar etkilenmez), boyut sınırı + try/catch; hayalet yalnız deterministik sim zamanına göre örneklenir (4.1 önce yapılmalı). Ayarlarda kapatılabilir.
- Maliyet M. Risk: localStorage kotası (10 bölüm × 4 KB önemsiz), 1 ek draw call.

**4.5 Tekrarlanan yarıları yeni segmentlerle değiştir (en az B4-B10)**
- Ne: 8 tekrar çiftinden en görünür olanları (B4-1, B8-2, B9-2, B10'un ikisi) yeni layout'larla değiştir; yeni segmentlerde mevcut tokenların zor kombinasyonları (ip→kayan tahta, rüzgâr içinde kırılan çini, tezgâh zinciri için uzun düz çatılar) ve sona doğru artan yoğunluk.
- Neden: 3.6 (D). Zorluk eğrisi ve "yeni yer" hissi.
- Nasıl: yalnız `LEVELS[i].layout` dizgeleri; her yeni segment bot ile (4.1'den sonra) 0 düşüşle doğrulanmalı; par otomatik (uzunluk/5). Eski `best` kayıtları anlamını kısmen yitirir (süreler artık başka yol için) → `arena.carsi.best` içine `layoutVer` ekleyip farklıysa yalnız `splits`'i sıfırla, yıldızları koru.
- Maliyet M. Risk: kayıt anlamı (yukarıdaki göç ile çözülür), bot doğrulama süresi.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Rüzgârı gerçekten hissedilir yap (S):** rüzgârı `approach` sonrasına değil, hedef hıza (`inp.mx*sp + wind*k`) ekle ya da yatay ivmeyi rüzgâr bölgesinde düşür. Ancak 4.2'deki yanal kontrol olmadan telefonda haksız olur — **koşul: 4.2 önce**. Botun yanal düzeltmesi var, doğrulanmalı.
- **Erişilebilirlik bağlantıları (S):** `Arena.settings.reducedMotion` → hız FOV'u ve kubbe kaymasındaki FOV artışı kapalı; `--arena-text-scale` toast/HUD/kart yazılarına; `autoPause` ayarına oyunun kendi dinleyicisi de uysun. **K** Xbox XAG 117, Game Accessibility Guidelines: kamera hareketi efektleri kapatılabilir olmalı.
- **"Rahat mod" / yavaş oyun hızı (S-M):** sim adımını değiştirmeden `RUN` ve kedi hızını %85'e çeken seçenek; yıldızlardan süre yıldızı bu modda verilmez. **K** Celeste Assist Mode oyun hızı. Kayıtla uyumlu (yeni ayar alanı).
- **Lonca bilgisini 10'a çıkar (S):** 4 yeni *kaynaklı* bilgi (Kapalıçarşı hanları, bedestenler; Wikipedia/İBB kaynaklı). Kaynaksız bilgi eklenmemeli.
- **Dinamik müzik katmanı (S):** kedi `lead < 7.5` iken ya da kombo ≥2 iken darbuka yoğunluğu/tempo +%10; gece bölümlerinde farklı melodi dizisi. Maliyet düşük, Web Audio zaten var.
- **Arka plan üçgen bütçesi (S):** arka plan kubbelerini daha az segmentle (`SphereGeometry(1,8,4)`), kubbesiz hücreleri `count` dışına al, uzak kubbe mürekkebini düşük kalitede kapat. Görsel değişiklik çok az; UHD için pay (T, gerçek GPU'da ölçülmeli).
- **Zincir Tezgâh için bölüm başına "en iyi kombo" kaydı ve sonuç kartında satır (S):** `L.bestCombo` zaten hesaplanıyor; `best.lv[i].combo` olarak eklenir (yeni alan, eski kayıt uyumlu).

## 6. EKLENMEMELİ
- **Çevrimiçi skor tablosu / hayalet paylaşımı sunucuda:** sunucu ve hesap gerektirir, kısıtı aşar. (Paylaş metni zaten var.)
- **Prosedürel sonsuz mod / rastgele bölüm üretici:** el yapımı ve bot doğrulamalı layout tasarımı oyunun gücü; rastgele segmentler doğrulanamaz boşluklar üretir, `?auto` garantisi bozulur.
- **Daha fazla hava zıplaması / dash eklemek:** 3.1 düzelince mevcut çift zıplama + kayma dengesi bölümlere göre ayarlı; yeni hareket bütün layout'ları yeniden doğrulamayı gerektirir.
- **Sürekli sanal çubuğu telefonda zorunlu kılmak:** **K** sanal joystick ekranı kapatıyor ve koşu oyunlarında swipe/dokunma bölgeleri tercih ediliyor; çubuk yalnız auto-run kapalıyken kalmalı.
- **Ekran sarsıntısı, hareket bulanıklığı, tam ekran flaş:** erişilebilirlik ve UHD performansı açısından zararlı (**K** XAG 117).
- **Gerçek bir oyunun karakteri/haritası (ör. bilinen bir koşu oyununun çizgisel şeritleri, Skyfall sahnesi canlandırması):** kopya riski; Skyfall yalnız kaynaklı bilgi olarak kalmalı.
- **Ek CDN modülü (ör. post-processing outline):** importmap/SRI satırları düzenlenmez; mevcut ters-gövde mürekkep yeterli.

## 7. Düzeltilmeli
1. Coyote/buffer duvar saati hatası (3.1) — 1331-1333, 1351.
2. Auto-run ayarı değişince kontrol şemasının güncellenmemesi (3.2) — 2901-2916, 2831.
3. Basılı tutup bırakınca istem dışı zıplama (3.4) — 2907 (`touchHoldTimer = null` eksik); zıplamayı pointerdown'a al (3.5).
4. Telefon HUD taşması (3.8) ve başlık kartındaki klavye metni (3.9).
5. İpuçlarındaki tuş adı: buton yokken "Zıpla"/"Kay" yerine "sağa dokun"/"basılı tut" (2367-2372).
6. Arena reduced-motion / text-scale / autoPause bağlantısı (3.10).
7. Auto-run düğmesinde gereksiz `applyQuality()` (2831).
8. README "bot 10/10, 0 düşme" iddiası 3.1 düzeltildikten sonra yeniden ölçülmeli; ölçülene kadar iddia "coyote hatalı simde" notuyla zayıf.

## 8. Önerilen ilk 3 iş
1. **Coyote/jump-buffer'ı oyun zamanına taşı + botla 10 bölümü yeniden doğrula (S).** Hem oyuncu kuralını (üçlü zıplama) hem de bütün doğrulama zincirini (bot, README iddiası, gelecekteki hayalet) etkileyen tek hata; diğer her şeyin ölçümü buna dayanıyor.
2. **Telefon kontrol şemasını onar ve tamamla (M):** auto-run ayarı canlı uygulanmalı (şu an kapatınca oyun kilitleniyor), hold→kay sonrası zıplama hatası, zıplama basışta, sol yarıda yanal sürükleme, dokunma talimatı ve HUD taşması. Telefon kitlesi için oyun şu an yarım oynanabilir; imza mekaniği (tezgâh hedefleme) telefonda erişilemez.
3. **Tekrarlanan bölüm yarılarını yeni segmentlerle değiştir (M), ardından hayalet koşucu (M).** Önce içerik (16/20 yarı tekrar), sonra en iyi koşuya karşı hayalet; ikisi birlikte 10 bölümün tekrar değerini artırır. Hayalet 1. işe bağımlı (deterministik zaman).

## 9. Doğrulanmayanlar / açık sorular
- Gerçek zamanlı üçlü zıplama penceresi 60 fps'de ölçülemedi (makine yükü nedeniyle oyun zamanı ilerlemedi: 6 sn duvar saatinde `t=0.15`). Mantık sim ile doğrulandı; gerçek tarayıcıda 1 kez daha denenmeli.
- Masaüstü ekran görüntüleri yük nedeniyle zaman aşımına uğradı; masaüstü düzeni ölçülmedi (yalnız 390×844 telefon).
- Gerçek UHD 620'de fps/üçgen etkisi ölçülmedi; README'deki 60 fps headless ölçümü bu oturumda tekrarlanamadı (gözlenen fps 20-46, yük altında anlamsız).
- Coyote hatası düzeltilince botun 10/10 0 düşmeyle geçip geçmediği bilinmiyor (e539316 öncesi coyote 0.12 sn oyun zamanıydı; o halde doğrulanmıştı — README v2 notu).
- Rüzgârın etkisizliği sabitlerden hesaplandı (T), sim ile ölçülmedi.
- Kayan kaymanın (`slideQ` 250 ms) gerçekten kubbede düşüşe yol açıp açmadığı ölçülmedi.
- Hayalet için localStorage kotası portal iframe'lerinde (itch.io, Playgama) farklı olabilir; try/catch ile sessiz düşmeli.

## Kaynaklar
- Maddy Thorson, "Celeste & Forgiveness" — https://maddymakesgames.com/articles/celeste_and_forgiveness/
- Coyote time ve input buffering açıklaması — https://bugnet.io/blog/coyote-time-and-input-buffering-explained
- Mobil kontrol kalıpları (auto-run, tek el, swipe vs. joystick) — https://www.abratabia.com/game-controls/best-mobile-controls.php ; https://cursa.app/en/page/touch-controls-for-mobile-games-input-patterns-and-feedback ; https://bugnet.io/blog/how-to-fix-no-toggle-sprint-causing-hand-strain-mobile
- Mikey Shorts mobil platform kontrol vaka çalışması — https://gamedeveloper.com/design/mikey-shorts-a-case-study-of-optimizing-controls-for-mobile-platformers
- Hayalet yarışı örnekleri — https://TVTropes.org/pmwiki/pmwiki.php/Main/RacingGhost ; https://troystorygames.itch.io/messenger-mouse/devlog/945109/record-and-replay-ghost-races
- Poki: yüksek kaliteli tarayıcı oyunu, portrait, ilk saniyeler — https://poki.com/blog/what-makes-high-quality-browser-game ; https://developers.poki.com/guide/easy-access ; https://poki.com/blog/building-web-browser-games-2026
- Xbox Accessibility Guideline 117 (hareket ayarları) — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117
- Game Accessibility Guidelines — https://gameaccessibilityguidelines.com/intermediate/
- Celeste assist mode / oyun hızı (erişilebilirlik seçenekleri derlemesi) — https://www.thegamer.com/best-video-game-accessibility-options/

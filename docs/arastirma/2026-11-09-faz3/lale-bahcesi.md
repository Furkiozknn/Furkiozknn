# Lale Bahçesi — faz 3 araştırması

Kapsam: `/home/user/lale-bahcesi` @ 765716e (origin/main ile aynı). Bu commit, brief'te anlatılan durumun üstüne gelen üç Gemini relay commit'ini de içeriyor (a4d159a, e052030, ad925d0). Depoda hiçbir dosya değişmedi.
Ölçüm ortamı: headless Chromium (Playwright, swiftshader); CDN yerel kopyadan servis edildi; 960×540 masaüstü ve 360/390/412/600 px telefon. Makine aşırı yüklüydü (load 70-80), bu yüzden fps ölçümü güvenilir değil.
Geçici dosyalar ve ekran görüntüleri: `.../scratchpad/arastirma/_lale-bahcesi/` (`run.cjs`, `bloom.cjs`, `2-desktop-bloom.png`, `4-phone-tile.png`, `5-phone-cat.png`, `6-auto-end.png`).

## 1. Şu anki durum
- **D** Tek dosya, 2948 satır. Simülasyon gün tabanlı: `DAY_SEC=14`, mevsim 30 gün, 4 mevsim (`index.html:1278`). Oyunun tamamı 1x hızda yaklaşık 28 dakika sürüyor, 1x/2x/4x hız seçilebiliyor (`:2767`).
- **D** Ana döngü şöyle: dik → sula (çeşmeye 4.6 karo yakın yataklar kendiliğinden sulanır, `:1660`) → çiçek 22. günde açar (`stageOf`, `:1528`) → kes ya da sök → yan yana açan iki lale melez tohum verir (`breedPass`, `:1680`). Pazarda fiyatlar dalgalanıyor ve her mevsimin 5. gününde bir "lale çılgınlığı" başlıyor (`:1697`). Don 2. mevsimin 12. gününde ve 4. mevsimin 20. gününde sabit (`:1711`). Yaprak biti her gün %3 olasılıkla çıkıyor.
- **D** Puanlama iki ayrı sistemden oluşuyor. Yıldızlar `beauty()`'den geliyor (0-100: çeşit 35, uyum 25, simetri 20, süs 20; `:1726`). Şükûfe jürisi ayrıca 0-40 puan veriyor; bu puan ödül akçesini, itibarı ve hediye soğanı belirliyor (`:1770`). Kazanmak için 3 yıldız ve en az 20 çeşit gerekiyor (`:1875`).
- **D** Kayıt `arena.lale-bahcesi.save` anahtarında, `S` nesnesi doğrudan JSON olarak yazılıyor. Sürüm alanı yok; eski kayıtlarda `rep` alanı yoksa 0 sayılıyor (`:2685`). Günlük meydan okumada mulberry32 tohumu `S.seed` içinde saklanıyor (`:1468`).
- **D** `?auto` bot 5 oyunun 5'ini kazandı: 22-27 çeşit, güzellik puanı 87-88 (3 yıldız eşiği 85), jüri 26-29/40, 0 JS hatası. Hızlandırılmış simülasyonla bir oyun 0,4-12 saniye sürdü; fark makine yükünden kaynaklanıyor.
- **D** İlk çiçek oyuncu 1. günde diktiğinde 23. günde açıyor. Bu, 1x hızda **308 saniye (≈5 dakika)** bekleme demek. Bu süre boyunca koç yalnız "Soğanlar filizleniyor" diyor (`:1371`).
- **D** Ses tamamen sentezleniyor (makam benzeri dizi, ud/kanun/ney taklidi; `:2702`). TR/EN dil desteği `STR` içinde. `isPhone` olunca düşük kalite seçiliyor (`:1457`).
- **D** Sayfa dışarıya iki istek yapıyor: GoatCounter (`gc.zgo.at/count.js`, `:1125`) ve Google Fonts. Ölçüm sırasında ikisi de yakalandı.
- **D** Yeni Divan adlandırması (e052030) adı `DIVAN_ADJ[v%20] + şekil` biçiminde kuruyor (`:1488`). Renk ve desen artık adda geçmiyor.

## 2. Güçlü yanlar (korunmalı)
- Tema özgün: Lale Devri, akçe, bazar, lale çılgınlığı, Şükûfe jürisi (Nakkaş, Şükûfezen, Mimar, Bostancıbaşı). Jüri her kusuru sayıyla ve yapılabilir bir öneriyle söylüyor ("6 yatak kuru"). Bu, oyuncuya iyi bir geri bildirim döngüsü sağlıyor (**D**, `:1342-1353`).
- Jüri puanı deterministik (`juryOf` rastgelelik kullanmıyor). Günlük meydan okuma tohumlu. Festival ekranı açıkken kayıt alınırsa ödül iki kez ödenmiyor (**D**, `festPending`).
- Performans tasarımı sağlam: dünya yalnız `dirty` olunca yeniden kuruluyor, laleler instanced mesh ile çiziliyor ve `count` kırpılıyor (`:2191`). README'deki ölçüm 42-61 draw call (**K**: README; bu turda yük yüzünden yeniden ölçülemedi).
- Bot ve test kancaları iyi: `window.lale`, `laleSim`, `?sim`, `?debug`.
- Simetri ve renk uyumu gibi "bahçe estetiği" hedefleri gerçek bahçe kültürüne dayanıyor ve türün içinde ayırt edici.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Telefonda HUD düğmeleri ekranın dışında kalıyor (kritik, D).** Ölçümler:
   - 360, 390 ve 412 px'te Duraklat, Katalog, Bazar, Ses ve Dil düğmelerinin hepsi `getBoundingClientRect().right > innerWidth`. 390 px'te Hız da dışarıda (362-402).
   - 600 px'te bile Ses ve Dil dışarıda; 960 px masaüstünde "EN" yarıya kadar kesik (`2-desktop-bloom.png`).
   - Playwright, 390 px'te `#b-cat` için "element is outside of the viewport" verdi.
   - Sonuç: dokunmatik telefonda **bazar açılamıyor**, yani paket alınamıyor ve çiçek satılamıyor. Katalog ve duraklatma da yok.
   - Kaynak: 7e52007 "UI/UX REBIRTH" commit'i `.stats{flex-wrap:nowrap}` ekledi ve etiketleri gizledi (`:1061-1070`). `#hud` taşmayı yönetmiyor. Eski `docs/phone-gameplay.png` iki satırlı, çalışan bir düzen gösteriyor.
2. **Çeşit adları çakışıyor (D).** Adlandırılmış 5 çeşit dışındaki 85 çeşidin **54'ü**, 27 grup halinde başka bir çeşitle aynı adı taşıyor. Örnekler:
   - v1 (Kırmızı alevli) ile v81 (Ateş düz) aynı ada sahip.
   - v3 (Kırmızı badem düz) ile v23 (Beyaz badem kenarlı) aynı ada sahip.

   Dikim çiplerinde ve bazar listesinde yalnız ad ve renk noktası görünüyor; desen hiç görünmüyor. "Maşukî Yuvarlak ×6" seçimin içeriği hakkında bilgi vermiyor. EN çeviriler de zayıf ("Sun-exciting round", "Life-increasing round"). Toast'larda "Hybrid seed: Beloved round" yazıyor, ama bu adın hangi tohum olduğu anlaşılmıyor.
3. **Melezleme ipucu yanlış (D).** `getHybridParents` (`:2503`) şekil ve deseni yok sayıyor ve yalnızca "renk×9", yani yuvarlak-düz ebeveynlerin keşfedilip keşfedilmediğine bakıyor. Hiçbiri yoksa sabit olarak "Kırmızı + Sarı" döndürüyor. Kırmızı+Sarı aslında Turuncu verir (`MIX '0,3':5`).
   - Başlangıçta 90 kartın **81'i** "Gereken: Kırmızı + Sarı" gösteriyor (390 px katalogda ilk 12 kartın 12'si).
   - Beyaz, Sarı ve Mor (2, 3, 4) hiçbir karışımla üretilemiyor, yalnız paketten geliyor; ipucu bunu da söylemiyor.
   - İpucu ayrıca keşfedilmemiş çeşidin rengini dolaylı olarak ele veriyor.
4. **Sonsuz mod devam ettirilemiyor (D).** Bitiş ekranında "Sonsuz bahçe" seçilince kayda `endless:true, ended:true` yazılıyor. Sayfa yenilenince `#b-cont` gizli kalıyor (`:2617`), `continueGame` ise `ended` görüp yeni oyun açıyor (`:2683`). Sonsuz bahçe ilk yenilemede kayboluyor. Adımlar: `?auto` ile oyunu bitir → Sonsuz bahçe → yenile → Devam düğmesi yok.
5. **İlk ödül çok geç (D ölçüm, K ilke).** İlk çiçek 1x hızda 5 dakika sonra açıyor. İlk 30 saniyede oyuncu bir yatağa tıklayıp soğan dikiyor, sonra yalnız bekliyor. FTUE kaynakları ilk somut kazanımı ilk 1-2 dakika içinde öneriyor.
6. **Parsel paneli her gün yeniden kuruluyor (D).** `rebuildWorld` (`:2177`) her `dirty`'de `renderTile()` çağırıyor ve `endDay` her gün `dirty=true` yapıyor. Panel 1x'te 14 saniyede, 4x'te 3,5 saniyede bir `innerHTML` ile baştan yazılıyor. Playwright tıklama sırasında "Element is not attached to the DOM" hatası verdi. Basma ile bırakma arasında yeniden çizim olursa dokunuş boşa gidiyor, klavye odağı da kayboluyor (**T**: oyuncu bunu ara sıra "tıklamam çalışmadı" diye yaşar).
7. **Zorluk tavanı düşük (D/T).** Basit sezgisel bot 5 oyunun 5'ini kazandı. Kazanan bir oyuncu için 2. oyunda bir hedef yok; sonsuz mod da (madde 4) kırık.
8. **İki ayrı puan kafa karıştırıyor (T).** Festivalde 0-100 "Puan" ile yıldız, altında da 0-40 jüri puanı gösteriliyor. Renk uyumunun ölçütü ikisinde farklı: `beauty` renk sayısına, jüri komşu çiftlere bakıyor. Hangi puanın kazandırdığı oyuncuya söylenmiyor.
9. **i18n kaçakları (D).** Bazardaki "3 adet melez/nadir soğan" İngilizcede de Türkçe görünüyor (`:2485`). "Low/High quality takes effect after reload." Türkçede de İngilizce görünüyor (`:2791-2792`). Dikim çipindeki "ak." de çevrilmiyor. Ayrıca paket aslında 0-7 renklerden **rastgele** soğan veriyor (`:1646`); "melez/nadir" ifadesi yanıltıcı.
10. **Erişilebilirlik (D):**
    - Parsel seçmek yalnız işaretçiyle mümkün; klavyeyle karo seçilemiyor.
    - `REDUCED` yalnız jüri ziyaretçilerini durduruyor (`:2282`). Yaprak, arı, kelebek, salınım ve fıskiye hareket etmeye devam ediyor (`:2256-2279`).
    - İpucu `title` özniteliğinde duruyor, dokunmatik ekranda görünmüyor.
11. **Kısıtla çelişme (D, karar sahibine):** GoatCounter analitiği harici bir ağ çağrısı yapıyor ve ziyaret verisi topluyor. Brief'teki "harici ağ çağrısı yok / kullanıcı verisi toplanmaz" kısıtıyla çelişiyor; ekosistem genelinde bilinçli bir karar olabilir (bkz. 9).

## 4. EKLENMELİ — yüksek değer
**A. Telefon HUD'unu kurtar.**
- Ne: Bütün araç düğmeleri her genişlikte görünür ve en az 44 px olsun.
- Neden: Telefonda bazar, katalog ve duraklatma şu an erişilemez (sorun 1).
- Nasıl: Yalnız CSS, oyun mantığına dokunulmaz.
  - `@media (max-width:760px)` içinde `#hud{flex-wrap:wrap}`; `.stats{order:2;flex-basis:100%}`; `.tools{order:1;margin-left:auto}`.
  - Alternatif: 6 araç düğmesini alt başparmak bölgesine, yapı çubuğunun üstüne taşı.
  - `#coach`, `#tile` ve `#toasts` konumlarını HUD'un yeni yüksekliğine göre ayarla.
- Doğrulama: 360/390/412/768/1280 px'te `rect.right<=innerWidth`; smoke testine bir "ekran içinde" assert'i eklenebilir.
- Maliyet: S. Risk: düşük. Kayıt ve bot etkilenmez.
- Kaynak: XAG 107, GAG dokunma hedefi; Poki/CrazyGames'te "mobilde oynanabilir" zorunlu (**K**).

**B. Benzersiz ve bilgi taşıyan çeşit adları.**
- Ne: Divan sıfatı kalsın, ama ad renk ve deseni de taşısın.
  - TR örneği: "Maşukî Kırmızı Badem (alevli)".
  - Alternatif: sıfatı 90 çeşide birebir eşleyen bir tablo (her çeşide ayrı sıfat) ve altta renk·şekil·desen satırı.
- Neden: 54 çeşit çakışıyor; dikim ve satış kararı adla veriliyor.
- Nasıl: `nameOf` (`:1488`) düzeltilir. Çip ve bazar satırlarına küçük desen simgesi ya da `flowerSVG` eklenir. EN'de çevrilmiş sıfat yerine özgün terim kullanılır: "Maşukî" + ayrıca "red almond, flamed".
- Maliyet: S. Risk: yok, çünkü kayıt `v` sayısını saklıyor.

**C. Doğru ve dokunmatikte görünen melezleme rehberi.**
- Ne: İpucu yalnız oyuncunun **elindeki** ya da keşfettiği çeşitlerden gerçekten ulaşılabilen bir yol gösterir.
  - Örnek: "Kırmızı + Beyaz yan yana → Pembe". Şekil ve desen için "ebeveynlerden biri lale-i rumi olmalı".
  - Ulaşılamayan renk için "Bazar paketinden gelir" yazar.
  - Rastgele sapmalar için (%12 renk, %10 şekil/desen) "şansla" etiketi kullanılır.
- Nasıl: `getHybridParents` yeniden yazılır. `breed()`'deki kurallar tersine çevrilir: hedef renk = ebeveynlerden biri ya da `MIX` sonucu; şekil ve desen ebeveynlerden birinden. İpucu `small` içinde kalır, `title` kaldırılır. Keşfedilmemiş bir kartın rengini ipucunun ele vermemesi için yalnız "1 adım uzaklıktaki" çeşitler gösterilebilir.
- Maliyet: S-M. Risk: düşük.
- Kaynak: Animal Crossing melezleme rehberlerinin popülerliği, oyuncuların kuralı bilmek istediğini gösteriyor (**K**). İlke: kural açık olsun, şans görünür olsun.

**D. İlk 2 dakikada ilk çiçek.**
- Ne: Yalnız **yeni** oyunlarda (`newState`), 4 başlangıç yatağından ikisine tomurcuk evresinde (`a≈18`) iki lale konur. İkisi yan yana durur, böylece ilk melez tohum da hızlı gelir. Kalan 6 soğan elde kalır.
- Neden: Şu an ilk ödül 5 dakika sonra geliyor (sorun 5).
- Nasıl: `makeTiles` içinde `pl:{v:0,a:18,...}`. Günlük modda tohumlu renk kullanılır. Eski kayıtlar etkilenmez.
- Bot: bot `S.day<=8` kuralıyla dolu yatağı atlar, sonucu değişmez; yine de 3 `?auto` koşusuyla doğrulanmalı.
- Maliyet: S. Risk: mevsim 1 festival puanı hafif yükselir; `starsFor` eşikleri değişmez.
- Alternatif: 1. mevsimde büyüme ×1.5. Bu, denge değişikliği olduğu için daha riskli.

**E. Sonsuz modu kalıcı yap.**
- Ne: `b-end-endless` tıklanınca `S.ended=false` yapılsın ya da `continueGame` ve `renderTitle` `ended && !endless` kontrolü kullansın.
- Ek: `KEY_BEST` ve `Arena.award`'ın ikinci kez tetiklenmemesi kontrol edilmeli. `endGame` zaten `S.endless` ile tekrar çağrılmıyor (`:1869`).
- Maliyet: S. Risk: düşük. Eski kayıtlar da düzelir: `endless:true, ended:true` artık devam edilebilir hale gelir.

**F. Parsel panelini yalnız değişince yeniden çiz.**
- Ne: `renderTile` üretilen HTML dizgisini bir önceki ile karşılaştırsın, aynıysa `innerHTML`'e dokunmasın.
- Ek: değişen kısım çoğunlukla nem yüzdesi; o `textContent` ile güncellenebilir.
- Maliyet: S. Risk: yok. Dokunuş kaybı ve odak kaybı biter.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Mevsim siparişi ("Saraydan ferman"):** Her mevsim başında deterministik tek bir hedef verilir, ör. "şenlikte 3 alevli lale" ya da "çeşmenin iki yanı %80 simetrik". Ödülü akçe ve itibar olur. Mevsim ortasına yön verir ve jüriyle aynı dili konuşur. Maliyet M. Kayıt için `S.order` eklenir, eskilerde yoksa üretilir. Bot görmezden gelebilir.
- **Zor mod / "Sultan'ın gözdesi" kademesi:** Bot hep kazandığı için (sorun 7), kazanılmış bir oyundan sonra açılan seçmeli bir zorluk. Ör. 30 çeşit + jüri ≥30/40 ya da daha sert don. Puan yalnız ayrı bir rozetle saklanır. Maliyet M. Risk: denge; `?auto` normal modda kalır.
- **Melezleme önizlemesi:** Parsel panelinde, yan yana açan bir çift varsa "Komşu çiçekle melez şansı ~%X/gün" gösterilir (formül `:1688`). Oyuncu yerleşimi bilerek yapar. Maliyet S.
- **Tek puan anlatısı:** Festival ekranında "Yıldızlar güzellikten, ödül jüriden" diye tek satır açıklama ve hangi puanın kazanmayı belirlediği yazılır. Maliyet S.
- **Klavye ile karo imleci:** Ok tuşları bugün kamerayı döndürüyor. Shift+ok ile imleç, Enter ile panel açma eklenebilir; panelde zaten düğmeler var. Maliyet M. Risk: tuş çakışması; kamera tuşları korunmalı.
- **Hareketi azalt kapsamı:** `REDUCED` iken yaprak, kelebek ve fıskiye hareketi yavaşlatılır ya da durdurulur, arılar sabitlenir. Maliyet S.
- **Bahçe kartpostalı:** `Arena.shareCard` zaten var. Festival anındaki kare (`renderer.domElement.toBlob`) karta eklenebilir. Ağ çağrısı yok. Maliyet S-M. Risk: `preserveDrawingBuffer` gerektirmeden render sonrası aynı karede alınmalı.
- **Katalogda soy ağacı ("Lale defteri"):** Keşfedilen her çeşidin hangi iki ebeveynden ve hangi gün geldiği kaydedilir. Kayda küçük bir `S.lineage` eklenir; yoksa boş sayılır. Maliyet M.

## 6. EKLENMEMELİ
- **Gerçek zamanlı ya da çevrimdışı büyüme (`Date.now` ile):** Günlük meydan okumanın determinizmini, `laleSim`/`?auto` testlerini ve kayıt anlamını bozar.
- **Oyuncular arası takas, çevrimiçi lale borsası, liderlik tablosu:** Sunucu ve hesap gerektirir; kısıtı aşar.
- **Daha fazla parçacık, gölge ya da post-process (bloom, SSAO):** Intel UHD bütçesini zorlar. Mevcut sahne zaten 7+ animasyonlu sistem içeriyor.
- **Yeni bir para birimi, enerji/sulama sınırı, bekleme süreleri:** Rahat (cozy) türün gevşekliğini bozar ve mobil-F2P hissi verir.
- **Animal Crossing'in gen tablolarını ya da çiçek türlerini birebir almak:** Kopya riski taşır. Mevcut basit renk-şekil-desen sistemi yeterli; yalnız açıklanması gerekiyor.
- **Bir dil modeli ya da harici API ile isim veya şiir üretmek:** Harici ağ çağrısıdır. Divan sıfatlarının statik tabloda kalması doğru.
- **İpucunu daha da çoğaltan relay tarzı yüzeysel eklemeler:** Son üç Gemini relay'inin ikisi gerileme getirdi (çakışan adlar, yanlış ipucu). Doğrulanmamış toplu "UI rebirth" türü değişiklikler, kritik telefon HUD regresyonunun kaynağı oldu.

## 7. Düzeltilmeli (hata, cila, erişilebilirlik, performans)
1. Telefon HUD taşması (4A), kritik.
2. Çeşit adı çakışması (4B) ve zayıf EN çevirileri.
3. Yanlış melezleme ipucu (4C).
4. Sonsuz mod kaydı (4E).
5. Parsel panelinin günlük yeniden kurulması (4F).
6. i18n: `:2485` "3 adet melez/nadir soğan" → `STR`'ye taşı ve metni düzelt ("rastgele 3 soğan"). `:2791-2792` kalite toast'ları → `STR`. "ak." kısaltması.
7. Toast yığını (3 adet) masaüstünde bahçenin ortasını kapatıyor (`2-desktop-bloom.png`). Telefonda üst kenar uygun; masaüstünde köşeye ya da tek satıra alınabilir.
8. `REDUCED` kapsamı (5).
9. Festival ekranında puan açıklaması (5).
10. GoatCounter ve Google Fonts için kısıt kararı (9).

## 8. Önerilen ilk 3 iş
1. **Telefon HUD'u (4A).** Bugün dokunmatik telefonda bazar, katalog ve duraklatma erişilemiyor. Oyunun ekonomik döngüsü telefonda kırık ve brief'teki mobil zorunluluğu sağlanmıyor. Yalnız CSS gerekiyor; 360/390/412 px ekran içi assert'iyle doğrulanır. S.
2. **Ad + ipucu + panel paketi (4B, 4C, 4F, i18n kaçakları).** Hepsi son relay'lerin getirdiği ya da bıraktığı bilgi hataları ve hepsi kayıt uyumlu, S maliyetli. Bitince oyuncu neyi diktiğini ve neyi nasıl melezleyeceğini doğru biliyor; tıklamalar da kaybolmuyor.
3. **İlk çiçek 2 dakikada + sonsuz modun kalıcılığı (4D, 4E).** İlk 5 dakikalık ölü süre, yeni oyuncu için en büyük bırakma riski (**T**). Sonsuz mod ise kazanan oyuncunun tek devam yolu. İkisi de küçük değişiklik; `?auto` ile 3 koşu ve eski kayıt yükleme testiyle doğrulanır.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek telefonda (iOS Safari/Android Chrome) dokunma ve HUD davranışı denenmedi; yalnız Playwright mobil öykünmesi kullanıldı.
- Fps ve draw call yeniden ölçülemedi (makine yükü 70-80, swiftshader). README'deki 60 fps ve 42-61 çağrı kabul edildi.
- Firefox/WebKit'te koşulmadı.
- GoatCounter ve Google Fonts: ekosistemde bilinçli bir istisna mı? Brief "harici ağ çağrısı yok, kullanıcı verisi toplanmaz" diyor. Karar sahibi netleştirmeli. Fontlar yerel `system-ui`'ye düşebilir; analitik kaldırılabilir ya da açıkça istisna yazılabilir.
- Bot hep kazanıyor, ama bir insanın 20 çeşide ve 3 yıldıza ne kadar zorlandığı ölçülmedi (oyuncu verisi yok).
- 4D'nin festival dengesine etkisi yalnız tahmin; uygulanınca 3+ `?auto` koşusu ve elle bir 1. mevsim oyunuyla bakılmalı.
- Divan sıfatlarının tarihsel ve dilsel doğruluğu (ör. "Mihr-engiz" = "Sun-exciting") bir Osmanlıca bilen tarafından gözden geçirilmeli.

## Kaynaklar
- Unity, 10 FTUE ipucu: https://unity.com/how-to/10-first-time-user-experience-tips-games
- FTUE ve ilk ödül zamanlaması: https://recognizingpatterns.substack.com/p/first-time-user-experience-your-player · https://liquidandgrit.com/first-time-user-experience-ftue-toolkit
- Apple, oyunlarda onboarding: https://developer-rno.apple.com/app-store/onboarding-for-games/
- Stardew Valley ürün ve mevsim süreleri (4-14 gün büyüme, 28 günlük mevsim): https://stardewvalleywiki.com/Crops
- Animal Crossing NH melezleme rehberleri (kuralı açık isteyen oyuncu kitlesi): https://www.pocketgamer.com/animal-crossing-new-horizons/flower-breeding · https://github.com/joeyparrish/acnh-flowers
- Game Accessibility Guidelines, dokunma hedefi: https://gameaccessibilityguidelines.com/?p=3181
- Xbox Accessibility Guidelines 107 (girdi, dokunma hedefi): https://devdocs.xbox.com/gaming/accessibility/xbox-accessibility-guidelines/107
- WCAG 2.2 hedef boyutu (axe): https://dequeuniversity.com/rules/axe/4.8/target-size
- Poki gereksinimleri: https://sdk.poki.com/requirements · CrazyGames teknik ve kalite: https://docs.crazygames.com/requirements/technical/ · https://docs.crazygames.com/requirements/quality/

# Karagöz — faz 3 araştırması

Repo `/home/user/karagoz` @ `e242871` (dal `claude/cloud-session-research-analysis-dufc2b`, git status temiz). Ölçümler headless Chromium + swiftshader ile, yük ortalaması 23-73 olan paylaşımlı makinede yapıldı. Bu yüzden mutlak süreler güvenilir değil, yalnız davranışlar ve göreli değerler kullanılabilir. Geçici dosyalar ve ekran görüntüleri: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_karagoz/`.
Etiketler: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.

## 1. Şu anki durum
- **D** Tek dosya, 3186 satır. 4 perdede 24 sahne, toplam 72 yıldız (`SCENES` 1285-1403, `ACTS` 1404). İlerleme doğrusal: harita yalnız ilk çözülmemiş sahneye kadar açık (`buildMap` 2957-2977).
- **D** Çekirdek: gölgeler 80×52'lik bir EVAL kanvasına çiziliyor. Uyum, piksel karanlığının ağırlıklı Jaccard'ı × parlaklık çarpanıyla hesaplanıyor (`matchOf` 1558-1564). Eşik %90 (`afterChange` 2118).
- **D** Bugünkü imza mekaniği "Mum Işığı" (76426a9): mum perdeye yaklaşıp uzaklaşabiliyor (5 kademe, `LAMP_DIST` 1163). Sahne 4 ve 16'da alev titremesine karşı "Göster" ile gölge boyu vuruşu yapılıyor (`present` 2122, `beatPass` 1467).
- **D** Arena-kit bağlı (303-656 kit bloğu; entegrasyon 3028-3041): günlük meydan okuma `seed % 24` ile mevcut bir sahneyi seçiyor (3033). Paylaş, rozet ve "başka oyun" da bağlı.
- **D** Bugün iki "relay" commit'i daha geldi, ikisi de kanıtsız:
  - 4a6ab11 "Proximity Audio Feedback": uyum ≥ %81 olunca çalan bir sinüs tonu (`curMatch` 2062-2076, `update` 2367-2369, `audioInit` 2742-2744).
  - fce5e6a "PWA": data: URL'li bir manifest (17) ve blob: URL'li bir service worker (932-944).
- **D** Kayıt `arena.karagoz.{settings,save,best}` anahtarlarında (976-987). Mumdan önceki kayıtlar `zi` alanı olmadan da yükleniyor (2086).
- **D** `?auto` bot çalışıyor: 150 sn'lik canlı koşuda 2 sahne çözüldü, 6 yıldız, 0 hata. Bu, makine yükü altında kısmi bir koşu. Eski tam koşu sonucu 24/24 sahne, 64 yıldız (76426a9 commit mesajı).
- **D** Üç koşuda (masaüstü, telefon, ton testi) konsol/sayfa hatası 0. `serviceWorker.getRegistrations()` her koşuda 0 döndü, yani SW hiç kaydolmuyor.
- **D** i18n TR/EN tam (`I18N` 992-1051). Dil tarayıcıdan seçiliyor. Telefonda varsayılan kalite "low" (980).
- **D** Ses tamamen sentez (ney, tef, Hicaz). Gizli sekmede AudioContext askıya alınıyor (3051-3054).

## 2. Güçlü yanlar (korunmalı)
- Fizik temelli ve özgün bulmaca: nokta ışıkta gölge ölçeği D/(D-p) ve yarı gölge; renkli lambaların karışımı. Tür içinde (gölge bulmacası) ayırt edici, kültürel teması güçlü.
- Her sahne bir referans dizilimden üretiliyor, bu yüzden çözülebilirlik kanıtlı. Bot da oyuncunun gördüğü aynı uyum değerini okuyor.
- Her sahnede tek yeni kavram veriliyor (pill ipuçları; örneğin sahne 2 "sabit dekor", sahne 5 "döndür", sahne 6 "yerleştir/kaldır"). Öğretim eğrisi iyi.
- Yıldızlar (çözüm / par / ipucusuz), hamle başına geri alma ve sıfırla var. Ceza yumuşak.
- Diyalog ödülü: çözünce Karagöz ile Hacivat'ın TR/EN nüktesi geliyor. Oyunun ruhu bu, korunmalı.
- Erişilebilirlik tabanı:
  - Klavyeyle tam oynanıyor.
  - Uyum yüzde olarak ve çubukla gösteriliyor; renk tek başına bilgi taşımıyor.
  - `prefers-reduced-motion` destekleniyor.
  - Telefonda üst bar düğmeleri 44×44 (**D**).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Uyum tonu sahne bitince susmuyor (D, hata).**
   - Adımlar: sahne 1'i aç → sesi başlat → sahneyi çöz (uyum 1.0) → sonuç ekranı → "Harita" → "Ana menü".
   - Kanıt: tonun GainNode'u (4. `createGain`, enstrümante edildi) her aşamada `0.048` olarak kaldı: play, result, map ve title ekranında (`tone.log`).
   - Neden: `curMatch` tonu yalnız `G.screen==='play'` iken günceller (2064). `update` de onu yalnız play ekranında ve duraklatılmamışken çağırır (2367). Sonuç ekranında, haritada, menüde ve duraklatma menüsünde 220-440 Hz'lik bir sinüs sürekli çalar.
   - Ton müzik kanalına bağlı (2744). Müzik açıksa bir sonraki sahnede uyum %81'in altına inene kadar susmuyor.
2. **Uyum her karede gereksiz yere yeniden hesaplanıyor (D kod, T etki).**
   - 4a6ab11, `update()` içine her kare `G.match = curMatch()` ekledi (2367-2369).
   - Oysa uyum yalnız durum değişince değişiyor: statik sahnelerde t=0, zamanlı sahnelerde sabit `tc` kullanılıyor (2063). Önceden yalnız `afterChange`'de hesaplanıyordu (2117).
   - Her kare bir ek `renderShadows` (lamba başına blur filtreli çizim) ve `getImageData` geri okuması yapılıyor.
   - Ölçüm (yük altında, gürültülü): `matchOf` çağrı başına 0.8-4.5 ms (`perf-head.log`, `perf-pre.log`). Önceki sürümle `update` farkı gürültü içinde kaldı.
   - Intel UHD dizüstünde kare başına ~1-4 ms ek CPU ve kanvas geri okuması demek (**T**). README'nin "timed act IV scenes 39 fps" notu düşünülürse kırılgan bir bütçe.
3. **PWA commit'i işlevsiz ve ileride zararlı olabilir (D/K).**
   - Blob: URL ile `serviceWorker.register` spesifikasyona göre reddediliyor. Hata `.catch(()=>{})` ile yutuluyor; ölçümde kayıt sayısı 0.
   - Manifest data: URL'de, ikonu yok, `start_url:"."` data: URL'ye göre çözülüyor. Kurulabilirlik ölçütlerini karşılamaz (**T/K**).
   - Daha önemlisi: biri bunu "düzeltip" çalışır hale getirirse, sabit `karagoz-v1` önbelleği ve cache-first `fetch` yüzünden oyuncu bir daha yeni sürüm göremez (**T**).
   - Kısıt açısından: tek dosya kalması için ayrı bir `sw.js` gerekir, bu da "tek dosya" kısıtını aşar.
4. **Telefonda HUD taşıyor (D).**
   - Ekran: `phone-4-scene16.png`, 390×844, sahne 16.
   - Gölge boyu göstergesi eklenince istatistik satırı sağdan taşıyor: "Hamle" kesik, hamle sayısı/par ve yıldızlar görünmüyor (`.stats` 760 px altında tek satır, 97-103). Bu durum vuruş sahnelerinde (4 ve 16) çıkıyor.
   - Pill ipucu kutusu (113) perdenin üst bölümünü ve hedef ayın üstünü örtüyor.
5. **İlk oyuna giriş 2 tıklama + 3 sn göstermelik sürüyor (D).** Oyna haritayı açıyor (3003), sonra sahne 1, sonra 3 sn intro (2386). CrazyGames yeni oyuncuyu doğrudan oyuna ya da en fazla 1 tıkla sokmayı istiyor (**K**).
6. **İpucu tek kademeli ve sert (D).** `useHint` (2204-2220) bir parçayı doğrudan referansa oturtuyor ve bir yıldız alıyor. Ara kademe yok ("hangi parça yanlış?" ya da "hangi yöne?"). Tür örneklerinde kademeli ipucu yaygın (**K**).
7. **Tekrar oynanabilirlik sınırlı (D).** 24 sabit sahne var. Günlük meydan okuma da aynı 24 sahneyi döndürüyor (`seed % 24`), yani ~24 günde bir aynı sahne geliyor. Final sonrası yeni içerik yok.
8. **Ton tasarımı (D/T).**
   - Eşik sabit `0.9*0.9` (2065). Ses müzik ses düzeyiyle çarpılıyor, sfx anahtarından bağımsız.
   - Ayarlarda kapatma seçeneği yok.
   - Statik sahnelerde %81-90 arasında, zamanlı sahnelerde ise %100'e kadar sürekli çalan saf bir sinüs. Hicaz müziğiyle akort ilişkisi yok (**T**: kulak yorucu).
9. Küçük: harita sahne düğmeleri telefonda 38×48. WCAG 2.5.8 (24 px) karşılanıyor, 44 px önerisinin altında (**D**). Başlıkta "(seri 0 · en iyi 0)" yazısı telefonda iki satıra kırılıyor (`phone-1-title.png`, **D**).

## 4. EKLENMELİ — yüksek değer
1. **Uyum tonunu düzelt ya da kaldır (S).**
   - Ne/nasıl:
     - (a) Per-frame `curMatch` satırını kaldır; uyum yine `afterChange`'de hesaplansın.
     - (b) Tonu `afterChange` + `showResult`/`openMap`/`toTitle`/`togglePause`'da kapat, ya da `update`'te `G.screen!=='play'||G.paused` iken gain'i 0'a çek.
     - (c) Tonu sfx kanalına al, Ayarlar'a bir anahtar ekle, sinüsü Hicaz perdesine (ör. 293.66 → 440) kuantala.
     - Alternatif: tonu tamamen kaldırıp yerine eşik geçişinde tek bir "tık/zil" one-shot'ı koy.
   - Neden: §3.1-2 hata ve performans. Sesli "sıcak/soğuk" ipucu bulmacanın "aha" anını da zayıflatıyor (**T**).
   - Risk: düşük. Bot `matchOf`'u doğrudan çağırıyor (3090), etkilenmez.
   - Kanıt için: `tone.log` tekrarı; gain sonuç ekranında 0 olmalı.
2. **PWA bloğunu geri al (S).**
   - Ne/nasıl: 17. satırdaki manifest ve 932-944'teki SW scriptini sil.
   - Neden: §3.3. İşlevsiz, tek dosya kısıtıyla gerçek bir PWA olamıyor ve ileride önbellek tuzağı kuruyor.
   - Risk: yok. Kayıt ya da bot etkilenmez.
3. **Telefon HUD düzeni (S).**
   - Ne/nasıl: 760 px altında `.stats` için ya `flex-wrap:wrap` ya da beat göstergesini uyum çubuğunun altına küçük bir satır olarak taşıma. Pill'i sahne açılışında 4-5 sn gösterip küçült (dokununca geri gelsin).
   - Neden: vuruş sahnelerinde hamle/par/yıldız görünmüyor, ipucu hedefi örtüyor.
   - Risk: yalnız CSS ve küçük JS. 390×844'te sahne 4/16/19 ekran görüntüsüyle doğrula.
4. **Kademeli ipucu (M).**
   - Ne/nasıl: `useHint` iki kademe olsun.
     - 1. kademe ücretsiz ya da yarım maliyetli: `hintCandidates` içinden en çok kazandıran parçayı seç, tepside ve 3B'de vurgula, yön oku göster ("Hacivat → sağa"). Durumu değiştirmez.
     - 2. kademe bugünkü davranış: parçayı yerine oturtur, yıldız gider.
     - `G.hint` yalnız 2. kademede `true` olur.
   - Neden: şu an "sıkıştım" ile "çözümü gör" arasında bir şey yok. Kademeli ipucu tür standardı (**K**: bugnet, roomescapeartist; Shadowmatic'te 4 kademe, ilk ikisi belirsiz).
   - Risk: kayıt biçimi değişmez (`h` alanı aynı). Bot `useHint`'i yalnız çıkmazda çağırıyor (3112); bot için 2. kademeyi doğrudan çağıran bir yol bırak.
5. **İlk deneyim kısayolu (S).**
   - Ne/nasıl: hiç ilerleme yoksa (`!PROG.stars.some(Boolean)`) "Oyna" doğrudan sahne 1'i açsın. Göstermelik intro dokunuşla geçilebilir olsun (`skip` metni I18N'de zaten var, 1010; geçişin bağlı olduğunu doğrula).
   - Neden: §3.5, CrazyGames "≤1 tık" (**K**).
   - Risk: düşük. Bot `title→map` akışını kullanıyor (3118); bot dalı korunmalı.

## 5. EKLENEBİLİR — orta değer / koşullu
- **"Serbest Perde" / sahne kurucu (L).** Oyuncu parçaları ve lambaları serbestçe dizer, durum URL hash'ine (`#p=` base64 JSON) yazılır, paylaşılan link aynı dizilimi hedef olarak açar.
  - Sunucu gerekmiyor; kullanıcı verisi toplanmıyor (veri linkin içinde).
  - Değeri: tekrar oynanabilirlik ve paylaşım; Karagöz'ün "perde gösterisi" fikrine uyuyor.
  - Riskler:
    - Hedefin çözülebilirliği kurulumdan geldiği için garanti.
    - Hash doğrulaması şart (aralık dışı indeks).
    - `startScene` sahne nesnesi istiyor; geçici `SCENES` dışı bir nesne lazım.
- **"Usta" kipi (M).** Tamamlanmış sahneyi hedef çizgisi olmadan, yalnız ilk 2 sn gösterilen hedefle oynamak; ayrı rozet. İçerik eklemeden zorluk ekler. Yıldızları ayrı alanda tutmalı (`PROG.master`); eski kayıt bozulmaz.
- **Günlük meydan okumada varyasyon (M).** `seed`'den türeyen farklı bir başlangıç karıştırması (`st`), aynı `ref` ile. 24 gün tekrarını kırar. Bulmaca kanıtlı çözülebilir kalır, çünkü hedef değişmiyor. Par yeniden hesaplanmalı.
- **Sahne seçiminde sıkışma kurtarıcısı (S).** Perde içinde 1 sahne atlamaya izin (sahne N+1 açık). Doğrusal kilit, ipucu olsa da bırakmaya yol açabilir (**T**).
- **Renk körü yardımı (S, koşullu).** Perde III'te kızıl/mavi lamba ikonuna desen ya da harf (K/M). Uyum yüzdesi zaten var, bu yüzden düşük öncelik.

## 6. EKLENMEMELİ
- **Gerçek PWA / offline service worker.** Ayrı `sw.js` dosyası gerektirir ("tek dosya kısıtını aşar"). Yanlış önbellek stratejisi oyuncuyu eski sürümde kilitler.
- **Sürekli ses ya da görsel "sıcak/soğuk" geri bildirimi.** Uyum yüzdesi zaten anlık. Ek sürekli sinyal bulmacayı "çubuğu doldur" oyununa çevirir.
- **Prosedürel rastgele sahne üretimi.** Rastgele hedefler kültürel/öykü bağlamını (diyalog) kaybeder. Ayrıca uyum ölçüsü bazı dizilimlerde belirsiz ya da çok-çözümlü olur.
- **Hesap, liderlik tablosu, bulut kaydı.** Sunucu ve kullanıcı verisi gerektirir; kısıtı aşar.
- **Daha ağır görsel (gerçek zamanlı gölge haritası, post-processing).** Zamanlı sahneler UHD'de zaten 39 fps (project-meta).
- **Diyalogları seslendirme.** Ücretli TTS ya da harici dosya gerekir. Tek dosya ve boyut açısından da uygun değil.

## 7. Düzeltilmeli
- §3.1 ton sızıntısı (hata) ve §3.2 per-frame `matchOf` (performans): ilk iş.
- §3.3 PWA kalıntısını kaldır.
- §3.4 telefon HUD taşması (vuruş sahneleri), pill'in hedefi örtmesi.
- Uyum yüzdesi TR'de "1%" yazılıyor; Türkçe biçim "%1" (2908, **D** ekran görüntüsü).
- Harita sahne düğmelerini 44 px'e yaklaştır (6 sütun, 390 px'te ~46 px mümkün).
- Relay commit'leri (4a6ab11, fce5e6a) kanıtsız birleştirilmiş: bot ve smoke testi yeniden koşulmalı. Bu araştırmada smoke koşulmadı, yalnız 0 hata gözlendi.

## 8. Önerilen ilk 3 iş
1. **Ton hatası + per-frame uyum hesabı (S):** satır 2367-2369'u kaldır, tonu ekran değişiminde/duraklatmada sustur ya da tonu tamamen çıkar. Gerekçe: doğrulanmış bir hata, her oyuncuyu etkiliyor, performans bütçesini yiyor, düzeltmesi küçük.
2. **PWA bloğunu geri al + telefon HUD taşmasını düzelt (S):** iki küçük cila tek PR'da. Kanıt: smoke chromium, 390×844'te sahne 4/16 ekran görüntüsü, `getRegistrations()==0` testine gerek kalmaz.
3. **Kademeli ipucu (M):** oyuncunun takıldığı anı yumuşatan en yüksek değerli oynanış eklemesi. Kayıt biçimi değişmez, bot yolu korunur. Sonrasında "Serbest Perde"ye (URL ile paylaşım) geçilebilir.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek UHD 620'de per-frame `matchOf` maliyeti: buradaki ölçüm 0.8-4.5 ms/çağrı, ama yük ortalaması 23-73 altında alındı. Gerçek donanımda `?debug` fps'i ile önce/sonra karşılaştırılmalı.
- Tam `?auto` 24/24 koşusu bu turda yapılmadı (makine yükü). 150 sn'de 2 sahne çözüldü, 0 hata.
- Ton testi sesi gerçekten duymadı; yalnız GainNode değeri okundu (`--autoplay-policy=no-user-gesture-required`, AudioContext "running").
- Manifest'in Chrome'da data: URL'den nasıl işlendiği DevTools ile denenmedi (**T**).
- Kullanıcı verisi kısıtı: sayfada GoatCounter sayacı (660) ve Google Fonts (20) harici çağrıları var. CDN istisnası dışında kalıyorlar. Kısıtla uyumu sahibine sorulmalı.
- Firefox/WebKit'te koşu yapılmadı.

## Kaynaklar
- CrazyGames gameplay/kalite gereksinimleri (≤1 tık ile oyuna giriş): https://docs.crazygames.com/requirements/gameplay/ , https://docs.crazygames.com/requirements/technical/ , https://docs.crazygames.com/resources/basic-launch-metrics/
- Kademeli ipucu ilkeleri: https://bugnet.io/blog/how-to-design-a-hint-system-for-puzzles , https://roomescapeartist.com/2016/10/02/hints-and-hinting-systems-room-design
- Shadowmatic ipucu kademeleri ve "fazla kılı kırk yaran" eleştirisi: https://www.macworld.com/article/224913/you-should-play-twist-objects-into-shadow-puppets-with-puzzler-shadowmatic.html , https://www.trustedreviews.com/shadowmatic-review , https://www.commonsensemedia.org/app-reviews/shadowmatic
- Service worker'ın blob:/data: URL ile kaydının reddi: https://searchfox.org/firefox-main/source/testing/web-platform/tests/connection-allowlist/tentative/service-worker.sub.https.window.js , https://lists.w3.org/Archives/Public/public-webapps-github/2015Nov/0332.html
- Hedef boyutu: WCAG 2.2 SC 2.5.8 (https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

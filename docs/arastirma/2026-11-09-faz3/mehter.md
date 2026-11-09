# Mehter — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Repo: `/home/user/mehter` @ 7bf40e8 (dal `claude/cloud-session-research-analysis-dufc2b`), `index.html` 3850 satır.
Çalıştırma: headless Chromium + SwiftShader, CDN yerelden, goatcounter boşa yönlendirildi. Makine çok yüklüydü
(load avg ~70), bu yüzden fps ölçümleri (1-5 fps) **performans kanıtı değil**. Geçici dosyalar ve ekran görüntüleri:
`scratchpad/arastirma/_mehter/` (`desktop-play-idle.png`, `phone-play.png`, `stats.mjs`, `fail.mjs`, `res2.json`, `res3.json`).

## 1. Şu anki durum
- **D** Döngü: `frame()` (3730) → `tickGame` (2580) → `logic` (2610). Saat Web Audio'ya bağlı (`G.clock='audio'`, `nowSong()` 2776). Müzik 0,3 sn ileriye planlanıyor (`scheduleAudio` 2597). Pencereler: Perfect 45 ms, Good 110 ms (2220).
- **D** İçerik: 6 sabit şarkı + "Günün Marşı". Hepsi `buildSong` (2258) ile usul kalıbından ve tohumdan kodla üretiliyor. Zorluk, notalardaki `lvl` alanından süzülüyor (`makeChart` 2316). Ölçtüğüm yoğunluk (`stats.mjs`):
  | şarkı | Kolay nota/sn | Normal | Zor |
  |---|---|---|---|
  | Düyek 96 | 3,1 (yalnız 2 şerit) | 6,0 | 7,7 |
  | Nevbet 138 | 4,5 | 9,9 | 12,3 |
  | Zafer 176 | 7,2 | 13,6 | 16,7 |
- **D** Kolay'da zurna ve zil şeridine hiç nota düşmüyor, uzun nota da yok (`lvl` 2-3). Kolay = iki şeritli oyun. Düyek ve Sofyan'da hiçbir zorlukta zil notası yok (usul kalıbında `z` yok, 2232-2233).
- **D** İmza mekaniği Dört Katman (2221-2227, 2507-2525): 16 isabetlik seri bir katman açar, 3 kayma bir katman düşürür, katman çarpanı ×1-×2,5. `LANE_LAYER` (2227) tanımlı ama **hiç kullanılmıyor**. Katman 1'deyken zurna ve zil notaları ekranda duruyor ve vurulmaları gerekiyor, ama o şeritlerin sesi kapalı (`setLayerGains`, 2441).
- **D** Kayıt: `arena.mehter.settings` ve `arena.mehter.best` (2132-2137). `store()`, eski kaydı varsayılanların üstüne yayıyor (geriye uyumlu). Seçilen zorluk kaydedilmiyor, her açılışta Normal'e dönüyor (2464).
- **D** Bot: `?auto&sim=99999&noassets` 6 şarkının hepsini bitirdi. Son şarkı 907/907 Perfect, S notu, 4 katman, 0 hata (`res2.json`).
- **D** Mobil: `pointer: coarse` olunca Düşük kalite (2122, 2124). Dört dokunma alanı 97×320 px. Oyun i18n ile TR/EN (2140-2211), ilk açılışta dil tarayıcıdan geliyor.
- **D** Ses tamamen sentez (`tone`/`noiseHit`). Yalnız UI tıkı ve fanfar CC0 mp3. Varlıklar 1,8 MB, bunun 1,6 MB'ı `dusk.hdr` (yalnız Yüksek kalitede yükleniyor, 3303).
- **D** Arena-kit bağlı (perf, a11y paneli, günlük + seri, paylaş, rozetler, başka oyun), 3218 ve 3645-3655.

## 2. Güçlü yanlar (korunmalı)
- Saat Web Audio'ya bağlı, kalibrasyon medyanla yapılıyor (2833), sonuç ekranında erken/geç histogramı var. Ritim oyunu için doğru temel (**D**). Bunu bir görsel saate geçirmek kötü olur.
- Şarkılar koddan, gerçek usul kalıplarından üretiliyor. Bu sayede hiç dosya eklemeden içerik genişletmek mümkün (**D**). Kültürel kimlik güçlü: usul adları, hicaz dizisi, nevbet (**T**).
- Dört Katman müziği ve görüntüyü birlikte değiştiriyor. Saftan düşen bando üyesi yol kenarına çekiliyor (3337-3383). Ödül oyunun içinde, kurgunun parçası (**T**).
- Bot düşük fps'te de geride kalmıyor. `?sim` ve `window.mehter.state()` iyi bir test yüzeyi (**D**).
- Seçenekler yerinde: tuş yeniden atama, gamepad (3713), sekme gizlenince duraklama (3670), `e.repeat` filtresi (3688) (**D**).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **İlk deneyim acımasız (D).** Varsayılan zorluk Normal. Düyek Normal 6 nota/sn ve 159 akor (iki tuşa birlikte basılan nota) içeriyor. Ruh barı kaçan notada −7, isabette +1,2 (2673, 2684). 15 kaçış oyunu bitiriyor. Hiç basmayan yeni oyuncu ilk notadan **2,15 sn sonra** "Ruh tükendi" görüyor (`fail.mjs`: Normal-0'da t=4,15 sn). Kolay'da bile 6,5 sn. Ekran görüntüsü: `desktop-play-idle.png` (15 kaçış, C, 0 puan). Rekor yazılmıyor ve rozet yok, yani oyuncu hiçbir şey kazanmadan çıkıyor. Ayrıca ekranda sadece "Ruh tükendi" ve bir C notu var, bir sonraki adım önerilmiyor.
2. **Tuş çakışması hatası (D).** `onKey` (3700-3703) M, X, L, P ve Esc tuşlarını şerit tuşlarından önce yakalıyor. Bir şerit M'ye atanırsa o tuş müziği kapatıyor, nota basılmıyor. Ölçüm: `keys:['d','f','j','m']` ile M'ye basınca `held` 4×false kaldı, `musicOn` true→false oldu (`res2.json` rebindM). Yeniden atama ekranı (3690-3698) bu tuşları reddetmiyor.
3. **Telefonda HUD taşıyor (D).** 390×844'te üst şeritte "SKOR 0" görünüyor, "KOMBO" sağdan kesiliyor, İsabet hiç görünmüyor (`phone-play.png`). Oyun alanı küçük: vuruş çizgisinde dört şerit toplam ~170 px, altındaki dokunma alanları 4×97 px. Görsel şerit ile dokunma alanı arasında ~200 px'lik boş halı var (**T**: göz ile parmak arasındaki eşleşme zayıf).
4. **Katman–nota uyumsuzluğu (D/T).** Katman 1'de sesi kapalı zurna ve zil notalarına basılıyor (`LANE_LAYER` ölü kod). Oyuncu duymadığı bir sazı çalıyor (**T**). Kolay'da zurna ve zil katmanları açılıyor ama o şeritlerde nota yok (**D**), yani katman yalnız ses ve dekor.
5. **Erişilebilirlik paneli ile oyun arasında bağ yok (D).** Oyunun CSS'i `--arena-text-scale` kullanmıyor; değişken yalnız kit bloğunda geçiyor (3 eşleşme). Yazı boyutu kaydırıcısı oyun arayüzünü değiştirmiyor. "Hareketi azalt" yalnız CSS animasyonlarını etkiliyor; 3B sahnedeki menü kamera salınımı (3759), vuruşta ışık nabzı (3450), konfeti ve petaller etkilenmiyor. "Titreşim" seçeneğinin karşılığı yok, oyunda `navigator.vibrate` çağrısı yok. Yüksek karşıtlık, WebGL tuvalini de içeren `body`'ye `filter` uyguluyor; bunun UHD'de maliyeti olabilir (**T**, ölçülmedi).
6. **Kalite düğmesi (D).** 3632: Düşük/Yüksek'e basınca "Tuş atandı" (`rebindDone`) bildirimi çıkıyor. Ayar yeniden yüklemeye kadar uygulanmıyor, çünkü gölge ve pixel ratio açılışta bir kez okunuyor (3217-3233). Kullanıcıya bu söylenmiyor.
7. **Zorluk eğrisinde uçurum (D).** Normal'de 4. şarkıdan 5.'ye 9,9 → 12,1 nota/sn. Kolay'da Zafer 7,2 nota/sn, yani Düyek Normal'den yoğun. Zorluklar arasındaki fark yalnız nota sayısı; tempo ve okuma hızı (`SPEED=8` sabit, 2228) aynı kalıyor.
8. Küçük **D** bulgular: `howto1` metninde "D F J K" sabit yazılı, tuş değişince güncellenmiyor (2143). `#judge` aria-live her vuruşta ekran okuyucuya "MÜKEMMEL" okutuyor (1862). 960×540'ta sonuç kartının düğmeleri ekranın altında kalıyor, kaydırmak gerekiyor (`desktop-play-idle.png`). Gamepad'de duraklat düğmesi yok (3713-3725). `breakHold` içinde etkisiz `G.judged += 0` (2695).

## 4. EKLENMELİ — yüksek değer
**4.1 İlk deneyim: Kolay varsayılan + kısa ısınma + "pes etmeyen" ilk oyun**
- Ne: İlk oyunda zorluk Kolay olmalı. Seçilen zorluk ayarlarda saklanmalı. İlk 2 ölçüde ruh barı düşmemeli (ısınma). Zorluk seçiminin yanında "Ruh tükenmez" (no-fail) seçeneği olmalı; bu açıkken rekor ve rozet yazılmaz.
- Neden: Bugün sessiz kalan yeni oyuncu 2 saniyede kaybediyor (§3.1). Portallar "yeni oyuncuyu şaşırtan mekanik" ve "zayıf ilk deneyim" yüzünden oyun reddediyor (K). Rhythm Doctor'ın "Unmissable" modu ve Spin Rhythm XD'nin hız ve zorluk seçimi örnek (K). Rhythm Quest gibi oyunlar basit ve tekrarlı başlayıp yavaş yavaş zorlaşıyor (K).
- Nasıl: `DEF.diff='easy'`, `S.diff` kalıcı (eski kayıtlarda alan yok → varsayılan; `store()` yayması zaten uyumlu). `onMiss` içinde `if (G.gt < LEAD + 2*barDur) spirit-=0`. `noFail` bayrağı açıkken `checkFail` atlanır ve `endSong` rekor yazmaz. Bot `?auto` Normal'e sabit (3837), etkilenmez.
- Maliyet S. Risk düşük (kayıt uyumlu, bot etkilenmez). Kısıtlara uyar.

**4.2 Kolay'ı gerçek bir dört şeritli zorluk yapmak + katmanı şeritle eşlemek**
- Ne: Kolay'a seyrek zurna (tek basış) ve zil notaları eklenmeli. `LANE_LAYER` gerçekten kullanılmalı: bir şeridin katmanı henüz açılmadıysa o şeritteki notalar "hayalet" çizilir (sönük) ve bonus sayılır. Vurursa puan, kaçırırsa ceza yok.
- Neden: Kolay şu an iki şeritli, katman ödülü boşa çıkıyor. Duyulmayan sazı çalmak da kopuk (§3.4). Rock Band'de kaçan nota sazı susturuyor ve oyuncular bunu sevmiyor (K). Mehter'in tersine çevirdiği "katman açılınca saz duyulur" fikri tutarlı hale gelir.
- Nasıl: `buildSong` içinde zurna seçimine `lvl:1` alt kümesi eklenir (her 2 ölçüde 1 kısa nota). `z` kalıplarına ölçü başına 1 zil `lvl:1`. Notaya katman durumu eklenir: `n.ghost = LANE_LAYER[n.lane] >= G.layers`. `onMiss` içinde ghost ise slip ve spirit cezası yok. `updateNotes` içinde ghost renk ×0,35.
- Maliyet M. Risk: puan dengesi değişir, eski rekorlarla karşılaştırma bozulur (**T**). Önlem: Kolay rekorları ayrı anahtarla tutulur ya da "v2" etiketiyle gösterilir. Bot etkilenmez, çünkü bütün notalara basıyor.

**4.3 Tuş çakışmasını ve telefon HUD'unu düzeltmek (cila ama ilk izlenimi doğrudan etkiliyor)**
- Ne: Yeniden atamada M, X, L, P, Esc ve Boşluk reddedilmeli. Oyun sırasında şerit tuşları global kısayollardan önce kontrol edilmeli. 390 px genişlikte HUD iki satıra inmeli ya da Kombo ve İsabet gizlenip yalnız Skor ve katman şeridi kalmalı.
- Nasıl: `onKey` içinde `const l = S.keys.indexOf(k); if (l>=0 && G.screen==='play') {...; return;}` global kısayollardan önce gelmeli. Yasak tuş seti için mesaj eklenmeli. `@media (max-width:430px)` içinde `#hud` grid düzeni.
- Maliyet S. Risk çok düşük.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Not hızı (scroll speed) ayarı**, 0,75×-1,5×. `SPEED` sabitini ayara bağlamak yetiyor (`LOOK` türetiliyor, 2229). Yoğun şarkılarda okunabilirliği artırır. Spin Rhythm XD bunu erişilebilirlik özelliği olarak listeliyor (K). Maliyet S. Risk: notaların görünür sayısı artarsa `nc<720` sınırı var (3423), bir kez ölçülmeli.
- **Pratik modu / tempo %75**: aynı şarkı daha yavaş, rekor yok. `buildSong({..., bpm: bpm*0.75})` ile yapılabilir. Maliyet S-M. ADOFAI Access ve One Hand Clapping'de pratik alanı var (K).
- **Çıkış gecikmesi tahmini**: `AU.ctx.outputLatency + baseLatency` değeri kalibrasyonun başlangıç değeri olarak gösterilsin (Bluetooth kulaklıkta 150-250 ms olabilir, **T**). Kaynaklar bu değerlerin tarayıcıya göre değiştiğini, tap testinin asıl ölçü olması gerektiğini söylüyor; Firefox'ta baseLatency 0 (K). Maliyet S, yalnız ipucu olarak.
- **Görsel ofset** (ses ve görüntü ayrı kalibrasyonu, Rhythm Doctor'ın yaptığı gibi, K). Bugün tek ofset yalnız girişe uygulanıyor (2780). Maliyet M.
- **Sonsuz/"uzun yürüyüş" modu**: usul tohumdan sürekli ölçü üretilir, BPM her 8 ölçüde artar. İçerik derinliği getirir, dosya gerektirmez. Maliyet M. Risk: `G.notes` sürekli büyür, halka tampon gerekir (**T**).
- **Usul tanıtım ekranı**: şarkı kartındaki usul noktaları (3526) zaten var. "Dinle" düğmesinin yanında usulü yalnız davulla çalan 4 ölçülük bir ön çalım eklenebilir. Hem öğretici hem kültürel. Maliyet S.
- **Erişilebilirlik bağları**: oyunun yazıları `calc(var(--arena-text-scale,1) * …)` kullanmalı. `Arena.settings.reducedMotion` açıkken kamera salınımı, ışık nabzı ve konfeti kapanmalı. Titreşim için vuruşta `navigator.vibrate(8)` yalnız dokunmatikte (kit zaten anahtarla sarıyor). Maliyet S. ARENA-KIT bloğuna dokunmadan yapılabilir.

## 6. EKLENMEMELİ
- **Çevrimiçi liderlik tablosu / skor gönderme**: sunucu, hesap ve veri toplama ister → kısıtı aşar. Günlük seri ve paylaş metni yeterli.
- **Gerçek mehter marşlarının kaydı ya da notası (ör. bilinen marşlar)**: telif durumu belirsiz, dosya boyutu ve tek dosya kuralıyla çelişir. Mevcut "koddan usul" yaklaşımı hem güvenli hem özgün.
- **Kaçan notada sazı susturma (Rock Band tarzı)**: Dört Katman zaten ses ödülü veriyor; ikinci bir ceza katmanı oyuncuyu bezdirir. Rock Band oyuncuları bundan şikayet ediyor (K).
- **Video/MP3 müzik akışına geçmek**: Web Audio sentezini ve saat hassasiyetini bozar, `?sim` sanal saatini işlevsiz kılar, boyutu artırır.
- **Daha dar pencere ya da "Mükemmel+" kademesi**: yeni oyuncu sorunu çözülmeden üst uç için derinlik eklemek yanlış öncelik. Swiftshader veya düşük fps cihazlarda haksız hissettirir (**T**).
- **Ağır görsel ekler (bloom/postprocessing)**: UHD 620'de 31 draw call'luk bütçeyi zorlar. Telefonda Düşük kalite zaten gölgesiz.
- **ARENA-KIT bloğunu, importmap'i ya da SRI satırlarını düzenlemek**: kısıt. Erişilebilirlik bağları oyun tarafında yapılmalı.

## 7. Düzeltilmeli
| # | Ne | Kanıt | Maliyet |
|---|---|---|---|
| 1 | Şerit tuşu M, X, L, P'ye atanınca oyun bozuluyor | D, res2.json | S |
| 2 | Telefonda HUD taşması (Kombo kesik, İsabet görünmüyor) | D, phone-play.png | S |
| 3 | Kalite düğmesi "Tuş atandı" diyor ve ayar yeniden yüklemeden uygulanmıyor ("yeniden yükleyince uygulanır" denmeli ya da canlı uygulanmalı) | D, 3632 / 3217-3233 | S |
| 4 | Ölü kod `LANE_LAYER` (ya kullanılmalı, §4.2, ya silinmeli). `G.judged += 0` | D | S |
| 5 | `howto1` tuşları sabit; `S.keys` değerinden üretilmeli | D, 2143 | S |
| 6 | `#judge` aria-live her vuruşta okunuyor → `aria-live="off"`, katman değişimi `#toasts` ile duyurulmalı | D, 1862 | S |
| 7 | Yazı boyutu, hareketi azalt ve titreşim seçenekleri oyunda etkisiz | D, §3.5 | S |
| 8 | Sonuç kartında birincil düğme küçük ekranda katlanma çizgisinin altında → yenilgide "Kolay'da dene" önerisiyle birlikte üstte | D, ekran görüntüsü | S |
| 9 | Gamepad'de duraklat yok (button 9 / Start) | D, 3713 | S |
| 10 | Yüksek karşıtlık `body` filtresinin WebGL maliyeti UHD'de ölçülmeli | T | — |

## 8. Önerilen ilk 3 iş
1. **İlk deneyim paketi (§4.1 + §7.8):** varsayılan Kolay, kalıcı zorluk seçimi, 2 ölçülük ısınma, "Ruh tükenmez" seçeneği, yenilgi ekranında "Kolay'da dene". Gerekçe: en büyük ölçülen sorun bu. Yeni oyuncu 2 sn'de kaybediyor ve oyunun geri kalanını hiç görmüyor. Maliyet S, bota ve kayda risk yok.
2. **Cila hataları (§7.1-7.3, 7.5):** tuş çakışması, telefon HUD'u, kalite bildirimi, howto tuşları. Gerekçe: hepsi doğrulanmış, küçük ve izole. Telefon ilk izlenimi doğrudan düzelir.
3. **Kolay'ı dört şeritli yapmak + katman–şerit eşlemesi (§4.2):** Dört Katman imza mekaniğini anlamlı kılar ve Kolay ile Normal arasına basamak koyar. Önce tek şarkıda pilot (Düyek), `stats.mjs` ile yoğunluk ölç (hedef Kolay ≤ 3,5 nota/sn, Normal'in ~%55'i), bot ve `?sim` ile 0 hata doğrula.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek UHD 620 fps'i ölçülmedi. Makine paylaşımlıydı (load avg ~70), SwiftShader 1-5 fps gösterdi. README'deki 60 fps / 31 draw call iddiası yeniden ölçülmedi. Bu turda yalnız 31 draw call ve 65.544 üçgen okundu (masaüstü başlık ekranı).
- Gerçek dokunmatik cihazda gecikme ve çoklu dokunma (akorlar) denenmedi. Headless'ta ses saati ilerlemediği için (`gt=-0.15`) telefon oyun akışı ölçülemedi; yalnız düzen ölçüldü.
- Yüksek karşıtlık filtresinin performans etkisi ölçülmedi.
- `gc.zgo.at` (GoatCounter) sayaç betiği yükleniyor (1745). "Kullanıcı verisi toplanmaz / harici ağ çağrısı yok" kısıtıyla nasıl bağdaştığı sahibine sorulmalı (mevcut durum, öneri değil).
- 4.2'deki puan dengesi değişikliğinin eski rekorlara etkisi: ayrı anahtar mı, yoksa kabul mü? Sahibin kararı.
- ddrkirby.com ve poki.com bu oturumun ağ izinlerinde yok. O sayfalar okunamadı, yalnız arama özetleri kullanıldı.

## Kaynaklar
- Rhythm Quest devlog 10 (gecikme kalibrasyonu, ses + giriş gecikmesinin tek testte ayrılamaması): https://ddrkirby.com/rhythm-quest/devlog/10.html (yalnız arama özeti)
- Rhythm Quest devlog 13 (basit başlayıp yavaş zorlaşma): https://ddrkirby.com/rhythm-quest/devlog/13.html
- Ritim oyunu zorluk ölçekleme (geniş pencere, kısa zincirler): https://dev.to/hermeshorizon/designing-rhythm-game-difficulty-how-we-scaled-from-80-to-140-bpm-across-5-elemental-realms-2bi7
- Rhythm Doctor ("Unmissable" modu, zorluk sıçramaları): https://vaporlens.app/app/774181/rhythm_doctor.md
- A Dance of Fire and Ice (zorluk sıçramaları): https://vaporlens.app/app/977950/a_dance_of_fire_and_ice.md
- Guitar Hero ve yeni oyuncular: https://pixelpoppers.com/2019/07/guitar-hero-misled-new-players/
- Spin Rhythm XD erişilebilirlik (hız, zorluk): https://www.familygamingdatabase.com/accessibility/Spin+Rhythm+XD
- One Hand Clapping erişilebilirlik (pratik alanı): https://www.familygamingdatabase.com/accessibility/One+Hand+Clapping
- Just Shapes & Beats erişilebilirlik (cezasız mod, ayrı ses seviyeleri): https://www.familygamingdatabase.com/accessibility/Just+Shapes+Beats
- ADOFAI Access (pratik ve önizleme): https://molitvan.pages.dev/projects/adofai-access
- Hi-Fi RUSH erişilebilirlik ayarları: https://support.krafton.com/hc/en-us/articles/52371575035801-Hi-Fi-RUSH-Accessibility-Settings
- MDN AudioContext.baseLatency: https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/baseLatency
- web.dev ses çıkış gecikmesi: https://web.dev/articles/audio-output-latency
- WebAudio issue 2467 (baseLatency + outputLatency): https://github.com/WebAudio/web-audio-api/issues/2467
- Rock Band 3 (kaçan notada susan iz): https://Www.wikipedia.org/wiki/Rock_Band_3 ; https://rhythmgamingworld.com/?p=397814
- CrazyGames teknik gereksinimler ve ilk kare: https://docs.crazygames.com/requirements/technical/ ; https://docs.crazygames.com/resources/getting-to-the-first-frame/
- Poki, kaliteli tarayıcı oyunu (2026): https://poki.com/blog/what-makes-high-quality-browser-game (yalnız arama özeti)
- Portal yayını rehberi (ret nedenleri: uzun yükleme, zayıf mobil, kafa karıştırıcı mekanik): https://app.cinevva.com/guides/publish-game-poki

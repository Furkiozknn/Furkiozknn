# Dolmuş — faz 3 araştırması

Kanıt etiketleri: **D** = doğruladım/ölçtüm (kod satırı ya da koşu), **T** = tahmin/çıkarım, **K** = dış kaynak.
Satır numaraları `index.html` @ `2ea8db8` (origin/main = yerel HEAD). Repo değiştirilmedi.

## 1. Şu anki durum
- **D** Tek dosya, 6344 satır / 372 KB; Three.js r170 importmap + SRI (s.1865), ARENA-KIT v1.0.0 bloğu (s.1511-1864), oyun modülü s.2136-6344.
- **D** Yapı: 8 vardiyalık kampanya (`LEVELS`, s.2936-2945, hedef 160-250 TL, ★★=×1,4, ★★★=×1,85), sonsuz mod (`endlessLevel`, s.2947), günlük meydan okuma = gün tohumlu sonsuz dalga 1-4 (`dailyLevel`, s.5796). Vardiya 240 sn, 12 koltuk (s.4199-4200).
- **D** İmza mekaniği "Hat Ustası" (e22d07b): seviye 2-8'de vardiya öncesi 3 durak + radyo kanalı; hat duraklarında yolcu ×1,6, diğerlerinde ×0,8; kanal yolcu tipi karışımını ve sabrı etkiler; yakıt/rölanti kesintili "hat kârı" rekoru `dolmus.hat` anahtarında (s.3805-3851, 5839-5866, 5913-5917).
- **D** Sabit 60 Hz simülasyon (s.6261-6273), `?auto` botu (s.6198-6241). `?auto&debug&sim=4000&noassets` koşusu: 8/8 vardiya bitti, 0 JS hatası; yıldız/net: 1:2/385, 2:2/285, **3:1/226**, 4:2/343, 5:3/396, 6:2/346, 7:3/453, **8:1/266** (bot hep Arabesk + Balat'lı hat seçiyor, s.6193).
- **D** Kayıt: `arena.dolmus.settings`, `arena.dolmus.save` ({best:{total,stars[8],endless,fares[8]}, run}), `dolmus.hat` (s.2365-2381, 3824). Okumalar `Object.assign` ile varsayılanla birleşiyor → eski kayıtlar güvenli.
- **D** Son commit (fb4402a, 20:34, "relay: Juice Pass", Gemini) arena-kit'ten **sonra** girdi: her jetonda kamera sarsıntısı + titreşim, her çarpmada `#hurt` 0,85 / 300 ms + titreşim (s.4348-4351, 4574-4575, 4595-4596, 4611-4612). Bu commit'in testi/kanıtı yok.
- **D** Headless Chromium (SwiftShader): 1280×720 ve 390×844 açılışta 0 konsol hatası, 0 başarısız istek. SwiftShader'da gerçek zamanlı ~1 fps (yazılım GL; Intel UHD değerini temsil etmez), `?low` ile 50 draw call / 238k üçgen.
- **D** i18n: `STR.tr/en` (s.2182-2352), dil tarayıcıdan; 24 yolcu repliği/dil, 12'lik tekrar penceresi (s.4300-4310).
- **D** Ses tamamen Web Audio sentezi: tek Hicaz ezgisi (s.2385-2395), isteğe bağlı Kenney sfx.
- **D** Mobil: dokunmatik direksiyon kaydırıcısı + gaz/fren/kapı/korna pedalları (s.6117-6135), `pointer:coarse` ile otomatik.

## 2. Güçlü yanlar (korunmalı)
- **D** Belirli bir kimlik: dolmuş, "müsait bir yerde", ücret zinciri (s.4312-4360), esnaf odası makbuzu, Van kedisi. Mekanik fikir (dur-aç-al-bırak + elden ele ücret) türde özgün.
- **D** Vardiya sonu makbuzu en pahalı 2 hatayı düz dille söylüyor (s.5946-5948): iyi bir öğrenme döngüsü.
- **D** Bot + `dolmusSim` + `window.dolmus` QA yüzeyi çok güçlü; deterministik tohumlar (s.4723-4724) ve "klasik vardiya aynı rastgele akışı korur" disiplini (s.3836).
- **D** Kalite bekçisi (s.6247-6260) + elle seçilen kalite asla ezilmiyor; varlıklar ilk kareden sonra, prosedürel yedekle.
- **D** İlk 30 sn: tek tık → 3-2-1 → seviye 1'de koçlu ilk durak (s.5876-5880, `COACH`); bloklayan intro yok.

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Radyo açıkken yolcuların çoğu durağını söylemiyor.** `finishBoard` (s.4295): yolcunun kanala karşı bir "mood"u varsa baloncuk yalnız `moodLike/moodDislike`'tan (her biri **2 replik**) seçiliyor, varış durağı söylenmiyor ve tekrar penceresi atlanıyor. Arabesk'te karışım shopkeeper:4 + diğerleri 1 → binenlerin ~%50'si "like", ~%12'si "dislike" (**D** kod, **T** oran). Seviye 2 ekran görüntüsünde 3 baloncuğun ikisi aynı: "Bu şarkı benim!" (**D** `_dolmus/desktopshot.png`). README'deki "each one names their stop" vaadi radyo açıkken bozuluyor.
2. **Seçilen radyo kanalı duyulmuyor.** Kanal yalnız simülasyon çarpanı; müzik her kanalda aynı Hicaz döngüsü (s.2385-2401; `AUD` içinde kanal referansı yok) (**D**). İmza mekaniğinin yarısı oyuncuya hissettirilmiyor.
3. **"Hareketi azalt" kamera sarsıntısına uygulanmıyor; relay her jetona sarsıntı ekledi.** `HOOK.shake` ve yeni `camState.shake = 0.45` (s.4349, 5775) Arena `reducedMotion`'ı okumuyor; `updateCamera` rastgele titreşim uyguluyor (s.5616-5618). Ölçüm: `reducedMotion: 'reduce'` + `?auto&sim=90`: Arena ayarı `true`, `data-arena-reduced-motion` var, 0 çarpışma, 2 yolcu ödedi → `camState.shake = 0.415` (**D** `_dolmus/run.cjs rm`). Durakta her ücrette (3-6 jeton) kamera titriyor: Xbox XAG 117 sarsıntının kapatılabilir olmasını ister (**K**). Ayrıca çarpmada `#hurt` iki kez tetikleniyor (`addDent→HOOK.hurt` 120 ms + relay 300 ms) (**D** s.4558, 4574).
4. **Telefonda HUD çakışması.** 390×844'te üst bar 155 px'e sarıyor ama `--barh` yalnız `setHud`/`resize`'da ölçülüyor (s.4804, 5821; ResizeObserver yok) → mini harita (y=127) ve hız göstergesi üst barın üstüne biniyor, hız göstergesi dil düğmesini kapatıyor; nazar boncuğu saat rakamlarını örtüyor (**D** `_dolmus/phoneshot.png`, ölçülen kutular). Not: testte Google Fonts boş döndürüldü; gerçek fontla bar yüksekliği farklı olabilir (**T**), ama font geç yüklenince aynı bayat ölçüm oluşur.
5. **Baloncuk metni telefonda taşıyor.** `.bubble {white-space:nowrap; max-width:60vw}` (s.766-767) → 390 px'te metin kutunun dışına çıkıyor (**D** phoneshot).
6. **"Oyna" kampanya kaydını onaysız siliyor.** `startCampaign(false)` → `runSave = null; writeSave()` (s.5829); "Devam" ikinci düğme, büyük sarı "OYNA" birinci (**D**).
7. **Seviye seçimi yok, ama 24 yıldız hedefi ve "tüm yıldızlar" rozeti var.** Biten bir vardiyayı tekrar oynamanın tek yolu baştan kampanya ya da `?level=N` (s.5827-5831, 5923; `bestLine` "x/24 yıldız") (**D**). 3 yıldız avı pratikte erişilemez.
8. **Zorluk sıçramaları.** Bot seviye 3 (yağmur+kamyonet) ve 8'de (gece) hedefin %13 / %6 üstünde kaldı; diğerlerinde ★★-★★★ (**D** bot koşusu). İnsan için seviye 3 erken bir duvar olabilir (**T**).
9. **EN modunda sabit Türkçe metinler**: pedal etiketleri `FREN/GAZ/KAPI/KORNA` (s.1958-1961, `data-i` yok), "VARDİYA MOLA", "KOKPİT & SİGORTA PANELİ", makbuz başlıkları (**D** HTML). Bir kısmı tat olarak kalabilir, pedaller kalamaz.
10. **Renge dayalı işaretler**: kaldırım halkası yeşil/turuncu/kırmızı (s.5351), koltuk çipi sabır renkleri; şekil/simge farkı yok (**T**, renk körlüğü testi yapılmadı).
11. Küçükler: başlık levhası "KADIKÖY — BOSTANCI" oyundaki duraklarla örtüşmüyor (**D** s.2035); `dolmus.hat` anahtarı `arena.` önekli değil (**D**).

## 4. EKLENMELİ — yüksek değer
**4.1 Baloncukta her zaman varış durağı (+ ruh hali simgesi)** — Ne: mood'lu yolcu da `voiceLine` ile durağını söylesin; mood ayrı küçük ikon/ikinci kısa satır (koltuk çipinde zaten var). Neden: oyunun çekirdek bilgisi; tekrar eden 2 replik yerine 24'lük havuz. Nasıl: s.4295'te `txt = voiceLine(...)`, mood varsa başına 🎵/🔇 benzeri tek karakter ya da `moodLike` havuzunu 6+ replik yapıp `{0}` durak adı içersin; `CR` çağrı sayısı değişmesin diye `cpick` sırasını koru (bot/tohum uyumu). Maliyet **S**. Risk: düşük; `CR` akışı değişirse bot sonuçları değişir → `?auto&sim=4000` ile tekrar doğrula. Kanıt: §3.1.

**4.2 Duyulabilir radyo kanalları** — Ne: her kanal için prosedürel müzik varyantı: Arabesk = mevcut Hicaz; Pop = majör/hızlı (≈118 BPM), Türkü = Hüseyni/Uşşak benzeri dizi + bağlama-benzeri pluck, Haberler = kısa jenerik + "konuşma" mırıltısı (filtrelenmiş gürültü), Kapalı = sadece motor/şehir. Neden: imza mekaniğinin seçimi hissedilir olur; yolcu tepkisi ("Kıs şunu") anlam kazanır. Nasıl: `AUD` içinde `SC/MEL/STEPDUR/CHORDS`'u kanala göre tablo yap, `beginShift`'te `AUD.setChannel(SIM.plan.ch)`; yeni dosya yok. Maliyet **M**. Risk: CPU düşük (aynı osilatör sayısı); gerçek şarkı/melodi kopyalanmamalı (kendi dizileri). Kısıta uygun.

**4.3 Hareket/titreşim ayarına saygı + juice'u ölçülü yap** — Ne: `HOOK.shake` ve jeton sarsıntısı `Arena.settings.reducedMotion` iken 0; jeton sarsıntısını kaldır ya da yalnız bahşişli jetonda çok küçük (≤0,1) yap; `#hurt`'u tek yoldan (`HOOK.hurt`) tetikle. Nasıl: `const motionOK = () => !(window.Arena && Arena.settings.reducedMotion)`; s.4349 ve s.5775'te kontrol; relay'in s.4574/4595/4611 satırlarındaki tekrar opaklığı sil (titreşim kalabilir, Arena sarmalıyor). Maliyet **S**. Risk: yok. Kaynak: Xbox XAG 117/118 (**K**).

**4.4 Vardiya seçimi (kilit açılmış seviyeler)** — Ne: başlıkta "Vardiyalar" ızgarası: 8 kart, her birinde en iyi yıldız/TL ve hat rekoru; kampanyada ulaşılan seviyeye kadar açık. Neden: 24 yıldız ve "tüm yıldızlar" rozeti erişilebilir olur; kısa oturumlu (4 dk) tarayıcı oyununda "bir tane daha" döngüsü. Mini Metro şehir kilitlerini skorla açar ve tekrarı aynı haritada yaptırır (**K**). Nasıl: yeni `screen` (sRoute deseni), `best.stars[i] > 0 || i <= maxReached` ile açık; seçilen vardiya `G.mode='practice'` → `runSave`'e dokunmaz, yalnız `best.*` ve `dolmus.hat` günceller. Kayıt: ek alan `best.reached` (yoksa `stars`'tan türet) → eski kayıt uyumlu. Bot: `?auto` başlıktan yine `startCampaign` çağırır, etkilenmez. Maliyet **M**.

**4.5 Telefon HUD düzeltmesi** — Ne: `--barh`'ı `ResizeObserver(topbar)` + `document.fonts.ready` ile güncelle; dikey telefonda üst barı 2 satırda sabit düzenle, nazarı saatin üstünden al ya da `body.touch`'ta gizle; baloncuğa `white-space:normal; max-width:min(60vw,260px)`. Maliyet **S**. Risk: yalnız CSS/ölçüm. Poki dikey mobil QA'yı zorunlu tutuyor (**K**). Kanıt: §3.4-3.5.

## 5. EKLENEBİLİR — orta değer / koşullu
- **"Yeni oyun" onayı** (S): kayıt varken "OYNA" → "Devam" birincil olsun, yeni kampanya için ikinci onay. §3.6.
- **Seviye 3 / 8 ayarı** (S): bot payı ince; hedefi ~%5 düşürmek ya da seviye 3'te ilk yağmuru 60→90 sn'ye almak. Önce 2-3 insan oyunu ya da bot+farklı tohum (`?seed=`) ile ölç; `?cal` hazır. Hedef değişince eski `best.stars` korunur (yalnız artar).
- **Günlük meydan okumada Hat Ustası** (S-M): günlük şu an hat/radyosuz sonsuz dalga; günün sabit "önerilen hattı" ile oynamak paylaşılan bulmaca hissi verir (günlük tohum deseni, **K** gamedeveloper/dev.to). `planFits` yalnız daily için genişletilir; kampanya akışı değişmez.
- **Renk körü ipuçları** (S): kaldırım halkasına durum simgesi (✓ / ! / ✕) ya da desen; koltuk çipinde sabır için doluluk çubuğu zaten var, renge ek şekil.
- **EN pedal etiketleri** (S): `data-i` ekle (GAS/BRAKE/DOOR/HORN); "VARDİYA MOLA" gibi tat metinleri TR kalabilir ama altına EN alt yazı.
- **Kişisel en iyi "hayalet" dolmuş** (M): seviye başına 2 Hz konum kaydı (~480 nokta, localStorage), yarı saydam ikinci dolmuş. Değer orta: yolcu/trafik rastgeleliği yüzünden yarış hissi zayıf (**T**); önce 4.4 gelsin.
- **Eğerek direksiyon (tilt) seçeneği** (M): `DeviceOrientation`, iOS'ta izin ister; varsayılan kapalı. Kaydırıcıyla birlikte opsiyon.

## 6. EKLENMEMELİ
- **Çevrim içi skor tablosu / bulut kayıt / hesap**: sunucu + kullanıcı verisi → kısıtı aşar.
- **Daha fazla ekran sarsıntısı, tam ekran kırmızı flaş, kare donması (hit-stop) türü "juice"**: zaten §3.3 sorunu; 4 dk'lık sürüşte sürekli tekrar eder, mide bulandırır; Intel UHD'de ek post-process maliyeti.
- **Gerçek şarkı / tanınabilir radyo jingle'ı, gerçek marka logoları** (THY esprisi dahil genişletilmemeli): telif + brief kuralı.
- **Serbest dolaşım/açık dünya, yeni ilçe haritası**: tek dosya 372 KB; world-gen bütçesi (52-65 draw call) ve yükleme süresi büyür; ölçüm yapılmadan L+ iş.
- **Hasar/yakıt yönetimi için ikinci kaynak çubuğu, yükseltme ağacı (mağaza)**: HUD telefonda zaten dolu (§3.4); kampanya dengesi ve bot hedefleri bozulur.
- **Yeni zorunlu ekran** (her vardiya öncesi ek ekran): seviye 2+'da zaten Hat Ustası araya giriyor; daha fazlası ilk-30-sn akışını bozar.
- **ARENA-KIT bloğuna müdahale** (ör. reducedMotion'ı orada JS'e yaymak): kısıt; çözüm oyun tarafında okumak.

## 7. Düzeltilmeli (hata, cila, erişilebilirlik, performans)
- s.4295 mood baloncuğu durağı gizliyor (§4.1). — hata
- s.4349 jeton sarsıntısı + reduced-motion yok sayılıyor (§4.3). — erişilebilirlik
- s.4574/4595/4611 `#hurt` çift tetikleme; `HOOK.hurt` kullan. — cila
- s.4804/5821 bayat `--barh` → telefonda HUD çakışması (§4.5). — mobil
- s.766 `.bubble` nowrap taşması. — mobil
- s.5829 "OYNA" onaysız kayıt silme. — kayıt güvenliği
- Pedal etiketleri ve birkaç başlık EN'de Türkçe. — i18n
- Başlık levhası "KADIKÖY — BOSTANCI" → oyundaki bir hat (ör. "BALAT — KADIKÖY İSKELE"). — tutarlılık
- Relay commit'i (fb4402a) için en azından `node tools/smoke.mjs` + bot koşusu kanıtı repoya/PR'a eklenmeli (CLAUDE.md "yeşil ≠ test edildi").

## 8. Önerilen ilk 3 iş
1. **Juice/erişilebilirlik onarımı + baloncukta durak (4.3 + 4.1)** — S+S. En son girmiş, test edilmemiş relay değişikliği reduced-motion ayarını fiilen deliyor (ölçüldü) ve imza mekaniği çekirdek bilgiyi (durak) gizliyor. Ucuz, düşük riskli, bot ile hemen doğrulanır.
2. **Telefon HUD + baloncuk + "OYNA" onayı (4.5 + §5 ilk madde)** — S. Telefon brief kısıtı; ölçülen çakışma dil düğmesini kullanılamaz yapıyor. Kayıt silme bir dokunuşluk kayıp.
3. **Vardiya seçimi (4.4), ardından duyulabilir radyo (4.2)** — M. 4.4 mevcut yıldız/rozet sistemini anlamlı kılar (tekrar oynanabilirlik); 4.2 Hat Ustası'nın "radyo" yarısını gerçek bir seçime çevirir. 4.4 önce, çünkü kayıt biçimi kararını (practice modu, `best.reached`) erken sabitler.

## 9. Doğrulanmayanlar / açık sorular
- Intel UHD'de gerçek fps ölçülmedi (SwiftShader ~1 fps, anlamsız); README'deki 60 fps ölçümü relay öncesi.
- Telefon bar yüksekliği gerçek Google Fonts ile ölçülmedi (testte fontlar boş döndü); çakışmanın gerçek cihazda ne kadar olduğu **T**.
- İnsan oyuncu için seviye 3 / 8 zorluğu bilinmiyor; yalnız bot verisi var.
- Radyo açıkken yolcu mood oranları koddan hesaplandı, sayılmadı (`G.voices` ile sayılabilir).
- Firefox/WebKit'te bu sürüm koşulmadı (yalnız Chromium).
- Renk körlüğü simülasyonu yapılmadı.
- `tools/smoke.mjs` bu oturumda koşulmadı (eşdeğer yükleme kontrolü yapıldı: 0 hata).

## Kaynaklar
- Xbox Accessibility Guideline 117 (görsel dikkat dağıtıcılar, kamera sarsıntısı kapatılabilir olmalı): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117
- Xbox Accessibility Guideline 118 (fotosensitivite): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/118
- Poki gereksinimleri / dikey mobil ve uyarlanabilir kontroller: https://sdk.poki.com/requirements , https://poki.com/blog/building-web-browser-games-2026 , https://poki.com/blog/what-makes-high-quality-browser-game
- Crazy Taxi çekirdek döngü (kısa yoğun oturum, ok yönlendirme, hız ödülü): https://en.wikipedia.org/wiki/Crazy_Taxi , https://itch.io/blog/530882/breaking-down-elements-related-to-core-loop-of-crazy-taxi
- Mini Metro (skorla şehir kilidi, aynı haritada tekrar): https://giantbomb.com/wiki/Games/Mini_Metro , https://dinopoloclub.com/2018/08/16/challenge-completed/
- Günlük tohumlu koşular / hayalet tekrar: https://gamedeveloper.com/design/the-24-hour-ticket-examining-daily-runs- , https://dev.to/gowtham_r_2002/one-seed-same-puzzle-for-everyone-seeded-rng-for-a-fair-daily-challenge-1h7d , https://kindatechnical.com/game-development/replay-systems-and-input-recording.html
- Yerel kanıt: `_dolmus/run.cjs`, `_dolmus/desktop-title.png`, `_dolmus/desktopshot.png`, `_dolmus/phoneshot.png`

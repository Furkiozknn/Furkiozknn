# Kervan — faz 3 araştırması

Repo: `/home/user/kervan` (dal `claude/cloud-session-research-analysis-dufc2b`, HEAD 48b2745, `git status` temiz). Ana dosya `index.html` 5083 satır / 295 KB.
Kanıt etiketleri: **D** = doğruladım/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Geçici dosyalar ve ekran görüntüleri: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_kervan/` (`bot.cjs`, `run.cjs`, `out.json`, `run.log`, `d1-3*.png`, `p1-3*.png`).

## 1. Şu anki durum
- **D** Oyun 3D İpek Yolu ticaret stratejisi: 7 şehir, 7 mal, 9 yol, 7 han, 3 rakip tüccar. Bütün kurallar `ECONOMY` tablosunda (s. 1003-1064). Simülasyon render'dan bağımsız (`/*SIM-START*/…/*SIM-END*/`, s. 990-1945), Node'da çalışıyor.
- **D** Hedef: 5. yıl bitmeden 10.000 akçe ve 3 han (s. 1056). Yıl 4×20 gün, oyun 400 gün. Yıldız eşikleri 160/280. gün (s. 1057). Kazandıktan sonra sonsuz mod var (s. 1818).
- **D** İmza mekaniği "söylenti ticareti" (commit 29a0ae3, öneki `oyun:`; git log'da `oynanis:` önekli commit yok). Söylenti 25 akçe, şehir başına 4 günde bir. %70 doğru çıkıyor, kendi hanı olan yolda %88. Kendi RNG akışını (`S.rrng`) kullanıyor (s. 1239-1306).
- **D** ARENA-KIT bağlı (s. 1948-2301): `Arena.perf.attach` (s. 2423), günlük meydan okuma tohumu kayda yazılıyor (`S.daily`, s. 4079), rozetler, paylaş, "başka oyun" (s. 4697-4731). Erişilebilirlik paneli Ayarlar'dan açılıyor (s. 4636).
- **D** Kayıt `arena.kervan.save` = `{v:1, S, at}`. Yalnız gün sonunda (s. 4151) ve sekme gizlenince (s. 4804) yazılıyor. Söylenti alanları eski kayıtta tembel başlatılıyor (`rumorState`, s. 1242), yani eski kayıtlar yükleniyor. Göç (migration) kodu yok.
- **D** TR/EN anahtar eşliği tam: 211/211 anahtar, eksik yok (`_kervan/i18n.cjs` ile ölçtüm).
- **D** Son üç commit, incelenmemiş "relay" düzenlemeleri (gemini flash-lite): 7a3fb65 hızlı alım düğmeleri, 7153fae dokunma isabet alanı, 05af673 otomatik düşük kalite. Hepsi arena-kit'ten sonra geldi. Üçünde de sorun buldum (§3).
- **D** `?auto` botu tarayıcıda çalışıyor: `?auto&seed=5&noassets&sim=1800` 142. günde kazandı (10.229 akçe, 3 han), 0 JS hatası. README'deki "day 142 for seed 5" ile aynı.
- **D** Node'da bot, tohum 1-12: 11 galibiyet, 1 iflas (tohum 6, 68. gün). Galibiyet günleri 123-223, 4 tohumda 3 yıldız. Aynı sonuç söylenti öncesi commit'te (1add515) de çıkıyor, yani söylenti ekonomiyi değiştirmemiş. Dikkatsiz bot 12/12 ilk 28 günde iflas ediyor.
- **D** Masaüstü 1280×720 (swiftshader): oyun 13 sn'de hazır, 26 draw call, 92k üçgen, 0 hata. Makine aşırı yüklüydü (load average 65-73), bu yüzden ölçülen 10 fps anlamsız. Telefon 390×844: yatay taşma yok (`scrollWidth` 390), 0 hata.

## 2. Güçlü yanlar (korunmalı)
- Simülasyon ile render ayrımı ve tek `ECONOMY` tablosu. Denge ve bot testi Node'da saniyeler sürüyor (12 tohum ≈ 4 sn CPU). **D**
- Bot oyuncunun eylemlerini kullanıyor (`KervanBot`, s. 1825), dikkatsiz bot iflas ediyor. Ekonomi "düşünen oyuncuyu ödüllendiriyor". **D**
- Söylenti mekaniği ayrı RNG akışı kullanıyor. Deterministik tohum ve günlük meydan okuma bozulmuyor (s. 1240). **D**
- Fiyat önizlemesi: alım/satım kaydırıcısı ortalama fiyatı ve işlem sonrası fiyatı gösteriyor (s. 4466-4469). Oyuncu fiyatı kendi hareketiyle bozduğunu görüyor. **D**
- Modal açıkken oyun duruyor, render 15 karede bire düşüyor (s. 4867, 4892). Gölgeler 30 Hz'de güncelleniyor (s. 4891). **D**
- Görsel kimlik güçlü: parşömen ve deri arayüz, gün/gece, mevsim boyama (`d2-play.png`). **D**
- Klavye kısayolları tam, Esc katmanlı kapanıyor (s. 4778-4803). `toasts` alanı `aria-live` (s. 970). **D**

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Varsayılan "Düşük" kalite çoğu masaüstünde açılıyor (05af673).** `isLowSpec = hardwareConcurrency <= 4 || devicePixelRatio < 1.5` (s. 2327).
   - Neden sorun: DPR 1 olan her 1080p monitör ve DPR 1.25 olan çoğu dizüstü bu koşula giriyor. Düşük kalitede gölge yok, HDRI yok, asset modelleri yok, ağaç ve parçacıklar yarıya iniyor (s. 2425, 3041, 5003, 5019).
   - Ölçüm **D**: headless ortamda (hc=4, dpr=1) `shadowMap.enabled=false` çıktı. Kayıtlı ayarı olmayan yeni oyuncu bu varsayılanı alıyor ve `saveSettings` ile kalıcı oluyor.
   - Gereksiz: `Arena.perf` zaten zayıf GPU için piksel oranını dinamik düşürüyor (s. 2423, 2273). README, hedef makine Intel UHD 620'de High için 60 fps ölçmüş. Değişiklik ölçümsüz yapılmış.
2. **Mal başına "Hepsini sat" kalktı (7a3fb65).**
   - Düğmeler artık `1/4`, `1/2`, `Maks` (s. 4453-4455). Üçü de yalnız alım yönünde çalışıyor ve `maxB=0` iken devre dışı. Yani yük doluyken hiçbiri çalışmıyor. **D**: `out.json` → `trade.btns`.
   - Tek bir malı satmak için artık kaydırıcıyı sürüklemek gerekiyor. Telefonda bu zahmetli. Şehir düzeyindeki `cSellAll` bütün yükü satıyor, ama sözleşme malını tutmak isteyen oyuncu için bu bir çözüm değil. **D**/**T**
   - Ek kusurlar: "Maks/Max" metni i18n dışında sabit yazılmış (s. 4455). `tradeBox` içindeki `maxAff` hiç kullanılmıyor (s. 4443). `maxAffordable` aynı render'da iki kez hesaplanıyor (s. 4443, 4474). **D**
3. **Dokunma isabet çarpanı 2,2 (7153fae, s. 3981-3985).**
   - Şehir yarıçapı 68×2,2 ≈ 150 px, 390 px genişliğindeki ekranın yaklaşık %77'si. Haritada boş bir yere dokunmak çoğunlukla bir şehri seçer ya da kervanı yönlendirir. Seçili kervan varken yanlışlıkla sefer emri verilebilir (`cityClicked`, s. 4298).
   - Hesap **D**, oyuncu etkisi **T** (cihazda denenmedi). Kaydırma sürüklemeyle yapıldığı için risk kısmen azalıyor.
4. **Bot imza mekaniğini hiç kullanmıyor.** `KervanBot` `buyRumor` çağırmıyor. 12 tohumda söylenti sayısı 0. **D**. `?auto` regresyon testi söylentiyi kapsamıyor. Söylentinin beklenen değeri (25 akçeye değer mi) ölçülmemiş. **T**
5. **README iddiası güncel değil.** README "12 of 12 seeded runs" diyor, oysa tohum 1-12'de tohum 6 68. günde iflas ediyor (1add515'te de aynı). README'nin hangi tohum kümesini kullandığı belirsiz. **D**/**T**
6. **Telefonda üst bilgi alanı kalabalık.**
   - HUD 378×150 px (ekranın %18'i), kervan çubuğu 134 px. Ekranın yaklaşık %34'ü arayüz. **D** `phoneLayout`
   - İlk ipucu toast'u akçe/kervan/han çiplerinin üstüne biniyor; ilk 7 saniyede oyuncu parasını göremiyor. **D** `p2-play.png`
   - Telefonda tarih çipinde gün numarası yok ("Year 1 · Spring"). **D**
   - Sol alttaki dekoratif "KERVAN FİLOSU" logosu harita alanı yiyor. **D** `d2/p2`
7. **i18n sızıntıları.** Duraklat menüsünde "WASD / Oklar", "+ - / Tekerlek" EN modunda da Türkçe (s. 4615-4616). Şehir panelindeki "spread" TR modunda da İngilizce (s. 4402). **D**
8. **Gün içi kayıp riski.** Han kurma ve alım hemen kaydedilmiyor (yalnız gün sonunda ve `visibilitychange` ile). Mobil tarayıcının sekmeyi öldürdüğü bazı durumlarda gün içindeki işlemler kaybolabilir. **T**
9. **Erken oyun kırılganlığı.** Tohum 6'da akıllı bot bile iflas ediyor. İnsan oyuncu için ilk 20 günde borç tuzağı daha olası. Borç uyarısı yalnız bir toast (s. 1735, 4143). **D**/**T**

## 4. EKLENMELİ — yüksek değer
**4.1 Relay gerilemelerini düzelt (kalite varsayılanı, Hepsini sat, dokunma alanı)**
- Ne: `isLowSpec`'i kaldır (ya da yalnız `hardwareConcurrency <= 2`). Varsayılan `isPhone ? 'low' : 'high'`, gerisini `Arena.perf` yapsın. Mal başına `Hepsini sat` düğmesini geri getir, `1/4 · 1/2 · Maks`'ı alım için tut, "Maks" metnini `t('maxBuy')` yap. Dokunma çarpanını yaklaşık 1,6-1,8'e indir ya da en yakın hedefi `d/r` ile seçip mutlak üst sınır koy (örn. 90 px).
- Neden: §3.1-3.3. Hedef makinede görsel düşüyor, satış zahmetli, yanlış dokunma riski var.
- Nasıl: 3 küçük düzenleme (s. 2327-2328, 4441-4478, 3981-3985). Doğrulama: smoke, `?auto` 2 tohum, 390×844 ekran görüntüsü.
- Maliyet S. Risk düşük. Kayıtlı ayarlar zaten `store.get(SKEY)` ile önce geldiği için yalnız yeni oyuncuyu etkiler. Kısıta uygun.
- Kaynak: NN/g dokunma hedefi en az ~1 cm, Apple 44 pt, Material 48 dp (K). Gerekenden büyük alan komşu hedefleri yutuyor (T).

**4.2 "Pazar defteri": görülen fiyatların hafızası**
- Ne: Kervan bir şehre vardığında o şehrin fiyatları `S.seen[city] = {day, buy[], sell[]}` olarak kaydedilir. Pazar panelinde "Bildiğin fiyatlar" sekmesi açılır: her mal için en iyi bilinen alış ve satış şehri ile "N gün önce" bilgisi.
- Neden: Şu an oyuncu başka şehrin fiyatını görmek için o şehrin panelini açıyor. Sonuçta bütün fiyatlar her an tam görünür, yani bilgi asimetrisi yok, ve bu söylenti mekaniğinin değerini düşürüyor (T). Port Royale incelemelerinde en sık istek "limanlar arası fiyat karşılaştırması" (K). Eski bilgi ile söylenti birlikte "ilginç karar" üretir (Meier'in tradeoff/situational ölçütleri, K).
- Nasıl: Sim'e `noteSeen(city)` eklenir, `arrive()` içinde çağrılır. UI'da tablo kullanılır, yeni 3D nesne yok.
- Kayıt: `S.seen` yoksa boş başlar, eski kayıt uyumlu. Bot etkilenmez, çünkü gerçek fiyatları okumaya devam eder.
- Seçenek: diğer şehirlerin canlı fiyatını gizlemek (sis) daha radikal. Önce yalnız defter + "bayat" etiketi eklenmeli.
- Maliyet M. Risk orta: sis seçilirse denge değişir, bu yüzden Node bot testi gerekir.

**4.3 Botun söylenti kullanması + denge ölçümü**
- Ne: `KervanBot.smart` söylentiyi şu koşulla alsın: güvenilir şehir ve `S.akce > 300`. Rota puanına söylenen şoku `dir*pct*olasılık` ile katsın.
- Neden: `?auto` imza mekaniği için regresyon testi olur. Söylentinin beklenen değeri ölçülür (25 akçe çok mu ucuz ya da pahalı?).
- Nasıl: `bestPlan` içinde `S.rumors` filtrelenir. `_kervan/bot.cjs` benzeri bir Node betiği `tools/` altına eklenebilir (12 tohum, söylentili ve söylentisiz karşılaştırma).
- Maliyet S-M. Risk: bot galibiyet günleri değişir, README rakamları güncellenmeli. Kısıta uygun.

**4.4 İlk 3 dakikaya rehberli ilk sefer**
- Ne: 3 adımlı bağlamsal görev şeridi (toast değil, kalıcı küçük kart): "Konya'da halı al (üretir, ucuz)" → "İzmir'e gönder (halı ister)" → "Sat". Tamamlanınca kart kaybolur.
- Neden: Bugün ipucu tek bir 7 sn'lik toast (s. 4087), telefonda HUD'u kapatıyor (§3.6). Hangi malın nereye gideceğini oyuncu tablodaki P/D etiketlerinden çıkarmak zorunda. İlk kazancı erken göstermek ve zorunlu metinden kaçınmak öneriliyor (K: onboarding kaynakları).
- Nasıl: `S.tut` adımı kayda yazılır. Koşullar `trade`/`depart`/`arrive` olaylarından gelir (s. 4123). `?auto`'da kapalı.
- Maliyet S-M. Risk düşük. Telefonda kart, kervan çubuğunun üstüne yerleştirilmeli.

**4.5 Telefon HUD'unu sadeleştir**
- Ne: Telefonda HUD tek satıra (tarih+gün · akçe · han) ve bir hız düğmesine (1x→2x→4x döngüsü) insin. İpucu toast'u HUD'un altına konumlansın. Dekoratif filo logosu telefonda gizlensin.
- Neden: §3.6, harita alanı %34 arayüz. Kısıt "telefon dikey destek".
- Nasıl: Yalnız CSS media query + `buildHud` küçük dal. Maliyet S. Risk: düşük, düğmeler 44 px kalmalı.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Borç kurtarma seçeneği**: Borçtayken "deve sat / yükü sat" önerisi olan bir kart. Tohum 6 tipi erken iflasları yumuşatır. Maliyet S. Risk: kolaylaştırma; dengeyi bot ile ölç. (T)
- **"Seferi tekrarla" (tek kervan, tek tur)**: Son rotayı ve aynı alımı tekrar öneren tek düğme; tam otomasyon değil. İnceleyenler otomatik rotayı Port Royale'in en zor kısmı buluyor (K). Düğme oyuncunun kararını korur. Maliyet M. Risk: oyun kendini oynamaya kayar, bu yüzden yalnız öneri olmalı.
- **Mevsim takvimi**: Ledger'da sonraki kar (geçit kapanışı) ve sel günleri. Kontratlar zaten "ilk kardan önce" diyor. Maliyet S.
- **Kayıt anında yazma**: `buildHan`, `buyCaravan` ve `acceptContract` sonrasında `save()` çağrılsın. Maliyet S. Risk: localStorage yazımı küçük, sorun beklenmez.
- **Rakip tüccarların görünür izi**: Panelde "Venedik tüccarı dün buradan 20 ipek aldı" satırı. Fiyat hareketini açıklar. Maliyet S-M.
- **Haftalık/günlük değişken (mutator)**: Günlük meydan okumaya tek kural ekle (örn. "bu gün haydut iki kat"). Mevcut günlük tohumla uyumlu, `S.daily` yanında `S.mod`. Maliyet M. Not: arena-kit bloğu düzenlenmez, kural oyun tarafında okunur.

## 6. EKLENMEMELİ
- **Çevrimiçi lider tablosu, bulut kayıt, çok oyunculu pazar.** Sunucu ve hesap gerektirir: kısıtı aşar.
- **Üretim zinciri / şehir yönetimi (Patrician tarzı ayrıntı).** İncelemeler fazla ayrıntının eğlenceyi öldürdüğünü söylüyor (K, worthplaying). Ayrıca 7×7 tablo telefonda zaten sınırda.
- **Tam otomatik ticaret rotaları.** Oyunun çekirdek kararı rota ve mal seçimi; "bilgisayar eğleniyor, oyuncu değil" (K, Soren Johnson/Meier).
- **Korsanlık/savaş modu.** Ticaretin değerini gölgeler (K, Port Royale oyuncu yorumu), ayrıca tür kayması.
- **Donanım sinyaliyle kör kalite düşürme** (`hardwareConcurrency`/DPR). Ölçümsüz; `Arena.perf` zaten var (§3.1).
- **Daha fazla mal veya şehir.** Tablo ve harita telefonda dolu; denge ve bot yeniden ayarlanmalı. Değeri düşük.
- **Gerçek oyunlardan isim veya kopya içerik** (Patrician/Port Royale UI'si, gemi sınıfları vb.).

## 7. Düzeltilmeli (hata, cila, erişilebilirlik, performans)
- s. 2327: `isLowSpec` (§3.1). **D**
- s. 4441-4478: mal başına "Hepsini sat" geri gelsin, "Maks" metni `t()` ile, ölü `maxAff` silinsin, alım için 0 akçe durumunda düğmeler devre dışı olsun. **D**
- s. 3981-3985: dokunma alanı üst sınırı. **D**/**T**
- s. 4615-4616: duraklat tuş listesi i18n'e (`keyPanKeys`, `keyZoomKeys`). **D**
- s. 4402: "spread" → `t('spread')` (TR: "makas"). **D**
- Telefon: ilk ipucu toast'u HUD'un altına (CSS `#toasts` top). **D** `p2-play.png`
- Telefon tarih çipinde gün numarası yok. **D**
- README: bot iddiası tohum kümesiyle birlikte güncellensin (1-12'de 11/12). **D**
- `newYearStats_unused` (s. 1939) ve `const pr = 0; void pr;` (s. 4483) ölü kod. **D**
- Tıklanabilir tablo satırları `tr[tabindex]`, ama rolü yok. `role="button"` ve `aria-expanded` eklenmeli. **D**/**T**

## 8. Önerilen ilk 3 iş
1. **Relay gerilemelerini düzelt (§4.1 + §7'deki küçük i18n kalemleri).** Üç commit incelenmeden main'e girdi. Biri hedef makinede görseli düşürüyor, biri satış akışını bozuyor. En ucuz ve en yüksek getirili iş (S). Pilot: `?auto` 2 tohum + smoke + 390×844 görüntü.
2. **Botun söylenti kullanması ve Node denge betiği (§4.3).** İmza mekaniği ancak bu sayede test kapsamına girer. Bir sonraki ekonomi değişikliğinin (§4.2) güvenli yapılması da buna bağlı (S-M).
3. **Pazar defteri (§4.2), önce gizlemesiz.** Ticaret çekirdeğine bilgi kararı ekler, söylentiye anlam verir, kayıtla uyumlu (M). Ardından §4.4 (ilk sefer rehberi) ve §4.5 (telefon HUD'u) gelmeli.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek Intel UHD dizüstünde High ile Low arasındaki fps farkı ölçülmedi. Ölçüm ortamı aşırı yüklüydü (load average 65-73, swiftshader), fps sayıları anlamsız.
- Dokunma alanının gerçek cihazdaki yanlış seçim oranı denenmedi (Playwright `tap` ile yalnız düzen ölçüldü).
- README'deki "12/12" tohum kümesi bilinmiyor. Benim kümem tohum 1-12.
- Söylentinin beklenen kârı ölçülmedi (bot onu kullanmıyor).
- GoatCounter analitiği (s. 964) "kullanıcı verisi toplanmaz" kısıtıyla nasıl uzlaşıyor? Mevcut bir karar gibi görünüyor; dokunmadım, ama kullanıcıya sorulmalı.
- Firefox ve WebKit çalıştırılmadı (yalnız Chromium).
- Ses ve müzik dinlenmedi (headless; AudioContext jest uyarısı beklenen davranış).

## Kaynaklar
- NN/g, Touch Target Size — https://www.nngroup.com/articles/touch-target-size/
- Ocean View Games, Mobile UI for complex games (Apple 44 pt / Material 48 dp) — https://oceanviewgames.co.uk/blog/posts/mobile-ui-design-complex-games
- CrazyGames gereksinimleri (kalite, mobil, boyut) — https://docs.crazygames.com/requirements/quality/ , https://docs.crazygames.com/requirements/technical/ , https://docs.crazygames.com/requirements/gameplay/
- Poki kalite rehberi — https://sdk.poki.com/poki-quality-guidelines
- Port Royale incelemesi (fiyat karşılaştırma isteği, ayrıntı/otomasyon) — https://worthplaying.com/article/2003/8/26/reviews/12008-pc-review-port-royale/
- Patrician 3 oyuncu tartışması — https://www.gog.com/forum/patrician_series/p3_production_woes_how_do_you_handle_it/page1
- Rise of Venice incelemesi — https://www.gamespot.com/reviews/rise-of-venice-review/1900-6415468/
- Soren Johnson, OTC Designer Notes #1 (opak sistemler, "bilgisayar eğleniyor") — https://www.designer-notes.com/otc-designer-notes-1-unit-selection/
- Interesting decisions (Meier) — https://www.gamedeveloper.com/design/designing-interesting-decisions-in-games-and-when-not-to- , https://dandylyons.github.io/notes/Clippings/Sid-Meier's-Interesting-Decisions

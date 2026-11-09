# Boğaz Vapuru — faz 3 araştırması

Repo `/home/user/bogaz-vapuru` @ `0db54e4` (git status temiz; repoda hiçbir dosya değişmedi). Geçici dosyalar ve ekran görüntüleri:
`/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_bogaz-vapuru/` (`h.cjs` koşum aracı, `old/` = `eb7fdc0` relay öncesi, `new/` = HEAD, `nogear/ nonet/ noanch/` = yalnız scratch kopyada tek değişiklik kapatılmış varyantlar).
Etiketler: **D** doğrulandı/ölçtüm, **T** tahmin/çıkarım, **K** dış kaynak.

## 1. Şu anki durum
- **D** Tek `index.html` (4133 satır, ~297 KB), Three.js r170 import map + SRI (s.1001), ARENA-KIT bloğu s.~640-1000. Konsol/sayfa hatası yok (masaüstü 1280×720 ve telefon 390×844, swiftshader).
- **D** İçerik: 6 iskele, 8 sefer tablosu (s.1384-1393), sonsuz mod (`endlessShift` s.1398), günlük meydan okuma, Sis Seferi imza mekaniği (s.2537+), rozetler. Puan: yolcu×10 + dakiklik + konfor×3 + yanaşma primi (s.2645).
- **D** Kayıt: `arena.vapur.save = {best, run}`, `arena.vapur.settings` (s.1409-1432); relay commit'leri kayıt biçimine dokunmadı → eski kayıt uyumu korunuyor.
- **D** Son birleşen relay (`732d31b`, gemini flash-lite, "helm instruments / deck life / low-power + fishing boats") oyuna 7 yeni davranış ekledi: vites bekleme (s.2256-2265), "Halatları At" için Boşluk şartı (s.2527-2532), demirli balıkçı + görünmez ağlar (s.2310-2324, 2396-2398), simit/çaycı olayları (s.2603-2635), düşük güç 30 fps kilidi (s.1255-1262, 4040-4046), RPM göstergeleri (s.1099-1103, 3459-3470), sonuç ekranına "Yanaşma puanı" (s.3797).
- **D** Bu relay **bot kampanyasını bozdu**: aynı koşumda (`?auto&cal`, `vapurSim` 1/30 s adım) eski sürüm sefer 1 = 3★ 1557, sefer 3 = 3★ 2938; HEAD sefer 1 = **0★ 103 (gövde %100, batık)**, sefer 3 = **0★ 93**.
- **D** Masaüstü HUD: 27-29 draw call, ~440k üçgen (swiftshader'da fps anlamsız; README'deki UHD 620 ölçümü relay öncesine ait).
- **T** README ve `project-meta.json` "60 fps, bot her seferde 3★" diyor; relay sonrası bu iddia doğru değil.

## 2. Güçlü yanlar (korunmalı)
- **D** Sis Seferi: yankı gecikmesi fiziksel (2d/343), stereo pan, kör radar, adil trafik düdükleri — türde özgün, ses tabanlı navigasyon. Dokunma.
- **D** Kural tutarlı yanaşma geri bildirimi: mesafe/hız/açı paneli + ipucu metinleri (s.2533) ve kalite bazlı yanaşma primi (s.2186).
- **D** Prosedürel, varlıksız dünya (ses dahil Web Audio sentezi); `?auto`, `?debug`, `?sim`, `window.vapurSim` ile hızlı, render'sız QA — araştırmayı da bu sayede yapabildim.
- **D** Telefon düzeni: solda dümen, sağda çift kollu gaz, ayrı korna/kamera; dikeyde oynanabilir (ekran görüntüsü `phoneplay-shift1.png`).
- **D** Günlük meydan okuma deterministik (`Arena.daily().rng`), seri ve paylaş akışı çalışıyor (arena-kit commit kanıtı).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Vites kilidi — ileri→tornistan geçişi kalıcı olarak takılıyor (KRİTİK, D).** s.2258/2263: işaret farklı ve iki değer de >0.1 ise `gearPause=0.5`; süre bitince aynı koşul yine doğru → sonsuz döngü, `P.thrP` hiç değişmez.
   Adım: sefer 1, ileri 1 → 0.5 → tornistan -1 tut. Ölçüm (`gear`, 30 adım/sn): eski sürümde 1 sn'de `thrP` -0.2, 3 sn'de -1, hız 1.55 → -1.2 m/s. **HEAD'de 12 sn boyunca `thrP = +0.5`, hız 1.92 → 4.14 m/s artmaya devam ediyor** (telgraf "TORNİSTAN" gösterirken gemi hızlanıyor). Klavyeyle (S basılı) de olur: girdi 0'dan ~0.22 sn'de geçer, `thrP` o anda ~0.15 kalır ve kilitlenir (T, hesaba dayalı). Dokunmatik kolda tek sürüklemede geçiş → kesin kilit.
   Bot da etkileniyor: `nogear` varyantında (yalnız kilit kapalı) sefer 1 batmıyor (gövde %73, 3★); HEAD ve `nonet` varyantında t=289 sn'de **gövde %100, batış** → batışın nedeni kilit (D).
2. **Görünmez ağlar konforu yok ediyor (D).** s.2310-2324: her yarım balıkçı demirli, ağı 25 m, *çizilmiyor*; her 1/60 sn'lik adımda, her gövde dairesi × ağ noktası temasında konfor -0.5 (≈ -30/sn/nokta). Bot sefer 1'de 16 kez "Ağlara dikkat", konfor 4; ağ kapalı (`nonet`/eski) konfor 51. Oyuncu görmediği bir şeyle cezalandırılıyor. Ağ noktaları kanal içinde rastgele (s.2397) → rota üstünde olabilir.
3. **Yanaşma Boşluk/korna basılı tutmayı istiyor, belgesiz (D).** s.2527: `DOCK.ok && (keys.Space || input.horn || FLAG.auto)`. Başlıktaki nasıl oynanır metni hâlâ "halatlar atılınca…" (otomatik) diyor; tek ipucu bir kez çıkan toast. Siste Boşluk = sis düdüğü + yankı turu (yan etki). Dokunmatikte korna düğmesini basılı tutmak gerekiyor. Ayrıca `dockAt` artık `SIM.ropes=false` (s.2179) ve onu yalnız bot `true` yapıyor (s.3896) → **insan oyuncuda halatlar hiç çizilmiyor ve "Halat gerginliği" hiç görünmüyor**, ama "Halatlar atıldı!" toast'u (s.2191) yine çıkıyor (D kod).
4. **i18n kırığı (D).** `sDockScore, ropeTension, throwLines, netWarning` yalnız TR'de (s.1291); `t()` TR'ye düşüyor (s.1370) → İngilizce oyuncu "Ağlara dikkat", "Halatları At (Boşluk/Buton)", "Yanaşma puanı" görüyor (toast sayımında EN oturumda "Ağlara dikkat" ×16). Simit/çay metinleri STR yerine satır içi `LANG === 'tr'` (s.2609-2631). RPM etiketi EN'de "P/S" ama TR'de de "P/S" ve "TORN" (kesik "TORNİSTAN").
5. **Yanlış tuş etiketi (D).** Kollar `İ A/T`, `S A/T` (s.1099-1100); gerçek tuşlar T/G (iskele) ve Y/H (sancak) (s.3614), A/D dümen. Relay önceki doğru etiketi bozdu; EN arayüzde de "İ".
6. **Toast yağmuru (D).** Bot sefer 1 (nogear): simit 28, çaycı 13+11, ağ 16 toast ≈ 68 güverte/ağ toast'u, gerçek bilgi toast'u ~20. Telefonda toast "Sıradaki iskele" kartını örtüyor (`phoneplay-shift1.png`). Çay dökülme eşiği `|r|>0.08` rad/s (s.2622) olağan dönüşte tetiklenir (T). `SIM_EXT` sefer başında sıfırlanmıyor (s.2101; yalnız 15 kullanım, hiçbiri reset) (D).
7. **Düşük güç modu (D/T).** Pil <%20 ve şarjda değilse veya `deviceMemory<=2` ise 30 fps'e kilitleniyor, geri dönmüyor, arayüzde göstergesi/ayarı yok; `arena.vapur.lowPowerOverride` anahtarını yazan UI yok (yalnız okuma). `lsGet` her rAF'ta `JSON.parse(localStorage)` (s.4040) (D). `?low` artık 30 fps de demek (README ile çelişki). Arena.perf kendi rAF'ını ölçtüğü için çözünürlüğü yanlışlıkla düşürmüyor (D, s.962-977).
8. **Küçük/taşan HUD metni (D).** `rpmReadout` 8 px ve hız kadranından taşıyor (masaüstü `play-shift1.png`), `tPVal/tSVal` 7 px; telefonda okunamaz. "NEXT PIER" başlığı ile "BİLET / VOUCHER" süsü üst üste (masaüstü görüntü). `updateHUD` her karede 3× `getElementById` (s.3463-3466).
9. **Fırtına şimşeği tam sahne parlama (D kod, s.2637/3176-3178):** güneş +3, hemi +1.5 ani sıçrama; arena `reducedMotion` ayarı bunu kapatmıyor. **K** Xbox AG 118: tetikleyiciyi kaldırmak uyarıdan iyidir; kaldırılamıyorsa yoğunluğu/kontrastı azalt.
10. **İlk deneyim ağır (D/T).** Başlıkta 4 satırlık tuş listesi; ilk sefer tam kurallarla başlıyor, yönlendirmeli ilk yanaşma yok, Arena.hint kullanılmıyor (s.655 tanımlı, oyun çağırmıyor). **K** Poki: ilk oturumda oynanışa hızlı ulaştır.
11. **Belgeler güncel değil (D):** README/meta relay özelliklerinden ve bot düşüşünden habersiz; meta "60 fps, 0 hata, 3★" iddiası relay öncesi ölçüm.

## 4. EKLENMELİ — yüksek değer
(Hepsi kısıtlarla uyumlu: tek dosya, ağ çağrısı yok, kayıt biçimi değişmiyor, ARENA-KIT/importmap'e dokunulmuyor.)

**4.1 Relay davranışlarının onarımı/geri alınması (önce bu).** Ne: vites beklemesini tek seferlik zamanlayıcıya çevir (bekleme bitince ramp başlasın, `P.thrP` 0'dan geçsin); ağları ya kaldır ya görünür yap (şamandıra dizisi = instanced küçük küre, mevcut `fishH` çizimine ek 1 draw call) ve cezayı olay başına tek seferlik yap (ör. -3, 4 sn bekleme); "halat at"ı ya geri otomatik yap ya da ayrı tuş + başlık metni + kalıcı yanaşma paneli ipucu; insan için `SIM.ropes=true` (bot satırı s.3896 gereksizleşir); eksik EN anahtarları; doğru tuş etiketleri. Neden: kontrol bozuk, bot kırmızı, EN oyuncu TR görüyor. Maliyet **S**. Risk düşük; doğrulama: `?auto&cal` kampanya eski sürümle aynı/üstü yıldız, `gear` testi. Kanıt: §3.1-3.5.

**4.2 Bot regresyon kapısı (`tools/` altında, oyun dosyasına dokunmadan).** Ne: `tools/smoke.mjs` yalnız "yükleniyor ve hata yok" diyor; bir `tools/bot.mjs` ekle: `?auto&cal` + `vapurSim` ile 8 seferi koş, `vapur.log`'u eşikle karşılaştır (ör. her sefer ≥2★, batış yok) ve bir girdi testi (ileri→tornistan 3 sn içinde `thrP<0`). Neden: bu relay "verified by verify_merge.py" ile birleşti ama oyunu bozdu — smoke bunu yakalamıyor. Maliyet **S-M**. Risk: CI süresi (~2-3 dk, render yok). Kanıt: §1, §3.1.

**4.3 Rehberli ilk yanaşma (sefer 1'e katman).** Ne: sefer 1'in ilk iki ayağında hayalet yanaşma çizgisi (iskele `P.tx/tz` boyunca 3-4 şeffaf ok, mevcut `berth` malzemesiyle) + adım ipuçları `Arena.hint` ile (kalk → yavaşla → paralel → dur); başlık metnini tek satıra indir, tuş tablosu "Nasıl oynanır" açılır panelinde. Neden: tür oyunlarında adım adım eğitim ve görsel yaklaşma kılavuzu standart (K: Boat Simulator itch, Boat Master "berthing mode"); Poki ilk oturum vurgusu (K). Maliyet **M**. Risk: bot etkilenmez (yalnız görsel/toast); mobilde toast çakışması → ipuçlarını yanaşma paneline yaz.

**4.4 Güverte olaylarını sadeleştir ve ekonomiye bağla.** Ne: simit/çay toast'larını kaldır, yerine HUD konfor çubuğunda küçük ikon + kısa yüzer metin; olay sıklığını sefer başına 1-2'ye indir, `SIM_EXT`'i `startShiftSim`'de sıfırla; çay eşiğini dümen açısına (`|rud|>0.6` ve hız>4) bağla ve olay başlarken 3 sn önce uyar. Neden: şu an ~68 toast/sefer, oyuncuya karar vermeyen gürültü. Maliyet **S**. Risk düşük (puanı az etkiler; hedefleri `?cal` ile yeniden kalibre et).

**4.5 Şimşek yumuşatma + reduced-motion bağlantısı.** Ne: `lightning` çarpanını 3→~1 ve süreyi uzat; `document.documentElement.hasAttribute('data-arena-reduced-motion')` ise sahne flaşı yok, yalnız ses ve gökyüzünde uzak parıltı. Aynı bayrakla yanaşma kamerası orbit/FOV genişlemesini kapat. Maliyet **S**. Risk yok. Kaynak: K Xbox AG 118, gameaccessibilityguidelines.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Düşük güç modunu görünür ayar yap (S):** Ayarlar'a "Pil tasarrufu: Otomatik/Açık/Kapalı" (mevcut `lowPowerOverride` anahtarı), değeri bir kez oku (her karede değil); pil şarja takılınca otomatiği geri al. Koşul: 4.1 sonrası.
- **Tek kol/ikiz makine kip seçimi (S-M):** Varsayılan "kolay" kipte tek telgraf (W/S), ikiz makine ileri sefer/ayarlarda. K: Hafenskipper incelemesinde yakın kollar telefonda zor; Boat Master iki kip sunuyor. Telefonda ikiz kol zaten var; kip yalnız yükü azaltır.
- **Sefer sonu tekrar şeridi (M):** minimap üzerine rotanın izi + çarpışma/sert yanaşma noktaları (veri zaten SIM'de; kayda yazılmaz). Neden: oyuncu neden yıldız kaybettiğini görür. Risk: bellek düşük (iz noktası/sn).
- **Hafta içi "hat ustalığı" kademesi (M):** 3★ seferlerde ek koşul rozetleri (ör. hiç sert yanaşma yok) → `Arena.award`; kayıt biçimi aynı kalır (`best` dokunulmaz). Koşul: rozet sayısı enflasyonu olmasın.
- **Yolcu sesi/iskele anonsu (S):** sentez çan + kısa melodik anons yanaşmada; mevcut AUD yapısına ek. Koşul: ses seviyesi ayarına bağlı.

## 6. EKLENMEMELİ
- **Görünmez ceza mekaniği** (mevcut ağlar gibi): oyuncu göremediği/duyamadığı şey için ceza adil değil; Sis Seferi'nin "adil trafik" ilkesiyle çelişir.
- **Sabit 30 fps kilidini otomatik ve sessiz tutmak**: 8 GB UHD makinede gereksiz yere akıcılığı düşürür; kullanıcı bilmeden değişen davranış.
- **Gerçekçi sim derinliği (rüzgâr baş/kıç iticisi, ayrı vites kutusu, halat gerdirme fiziği):** bu relay'in gösterdiği gibi kontrolü kırar, mobilde düğme kalabalığı yaratır, bot rotasını bozar.
- **Çevrimiçi skor tablosu / hesap / bulut kaydı / reklam SDK'sı:** kısıtı aşar (sunucu, kullanıcı verisi, harici ağ).
- **Gerçek vapur/hat markalarının logo veya renk kopyası, gerçek bir oyunun haritası/müziği:** telif ve brief kuralı. (Mevcut "Şehir Hatları 1960" bileti stil olarak kalabilir; resmi logo eklenmemeli.)
- **Daha fazla toast tabanlı "atmosfer" olayı:** telefonda kartları örtüyor (D).
- **Yeni ağır görsel katman (gerçek zamanlı yansıma, post-process bloom):** ~440k üçgen ile UHD bütçesi zaten dolu (T, README ölçümü).

## 7. Düzeltilmeli
- Vites kilidi (s.2256-2265) — kritik.
- Ağ cezası/görünmezliği (s.2310-2324), demirli teknelerin fairway dışına yerleşmesi (s.2397, `fairway` grafiğine mesafe şartı).
- `SIM.ropes` insan oyuncu için (s.2179, 2527-2532); "Halatlar atıldı!" toast'u ile tutarlılık.
- EN anahtarları: `sDockScore, ropeTension, throwLines, netWarning` + simit/çay metinleri STR'ye; "TORN" → "TORNİSTAN"/kısaltma "TOR"; TR'de "İ/S".
- Kol etiketleri `T/G`, `Y/H` (s.1099-1100), EN'de "P/S".
- `rpmReadout` 8 px ve kadran taşması, `tPVal/tSVal` 7 px → min 11 px ya da kaldır (bilgi zaten kol konumunda); `getElementById` önbelleğe.
- "NEXT PIER" / "BİLET / VOUCHER" üst üste binme (CSS s.266 `content`).
- Her rAF `localStorage` okuma (s.4040).
- `SIM_EXT` reset; toast sayısı.
- Şimşek flaşı + reduced-motion.
- README/meta: yeni mekaniklerin belgesi ve yeniden ölçülmüş bot/fps sonuçları (iddialar ancak 4.1+4.2'den sonra).

## 8. Önerilen ilk 3 iş
1. **Relay regresyonlarını onar (4.1 + §7 ilk 5 madde).** Gerekçe: oyuncu ileri→tornistan yapamıyor (gemi telgrafın tersine hızlanıyor), görünmez ağlar konforu sıfırlıyor, bot 1. ve 3. seferde 0★/batış. Bunlar düzelmeden yeni özellik eklemek anlamsız. Kabul: `gear` testinde 3 sn içinde `thrP<0`; `?auto&cal` kampanyada eski sürümün yıldızları (1-4. sefer 3★) geri; EN arayüzde TR metin yok.
2. **Bot regresyon kapısı (4.2).** Gerekçe: bu kırılma "verified" etiketiyle main'e girdi; kapı olmadan bir sonraki relay aynı şeyi yapar. Mevcut `window.vapurSim` ile render'sız, ucuz.
3. **Rehberli ilk yanaşma + toast sadeleştirme (4.3 + 4.4).** Gerekçe: oyunun çekirdek becerisi yanaşma; ilk 30 sn tuş duvarı ve toast yağmuru telefonda en zayıf deneyim. Görsel/ipucu katmanı olduğu için kayıt ve bot riski düşük.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek UHD 620 / telefonda fps ölçmedim (swiftshader fps anlamsız: masaüstü ~50, telefon ~23). Relay sonrası README'deki 60 fps iddiası doğrulanmadı.
- Bot ölçümlerim `vapurSim` 1/30 s adımla; gerçek zamanlı 1/60 adımda sonuçlar farklı olabilir (eski sürüm bu koşumda da 5. seferde 0★ — README "5 ve 8'de tekrar" ile uyumlu). Karşılaştırma aynı koşumda olduğundan eski/yeni farkı geçerli; mutlak değerler değil.
- `noanch` varyantı (demirli tekne yok) 60000 adımda sonuç vermedi — neden incelenmedi (vites kilidi yüzünden takılmış olabilir, T).
- Klavye ile kilit senaryosu hesapla çıkarıldı (T); doğrudan girdi atamasıyla D. Gerçek dokunmatik sürükleme denenmedi.
- Kaydın relay öncesi sürümden yüklenmesini ayrıca denemedim (kod kayıt biçimini değiştirmiyor, T).
- Arena metin büyütme ayarının oyun HUD'una (px tabanlı) etkisi denenmedi.
- Oyuncunun "halat at" adımını isteyip istemediği bir tasarım kararı — kullanıcıya sorulmalı (geri al vs. belgele).

## Kaynaklar
- Xbox Accessibility Guideline 118 (Photosensitivity): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/118
- Game Accessibility Guidelines — avoid flickering images: https://gameaccessibilityguidelines.com/avoid-flickering-images-and-repetitive-patterns/
- Poki for Developers — easy access / ilk oturum: https://developers.poki.com/guide/easy-access
- Poki — What makes a high quality browser game (2026): https://poki.com/blog/what-makes-high-quality-browser-game
- Poki — State of Web Gaming 2026: https://poki.com/blog/state-of-web-gaming-report-2026
- Hafenskipper (App Store; ikiz kol yakınlığı yorumları): https://apps.apple.com/us/app/hafenskipper/id1022317291
- Boat Master (App Store; berthing ve driving kipleri): https://apps.apple.com/us/app/boat-master/id1349495816
- Boat Simulator (itch.io; adım adım eğitim → yanaşma görevi): https://jakesobo.itch.io/boat-simulator
- Unity — Video game accessibility basics: https://unity.com/blog/video-game-accessibility-basics

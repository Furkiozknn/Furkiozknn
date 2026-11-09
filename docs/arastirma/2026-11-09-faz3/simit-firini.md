# Simit Fırını — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak. Satır numaraları `index.html` (HEAD 9ecd2dd).
Ölçüm araçları (repo dışında): `_simit-firini/sim.js` (SIM+BOT bloklarını index.html'den kesip Node'da 30 tohumla koşar), `_simit-firini/pw.cjs` (headless Chromium, swiftshader, `?low`). Makine o sırada yüklüydü (load avg ~79), bu yüzden fps değerleri **performans kanıtı sayılmaz**.

## 1. Şu anki durum
- **D** Tek dosya (3811 satır, 280 KB). Saf sim + bot `DAY_LEN…/*BOT-END*/` (1191-1838) DOM'dan bağımsız; Node'da hatasız koşuyor (30 tohum, `__errors` = 0).
- **D** Döngü: plan (5 sekme: üretim/fiyat, tedarik, sokak, ekip, gelişim) → gün (255 sim-sn, 05:00-22:00, 1/2/4x) → gece masrafları → özet. Kayıt `{v:1,S}` yalnız gün sınırında (`saveGame` 3557; çağrılar 3611, 3630, 3631). Göç fonksiyonu `migrateState` (1692) mayalanma alanlarını ekliyor.
- **D** Hedef: 20. günün sonunda 5000 ₺ **ve** 4 yıldız (1191, 1678). Bot ölçümü (30 tohum): **19/30 kazanıyor** (16-20. gün), kaybedenler hep `timeup`, 24-32 bin ₺ kasayla ama itibar 3.2-3.99.
- **D** Kasa hedefi 11-14. günde doluyor (30/30 tohumda); kazanıp kaybetmeyi **yalnız itibar** belirliyor. Gün başına itibar artışı en fazla +0,35 (1665) ve memnuniyet (`sat-0.66`) talebi artırıp kaçan müşteriyi de artırdığı için kendi kendini frenliyor (örnek tohumda sat 0,65-0,92 arası salınıyor).
- **D** İmza mekaniği (altın pişme + mayalanma penceresi) etkili: bot altın çekmeyince kazanma 19/30 → **8/30**.
- **D** `careless` bot: 30/30 `timeup`, ~2800 ₺, 0,9-1,7 yıldız; **hiç iflas etmiyor**. README'deki "careless play bankrupt around day 7" iddiası tutmuyor.
- **D** Gerçek sayfada `?auto&seed=11&low`: 20. günde kazandı (27 891 ₺, 4,12 yıldız), 0 JS hatası, yalnız AudioContext autoplay uyarıları (beklenen).
- **D** Masaüstü (1024×640) ve telefon (390×844, dokunmatik) açılışında 0 konsol hatası; 28 draw call, 51,4k üçgen.
- **D** i18n: her string `[tr,en]` (1171-1182, 3048-3145); dil `?lang` → ayar → tarayıcı. Ses tamamen Web Audio sentezi (2936-3044).
- **D** Son relay commit'leri (687d6e1 dokun-ata, 6145f44 uçan para + fırın alarmı) eklendi; ikincisinin alarm kısmı çalışmıyor (bkz. §3).

## 2. Güçlü yanlar (korunmalı)
- Saf, deterministik sim (mulberry32, `S.rng` kayıtta) + oyuncuyla aynı aksiyonları çağıran bot (1704): denge değişikliklerini 30 tohumda saniyeler içinde ölçmeyi sağlıyor. **Bu ayrım bozulmamalı.**
- Kültürel kimlik: simitçi, iskele/vapur, çay ocağı, pekmez-susam zinciri, klarnet+darbuka müziği; hava ve saate göre talep eğrileri (1220-1233) okunur ve mantıklı.
- Altın pişme gerçek bir beceri anı: bot verisi onun kazanmaya büyük katkısını gösteriyor (§1).
- Gün sonu özeti "fiş" (3512) + gerekçeli ipuçları (tip_miss/burn/stale/over/under) iyi bir öğrenme döngüsü.
- Özet tutarlılık kontrolü (1666-1667): gelir-gider satırları kasa değişimiyle eşleşmezse `__errors`'a yazıyor.
- Telefon plan modalı (390 px) düzgün: tablo kart düzenine dönüyor (639-649), yatay taşma yok (**D**: scrollWidth 390 = innerWidth).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Telefon dikey HUD'u bozuk (D, ekran görüntüsü `5-phone-day.png`).** 390 px'de hız seçici yıldızların ve kasanın üstüne biniyor, hava çipi müzik ikonunun altında kalıyor, gün/saat çipi görünmüyor, sol kenar kesiliyor. Neden: "RADICAL UI/UX REBIRTH" relay'i (3bcebe6) `#hud` için `flex-wrap: nowrap` (230-234) koymuş, 680 px altı kural (607-614) yalnız boyut küçültüyor. `docs/phone.png` eski 3 satırlı HUD'u gösteriyor; yani bu bir gerileme. Ayrıca 1024 px masaüstünde de hava çipi hız seçicinin altında kalıyor (`3-day.png`).
2. **Bitişte kasa hedefi anlamsız, geç oyunda paranın gidecek yeri yok (D).** Kasa 12. günde ~5000'i geçiyor, kaybeden koşular bile 25-32 bin ₺ ile bitiyor. Bütün yükseltmeler + tarifler ~8 bin ₺. Son 6-8 gün yalnız itibar bekleme oyunu. Tür genelinde bilinen bir sorun (K: geç oyunda para birikmesi oyuncuyu sıkıyor; çözüm para yutan unsurlar ve itibar kademeleri).
3. **İtibar neden değişti, oyuncu göremiyor (D).** Özet yalnız `dRep` gösteriyor (3524). Formül 1660-1664'te 7 bileşenli (memnuniyet, yanık, sözleşme, fiyat, mayalanma, altın, az müşteri cezası). Kazanmayı belirleyen tek değişken bu, ama oyuncu hangi bileşenin etkili olduğunu göremiyor.
4. **Etiketler üst üste biniyor (D).** Telefonda görünen 10 etiketten 9 çift kesişiyor; "Yoğurma" Fırın/Şekil'in altında tamamen kayboluyor, "Pekmez" Susam'ın altında kalıyor. Masaüstünde de aynı küme var (`3-day.png`). Dokunmatikte yanlış istasyona dokunma riski var (**T**).
5. **Fırın yanık alarmı ölü kod (D).** `labelText` (2751) ve `updateLabels` (2779) `s.wait > 30` bekliyor, ama ekmek `wait > DATA.grace` (= 6, 1197/1554) olunca yanıp slottan çıkıyor; alarm hiç tetiklenemez. Ayrıca 2751-2752'de hesaplanan fırın `pip`'i 2755'teki `else` tarafından her zaman eziliyor (eski `wait > 3` → kırmızı uyarısı da relay öncesinden beri ölü). 2771'de `&& false`, 2810'da çift `rotation.y` ataması var.
6. **Uçan para efekti (6145f44) yanlış ve sınırsız (D).** Gösterilen tutar `d.q * S.sell[d.p]` (3654), gerçek tahsilat ise kaliteyle çarpılıyor (`rackQ/trayQ`, 1634). Altın ya da çökük üründe yanlış sayı gösteriyor. Her satışta bir DOM düğümü yaratılıyor (kısıtlama yok, 4x'te saniyede çok sayıda; **T** zayıf GPU'da layout maliyeti). `prefers-reduced-motion` ve arena-kit azaltılmış hareketi dikkate alınmıyor (313'teki kural `.float-currency`'yi kapsamıyor, **T**: kuralın içeriği kontrol edilmedi).
7. **Altın çekme zamanlaması hızla daralıyor (D, kod).** Pencere 0,4 sn öncesi + 1,4 sn sonrası sim zamanı (1206). 4x'te gerçek zamanda ~0,45 sn. Duraklatılmışken çekilemiyor (1422). Kazanmaya katkısı büyük olduğu için motor güçlüğü olan oyuncu dezavantajlı. K: "precise timing essential olmasın; alternatif sun" kılavuzu.
8. **İlk deneyim yoğun (D/T).** Oyna'ya basınca doğrudan 5 sekmeli plan modalı açılıyor (`2-plan.png`); başlık ekranındaki 5 maddelik metin dışında rehber yok. Arena-kit'in `Arena.hint` özelliği (718) oyunda hiç kullanılmıyor (**D**: grep). CrazyGames'in yönergesi yeni oyuncuyu hemen oynanışa sokmayı istiyor (K).
9. **Dokunma hedefleri küçük (D).** Telefonda HUD ikon düğmeleri 36×36, hız düğmeleri 44×32 (`pointer:coarse` kuralı 211-214 `#hud .btn.icon` 680 px kuralıyla eziliyor).
10. **Belge uyuşmazlığı (D).** README "careless bankrupt ~day 7" yanlış (§1); "9/12 seed" yerine ölçüm 19/30 (%63).

## 4. EKLENMELİ — yüksek değer
**4.1 Telefon HUD'unu düzelt (iki satır + kompakt çipler)**
- Ne: ≤680 px'de HUD'u 2 satıra böl (üst: logo, gün, saat, kasa; alt: yıldız, hava, hız, araçlar) ya da araçları (müzik/efekt/dil) duraklat menüsüne taşı.
- Neden: oyunun temel bilgisi (saat, kasa) telefonda okunmuyor. Kısıt "telefon desteklenmeli".
- Nasıl: `#hud{flex-wrap:wrap}` + `.stats{order;flex-basis:100%}` 680 px medya sorgusunda; `--hudH` zaten `resizeHudVar` ile ölçülüyor (3755), panel konumları uyum sağlar. Seg/ikon düğmelerine coarse'ta 44 px.
- Maliyet S · Risk düşük (yalnız CSS) · Kanıt `5-phone-day.png` vs `docs/phone.png`.

**4.2 İtibar dökümü (özet + HUD hedef çubuğu)**
- Ne: `endDay` itibar bileşenlerini `S.last.repParts` olarak kaydetsin; özet fişinde "Memnuniyet +0,12 · Yanık −0,02 · Sözleşme +0,10 · Mayalanma −0,01…" satırları; HUD'da iki hedef ilerlemesi (₺ x/5000, ★ x/4).
- Neden: kazanmayı belirleyen tek değişken itibar (§1) ama oyuncu nedenini göremiyor. Özet ipuçları zaten var, bu onları sayıya bağlar.
- Nasıl: 1660-1665'teki terimleri ayrı değişkenlere al (toplam değişmez → bot ve denge birebir aynı), `S.last`'a ek alan. Eski kayıtta alan yoksa satırı gizle.
- Maliyet S · Risk çok düşük (sonuç aynı; Node harness'iyle 30 tohum karşılaştırılabilir) · Kanıt §3.3.

**4.3 Geç oyun para → itibar dönüşümü: "Askıda simit" ve mahalle katkıları**
- Ne: plan modalında yeni seçenek: günün simitlerinin bir kısmını "askıya" bırakmak (ürün + küçük ₺ maliyeti → itibar +), ileri günlerde pahalı tek seferlik "mahalle" yatırımları (çeşme onarımı, okul kantinine bağış; azalan getiriyle).
- Neden: §3.2'deki birikimi anlamlı kılar, itibar kapısına oyuncu kontrolünde ikinci bir yol açar. Kültürel kök: askıda ekmek geleneği (K). Tür ilkesi: ilerlemeyle ölçeklenen para yutan unsurlar (K). Gerçek bir oyunu kopyalamıyor.
- Nasıl: `S.charity={pct:0, done:{}}` (migrateState'te varsayılan 0 → eski kayıt ve davranış aynı); `endDay`'de `dr += min(0.08, k*verilen/tot)`, günlük üst sınır 0,35 kalır. Bot ilk sürümde kullanmasın (kazanma oranı değişmez), sonra ayrı ölçümle `botPlan`'a eklenebilir.
- Maliyet M · Risk orta: denge (itibar kapısını çok kolaylaştırabilir → üst sınır şart), kayıt (yeni alan, migrate ile çözülür) · Kanıt §1 harness çıktısı.

**4.4 Etiket ayrıştırma (çakışma önleme)**
- Ne: `updateLabels`'te ekran uzayında basit itme: etiketleri y'ye göre sırala, çakışanı aşağı/yukarı kaydır; uzakta (cam.dist büyük) istasyon etiketlerini tek "Fırın içi" etiketinde topla.
- Neden: telefonda 9 çakışma, bir istasyon görünmüyor (§3.4).
- Nasıl: 12 etiket için O(n²) dikdörtgen kontrolü, yalnız `refreshText` turunda (0,25 sn'de bir) yeni ofset hesapla, ara karelerde ofseti koru. `getBoundingClientRect` yerine bilinen etiket genişliği (`offsetWidth` önbelleği).
- Maliyet M · Risk düşük-orta (layout thrash: önbellekle önlenir) · Kanıt `5-phone-day.png`, ölçüm 9 çift.

**4.5 İlk gün rehberi (`Arena.hint` ile, 4-5 bağlamsal ipucu)**
- Ne: ilk oyunda plan modalında "önce Dükkânı aç" vurgusu; gün içinde sırayla "işçiyi sürükle/dokun-ata", "ilk altın an: G / Altın çek", "simitçiyi iskeleye gönder", "raflar dolunca…". Her biri bir kez.
- Neden: §3.8; arena-kit özelliği hazır ama kullanılmıyor. Portallar ilk oturumda hızlı oynanış istiyor (K).
- Nasıl: `listeners`'a olay bazlı (daystart, ilk `gold` bandı, ilk `full`) `Arena.hint(id, t(...))` çağrıları; `FLAGS.auto`'da kapalı. Yeni i18n anahtarları.
- Maliyet S · Risk düşük (bot etkilenmez; ARENA-KIT bloğu düzenlenmez, yalnız API çağrılır).

## 5. EKLENEBİLİR — orta değer / koşullu
- **Altın çekme erişilebilirlik seçeneği** (Ayarlar: "Kolay altın": pencere gerçek zamanda en az ~1,2 sn olacak şekilde hıza göre genişlet, ya da 4x'te altın an başlayınca hızı geçici 1x'e indir). Değer: §3.7. M. Risk: denge (yalnız ayar açıkken; varsayılan kapalı → bot aynı). Eşik ölçümle seçilmeli.
- **Bitiş sonrası sonsuz mod hedefleri**: 21+. günde haftalık "mahalle görevleri" (ör. "3 gün üst üste %90 memnuniyet") → rozet. 4.3 olmadan anlamı azalır. M.
- **Gün içi otomatik kayıt** (her saat başı `saveGame`): bugün sekme kapanırsa gün baştan oynanıyor (yalnız plan anında kayıt). Değer düşük-orta (gün ~4 dk @1x). Dikkat: `resumeRun` gün ortasını `plan`'a çeviriyor (3621); gün ortası kayıt için sim durumunun (S.t, slotlar) doğru geri yüklenmesi gerekir. M, kayıt riski var.
- **Hava/olay çeşitliliği**: mevcut `mods` (festival, vapur grevi, zam) 3 tane; 2-3 yeni olay (ör. maç günü pier talebi, okul tatili) yalnız `DATA` satırıyla eklenir. S. Bot `spotLambda` üzerinden otomatik uyum sağlar; 30 tohumla ölçülmeli.
- **README düzeltmesi**: careless/kazanma oranı ölçümünü güncelle (§3.10). S.

## 6. EKLENMEMELİ
- **Online liderlik tablosu / hesap / bulut kayıt**: sunucu ve kullanıcı verisi kısıtını aşar. Günlük meydan okuma + yerel seri zaten var.
- **Kasa hedefini yükseltmek ya da itibar formülünü sertleştirmek**: eski kayıtların sonucu değişir, bot kazanma oranı düşer. Önce 4.2/4.3 ile oyuncuya araç ver, denge sonra.
- **Daha fazla 3B detay / gölge / partikül**: 28 draw call, 51k üçgen ve uçan para DOM'u zaten var; Intel UHD hedefinde ölçüm yapılmadan yük ekleme. Görsel bütçe yerine okunabilirliğe (etiketler) harca.
- **Gerçek zamanlı müşteri sırası yönetimi / tıkla-sat mikro yönetimi**: oyun planlama tycoon'u; her satışı tıklatmak 4x'te ve telefonda oynanmaz, botu da bozar.
- **Reklam/IAP/ödüllü video**: ücretli servis ve kullanıcı verisi kısıtı.
- **Uçan para efektini çoğaltmak** (her olaya sayı): DOM churn ve görsel gürültü; tersine sınırlandırılmalı (§7).

## 7. Düzeltilmeli
- [D] Fırın alarmı: eşiği `DATA.grace`'e bağla (ör. `wait > DATA.grace*0.5`), 2751-2755 pip mantığını tek dala indir, 2771 `&& false` ve 2810 çift atamayı temizle. S.
- [D] Uçan para: tutarı gerçek fiyatla (`S.sell[p]*kalite`) hesapla (olay verisine `price` ekle, 1634'teki `emit`'e), spot başına ~250 ms birleştir, `RM`'de kapat, ekranda en fazla ~12 düğüm. S.
- [D] Telefon dokunma hedefleri: coarse'ta HUD ikonları 44 px (680 px kuralı eziyor). S.
- [D] 1024 px masaüstünde HUD çakışması (hava çipi). 4.1 ile birlikte. S.
- [T] Altın an yalnız renk+zil ile başlıyor; etiket metni "Altın an!" var (2754), ama ekran okuyucuya duyurulmuyor. `Arena` `announce` dışa açıksa ilk altın anında kullan (yoksa aria-live bölgesi). S.
- [D] README: careless iddiası ve kazanma oranı. S.
- [T] Önyüklemede Google Fonts ve GoatCounter dış çağrıları var (19-21, 658). Brief'in "harici ağ çağrısı yok (CDN modülleri hariç)" kısıtıyla çelişebilir; ekosistem kararı mı, kontrol edilmeli (§9).

## 8. Önerilen ilk 3 iş
1. **Telefon HUD'u + dokunma hedefleri + 1024 px çakışması (4.1, §7)**: görünür bir gerileme; yalnız CSS, risk en düşük, telefon kısıtını doğrudan karşılıyor. Doğrulama: 390×844 ve 1024×640 ekran görüntüsü + `smoke.mjs`.
2. **Ölü/yanlış relay kodunun düzeltilmesi (fırın alarmı, uçan para tutarı ve sınırı)**: bugün eklenen iki özellik ya hiç çalışmıyor ya yanlış sayı gösteriyor. S maliyet, sim'e dokunmuyor, bot etkilenmiyor.
3. **İtibar dökümü + hedef ilerlemesi (4.2)**: kazanmayı belirleyen değişkeni görünür kılıyor, hesap sonucu aynı kaldığı için denge/bot/kayıt riski yok. 4.3'ün (askıda simit) zeminini hazırlar; 4.3 bundan sonra Node harness'iyle ölçülerek gelmeli.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek Intel UHD 620'de fps ölçülmedi. Swiftshader + 79 load average altında 11-15 fps görüldü; bu değer anlamsız.
- Uçan para efektinin performans maliyeti ölçülmedi (T).
- `prefers-reduced-motion` kuralının (313) içeriği okunmadı; uçan paranın kapsanıp kapsanmadığı kesin değil.
- Dokun-ata (687d6e1) akışı telefonda elle denenmedi; kod yolu okundu (2910-2913): seçili işçi + istasyon/spot dokunuşu → `dropWorker`.
- GoatCounter ve Google Fonts dış çağrıları ekosistem çapında kabul edilmiş mi? Brief kısıtıyla çelişkili görünüyor.
- Botun kazanma oranı Node harness'inde ölçüldü; harness `autoDrive` sırasını taklit ediyor ama oyundaki `fastForward` adımlamasıyla birebir değil. Gerçek sayfada yalnız 1 tohum (11) denendi: kazandı.
- "Askıda simit" diye yerleşik bir gelenek kaynakta doğrulanmadı; doğrulanan "askıda ekmek". Metinde "askıda ekmek/simit" ya da genel ifade kullanılabilir.
- 4.3 için itibar katkısının üst sınırı tahmin; 30 tohumla ayarlanmalı.

## Kaynaklar
- Tycoon geç oyun para sorunu: https://discourse.automationgame.com/t/common-problem-of-nearly-all-business-tycoon-games/2919 · https://vaporlens.app/app/1342330/mad_games_tycoon_2.md · https://arshyagupta.cargo.site/ekosphere-economy
- İtibarı ilerleme kapısı olarak kullanmak: https://gamedeveloper.com/design/deep-dive-player-choice-in-space-warlord-organ-trading-simulator-s-ruthlessly-greedy-world
- Portal beklentileri: https://docs.crazygames.com/requirements/gameplay/ · https://docs.crazygames.com/requirements/technical/ · https://docs.crazygames.com/resources/getting-to-the-first-frame/
- Erişilebilirlik: https://gameaccessibilityguidelines.com/do-not-make-precise-timing-essential-to-gameplay-offer-alternatives-actions-that-can-be-carried-out-while-paused-or-a-skip-mechanism/embed/ · https://learn.microsoft.com/en-gb/gaming/accessibility/xbox-accessibility-guidelines/103 · https://igda-gasig.org/?p=42
- Askıda ekmek: https://www.hurriyet.com.tr/galeri-askida-yemek-nedir-iste-askida-uygulamasinin-detaylari-41620547 · https://yemek.com/askida-ekmek/ · https://www.milligazete.com.tr/ekmekle-akrabaligimiz
- Ekran görüntüleri: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_simit-firini/{1-title,2-plan,3-day,4-phone-plan,5-phone-day,6-auto-end}.png`

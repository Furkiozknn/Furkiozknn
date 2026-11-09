# Kırkpınar — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Çalıştırma: headless Chromium (swiftshader), CDN yerel kopyadan, 3 kısa oturum (masaüstü 960×540 TR, telefon 390×844 EN, `?auto&mode=quick`). Betik ve görüntüler: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_kirkpinar/` (`run.cjs`, `01-title-desktop.png`, `02-play-desktop.png`, `04-play-phone.png`). Repo değiştirilmedi (`git status` temiz).

## 1. Şu anki durum
- **D** Tek dosya `index.html` (4616 satır, 280 KB), Three.js r170 import map + SRI (satır 1676). Saf simülasyon `SIMLIB` içinde DOM'suz `Match` (1835) ve aynı girdileri kullanan `Brain` yapay zekâsı (2435).
- **D** İlerleme: 5 sıklet × 3-4 rakip = **18 maçlık** merdiven (`LADDER`, 1786-1792), sıklete göre süre 60/75/90/105/120 sn (`CLASS_LIMIT`, 3646). Üst üste 3 kariyer bitirince altın kemer kalıcı (4316-4318). Hızlı maç, 2 oyunculu (tek klavye), günlük meydan okuma (arena-kit, 4136).
- **D** Zorluk eğrisi yalnız rakipte: rakip seviyesi 0.34 → 1.0; oyuncu her zaman `balanced`, seviye 0.72 (4098). Kaybetmenin bedeli yok: "Tekrar dene" aynı rakibe sınırsız döner (4334).
- **D** İmza mekaniği "Tutuş Dengesi" (3e4e2d1): kilitli tutuşta işaret/aldatma okuma oyunu, stil desenleri `TUT_PAT` (1773).
- **D** Kayıt: `arena.kirkpinar.save` = `{run:{ci,oi,wins,…}, best, coachDone, belt}`; eksik alanlar `Object.assign` ile varsayılanlanıyor (2599-2601). Eski biçim kayıt (`{ci,oi,wins}`) yeni sürümde açıldı, 0 hata.
- **D** Son relay commit'i eb8edc7 ("Mid-Career Save and Resume", gemini flash-lite) başlık ekranına üçüncü bir kariyer düğmesi ve 4 gereksiz kayıt alanı (`class, boutIndex, winsCount, lossesCount`) ekledi; kariyer zaten kayıtlıydı (bkz. §3.2).
- **D** Konsol/sayfa hatası: 3 oturumda da **0**. `?auto&mode=quick` maçı bitirdi (`matches:1, wins:1, hows:{fall:1}`), 0 hata.
- **D** Hızlı maçta (yüksek kalite, 960×540) 66 draw call, **357 bin üçgen**. FPS swiftshader'da anlamsız (20); README'deki UHD 620 60 fps iddiası bu oturumda doğrulanamadı.
- **D** Mobil: sanal çubuk + 4 düğme (Tut/Hamle/Çek/İt), 390×844'te yatay taşma yok (`scrollWidth 390`), HUD tek satır. Telefonda kalite varsayılanı `low` (2597).
- **D** Ses tamamen sentez (Web Audio, 2606), TR/EN tam i18n (`TX`, 3523), gamepad desteği (3999-4005), `prefers-reduced-motion` + arena-kit paneli `RM`'yi sürüyor (2586-2588).

## 2. Güçlü yanlar (korunmalı)
- Saf sim + aynı girdiyi kullanan bot: `?auto` ve `kirkpinarSim` ile her değişiklik test edilebilir (**D**). Bu ayrım korunmalı; yeni mekanikler `Match` içine, sunum dışarıda.
- Yağ/terle zayıflayan tutuş, denge eğimiyle düşüş — türün özü okunabilir biçimde HUD'da (grip çubuğu + yağ sınırı) (**D**, ekran 02).
- Tek tıkla oyna → 2,5 sn rakip kartı → ilk maç koçu (4 adım, gerçek girdide ilerler) (**D**, 3956-3976). Poki'nin "ilk dakikada hemen oyuna sok" ilkesine uyuyor (**K** Poki).
- Kültürel doku (cazgır, davul-zurna, gerçek kemer kuralı bilgileri) gerçek kişi/marka kopyalamadan (**D**).
- Kayıt uyumu: v1 kayıtları v2'de açılıyor (**D**).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **HATA — tek oyunculu maçta `L` dili değiştiriyor (D).** README ve `MAP_ALL` (3983) `L`'yi tek oyuncuda "çek" tuşu sayıyor, ama keydown işleyicisi `KeyL`'yi oyun tuşlarından önce yakalıyor: `if (c === 'KeyL' && !(G.screen === 'play' && G.versus)) toggleLang()` (4041). Adım: Diğer modlar → Hızlı maç → Başla → Gir → `L`. Ölçüm: `lang tr → en`, maç sürerken; `rebuild()` ekranları yeniden kuruyor, HUD'da "Sen"/"Orta" TR kalırken etiketler EN oluyor (ekran 02), çekme yapılmıyor. Ok tuşları + K/L/;/Enter ile oynayan herkes etkileniyor.
2. **Relay regresyonu — üçlü kariyer düğmesi + taşan başlık (D).** Kayıtlı kariyerde başlıkta `Devam(play)`, `Kariyer merdiveni(continue)`, `Kariyer Devam(continueCareer)` — ilki ile üçüncüsü aynı işi yapıyor (4104 ve 4155). `bContinueCareer` yükleme bitmeden görünüyor (yalnız `bPlay/bCont` `hidden` ile bekletiliyor, 3803-3804, 4596). 960×540'ta amblem üstten kesiliyor, alt bilgi ("Claude Game Arena · built by…") "Diğer modlar / English" düğmelerinin üstüne biniyor (ekran 01). Ölü kod: `store.run ? t('continueCareer') : t('continueCareer')`; `lossesCount` yazılıyor ama hiç gösterilmiyor.
3. **Cazgır alt yazı kutusu iç içe çiziliyor, telefonda ekranı kapatıyor (D).** CSS `#subs .cazgir-speech, #subs div` (676) iç `<div>`'e de kutu stili veriyor → kutu içinde kutu, "ANNOUNCER" etiketi dar sütuna sıkışıyor. 390×844'te ilk maçın açılış bilgisi ekranın ortasının ~%40'ını 6,5 sn kapatıyor (ekran 04; `say('fact')` 3788). Masaüstünde de stamina etiketlerinin üstüne biniyor (ekran 02).
4. **Koç dokunmatikte klavye tuşu gösteriyor (D).** `COACH_STEPS` sabit `F/G/S/R` (3955); telefonda "F Close in on your rival and grab" (ekran 04). Tutuş Dengesi paneli bunu doğru yapıyor (`IS_TOUCH ? ['','']`, 4473) — tutarsız.
5. **Global ses düğmesi HUD'daki dil düğmesinin üstüne biniyor (D).** `#bMute` `position:fixed; right:14px; z-index:45` (249-258); masaüstü HUD'da `.acts` içindeki `#bLang` ("EN") yarısı kapalı (ekran 02).
6. **Kariyerde oyuncu gelişimi ve kayıp anlamı yok (D kod / T etki).** Oyuncu 18 maç boyunca sabit 0.72; kayıp = bedelsiz tekrar. Kemer için 3×18 = 54 maç aynı 18 rakiple → tekrar hissi (T). Kaybın "neden"i sonuç ekranında söylenmiyor; `M.stats` (throws, tut, counters, tutSlips) toplanıyor ama gösterilmiyor (1842, 4306-4345).
7. **Erişilebilirlik — künde/kaldırma kurtuluşu tuş basma yarışı (D).** `f.e.any` her yeni basışta `struggle += 1` (2285); bot `mash(3+9*lv)` Hz ile basıyor (2448). Basılı tutma alternatifi yok. XAG 107 ve GAG bunu temel motor sorunu sayıyor (**K**).
8. **2 oyunculu mod dokunmatikte oynanamaz, uyarı yok (D kod 3937, T etki).** Telefonda kart seçilebiliyor, sonra kontrol yok.
9. **README tutarsızlığı (D):** "26-bout tournament ladder" yazıyor; `LADDER` 18 rakip (3+3+4+4+4).

## 4. EKLENMELİ — yüksek değer
**4.1 Maç sonu "neden" kartı (tek ipucu)**
- Ne: Sonuç ekranında, toplanan istatistikten tek bir somut ders: örn. "Elin 4 kez kaydı — yağ sınırına yaklaşınca kıspetten tut", "Tutuş Dengesi'nde 2 yanlış okuma — ilk basış işarettir", "Rakip dengesizken hamle düğmesi yandı ama basmadın".
- Neden: Kayıp oyuncunun seçiminden kaynaklandığı hissedilirse geri dönülüyor; "kaçınılmazdı" hissi bıraktırıyor (**K** gamedeveloper "punishment systems"). Bedelsiz tekrar döngüsünü öğrenme döngüsüne çevirir (T).
- Nasıl: `Match` içinde birkaç sayaç ekle (el kayması sayısı türüne göre, yanan-ama-kullanılmayan hamle süresi); `showResult` (4306) öncelik sırasıyla ilk eşleşen TX anahtarını basar. Kayıt şeması değişmez; bot etkilenmez.
- Maliyet **S**. Risk düşük (yalnız UI + sayaç). Kısıtlara uygun.

**4.2 Rakip kartında "keşif notu" (stil eğilimi)**
- Ne: Versus kartına rakibin tarzına göre bir satır: "Güçlü: önce yüklenir (iter)", "Hileci: aldatır, ikinci basışa dikkat". `TUT_PAT` (1773) ve stil verisinden üretilir.
- Neden: İmza mekaniği bir okuma oyunu; okunabilir rakip kişiliği tekrar oynamayı öğrenmeye çevirir (T). Kartta zaten boş yer var (fact satırı).
- Nasıl: `renderVersus` (3885) içine TX'ten stil başına 1 satır; ilk iki sıklette açık, sonra "?" (ilerleme ödülü). Kayıt değişmez.
- Maliyet **S**. Risk: metin yükü telefonda — kısa tut.

**4.3 Basılı tutma ile kurtuluş/künde (erişilebilirlik)**
- Ne: Ayarlar'da "Basma yerine basılı tut" seçeneği: tuş/düğme basılıyken saniyede ~6 sanal basış üretir.
- Neden: XAG 107 ve GAG "tekrarlı basış zorunlu olmasın, daha az zorlayıcı alternatif sun" diyor (**K**). Telefonda hızlı dokunma yorucu (T).
- Nasıl: `readInput` (3990) içinde, ayar açıksa ve oyuncu `pinned/lifted/down/kunde` durumundaysa basılı `grab/ctx` için zamanlayıcıyla `edges` üret. Sim'e dokunma; ayar `settings` içine (eksikse false → eski kayıt uyumlu). Bot `Brain` girdisini kullandığından etkilenmez.
- Maliyet **S-M**. Risk: denge — oranı botun `3+9*lv` aralığının ortasına sabitle (≈6 Hz) ki avantaj olmasın.

**4.4 Kemer yıllarında çeşitlilik ("yıl 2/3 rakip değişkesi")**
- Ne: 2. ve 3. kemer yılında aynı 18 isim yerine tarz/renk karışımı ve hafif seviye artışı (+0.03/yıl), merdivende "Yıl 2" etiketi.
- Neden: 54 maçlık hedefte tekrar azalır; kemer serisi zaten var, içerik yok (D kod / T etki).
- Nasıl: `careerSpecs` (4096) `store.belt.streak` ile deterministik tohumla tarz kaydırır; `LADDER` değişmez, kayıt şeması değişmez.
- Maliyet **S**. Risk: denge (son sıklet zaten 1.0 → üst sınırla `min(1.0, …)`).

## 5. EKLENEBİLİR — orta değer / koşullu
- **Kariyer içi küçük gelişim seçimi** (galibiyet sonrası 3 karttan 1: tutuş +3 %, dayanıklılık +3 %, yağ direnci): oyuncunun sabit 0.72 kalmasını kırar. `run.perks` yoksa boş dizi → eski kayıt uyumlu; bot ilk kartı alır. **M**. Risk: meta-ilerleme beceriyi gölgeleyebilir ("galibiyet boş hissettirir", **K** roguelite tartışmaları) — etkiler küçük tutulmalı.
- **"Usta" kariyer zorluğu** (kayıp = sıklet başına dön): isteğe bağlı gerilim. **S**. Kemer serisi kurallarıyla etkileşimi netleştirilmeli.
- **Tekrar oynatmayı GIF/kısa klip olarak kaydet**: `G.rec` halkası (120 kare) zaten var; `MediaRecorder` ile 4 sn indirme. **M**. Risk: telefon belleği, tarayıcı desteği.
- **2P için telefonda bölünmüş dokunmatik** (yatay, iki çubuk): **L**, düzen riski yüksek; en azından §7'deki uyarı yeterli.
- **Tuş yeniden atama** (XAG 107, **K**): klavye düzeni farkları (AZERTY'de A/D) için değerli; **M**, i18n + kayıt alanı gerekir.

## 6. EKLENMEMELİ
- **Çevrimiçi çok oyunculu / küresel lider tablosu / hesap**: sunucu gerektirir — kısıtı aşar.
- **Gerçek başpehlivan adları, yüzleri, Kırkpınar Ağası/organizasyon logoları**: gerçek kişi/marka kopyası; mevcut kurgusal isimler korunmalı.
- **Tam ragdoll/fizik motoru (Ammo/Rapier vb.)**: ek CDN modülü + UHD/telefon performansı; mevcut özel sim okunabilir ve bot-test edilebilir. Gang Beasts tarzı "slapstick" fizik oyunun teknik denge kimliğini bozar (**K** PC Gamer).
- **Daha fazla seyirci/sahne detayı**: hızlı maçta 357 bin üçgen ölçüldü (D); telefon ve UHD'de bütçe zaten dolu (T).
- **Telefona 5.+ düğme** (ayrı künde/kaldır düğmesi): bağlam düğmesi tasarımı doğru; ekran zaten dolu (ekran 04).
- **Ödüllü reklam/kozmetik satış, zorunlu giriş ekranı/uzun intro**: ücretsiz-hesapsız kuralına ve Poki "intro'yu atla" ilkesine aykırı (**K**).
- **Mid-career save gibi zaten var olan şeyi yeniden ekleyen relay'ler**: eb8edc7 örneği; kariyer `store.run` ile zaten kalıcıydı.

## 7. Düzeltilmeli
| # | Sorun | Yer | Öneri | Mal. |
|---|---|---|---|---|
| 1 | `L` tek oyunculu maçta dil değiştiriyor (D) | 4041 | Koşulu `G.screen !== 'play'` yap (maçta dil yalnız menüden/HUD düğmesinden) | S |
| 2 | Üçlü kariyer düğmesi, yüklemede görünür, başlık taşması (D) | 3804, 4155, 4113-4115, 4283-4288 | `continueCareer` düğmesi/eylemi/TX anahtarlarını kaldır; ekstra run alanlarını yazmayı bırak ama okurken yok say (eski/yeni kayıt uyumlu) | S |
| 3 | `#subs div` iç içe kutu, telefonda ekranı kapatıyor (D) | 676-694, 706 | Seçiciyi `#subs > .cazgir-speech` yap; telefonda yazı 14 px, `max-height`, açılış bilgisini 6,5 → ~4 sn ya da koç açıkken erteleme | S |
| 4 | Koç dokunmatikte F/G/S/R gösteriyor (D) | 3955-3962 | `IS_TOUCH` ise düğme simgesi/adı (Tut, Çek, çubuk aşağı, Hamle) | S |
| 5 | `#bMute` HUD `#bLang` üstünde (D) | 249-258, 351 | Oyunda `#bMute`'yi `.acts` içine taşı ya da HUD açıkken `.acts`'a sağ boşluk ver | S |
| 6 | 2P dokunmatikte kontrolsüz (D kod) | 3937, mode ekranı | `IS_TOUCH && !klavye` ise 2P kartında "klavye gerekir" notu | S |
| 7 | README "26-bout" (D) | README.md | 18 maç olarak düzelt | S |
| 8 | 960×540 başlıkta amblem kesiliyor (D) | başlık CSS | `max-height` medya sorgusunda amblemi küçült (madde 2 sonrası yeniden ölç) | S |

## 8. Önerilen ilk 3 iş
1. **Hata paketi: §7 #1 + #2 + #3** — `L` dil hatası oyunu bozuyor, relay düğmesi başlığı bozdu ve taşırdı, alt yazı telefonda ilk 6,5 sn oynanışı kapatıyor. Üçü de S, kayıt şemasına dokunmaz; `?auto`, smoke ve eski kayıt testiyle doğrulanır. İlk deneyimi doğrudan iyileştirir (Poki "ilk dakika" ilkesi, **K**).
2. **Maç sonu "neden" kartı (§4.1) + koçun dokunmatik etiketleri (§7 #4)** — sınırsız tekrar döngüsünü öğrenmeye çevirir, telefon oyuncusuna doğru dili konuşur. S, sim'e yalnız sayaç ekler.
3. **Basılı tutma kurtuluşu (§4.3) + rakip keşif notu (§4.2)** — biri erişilebilirlik (XAG 107), diğeri imza mekaniği Tutuş Dengesi'ni okunur kılar. Toplam S-M; kemer yılları çeşitliliği (§4.4) sonraki tura.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek UHD 620 / orta telefonda FPS: swiftshader ölçümü anlamsız (20 fps); README'nin 60 fps iddiası bu oturumda doğrulanmadı.
- Tam kariyer `?auto` koşusu yapılmadı (makine paylaşımlı); `kirkpinar-title/belt` rozetleri ve `endGame` yolu bu oturumda denenmedi.
- `bContinueCareer`'a yükleme bitmeden tıklamanın hata üretip üretmediği denenmedi (T: `renderer.compile` öncesi maç kurulabilir, büyük olasılıkla yalnız takılma).
- Gerçek dokunmatik cihazda çubuk ölü bölgesi (0.28/0.45) ve künde dokunma yarışının yorgunluğu ölçülmedi.
- 1280×720 ve 1366×768 başlık düzeni ölçülmedi; taşma 960×540'ta görüldü.
- Oyuncu kitlesi verisi (GoatCounter) okunmadı; hangi modun oynandığı bilinmiyor.

## Kaynaklar
- Poki geliştirici rehberi (intro/başlık ekranını atla, hızlı yükleme): https://developers.poki.com/guide/easy-access
- Poki kalite yönergeleri: https://sdk.poki.com/poki-quality-guidelines
- Poki gereksinimleri (dikey/yatay tam ekran, ilk indirme boyutu): https://sdk.poki.com/requirements
- Defold–Poki en iyi uygulamalar (ilk dakika, dokunmatik, küçük UI yok): https://defold.com/extension-poki-sdk/best-practices
- Xbox Accessibility Guideline 107 — Input (tekrarlı basış/uzun basılı tutma alternatifi, yeniden atama): https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
- Game Accessibility Guidelines: https://gameaccessibilityguidelines.com/?p=21
- Game Developer — "How punishment systems hurt gameplay": https://www.gamedeveloper.com/design/how-punishment-systems-hurt-gameplay
- Roguelite meta-ilerleme tasarımı: https://bugnet.io/blog/how-to-design-a-roguelite-meta-progression
- PC Gamer, Gang Beasts incelemesi (basit girdi, slapstick fizik): https://pcgamer.com/gang-beasts-review
- Epic Games Store, Toribash Next (öğretici felsefesi, fizik okunabilirliği): https://store.epicgames.com/news/how-toribash-next-plans-to-reinvent-the-classic-physics-battler

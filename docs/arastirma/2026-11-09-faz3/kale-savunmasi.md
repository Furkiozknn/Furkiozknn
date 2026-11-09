# Hisar (kale-savunmasi): faz 3 araştırması

Kapsam: `/home/user/kale-savunmasi` @ 333bec6 (dal `claude/cloud-session-research-analysis-dufc2b`, origin/main ile aynı, `git status` temiz). Ana dosya `index.html` (4106 satır).
Kanıt etiketleri: **D** = doğrulandı/ölçüldü, **T** = tahmin/çıkarım, **K** = dış kaynak.
Ölçüm ortamı: headless Chromium (swiftshader), yerel three@0.170.0. Makine paylaşımlıydı (yük ortalaması 56-80, 4 çekirdek), bu yüzden fps değerleri bu ortamda anlamsız. Benim harness'im ve ekran görüntüleri: `_kale-savunmasi/` (`run.cjs`, `bot2.png`, `phone-sheet.png`, `phone-title.png`).

## 1. Şu anki durum

- **D** Bugün 3 commit "relay" olarak, govdesinde kanıt olmadan girdi (`git show --stat`):
  - fe93b64: hasar sayıları ve DOM can çubukları.
  - d8269ce: dokunmatik için alt sayfa (bottom sheet).
  - bb7011c: zırha karşı okların "Blocked" göstermesi ve bir ipucu.
  Bu üçü, aşağıdaki kritik hataların hepsinin kaynağı.
- **D** İmza mekaniği **Yol Mühendisi** (19cc140): 2 m ızgara üzerine barikat koyma, Dijkstra akış alanıyla yeniden rota hesabı, rota önizlemesi. Yeri `index.html:2461-2763`.
  - Barikatlar kayda girer (`walls`, 3556). Geri yüklenirken her biri yeniden kontrol edilir (3573).
- **D** İlerleme yapısı:
  - 15 dalga, sonra sonsuz mod. Dalgalar `makeWave` ile kurulur (2779). Can ölçeği `hpMul(w)=1+0.18k+0.022k²` (2778).
  - 3 kule × 3 seviye (1202-1206). 4 düşman türü (1208-1213). Koçbaşı (ram) her 5. dalgada.
  - Erken çağrı bonusu (2813), 1×/2×/3× hız (3479).
- **D** Kayıt:
  - `arena.hisar.save` v1: dalga, altın, can, kuleler, duvarlar (3551-3574). Ayrıca `arena.hisar.best` ve `arena.hisar.settings` var.
  - Bütün okuma/yazmalar try/catch ile sarılı. `?auto` altında `store.set` hiçbir şey yazmıyor (1319).
- **D** Bot (`?auto`, 3967-3981): `hisarSim(1260)` ile ölçüldü.
  - Relay öncesi kod (54cbd60): **dalga 15, 522 avlanan, 218 altın**. Bu, 19cc140'taki kayıtla birebir aynı.
  - **Şimdiki HEAD: dalga 8'de düşüyor, 163 avlanan.**
  - HEAD'de yalnız bb7011c'nin ok-blok koşulu kapatılınca sonuç yine 15 / 522 / 218 çıkıyor. Yani bütün fark bu tek satırdan geliyor.
- **D** Arena-kit entegrasyonu çalışıyor (615b46a): perf, günlük meydan okuma (bir kule türü kapalı), paylaş, rozetler, hareketi azalt.
- **D** i18n: `STR.tr/en` (1217-1310). `?lang` parametresi ve tarayıcı dili destekleniyor. **İstisna:** "Blocked" etiketi sabit İngilizce (2835).
- **D** Ses: tamamı Web Audio ile sentezleniyor. 9/8 Hicaz döngüsü, dalga sırasında giren davul katmanı (3797-3965). `?auto` sessiz.
- **D** Performans ayarları:
  - `?low`: gölge yok, pixelRatio 1, LOD (3785).
  - `Arena.perf` dinamik çözünürlük.
  - Bu ortamda draw call 44-47, üçgen yaklaşık 118k (`?low`, dalga 6).
- **D** Konsol: yükleme, bot ve telefon koşularında 0 sayfa hatası, 0 konsol hatası.

## 2. Güçlü yanlar (korunmalı)

- **Yol Mühendisi** gerçekten özgün bir katman:
  - Barikatsız oyun ve bot birebir aynı oynuyor.
  - Yolu tamamen kapatan ya da düşmanı hapseden hamle reddediliyor (TR/EN toast ile).
  - Rota önizlemesi var (D, kod ve 19cc140 kanıtı).
- **Deterministik denge testi:** `hisarSim` ile 25 ms sabit adım, tohumlu `rand`. Denge regresyonunu dakikalar içinde yakalıyor; bu araştırmada da yakaladı (D).
- **Kayıt disiplini:** sürümlü JSON, her alan sınırlanmış (`|0`, `clamp`), eski kayıtta `walls` yoksa sorun çıkmıyor (D, 3564-3574).
- **Bilgi sunumu:**
  - Sonraki dalga önizlemesi (3382-3387).
  - Dalga afişi ve koçbaşı can çubuğu.
  - Kule panelinde "şimdi → sonraki seviye" değerleri (3272-3275).
  - Hedefleme modları (D).
- **Atmosfer:** el yapımı kale, Hicaz müzik, parşömen arayüz. Prosedürel geometri yedeği var (`?noassets`).
- **Erişilebilirlik temeli:**
  - Klavye kısayolları ve overlay içinde focus trap (3507).
  - `prefers-reduced-motion` desteği ve Arena "hareketi azalt" ile sarsıntı/flaş kapatma (2863, 3033).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)

1. **KRİTİK: denge kırıldı, oklar zırhlılara ve koçbaşına 0 hasar veriyor (D).**
   - `damage()` 2833-2840: `if (e.type === 'shield' || e.armor > 0) a = 0`.
   - Kalkanlının zırhı 0.55, koçbaşınınki 0.35. Önceden oklar bunlara %45 ve %65 hasar veriyordu. Şimdi ikisine de 0.
   - Bot dalga 15'ten 8'e düştü (bölüm 1'deki ölçüm).
   - Çelişkili metinler:
     - Rehberdeki `guideRule1` "oklar işlemez" diyor; eski kodla zaten tutarsızdı.
     - README "Armour negates arrow damage completely" diyor.
     - `archerDesc` "Zırha karşı zayıf" diyor.
   - Yani metin tutarsızlığı, metin yerine kod "düzeltilerek" giderilmiş.
2. **KRİTİK: telefonda üst kontroller ekran dışında (D, 390×844, `isMobile`, `hasTouch`).**
   - `#topControls` x 386-630 aralığında. Barikat, Hız, Duraklat, Ses ve Dil düğmelerinin hepsi `elementFromPoint` ile "offscreen" çıktı.
   - Sonuç: telefonda imza mekaniği (barikat) ve oyun içi duraklatma kullanılamıyor.
   - Kaynak 651c5b4 (UI rebirth): `#top` için `flex-wrap` yok (181-193, 723-735). Koddaki yorum "the top bar wraps on phones" diyor (4079) ama sarmıyor.
3. **YÜKSEK: yüzen etiket havuzu tıkanıyor ve "Blocked" etiketleri ekranda takılı kalıyor (D).**
   - `floatText(..., 'bad')` etiketinin tipi `'bad'` oluyor. `updateFloatText` ise yalnız `type==='dmg'` olanların ömrünü azaltıyor (3444). "Blocked" etiketleri bu yüzden **hiç silinmiyor**, dünya koordinatında asılı kalıyor.
   - Katran DOT'u her 25 ms'lik adımda `damage(..,'dot')` çağırıyor (2985) ve her seferinde `floatText(0)` oluşuyor. Ekranda "0" yağmuru var.
   - Ölçüm (`?auto&low`, dalga 6), 45 slotluk havuzun dağılımı:

     | An | "0" etiketi | "Blocked" | Can çubuğu |
     |---|---|---|---|
     | Başlangıç | 35 | 3 | 2 |
     | 40 sn sonra | 22 | 15 (artıyor) | 2 |

   - Havuz bir süre sonra tamamen "Blocked" ile dolacak; o zaman hasar sayıları, "+altın" ve DOM can çubukları da kaybolacak. Bu son kısım **T** (çıkarım).
   - Görsel kanıt: `bot2.png`, kapı önünde üst üste binen "Blocked" ve "0" yazıları.
4. **YÜKSEK: telefonda alt sayfa dalga düğmesinin üstüne biniyor (D).**
   - `#bottomSheet` için `bottom:12px; z-index:7`. Sayfa açıkken `bWave` merkezine `elementFromPoint` → `card`.
   - Eski `#panel` telefonda `bottom:76px` ile dalga kutusunun üstünde duruyordu (751). Alt sayfa bu ayarı bozdu.
   - Kule kurma sayfası ekranın yaklaşık alt yarısını kaplıyor (`phone-sheet.png`).
   - `COARSE` olan geniş ekranlarda (dokunmatik dizüstü, tablet) da tam genişlik sayfa açılıyor (T).
5. **ORTA: `?auto` sözleşmesi ihlal ediliyor (D).**
   - Bot koşusu sonunda localStorage'da `arena.hints.v1 = {"kale-savunmasi:arrow_shield":…}` vardı.
   - Nedeni: bb7011c'nin `ARENA.hint` çağrısı `AUTO` kontrolü yapmıyor (2836). README ise `?auto` için "writes nothing to localStorage" diyor.
   - Ayrıca `arena.profile.v1.plays` sayacı da yazılıyor. Bu kit'in `boot` adımından geliyor, oyunun kodu değil (bölüm 9).
6. **ORTA: can çubuğu iki kez çiziliyor ve kare başına DOM yazılıyor.**
   - Zaten instanced 3D çubuk vardı (`barBg/barFg`, 3094-3104). fe93b64 bunun üstüne ikinci bir DOM çubuğu ekledi (3108-3122). İkisi `bot2.png`'de üst üste görünüyor (D).
   - Her karede her hasarlı düşman için `labelPool.find` (O(n²)) ve `innerHTML` yeniden yazılıyor.
   - UHD dizüstünde dalga 10 ve sonrasında maliyetli olması bekleniyor (T). Bu makinede ölçülemedi.
7. **ORTA: barikat mekaniği keşfedilmesi zor.**
   - README Features bölümünde ve `project-meta.json key_features`'ta barikat yok (D).
   - Dokunmatik kontrol metni `controlsTouch` barikattan söz etmiyor (D, 1222).
   - İlk 30 saniyede oyuncu yalnız "taş kaideye tıkla" toast'unu görüyor (3740, D).
8. **DÜŞÜK:**
   - `.dmg-num.bad` için CSS yok; "Blocked" sıradan sarı sayı gibi görünüyor (D).
   - Günlük meydan okuma düğmesi telefonda "(seri 0 · en iyi 0)" metnini iki satıra kırıyor (D, `phone-title.png`).
   - Rehber kartındaki maliyetler (60/110/80) sabit yazılmış, `TOWERS`'tan okunmuyor (3625-3635, D).

## 4. EKLENMELİ (yüksek değer)

**4.1 Telefonda erişilebilir kontrol çubuğu (barikat, duraklat, hız)**
- **Ne:** `≤760px` genişlikte `#top` iki satıra sarsın. Ya da daha iyisi: Barikat ve Hız düğmeleri dalga kutusuna (alt şerit) taşınsın, Duraklat ve Ses üstte kalsın.
- **Neden:** Şu an telefonda imza mekaniği ve duraklatma yok (Sorun 2).
  - Poki ve CrazyGames, mobil ve dokunmatik desteğini taban gereksinim sayıyor (K: sdk.poki.com/requirements, docs.crazygames.com/requirements/technical).
  - "Her an duraklatabilme" erişilebilirlik kılavuzlarında temel madde (K: gameaccessibilityguidelines.com).
- **Nasıl:** Yalnız CSS ve medya sorgusu: `#top{flex-wrap:wrap}`, `.hud-controls{order:3;width:100%;justify-content:flex-end}`. `--top-h` gözlemcisi zaten var (4080). Doğrulama 390×844 ve 360×740'ta `elementFromPoint` ile yapılmalı.
- **Maliyet / risk:** S. Risk düşük; banner ve toast konumları `--top-h`'ye bağlı, kontrol edilmeli.

**4.2 Yumuşak sayaç ve tutarlı zırh bilgisi**
- **Ne:** Okların zırha karşı hasarı eski çarpana dönsün (`a *= 1 - e.armor`). Zırh, "Blocked" yerine **küçültülmüş ve gri bir hasar sayısı** ile, ayrıca ilk karşılaşmada bir kerelik i18n ipucu ile gösterilsin.
- **Neden:**
  - Bot ölçümüyle denge geri geliyor (D, 15/522/218).
  - Tower defense türünde yüzdesel azaltma yaygın; tam bağışıklık (hard counter) oyuncuyu tek çözüme kilitliyor (K: game-ace.com, critpoints.net).
  - Kingdom Rush'ta zırh azaltır ama "true damage" gibi karşı araçlar da var (K: tvtropes / KR wiki).
- **Nasıl:**
  - Bölüm 7'deki düzeltmeleri uygula.
  - Metinleri koda uydur: `guideRule1`, README ve `archerDesc` → "zırh okları büyük ölçüde azaltır".
  - `arrowShieldHint`'i `!AUTO` ile koru.
  - Hasar sayısında `kind==='armor'` sınıfı kullan.
- **Maliyet / risk:** S. Risk yok; bot karşılaştırması zorunlu.

**4.3 İlk karşılaşma kartları ("Harp Defteri")**
- **Ne:** Atlı, Kalkanlı ve Koçbaşı ilk kez geldiğinde oyun 1 kez yumuşakça duraklasın. Kartta ikon, bir cümlelik tarif ve karşı önerisi olsun (TR/EN). Rehbere "Düşmanlar" sekmesi eklensin; görülen türler orada açılsın.
- **Neden:** Kingdom Rush ansiklopedisi yeni bilgiyi açıldıkça kaydediyor ve kaybedince ipucu veriyor (K: kingdomrushtd.fandom.com/wiki/Encyclopedia). Şimdiki rehberde tek bir statik kural listesi var (3619).
- **Nasıl:**
  - `arena.hisar.seen` anahtarı (yeni, opsiyonel; eski kayıtları etkilemez).
  - `spawn()` içinde, `!AUTO && !seen[type]` ise `setPaused` ve özel kart.
  - Görsel olarak `showScreen` deseni ile mevcut `ocard` kullanılabilir.
- **Maliyet / risk:** S-M. Risk: `?auto` ve günlük modda atlanmalı; telefonda kart küçük ekranda sığmalı.

**4.4 Barikatın ilk deneyime girmesi**
- **Ne:** Dalga 2 bittiğinde bir kerelik bir ipucu: "B / Barikat düğmesi: düşmanı kulelerin önünde dolaştır". Ayrıca `controlsTouch`'a barikat eklensin, README ve meta `key_features`'a madde eklensin.
- **Neden:** Mekanik görünmez (Sorun 7). İlk 30 saniye rehberliği Arena.hint'in amacı (kit başlığı, 796).
- **Nasıl:** Faz geçişinde (3052) `!AUTO && ARENA && G.wave===2` → `ARENA.hint('wall', t('wallTip'))`.
- **Maliyet / risk:** S. Risk yok.

**4.5 Zorluk seçimi (Kolay / Normal / Zor)**
- **Ne:** Başlık ekranında seçim. `hpMul` ve başlangıç altını/canı bir katsayıyla değişsin. Rekor her zorluk için ayrı tutulsun (`arena.hisar.best.<d>`; mevcut `best` = normal sayılsın).
- **Neden:**
  - Bot normalde dalga 15'te düşüyor, yani normal zorluk yeni oyuncu için sert (T).
  - Oyun hızı ve zorluk seçimi erişilebilirlik kılavuzlarında temel madde (K: gameaccessibilityguidelines.com).
  - KR'deki zorluk ve challenge modları tekrar oynanabilirlik sağlıyor (K: App Store yorumları, PocketGamer).
- **Nasıl:**
  - Kayda `diff` alanı eklensin; yoksa `'normal'` kabul edilsin.
  - `?auto` her zaman normal oynasın; bot ölçümü değişmez.
  - Günlük meydan okuma normal kalsın.
- **Maliyet / risk:** M. Risk: kayıt uyumluluğu (varsayılanla çözülür), rekor anahtarlarının göçü.

## 5. EKLENEBİLİR (orta değer / koşullu)

- **Dalga sonu yıldız / not (1-3):** kaybedilen cana göre, KR yıldızları gibi (K: KR wiki). Bitiş kartı ve paylaş metnine eklenir. Maliyet S. Yalnız yerel; ödül yok, sadece hedef.
- **Seviye 3'te kule dalı:** örneğin okçuda "zırh delici" ya da "yaylım"; topta "uzun menzil" ya da "misket". Derinlik katar. Maliyet M-L. Bot planı ve kayıttaki `level`/`branch` alanı gerekir. Dengeyi `hisarSim` ile ölçmeden yapılmamalı.
- **Hazır barikat bulmacası günlük meydan okumada:** günün tohumu 3-5 hücreyi önceden kapatsın, böylece imza mekaniği günlük modda öne çıksın. Maliyet S-M. Risk: `wallProblem` kontrolü zaten var.
- **Sonsuz modda dalga 20, 25 ve 30'da kilometre taşı rozeti** (`ARENA.award`). Maliyet S.
- **Aktif yetenek "Kızgın yağ"** (bekleme süresiyle kapı önüne alan hasarı). Ana döngüye etkileşim katar. Maliyet M. Bot ona dokunmazsa denge ölçümü değişmez; ama oyuncu dengesi değişir. Koşullu.
- **Dokunmatik barikat modunda "sürükleyerek çoklu yerleştirme"** ve hover olmadığı için dokunmada rota önizlemesinin ilk dokunuşta gösterilmesi. Telefonda dokunma ile hover yokluğu doğrulanmadı (T). Maliyet S-M.

## 6. EKLENMEMELİ

- **Tam bağışıklık (hard counter):** Okların 0 hasar vermesi gibi kurallar dengeyi bozdu (D: dalga 15 → 8). Tek çözümlü sayaç tasarımı, türde yüzdesel azaltmanın standart olmasına da ters (K).
- **Uçan birimler:** Barikat ve yeniden rota mekaniğini anlamsızlaştırır. 19cc140 de bilinçli olarak "uçan birim yok" demiş (D).
- **Düşman başına daha fazla DOM öğesi** (etiket, can çubuğu, isim): 3D instanced çözüm zaten var. DOM, UHD/8 GB hedefini ve telefonu zorlar (T).
- **Çevrimiçi skor tablosu, hesap, bulut kayıt, reklam/IAP:** kısıtı aşar (sunucu, kullanıcı verisi, harici ağ).
- **Prosedürel ya da çoklu harita kampanyası:** Kısıtı aşmaz, ama maliyeti L. Ayrıca pad, yol ve barikat ızgarası tek haritaya göre ayarlı (1583-1585, 2471). Şimdilik değer/maliyet oranı kötü.
- **Ünlü TD oyunlarından kahraman, isim ya da sanat kopyası** (ör. KR kahramanları ve büyüleri). Yalnız tür ilkesi alınmalı.
- **Kanıt ve bot ölçümü olmadan "relay" ile oynanış değişikliği:** Bugünkü üç commit kanıtsız girdi ve üç kritik hata getirdi (D).

## 7. Düzeltilmeli (hata, cila, erişilebilirlik, performans)

1. `damage()` (2833-2846):
   - Ok kolunu `a *= 1 - e.armor` olarak geri al.
   - DOT için hasar sayısı üretme ya da biriktirip yaklaşık 0,5 sn'de bir göster.
   - "Blocked" yerine i18n'li metin kullan.
   - `ARENA.hint` çağrısını `!AUTO` ile koru.
2. `floatText` / `updateFloatText` (3432-3452):
   - `'dmg'` dışındaki ve `'hp'` dışındaki tipler de ömür azaltsın (`type !== 'hp'`).
   - Havuz dolunca en eskisinin yerine geçsin.
   - Can çubukları ayrı bir havuz kullansın, ya da daha iyisi DOM can çubuğu tamamen kaldırılsın (3108-3122). 3D çubuk yeterli.
3. Alt sayfa (2452-2457):
   - Telefonda `bottom` değeri dalga kutusunun üstüne alınsın (`calc(76px + env(safe-area-inset-bottom))`, eski panel gibi).
   - Ya da alt sayfa açıkken dalga düğmesi sayfanın içinde gösterilsin.
   - `COARSE` yerine `COARSE && innerWidth<=760` kullanılsın.
   - Sayfaya `role="dialog"` ve `aria-label` eklensin.
4. `#top` telefonda sarmalı (bölüm 4.1).
5. Metinler koda uymalı: `guideRule1` (TR/EN), README "Armour negates…" ve "Features" barikat maddesi, `project-meta.json key_features`.
6. `.dmg-num.bad` / armor stili eklensin. Renge ek olarak biçim kullanılsın (küçük, italik); erişilebilirlik kılavuzlarına göre bilgi yalnız renkle verilmemeli (K: IGDA GA-SIG top ten).
7. Rehber maliyetleri `TOWERS[k].cost[0]`'dan okunsun (3625-3635).
8. Doğrulama kapısı (gelecek her oynanış değişikliği için):
   - `hisarSim(1260)` sonucu `{wave:15, kills:522, gold:218}` ile karşılaştırılsın.
   - `?auto` sonrasında localStorage boş olmalı (kit `profile` hariç).
   - 390×844'te `elementFromPoint` kontrolü yapılsın.
   - `tools/smoke.mjs` koşulsun.

## 8. Önerilen ilk 3 iş

1. **Relay regresyonlarını düzelt** (bölüm 7.1-7.3 ve 7.5): zırh çarpanı, etiket havuzu, DOT spam'i, `?auto` hint yazımı, çift can çubuğu, alt sayfa/dalga düğmesi çakışması.
   - Gerekçe: oyun şu an bir önceki sürümden ölçülebilir biçimde kötü. Bot 15'ten 8'e düştü, ekranda silinmeyen yazılar birikiyor, telefonda alt sayfa açıkken dalga çağrılamıyor.
   - Kabul ölçütleri:
     - `hisarSim` = 15 / 522 / 218.
     - Dalga 6'dan sonra 60 sn boyunca görünür etiket sayısı sınırlı, "Blocked"/"0" birikmesi yok.
     - `?auto` sonrası `arena.hints.v1` yok.
2. **Telefon üst çubuğunu düzelt** (bölüm 4.1).
   - Gerekçe: imza mekaniği ve duraklatma telefonda erişilemez. Maliyeti S, etkisi en yüksek. Portal gereksinimi (K).
3. **Barikatın ilk deneyime girmesi ve ilk karşılaşma kartları** (bölüm 4.4, sonra 4.3).
   - Gerekçe: oyunun ayırt edici mekaniği şu an yalnız bir B tuşu olarak duruyor. Yeni düşmanlar için karşı-öneri, zırh dengesi geri geldiğinde oyuncunun "neden kaybettim" sorusunu cevaplar.
   - Zorluk seçimi (4.5) bundan sonra gelir.

## 9. Doğrulanmayanlar / açık sorular

- **Gerçek fps:** UHD 620'da DOM can çubuklarının maliyeti ölçülmedi. Bu makinede yük ortalaması 56-80 olduğu için fps 5-6 çıktı; bu oyunla ilgili değil.
- **Havuzun tamamen "Blocked" ile dolması:** 40 sn'de 3'ten 15'e çıktığı ölçüldü. Uzun koşu yapılmadı; dolma ve sonucu çıkarım (T).
- **`phone-title.png`'deki yatay bant:** başlık kartını kesen bulanıksız bir şerit var. Büyük olasılıkla yük altında headless compositor artefaktı (T). Gerçek telefonda kontrol edilmeli.
- **Dokunmatikte barikat önizlemesi:** `pointermove` olmadan rota önizlemesi çalışmıyor olabilir. Kontroller ekran dışında olduğu için test edilemedi.
- **Kit'in `?auto` altında `arena.profile.v1` yazması:** `touchProfile()` boot sırasında çağrılıyor. Bu ARENA-KIT bloğu, düzenlenemez. Kit sahibine bildirilmeli; oyun tarafında düzeltilemez.
- **Tasarım kararı:** zırh tam bağışıklık mı olmalı? Kullanıcı bunu bilerek istediyse, bunun yerine dalga ve kule dengesinin yeniden ayarlanması gerekir. Bu rapor yumuşak sayaçta kalmayı öneriyor.
- **Firefox ve WebKit:** bu turda koşulmadı; yalnız Chromium. CI'da `smoke.yml` üç tarayıcıyı kapsıyor.
- **gamedeveloper.com:** bu oturumun ağ izinlerinde olmadığı için Defender's Quest makalesi okunamadı.

## Kaynaklar

- Poki SDK gereksinimleri: https://sdk.poki.com/requirements · https://sdk.poki.com/new-requirements
- Poki, yüksek kaliteli tarayıcı oyunu (2026-05): https://poki.com/blog/what-makes-high-quality-browser-game
- CrazyGames teknik gereksinimler: https://docs.crazygames.com/requirements/technical/ · ilk kareye ulaşma: https://docs.crazygames.com/resources/getting-to-the-first-frame/
- Kingdom Rush ansiklopedisi: https://kingdomrushtd.fandom.com/wiki/Encyclopedia · KR wiki: https://kingdomrushtd.fandom.com/wiki/Kingdom_Rush
- KR Frontiers ipuçları: https://www.pocketgamer.com/kingdom-rush-frontiers/how-to-survive-in-kingdom-rush-frontiers-hints-tips-and-tricks/
- KR kule mekanikleri (true damage / zırh): https://tvtropes.org/pmwiki/pmwiki.php/Characters/KingdomRushTowers
- TD hasar ve zırh türleri: https://game-ace.com/blog/engineering-of-tower-defense-games/
- Sert ve yumuşak sayaçlar: https://critpoints.net/2025/05/06/building-counterplay-for-pvp-games · https://www.gamedeveloper.com/design/in-defense-of-hard-counters-in-real-time-strategy-games (yalnız arama özeti; sayfa ağ izni yüzünden açılamadı)
- KR seviye tasarımı: https://www.gamedeveloper.com/design/kingdom-rush---the-wonderful-campaign-level-design (yalnız arama özeti)
- Game Accessibility Guidelines: https://gameaccessibilityguidelines.com/basic/
- IGDA GA-SIG Top Ten: https://igda-gasig.org/how/game-accessibility-top-ten-se/

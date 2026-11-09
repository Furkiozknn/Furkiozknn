# Peri Golf — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Ölçüm ortamı: headless Chromium + SwiftShader, makine yükü ~70 (4 çekirdek). Bu yüzden fps ve yükleme süreleri gerçek donanımı temsil etmez.
Ham çıktılar ve ekran görüntüleri: `_peri-golf/` (`result.json`, `result2.json`, `01..05-*.png`, `run.cjs`, `run2.cjs`). Repo değişmedi (`git status` temiz).

## 1. Şu anki durum
- **D** `index.html` 3925 satır, 228 KB. Three.js r170 import map + SRI (s.1486-1487). Oyunda 12 delik var, toplam par 40 (s.1964-2006). Sabit adımlı fizik kullanılıyor: DT=1/120, sürtünme yüzeye göre değişiyor (s.2655-2656, `stepBall` s.2712). Hareketli engeller: çark, kapı, fener, eşek.
- **D** İlerleme: delikler sırayla açılıyor (`best.unlocked`, s.2954). Her delikte 3 yıldız var: par altı, gizli üzüm, özel görev (s.2940). Hayalet çizgi en iyi vuruşu gösteriyor. Gizli kestirme ve tek vuruş galerisi de var (s.2010-2023, s.3000-3007).
- **D** Kayıtlar `localStorage`'da tutuluyor:
  - `arena.periGolf.settings|save|best` (s.1799)
  - `perigolf.shortcuts|aces` (s.1820)
  - Eksik alanlar yüklenirken tamamlanıyor (s.1816-1817), yani eski kayıtlar açılıyor.
- **D** `?auto` botu aynı fiziği simülasyonla arayarak oynuyor (`botPlan` s.2818). Ölçüm (`?auto&nosave&noassets` + `periGolfSim(400)`):
  - 12 deliği **14 vuruşta** bitirdi; delik başına `[1,1,1,1,1,1,1,1,1,1,2,2]`.
  - **20 yıldız** topladı, 0 hata, ~10 sn sürdü.
  - README ve project-meta "18 vuruş, 23 yıldız" diyor; bu bilgi eski.
- **D** Bugün arena-kit (s.1132-1485) ve imza mekaniği eklendi. Bunlardan sonra relay ile iki commit daha geldi:
  - `be2763e`: HUD'a "deliği yeniden başlat" düğmesi ve "vuruş iptali" (s.1579, s.3596-3610, s.3779).
  - `639a648`: data-URL manifest (s.17) ve blob-URL service worker (s.3906-3922).
- **D** i18n TR/EN; dil `navigator.language` ile seçiliyor (s.1729-1813). `restartHoleShort` anahtarı tanımlı ama hiçbir yerde kullanılmıyor (s.1731, s.1760).
- **D** Telefon (390×844, TR, dokunmatik):
  - Yatay taşma yok (`scrollWidth` 390).
  - HUD'da 6 düğme var, her biri 44×44 px.
  - Arena dişlisi sağ altta (340,794) ve ipucu kutusuyla çakışmıyor.
  - Telefonda Low tier otomatik seçiliyor (s.1805-1809).
- **D** Ses tamamen Web Audio ile sentezleniyor (s.1827-). İsteğe bağlı 671 KB'lık varlık paketi ilk kareden sonra yükleniyor (s.3494, s.3901).
- **D** Konsolda hata yok: masaüstü, telefon ve bot koşularında `pageerror`/`console.error` = 0.

## 2. Güçlü yanlar (korunmalı)
- Gerçek fizik ile görsel tahmin aynı kodu kullanıyor. Önizleme çizgisi `simulateShot` ile çiziliyor (s.2798, s.3830), bu yüzden çizgi oyuncuya yalan söylemiyor (**D**). Golfie incelemesi, güvenilir yörünge önizlemesinin riskli vuruş tasarımı için şart olduğunu söylüyor (**K**).
- Delik başına 3 farklı yıldız var (par altı, keşif, beceri). Bunlara gizli kestirme ve tek vuruş galerisi eklenince tekrar oynama nedeni ve tek seferlik hedefler ucuza sağlanmış (**D**).
- Bot aynı fiziği kullanıyor, kayıtlara dokunmuyor (`arenaAward` s.3097 `FLAG.auto`'yu dışlıyor) ve `periGolfSim` ile 10 sn'de 12 delik doğrulanabiliyor (**D**).
- Tamamen procedural bir temel var; varlıklar yüklenemezse oyun procedural sürüme düşüyor (`?noassets`). Draw call sayısı 27-29 (**D**, debug satırı).
- Erişilebilirlik temeli yerinde (**D**, s.1123, s.3613-3631):
  - 44 px dokunma hedefleri
  - `prefers-reduced-motion` CSS'i
  - tam klavye desteği (oklar + Space ile güç doldurma)
  - `aria-label`'lar `data-tt` ile iki dile çevriliyor
- İlk 30 saniye sade (**D**, ekran görüntüleri 01, 02, 05):
  - Oyna → 3,2 sn'lik geçilebilir tanıtım uçuşu
  - "Topa basıp geriye çek" ipucu
  - Ekranda delik adı, par ve özel görev

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Ölü ve riskli PWA kodu (D + K).** `navigator.serviceWorker.register(blob:…)` her tarayıcıda reddediliyor.
   - Ölçtüm: `Failed to register a ServiceWorker: The URL protocol of the script ('blob:…') is not supported`, kayıt sayısı 0.
   - `.catch(()=>{})` hatayı yuttuğu için kimse fark etmiyor. WPT testleri blob/data SW kaydının TypeError vermesini bekliyor (**K**).
   - Kod çalışsaydı daha kötü olurdu: cache-first, sürümsüz `perigolf-v1` önbelleği oyuncuları eski `index.html`'e kilitlerdi.
   - Data-URL manifestte ikon yok ve `start_url:"./"` bir `data:` adresine göre çözülüyor. Kurulabilir PWA olması beklenmez (**T**).
   - Sonuç: tek dosya kısıtıyla gerçek bir offline PWA mümkün değil. Bu kod yalnızca yanıltıcı.
2. **Vuruş iptali, oyuncuya görünen gücü siliyor (D).** Önizleme çizgisi ve güç çubuğu `power>0.03`'te açılıyor (yaklaşık 12,5 px sürükleme; s.3589, s.3829). İptal eşiği ise 24 px (s.3600).
   - Ölçtüm: 20 px sürüklemede `power=0.069`, güç çubuğu görünür. Bırakınca vuruş sayısı 0 kaldı; vuruş sessizce yutuldu. İptal edildiğini gösteren bir işaret de yok.
   - Yan etki: fare ve dokunmada en kısa vuruş büyüdü. Ölçülen yuvarlanma mesafeleri (s.2787 hız = 1,2 + 8,8·güç):

     | Durum | Güç | Yuvarlanma |
     |---|---|---|
     | Eski en kısa vuruş | 0,04 | 0,99 m |
     | Telefonda yeni en kısa (24 px) | 0,107 | 1,85 m |
     | Masaüstü 960×540'ta yeni en kısa | ~0,09 | ~1,6 m |

   - Bu, ıskalanan kısa vuruşlarda deliği geçip uzağa gitme demek. Delik yakalama hızı cömert (<2,8 m/s, s.2781), bu yüzden zararı orta düzeyde (**T**).
3. **"Yeniden başlat" düğmesi top deliğe düştükten sonra da çalışıyor (D).** Ölçtüm: `phase:'sunk'` sırasında HUD düğmesi görünür ve tıklanabilir.
   - Tıklayınca `card[0]` null oluyor ve delik 1 yeniden başlıyor.
   - Ama kayıt `{"hole":1,"card":[2,…]}` olarak (yani delik 2'ye geçmiş hâliyle) ve `holeBest` yazılmış kalıyor.
   - Sonuç: tutarsız bir kayıt durumu ve Devam Et/kart karışıklığı oluşuyor.
   - Ayrıca `restartHole` (s.3057) o deliğin vuruşlarını sınırsız sıfırlıyor. Pause menüsünde zaten vardı; artık HUD'da tek dokunuşla erişiliyor. Bu yüzden "en iyi tur" rekoru (s.2975) sınırsız mulligan ile alınabiliyor (**D** kod; etkisi **T**). Forumlar bu dengeyi tartışıyor: kolay yeniden başlatma hayal kırıklığını azaltıyor ama rekorun anlamını düşürüyor (**K**).
4. **Harici Google Fonts çağrısı (D + K).** s.18-20 `fonts.googleapis.com`'dan Fredoka ve Plus Jakarta Sans yüklüyor. Fredoka zaten `assets/fonts/`'tan self-host ediliyor (s.83-96), yani çağrı gereksiz.
   - Bu, "harici ağ çağrısı yok (CDN modülleri hariç)" kısıtını ihlal ediyor.
   - Oyuncunun IP'si Google'a gidiyor. LG München I 3 O 17493/20 kararı, yerel alternatif varken bunu GDPR ihlali saydı (**K**).
   - Not: s.1489'daki GoatCounter sayacı da harici bir çağrı. Daha önce eklenmiş; kısıtla ilişkisi kullanıcıya sorulmalı.
5. **Zorluk ve içerik sığ (D + T).** Bot 10/12 deliği tek vuruşta bitiriyor ve tümünü 14 vuruşta (par 40) tamamlıyor.
   - Bunun bir kısmı gizli kestirmelerden geliyor. Bot simülasyonu warp'ı içeriyor; oyuncunun önizlemesi ise warp'ta kesiliyor (s.2805).
   - Delikler küçük (~8-15 m) ve 12 delik insan için tahminen 8-12 dakikalık bir oturum (**T**).
   - Günün meydan okuması mevcut 12 delikten birini seçiyor (s.3077). Rüzgâr ise yalnız havadaki topa etki ediyor: ivmesi ≤0,14 m/s² (s.2749), yani pratikte fark yaratmıyor (**D** kod). Bu yüzden günlük deliğin yeniliği zayıf.
   - Günlük skor yıldız sayısı (0-3) ve maksimumu tutuluyor (s.1392). Vuruş sayısıyla rekabet yok.
6. **Arena erişilebilirlik ayarları okunmuyor (D).** Oyun kodunda `Arena.settings` (reducedMotion, autoPause, vibration) hiç kullanılmıyor (grep, kit dışı 0 sonuç).
   - Hareket azaltma tercihine rağmen şunlar aynen çalışıyor: 3,2 sn tanıtım kamera uçuşu (s.2879, s.3536), peri pırıltı izi (s.3822), balonlar ve partiküller.
   - XAG 108/107, mekanik bazında ayarlanabilir yardımlar öneriyor (**K**).
7. **Belgeler eski (D).** README ve project-meta'da bot "18 vuruş/23 yıldız" yazıyor; ölçülen 14/20. README kontroller tablosunda yeni HUD yeniden başlat düğmesi ve iptal jesti yok.
8. **Telefon HUD'u küçük kusurlar (D, ekran 05).** Üst bardaki 12 noktalı ilerleme şeridi 390 px'te sağdan kesiliyor. Tee'de top, yakın duvarın arkasında yarı gizli. Ekranın alt ~%35'i teras yan yüzüne gidiyor. Masaüstünde de top yakın duvarın üstünden görünüyor (ekran 02).

## 4. EKLENMELİ — yüksek değer
**4.1 Relay PWA kodunu kaldır ya da dürüst hâle getir.**
- Ne: s.3906-3922'deki SW bloğunu ve s.17'deki data-manifesti kaldır.
- Neden: hiç çalışmıyor; çalışsaydı eski sürüme kilitlerdi.
- Nasıl: iki bloğu sil. Offline desteği tek dosya kısıtını aşar (ayrı `sw.js` gerekir); istenirse ayrı karar olarak işaretlenmeli.
- Maliyet **S**. Risk yok; bot ve kayıt etkilenmez.

**4.2 Vuruş iptalini görünür ve tutarlı yap.**
- Ne: eşikleri hizala.
  - İptal yarıçapı içinde önizleme ve güç çubuğu gösterilmesin.
  - Güç, iptal yarıçapından itibaren 0'dan başlasın: `power = (len - CANCEL) / range`. Böylece en kısa vuruş eski ~1 m'ye döner.
  - İptal bölgesinde topun etrafında soluk bir halka ve "İptal / Cancel" etiketi olsun.
- Nasıl: s.3589 ve s.3600'ü aynı `CANCEL_PX` (≈16-20 px) sabitine bağla, `ui.power` çağrısına koşul ekle, iki i18n anahtarı ekle.
- Maliyet **S**. Risk düşük: bot `stroke()`'u doğrudan çağırıyor, etkilenmez.
- Kanıt: §3.2 ölçümü. Golfie incelemesi "vuruşu görüp ayarlayabilmeli" diyor (**K**).

**4.3 Yeniden başlatmayı güvenli ve dürüst yap.**
- Ne:
  - HUD düğmesi yalnız `phase==='play'||'intro'` iken etkin olsun; `sunk/result/end` sırasında `disabled`.
  - Restart sayısını tut (`game.restarts`).
  - Restart yapılmış turlar "en iyi tur" rekoruna yazılmasın ya da kartta "↺" işaretiyle gösterilsin.
  - Alternatif: Mini Golf Resort'taki gibi +1 vuruş cezalı mulligan (**K**).
  - İsteğe bağlı: `R` kısayolu.
- Nasıl: `restartHole` başına faz koruması. `finishCourse` (s.2975) rekor şartına `!game.restarts` ekle. Eski kayıt biçimi değişmesin; yeni alan isteğe bağlı olsun.
- Maliyet **S**. Risk: kayıt uyumu iyi (eski kayıtlarda alan yok, 0 kabul edilir).

**4.4 Harici font çağrısını kaldır.**
- Ne: s.18-20'deki Google Fonts `preconnect` ve stylesheet satırlarını sil.
- Neden: Fredoka zaten yerelde. Plus Jakarta yalnız yedek fonttu; `system-ui`'ya düşer.
- Maliyet **S**. Risk: başlık glifleri değişmez (Fredoka yerel), yalnız yedek font değişir. Kısıta uyumu artırır.

**4.5 Günün meydan okumasını gerçekten günlük yap.**
- Ne: günlük delik için seed'li değiştiriciler ekle:
  - ayna (x → −x)
  - kaydırılmış tee (yol üzerinde bir nokta)
  - engel hızı veya faz ±%30
  - "2 vuruş sınırı" ya da "üzümü al + par" gibi bir hedef
- Skor: yıldız + vuruş birleşimi, örneğin `stars*10 + max(0, par+2-strokes)`; `complete()` maksimumu tuttuğu için büyük daha iyi olmalı.
- Nasıl: `startDaily` (s.3080) içinde `HOLES[i]`'nin derin kopyasını alıp dönüştür. `Course` ve `botPlan` veriyle çalıştığı için bot da oynayabilir. Doğrulama: her değiştirici için `periGolfSim` + bot ≤ par+3. Ayna dönüşümünde `SHORTCUTS[i]` ve `deco` da aynalanmalı.
- Maliyet **M**. Risk orta: duvar ve tünel tanımları ile kestirme koordinatları birlikte dönüşmeli; çözülemeyen delik riski var, bu yüzden bot testi şart. Desert Golfing'deki çözülemeyen procedural delik deneyimi bu riskin örneği (**K**).

## 5. EKLENEBİLİR — orta değer / koşullu
- **Arena ayarlarını bağla (S).** `Arena.settings.reducedMotion` açıkken: tanıtım uçuşu 0,6 sn olsun (bot zaten 0,6), pırıltı izi ve motes kapansın, kamera lerp'i anlık olsun. Titreşim açıksa vuruşta `navigator.vibrate(10)`, düşüşte `[20,40,20]` (yalnız Android; iOS yok sayar). Risk düşük. XAG 107/108 (**K**).
- **Nişan yardımı seviyesi (S-M).** Ayarlarda "Önizleme: kısa / ilk sekme / yok" seçeneği; şu anki varsayılan "ilk sekme". Çizgisiz modda bir yıldız bonusu ya da rozet eklenebilir. Uzmanlara zorluk, yeni başlayanlara güven sağlar. Kanıt: XAG 108 (mekanik bazında zorluk) **K**; Golfie/Golf Mini çizginin rolü üzerine **K**.
- **İkinci parkur: "Gün Batımı" ayna/değiştirici seti (M-L).** Mevcut 12 deliğin dönüştürülmüş versiyonlarıyla, 4.5'teki altyapıyı kullanarak 12 yeni delik. Ayrı kayıt anahtarında tutulmalı (`arena.periGolf.best2`) ki eski kayıt bozulmasın. İçerik süresini kabaca ikiye katlar (**T**). Önce 4.5 yapılmalı.
- **Telefon kadrajı (S).** Portre modda (`aspect<1`) kamera pitch'ini biraz artır ya da hedefi tee'nin 0,5 m önüne al; böylece top yakın duvarın arkasında kalmaz ve ekranın alt yarısı israf olmaz. İlerleme noktaları 500 px altında gizlensin ya da `Delik 1/12` yeterli sayılsın.
- **Kestirme ipucu (S).** Bir delikte 3. denemeden sonra kestirme halkası biraz daha görünür parlasın (`SC_NEAR` büyüt). Keşfi ödüllendirir, kayıt etkisi yok.
- **İlk oyuncuyu doğrudan oyuna al (S, koşullu).** Poki rehberi ilk kez gelen oyuncu için başlık/seçim ekranını atlamayı öneriyor (**K**). Kayıt yoksa "Oyna" tek dokunuşla zaten oyunda; doğrudan delik 1 tanıtımına girmek ses başlatma için bir jest gerektirir. Yalnız portal sürümünde düşünülmeli.

## 6. EKLENMEMELİ
- **Gerçek offline PWA / service worker:** ayrı `sw.js` dosyası gerektirir, tek dosya kısıtını aşar. Yanlış yapılırsa (cache-first, sürümsüz) güncellemeleri kilitler.
- **Çevrimiçi skor tablosu, çok oyunculu, bulut kaydı:** sunucu/hesap kısıtını aşar.
- **Sonsuz rastgele delik üretimi:** çözülemeyen delik riski var (Desert Golfing örneği, **K**). Hayalet çizgi ve delik rekoru anlamını yitirir; bot doğrulaması zorlaşır.
- **Fizik sabitlerini değiştirmek (MU, G, delik yakalama hızı):** bütün `holeBest`/`ghost` kayıtlarını ve botun 14 vuruşluk referansını anlamsızlaştırır. Zorluk istenirse veriyle (yeni delikler, değiştiriciler) yapılmalı.
- **HUD'a yeni düğme:** telefonda üst satır 6 düğmeyle dolu (5×44 px + dil). Yeni işlevler pause menüsüne ya da Arena paneline gitmeli.
- **Daha fazla partikül, gölge kalitesi, post-processing:** Intel UHD hedefini zorlar. Mevcut 27-29 draw call iyi bir denge.
- **Reklam/mağaza, kozmetik top satışı:** ücretli servis ve veri toplama kısıtına aykırı.
- **Bilinen bir mini golf oyununun deliklerini, karakterini veya adını kopyalamak:** yasak. Tür mekaniği (değirmen, rampa, portal) serbest.

## 7. Düzeltilmeli
- s.3906-3922 blob SW ve s.17 data manifest: kaldır (§4.1).
- s.3600 iptal eşiği ile s.3589/s.3829 önizleme eşiği uyumsuz (§4.2).
- `b-restart-hud` sunk/result fazında aktif (§3.3) → faz koruması ekle.
- `restartHoleShort` ölü i18n anahtarı (s.1731, s.1760): ya kullan (telefonda etiket) ya da sil.
- s.18-20 Google Fonts (§4.4).
- README ve project-meta: bot 14 vuruş/20 yıldız. Kontroller tablosuna HUD restart ve iptal jestini ekle.
- Telefon ilerleme noktaları kesiliyor (ekran 05) → `@media (max-width:500px)` içinde gizle ya da daralt.
- Erişilebilirlik: güç yalnız renkli çubukla gösteriliyor. Ekran okuyucu için `aria-live` "Güç %40" (kısıtlı sıklıkla) ve iptal durumu duyurulabilir (**T**).
- Kestirme bot sonucunu çarpıtıyor: bot regresyon referansı olarak "kestirmesiz" bir mod (`?auto&nosc`) iyi olur. İnsan zorluğu ancak böyle ölçülür (**T**).

## 8. Önerilen ilk 3 iş
1. **Relay commit'lerinin hasarını onar (4.1 + 4.2 + 4.3, toplam S).** Bugün gelen üç değişiklikten biri hiç çalışmıyor (SW). Diğer ikisi gerçek UX hatası üretiyor: görünen vuruşun yutulması ve sunk sırasında kayıt tutarsızlığı. En ucuz ve en kesin kanıtlı iş bu. Bot ve kayıt etkilenmez. Doğrulama: aynı `run.cjs` senaryosu (20 px iptal, sunk+restart) ve `periGolfSim` botu.
2. **Google Fonts'u kaldır ve belgeleri güncelle (4.4 + §7, S).** Proje kısıtını (harici çağrı yok) ve gizliliği doğrudan düzeltir. README'deki ölçülmüş iddiaları gerçeğe çeker; "yeşil ≠ test edildi" ilkesine uyum sağlar.
3. **Günlük değiştiriciler (4.5, M).** En büyük oyun değeri: günlük seri sistemi zaten var, ama her gün aynı 12 delikten biri geliyor ve rüzgâr fark yaratmıyor. Değiştiriciler veriyle çalışıyor, botla doğrulanabiliyor ve kayıt şemasına dokunmuyor. İkinci parkur (§5) için de altyapı olur.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek fps ve yükleme süresi (Intel UHD, gerçek telefon) ölçülmedi. SwiftShader'da ~20 fps ve 12,6 sn yükleme, makine yükü ~70 altında alındı; anlamlı değil.
- İlk telefon koşusunda (DPR 2, dondurulmuş rAF ile ekran görüntüsü) oyun alanı kırmızı-kahve bir yüzeyle kaplı göründü. DPR 1 ile tekrarında (ekran 05) görüntü normaldi. Büyük olasılıkla çekim artefaktı, ama DPR 2 + Low tier gerçek cihazda kontrol edilmeli.
- İnsan oyuncu için zorluk eğrisi bilinmiyor. Bot sonucu kestirmeler yüzünden insanı temsil etmiyor. Kestirmesiz bot modu ya da gerçek oyuncu testi gerekli.
- Data-URL manifestin Chrome/Android'deki tam davranışı (yok sayılıyor mu, hata mı veriyor) ölçülmedi; tahmin "kurulabilir değil".
- GoatCounter (s.1489) "kullanıcı verisi toplanmaz" kısıtına uyuyor mu? GoatCounter çerezsiz, ama yine de harici bir çağrı. Kullanıcı kararı gerekiyor.
- Arena kit'in `autoPause` özelliği oyunu kendiliğinden duraklatıyor mu, yoksa oyunun dinlemesi mi gerekiyor? Kit kodu ayrıntılı okunmadı.
- gameaccessibilityguidelines.com ve poki.com oturum ağ izninde değildi; bu yüzden ikincil özetler kullanıldı.

## Kaynaklar
- Golfie incelemesi (yörünge önizlemesi ve riskli vuruş): https://www.superjumpmagazine.com/golfie-they-see-me-rollin/
- Minigolf Kingdom QoL geri bildirimi (zorluk sıçraması): https://forums.pixeltailgames.com/t/minigolf-kingdom-quality-of-life-feedback/35718
- Mulligan / cezalı yeniden başlatma tartışmaları: https://forums.pixeltailgames.com/t/restart-a-mini-golf-level-by-pressing-r-1-or-2-penalty/13559 , https://forums.pixeltailgames.com/t/adding-mulligans-to-reset-stroke-count-reset-hole/45403 , https://gamingtrend.com/reviews/may-i-have-a-mulligan-mini-golf-resort-review/
- Desert Golfing (procedural delik, çözülemezlik, sürtünmesiz akış): https://en.wikipedia.org/wiki/Desert_Golfing , https://www.tapsmart.com/features/classics-desert-golfing/
- Poki geliştirici rehberi (mobil, ilk oyuncu için başlık ekranını atla): https://developers.poki.com/guide/easy-access , https://sdk.poki.com/requirements
- Xbox Accessibility Guidelines 107 (girdi) / 108 (zorluk seçenekleri): https://learn.microsoft.com/gaming/accessibility/guidelines , https://learn.microsoft.com/vi-vn/gaming/accessibility/xbox-accessibility-guidelines/108
- Service worker blob/data URL reddi (WPT): https://searchfox.org/firefox-main/source/testing/web-platform/tests/connection-allowlist/tentative/service-worker.sub.https.window.js
- Google Fonts GDPR kararı (LG München I, 20.01.2022): https://thehackernews.com/2022/01/german-court-rules-websites-embedding.html , https://www.activemind.legal/guides/ruling-google-fonts/

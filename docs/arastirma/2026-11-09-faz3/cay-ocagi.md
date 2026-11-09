# Çay Ocağı — faz 3 araştırması

Kanıt etiketleri: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Repo `/home/user/cay-ocagi` @ 76ddc0c (git status temiz kaldı). Satır numaraları `index.html`'e göredir.
Ölçüm ortamı: headless Chromium + swiftshader, **makinenin yük ortalaması ~73 idi (4 çekirdek)**. Bu yüzden fps ve süre ölçümleri kullanılamaz. Denge verileri gerçek zamanlı oynanıştan değil, `caySim`/`cayBench` ile yapılan deterministik simülasyondan alındı.

## 1. Şu anki durum
- **D** Döngü: 60 Hz sabit adımlı `simStep` (2823). İçinde istasyonlar, spawn, masalar, martı, garson, çırak ve insanlar güncellenir. `frame` kare başına en fazla 14 adım koşar (4702-4720).
- **D** İlerleme: 7 günlük kampanya (`DAYS` 2150), her gün 180 sn. Hedef 1. günde 65, 7. günde 250. Sonra sonsuz vardiya geliyor: hedef her gün +35 artıyor, gelme aralığı en az 3,4 sn (`dayCfg` 2159). Günler arasında dükkân var (`UPG` 2164, toplam maliyet 860 altın).
- **D** İmza mekaniği "Müdavimler" (46626e3): 2. günden itibaren 7 isimli müşteri gelir. Her birinin "her zamanki" siparişi, 0-10 sevgi puanı ve sürpriz siparişi var (`REG`/`REGULARS` 2113-2130). Kayıt anahtarı `cayocagi.regulars`. v2 mekanikleri: vapur akını, çay tazeliği, tavla müdavimi, martı hırsızı, kusursuz kahve.
- **D** Kayıtlar: `arena.cay.settings`, `arena.cay.save` (v:1; `loadSave` 2384 sürümü ve `up` alanını kontrol ediyor), `arena.cay.best` (`life` alanı rütbe için) ve `cayocagi.regulars` (v:1). Eski `cay_prefs`/`cay_best` anahtarları bir kez taşınıyor (1847-1855).
- **D** Bot: `?auto&noassets` ile `cayBench(12,3)` → **12/12 galibiyet**. Hedefe oran 1.-3. günlerde ~1,8×, 7. günde 1,25×. Ortalama yıldız d1 3,0 … d7 1,5. Kapıdan dönen müşteri (walk-by) d1'de 3,7, d7'de **18,4**.
- **D** Sonsuz vardiya (`?auto&seed=11`, `caySim(3000)`): bot **9. günde 315/320 ile kaybediyor**. Gelir 6.-9. günlerde ~300'de sabit kalırken hedef 225 → 320'ye çıkıyor ve walk-by 12 → 24'e yükseliyor.
- **D** `?selftest` tek başına çalıştırınca 10 PASS, 1 FAIL veriyor ("regular asks for >= 2 refills: asked 0"). `?selftest&auto` ile 11/11 PASS. FAIL eski bir sorun: 46626e3 ve 49a2685'te de aynı sonuç çıkıyor.
- **D** i18n: `TXT.tr/en` (1945-2059). Eksik anahtar önce TR'ye, sonra anahtarın kendisine düşüyor. Dil `?lang`, ayarlar ya da `navigator.language` ile seçiliyor.
- **D** Mobil: dokunmatik dokunma, sürükle-kaydır ve iki parmakla yakınlaştırma var (4540-4571). Alt dock'ta tepsi + 5 istasyon. 390×844'te istasyon düğmesi 67×72, tepsi yuvası 44×44, yatay taşma yok (docW 390).
- **D** Ses: tamamı Web Audio sentezi (2964-3064), hicaz döngüsü 96 BPM. Performans: `PR` en fazla 1,5 (`?low`'da 1), `Arena.perf.attach` var (3681). Çizim çağrısı simülasyonda en fazla 28.

## 2. Güçlü yanlar (korunmalı)
- **D** Veri tablosuna dayalı denge (`PRICE/CUST/DAYS/UPG/TAVLA/GULL/REG`). Simülasyon ile görsel ayrı, tohum tekrarlanabilir. `cayBench` ve `?selftest` hızlı regresyon imkânı veriyor.
- **D** İlk deneyim iyi: tek tıkla 1. güne giriliyor, koç işaretleri gerçek eyleme göre ilerliyor (`coachState` 4024). Gün 2-7 her biri tek bir yenilik getiriyor (`nk/ni`).
- **D** Bilgi okunabilirliği güçlü: sabır halkası son %25'te kızarıp titriyor, çay tazelik çubuğu ve gri ton var, kahvede kusursuz pencere için altın halka (4236-4244) var, son 20 sn'de saat kırmızıya dönüyor.
- **D** Başarısız gün affedici: kazanılan altın korunuyor ve tekrar deneme dükkândan geçiyor (2369-2373). Yerel ve kültürel doku özgün: Müdavimler, kaynakları belirtilmiş bilgi kartları, Van kedisi.
- **D** Günlük meydan okuma kampanya kaydına dokunmuyor (2301-2319). Hiçbir test bayrağı oyuncu kaydına yazmıyor (`FLAG.nosave` 1860).

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Düşük kalitede ekran kartları okunmuyor (D, hata).** `body.low .glass { background:#2a160d }` (499-503) özgüllükte `.card` gradyanını (1178-1185) eziyor. Bu yüzden Low modda kart zemini koyu kahve oluyor, ama yazılar hâlâ koyu: `h2` #2a160d (kontrast 1:1), `p` #54311e (≈1,4:1).
   - Ölçüm: `getComputedStyle` normalde `bg rgba(0,0,0,0)` + krem gradyan, `?low`'da `rgb(42,22,13)`, gradyan yok.
   - Ekran görüntüsünde "Vardiya bitti" başlığı ve açıklama metni görünmüyor (`_cay-ocagi/auto_late.png`). Başlıktaki slogan da okunmuyor (`phone_title.png`).
   - Low, Ayarlar'da seçilebilen ve zayıf GPU'ya önerilen mod. Hedef kitle tam olarak bu oyuncular.
2. **Sonsuz vardiya bir kapasite duvarında bitiyor (D bot / T insan).** 6 masa ve 860 altınlık dükkânın tamamı alındıktan sonra gelir ~300'de kalıyor, hedef ise her gün +35 artıyor. Bot 9. günde düştü. Gameover kartı "Dükkândaki geliştirmeler işine yarar" diyor ama dükkân zaten bitmiş. Yani tekrar dene döngüsü yeteneğe değil sınırlı kapasiteye takılıyor.
3. **Altın, dükkân bittikten sonra anlamsızlaşıyor (D hesap).** Botun toplam kazancı 7. güne kadar ~1600+ (9. günde toplam 2270). 860'lık dükkân ~5.-6. günde tükeniyor. Sonra altın yalnız rütbeye yarıyor, rütbe tavanı da 2500.
4. **7. günde ani zorluk sıçraması ve görünmeyen kayıp (D).** Walk-by 10,4'ten 18,4'e çıkıyor, yıldız 2,2'den 1,5'e düşüyor. Masa doluyken dönen müşteri yalnız küçük bir "Masa yok" float yazısıyla gösteriliyor (2810). 1.-3. günler bot için 3 yıldızla ~1,8× hedef, yani başlangıç kolay ve sonra eğri dikleşiyor.
5. **Martı isabet alanı ve rölenin bıraktığı ölü kod (D kod / T etki).** `pickAt` (4522-4531), 80 px ekran yarıçapını raycast'ten **önce** kontrol ediyor. Bu yüzden martının yakınındaki bir masaya ya da istasyona yapılan tık martıya gidebilir.
   - Telefonda dikey ekranda martı ekran dışında kalıyor (işaret x=356'ya sıkışık). Tam yarıçapı ölçtüğüm 3 tıkta yanlış hedef görülmedi.
   - Masaüstünde ölçülemedi.
   - `document.body.classList.add('arena-shake')` için CSS yok (3770-3774), yani ölü kod.
6. **Dock'taki kahve halkası dünya halkasıyla çelişiyor (D).** Dock halkası ilk 2,6 sn yeşil, son 1 sn kırmızı (4157-4170). Dünya halkası ise ilk 1 sn'de altın, yani "kusursuz" (4241). Aynı pencere iki farklı anlamla gösteriliyor. Ayrıca dock halkası pot hazır olmasa da her karede `clearRect` çağırıyor; küçük bir maliyet.
7. **Telefonda başlık kartı ve HUD (D).** 390×844'te "Ayarlar" düğmesi 836. pikselde, kaydırmadan görünmüyor. 4 maddelik nasıl-oynanır listesi klavye kısayollarını (P/Esc/M/X/L) dokunmatikte de gösteriyor. Oyun içinde üst HUD 127 px (iki satır) + dock 164 px, ekranın ~%34'ünü kaplıyor.
8. **`?selftest` tek başına FAIL veriyor (D).** 7. test botu varsayıyor ama `FLAG.auto` açmıyor (4802). README yalnız `?selftest` yazıyor.
9. **Oyunun toast'ları ekran okuyucuya ulaşmıyor (D).** `#toasts`'ta `aria-live` yok. `Arena.announce` var ama oyun onu kullanmıyor.
10. **Varlık yükleme yavaş ve kırılgan (D/T).** Yüklü makinede 18-21 sn sürdü ve bir koşuda 15 sn yarışı (4826) kaybedildi (`G.assets=[]`, prosedürel görünüm). Sonradan gelen modeller hiç uygulanmıyor. Gerçek donanımda ölçülmedi (T).

## 4. EKLENMELİ — yüksek değer
**4.1 Low-mod kart kontrast düzeltmesi + kontrast kapısı**
- Ne: Kartlar düşük kalitede de krem zemini korusun.
- Neden: Bölüm 3'teki 1. madde; okunmayan başlıklar kritik bir hata.
- Nasıl: `body.low .card { background: linear-gradient(180deg,#fffdf9,#faf4e8); }` ekle, ya da kuralı `body.low .glass:not(.card)` yap. Smoke testine Low modda `.card h2` ile zeminin kontrastının ≥4.5 olduğunu kontrol eden bir adım ekle.
- Maliyet: **S**. Risk: yok. Kanıt: D.

**4.2 Sonsuz vardiyayı kapasite duvarından kurtarmak**
- Ne: Hedef artışını gelir tavanına bağla ve kaybı yumuşat.
- Neden: Diner Dash'in "Endless Shift"i bir hayatta kalma modu; amaç dayanabildiğin kadar dayanmak (K). Bizdeki sınırlı kapasite tasarımı, yetenekle aşılamayan bir duvar ve anlamsız bir "dükkâna git" tekrarı üretiyor (D).
- Nasıl (`dayCfg` 2159):
  - (a) Hedefi doğrusal +35 yerine azalan artışla büyüt, örn. `250 + 35·√k·…`, ya da tavanı walk-by'a göre ayarla.
  - (b) Sonsuzda gün kaybı = koşunun bitişi olsun. Kart "N. güne ulaştın, rekor" desin ve "dükkân ve tekrar" yerine "yeni sonsuz koşu" sunsun.
  - (c) Sonsuza özel 1-2 ek dükkân kalemi ekle; bu da 4.3'e bağlanıyor.
  - Bot: `cayBench` sonsuz için en az 12 gün koşsun ve sonuç not edilsin.
- Maliyet: **M**. Risk: kayıt (`endless` bayrağı aynı kalmalı) ve bot.

**4.3 Dükkân sonrası altın için anlamlı bir hedef (kozmetik/çay ocağı süsü)**
- Ne: Tükenen dükkândan sonra altını kozmetik ve küçük konfor kalemlerine harcama imkânı. Örnekler: kilim deseni, fener rengi, ikinci kedi minderi, müdavim fotoğraf duvarı.
- Neden: Altın ~6. günden sonra işlevsiz kalıyor (D). Tür örnekleri restoranı yıldızdan yıldıza büyütmeyi uzun vadeli hedef olarak kullanıyor (K, CSD).
- Nasıl: `UPG` tablosuna `cosmetic:true` kalemleri ekle; `G.up`'a yeni alan açıp `Object.assign` ile geriye uyumlu tut (2395 zaten varsayılanlarla birleştiriyor). Görselde mevcut Merger yeniden kurulmasın; yalnız malzeme rengi ya da instans görünürlüğü değişsin.
- Maliyet: **M**. Risk: çizim çağrısı ≤34 bütçesi; bot bu kalemleri almamalı.

**4.4 "Sakin mod" / zaman yardımı (erişilebilirlik)**
- Ne: Ayarlarda "Sabır ×1,5" ya da "müşteriler kızmasın" seçeneği; yıldız tavanı 2 olsun.
- Neden: Overcooked AYCE'nin Assist Mode'u süre uzatma ve sipariş zaman aşımını kapatma sunuyor (K). CSD3'ün Chill Mode'u sabrı sonsuz yapıyor ama madalyayı gümüşle sınırlıyor (K). GAG oyun hızı seçeneğini temel düzey önlem sayıyor (K). Mevcut 1×/2×/3× yalnız hızlandırıyor, yavaşlatma yok (4429).
- Nasıl: `SET.assist`, `spawnParty` içinde `maxP` çarpanı (2498); `ratingStars`'ta assist açıkken 3 yıldız kapalı. Günlük meydan okumada assist kapalı ya da ayrı işaretli olsun. Bot `FLAG.auto` ile assist'i yok saysın.
- Maliyet: **S-M**. Risk: düşük; kayıt uyumu tamam (yeni ayar alanı varsayılanla birleşiyor).

**4.5 Kayıp müşteriyi görünür kılmak ve 7. gün eğrisi**
- Ne: Walk-by sayısını gün özetine yaz ("kapıdan dönen: N") ve kartta "Ek masa" önerisi göster. 7. günün `gap` değerini 4,9'dan ~5,1'e yumuşat ya da `regular` ağırlığını düşür.
- Neden: d7 walk-by 18,4, yıldız 1,5 (D). Tür incelemelerinde yeni öğeyle gelen ani sıçrama şikâyet konusu (K, düşük güvenilirlikli kaynak).
- Nasıl: Veri `rec.blocked` olarak zaten var (2348); özette yalnız bir `rowk` satırı eksik.
- Maliyet: **S**. Risk: denge değişirse `cayBench 90` yeniden koşulmalı.

## 5. EKLENEBİLİR — orta değer / koşullu
- **Müdavim hikâye kırıntıları** (S-M): 5 kalbe ulaşınca kısa bir TR/EN satır ya da Müdavimler panelinde bir not açılsın. İmza mekaniğini derinleştirir, yeni sistem eklemez. Koşul: metin iki dilde ve yerel kültüre uygun olmalı (T).
- **Dokunmatikte nasıl-oynanır listesini sadeleştirme** (S): `(pointer:coarse)` iken 4. maddeyi gizle ya da "Sürükle/Kıstır" yap. Başlık kartı kısalır, "Ayarlar" görünür olur (D, Bölüm 3 madde 7).
- **Telefonda HUD'u tek satıra sığdırma** (S-M): Hız, ses ve dil düğmeleri Ayarlar'a gitsin, telefonda yalnız duraklat ve dişli kalsın. Oyun alanı ~%10 büyür (T).
- **Toast'ları ekran okuyucuya iletme** (S): `toast()` içinde `Arena.announce(msg)` çağır, ya da `#toasts`'a `aria-live="polite"` ekle. Gereksiz tekrarı önlemek için yalnız `good/bad` türleri gitsin.
- **"Bugünün siparişi" bilgi kartı rotasyonu** (S): 6 bilgi kartı var ve her gün dönüyor. Kaynaklı yeni bilgiler eklenebilir (vapur, simitçi). Koşul: her biri kaynak URL'li olmalı (CREDITS.md düzeni).
- **Kahve halkalarını tek dile indirme** (S): Dock halkası da ilk 1 sn'de altın olsun ve yalnız pot hazırken çizilsin.

## 6. EKLENMEMELİ
- **Çevrimiçi skor tablosu / hesap / bulut kaydı:** Kısıtı aşar (sunucu, hesap, kullanıcı verisi). Paylaşım kartı ve günlük seri zaten bu ihtiyacı karşılıyor.
- **Reklam, ödüllü video, portal SDK'sı:** Harici ağ çağrısı demek ve kısıtı aşar. Oyun "ücretsiz kalır" vaadi veriyor.
- **Yeni istasyon ya da ürün eklemek (ör. 6. istasyon "kumpir"):** Dock telefonda zaten tam genişlikte (5×67 px). 6. düğme 44 px altına düşer (D ölçüm). Bot karar ağacı (2846) ve dengenin tamamı yeniden ayarlanmak zorunda kalır. Getirisi düşük, riski yüksek.
- **Ekran sarsıntısı / tam ekran flaş efektleri** (rölenin `arena-shake` niyeti): Hareket hassasiyeti ve azaltılmış-hareket ayarıyla çelişiyor. Martı kovma zaten tüy patlaması, ses ve toast ile geri bildirim veriyor.
- **Çok oyunculu ya da co-op (Overcooked tarzı):** Kısıtı aşar (ağ) ve aynı ekranda tek garson tasarımını bozar.
- **Prosedürel sonsuz bölüm üretici / yeni harita:** Tek dosya boyutu (281 KB) ve çizim çağrısı bütçesi zorlanır. Değer 4.2'deki ayar ile daha ucuza alınıyor.
- **Gerçek bir oyunun adını, karakterini ya da "Flo" benzeri bir maskotu kullanmak:** Brief'e aykırı. Mekanik ilke serbest, kopya yasak.

## 7. Düzeltilmeli
- **Hata:** Low modda kart kontrastı (4.1), en öncelikli iş.
- **Hata/test:** `selfTest` 7. adımda `FLAG.auto` geçici olarak açılmalı (4802) ya da README `?selftest&auto` yazmalı. Şu an `?selftest` tek başına FAIL veriyor.
- **Hata adayı:** `pickAt` martı yarıçapı (4524-4531) raycast'ten sonra ya da yalnız raycast boş kalınca uygulanmalı. Böylece masa/istasyon tıkları çalınmaz. Ölü `arena-shake` satırları silinmeli.
- **Cila:** Dock kahve halkası altın pencereyle uyumlu olmalı ve yalnız hazır pot varken çizilmeli (4157-4170).
- **Cila:** Gameover kartında `bestLine` "Henüz rekor yok" yazarken aynı kartta "Yeni rekor!" çıkıyor. Bu `nosave` testine özgü bir durum (D: auto_late.png); gerçek kayıtta tutarlı olmalı (T).
- **Cila:** Sonsuz vardiyada gameover metni "geliştirmeler işine yarar" diyor; dükkân tamamen alınmışsa farklı bir metin gerekli.
- **Erişilebilirlik:** Toast'lar ekran okuyucuya iletilmiyor. `.tray-dot.filled` sonsuz `dotPulse` animasyonu kullanıyor; kit'in azaltılmış-hareket kuralı bunu durduruyor, kontrol edildi (196).
- **Performans:** Model yüklemesi ~15 sn yarışını kaybedince geç gelen modeller atılıyor. Yükleme `plain()` + `P.push(...arr)` ile CPU'ya ağır (4598-4611; T). Gerçek Intel UHD'de ölçülmeli.

## 8. Önerilen ilk 3 iş
1. **Low-mod kart kontrastı (4.1)**, S.
   - Gerekçe: Doğrulanmış, kullanıcıya görünen ve kritik bir okunabilirlik hatası. Hem de tam olarak zayıf donanım kullanan hedef kitlede.
   - Tek CSS satırı, risk yok.
   - Doğrulama: Low + High'da `getComputedStyle` kontrast kontrolü ve ekran görüntüsü.
2. **Sonsuz vardiya duvarı + gameover metni (4.2) ve 7. gün walk-by görünürlüğü (4.5)**, M.
   - Gerekçe: Bot verisi uzun vadeli oynanışın 9. günde yetenekten bağımsız bir duvara çarptığını gösteriyor.
   - Tekrar oynanabilirliği en çok etkileyen tek ayar bu. `dayCfg` ile özet satırı küçük değişiklikler.
   - Kabul ölçütü: `cayBench 90` kampanya galibiyeti ≥ 84/90 kalmalı, sonsuzda ortalama ulaşılan gün raporlanmalı.
3. **Sakin mod / sabır yardımı (4.4) + selftest düzeltmesi**, S-M.
   - Gerekçe: Türün kabul görmüş erişilebilirlik desenini (Assist/Chill) ekliyor ve oyunun "rahat çay ocağı" tonuna uyuyor.
   - Yıldız tavanı sayesinde kampanya dengesi korunuyor.
   - Selftest düzeltmesi, bu ve sonraki değişiklikler için regresyon kapısını güvenilir kılıyor.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek fps ve yükleme süresi ölçülemedi; makine yükü 73/4 çekirdekti. README'deki "60 fps, 31 çağrı" iddiası bu turda yeniden ölçülmedi.
- Martı 80 px yarıçapının masaüstünde (1280×720) masa/istasyon tıklarını çalıp çalmadığı doğrulanmadı. Telefonda 3 tıkta sorun görülmedi; bunun nedeni martının ekran dışında olması.
- İnsan oyuncunun sonsuz vardiyada botun 9. gününü geçip geçemeyeceği bilinmiyor; bot tepkisi 0,55-0,95 sn. Duvarın yapısal olduğu (gelir tavanı ~300) D, insanlar için kesin gün sayısı T.
- `?auto` canlı çalıştırması yükten dolayı yalnız ~1 sn simüle edildi. Bot ilerlemesi `caySim` ve `cayBench` ile doğrulandı, gerçek zamanlı değil.
- Kaynak araştırmasında gamedesignskills.com ağ kısıtı nedeniyle açılamadı; içeriği yalnız arama özetinden alındı. Poki/CrazyGames boyut sınırları üçüncü taraf kaynaklardan geliyor.
- Ekran görüntüleri (tümü `?low` ya da `?noassets`): `_cay-ocagi/phone_title.png`, `_cay-ocagi/phone_play.png`, `_cay-ocagi/auto_late.png`.

## Kaynaklar
- Diner Dash, Endless Shift hayatta kalma modu: https://en.wikipedia.org/wiki/Diner_Dash
- Zaman yönetimi türü, seviye + hedef + süre yapısı: https://wikiwand.com/en/articles/Time_management_(video_game_genre)
- Gündelik oyun tasarımı, zorluk eğrisi, sonsuz ve aşamalı seviyeler (arama özeti): https://gamedesignskills.com/game-design/casual/
- Grub Burgers / DinerTown Tycoon analizi, uzun aralıklı başarısızlık eleştirisi: https://www.gamedeveloper.com/game-platforms/analysis-grub-burgers---i-dinertown-tycoon-i-s-story
- Overcooked! All You Can Eat Assist Mode: https://blog.playstation.com/?p=340908 , https://destructoid.com/?p=255244 , https://gamerant.com/overcooked-all-you-can-eat-assist-mode-accessibility-options/
- Cook, Serve, Delicious! 3 Chill Mode ve gümüş tavanı: https://pcgamer.com/cook-serve-delicious-3-review , https://www.thexboxhub.com/cook-serve-delicious-3-review/ , https://vaporlens.app/app/1000030/cook_serve_delicious_3
- Game Accessibility Guidelines, oyun hızı ve zaman baskısı: https://gameaccessibilityguidelines.com/?p=3102 , https://gameaccessibilityguidelines.com/?p=21
- CrazyGames teknik gereksinimler (dokunmatik, 4 GB RAM cihaz, ilk kare): https://docs.crazygames.com/requirements/technical/ , https://docs.crazygames.com/resources/getting-to-the-first-frame/
- Poki gereksinimleri (mobil ve tablet desteği): https://sdk.poki.com/requirements

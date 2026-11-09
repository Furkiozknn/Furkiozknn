# Ebru — faz 3 araştırması

Repo `/home/user/ebru`, dal `claude/cloud-session-research-analysis-dufc2b`, HEAD `b2101d2`, `index.html` 4119 satır.
Kanıt etiketleri: **D** = doğruladım/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak.
Ölçüm notu: makine paylaşımlıydı (load average 27-78, 4 çekirdek), headless Chromium + swiftshader. FPS ve yükleme süreleri bu yüzden anlamsız. Yalnız hata sayısı, durum, düzen ve göreli sayılar kullanılabilir.
Geçici dosyalar: `_ebru/probe.cjs`, `_ebru/probe-*.json`, ekran görüntüleri `_ebru/02-lesson1-desk.png`, `03-title-phone.png`, `04-lesson-phone.png`, `05-nefes-phone.png`.

## 1. Şu anki durum
- **Çekirdek:** kapalı biçimli "mathematical marbling" simülasyonu (`Marble`, satır 2345-2468). Damla eski noktaları itiyor, biz ve tarak 8 birimlik sabit adımlarla `exp` düşüşüyle çekiyor (`StrokeRunner`, 2472-2516). Belirlenimci, oyuncu, bot ve hedef aynı kodu kullanıyor. **D** (kod)
- **İlerleme:** 3 bölümde 18 ders (2571-2629). Her hedef bir vuruş tarifinin yeniden oynatılması, par = tarifteki vuruş sayısı + 1 (2631). Yıldızlar: %80 çözüm, %90, par içinde (3566). Mühür: %90 + par + ipucusuz (3572). Derece: 6 mühürde kalfa, 12 mühürde usta (3621). Dersin kilidi, bir önceki derste yıldız alınınca açılıyor (3667). **D**
- **Puanlama:** 16×12 kaba renk ızgarası + 40×30 ızgarada pigment başına alan/ağırlık merkezi (`matchScore` 2666). Ustanın eleştirisi en kötü iki sapmayı metinle söylüyor (`critique` 2709, HUD 3739-3740). **D**
- **İmza mekaniği "Tek Nefes"** (`12061dc`): 60 sn, 4 nefes, nefes başına bir damla ve bir çekiş, geri alma yok. Baskı `arena.ebru.duvar.v1` anahtarına yazılıyor, son 12 baskı 160×120 JPEG (1999-2012, 3381-3484). Hedef ya da puan yok, yalnız nefes/saniye/damla istatistiği (3466). **D**
- **Arena-kit:** dinamik pixel ratio (2745-2746), günlük meydan okuma (3958), paylaşım yalnız metin (3465, 3577-3584, 3951), rozetler (3961), erişilebilirlik paneli Ayarlar içinden (3950). Günlük ders, 18 sabit dersten biri: `seed % 18`. **D**
- **Kayıt:** `arena.ebru.settings|save|best|gallery|bound|duvar.v1`. `load()` varsayılanla birleştiriyor, v1 kayıtlar yükleniyor (1979, 1985-1993), her erişim try/catch içinde. `?auto`/`?nosave` yazmıyor (1980). **D**
- **Bot `?auto`:** ağır yük altında `ebruSim` ile 134 sn'de 2 ders bitti. Ders 1: %89,6, 2★, mühür yok. Ders 2: %95,6, 3★, mühür var. 0 JS hatası (`probe-bot.json`). **D**
- **Yükleme:** masaüstü 1280×720'de 0 konsol hatası, oyun içinde 17 çağrı ve 5400 üçgen (README'deki 14-18 ve 5,4k ile tutarlı). Telefon 390×844'te 0 hata, yatay taşma yok (`docW` 390). **D**
- **Son relay commit'leri** (`d773d3d` pinch, `90d889a` görünürlük; gemini flash-lite, testsiz) önceki yapıyı bozmamış, ama pinch commit'i başlığındaki "deadzone"u gerçekte eklemiyor (bkz. §3.1). **D**
- **Belgeler:** README Tek Nefes'ten, günlük meydan okumadan ve galeri duvarından hiç bahsetmiyor. `project-meta.json` da bahsetmiyor (grep sonucu boş). **D**

## 2. Güçlü yanlar (korunmalı)
- Her hedef bir tarif ve her ders çözülebilir. İpucu hayaleti de, bot da aynı tarifi kullanıyor (2540, 3346, 3999-4001). Bu tasarım günlük varyant gibi yeni içerik için de çok değerli. **D**
- Renkler hiç karışmıyor, poligon başına renk var. Performans bütçesi kendini ayarlıyor: nokta sayısı arttıkça örnekleme kabalaşıyor (2424-2425). Vuruş sırasında boya 30 Hz'de rasterleşiyor, oda 60 Hz'de kalıyor (4075). **D**
- Ustanın eleştirisi metinle konuşuyor ("Daha çok Aşı kırmızısı ekle, sol üstte"). Bu, renk körleri için de değerli bir kanal. **D**
- Kültürel doğruluk: UNESCO kaynaklı bilgiler (1941-1948), gerçek desen adları, gerçek pigment adları. **D**
- İlk deneyim: "Oyna" doğrudan ilk çözülmemiş derse götürüyor (3651). Ders 1-3'te ilk vuruşun hayaleti bedava (3681). %80'de kenar ışığı ve çan çalıyor (3227). **D**
- Telefon düzeni dikey: HUD üstte, araç tepsisi ve renkler altta, hedef önizlemesi döndürülmüş (3716-3720). Ekran görüntüsünde 44 px altında dokunma hedefi yok (`small: []`). **D**
- Ses tümüyle sentez: damla perdesi boyuta, ıslık hıza bağlı. Hicaz ney + kanun müziği var, gizli sekmede ses askıya alınıyor. **D**

## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla)
1. **Pinch başlangıcı boya döküyor ve vuruş sayıyor (HATA, D).** İlk parmak `pointerdown` olur olmaz `startStroke` çağrılıyor (3848). Fırça ya da büyük damla `begin()` içinde hemen damla bırakıyor (2476-2479). İkinci parmak geldiğinde `endStroke` bu damlayı vuruş olarak işliyor (3839).
   - Adımlar: telefonda ders 1'i aç, iki parmakla yakınlaştır.
   - Ölçülen (`probe-phone.json`): `strokes 0→1, polys 0→1, undo 0→1`. Par sayacı 1 artıyor. Geri alınabiliyor ama "par içinde" ve mühür için gizli bir ceza.
   - **Tek Nefes'te daha kötü:** `nefes {drop:false, started:false}` → `{drop:true, drops:1, started:true}`. Pinch o nefesin damla hakkını yiyor ve 60 sn'lik saati başlatıyor. Tek Nefes'te geri alma yok.
2. **Paylaşım yalnız metin; kâğıdı dışa aktarmanın yolu yok (D).** Oyunun en paylaşılabilir ürünü bitmiş kâğıt. Ama galeri 256×192 (3531), duvar 160×120 (3457) ve "indir/paylaş" düğmesi yok. `Arena.share` yalnız metin gönderiyor ("One Breath · 4/4 breaths · 47 s"). Rakip marbling uygulamalarının temel özelliği fotoğraf arşivine kaydetmek ve paylaşmak (**K**: Ink Marbling, Ebru iOS).
3. **Günlük meydan okuma 18 sabit dersten biri (D, 3958).** Aynı ders birkaç haftada bir tekrar geliyor (T: 18 olasılık, tekrar beklentisi kısa), oyuncu cevabı zaten biliyor. Yeni oyuncuya da kilitli bir çiçek dersi düşebiliyor: bu bilinçli, notu var (2059).
4. **Tek Nefes'in hedefi ya da ölçütü yok (D, 3450-3467).** Yalnız süre, nefes ve damla sayılıyor. "Bir nefes daha" için iç motivasyon dışında bir neden yok. Duvara her baskıya usta mührü basılıyor (3461), bu da derslerdeki mührün anlamını sulandırıyor (T).
5. **Ana menü kalabalık ve iki "galeri" var (D, ekran 03).** Telefonda 8 düğme alt alta diziliyor. Panel `scrollH 944 > clientH 808`, yani bilgi satırı ve altbilgi kaydırmadan görünmüyor. "Galeri" ile "Galeri duvarı" isim olarak karışıyor. "Günün Meydan Okuması (Seri 0 gün · en iyi 0)" iki satıra kırılıyor.
6. **Masaüstünde koç kartı ilk vuruşun başlangıcını örtüyor (D, ekran 02).** Ders 1'de hayaletin başlangıç halkası (sol üst) kartın sağ kenarının altında kalıyor. Pencere ışığı tepsinin sol alt köşesini parlatıyor: açık pigmentlerin (üstübeç beyazı, sarı toprak) okunması zorlaşabilir (T).
7. **Renk yalnız renkle ayırt ediliyor (D).** Renk düğmelerinde ad, desen ya da sembol yok, ad yalnız `title`/`aria-label`'da (3726). Ebru mavisi #1E6FB8 / Lahor çividi #2C4A8A, Aşı kırmızısı / Turuncu / Gül kurusu gibi çiftler, renk görme farkı olan oyuncu için karışır (T). Seçili rengin adı tepside görünmüyor. **K**: GAG temel düzey "yalnız renkle bilgi verme", XAG 103.
8. **Erken "Kâğıdı yatır" bütün işi yakıyor (D, 3489-3491, 3566).** %80'in altında da onaysız basılabiliyor. Sonuç "Henüz değil" oluyor ve "Tekrar dene" boş tekneden başlatıyor. Telefonda düğme büyük ve renk düğmelerinin hemen yanında (ekran 04).
9. **Ders 1'de mühür, tarifi titremeyle tekrarlayan bota bile ulaşılmaz (D, %89,6).** Fırça damlalarının boyu başlangıç noktasının hash'inden türetiliyor (2477, 2338). Battal "rastgele serpinti"ye %90 uymayı istiyor, yani beceriden çok şansa kalıyor (T). README'ye göre bot 12/18 mühür alıyor, 6 dersin mührüne mükemmel tarif bile yetmiyor.
10. **Kopya kod (D):** görünürlükte ses askıya alma iki kez yapılıyor: arena `pause/resume` (3965-3966) ve relay'in eklediği handler (3896-3900). Zararsız, ama ikisi birbirine ayrık mantıklar kurar (T).
11. **Yanlış "Three.js yüklenemedi" mesajı (T, 1955).** 20 sn'de `__loaded` yoksa bu mesaj çıkıyor. Yük altında yükleme 53 sn sürdü (D, `loadMs`). Yavaş bağlantıda modül hâlâ inerken oyuncu "bağlantını kontrol et" görür. Hedefler kurulmaya başlayınca metin düzeliyor (4107).
12. **Belge açığı (D):** README "How to play", "Persistence", "URL flags" bölümlerinde Tek Nefes, günlük, duvar ve `arena.ebru.duvar.v1` yok. `?d=YYYYMMDD` bayrağı da yazılmamış.
13. **Smoke testi yalnız yüklemeyi kontrol ediyor (D, `tools/smoke.mjs`).** Testsiz relay commit'leri (pinch, görünürlük) oynanışı bozabiliyor ve CI bunu yakalamıyor. §3.1 tam böyle bir gerilemeydi.

## 4. EKLENMELİ — yüksek değer
**4.1 Dokunmada "niyet bekleme" ile pinch hatasının kökten düzeltilmesi.**
- Ne: Dokunma ile başlayan vuruş hemen değil, ya ~6 px hareket ya da ~120 ms tek parmak bekleme sonrası başlasın. Bu sürede ikinci parmak gelirse vuruş hiç başlamasın, pinch olsun.
- Neden: §3.1. Tek Nefes'te nefes hakkı yanıyor, derslerde par/mühür cezası var.
- Nasıl:
  - `pointerdown`'da `e.pointerType==='touch'` ise `pending={id,x,y,t}` sakla.
  - `pointermove` ya da `tick` içinde koşul sağlanınca `startStroke(pending.x,pending.y)` çağır. Damla, orijinal dokunma noktasına düşsün; belirlenimcilik korunur.
  - Fare ve kalem bugünkü gibi anında başlasın.
  - Bot `startStroke`'u doğrudan çağırıyor, etkilenmez.
- Maliyet **S**. Risk düşük: dokunma gecikmesi algısı; 120 ms ve ilk damlada titreşim/ses ile maskelenir.
- Kanıt **D** (probe) + **K** (çizim uygulamalarında tek parmak çizer, iki parmak yakınlaştırır: Notewise; Android palm rejection, yanlış dokunmayı geri alabilmek).

**4.2 Kâğıdı resim olarak kaydet / paylaş.**
- Ne: Sonuç kartında, baskı ekranında ve galeri/duvarda "Kaydet" düğmesi.
- Nasıl:
  - Görüntüyü `paintToCanvas(1024,768)` ile al (zaten var, 3004 civarı). İstenirse `bindCover` kapağı ya da kâğıt kenarı + küçük "Ebru · Ders 14 · %92" künyesi eklensin.
  - `canvas.toBlob` → `navigator.canShare({files})` varsa `navigator.share({files,text})`, yoksa `<a download>`.
  - ARENA-KIT bloğu değişmez; oyun kendi kodunda yapar.
- Neden: oyunun asıl ürünü görsel. Metin paylaşımı bu türde zayıf. Ağ çağrısı yok, veri toplanmıyor, kullanıcı başlatıyor.
- Maliyet **S**. Risk: iOS Safari dosya paylaşımı sürüme bağlı, indirmeye düşer. Bellek: bir kerelik 1024×768 okuma, sorun değil.
- Kanıt **D** (dışa aktarma yolu yok, grep) + **K** (MDN `canShare` / web.dev share-files; Ink Marbling ve Ebru iOS'ta "Photos'a kaydet").

**4.3 Tohumlu günlük desen (tarif varyantı).**
- Ne: Günün dersi `seed`'den türetilmiş bir tarif olsun: şablon ders × renk permütasyonu × ayna (x/y) × küçük öteleme.
- Nasıl:
  - `daily.rng` ile `LESSONS[k]`'nin vuruşlarını kopyala.
  - Renkleri o dersin `colours` kümesinden permütele et, noktaları `SW-x`/`SH-y` ile aynala.
  - `{...L, strokes, cols, par, target:null, index:L.index, daily:true}` nesnesi kur, `startLesson` buna izin verecek şekilde küçük bir dal alsın.
  - Hedef hâlâ tarifin yeniden oynatılması: çözülebilirlik, ipucu hayaleti ve bot korunur.
  - PROG'a yazılmıyor (bugünkü gibi), eski kayıtlara dokunmaz.
- Neden: herkes aynı günü oynar ama cevabı ezberden bilmez. Seri anlam kazanır.
- Maliyet **M**. Risk: aynalanmış flower derslerde sap aşağıda kalır (yalnız x aynası ya da yalnız renk permütasyonu ile sınırla); hedef üretimi ~1 kare.
- Kanıt **D** (3958, 2631) + **K** (Wordle: tek günlük ortak bulmaca, kıtlık ve ortak konuşma; hafif seri).

**4.4 Renk adları ve renk körü desteği.**
- Ne:
  - Seçili rengin adı tepside küçük bir etiket olsun (örn. "Lahor çividi").
  - Hedef önizlemesinin altında "Bu desende: ● Ebru mavisi ● Aşı kırmızısı" anahtarı.
  - Renk düğmelerine ince bir sembol/numara katmanı (1-12), Arena "yüksek karşıtlık" açıkken ya da her zaman.
- Neden: oyun renk eşleştirme üstüne kurulu, §3.7.
- Nasıl: `buildSwatches` (3722) ve `drawPreview` (3716) içinde DOM/CSS. Simülasyona dokunmaz.
- Maliyet **S**. Risk: telefon tepsisinde yer (12 renk tek satırda); etiket renk satırının üstüne.
- Kanıt **K** (Game Accessibility Guidelines temel düzey; XAG 103; Unity accessibility).

## 5. EKLENEBİLİR — orta değer / koşullu
- **Tek Nefes'e günlük kısıt ("Günün nefesi") (M):** seed'den 3 pigment + bir zorunlu araç (ör. yalnız tarak). Puan yok, duvarda gün etiketi. Hedefsiz modun ifade özgürlüğünü korur, tekrara neden verir. Koşul: 4.3'ten sonra, aynı `daily` altyapısıyla. Risk: düşük. **T**
- **%80 altında "Kâğıdı yatır" onayı (S):** ilk basışta "Uyum %62: yine de yatır?" toast'ı, ikinci basışta yatır. Derslerde geçerli, serbest tekne ve Tek Nefes'te değil. Bot `layPaper`'ı %80+'da çağırıyor, etkilenmez. **D** (§3.8)
- **Ana menüyü sadeleştir (S):** "Oyna" + "Tek Nefes" + "Günün desen"i birincil; Serbest tekne/Galeri/Duvar tek "Atölye" alt menüsü. "Galeri duvarı" → "Baskı duvarı". Koşul: buton id'leri bot için (`bPlay`) değişmeden. **D** (§3.5)
- **Koç kartını hayaletin başlangıcıyla çakışmayacak yere koy (S):** hayaletin ilk noktası kartın altında kalıyorsa kart sağa/alta kaysın. **D** (ekran 02)
- **Ders 1-3 mühür eşiğinin kalibrasyonu (S, ama dikkat):** serpinti dersleri şansa bağlı (§3.9). Seçenek: eşiği düşürmek yerine fırça boyutu rastgeleliğini tarif başlangıcına "yapıştırmak" (hayaletin başlangıç halkasına 20 birim yakın başlanırsa tarifin tohumu kullanılsın). Koşul: önce botla 18 dersin mühür tablosu çıkarılsın. Eski mühürler zaten kayıtlı, dokunulmaz. **T**
- **Dokunsal geri bildirim (S):** damla düşerken `navigator.vibrate(8)`, Arena "titreşim" ayarına bağlı. Telefonda damla hissi verir. Şu an hiç `vibrate` çağrısı yok (**D**, grep). Risk: iOS desteklemez, zararsız.
- **Oynanış smoke testi (S, repoda `tools/` altında):** `?auto&nosave` ile 2 dersi `ebruSim` ile koştur + sentetik pinch senaryosu (bu rapordaki `probe.cjs`'in özü). `index.html`'e dokunmaz, relay gerilemelerini yakalar. **D**

## 6. EKLENMEMELİ
- **Çevrimiçi galeri / topluluk duvarı / skor tablosu:** sunucu, hesap ve kullanıcı içeriği moderasyonu ister. **Kısıtı aşar.**
- **Renk karıştırma / sıvı (Navier-Stokes) simülasyonu:** ebrunun "renkler karışmaz" kuralını ve belirlenimciliği bozar. Hedefler, bot ve çözülebilirlik çöker. 8 GB / UHD bütçesini aşar.
- **Puanlı Tek Nefes (hedefe uyum ölçümü):** Tek Nefes'in değeri hedefsiz, nefesle sınırlı ifade. Puan eklemek onu 19. derse çevirir; dersler bu işi zaten yapıyor.
- **Daha fazla ders eklemek (önce 4.3'ü yapmadan):** 18 elle yazılmış tarif bitişe yeterli. Tekrar oynanabilirlik günlük varyanttan daha ucuza gelir.
- **Zamanlayıcı / ceza ile derslere baskı:** usta-çırak öğretim temasına ve sakin atölye tonuna ters (T).
- **ARENA-KIT bloğunda değişiklik (örn. `share`'e dosya desteği):** kurala aykırı. Dosya paylaşımı oyun kodunda yapılmalı (4.2).
- **Pinch'i tamamen kapatmak:** telefonda tepsi küçük; yakınlaştırma faydalı. Doğru çözüm 4.1.

## 7. Düzeltilmeli
- **Pinch damla hatası:** 4.1. En yüksek öncelik, Tek Nefes'te geri alınamaz kayıp.
- **Görünürlük handler'ı:** `90d889a` ile eklenen ses askıya alma, arena `pause/resume` (3965-3966) ile çakışıyor. Birini bırak (tercihen arena'nınki, "otomatik duraklat" ayarına uyar). Ya da "kopya ama zararsız" diye yorumla işaretle.
- **20 sn "yüklenemedi" mesajı (1955):** "Hâlâ yükleniyor…" yazsın, hata metni yalnız `error`/`unhandledrejection` modül hatasında çıksın. **T**
- **Tek Nefes baskı mührü (3461):** ders mühründen farklı bir damga kullan (ör. "nefes" damgası). Usta mührünün anlamını korur.
- **README / project-meta:** Tek Nefes, günlük meydan okuma, galeri duvarı, `arena.ebru.duvar.v1`, `?d=YYYYMMDD` eklenmeli. "Persistence" ve "URL flags" tabloları eksik.
- **Erişilebilirlik:** renk adı etiketi (4.4). Sonuç kartında `rStars` için metin alternatifi var mı, kontrol et (yıldızlar SVG, `aria-label` görmedim, **T**).
- **Telefon ana menü:** panel kaydırması gerekiyor, ilk ekranda "Biliyor muydun?" ve altbilgi görünmüyor. Kabul edilebilir ama sadeleştirme (§5) bunu da çözer.

## 8. Önerilen ilk 3 iş
1. **Dokunmada niyet bekleme (4.1) + sentetik pinch testi (`tools/` altında).** Doğrulanmış bir hata, Tek Nefes'te (imza mekaniği) geri alınamaz. S maliyet, kayıt/bot riski yok. Bu raporun `probe.cjs` senaryosu kabul testi olarak hazır: pinch sonrası `strokes` 0 kalmalı, `nefes.drop` false kalmalı.
2. **Kâğıdı resim olarak kaydet / paylaş (4.2).** Oyunun ürünü görsel, bugün dışarı çıkamıyor. S maliyet, yalnız kullanıcı tetiklemeli, ağ yok. Tek Nefes ve günlük paylaşımı da güçlendirir. Sonra README'ye Tek Nefes + günlük + duvar eklenmeli (aynı turda, S).
3. **Tohumlu günlük desen (4.3).** Arena-kit'in günlük/seri katmanını gerçekten anlamlı yapar ve tarif mimarisini en iyi kullanan iş. M maliyet. Önce 1 ile 2 yapılmalı ki paylaşılan günlük kâğıt resmiyle gitsin. Bot için günlük modda bir tur kontrolü eklenmeli.

## 9. Doğrulanmayanlar / açık sorular
- Gerçek GPU'da (Intel UHD 620) FPS ölçülmedi. Bu oturumda makine aşırı yüklüydü (swiftshader 10 fps, `workMax` 4,3 sn); README'deki 58-60 fps iddiası test edilemedi.
- Masaüstü başlık ekran görüntüsü yük nedeniyle zaman aşımına uğradı. Masaüstü ders, telefon başlık/ders/Tek Nefes görüntüleri alındı.
- Botun 18 derslik tam koşusu yapılmadı (yük altında ~1 ders/dk). Yalnız 2 ders, 0 hata. README'deki 48/54★, 12/18 mühür yeniden ölçülmedi.
- Pinch hatası, sentetik `PointerEvent` ile gösterildi. Gerçek cihazda ilk parmak ile ikinci parmak arasındaki tipik gecikme (30-100 ms) aynı sonucu verir (T), ama gerçek telefonda denenmedi.
- iOS Safari'de `navigator.share({files})` davranışı ve itch.io/Playgama iframe'inde `download`/Web Share izni denenmedi (iframe `allow="web-share"` isteyebilir, **T**).
- Renk körü simülasyonu (deuteranopi vb.) ile 12 pigmentin ayırt edilebilirliği ölçülmedi; çiftler tahmin.
- Günlük dersin tekrar sıklığı (FNV-1a `seed % 18`) hesaplanmadı. Erişilemeyen iki dış kaynak var: `blog.amandaghassaei.com` ve `gameaccessibilityguidelines.com` bu oturumun ağ izninde değil; yalnız arama özetleri kullanıldı.

## Kaynaklar
- Lu, Jaffer, Jin, "Mathematical Marbling" (IEEE CG&A 2012): https://Www.Gwern.net/doc/cs/cellular-automaton/2012-lu.pdf ; Jaffer, marbling matematiği: https://people.csail.mit.edu/jaffer/Marbling/Mathematics
- Dijital marbling uygulamaları (dışa aktarma/paylaşım beklentisi): https://apps.apple.com/mx/app/ink-marbling/id6739265121 , https://tryebru.pages.dev/ , https://danybittel.itch.io/marbling , https://blog.amandaghassaei.com/2022/10/25/digital-marbling/ (erişilemedi)
- Web Share dosya paylaşımı: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/canShare , https://web.dev/patterns/files/share-files
- Günlük bulmaca tutundurma: https://www.moengage.com/blog/wordle-viral-growth-story/ , https://www.enchant.com/lessons-from-wordle , https://danmeyer.substack.com/p/why-wordle-works-according-to-desmos
- Portal beklentileri (dikey, boyut): https://docs.crazygames.com/requirements/technical/ , https://sdk.poki.com/requirements
- Dokunma jestleri: https://help.notewise.dev/articles/9821547-draw-scroll-and-zoom-using-fingers , https://developer.android.com/develop/adaptive-apps/cookbook/stylus-palm-rejection
- Renk erişilebilirliği: https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/ , https://learn.microsoft.com/en-gb/gaming/accessibility/xbox-accessibility-guidelines/103 , https://unity.com/blog/video-game-accessibility-basics

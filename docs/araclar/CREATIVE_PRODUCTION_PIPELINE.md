# Yaratıcı üretim hattı

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).
Araç seçiminin gerekçesi: [RECOMMENDED_TOOLSTACK.md](RECOMMENDED_TOOLSTACK.md).

Bu belge **önerilen** hattı anlatır. Hattın kendisi bir öneridir (T); içindeki araç bilgileri D ya da K etiketlidir.
Hat bu oturumda uçtan uca koşulmadı. Yalnız bazı halkaları scratch'te denendi: [INSTALLATION_AND_TEST_REPORT.md](INSTALLATION_AND_TEST_REPORT.md).

## Değişmez kurallar

1. **Özgünlük.** Bu araçlar yalnız sahibin kendi evreni, karakterleri ve maskotu için kullanılır.
   Başka bir projenin (ör. F.L.A.Q.) maskotu, karakteri ya da marka kimliği kopyalanmaz ve taklit edilmez. Buna yönlendiren iş akışı kurulmaz.
   Promptlara başka eser, stüdyo ya da karakter adı yazılmaz.
2. **Kanon tek gerçek kaynağıdır.** Kanon zaten var ve Google Drive'da duruyor: `osmanli-evreni/evren/00-kanon.md` (D).
   İkinci bir wiki açılmaz. Başka yerlere kopya değil, bağlantı ya da özet konur.
3. **Taslak → onay → kanon.** Yeni fikir önce `taslak/` klasörüne girer, sahibi onaylar, sonra `evren/` altına taşınır.
   `kaynak/` değişmez. Dış yapay zekâ çıktısı doğrulanmadan kanona girmez (D: deponun kendi kuralları).
4. **Yapan ajan kendi işini "doğrulandı" ilan etmez.** Her aşamanın kapısı bağımsız kanıt ister: test çıktısı, kapı sonucu ya da ikinci bir inceleme.
5. **Toplu değişiklik sırası.** Bütün oyunlara yayılacak her şey önce tek oyunda pilot olur, sonra `schema/degisim.py` kapısından geçer, sonra sahibi onaylar.

## Kim ne yapar

| Kim | Rolü | Bu oturumdaki durumu |
|---|---|---|
| İnsan (sahip) | Kanon onayı, maskot ana çizimi, her ücretli ya da dışa yazan adımın onayı, son göz | — |
| Claude, bulut oturumu | Taslak, kod, bağlamsız alt ajanla denetim, statik inceleme | **Çalıştı.** Bu oturumda çalışan tek yapay zekâ budur |
| Claude, PC (A oturumu) | PC'deki dosyalar, Remotion render, Gemini TTS çağrısı | Çalıştırılmadı; mesaj gönderilmedi |
| Gemini TTS, Google Flow | Türkçe seslendirme; tarayıcıda video | **Çalıştırılmadı.** Anahtar yalnız PC'de |
| Higgsfield | İsteğe bağlı karakter tutarlılığı ve tanıtım klibi | Üretim yapılmadı; yalnız bakiye ve katalog okundu |

NVIDIA ve diğer sistemler bu hatta rol almıyor; onlar da çalıştırılmadı. Ayrıntı: [AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md).

## Aşamalar

| # | Aşama | Araç | Kim yapar | Girdi → çıktı | Kapı |
|---|---|---|---|---|---|
| 1 | Kanon / story bible | Drive'daki markdown kanon ve git deposu | Claude taslak yazar; insan onaylar | `kaynak/`, `taslak/` → `evren/*.md` | Sahibin onayı. Öneri: `evren/olgular.json` + stdlib doğrulayıcı |
| 2 | Senaryo | Fountain düz metin; fountain-js; screenplain | Claude taslak yazar; insan onaylar | Kanon + bölüm fikri → `.fountain` + PDF | Dosya hatasız ayrışır; sahne listesi ve kadro çıkar |
| 3 | Süreklilik denetimi | Deterministik betik → bağlamsız Claude alt ajanı → insan | Yazan ajandan **ayrı** bir Claude alt ajanı; sonra insan | `olgular.json` + editör talimatı + yeni taslak → bulgu tablosu | SERT bulgu kalmaz ya da sahibi karar verir |
| 4 | Maskot ana çizimi | Inkscape ya da Krita. Yapay zekâ yalnız keşif için | **İnsan çizer** | Maskot özeti + eskizler → ana SVG + `params.json` | Sahibin onayı; özgünlük kontrolü; süreç dosyaları saklandı |
| 5 | Karakter sayfası / turnaround | Ana SVG'den türetme. İsteğe bağlı: Higgsfield `character-sheet`, Figma bileşenleri | İnsan + Claude (kodla SVG). Higgsfield yalnız onayla | Ana SVG + `params.json` → ön, 3/4, yan, arka + ifade sayfası | Renk ve oranlar `params.json` ile aynı; göz kontrolü |
| 6 | Storyboard | Fountain sahne listesi; video-studio'nun 2x2 / 3x3 storyboard kalıbı + ffmpeg bölme | Claude taslak yazar; insan onaylar | `.fountain` → sahne planı ve kare tabloları | Sahne sayısı senaryoyla eşleşir; sahibin onayı |
| 7 | Animasyon | `src/puppet/` kukla rig'i + Rhubarb ağız şekilleri + Remotion | Claude (PC) kodlar; insan bakar | Parça seti + ses → Remotion kompozisyonu | Kare tablosuna gözle bakılır; ffprobe + tam çözme |
| 8 | Ses / müzik | TR: Gemini TTS. Altyazı: whisper-ctranslate2. Müzik/SFX: CC0 kaynaklar | Gemini TTS (PC); Claude (PC) tetikler; insan dinler | `icerik/vo/` metni → ses + kelime zamanlı altyazı | `finish_v3.py`: -14 LUFS, -1 dBTP; yapay zekâ sesi beyanı |
| 9 | Video | Remotion 4.0.535. İsteğe bağlı: Higgsfield klibi | Claude (PC) render eder; insan QA yapar | Kompozisyon + ses → 4 kesim MP4 | `finish_v3.py`; 14 maddelik QA listesi; `false-green-gate` |
| 10 | İnteraktif hikâye / oyun | Ink + inkjs; arena-kit; oyun gate'i | Claude yazar ve kodlar; insan oynar | `.ink` → derlenmiş JSON → tek `index.html` | Derleyici (kırık dal = çıkış 1); dal yürüyücü bot; gate |
| 11 | Web / sosyal | GitHub Pages + stdlib üretici; Buffer + video-studio kuyruğu | Claude üretir; Buffer'a yazmayı insan onaylar | `lore/*.md` → site; MP4 → kuyruk | Site testleri ve CI; erişilebilirlik/performans skill'leri; dil kuralı |
| 12 | Arşiv | git + Drive kopyası; PROVENANCE + `kilit.json`; paket pinleri | İnsan + Claude | Süreç dosyaları, pinler, kayıtlar | `kilit.py --kontrol`; tarihli commit'ler |

Kapılar hattın önerisidir (T). 8, 9 ve 11. satırdaki kontroller bugün depolarda mevcut (D: depo notu).
10. satırdaki derleyici kontrolü scratch'te denendi (D); dal yürüyücü bot henüz yok.

## Aşama notları

### 1. Kanon (D: Drive MCP ile okundu)

- `osmanli-evreni/` klasörü Drive'da, git deposunun kopyası olarak duruyor. İçinde `evren/`, `kaynak/`, `taslak/`, `gorsel/`, `araclar/` ve deponun kendi `CLAUDE.md` dosyası var.
- `00-kanon.md` (v0.2) süreklilik belgesi olarak iyi kurulmuş: kronoloji tablosu, karakter tablosu, açık gizemler listesi, numaralı tutarsızlık tablosu ve kaynak etiketleri var.
- Eksik olan yeni bir wiki değil. Eksik olan, bu kanonu **makinece kontrol edilebilir** kılmak (T).
- Depo bu bulut oturumunda klonlu değil; yalnız Drive kopyası okunabiliyor. Drive bağlantısı yazamıyor (`canEdit:false`).
- Obsidian kasası (BEYIN) kanonun kopyasını değil, bağlantısını ya da özetini tutmalı (T).

### 2. Senaryo (D: scratch denemesi)

- fountain-js bir deneme metninden sahne başlıklarını ve karakter kadrosunu çıkardı. Bu liste süreklilik denetiminin girdisidir.
- screenplain aynı metinden PDF, FDX ve HTML üretti. Türkçe karakterler PDF'te doğru göründü.
- video-studio'nun `icerik/vo/` "satır = sahne" biçimi Fountain sahneleriyle eşlenebilir (T).

### 3. Süreklilik denetimi

Önerilen üç kapı (T):

1. **Deterministik.** Senaryodan sahne ve kadro çıkar; `olgular.json` ile karşılaştır (ölü karakter sahnede mi, tarih aritmetiği tutuyor mu). Dallanan hikâyede derleyici kırık dalı yakalar.
2. **Bağlamsız Claude alt ajanı.** Girdi yalnız olgu tabanı, editör talimatı ve yeni taslak. Çıktı: alıntılı bulgu tablosu (SERT / YUMUŞAK / BİLGİ) ve "riskli ama temiz" listesi. Metni değiştirmez.
3. **İnsan.** SERT bulgular sahibine gider. Öneriler `taslak/` → onay → `evren/` yolunu izler.

Kanıt ve sınırlar (D):

- Küçük bir deneyde yapay zekâ geçişi ekili 2 çelişkinin 2'sini buldu, yanlış pozitif vermedi. Cevap anahtarı geçişten önce yazılıp hash'lendi.
- Bu deney **kör değildi**: çelişkiyi aynı ajan yazmıştı. Gerçek kör test henüz yapılmadı.
- Deterministik geçiş kırılgan: yalnız bilinen kurallar için güvenlik ağıdır. Anlamı yapay zekâ denetler.
- Ölçek farkı: deney 3 paragraftı; gerçek kanon çok daha büyük.
- `story-skills` süreklilik motoru bu işe uyuyor ama henüz kabul edilmedi: [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md).

### 4-5. Maskot ana çizimi ve karakter sayfası

Bugünkü durum (D: video-studio okundu): karakter hattı kişisel avatar için kurulu. **Özgün maskot hattı yok.**
Eski kukla denemesi "tutarlılık hiç yok" diye bırakılmış. Çıkan ders: tek ana çizim, parçalar ondan türetilir.

Eksikler:

1. Maskotun kendisi: isim, kişilik, silüet, renk kodları ve oran tablosu.
2. Vektör ana çizim ve ondan türetilmiş parça seti (kafa, göz, ağız şekilleri, kol, bacak).
3. Turnaround ve ifade sayfası.
4. Higgsfield'da maskotun Reference Element'i (isteğe bağlı, ana çizim onaylandıktan sonra).
5. Maskot sesi: Türkçe destekli, ticari serbest ve yerel bir ses yok.
6. İnsan katkısını gösteren süreç kaydı.

Scratch denemesi (D): tek parametre sözlüğünden 4 görünüşlü bir SVG turnaround üretildi. Renk ve oranlar tek yerde tutulunca görünüşler tutarlı kaldı.
Bu bir yer tutucu figürdü; maskot önerisi değildir.

### 7. Animasyon

- Remotion ve kukla rig'i kodu mevcut (D). Rhubarb kurulu değil.
- Rhubarb'ın tanıyıcısı yalnız İngilizce. Türkçe için fonetik kip kullanılır; isabeti daha düşük (D: README).
- Scratch'te 2 saniyelik bir zıplama klibi render edildi ve doğrulandı (D). Bir hata bulundu: en yüksek noktada figür çerçeveden taşıp kırpılıyor. Bu deneme "çalışıyor" der, "yayına hazır" demez.

### 8. Ses

- Gemini TTS'e giden metne gerçek kişi verisi konmaz; ücretsiz katmanda insan inceleyiciler okuyabilir (K-ikincil).
- Yapay zekâ sesi her zaman beyan edilir: bitiş kartında ve her gönderi metninde (D: video-studio kuralı).
- İngilizce maskot sesi için ileride yerel Kokoro denenebilir. Türkçe için yerel ve ticari serbest ses henüz yok.

### 10. İnteraktif hikâye

- Derlenmiş hikâye oyuna satır içi JSON olarak gömülür; tek dosya ve çevrimdışı kuralı korunur (T).
- Durum arena-kit depolama düzenine yazılır; hikâye bitince bitiş kartı çağrılır (T).
- Gate için "dal yürüyücü bot" önerisi: bütün seçenekleri dener; son sayısı sabit kalmalı, çıkmaz dal sıfır olmalı (T). **Bu bot henüz yazılmadı.**
- Scratch'te yalnız tek seferlik bir duman testi koştu: iki dal oynandı, koşullu seçenek doğru gizlendi, bozuk hikâyede test kırmızıya döndü (D).

### 11. Web ve sosyal

- Lore sitesi için mevcut dizin sitesinin deseni yeter: ayrı bir depo, GitHub Pages ve stdlib üretici. Yeni depo sahibin onayını ister.
- Dil kuralı (D: video-studio): YouTube ve X yalnız İngilizce, Instagram yalnız Türkçe. Threads için dil kararı sahibindedir.
- Yeni seri formatı adayı (T): "hangi seçimi yapardın?" sorusu; iki dal ekran kaydıyla çekilir.

## Maskot: telif ve marka

Kaynakların çoğu K-ikincil; mahkeme kararı ya da resmî Türk rehberi bulunamadı. Bu bölüm hukuki görüş değildir.

- **ABD telif (K-ikincil):** Telif Ofisi'nin Ocak 2025 raporuna göre yalnız prompt yazmak yazarlık sağlamaz. İnsanın kendi çizimi ve seçme, düzenleme, değiştirme katkısı korunabilir; koruma o katkıyla sınırlıdır.
- **Türkiye telif (K-ikincil, doktrin):** baskın görüşe göre eser sahipliği gerçek kişiye özgüdür; belirleyici olan insanın yaratıcı katkısıdır.
- **Marka:** ABD'de inceleme, işaretin kaynak göstergesi olup olmadığına bakar; kimin tasarladığına bakmaz (K-ikincil).
  Türkiye'de de maskotun marka olarak tescil edilebileceği bir çıkarımdır (T); yapay zekâ ile üretilmiş başvuru için resmî bir TÜRKPATENT yaklaşımı bulunamadı.

Pratik kurallar (T):

1. **Ana çizim insan elinden çıkar** (Inkscape ya da Krita). Yapay zekâ taslağı kullanılırsa elle yeniden çizilir.
2. **Süreç dosyaları saklanır:** eskizler, katmanlar, tarihli commit'ler.
3. Maskotun adı ve görseli marka olarak korunur. Tescilden önce benzerlik araması yapılır.
4. Ana çizim, güncel kullanım şartları okunmadan Higgsfield'a yüklenmez. Gerekirse düşük çözünürlüklü bir türev yüklenir.
5. Yapay zekâ çıktısının telif koruması zayıftır; başkası benzerini üretebilir. Yapay zekâ yalnız keşif ve varyasyon içindir.

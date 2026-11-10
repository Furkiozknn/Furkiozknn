# Sıradaki adımlar

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).

Her adım iki sınıftan birindedir:

- **Şimdi yapılabilir** (ücretsiz, geri alınabilir): para, dış yazma, hesap/izin değişikliği ya da depoya kabul içermez.
- **Sahibin onayı gerekir**: ücretli, dış sisteme yazan, hesap ya da izin değiştiren, ya da depoya skill/araç kabul eden adım. Engel adı yanında yazar.

Adımlar öneridir (T) ve bu oturumda **yapılmadı**. Sıra, bir adımın sonrakini açmasına göre kuruldu.
Yapay zekâ notu: bu adımları bulutta Claude yürütebilir. Gemini TTS gereken adımlar PC'de koşar; Gemini bu oturumda çalıştırılmadı.

## A. Şimdi yapılabilir

| # | Adım | Ne üretir | Neden şimdi | Not |
|---|---|---|---|---|
| A1 | Maskot özetini yaz: isim, kişilik, silüet, renk kodları, oran tablosu | Tek sayfalık özet; ilerideki `params.json`'un girdisi | Hattaki ilk eksik bu; araç gerektirmiyor | Kararlar sahibindir. Başka eser, stüdyo ya da karakter adı kullanılmaz |
| A2 | Kör süreklilik testi: editör talimatını ve deney dosyalarını bağlamsız bir Claude alt ajanına ver | Kör sonuç: yakalanan çelişki, yanlış pozitif | Önceki deney kör değildi | Ana oturumda alt ajanla yapılır; ayrı ücretli servis gerekmez |
| A3 | `olgular.json` taslağını çıkar: varlık, özellik, değer, geçerlilik aralığı, kaynak etiketi | Taslak olgu tabanı + stdlib doğrulayıcı taslağı | Kanon Drive'dan okunabiliyor | Taslak scratch'te kalır ve hiçbir şeyi değiştirmez. Hikâye raporu taslak için de sahibin onayını öngörüyor; depoya girmesi B2 ve B3'e bağlı |
| A4 | Ink için dal yürüyücü bot prototipi yaz | Bütün dalları deneyen deterministik betik: son sayısı, çıkmaz dal, erişilmeyen düğüm | Gate önerisinin eksik parçası; henüz yazılmadı | Scratch'te, özgün bir deneme hikâyesiyle |
| A5 | Bir deneme sahnesini Fountain'e çevir ve sahne/kadro çıkarımını `olgular.json` taslağıyla karşılaştır | Deterministik kapının ilk sürümü | A3'ün çıktısını kullanır | Scratch'te |
| A6 | Scratch'teki Remotion denemesinde çerçeve taşmasını düzelt ve yeniden render et | Temiz 2 sn'lik örnek | Bilinen tek hata | Yalnız örnek; yayın değil |

Bu adımları yapan ajan sonucu tek başına "doğrulandı" ilan etmez. Çıktıyı gösterir; kararı sahibi ya da ikinci bir inceleme verir.

## B. Sahibin onayı gerekir

| # | Adım | Engel (onay konusu) | Onaydan sonra ne açılır |
|---|---|---|---|
| B1 | Oturum ağına host ekle: `ai.google.dev`, `higgsfield.ai`, `www.copyright.gov`, `www.turkpatent.gov.tr`, `huggingface.co` | Ortam ağ izni değişikliği | Birincil kaynak doğrulaması: Gemini şartları ve kotası, Higgsfield şartları, telif raporu, Piper TR ses kartları |
| B2 | `osmanli-evreni` deposunu bulut oturumuna ekle | Depo erişimi (izin değişikliği) | Kanon üzerinde git ile çalışma; Drive bağlantısı yazamıyor |
| B3 | `olgular.json` ve doğrulayıcıyı kanon deposuna al | Kanon kuralı: taslak → onay → `evren/` | Deterministik süreklilik kapısı |
| B4 | PC'ye Inkscape (ya da Krita) kur | PC'ye kurulum; sürüm + hash kaydı | Maskot ana çizimi (insan çizer) |
| B5 | Ana çizimi ve `params.json`'u onayla | Sahibin yaratıcı kararı | Turnaround, ifade sayfası, parça seti |
| B6 | fountain-js ve screenplain'i bir proje deposuna al | Depoya araç kabulü: tam sürüm, lockfile, bütünlük hash'i; `reportlab` pini | Senaryo biçimi ve otomatik sahne/kadro listesi |
| B7 | inkjs'i **tek** oyunda pilot olarak dene | Depoya araç kabulü; pilot kuralı | Sonra `schema/degisim.py` kapısı, sonra diğer oyunlar için ayrı onay |
| B8 | ~~gamedev `dialogue-systems` + `visual-novel` skill'lerini kabul et~~ **Yapıldı (10 Kas)**: pinli, PROVENANCE + kilit, SkillSpector kapısıyla. Bkz. [KURULUM_5_DEPO.md](KURULUM_5_DEPO.md) | — | Ink'e özel rehber skill'ler |
| B9 | `story-skills` için izole çalışma ve yeniden üretim testi yap | Dış kodu çalıştırma izni (bu oturumda reddedildi); yayıncı doğrulaması | Koşullu kabul kararı; sonra skill kabul kapısı |
| B10 | PC'ye Rhubarb kur | PC'ye kurulum; release arşivi + sha256 | Dudak senkronu |
| B11 | A oturumuna iş devret: Gemini TTS ile seslendirme, Remotion render | PC'de iş başlatır; Gemini günlük kotasını harcar | Ses ve video aşamaları |
| B12 | Higgsfield şartlarını oku; sonra onaylı ana çizimden Reference Element oluştur | Ücretli kredi; ana çizimi dış servise yükleme. B1 ve B5'e bağlı | İsteğe bağlı tanıtım klibi ve karakter sayfası |
| B13 | Lore sitesi için yeni depo aç | Yeni GitHub deposu; yeni workflow'lar depo kuralına uymalı | Lore sitesi ve hikâye sayfaları |
| B14 | Threads için dil kararı ver; Buffer'a yazmayı aç | Dış sisteme yazma; dil kuralına ek | Dördüncü sosyal kanal |
| B15 | Zamanlanmış görevlerin `ACCESS_DENIED` sorununu çöz | Hesap/izin değişikliği | Haftalık otomatik süreklilik denetimi |
| B16 | Marka benzerlik araması yap; tescil kararını ver | Sahibin hukuki ve mali kararı; maliyet raporlarda yok | Maskot adı ve görseli için marka koruması |

## C. Bekletilenler

| Konu | Neden bekliyor | Ne zaman açılır |
|---|---|---|
| Piper TR sesleri `fettah` ve `fahrettin` | Model kartları okunamadı; lisans kökeni belirsiz | B1'den sonra |
| Kokoro ile İngilizce maskot sesi | Maskot ve ses kararı henüz yok | B5'ten sonra |
| Blender ve 3D maskot | PC donanımı sınırda | 2D hat oturduktan sonra |
| Higgsfield_Bridge | PC'de eklenti ve bağlı uygulama gerekir | Blender kararından sonra |
| Canva, Dropbox, TinyFish bağlantıları | Proxy reddediyor; raporlar bu projede rol tanımlamadı | İhtiyaç doğarsa, host onayıyla |
| Supabase ile seçim istatistiği | Kişisel veri ve anahtar yükü | Yalnız sunucu tarafı ihtiyaç doğarsa |
| Higgsfield'daki eski `furki-3d` öğesi | Artık kullanılmıyor; silmek sahibin kararı | Sahibi isterse |

## D. Yapılmayacaklar

Reddedilen araçların listesi ve gerekçeleri: [RECOMMENDED_TOOLSTACK.md](RECOMMENDED_TOOLSTACK.md).
Kısaca: kendiliğinden güncellenen ya da uzaktan talimat çeken skill kurulmaz; başka bir projenin maskotu, karakteri ya da markası taklit edilmez.

## E. Bağımlılık sırası (özet)

1. A1 → B4 → B5: maskot özeti, çizim aracı, onaylı ana çizim.
2. A2, A3, A5 → B2 → B3: süreklilik kapısı.
3. A4 → B7: Ink pilotu ve gate.
4. B1 → B12 ve bekleyen lisans soruları.
5. B5 → B10, B11: animasyon, ses, video.
6. B13, B14: yayın yüzeyi.

Bağlam: [CREATIVE_PRODUCTION_PIPELINE.md](CREATIVE_PRODUCTION_PIPELINE.md), [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md), [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md).

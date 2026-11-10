# Araç araştırması: envanterler ve üretim hattı

Tarih: 10 Kas 2026.
Konu: sahibin **kendi özgün** hikâye evreni, karakterleri ve maskotu için üretim altyapısı.
Araştırma bitti. Bu klasör beş alan raporunu özetler; yeni araştırma içermez.

## Belgeler

| # | Belge | Ne anlatır |
|---|---|---|
| 1 | [AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md) | Yapay zekâ sistemleri ve üretim servisleri: nerede çalışır, durum, maliyet, çıkan veri |
| 2 | [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md) | Kilitli 8 skill, `anthropic-skills:` kovası, dış skill depoları ve kabul kararları |
| 3 | [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md) | MCP sunucuları ve plugin'ler: bağlantı, salt okuma testi, proje rolü, onay |
| 4 | [CREATIVE_PRODUCTION_PIPELINE.md](CREATIVE_PRODUCTION_PIPELINE.md) | Kanondan arşive üretim hattı: araç, kim yapar, girdi/çıktı, kapı |
| 5 | [TOOL_COMPATIBILITY.md](TOOL_COMPATIBILITY.md) | Araç × ortam, PC donanımı, lisans ve kabul kuralı matrisi |
| 6 | [INSTALLATION_AND_TEST_REPORT.md](INSTALLATION_AND_TEST_REPORT.md) | Bu oturumda ne denendi, ne çıktı, ne bilerek yapılmadı |
| 7 | [RECOMMENDED_TOOLSTACK.md](RECOMMENDED_TOOLSTACK.md) | Alan başına en küçük yığın, "kullanma" listesi, maliyet |
| 8 | [NEXT_STEPS.md](NEXT_STEPS.md) | Sıralı adımlar: şimdi yapılabilir ya da onay gerekir |
| 9 | [KURULUM_5_DEPO.md](KURULUM_5_DEPO.md) | Beş GitHub deposunun incelemesi: ne kuruldu, ne kurulmadı, nasıl doğrulandı |

## Kaynaklar

Beş rapor: envanter, hikâye, görsel, oyun-web, güvenlik.
Raporlar ve deneme dosyaları oturumun geçici (scratch) klasöründe kaldı; depoya girmedi.
Raporlar çelişince **güvenlik raporu** esas alındı, çünkü diğerlerini birincil kaynaktan yeniden doğruladı.
Düzeltmeler ilgili belgede "Düzeltme" başlığı altında yazar.

## Kanıt etiketleri

| Etiket | Anlamı |
|---|---|
| **D** | Araştırma oturumunda çalıştırıldı ya da okundu (komut, çağrı, dosya) |
| **K** | Resmî doküman ya da kaynak kodu |
| **K-ikincil** | Resmî kaynağın yalnız arama özeti; birincil sayfa açılamadı. Kesin değildir |
| **T** | Çıkarım |

Depo notlarından aktarılan bilgi (PC envanteri, video-studio `araclar.md` gibi) "D: okundu" sayılır.
Bu, aracın çalıştırıldığı anlamına gelmez.

## Durum etiketleri

Her envanter satırı şu yedi etiketten tam birini taşır:

- `Mevcut ve çalışıyor`: var, bu oturumda denendi, çalıştı.
- `Mevcut ancak test edilmedi`: var (bulutta ya da PC'de), bu oturumda çalıştırılmadı.
- `Kuruldu ve doğrulandı`: depoda zaten kurulu ve bir kontrolle doğrulandı. Yalnız kilitli 8 Furkiozknn skill'inde kullanıldı.
- `Kullanılabilir ancak kurulum bekliyor`: uygun görünüyor, kurulmadı. Yalnız scratch'te denenenler de buradadır; deneme notu yanında yazar.
- `Ücretli veya onay gerektiriyor`: para, kredi, anahtar, dış sisteme yazma ya da hesap/izin değişikliği ister.
- `Uyumsuz`: bu ortamda ya da PC donanımında çalışmaz, ya da dosyası eksik.
- `Gereksiz veya önerilmiyor`: işi başka bir şey görüyor, kapsam dışı, ya da kural/güvenlik gereği reddedildi.

Etiket **bu proje açısından** verilir.
Bağlantısı çalışan ama projede işi olmayan bir araç "gereksiz" etiketi alabilir; bağlantı testi ayrı sütunda yazar.
Raporlar aynı araca farklı etiket verdiyse sıra şudur: güvenlik raporu, sonra aracı proje için değerlendiren alan raporu, sonra envanter.
"Çalışıyor" ile "test edilmedi" arasında kalınan yerde temkinli olan seçildi.

## Dürüstlük notu

- Bu bulut oturumunda çalışan tek yapay zekâ **Claude**'dur: ana oturum ve Claude alt ajanları (4 paralel alan araştırmacısı, 1 bağımsız güvenlik/lisans denetçisi).
- Gemini, NVIDIA ve diğer sistemlerin anahtarı burada yok. Yalnız sahibin PC'sinde (A oturumu, ai-router) duruyorlar ve **çalıştırılmadılar**.
- Ücretli hiçbir şey kullanılmadı. Dış servislere yazılmadı. Depolara hiçbir araç kurulmadı.
- Ücretsiz yerel denemeler yalnız scratch klasöründe koştu.
- Ayrıntı: [INSTALLATION_AND_TEST_REPORT.md](INSTALLATION_AND_TEST_REPORT.md).

## Değişmez kural

Bu araçlar başka bir projenin maskotunu, karakterini ya da marka kimliğini kopyalamak ya da taklit etmek için kullanılmaz.
Kuralın tam metni: [CREATIVE_PRODUCTION_PIPELINE.md](CREATIVE_PRODUCTION_PIPELINE.md).

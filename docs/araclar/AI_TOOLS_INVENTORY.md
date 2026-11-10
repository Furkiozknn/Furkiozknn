# Yapay zekâ sistemleri ve üretim servisleri

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).

> **Bu oturumda çalışan tek yapay zekâ Claude'dur**: ana oturum ve Claude alt ajanları (4 paralel alan araştırmacısı, 1 bağımsız güvenlik/lisans denetçisi).
> Gemini, NVIDIA ve aşağıdaki diğer sistemlerin anahtarı bu bulut oturumunda yok.
> Yalnız sahibin PC'sinde (A oturumu, ai-router) duruyorlar ve **çalıştırılmadılar**.
> Onlar için yazılanlar depo notlarından ve kaynaklardan gelir; deneme sonucu değildir.

Anahtar kontrolü (D): ortam değişkeni adları listelendi, değerler basılmadı.
GEMINI, NVIDIA, OPENAI, ELEVENLABS, HEYGEN, BFL, HF, RUNPOD, AZURE ve TINYFISH adlı anahtar yok.
`gcloud config list` çıktısında proje de hesap da yok; Vertex/Gemini yolu da kapalı (D).

## 1. Bu oturumdan erişilebilenler

| Sistem | Ne yapar | Nerede çalışır | Durum | Maliyet / kota | Makineden çıkan veri | Kanıt |
|---|---|---|---|---|---|---|
| Claude (ana oturum + alt ajanlar) | Araştırma, yazım, kod, süreklilik denetimi, paralel inceleme | Bu bulut oturumu | `Mevcut ve çalışıyor` | Raporlarda ölçüm yok | Oturum zaten bulutta; raporlar ayrıca incelemedi | D: bu oturum |
| Higgsfield (MCP) | Görsel, video, ses, 3D üretimi; Reference Elements ile karakter tutarlılığı | Bulut servisi, MCP üzerinden | `Ücretli veya onay gerektiriyor` | 64,03 kredi, plan "starter" (bölüm 4) | Prompt ve yüklenen referans görsel Higgsfield'a gider | D: `balance`. Yalnız salt okuma çağrıldı; üretim yapılmadı |

Envantere göre bu oturuma bağlı AI üretim servisi yalnız Higgsfield'dır (D).
Figma MCP'nin de görsel üretim araçları var; onlar [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md) içinde.

## 2. PC'de duran, bu oturumda çalıştırılmayanlar

Kaynak: PC envanteri (A oturumu, 9 Kas) ve video-studio notları. Bu oturumda yalnız okundu (D).
`ai-router` klonu bu konteynerde var ve sağlayıcıları Gemini, NVIDIA ve EVREN (D); anahtar burada olmadığı için çalışmaz.
Router anahtarı PC'deki yerel bir dosyadan okur.

| Sistem | Ne yapar | Nerede çalışır | Durum | Maliyet / kota | Makineden çıkan veri | Kanıt |
|---|---|---|---|---|---|---|
| Gemini API (metin, ai-router) | Metin üretimi | PC | `Mevcut ancak test edilmedi` | Raporlarda metin kotası yok | İstek Google'a gider (T) | D: PC envanteri "anahtar dolu" |
| Gemini TTS (`gemini-3.8-flash-tts`, ses Sadachbia) | video-studio'nun varsayılan seslendirmesi, Türkçe dahil | PC | `Mevcut ancak test edilmedi` | Ücretsiz katman; depo gözlemi günde ~10 istek | Metin ve ses Google'a gider (bölüm 6) | D: depo notu. K-ikincil: şartlar |
| Gemini görsel API (`gemini_karakter.py`) | Karakter görseli istemcisi (stdlib) | PC (Windows yolu sabit) | `Ücretli veya onay gerektiriyor` | Ücretsiz görsel kotası 0 | Prompt Google'a gider (T) | D: depo okundu |
| Gemini web / Google Flow (Veo) | Tarayıcıda video ve görsel; kişisel avatarın kayıtlı karakteri | PC tarayıcısı | `Mevcut ancak test edilmedi` | AI Pro, ~114 kredi | Google'a gider (T) | D: PC envanteri. Depo notu: Flow ücretsiz kredide ticari hak "belirsiz" |
| ChatGPT (ücretsiz, tarayıcı) | Görsel taslak ve stilize görsel | PC tarayıcısı | `Mevcut ancak test edilmedi` | Ücretsiz | OpenAI'a gider (T) | D: depo notu; çıktı hakkını kullanıcıya bırakanlar arasında sayılmış |
| Antigravity `agy` | PC envanterinde "ana işçi" | PC | `Mevcut ancak test edilmedi` | Raporlarda yok | Raporlarda yok | D: PC envanteri |
| EVREN (ai-router sağlayıcısı) | ai-router'daki üçüncü sağlayıcı | PC | `Mevcut ancak test edilmedi` | Raporlarda yok | Raporlarda yok | D: PC envanteri "doğrulanmadı" |
| NVIDIA NIM | ai-router sağlayıcısı | PC | `Mevcut ancak test edilmedi` | Raporlarda yok | İstek NVIDIA'ya gider (T) | D: PC envanteri "anahtar görünmüyor, doğrulanmadı"; PC'de GPU yok |
| OpenAI Codex CLI | Kod ajanı | PC | `Mevcut ancak test edilmedi` | Anahtar yok | Raporlarda yok | D: PC envanteri "kurulu, anahtar yok" |
| Claude Code, PC (A oturumu) | PC dosyaları ve anahtarlarıyla iş; Gemini TTS ve Veo işini devralabilir (T) | PC | `Mevcut ancak test edilmedi` | Raporlarda yok | Raporlarda yok | D: oturum listesinde boşta görünüyor; mesaj gönderilmedi |

PC'de kurulu olmayanlar: Ollama ve LM Studio (D: PC envanteri).
Bulut oturumu PC dosyalarına doğrudan erişemiyor: Remote Control'de iki klasör var, ikisi de `cannot_be_used / not_available` (D).

## 3. Anahtar isteyen bulut servisleri

Bunlar `anthropic-skills:` kovasındaki skill'lerin arkasındaki servislerdir. Hiçbirinin anahtarı yok; hiçbiri çağrılmadı (D).
Skill'lerin kendi durumu: [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md).

| Servis | Ne yapar | Anahtar | Durum | Maliyet | Makineden çıkan veri | Kanıt |
|---|---|---|---|---|---|---|
| HeyGen | Avatar videosu, TTS, video çevirisi, yüz değiştirme | `HEYGEN_API_KEY` | `Ücretli veya onay gerektiriyor` | Ücretli; fiyat raporlarda yok | İstek HeyGen API'sine gider | D: skill metni |
| ElevenLabs | TTS, ses efekti, müzik, konuşma tanıma, sesli ajan | `ELEVENLABS_API_KEY` | `Ücretli veya onay gerektiriyor` | Ücretsiz planda ticari kullanım yok | İstek ElevenLabs'e gider (T) | D: skill metni, depo notu |
| BFL FLUX API | Görsel üretimi | `BFL_API_KEY` | `Ücretli veya onay gerektiriyor` | Ücretli; fiyat raporlarda yok | İstek BFL'ye gider (T) | D: skill metni |
| Modal üzerinde LTX-2.3 | Metinden/görselden video (A100-80GB GPU) | `MODAL_LTX2_ENDPOINT_URL`, `HF_TOKEN` | `Ücretli veya onay gerektiriyor` | Modal GPU ücreti | İstek Modal'a gider (T) | D: skill metni |
| RunPod üzerinde ACE-Step 1.5 | Müzik üretimi | `RUNPOD_API_KEY` + uç nokta | `Ücretli veya onay gerektiriyor` | RunPod ücreti; model MIT | İstek RunPod'a gider (T) | D: skill metni, LICENSE |
| Azure AI Speech | Konuşma tanıma | `AZURE_SPEECH_KEY` | `Ücretli veya onay gerektiriyor` | Raporlarda yok | İstek Azure'a gider (T) | D: skill metni |
| Cloudflare Workers AI | Görsel üretimi (ileride) | Hesap gerekir | `Ücretli veya onay gerektiriyor` | Görsel başına ücretli | İstek Cloudflare'e gider (T) | K: Workers AI model sayfası |

Depo notuna göre ücretsiz katmanda ticari kullanımı yasaklayan video servisleri: Kling, Dreamina, Hailuo, PixVerse (D: `araclar.md`).

## 4. Higgsfield ayrıntısı (yalnız salt okuma, D)

- Bakiye 64,03 kredi; plan "starter". MCP deneme hakkı yok.
- Planlar: PLUS 49 $/ay (yıllık 39 $), 1.000 kredi. ULTRA 129 $/ay (yıllık 99 $), 3.000 kredi.
- Ek paket: 500 kredi 29,41 $ ile 4.000 kredi 210,53 $ arası. Ek kredi 90 günde biter.
- Tek tek model fiyatı MCP'de görünmüyor. Tahmin (T): karakter sayfası 16-17 kredi, video 5 kredi dolayında.
- Depo ölçümü (D: `araclar.md`): Seedance 2.0 Mini 5 kredi / 5 sn; Kling 3.0 ~8,75 kredi / 5 sn.
- 64 kredi kabaca 3-4 karakter sayfası ya da ~10 kısa klip eder (T).
- **Reference Elements**: tek görselden karakter, mekân ya da nesne. İnsan olmayan maskot için doğru yol budur (T).
- **Soul ID**: 5-20 fotoğrafla eğitilen tek kişilik kimlik. Gerçek insan içindir; maskota uygun değil (T).
- **AI Influencer sayfası**: rastgele özelliklerle karakter. Üretilen kişi bizim tasarımımız olmaz; özgün maskot için önerilmez (T).
- `character-sheet` iş akışı: turnaround (ön, 3/4, yan, arka), ifade sayfası, kıyafet varyantı. Kendi kuralı: "original characters only".
- Hesapta 2 Reference Element var: `furki-3d` (video-studio'ya göre geçersiz) ve `Mischief-Cat`.
  `Mischief-Cat` açıklaması stüdyo adları içeriyor; özgün maskot için temel alınmaz. Soul karakteri yok.
- Şartlar (K-ikincil, güncel ToU okunmadı): yardım sayfasına göre Higgsfield çıktıya sahip çıkmıyor ve ticari kullanım plana bağlı değil.
  Üçüncü taraf kaynaklar ise kullanıcı içeriği üzerinde kalıcı, alt lisanslanabilir ve eğitimi kapsayan bir lisanstan söz ediyor.
  Bir başka kaynak bu lisansın 27 Ağu 2026'da daraltıldığını yazıyor. **Çelişkili; kesin değil.**
- Karar (güvenlik): her kullanımda onayla kabul. Maskotun insan çizimi ana dosyası, güncel ToU okunmadan yüklenmez.

## 5. Yerel modeller (ses, altyazı, görsel)

| Model | Ne yapar | Nerede | Durum | Maliyet | Makineden çıkan veri | Kanıt ve not |
|---|---|---|---|---|---|---|
| Supertonic 3 | Yerel TTS; video-studio yedeği | PC | `Gereksiz veya önerilmiyor` | Ücretsiz | Hayır | D: README. Depo arşivlendi; model indirmeleri `supertone-oss-archive` ad alanına taşındı. Kod MIT, model OpenRAIL-M. Mevcut bölümlerde kalır; yeni iş için ret |
| Piper | Yerel TTS | PC (yalnız EN `ljspeech`) | `Mevcut ancak test edilmedi` | Ücretsiz | Hayır | D: program GPL-3.0; her ses ayrı lisanslı. TR sesleri için bölüm 7 |
| Kokoro-82M | Yerel TTS, İngilizce maskot sesi adayı | Kurulu değil | `Kullanılabilir ancak kurulum bekliyor` | Ücretsiz | Hayır | D: Apache-2.0; **Türkçe yok**; espeak gerekir |
| whisper-ctranslate2 0.5.8 | Kelime zamanlı altyazı | PC | `Mevcut ancak test edilmedi` | Ücretsiz (MIT) | Hayır (T) | D: depo notu |
| rembg, auto-editor | Arka plan silme, sessizlik kırpma | video-studio araç listesi | `Mevcut ancak test edilmedi` | Raporlarda yok | Raporlarda yok | D: depo notu; kurulum durumu raporda açık değil |
| ComfyUI + IP-Adapter + SD / FLUX ağırlıkları | Yerel difüzyon, referansla tutarlı karakter | Kurulu değil | `Uyumsuz` | Yerelde ücretsiz; bulut GPU ücretli | Yerelde hayır; custom node'lar ağa çıkabilir | D: README. Ayrıntı [TOOL_COMPATIBILITY.md](TOOL_COMPATIBILITY.md) |

## 6. Gemini TTS: şartlar ve veri (K-ikincil)

Birincil sayfalar açılamadı; aşağıdakiler arama özetinden gelir ve kesin değildir.

- **Sahiplik:** Gemini API Ek Şartları'na göre Google üretilen içeriğin sahipliğini üstlenmiyor. Aynı ya da benzer içeriği başkalarına da üretebilir.
- **Ücretsiz katman:** insan inceleyiciler girdiyi ve çıktıyı okuyabilir. Şart: hassas, gizli ya da kişisel bilgi gönderme.
  Sonuç: seslendirme metnine gerçek kişi verisi konmaz.
- **Filigran:** 3.1 Flash TTS çıktısında SynthID var. Depodaki `gemini-3.8-flash-tts` için doğrulanamadı (T: büyük olasılıkla aynı).
- **Kota:** depo gözlemi günde ~10 istek. Üçüncü taraf kaynaklar birbiriyle çelişiyor ("3 RPM / 15 RPD" ve "ücretsiz katman yok"). Depo gözlemi esas alınır.
- **Türkçe:** resmî dil tablosu okunamadı. Depo pratikte Türkçe kullanıyor (D: `build_audio.py`).
- **Karar (güvenlik):** kabul (mevcut), kısıtla.

## 7. Düzeltmeler (güvenlik raporuna göre)

- **Piper Türkçe sesleri.** Görsel raporu "TR sesi yalnız `dfki`, ticari olmayan lisans" demişti. Eksik.
  Upstream'de 3 Türkçe ses var: `dfki`, `fahrettin`, `fettah` (D: VOICES.md).
  `dfki`: ret (CC BY-NC-SA). `fettah` veri seti CC0 görünüyor ama başka bir sesten ince ayarlanmış (K-ikincil).
  `fettah` ve `fahrettin`, model kartı okunana kadar bekletilir.
- **Supertonic.** Arşivlendiği doğrulandı. Ek: indirme ad alanı taşındı; yeni makinede eski yol kırılabilir (T).
- **Gemini kotası.** Dış kaynaklar çelişkili olduğu için belgeye resmî kota yazılmadı.

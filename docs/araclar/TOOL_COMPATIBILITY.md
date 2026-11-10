# Araç uyumluluk matrisi

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).

## Nasıl okunur

- **Bulut:** bu araştırmanın koştuğu Claude Code bulut oturumu. Linux, 4 çekirdek, 15 GB RAM, GPU yok (D).
- **PC:** sahibin bilgisayarındaki Claude Code (A oturumu). **PC'de bu oturumda hiçbir şey çalıştırılmadı.**
  PC sütunları depo notlarına (D: okundu), resmî gereksinimlere (K) ve çıkarıma (T) dayanır.
- **PC donanımı:** 8 GB RAM, Intel UHD, ayrık GPU yok.
- **Ticari lisans:** aracın ve çıktısının ticari işte kullanılıp kullanılamayacağı.
- **Kabul kuralı:** Furkiozknn kapısına göre güvenlik raporunun kararı. Skill olmayan araçta "pin", tam sürüm + bütünlük hash'i + proje içi kayıt demektir.
- `?` = raporlarda bilgi yok ya da doğrulanmadı. `—` = ilgisiz.

Bu oturumda çalışan tek yapay zekâ Claude'dur; Gemini ve NVIDIA çalıştırılmadı ([AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md)).

## 1. Yapay zekâ ve bulut servisleri

| Araç | Bulut | PC | PC donanımı | Ticari lisans | Kabul kuralı | Durum |
|---|---|---|---|---|---|---|
| Claude (ana oturum + alt ajanlar) | Evet (D) | Evet; bu oturumdan denenmedi | — | Raporlarda incelenmedi | — | `Mevcut ve çalışıyor` |
| Gemini API ve Gemini TTS | Hayır: anahtar yok (D) | Evet: anahtar PC'de (D: PC envanteri) | Donanım istemez (T) | Şartlar ticari kullanımı engellemiyor görünüyor (K-ikincil) | Kabul (mevcut), kısıtla; yapay zekâ sesi beyanı zorunlu | `Mevcut ancak test edilmedi` |
| Google Flow (Veo) | Hayır | Tarayıcıda (D: depo notu) | Donanım istemez (T) | Ücretsiz kredide "belirsiz" (D: depo notu) | — | `Mevcut ancak test edilmedi` |
| NVIDIA NIM | Hayır: anahtar yok (D) | ? PC'de de anahtar görünmüyor | GPU yok | ? | — | `Mevcut ancak test edilmedi` |
| Higgsfield (MCP) | Evet, yalnız salt okuma (D) | ? | Donanım istemez (T) | Belirsiz: güncel şartlar okunmadı; ikincil kaynaklar çelişiyor | Her kullanımda onay | `Ücretli veya onay gerektiriyor` |
| Higgsfield_Bridge | Bağlı, host 0 (D) | PC eklentisi gerekir | Blender ile sınırda (T) | — | — | `Kullanılabilir ancak kurulum bekliyor` |
| HeyGen, ElevenLabs | Hayır: anahtar yok (D) | ? | Donanım istemez (T) | Ücretsiz planlarda ticari hak yok (görsel raporu; ElevenLabs için D: depo notu) | `text-to-speech` skill'i ret | `Ücretli veya onay gerektiriyor` |
| Modal LTX-2.3, RunPod ACE-Step, BFL | Hayır: anahtar yok (D) | ? | Donanım istemez (T) | ACE-Step modeli MIT (D); diğerleri ? | — | `Ücretli veya onay gerektiriyor` |
| ComfyUI + IP-Adapter + SD / FLUX | Denenmedi; GPU yok | Hayır | **Uyumsuz** | Kod GPL-3 ve Apache-2.0; ağırlık lisansı temel modele bağlı | Ret | `Uyumsuz` |

ComfyUI notu (D: README): 4 GB VRAM + 8 GB RAM ister; Intel desteği Arc kartları içindir. UHD'de ayrık VRAM yok; pratikte CPU'ya düşer (T).
FLUX.1-dev ağırlıklarının ticari olmayan lisanslı olduğu bilgisi doğrulanamadı. IPAdapter_plus 2025-04'ten beri yalnız bakım kipinde (D).

## 2. Hikâye ve senaryo

| Araç | Bulut | PC | PC donanımı | Ticari lisans | Kabul kuralı | Durum |
|---|---|---|---|---|---|---|
| Drive'daki markdown kanon | Evet, salt okuma (D) | Evet: git deposu ve Drive (T) | — | Sahibin kendi içeriği | Kanon kuralı: taslak → onay | `Mevcut ve çalışıyor` |
| Obsidian (BEYIN kasası) | Yalnız Drive üzerinden okuma (D) | Evet: uygulama PC'de (D: depo notu) | ? | Doğrulanmadı | — | `Mevcut ancak test edilmedi` |
| fountain-js 1.2.4 | Evet, scratch (D) | ? | Hafif (T) | MIT (D) | Pin sonrası kabul | `Kullanılabilir ancak kurulum bekliyor` |
| screenplain 0.12.0 | Evet, scratch (D) | ? | ? | MIT (D) | Pin sonrası kabul; `reportlab` de pinlenmeli | `Kullanılabilir ancak kurulum bekliyor` |
| beautiful-mermaid 1.1.3 (kütüphane) | Evet, scratch (D) | ? | ? | MIT; bağımlılığı elkjs EPL-2.0 (D) | Pin sonrası kabul | `Kullanılabilir ancak kurulum bekliyor` |
| extwee 2.3.18 | Evet, scratch, API yolu (D) | ? | ? | MIT (D) | Pin sonrası kabul (ihtiyaç olursa) | `Kullanılabilir ancak kurulum bekliyor` |
| `story-skills` @ `3c0e034` | Yalnız statik okuma (D) | ? | Node ≥18, sıfır bağımlılık (D) | MIT (D) | Koşullu: pin + yayıncı doğrulaması + izole test | `Kullanılabilir ancak kurulum bekliyor` |
| novelWriter | Denenmedi (GUI) | ? | ? | GPL-3 | — | `Kullanılabilir ancak kurulum bekliyor` |
| Manuskript, bibisco | Denenmedi (GUI) | ? | ? | GPL-3 | — | `Gereksiz veya önerilmiyor` |
| Yarn Spinner | Hayır: dotnet yok (D) | ? | ? | MIT | — | `Gereksiz veya önerilmiyor` |
| Aeon Timeline 3, World Anvil, Campfire | Denenmedi: siteleri proxy reddetti | ? | ? | Ticari; fiyat doğrulanmadı | — | `Ücretli veya onay gerektiriyor` |

Notlar: fountain-js bakımsız (son yayın 2023-11). elkjs'i kütüphane olarak kullanmak sorun değil; değiştirip dağıtırsak kaynağını açmak gerekir (D).
Yarn Spinner'ın resmî JS çalışma zamanı yok (D). Aeon, World Anvil ve Campfire ayrıca önerilmiyor: ikinci bir gerçek kaynağı açarlar (T).

## 3. Görsel ve animasyon

| Araç | Bulut | PC | PC donanımı | Ticari lisans | Kabul kuralı | Durum |
|---|---|---|---|---|---|---|
| Remotion 4.0.535 | Evet, scratch'te render (D) | Evet: aynı sürümler `package.json`'da (D) | Çalışır: mevcut üretim hattı (T) | Birey, en çok 3 çalışanlı şirket ve kâr amacı gütmeyen kurum için ücretsiz, ticari dahil (D: LICENSE) | Kabul (mevcut) | `Mevcut ve çalışıyor` |
| `src/puppet/` kukla rig'i | Okundu (D); çalıştırılmadı | Evet: depoda | ? | Sahibin kodu | — | `Mevcut ancak test edilmedi` |
| Rhubarb Lip Sync | Kurulu değil | Kurulu değil (D: depo notu) | ? | MIT; üretilen veri kullanıcının (D) | Pin sonrası kabul: release zip + sha256 | `Kullanılabilir ancak kurulum bekliyor` |
| Inkscape | Kurulu değil (D) | Kurulabilir | İyi (T) | GPL-2.0-or-later (T); çıktı kullanıcının | Pin sonrası kabul: winget sürüm + hash, onay | `Kullanılabilir ancak kurulum bekliyor` |
| Krita | Kurulu değil | Kurulabilir | Çalışır: en az 4 GB RAM, OpenGL 3.0 ya da D3D11 (K-ikincil) | GPL-3 (T); çıktı serbest | Pin sonrası kabul | `Kullanılabilir ancak kurulum bekliyor` |
| Blender | Kurulu değil (D) | Kurulabilir | **Sınırda** | GPL-2.0-or-later (T) | Pin sonrası kabul | `Kullanılabilir ancak kurulum bekliyor` |
| OpenToonz, Synfig, Pencil2D | — | Kurulabilir | İyi (T) | BSD-3, GPL, GPL | Güvenlik raporu incelemedi | `Kullanılabilir ancak kurulum bekliyor` |
| Lottie (lottie-web) | — | ? | İyi (T) | MIT (D) | Güvenlik raporu incelemedi | `Kullanılabilir ancak kurulum bekliyor` |
| Manim CE | Kurulu değil | ? | İyi (T) | MIT (D) | Güvenlik raporu incelemedi | `Kullanılabilir ancak kurulum bekliyor` |
| Rive | — | ? | İyi (T) | Ücretsiz planda dışa aktarma kısıtlı (D: depo notu) | — | `Ücretli veya onay gerektiriyor` |
| Spine | — | ? | İyi (T) | Ücretli, ~69 $ tek sefer (K) | — | `Ücretli veya onay gerektiriyor` |
| Figma (MCP) | Evet, salt okuma (D) | ? | — | — | Dış yazma onay ister | `Ücretli veya onay gerektiriyor` |
| Godot | Hayır: ikili yok (D) | Evet: kanıt çekimi PC'de (D: depo notu) | ? | MIT | godot-mcp daha önce reddedilmiş | `Mevcut ancak test edilmedi` |

Notlar: Blender en az 8 GB RAM ve 2 GB VRAM'li bir GPU ister (K-ikincil); modelleme olur, render yavaş kalır (T).
Rhubarb'ın tanıyıcısı yalnız İngilizce (D). Remotion 5.0 için lisans değişikliği duyurulmuş (D).
Remotion etiketi şuna dayanır: video-studio'daki sürümün aynısı scratch'te render edildi (D). video-studio'nun kendisi bu oturumda render edilmedi.
OpenToonz, Synfig ve Pencil2D gereksiz olabilir: kukla kodu ve Krita aynı işi görüyor (T). Manim maskot için değil, açıklayıcı animasyon için.

## 4. Ses

| Araç | Bulut | PC | PC donanımı | Ticari lisans | Kabul kuralı | Durum |
|---|---|---|---|---|---|---|
| Supertonic 3 | — | Evet (D: depo notu) | İyi (T) | Kod MIT, model OpenRAIL-M (D) | Mevcut bölümlerde kalsın; yeni iş için ret | `Gereksiz veya önerilmiyor` |
| Piper | — | Evet: yalnız EN `ljspeech` | Çok iyi (T) | Program GPL-3.0; her ses ayrı lisanslı (D) | EN kabul; TR `dfki` ret; diğer TR sesleri beklet | `Mevcut ancak test edilmedi` |
| Kokoro-82M | Kurulu değil | Kurulu değil | CPU'da hızlı (K) | Apache-2.0 (D) | Pin sonrası kabul, yalnız İngilizce | `Kullanılabilir ancak kurulum bekliyor` |
| whisper-ctranslate2 | Yok (D) | Evet (D: PC envanteri) | ? | MIT | — | `Mevcut ancak test edilmedi` |
| Kenney, Freesound CC0, YouTube Audio Library | — | Kullanılıyor (D: depo notu) | — | CC0 ya da platforma bağlı | — | `Mevcut ancak test edilmedi` |

## 5. Oyun, web ve sosyal

| Araç | Bulut | PC | PC donanımı | Ticari lisans | Kabul kuralı | Durum |
|---|---|---|---|---|---|---|
| inkjs 2.4.0 (+ `inkjs-compiler`) | Evet, scratch: Node ve headless Chromium (D) | Evet beklenir (T) | Hafif: 128 KB çalışma zamanı (D) | MIT (D) | Pin sonrası kabul; önce tek oyunda pilot | `Kullanılabilir ancak kurulum bekliyor` |
| inklecate | Denenmedi | ? | ? | MIT (D) | Kabul edilebilir ama gereksiz | `Gereksiz veya önerilmiyor` |
| Inky (editör) | — | Masaüstü | ? | Raporlar çelişiyor | — | `Kullanılabilir ancak kurulum bekliyor` |
| Mevcut oyun yığını (Three.js 0.170.0, arena-kit, gate) | Okundu (D); koşulmadı | Evet: depolarda | — | Sahibin kodu | Toplu değişiklik kapısı | `Mevcut ancak test edilmedi` |
| gamedev `dialogue-systems` + `visual-novel` | Statik okuma (D) | ? | — | Apache-2.0 (D) | Pin sonrası kabul; NOTICE korunur | `Kullanılabilir ancak kurulum bekliyor` |
| Dizin sitesi (GitHub Pages + stdlib üretici) | Depo okundu (D) | — | — | — | Mevcut CI ve testler | `Mevcut ancak test edilmedi` |
| Lore sitesi: ayrı depo, aynı desen | — | — | — | Pages ücretsiz (K; sayfa bu oturumda açılmadı) | Yeni depo onay ister | `Kullanılabilir ancak kurulum bekliyor` |
| Astro, Eleventy, Hugo; Vercel; Cloudflare Pages | — | — | — | ? | stdlib kuralından sapma | `Gereksiz veya önerilmiyor` |
| Buffer (MCP) | Evet, salt okuma (D) | Evet: doldurucu betik PC'de (D: depo notu) | — | — | Yazma onay ister | `Mevcut ve çalışıyor` |

Kütüphane pin kuralı (güvenlik): `package.json`'da tam sürüm (`^` yok), lockfile ve bütünlük hash'i tutulur.
Tek dosyalı oyuna gömülecekse CDN + SRI kullanılır; bu, oyunlardaki Three.js deseniyle aynıdır.
inkjs için ölçülen değerler (D): arşiv sha256 `100cf088ef2954927c2a107a42f2154e6b1c0dcea00faf7241b27542e5f88622`; sha512 kayıt defterindeki bütünlük değeriyle aynı.
inkjs paketinde kurulum betiği, bağımlılık ve ağ çağrısı yok (D). Paket tanımında depo alanı boş; köken bakımcı ve lisans dosyasıyla eşleştirildi (D).

## 6. Skill ve plugin'ler

Skill ve plugin'lerin ortam uyumu kendi envanterlerinde: [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md), [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md).
Özet: kilitli 8 Furkiozknn skill'i depo ile birlikte gelir (T). `anthropic-skills:` kovası bir yayıncı değildir; depoya kabul için her skill ayrıca kapıdan geçer.

## 7. Düzeltmeler (güvenlik raporuna göre)

- **ComfyUI.** Görsel raporu "en az 8 GB VRAM" demişti. README 4 GB VRAM + 8 GB RAM diyor. Sonuç değişmiyor: bu PC için uyumsuz.
- **beautiful-mermaid.** Hikâye raporu yalnız "MIT" demişti. Bağımlılığı elkjs EPL-2.0 (zayıf copyleft).
- **Remotion.** Ücretsiz kullanım kâr amacı gütmeyen kurumları da kapsıyor; değerlendirme muafiyeti var.
- **Inky lisansı.** Oyun-web "MIT" diyor; hikâye raporu deponun lisans alanını boş buldu. Güvenlik raporu bakmadı. Lisans yazılmadı.

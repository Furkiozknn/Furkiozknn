# Önerilen araç yığını

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).

İlke: mevcut bir şey işi görüyorsa yeni araç önerilmez. Öneriler çıkarımdır (T); dayandıkları bulgular D ya da K etiketlidir.
Bu yığının hiçbir parçası depoya kurulmadı. Kurulum ve kabul adımları: [NEXT_STEPS.md](NEXT_STEPS.md).
Hattaki yerleri: [CREATIVE_PRODUCTION_PIPELINE.md](CREATIVE_PRODUCTION_PIPELINE.md).

Yapay zekâ notu: bu yığında bugün çalıştığı görülen tek yapay zekâ Claude'dur.
Gemini TTS yığında yer alıyor ama bu oturumda **çalıştırılmadı**; anahtarı yalnız PC'de.

## 1. Alan başına en küçük yığın

| Alan | Önerilen | Neden | Neyin yerine | Maliyet |
|---|---|---|---|---|
| Kanon ve dünya kurma | Mevcut Drive markdown kanonu + git deposu | Zaten var ve iyi kurulmuş; buluttan okunuyor (D) | Notion wiki, World Anvil, Campfire | Ücretsiz |
| Süreklilik | Bağlamsız Claude alt ajanı + stdlib kural betiği + insan | Deneyde 2/2 çelişki, 0 yanlış pozitif (D; kör değildi) | Aeon Timeline; ayrı bir süreklilik servisi | Ücretsiz |
| Süreklilik motoru (değerlendir) | `story-skills`, pinli ve izole testten sonra | Durum modeli kanonun yapısına uyuyor (T; motorun tarifi K: README) | — | Ücretsiz |
| Senaryo | Fountain + fountain-js 1.2.4 + screenplain 0.12.0 | Sahne ve kadro otomatik çıkıyor; Türkçe PDF doğrulandı (D) | afterwriting, betterfountain, Manuskript, novelWriter, bibisco | Ücretsiz |
| İlişki ve akış diyagramı | beautiful-mermaid 1.1.3 **kütüphanesi** | Türkçe etiketli SVG üretti (D) | Aynı adlı kırık skill; Aeon Timeline | Ücretsiz |
| Belge yazımı | `doc-coauthoring` rehberi; isteğe bağlı Claude Docs | "Reader Testing" aşaması süreklilik kapısının hazır şablonu (D: skill metni) | — | Ücretsiz |
| Maskot ana çizimi | Inkscape (ya da Krita) + `params.json` | İnsan çizimi telif için gerekli; SVG doğrudan Remotion'a girer (T) | AI Influencer sayfası, Soul ID, ComfyUI / IP-Adapter | Ücretsiz |
| Karakter tutarlılığı (isteğe bağlı) | Higgsfield Reference Elements | İnsan olmayan maskot için doğru yol (T) | Soul ID, AI Influencer | Ücretli kredi |
| Animasyon | Remotion 4.0.535 + `src/puppet/` + Rhubarb | Kod mevcut; GPU'suz çalışıyor; scratch'te render edildi (D) | Synfig, Pencil2D, OpenToonz, Spine, Rive, LTX-2 | Ücretsiz |
| Ses, Türkçe | Gemini TTS (mevcut) | Türkçe için ana yol; depo zaten kullanıyor (D: depo notu) | HeyGen `text-to-speech`, ElevenLabs, yeni işte Supertonic, Piper `dfki` | Ücretsiz katman |
| Ses, İngilizce (ileride) | Kokoro-82M | Apache-2.0, yerel, CPU'da hızlı (D/K) | — | Ücretsiz |
| Müzik ve efekt | Kenney, Freesound CC0, YouTube Audio Library | Mevcut ve kullanılıyor (D: depo notu) | ACE-Step, ElevenLabs müzik/efekt | Ücretsiz |
| Altyazı | whisper-ctranslate2 (PC) | Mevcut (D: depo notu) | `video-understand`, Azure, ElevenLabs konuşma tanıma | Ücretsiz |
| Video | Mevcut video-studio hattı | 4 kesim, QA listesi ve ses ölçümü zaten var (D: depo notu) | `website-to-video`, `playwright-recording`, HeyGen | Ücretsiz |
| İnteraktif hikâye | inkjs 2.4.0 + `inkjs-compiler` | Tek dosyaya sunucusuz oturuyor; derleyici kırık dalı yakalıyor (D) | Yarn Spinner, kendi JSON grafiği, inklecate | Ücretsiz |
| Oyun anlatı rehberi | gamedev `dialogue-systems` + `visual-novel`, pinli | Ink'e özel rehber mevcut skill'lerde yok (T) | Deponun geri kalan skill'leri | Ücretsiz |
| Lore sitesi | Ayrı depo + GitHub Pages + stdlib üretici | Mevcut dizin sitesiyle aynı desen; 0 bağımlılık (D) | Astro, Eleventy, Hugo, Vercel, Cloudflare Pages, Supabase | Ücretsiz |
| Site tasarımı ve denetimi | Kilitli `frontend-design`, `accessibility`, `performance`, `core-web-vitals` | Kurulu ve doğrulanmış (D) | `web-design-guidelines`, `ui-ux-pro-max`, `tailwind-design-system`, `framer-motion` | Ücretsiz |
| Sosyal | Buffer + video-studio kuyruğu | Mevcut hat işi görüyor (D) | Yeni sosyal araç | Mevcut plan |
| Doğrulama | Kilitli `false-green-gate` + oyun gate'leri | "Yeşil" sonucun gerçek olduğunu kanıtlar | — | Ücretsiz |

Notlar:

- **Inkscape mi Krita mı.** Görsel raporu Inkscape'i öne koyuyor: çıktısı SVG ve Remotion'a doğrudan giriyor. İkisi de PC donanımına uygun (T / K-ikincil).
- **Kendi JSON grafiği** yalnız çok küçük diyaloglarda kabul edilebilir; aksi hâlde dil icat etme riski var (T).
- **extwee** yalnız yazar için görsel dallanma haritası gerekirse düşünülür. Oyuna gömmede Ink daha temiz (T).
- **Blender** ve 3D maskot ilk yığında yok: donanım sınırda. Three.js oyunlarında aynı SVG doku ya da sprite olarak kullanılabilir (T).
- **Threads** kanalı Buffer'da bağlı ama hat kullanmıyor. Eklemek yeni araç değil, bir dil kararıdır.

## 2. Kullanma listesi

| Ne | Neden | Kanıt |
|---|---|---|
| `zenstory-ai/oh-story-claudecode` (özellikle `browser-cdp`) | Chrome profilini ve parola veritabanını kopyalıyor; oturum token'ı çıkarıyor. Kritik | D |
| `anthropic-skills:web-design-guidelines` | Her koşuda uzak `main`'den talimat çekip uyguluyor | D |
| `anthropic-skills:website-to-video` | Pinsiz `npx`; mevcut hatla çakışıyor | D |
| `anthropic-skills:text-to-speech` | HeyGen'e gidiyor; Gemini TTS ile çakışıyor | D |
| `anthropic-skills:ui-ux-pro-max`, `beautiful-mermaid` (skill) | Dosyaları eksik; çalışmıyor | D |
| `anthropic-skills:faceswap` | Gerçek yüz değiştirir; kişilik hakları riski | T |
| gamedev deposunu `npx skills` ya da marketplace ile kurmak | `main`'i çeker; pin yok | D |
| `story-skills`'i `/plugin install` ile kurmak | `main`'i izler. Yalnız elle kopya + pin | D |
| ComfyUI, IP-Adapter, yerel SD / FLUX | PC donanımına uymuyor | D/T |
| Soul ID ve AI Influencer (maskot için) | Gerçek insan kimliği ya da rastgele tasarım içindir | T |
| Supertonic (yeni işte) | Depo arşivlendi; güvenlik yaması gelmeyecek | D |
| Piper `tr_TR-dfki` | Ticari olmayan lisans | D |
| ElevenLabs ve HeyGen ücretsiz planları | Ticari hak yok | Görsel raporu; ElevenLabs için D: depo notu |
| Kling, Dreamina, Hailuo, PixVerse ücretsiz katmanları | Ticari kullanım yasak | D: depo notu |
| Notion, World Anvil ya da Campfire'da ikinci bir kanon | İkinci gerçek kaynağı; süreklilik riskini artırır | T |
| Motion bağlayıcısı (üretim için) | Yalnız okur | D |
| Cloudflare MCP | Kendini kullanım dışı ilan ediyor | D |
| Promptlarda başka eser, stüdyo ya da karakter adı | Özgünlük kuralı; taklit riski | T |
| Higgsfield'daki `Mischief-Cat` öğesini temel almak | Açıklaması stüdyo adları içeriyor | D |

## 3. Maliyet

| Kalem | Bugünkü durum | Kanıt |
|---|---|---|
| Önerilen çekirdek yığın | Lisans ücreti yok; Remotion için alttaki koşul geçerli | D: lisans okumaları |
| Claude oturumları | Raporlarda ölçüm yok | — |
| Remotion | Birey ve en çok 3 çalışanlı şirket için ücretsiz. Daha büyük, kâr amaçlı şirket lisans alır | D: LICENSE |
| Gemini TTS | Ücretsiz katman; depo gözlemi günde ~10 istek. Resmî kota doğrulanamadı | D: depo notu |
| GitHub Pages | Açık depoda ücretsiz | K (sayfa bu oturumda açılmadı) |
| Higgsfield | Bakiye 64,03 kredi. PLUS 49 $/ay 1.000 kredi; ULTRA 129 $/ay 3.000 kredi; ek paket 29,41 $'dan başlar | D: salt okuma |
| Higgsfield kullanım tahmini | 64 kredi kabaca 3-4 karakter sayfası ya da ~10 kısa klip | T |
| Spine | ~69 $ tek sefer; önerilmiyor | K |
| Aeon Timeline, World Anvil, Campfire | Ücretli ya da abonelikli; fiyat doğrulanmadı; önerilmiyor | T |
| HeyGen, ElevenLabs, BFL, Modal, RunPod | Ücretli; fiyatlar raporlarda yok; önerilmiyor | D: skill metni |
| Marka araştırması ve tescili | Maliyet raporlarda yok | — |

Yerel araçlarda veri makineden çıkmıyor. Gemini TTS ve Higgsfield'da çıkıyor: [AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md).

## 4. Önerinin dayandığı üç bulgu

1. Kanon zaten var; eksik olan yeni bir wiki değil, kanonu makinece denetlenebilir kılmak (D/T).
2. Kod tarafı hazır (Remotion, kukla rig'i, tek dosya oyun yığını); eksik olan maskotun kendisi ve insan çizimi ana dosya (D).
3. Kendiliğinden güncellenen ya da çalışma anında uzaktan talimat çeken hiçbir şey kabul kapısından geçmiyor (D).

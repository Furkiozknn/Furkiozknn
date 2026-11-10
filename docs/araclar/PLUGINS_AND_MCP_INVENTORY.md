# Plugin ve MCP envanteri

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).

Her MCP'ye yalnız **salt okuma** çağrısı yapıldı (D). Hiçbir dış sisteme yazılmadı: gönderi, fikir, dosya, proje ya da şema oluşturulmadı.
Çağrı sonuçlarındaki kişisel içerik bu belgeye alınmadı.
Etiket bu proje açısından verilir; bağlantısı çalışan bir araç "gereksiz" etiketi alabilir.

## 1. Bağlı MCP sunucuları (claude.ai bağlayıcıları)

| MCP | Salt okuma testi (D) | Bu projede işe yaradığı yer | Onay gerektiren | Durum |
|---|---|---|---|---|
| GitHub | `get_me` → çalıştı; 23 açık depo | Depolar ve PR'lar; lore sitesi için yeni depo (T) | Yazma araçları, yeni depo | `Mevcut ve çalışıyor` |
| Google Drive | `search_files`, `read_file_content` → çalıştı; `osmanli-evreni/` ve BEYIN kasası okunuyor | Kanonu ve Obsidian kasasını buluttan okumak (PC kapalıyken de) | Yazma. Bu bağlantıda bütün dosyalar `canEdit:false` | `Mevcut ve çalışıyor` |
| Notion | `notion-get-self` → çalıştı (1 çalışma alanı); evren/karakter araması → 0 sonuç | Yok. Kanon Drive'da markdown; ikinci bir gerçek kaynağı süreklilik riskini artırır (T) | Her yazma | `Gereksiz veya önerilmiyor` |
| Gmail | `list_labels` → çalıştı | Raporlar rol tanımlamadı | Gönderme, taslak | `Mevcut ve çalışıyor` |
| Google Calendar | `list_calendars` → çalıştı (2 takvim) | Raporlar rol tanımlamadı | Yazma | `Mevcut ve çalışıyor` |
| Slack | `slack_search_channels` → çalıştı, 0 sonuç; semantik arama kapalı | Raporlar rol tanımlamadı | Gönderme | `Mevcut ve çalışıyor` |
| Asana | `get_me` → çalıştı (1 çalışma alanı) | Raporlar rol tanımlamadı | Yazma | `Mevcut ve çalışıyor` |
| Microsoft Learn | `microsoft_docs_search` → 10 sonuç | Raporlar rol tanımlamadı | Yok (salt okuma) | `Mevcut ve çalışıyor` |
| Figma | `whoami` → çalıştı; plan "starter", koltuk **View** | Maskot: vektör çizim, turnaround ve ifade sayfasını bileşen/varyant olarak kurma, renk değişkenleriyle paleti kilitleme, `export_video` (K: araç listesi) | Dosya oluşturma (dış yazma). View koltuğunda düzenleme sınırlı (T) | `Ücretli veya onay gerektiriyor` |
| higgsfield | `balance` ve aşağıdaki okuma çağrıları → çalıştı | Reference Elements, `character-sheet`, tanıtım klibi, görselden 3D | Her üretim kredi harcar; depo ayarında bütün `mcp__higgsfield` araçları "sor" kuralında | `Ücretli veya onay gerektiriyor` |
| Higgsfield_Bridge | `get_host_status` → bağlı, **host 0** (After Effects, Premiere, Blender, Cinema 4D, 3D Studio hepsi `false`) | PC'de Blender açılırsa sahne kurma (T) | PC'de Higgsfield eklentisi kurulup bağlanmalı | `Kullanılabilir ancak kurulum bekliyor` |
| Buffer | `get_account`, `list_channels` → çalıştı; 1 organizasyon, 4 bağlı kanal | Sosyal kuyruk (mevcut hat) | Gönderi ya da fikir oluşturma | `Mevcut ve çalışıyor` |
| Vercel | `get_auth_user` → **404 `User not found`**; `list_teams` → 1 takım; `list_projects` → 0 proje | Yok. GitHub Pages yetiyor | Her yazma | `Gereksiz veya önerilmiyor` |
| Supabase | `list_organizations`, `list_projects` → çalıştı; 1 organizasyon, 1 aktif proje | Yalnız sunucu tarafı ihtiyaç doğarsa (ör. seçim istatistiği). GoatCounter olayları daha basit (T) | Yazma, şema değişikliği; kişisel veri ve KVKK yükü | `Gereksiz veya önerilmiyor` |
| Cloudflare | Doküman araması ve `workers_list` → çalıştı, 0 Worker. Sunucu kendini **DEPRECATED** ilan ediyor | Yok | Yeni hesap ya da izin | `Gereksiz veya önerilmiyor` |
| Motion | `list_chats` → 1 sohbet; `get_motion_features` → `read_only: true` | Yok. Bağlayıcı yalnız okur; üretim Motion uygulamasında | Yok (salt okuma) | `Gereksiz veya önerilmiyor` |
| Claude Docs | `guide` → kılavuz döndü; hiç belge yok | Paylaşılan, yorumlanabilir belge: kanonun okunur sürümü, senaryo (T) | Belge oluşturma | `Mevcut ancak test edilmedi` |

Notlar:

- **higgsfield okuma çağrıları (D):** `show_plans_and_credits`, `show_characters`, `manage_reference_elements` (liste), `models_explore` (öneri), `get_workflow_instructions` (`character-sheet`), `ai_influencer_get_options`, `ai_influencer_list_presets`, `list_voices`. Fiyat veren `ai_influencer_prepare` çağrılmadı. Bulgular: [AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md).
- **Buffer (D):** kanallar threads, X, youtube ve instagram. Threads bağlı ama video hattı onu kullanmıyor; kuyruk yalnız youtube, instagram ve X için.
  Hesapta saat dilimi boş (`timezone: null`). Mevcut doldurucu +03:00 yazıyor; yeni bir otomasyon hesabın saatine güvenmemeli (T).
- **Cloudflare:** envanter iki okuma çağrısı yaptı (D). Oyun-web araştırmacısı sunucu kendini kullanım dışı ilan ettiği için hiç çağırmadı.
- **Claude Docs:** yalnız kılavuz çağrısı yapıldı. Belge oluşturmak dış yazma sayıldığı için denenmedi.
- **Figma:** dosya oluşturma ve üretim araçları denenmedi.

## 2. Bağlanamayan plugin MCP'leri

Üçü de `Kullanılabilir ancak kurulum bekliyor`. Neden: oturum proxy'si bu hostlara bağlantıyı reddediyor (403).

| Plugin (sürüm) | Skill'leri | Engel (D) | Bu projede rolü |
|---|---|---|---|
| canva 1.0.0 | brand-check, bulk-create, edit-design, get-design-feedback, implement-feedback, resize-for-social-media | Proxy 403; ayrıca yetkilendirme bekliyor | Raporlar rol tanımlamadı |
| dropbox 1.0.1 | find, inspect, organize, share, clean-up, collect | Proxy 403 | Raporlar rol tanımlamadı |
| tinyfish 1.4.0 | agent, fetch, search, monitor, doctor, feedback | Proxy 403; `TINYFISH_API_KEY` ortamda yok | Raporlar rol tanımlamadı |

Kanıt (D): proxy durum çıktısında Dropbox ve Canva hostları için "gateway answered 403 to CONNECT" kaydı var.
Ortamın ağ ayarı `limited`, izinli host listesi boş, MCP sunucularına izin açık.
claude.ai bağlayıcıları çalışıyor; plugin MCP hostları reddediliyor. Host eklemek sahibin onayını ister.

## 3. Diğer plugin önbellekleri (D)

Hepsi aynı pazardan (`knowledge-work-plugins`) geliyor.

| Plugin (sürüm) | İçerik | Durum | Neden |
|---|---|---|---|
| fastly-agent-toolkit 0.1.0 | 10 skill (CDN, VCL) | `Gereksiz veya önerilmiyor` | Yaratıcı işle ilgisi yok |
| vpai 0.1.107 | vibe-prospecting | `Gereksiz veya önerilmiyor` | B2B satış verisi |
| grasp 1.5.1 | 6 skill (tablo zenginleştirme, şirket arama) | `Gereksiz veya önerilmiyor` | Diskte var ama kapalı; oturumda yüklü değil |
| cowork-plugin-management 0.2.2 | create-cowork-plugin, cowork-plugin-customizer | `Uyumsuz` | Cowork modu gerekir |

## 4. Yerleşik özellikler

| Özellik | Kanıt (D) | Yaratıcı işte olası kullanım (T) | Onay gerektiren | Durum |
|---|---|---|---|---|
| Claude Artifacts | Liste: 4 yayın, sonuncusu 27 Eki | Karakter/dünya sayfası, interaktif hikâye prototipi | Raporlarda yok | `Mevcut ve çalışıyor` |
| Alt ajanlar | Bu araştırma alt ajanlarla yürüdü | Paralel araştırma, bağlamsız süreklilik denetimi | Yok | `Mevcut ve çalışıyor` |
| Zamanlanmış görevler | 2 görev var; ikisinin de son çalışması `ACCESS_DENIED` ile başarısız | Haftalık süreklilik denetimi | Önce izin sorunu çözülmeli | `Kullanılabilir ancak kurulum bekliyor` |
| Remote Control / A oturumu | Oturum listesi çalıştı; A oturumu boşta. İki PC klasörü `cannot_be_used / not_available` | Gemini TTS ve Veo işini PC'ye devretmek | Mesaj göndermek PC'de iş başlatır (T); gönderilmedi | `Mevcut ancak test edilmedi` |
| computer-use-desktop | Konteynerde kurulu | Konteynerde GUI aracı denemek | Yok | `Mevcut ancak test edilmedi` |

## 5. Değerlendirilip alınmayan MCP'ler

| MCP | Neden | Durum |
|---|---|---|
| `alexmeckes` godot-mcp | PROVENANCE'ta "kimliksiz RCE" gerekçesiyle zaten reddedilmiş (D) | `Gereksiz veya önerilmiyor` |
| Obsidian MCP seçenekleri (`coddingtonbear/obsidian-local-rest-api`, `MarkusPfundstein/mcp-obsidian`; ikisi de MIT) | PC'ye bağlı; bulutta işe yaramaz. Drive MCP okuma yolunu zaten veriyor (T) | `Gereksiz veya önerilmiyor` |

## 6. İzin yapılandırması (D)

- Hiçbir depoda proje düzeyinde `.mcp.json` yok. claude.ai bağlayıcıları sunucu tarafından geliyor (T).
- Furkiozknn `.claude/settings.json` "sor" kuralları: git tag ve `main`'e push, GitHub yazma araçları, Slack gönderme, Calendar yazma ve bütün `mcp__higgsfield` araçları.

## 7. Onay gerektirenlerin özeti

- **Kredi harcayan:** higgsfield üretim araçlarının tümü.
- **Dış sisteme yazan:** Buffer gönderi/fikir, Figma dosya, Notion sayfa, Claude Docs belge, Drive dosya, Slack mesaj, Gmail, Calendar, Asana.
- **Hesap ya da izin değiştiren:** oturum ağına host eklemek (Canva, Dropbox, TinyFish), Figma koltuğunu yükseltmek, PC'ye Higgsfield eklentisi kurmak, zamanlanmış görevlerin izin sorununu çözmek.
- **Depo açan:** lore sitesi için yeni GitHub deposu.

Sıralı adımlar: [NEXT_STEPS.md](NEXT_STEPS.md).

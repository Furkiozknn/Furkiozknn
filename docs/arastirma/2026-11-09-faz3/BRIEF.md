# Faz 3 ön araştırması — oyun başına derin inceleme (brief)

Sen tek bir oyunu araştırıyorsun. Amaç: bir sonraki güncelleme turunda bu oyuna **neyin eklenmesi, neyin değiştirilmesi, neyin kesinlikle eklenmemesi** gerektiğini kanıta dayalı olarak belirlemek. **Kod değiştirme, commit atma, push yapma.** Yalnız oku, çalıştır, ölç, araştır, rapor yaz.

## Bağlam
- 21 tek-dosyalık tarayıcı oyunu (çoğu Three.js r170, import map + SRI). GitHub Pages'te yayında, ücretsiz, sunucusuz, hesapsız. Türkçe + İngilizce.
- Repo: `/home/user/<oyun>` (origin/main'e eşit, dal `claude/cloud-session-research-analysis-dufc2b`). Ana dosya `index.html`; varsa `README.md`, `DESIGN.md`, `docs/`, `tools/`, `tests/`, `project-meta.json`, `CHANGELOG.md` oku.
- Bugün eklenenler (zaten var, tekrar önerme): oyunun **imza mekaniği** (git log'da "oynanis:" commit'i), **arena-kit** (`/*ARENA-KIT:BEGIN…END*/` bloğu: `Arena.perf`, erişilebilirlik paneli, günlük meydan okuma + seri, paylaş, rozetler/pasaport, "başka oyun"). `git log --oneline -30` ile son değişiklikleri gör.
- Kısıtlar (öneriler bunlara uymalı ya da açıkça "kısıtı aşar" diye işaretlenmeli): tek dosya kalmalı; sunucu/hesap/ücretli servis yok; kullanıcı verisi toplanmaz; harici ağ çağrısı yok (CDN modülleri hariç); importmap/integrity/CDN satırları ve ARENA-KIT bloğu düzenlenmez; eski kayıtlar yüklenmeye devam etmeli; `?auto` botu çalışmaya devam etmeli; 8 GB RAM'li Intel UHD dizüstünde akıcı olmalı; telefon (dokunmatik, dikey) desteklenmeli.
- Gerçek bir oyunun adını, karakterini, sanatını, müziğini, bölümünü kopyalayan öneri yapma (tür/mekanik benzerliği serbest).

## Yöntem (hepsini yap, her bulguya kanıt etiketi koy: **D** = doğrulandı/ölçtüm, **T** = tahmin/çıkarım, **K** = dış kaynak)
1. **Kod okuması:** oyun döngüsü, ilerleme yapısı, zorluk eğrisi, kayıt biçimi, bot, i18n, mobil kontroller, ses, performans ayarları. Satır numarası ver.
2. **Çalıştırma (hafif):** headless Chromium ile 1-2 kez aç (Playwright: `require('/home/user/pamukkale/node_modules/playwright')`, argümanlar `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`; CDN'i yerelden servis etmek için `tools/smoke.mjs`'in yöntemini oku, yerel kopya: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/cdn/x/package`). Konsol hataları, ilk 30 saniyede oyuncunun ne gördüğü, 390×844 telefon boyutunda düzen, varsa `?auto` ile bot ilerlemesi. 1-3 ekran görüntüsü al. Uzun koşu yapma (makine paylaşımlı, 4 çekirdek).
3. **Dış araştırma (web):** aynı türdeki iyi bilinen oyunların ve tasarım kaynaklarının ne yaptığı (tutundurma, ilk deneyim, zorluk, mobil, erişilebilirlik, tarayıcı oyunu portalı beklentileri). Kaynak URL'si ver. Kopyalama değil, ilke çıkar.
4. **Değerlendirme:** her aday fikir için değer (oyuncuya ne kazandırır), maliyet (S/M/L), risk (performans, karmaşıklık, kayıt uyumu, bot, mobil), kısıta uyum.

## Rapor biçimi — dosya: `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/<oyun>.md` (Türkçe, en fazla ~250 satır)
```
# <Oyun adı> — faz 3 araştırması
## 1. Şu anki durum (özet, 5-10 madde, kanıt etiketli)
## 2. Güçlü yanlar (korunmalı)
## 3. Sorunlar / zayıf yanlar (öncelik sırasıyla; hata varsa adım + kanıt)
## 4. EKLENMELİ — yüksek değer (her biri: ne, neden, nasıl (kısa teknik plan), maliyet S/M/L, risk, kanıt/kaynak)
## 5. EKLENEBİLİR — orta değer / koşullu
## 6. EKLENMEMELİ — oyunu kötüleştirir ya da kısıtı aşar (neden)
## 7. Düzeltilmeli (hata, cila, erişilebilirlik, performans)
## 8. Önerilen ilk 3 iş (sıralı, gerekçeli)
## 9. Doğrulanmayanlar / açık sorular
## Kaynaklar
```
Ayrıca son mesajında rapordaki "Önerilen ilk 3 iş"i ve en kritik 1-2 sorunu kısa yaz.
Kendi geçici dosyalarını `/tmp/claude-0/-home-user/4b846529-5eac-58c3-8994-b971516c8072/scratchpad/arastirma/_<oyun>/` altında tut. Repoda hiçbir dosyayı değiştirme (git status temiz kalmalı); `tools/node_modules` symlink'i açarsan sonunda kaldır.

# Faz 3 kararları (9 Kas 2026)

Kullanıcı (9 Kas, ~20:30Z): "en iyisini sen seç, sen karar ver, ben onay veriyorum". B, derleme README §7'deki 12 soruyu aşağıdaki gibi karara bağladı. İlke: **geri alınabilir, en az bozan, kanıtla doğrulanan seçenek**. Kullanıcı herhangi birini sonradan değiştirebilir.

| # | Konu | Karar | Gerekçe |
|---|---|---|---|
| 1 | GoatCounter (20 oyun) / Google Fonts (18) | GoatCounter **kalır, açık istisna olarak yazılır** (çerezsiz sayfa sayacı, kullanıcının bilinçli eklentisi). Google Fonts **kalır**; yalnız gereksiz olduğu kanıtlanan yerde (peri-golf: Fredoka zaten yerelde) kaldırılır. Her oyunda yazı tipi yüklenmezse `system-ui` yedeği bulunması dalga 2'de denetlenir. | Kaldırmak ziyaretçi verisini ve 18 oyunun görünüşünü değiştirir; geri dönüşü kullanıcıya pahalı. Brief kısıtı buna göre güncellenir. |
| 2 | Günlük gün anahtarı | **(c)** kit v1.0.1 `Arena.daily(game, {dayKey})` alır. Varsayılan UTC kalır; kendi günlüğü yerel gece yarısında dönen oyunlar (cini, fay, kapadokya, marti) `Arena._core.localDayKey()` geçer. | Mevcut seriler bozulmaz, her oyun kendi günüyle tutarlı olur. |
| 3 | Kit v1.0.1 | **Evet**: `?auto` / `?nosave` / `?demo` iken kit localStorage'a hiç yazmaz (`Arena.quiet`). Pilot (hamsi) → degisim → 21 oyun. | Botlar oyuncunun profilini/serisini kirletiyordu (D). |
| 4 | Yazı boyutu kaydırıcısı | Dalga 2'de **(a)**: önce HUD/kart fontları `--arena-text-scale`'e bağlanır, oyun oyun; bağlanmayan oyunda o zamana kadar kaydırıcı olduğu gibi kalır. | Erişilebilirlik vaadi gerçek olmalı; gizlemek geri adım. |
| 5 | Geri alınmamış eski "UI REBIRTH" commit'leri | **(a)** yalnız ölçülen sorunlar onarılır (telefon HUD taşması vs.). Toplu revert yok. | Büyük revert başka şeyleri de geri alır; onarım dar ve test edilebilir. |
| 6 | Kale zırhı | **(a)** yumuşak sayaç kalır (kod bugün böyle, bot 15. dalga), README düzeltilir. | Denge zaten ölçülü; tam bağışıklık 9 Kas'ta oyunu bozdu (D). |
| 7 | fay-hatti kartları | **(b)** sade: kart her 3 tahtada bir gelir; yalnız kozmetik (bölge/tema) kartı kalıcı yazar ve menüden "otomatik" seçeneğine dönülebilir. Günlükte ipucu: **hayır** (günlük herkes için eşit). | Biome hatasını kökten çözer, döngü anlamsızlığını azaltır. |
| 8 | Mehter | **Evet**: Kolay varsayılan + seçilen zorluk kaydedilir; "Ruh tükenmez" seçeneği (açıkken rekor/rozet yazılmaz). Kolay rekorları **ayrı anahtarda**. | Yeni oyuncu 2 sn'de kaybediyor (D); eski rekorlar bozulmaz. |
| 9 | Pamukkale 3★ | **(c) önce test**: "su akarken yerleştirme" ile 3★'ın mümkün olup olmadığı çözücüye eklenip ölçülür; imkânsız kalan seviyelerde **(a)** veri (par/envanter) ayarlanır. | Tasarımı bozmadan kanıta göre karar. |
| 10 | Titreşim anahtarı | **(a)** yalnız anlamlı yerlerde az haptik: marti (çarpma), peri (topun deliğe düşmesi), ebru (damla) — kit anahtarına bağlı. Diğer oyunlarda anahtar zararsız kalır. | Ayar işlevsel olur, abartı yok. |
| 11 | Revert edilen fikirler (tek el auto-run, oto-nişan) | **Kapalı.** carsi tek el modu ve topkapi oto-nişan yeniden yapılmaz; topkapi'de bunun yerine **sürükleyerek nişan** (araştırma önerisi) dalga 3'te. | Raporlar oto-nişanın zararlı olduğunu ölçtü (D). |
| 12 | Hayalet/rekor kayıtları | **Kabul**, oyun başına ≤10 KB localStorage, sürümlü anahtar, try/catch. | Sunucusuz, kişisel veri yok. |

Ek: **merge politikası** (A ile anlaşıldı): relay/worker çıktısı PR + smoke + (dalga 0'dan sonra) `tools/gate.mjs` olmadan main'e girmez.

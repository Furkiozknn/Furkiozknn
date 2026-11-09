# Faz 3: 21 oyunun değerlendirilmiş derlemesi (revert sonrası)

Kaynak: `arastirma/<oyun>.md` raporları (21 adet). Etiketler: **D** = doğrulandı/ölçüldü, **T** = tahmin/çıkarım, **K** = dış kaynak.
Raporlar `main`'i 9 Kasım ~16:20-17:50Z arasında birleşen 45 incelenmemiş "relay: … (gemini gemini-3.5-flash-lite, N edits)" commit'i varken inceledi. Bu commit'ler artık her oyunda tek bir `revert: undo N unreviewed gemini-worker commits from 9 Nov` commit'iyle geri alındı: 19 oyun, toplam 45 commit. fay-hatti ile mehter'de bu commit'lerden yoktu.
**Sınıflandırma yöntemi:** her oyunda `git fetch origin main` yapıldı. Ardından raporun alıntıladığı kod parçası `git show origin/main:index.html` içinde grep ile arandı (kopyalar `_derleme/<oyun>.main.html`). Parça yoksa **GİTTİ**, varsa **DURUYOR**, ucuz yoldan anlaşılamıyorsa **BELİRSİZ** dendi.
**Önemli:** daha eski "agy gemini" relay commit'leri (ör. "RADICAL UI/UX REBIRTH" 651c5b4, 7e52007, 3bcebe6, cc7c4a8; fay-hatti'nin kart sistemi) geri **alınmadı**. Bunlardan gelen sorunlar hâlâ duruyor.

## 1. Özet

- Raporlardaki kritik ve sorun bulgularının yaklaşık **59'u revert ile ortadan kalktı (GİTTİ)**. Kalanların çoğu eski tasarım ya da düzen sorunu ve 9 Kasım relay'inden önce de vardı. Kanıt grep ile `origin/main` üzerinde alındı.
- **En önemli 5 bulgu:**
  1. **Telefonda HUD taşması hâlâ duruyor**, kaynağı geri alınmamış "UI REBIRTH" commit'leri. Kale'de barikat ve duraklat ekran dışında (D), Lale'de bazar, katalog ve duraklat ekran dışında (D), Simit'te saat ve kasa okunmuyor (D). 15+ oyunda benzer taşma var.
  2. **Arena-kit'in erişilebilirlik ayarlarını oyunlar okumuyor (D, grep, kit dışı kod).** Yazı boyutunu (`--arena-text-scale`) **21 oyunun hiçbiri** kullanmıyor. `reducedMotion`'ı 11 oyun JS'te hiç okumuyor. `Arena.hint` ve `Arena.announce`'u hiçbir oyun çağırmıyor. Titreşim anahtarı 20 oyunda boşta, çünkü oyun kodunda `vibrate` çağrısı yok.
  3. **Kit sorunları:** `?auto` açılışta bile `arena.profile.v1`'e yazıyor (`touchProfile()` boot'ta, korumasız; D, kit 21 oyunda birebir aynı). Kit günü UTC ile sayıyor, en az bir oyun yerel günle sayıyor (cini, D) ve 3 oyunda yerel gün anahtarı var (fay, kapadokya, marti; etkisi BELİRSİZ).
  4. **Doğrulama kapısı yok.** Smoke testi yalnız "sayfa yükleniyor" kontrolü yapıyor. Relay hataları "verified by verify_merge.py" etiketiyle main'e girdi. Neredeyse her oyunda deterministik sim ya da bot var, ama hiçbiri eski/yeni karşılaştırması yapan bir kapıya bağlı değil.
  5. **Oyun başına gerçek hatalar duruyor:** fay-hatti'de bölge kartı haftalık rotasyonu kalıcı donduruyor, Kırkpınar'da `L` maç ortasında dili değiştiriyor, Ebru'da pinch boya döküyor (relay'den önce de vardı), Çay Ocağı'nda Low modda kartlar okunmuyor, Pamukkale'de birçok seviyede 3. yıldız imkânsız ve dil değişimi yarım kalıyor, Mehter'de yeni oyuncu 2 sn'de kaybediyor.
- Harici çağrılar: **GoatCounter 20/21** oyunda var (fay-hatti hariç), **Google Fonts 18/21** oyunda var (fay-hatti, hamsi, kervan hariç). Brief'teki "harici ağ yok" kısıtıyla çelişiyor; karar kullanıcıda.

## 2. Revert sonrası durum

| Oyun | GİTTİ | DURUYOR kritik/önemli sorunlar (kısa) |
|---|---|---|
| bogaz-vapuru | 9 (vites kilidi, görünmez ağ, halat/Boşluk, i18n, tuş etiketi, toast yağmuru, 30 fps kilidi, RPM metni, bot 0★) | Şimşek `lightning*3` sahne flaşı + reducedMotion yok; "NEXT PIER"/"BİLET / VOUCHER" çakışması (cc7c4a8); ağır ilk deneyim |
| carsi-kacisi | 4 (coyote duvar saati, auto-run kilidi, telefonda yanal kontrol yok, hold→zıplama) + 1 BELİRSİZ | 20 bölüm yarısının 16'sı tekrar; rüzgâr etkisiz (T); başlıkta klavye metni (D); HUD dil düğmesi taşması BELİRSİZ |
| cay-ocagi | 3 (martı 80 px yarıçapı, ölü `arena-shake`, dock kahve halkası) | **Low modda kart kontrastı ~1:1** (D, `body.low .glass` s.499); sonsuz vardiya 9. günde kapasite duvarı; `?selftest` tek başına FAIL; toast'lar aria-live değil |
| cini-ustasi | 2 (alt çubuk fırın/tamamlama kartını örtüyor; bitince işlevsiz düğmeler) | Klavyeyle oynanmıyor; 28/30 seviye renge dayalı; `.scoreRow` taşması (`min-width:84px` D); yerel gün ↔ UTC seri |
| dolmus | 2 (jeton sarsıntısı, çift `#hurt`) | Radyo açıkken baloncuk durağı söylemiyor; `HOOK.shake` reducedMotion'ı okumuyor (D); `--barh` bayat (ResizeObserver yok, D); "OYNA" kaydı onaysız siliyor (D) |
| ebru | 1 (çift görünürlük handler'ı) | **Pinch damla bırakıp vuruş sayıyor** (D, s.3838-3842; relay'den önce de vardı); dışa aktarma yok; günlük 18 sabit dersten biri |
| fay-hatti | 0 (gemini-flash-lite commit'i yoktu) | **Bölge kartı biome'u kalıcı yazıyor** (D, `applyBiome`); kartlar hiçbir şey açmıyor; menü 24 düğme; senkron "Tohum Doğrulama" donması |
| hamsi | 4 (lidaki cezası, terim gerilemesi, ölü PWA, flaş) | Dikey telefonda sonar ~140 px (D, CSS s.150); dokunmatikte "daireyi kapat" ipucu gizli (D s.121); README x3/x4 (D) |
| kale-savunmasi | 5 (zırhta 0 hasar, "Blocked"/"0" etiket havuzu, alt sayfa, `?auto` hint yazımı, DOM can çubuğu) | **Telefonda `#topControls` ekran dışında: barikat ve duraklat yok** (D, ≤760 px'te `flex-wrap` yok, 651c5b4); README "Armour negates… completely" ama kod %55 azaltıyor |
| kapadokya-balonu | 2 (zarf neon parlaması, ayarsız titreşim) | Altın Saat düğmesi alet panelini örtüyor (0c9ee93, relay değil); vizörde dokunmatik brülör/supap gizli (D); dokunmatikte "(Boşluk)" metni (D) |
| karagoz | 3 (ton sızıntısı, her kare `matchOf`, ölü PWA) | Vuruş sahnelerinde telefon HUD'u taşıyor (T: mum ışığı commit'i); oyuna giriş 2 tık + 3 sn; tek kademeli ipucu |
| kervan | 3 (`isLowSpec`, mal başına "Hepsini sat", 2,2× dokunma alanı) | Bot imza mekaniğini (söylenti) kullanmıyor; README "12 of 12" ama tohum 6 iflas (D); telefonda arayüz ekranın %34'ü; i18n sızıntıları (D) |
| kirkpinar | 1 (üçlü kariyer düğmesi) + 1 BELİRSİZ (960×540 başlık taşması) | **`L` tek oyunculu maçta dili değiştiriyor** (D s.4038); `#subs div` iç içe kutu telefonda ekranı kapatıyor (D); koç dokunmatikte F/G/S/R gösteriyor (D) |
| lale-bahcesi | 2 (Divan ad çakışması, yanlış melez ipucu) | **Telefonda bazar, katalog ve duraklat ekran dışında** (D, `.stats{flex-wrap:nowrap}` s.1063, 7e52007); sonsuz bahçe yenilemede kayboluyor (D); ilk çiçek 5 dk |
| marti | 5 (anında su ölümü, "undefined" kartı, SW 404, dokunmatik dalış/♿ çakışması, ölü `deathCause`) | Kamera sarsıntısı reducedMotion'ı okumuyor (D); günlük rüzgâr `Math.random` (D s.3745); telefon başlığında Günlük düğmesi kesik (BELİRSİZ) |
| mehter | 0 (gemini-flash-lite commit'i yoktu) | **Yeni oyuncu 2,15 sn'de kaybediyor** (Normal varsayılan); şerit tuşu M/X/L/P çakışması; telefon HUD'u; `LANE_LAYER` ölü (D) |
| mimar-sinan | 4 (6 kat çöküş paneli, ağır çekim/kamera, renk körlüğü eşiği, `simState` sızıntısı) | 390 px'te tepsi-lejant çakışması (lejant relay'den değil, D); günlük kilitli geç siparişi açıyor (D s.2689); ipucu bedava |
| pamukkale | 1 (blob SW) | **Seviye 2, 5, 6, 8, 11, 12, 16'da statik yerleştirmeyle 3★ imkânsız** (D, tarama); `const L` sabit, dil değişimi yarım (D s.1172); süre görünmüyor; "20 levels" (D) |
| peri-golf | 3 (blob SW, iptal eşiği, sunk'ta yeniden başlat) | Google Fonts gereksiz (Fredoka yerel); README 18/23 ama ölçülen 14/20; günlük rüzgârı etkisiz |
| simit-firini | 2 (ölü fırın alarmı, yanlış ve sınırsız uçan para) | **Telefon HUD'u bozuk** (D, `flex-wrap: nowrap` s.213/224, 3bcebe6); itibar dökümü yok; 12. günden sonra para anlamsız; etiketler çakışıyor |
| topkapi-gecesi | 3 (`throwPebble` ReferenceError, oto-nişan, sw.js 404) | Telefonda görev çubuğu yıldızları kesiliyor; günlük 9 sabit görevden biri; GoatCounter |

## 3. Ortak sorunlar ve ortak çözümler

**3.1 Bot tabanlı regresyon kapısı (smoke yalnız "yükleniyor" diyor)**
- Etkilenen: 21/21. Somut kanıt: bogaz (bot 3★ → 0★), kale (dalga 15 → 8), hamsi (ekonomi), marti (bot dalmıyor, su ölümünü kaçırdı), ebru (pinch), mimar (panel ×6), topkapi (dokunmatik taş). Hepsi smoke ya da `verify_merge.py`'den geçti (D, raporlar).
- Yaklaşım: her repoda `tools/gate.mjs` olsun. Oyunun kendi sim'ini `origin/main` (taban) ve aday için koşsun, ölçüleri eşikle karşılaştırsın. Hazır kancalar: `vapurSim`, `carsi.sim`, `cayBench`/`?selftest&auto`, `tests/core.test.mjs`, `dolmusSim`, `ebruSim`, `tools/sim.mjs`+`cardcheck.mjs`, `hisarSim(1260)`→15/522/218, kapadokya CORE (Node), `kervan` Node sim, `kirkpinarSim`, `laleSim`, `martiSim`, mehter `?sim`, `test-levels.js`, `solve-levels.mjs`, `periGolfSim`, simit SIM+BOT (Node), `topkapiSim`/CORE.
- Bot'un yürümediği yollar için senaryo testleri: marti dalış, ebru sentetik pinch, kale `?auto` sonrası localStorage boş, topkapi dokunmatik taş.
- Ortak ek: 360/390/412×(740-900) ve 844×390'da "her `button` `getBoundingClientRect` içinde ve `elementFromPoint` kendisi" assert'i.
- Maliyet: kit/ortak şablon **S**. Oyun başına **S-M** (21 × 1-3 saat). Toplam **L**. Yer: her oyunun `tools/`'u + CI. `index.html`'e dokunulmaz. Merge kuralı: relay ya da ajan commit'i bu kapıdan geçmeden main'e girmez.

**3.2 Telefon üst çubuk/HUD taşması**
- DURUYOR (D): kale (kontroller ekran dışında), lale (araç düğmeleri dışarıda), simit (saat/kasa), dolmus (bayat `--barh`), mehter (Kombo/İsabet), karagoz (vuruş sahneleri), kapadokya (Altın Saat örtüşmesi, yıldızlar), topkapi (yıldızlar, görünürlük paneli), pamukkale (stats-pill + tahta sığmıyor), peri (ilerleme noktaları), cini (`.scoreRow`), mimar (tepsi-lejant), hamsi (sonar 140 px), kervan (%34 arayüz), bogaz (VOUCHER).
- BELİRSİZ: carsi (auto-run hâlinde ölçüldü), cay (dock relay'i geri alındı, yeniden ölçülmeli), marti (başlıkta Günlük düğmesi).
- Ortak kök: UI REBIRTH commit'leri `nowrap` koydu, yükseklik ise yalnız resize'da ölçülüyor.
- Yaklaşım: ≤760 px'te `flex-wrap:wrap` ve ikincil düğmeler (ses/dil) duraklat menüsüne taşınsın. `ResizeObserver` + `document.fonts.ready` ile `--hud-h` güncellensin. Dokunmatikte hedef ≥44 px. Doğrulama 3.1'deki assert ile.
- Maliyet: oyun başına **S**, 15 oyun ≈ **M**. Yer: her oyun (CSS ağırlıklı).

**3.3 Arena-kit ayarlarını oyunun okumaması**
- `--arena-text-scale`: 0/21 oyun kullanıyor (D). Kit kaydırıcısı hiçbir oyun HUD'unu büyütmüyor.
- `reducedMotion` JS'te hiç okunmuyor (D, kit dışı grep = 0): bogaz, carsi, cay, cini, dolmus, kervan, marti, mehter, mimar, pamukkale, peri. Okuyan oyunlarda da kapsam kısmi: lale yalnız jüri, kapadokya ve kale iyi.
- Somut riskler: bogaz şimşek flaşı, dolmus/marti/mimar/cini kamera sarsıntısı, peri tanıtım uçuşu, mehter ışık nabzı.
- Titreşim: kit `navigator.vibrate`'i sarıyor, ama 20 oyunda oyun kodunda `vibrate` yok. Anahtar boşta. Yalnız fay-hatti'nin kendi haptiği var.
- Yaklaşım (oyun tarafı): `const calm = () => Arena?.settings?.reducedMotion` + `Arena.on('settings')`. Sarsıntı 0, flaş yok, kamera geçişi anlık.
- Yazı boyutu için iki yol var, **karar §7**: (a) her oyun HUD/kart fontlarını `calc(var(--arena-text-scale,1)*…)` yapar (M, 21 oyun); (b) kit sürümü bunu desteklemeyen oyunda kaydırıcıyı gizler.
- Maliyet: reducedMotion S × 11. Yazı boyutu M-L. Yer: oyun (kit bloğu düzenlenmez).

**3.4 Kit tarafı: `?auto` yazımı ve gün anahtarı**
- `?auto`: kit `boot` → `touchProfile()` `arena.profile.v1.plays` yazıyor (D, kit s.122/342, 21 oyunda aynı hash). README'lerdeki "`?auto` writes nothing" sözü bu yüzden yanlış. Oyun tarafında düzeltilemez. Kit v1.0.1'de `auto`/`nosave` koruması gerekir (**S**). Dağıtım CLAUDE.md'deki toplu değişiklik kuralıyla olmalı: pilot → `schema/degisim.py` → onay.
- Gün anahtarı: kit `getUTC*` kullanıyor (D, kit s.30). cini'nin günlük tahtası yerel gün (D). Türkiye'de 00:00-03:00 arası seri kayabilir (T). fay-hatti (`todaySeed` yerel + kendi `fayhatti.streak` serisi, D), kapadokya (s.3887) ve marti (`dayKey` s.3391, görevler) yerel tarih kullanıyor. Kit serisine etkileri **BELİRSİZ**, çünkü hangi anahtarın `Arena.daily`'ye gittiği izlenmedi. Yaklaşım: §7'deki karara göre ya oyunlar UTC'ye geçer (S her biri) ya da kit `daily(game,{dayKey})` alır.

**3.5 Renkten bağımsız işaret**
- cini (28/30 seviye şekil aynı, renk farklı; mercan/zümrüt kırmızı-yeşil; D), ebru (12 pigment yalnız renk; T), dolmus (kaldırım halkası yeşil/turuncu/kırmızı; T), pamukkale (havuz doluluğu renkle; T), mimar (relay'in renk körlüğü modu GİTTİ; gerilme hâlâ yalnız renk; T), karagoz (kızıl/mavi lamba; düşük öncelik, yüzde zaten var).
- Yaklaşım: ikinci kanal yalnız çizimde olsun (desen, simge, ad). Sim, tohum ve kayıt değişmez. cini'de `LEVEL_DEFS`/`pickPalette` **değiştirilmemeli**, yoksa koleksiyon resimleri değişir.
- Maliyet: S-M her biri. Yer: oyun.

**3.6 Dokunmatikte klavye tuşu gösteren ipuçları**
- D: carsi (başlık `keys`), cay (nasıl oynanır P/Esc/M/X/L), hamsi (`W/S gaz…` toast ve `#tThr small`), kapadokya (`liftHint` "(Boşluk)", "B ile…"), kirkpinar (`COACH_STEPS` F/G/S/R), mimar ("Sağ tık…" toast), mehter (`howto1` sabit "D F J K"; bu bir masaüstü yeniden atama sorunu).
- T: bogaz (başlıkta 4 satır tuş listesi).
- **Zayıf iddia:** topkapi "dokunmatikte `E` istemi" raporu yanlış görünüyor. `@media (pointer: coarse){ .prompt kbd{display:none} }` var (D s.501-502).
- Yaklaşım: `(pointer:coarse)` iken tuşsuz metin anahtarı. Maliyet S her biri.

**3.7 İlk deneyim ve zorluk**
- Sert: mehter (2,15 sn'de kayıp, D), fay (menü → yardım → eğitim, 3 katman, D), karagoz (2 tık + 3 sn, D), lale (ilk çiçek 308 sn, D), simit (5 sekmeli plan modalı, D), bogaz (tuş duvarı, D), hamsi (ağ dairesi öğretilmiyor, T), kale (barikat görünmez, D), kervan (tek 7 sn toast, D).
- İyi örnekler (korunmalı): cay, cini, dolmus, kirkpinar, peri, carsi (koç gerçek girdiyle ilerliyor).
- Yaklaşım: "oynayarak öğret", ilk kazanım 1-2 dk içinde, `Arena.hint` (hazır, hiç kullanılmıyor) ile tek seferlik bağlamsal ipuçları. Bot ve günlük modda kapalı.

**3.8 Günlük meydan okuma = sabit içeriğin tekrarı**
- D: ebru (`seed % 18`), karagoz (`% 24`), pamukkale (`% 23`), mimar (`% 15`, kilidi atlıyor), topkapi (`% 9`), peri (12 delik; rüzgâr ≤0,14 m/s² etkisiz).
- Yaklaşım: tohumlu **değiştiriciler**. Her kombinasyon önceden botla doğrulanır, kampanya kaydına dokunulmaz (ebru tarif aynalama/renk permütasyonu, topkapi `opts.mod`, peri ayna/tee kaydırma, mimar bütçe kuralı, pamukkale doğrulanmış varyant tablosu). Maliyet M her biri.

**3.9 README/meta'daki eski iddialar**
- D: kale "Armour negates arrow damage completely" (kod %55/%35 azaltıyor), kirkpinar "26-bout" (18 maç), hamsi "x1/x2/x3" (kod x4), pamukkale "20 levels"/"20/20" (23 seviye), peri "18 strokes/23 yıldız" (ölçülen 14/20), kervan "12 of 12" (tohum 1-12'de 11/12), simit "careless bankrupt ~day 7" (Node'da 30/30 iflas yok), cini meta `workflows: []` (smoke.yml var), ebru README'de Tek Nefes/duvar/günlük yok, kapadokya README'de Altın Saat yok, fay `DESIGN.md`'de `file:///` yolu (2 adet).
- carsi "10/10, 0 düşme" iddiası coyote hatası gidince yeniden geçerli olmalı (T, yeniden koşulmadı). README'lerdeki "60 fps" iddialarının hiçbiri bu turda doğrulanamadı.
- Yaklaşım: belge yalnız gate çıktısından güncellensin. Maliyet S.

**3.10 GoatCounter ve Google Fonts (karar kullanıcıda)**
- GoatCounter (`gc.zgo.at/count.js`): 20/21 oyunda var (fay-hatti hariç). Google Fonts (`fonts.googleapis`): 18/21 (fay-hatti, hamsi, kervan hariç).
- Brief "harici ağ çağrısı yok, kullanıcı verisi toplanmaz" diyor. Raporların hepsi bunu sahibin bilinçli kararı olabilir diye işaretledi.
- peri'de Fredoka zaten yerelde (Google çağrısı gereksiz). Self-host ya da `system-ui` yedeği S.
- K: LG München I (2022), yerel alternatif varken Google Fonts'u GDPR ihlali saydı (peri raporu).

**3.11 Ekran okuyucuya ulaşmayan toast'lar**
- D: cay, kapadokya, topkapi (`#toasts` aria-live değil). kervan doğru yapıyor (`aria-live="polite"`). mehter tersine fazla okutuyor (`#judge` her vuruşta).
- Yaklaşım: `role="status"` + yalnız önemli olaylar. Maliyet S.

## 4. Oyun başına plan (alfabetik)

**bogaz-vapuru** ([bogaz-vapuru.md])
- DURUYOR: şimşek `sun += lightning*3` sahne flaşı ve reducedMotion bağı yok (D, s.3104-3106); "NEXT PIER"/"BİLET / VOUCHER" CSS `content` çakışması (D, s.266, cc7c4a8); `Arena.hint` kullanılmıyor, ilk sefer tam kurallarla başlıyor (D).
- EKLENMELİ: (1) bot kapısı (`?auto&cal` + `vapurSim`, 8 sefer ≥2★, ileri→tornistan girdi testi), S-M; (2) rehberli ilk yanaşma (hayalet yanaşma okları + `Arena.hint`), M; (3) şimşek yumuşatma + reducedMotion, S.
- EKLENMEMELİ: görünmez ceza mekaniği; gerçekçi sim derinliği (relay bunun kontrolü kırdığını gösterdi); toast tabanlı atmosfer olayları.
- Not: raporun 4.1, 4.4 ve "düşük güç modu ayarı" önerileri yalnız relay hatalarını onarmak içindi → **düşürüldü**.
- Açık soru: yok. "Halat at" kararı relay ile birlikte gitti.

**carsi-kacisi** ([carsi-kacisi.md])
- DURUYOR: 20 yarının 16'sı tekrar, B10 tamamen eski parçalar (D); zorluk eğrisi düz; başlıkta klavye metni dokunmatikte (D); `--arena-text-scale`/reducedMotion bağı yok (D); ~868k üçgen arka plan (D/T); müzik tek döngü.
- EKLENMELİ: (1) tekrarlanan yarıları yeni segmentlerle değiştir (B4-B10), botla 0 düşüş, M; kayıt için `layoutVer` göçü; (2) kişisel en iyi hayalet koşucu, M (coyote artık oyun zamanında, ön koşul sağlandı, D s.1327); (3) dokunmatik talimat + başlık metni, S.
- EKLENMEMELİ: prosedürel sonsuz mod, yeni hava hareketi/dash, zorunlu sanal çubuk.
- Not: raporun 4.1 (coyote) ve 4.2'deki auto-run onarımları **düşürüldü** (GİTTİ). Yalnız "sağ yarı dokun-zıpla"nın pointerdown'da olması kontrol edilmeli (BELİRSİZ).
- Açık soru: tek el auto-run modu yeniden istenecek mi? İstenirse doğru biçimde (ayar canlı uygulanmalı) ve botla.

**cay-ocagi** ([cay-ocagi.md])
- DURUYOR: **Low modda `body.low .glass` kart gradyanını eziyor, başlık kontrastı ~1:1** (D s.499); sonsuz vardiya: gelir ~300'de sabit, hedef +35/gün, bot 9. günde düşüyor (D); dükkân 5-6. günde bitiyor; d7 walk-by 18,4 ve kayıp görünmüyor; `?selftest` tek başına FAIL (eski, D); toast'lar aria-live değil.
- EKLENMELİ: (1) Low-mod kart düzeltmesi + kontrast assert'i, S; (2) sonsuz vardiya hayatta kalma modu (azalan artış + "N. güne ulaştın" bitişi), M; (3) Sakin mod (sabır ×1,5, en fazla 2★), S-M; (4) gün özetinde walk-by satırı, S.
- EKLENMEMELİ: 6. istasyon/ürün (dock 5×67 px dolu), sarsıntı/flaş, co-op.
- Açık soru: sonsuz vardiyada kayıp = koşu bitişi mi olsun?

**cini-ustasi** ([cini-ustasi.md])
- DURUYOR: taş seçme ve döndürme klavyeyle yapılamıyor (D); renk tek işaret (28/30, D); 6×6 tahta telefonda ~40×30 px (D); fırın iğnesi 3,2 sn ve reducedMotion'dan bağımsız (D); `.scoreRow` 390 px'te taşıyor (D); yerel gün ↔ UTC seri (D kod, T etki); `hideAll()` üst çubuğu gizlemiyor (D kod, etkisi revert sonrası BELİRSİZ).
- EKLENMELİ: (1) çizimde renkten bağımsız işaret, S-M; (2) klavye imleci + `Arena.announce`, M; (3) portrede büyük tahta için kamera, S-M; (4) fırın ping-pong/yavaş, S.
- EKLENMEMELİ: `LEVEL_DEFS`/`pickPalette` değişikliği (koleksiyon resimlerini değiştirir), süre sınırı, dekor artışı.
- Not: raporun 4.1'i (alt çubuk) **düşürüldü** (GİTTİ). Skor satırı düzeltmesi kalıyor.
- Açık soru: günlük anahtarı UTC'ye mi çekilsin? (§7-2)

**dolmus** ([dolmus.md])
- DURUYOR: mood'lu yolcu durağını söylemiyor (`moodLike` 2 replik, D); radyo kanalı duyulmuyor (D); `HOOK.shake` reducedMotion'ı okumuyor (D: oyun kodunda RM=0); `--barh` yalnız resize'da ölçülüyor (D); `.bubble` nowrap (D s.766); "OYNA" `runSave = null` onaysız (D); seviye seçimi yok ama 24★ hedefi var; EN'de "FREN/GAZ…" (D); "KADIKÖY — BOSTANCI" levhası (D).
- EKLENMELİ: (1) baloncukta her zaman durak, S (`CR` sırası korunmalı); (2) reducedMotion + HUD/baloncuk + "OYNA" onayı, S; (3) vardiya seçimi (practice modu, `best.reached`), M; (4) duyulabilir radyo kanalları, M.
- EKLENMEMELİ: daha fazla juice (sarsıntı/flaş/hit-stop), yükseltme ağacı, açık dünya.
- Açık soru: yok.

**ebru** ([ebru.md])
- DURUYOR: **pinch ilk parmakta `startStroke`, ikinci parmakta `endStroke`** (D s.3838-3842). Rapor bunu kısmen relay'e bağlamıştı, ama kod relay'den bağımsız ve hâlâ duruyor. Tek Nefes'te nefes hakkını yiyor. Diğerleri: dışa aktarma yok (`canShare` 0, D); günlük `seed % 18`; Tek Nefes'e usta mührü basılıyor; menü kalabalık (iki "galeri"); renk adları görünmüyor; %80 altında onaysız "Kâğıdı yatır"; 20 sn'de yanlış "yüklenemedi" mesajı (T); README'de Tek Nefes yok (D).
- EKLENMELİ: (1) dokunmada niyet bekleme (6 px / 120 ms) + sentetik pinch testi, S; (2) kâğıdı PNG olarak kaydet/paylaş (`toBlob` + `navigator.share({files})`), S; (3) tohumlu günlük tarif varyantı, M; (4) renk adı etiketi, S.
- EKLENMEMELİ: sıvı simülasyonu, puanlı Tek Nefes, çevrimiçi galeri, pinch'i kapatmak.
- Açık soru: yok.

**fay-hatti** ([fay-hatti.md]; revert yok, her şey DURUYOR)
- DURUYOR: **bölge kartı `applyBiome(b)` varsayılan `save=true` ile haftalık rotasyonu kalıcı donduruyor** (D); `boardsSinceCard` okunmuyor, kartlar hiçbir şey açmıyor (D); ilk ziyarette 3 katman; menü 24 düğme ve 1201 px; `runSeedVerification` senkron (headless'ta 16,8 sn) ve aralık sabit; sonsuz modda K=6 düzlüğü; `DUR` canlı güncellenmiyor; `DESIGN.md`'de `file:///` (D); iki seri sistemi (T).
- Not: kart sistemi agy-gemini commit'lerinden geliyor, bu commit'ler revert edilmedi.
- EKLENMELİ: (1) biome düzeltmesi + tek seferlik kayıt göçü, S; (2) ilk deneyimi tek akışa indirme + menü sadeleştirme (Doğrulama yalnız `?debug`), M; (3) Wordle tarzı "deprem hikâyesi" paylaşım satırı, S.
- EKLENMEMELİ: daha fazla kart/tema/bölge, 5×5'ten büyük ızgara, süreye dayalı yıldız.
- Açık sorular: kartlar gerçek kilit açma mı olsun, kaldırılsın mı? Günlükte ipucu (en fazla 2★) olsun mu?

**hamsi** ([hamsi.md])
- DURUYOR: dikey telefonda sonar `min(262px,100vw-250px)` ≈140 px (D); `body.touch #actions .hint{display:none}` (D s.121); dokunmatikte klavye ipucu (D, `W/S gaz…`); `hurtFlash` reducedMotion'a bağlı değil (küçük, 180 ms, D); README x3 (D); sezon sonrası hedef yok (T).
- EKLENMELİ: (1) ağ çekiş karnesi (boşluk/alttan kaçış sayaçları + sonar şamandırası), S; (2) dikey sonar düzeni + dokunmatik ipuçları, S-M; (3) ilk sefer rehberi, S-M.
- EKLENMEMELİ: kaynaksız "otantik" terimler, keskin ekonomi eşikleri, PWA.
- Not: raporun 1. işi (relay hatalarını geri al) **tamamen GİTTİ**. Ekonomi gate'i (3 tohumla sezon) yine de §3.1 kapsamında kalıyor.
- Açık soru: "zor sezon" değiştiricileri istenir mi (M, kayıtta `mod` alanı)?

**kale-savunmasi** ([kale-savunmasi.md])
- DURUYOR: **telefonda üst kontroller ekran dışında** (D: `#top` ≤760 px'te `flex-wrap` yok, s.178/720; kod yorumu s.4001 "wraps" diyor ama sarmıyor; kaynak 651c5b4). Ölçüm relay'li sürümde yapıldı, düzen kodu aynı. Diğerleri: barikat keşfedilmiyor (README/meta/`controlsTouch`'ta yok, D); README "Armour negates… completely" ↔ kod `a *= 1 - e.armor` (D s.2821); rehber maliyetleri sabit yazılmış (T); kit `?auto` profil yazımı.
- EKLENMELİ: (1) telefonda `#top` sarması / kontrolleri alt şeride taşıma, S; (2) dalga 2'den sonra barikat ipucu + metinler, S; (3) ilk karşılaşma kartları ("Harp Defteri"), S-M; (4) zorluk seçimi, M.
- EKLENMEMELİ: tam bağışıklık (hard counter), uçan birimler, düşman başına DOM öğesi.
- Not: raporun 7.1-7.3'ü **düşürüldü** (GİTTİ). Bot kapısı referansı `hisarSim(1260)`=15/522/218 olmalı; revert sonrası yeniden koşulmadı (T).
- Açık soru: zırh politikası. Kod yumuşak sayaç, README tam bağışıklık diyor; hangisi doğru? (§7-6)

**kapadokya-balonu** ([kapadokya-balonu.md])
- DURUYOR: 390 px'te `#c-golden` `#inst` ile örtüşüyor (D raporda; kaynak 0c9ee93, relay değil); `#ui.vf-on .ctl{visibility:hidden}` dokunmatikte kumandasız bırakıyor (D); `liftHint` "(Boşluk)" (D); üst çubukta yıldız kırpması (D); uçuşlar 2-7 dk; günlük yeni oyuncuya gizli katmanlı uçuş verebiliyor; README'de Altın Saat yok (D); toast'lar aria-live değil (D).
- EKLENMELİ: (1) telefon kumanda yerleşimi + vizörde brülör/supap, S; (2) sürüklenme öngörüsü çizgisi (render tarafında, CORE'a dokunmaz), S-M; (3) seyir 4× otomatiği, S.
- EKLENMEMELİ: yatay dümen, bloom/parlama "juice", titreşimi yaygınlaştırmak.
- Not: raporun "titreşim ayarı yok" iddiası zayıftı. Kit'in Titreşim anahtarı `navigator.vibrate`'i zaten sarıyordu (D kit s.148-152). Konu artık GİTTİ.
- Açık soru: yeni oyuncu günlüğü yumuşatılsın mı? (günlük herkes için aynı kalmalı)

**karagoz** ([karagoz.md])
- DURUYOR: vuruş sahnelerinde (4, 16) telefon `.stats` taşması (D raporda; kaynak mum ışığı 76426a9, T); "Oyna" → harita → sahne + 3 sn intro (D); ipucu tek kademe, bir yıldız alıyor (D); günlük `% 24` (D); harita düğmeleri 38×48; "1%" biçimi (BELİRSİZ, yeniden bakılmadı).
- EKLENMELİ: (1) telefon HUD + pill'in kısalması, S; (2) ilk girişte doğrudan sahne 1, S; (3) kademeli ipucu (vurgula → yerleştir), M.
- EKLENMEMELİ: sürekli sıcak/soğuk ses ipucu (relay tonu bunu gösterdi), PWA, prosedürel sahne, seslendirme.
- Not: raporun 1. işi (ton + per-frame match) ve PWA kaldırma **düşürüldü** (GİTTİ, D: `curMatch` yalnız `startScene`/`afterChange`'de).
- Açık soru: "Serbest Perde" (URL hash ile sahne paylaşımı, L) istenir mi?

**kervan** ([kervan.md])
- DURUYOR: `KervanBot` `buyRumor` çağırmıyor (D rapor); README "12 of 12" (D); telefonda HUD + kervan çubuğu ≈%34 ve ilk toast HUD'u örtüyor (d48e780, D raporda); "WASD / Oklar" EN'de Türkçe (D), `spread` TR'de İngilizce (D); işlemler gün sonuna kadar kaydedilmiyor (T); ölü `newYearStats_unused` (D); tohum 6 erken iflas.
- EKLENMELİ: (1) botun söylenti kullanması + Node denge betiği (12 tohum, söylentili/söylentisiz), S-M; (2) "Pazar defteri" (görülen fiyatlar, gizlemesiz), M; (3) ilk sefer görev şeridi, S-M; (4) telefon HUD'u tek satır, S.
- EKLENMEMELİ: tam otomatik rotalar, üretim zinciri, donanım sinyaliyle kör kalite düşürme (relay örneği), daha fazla mal/şehir.
- Not: raporun 4.1'i **düşürüldü** (GİTTİ; mal başına `tAllSell` geri geldi, D s.4451).
- Açık soru: fiyat sisi (diğer şehirlerin canlı fiyatını gizlemek) istenir mi? Denge değişikliğidir.

**kirkpinar** ([kirkpinar.md])
- DURUYOR: **`if (c === 'KeyL' && !(G.screen === 'play' && G.versus)) toggleLang()`**; tek oyunculu maçta "çek" tuşu `L` dili değiştiriyor (D s.4038). Diğerleri: `#subs .cazgir-speech, #subs div` iç içe kutu, telefonda 6,5 sn ekranın ~%40'ı (D); `COACH_STEPS` F/G/S/R (D s.3952); `#bMute` dil düğmesinin üstünde (D); kurtuluş tuş basma yarışı (erişilebilirlik); 2P dokunmatikte kontrolsüz; README "26-bout" (D).
- EKLENMELİ: (1) hata paketi (L, subs, koç etiketleri, bMute), S; (2) maç sonu "neden" kartı (`M.stats` zaten toplanıyor), S; (3) basılı tutma ile kurtuluş (~6 Hz), S-M; (4) rakip keşif notu, S.
- EKLENMEMELİ: ragdoll/fizik motoru, gerçek pehlivan adları, telefona 5. düğme.
- Not: kariyer düğmesi düzeltmesi **düşürüldü** (GİTTİ). 960×540 başlık taşması yeniden ölçülmeli (BELİRSİZ).

**lale-bahcesi** ([lale-bahcesi.md])
- DURUYOR: **telefonda araç düğmeleri ekran dışında, bazar telefonda açılamıyor** (D: `.stats{flex-wrap:nowrap}` s.806/1063, kaynak 7e52007; a4d159a revert'i HUD'a dokunmamıştı, D diff). Diğerleri: "Sonsuz bahçe" yenilemede kayboluyor (D: s.2569 `ended` bırakıyor, s.2581/2647); ilk çiçek 308 sn; `renderTile` her gün `innerHTML` (dokunuş kaybı, T); bot 5/5 kazanıyor (zorluk tavanı); i18n kaçakları "melez/nadir", "takes effect after reload" (D); `REDUCED` kısmi.
- EKLENMELİ: (1) telefon HUD'u, S; (2) sonsuz modu kalıcı yap, S; (3) ilk 2 dakikada ilk çiçek (yeni oyunda iki tomurcuk), S; (4) panel diff'li yeniden çizim, S; (5) doğru melezleme rehberi (relay'in yanlış olanı gitti; ihtiyaç duruyor), S-M.
- EKLENMEMELİ: `Date.now` ile gerçek zamanlı büyüme, enerji/bekleme süresi, harici API ile isim üretimi.
- Not: ad çakışması düzeltmesi **düşürüldü** (GİTTİ; `nameOf` yine renk+şekil+desen, D s.1476).

**marti** ([marti.md])
- DURUYOR: kamera sarsıntısı (`S.shake`, s.2741/2761) reducedMotion'ı okumuyor (D); geç rampa rüzgârı `Math.random` ile, günlük adil değil (D s.3745); 5 görev tanımı dar (D); telefon başlığında Günlük düğmesi kesik (BELİRSİZ); GoatCounter.
- EKLENMELİ: (1) reducedMotion + darbede titreşim, S; (2) koşu özeti (sebep + tek ipucu, yeniden ve doğru), S; (3) günlük rotada kendi hayaleti (önce rüzgâr tohumlansın), M; (4) görev havuzu 5 → ~9, S.
- EKLENMEMELİ: SW/PWA, anında bitiş kuralları, görünmez dokunma bölgeleri, kalıcı yükseltme dükkânı, jiroskop.
- Not: raporun ilk iki işi **düşürüldü** (GİTTİ). Eski "kısa dokunuş = dalış" geri geldi. "Görünür dalış düğmesi" artık zorunlu değil, isteğe bağlı bir iyileştirme. Bot dalmadığı için gate'e dalış senaryosu eklenmeli.

**mehter** ([mehter.md]; revert yok)
- DURUYOR: varsayılan Normal ve hiç basmayan oyuncu 2,15 sn'de kaybediyor, rekor/rozet yok (D); şerit tuşu M/X/L/P global kısayola gidiyor (D); telefon HUD'u (Kombo kesik, İsabet yok, D); `LANE_LAYER` ölü (D) ve katman 1'de sesi kapalı şeride nota düşüyor; Kolay iki şeritli; kalite düğmesi "Tuş atandı" diyor (`rebindDone`, D); kit ayarlarıyla bağ yok (D); `#judge` her vuruşta ekran okuyucuya gidiyor.
- EKLENMELİ: (1) ilk deneyim paketi (Kolay varsayılan, kalıcı zorluk, 2 ölçü ısınma, "Ruh tükenmez"), S; (2) cila hataları, S; (3) Kolay'ı dört şeritli yap + hayalet notalar (önce Düyek'te pilot), M; (4) not hızı ayarı, S.
- EKLENMEMELİ: gerçek marş kayıtları, MP3 akışı, kaçan notada sazı susturma, daha dar pencere.
- Açık soru: Kolay rekorları ayrı anahtarda mı tutulsun?

**mimar-sinan** ([mimar-sinan.md])
- DURUYOR: 390 px'te tepsi-lejant 81 px örtüşme (D; lejant relay'den önce de vardı, D diff); günlük `seed % LEVELS.length` kilidi atlıyor, 30 günün 22'sinde 6+. sipariş (D s.2689); ipucu referans parçayı tam konumla veriyor ve yıldız cezası yok; reducedMotion yok (`G.shake`, deprem, D); telefonda "Sağ tık…" toast'u (D s.1548).
- EKLENMELİ: (1) "neden çöktü → çare" cümlesi + "Onar"da itki çizgisi, S; (2) kademeli ipucu, M; (3) günlüğü açılmış siparişlerle sınırla + adını göster, S; (4) telefon düzeni + reducedMotion, S; (5) "Sinan'a karşı taş" rekoru, S.
- EKLENMEMELİ: hazır fizik motoru, ekranı kaplayan modal (relay paneli örneği), referanssız prosedürel sipariş.
- Not: çöküş paneli, ağır çekim ve renk körlüğü düzeltmeleri **düşürüldü** (GİTTİ). Doğru eşikli bir renk körlüğü modu ise §3.5 kapsamında hâlâ isteniyor.

**pamukkale** ([pamukkale.md])
- DURUYOR: **2, 5, 6, 8, 11, 12, 16'da statik yerleştirmeyle "taşma yok + par" imkânsız** (D, tam tarama). 9, 15, 17-20 taranmadı. Su akarken yerleştirmeyle mümkün olup olmadığı BELİRSİZ. Diğerleri: `const L` sabit, dil değişince seviye/bölge adı eski dilde (D s.1172); kalan süre görünmüyor (D); dikey kamera 1.35 sabit, tahta sığmıyor (D); dokunmatikte hayalet önizleme yok (`pointerType === 'mouse'` D s.2330); S19 "Altı havuz" (D); meta "20 levels" (D); 1-7 tek araçla çözülüyor.
- EKLENMELİ: (1) dil + metin düzeltmeleri, S; (2) `solve-levels.mjs`'e "3★ mümkün mü" kontrolü + par/envanter/`spillMax` ayarı, M; (3) görünür süre + telefona sığan kamera, S; (4) akış önizlemesi, M.
- EKLENMEMELİ: SW, seviye `rows`/`pools` sırasını sessizce değiştirmek, hız yıldızı, SPH su.
- Açık soru: su akarken araç koymak bilinçli tasarım mı? (3★ çözümünün yolu buna bağlı)

**peri-golf** ([peri-golf.md])
- DURUYOR: Google Fonts s.18-20 (Fredoka zaten yerel, D); README/meta "18 vuruş/23 yıldız", ölçülen 14/20 (bot kestirme kullanıyor, insanı temsil etmiyor; T); `Arena.settings` oyun kodunda yok (D); günlük 12 delikten biri, rüzgâr etkisiz (D kod); telefonda ilerleme noktaları kesik (D); duraklat menüsündeki yeniden başlatma "en iyi tur"u sınırsız mulligan'a açıyor (T, eski davranış).
- EKLENMELİ: (1) Google Fonts kaldır + README, S; (2) günlük değiştiriciler (ayna/tee/engel fazı, botla doğrulanmış), M; (3) reducedMotion (tanıtım uçuşu 0,6 sn, pırıltı yok), S; (4) telefon kadrajı, S.
- EKLENMEMELİ: fizik sabitlerini değiştirmek (hayalet/rekor anlamsızlaşır), HUD'a yeni düğme, sonsuz rastgele delik.
- Not: raporun 4.1-4.3'ü **düşürüldü** (GİTTİ; `b-restart-hud` ve iptal eşiği yok, D).

**simit-firini** ([simit-firini.md])
- DURUYOR: **telefon HUD'u**: hız seçici yıldızların üstünde, gün/saat görünmüyor (D: `#hud` `flex-wrap: nowrap` s.213/224, 3bcebe6). Diğerleri: HUD ikonları 36×36 (D rapor); kasa 11-14. günde doluyor, kazanmayı yalnız itibar belirliyor, itibar dökümü yok (D); 10 etiketin 9 çifti çakışıyor (D); altın pencere 4x'te ~0,45 sn (D kod); `Arena.hint` yok (D); pip `if (… && false)` ölü kod (D s.2738, eski); README "careless bankrupt" (D).
- EKLENMELİ: (1) telefon HUD'u iki satır + 44 px, S; (2) itibar dökümü + hedef çubuğu (toplam aynı, bot birebir), S; (3) ilk gün `Arena.hint` ipuçları, S; (4) etiket ayrıştırma, M; (5) "askıda ekmek/simit" para→itibar dönüşümü, M (30 tohum harness'iyle).
- EKLENMEMELİ: kasa hedefini yükseltmek ya da itibar formülünü sertleştirmek, tıkla-sat mikro yönetimi, uçan para efektini geri getirmek.
- Not: fırın alarmı ve uçan para düzeltmeleri **düşürüldü** (GİTTİ).
- Açık soru: "askıda simit" adı kaynakta doğrulanmadı ("askıda ekmek" doğrulandı); hangi ad kullanılsın?

**topkapi-gecesi** ([topkapi-gecesi.md])
- DURUYOR: 390 px'te görev çubuğu 3. yıldızı kesiyor, görünürlük paneli ~200×162 (D rapor); dikey kamerada başlangıçta muhafız görünmüyor; günlük `seed % 9`; `PROG.times` tutuluyor ama gösterilmiyor (D); `#toasts` aria-live değil (D); `.redflash` reducedMotion'da kalıyor (T); title'da 83 draw call ↔ README 39-47 (yük altında, BELİRSİZ).
- **Zayıf bulgu:** "dokunmatikte `E` istemi" yanlış. `(pointer:coarse)` iken `.prompt kbd` gizli (D s.501-502).
- EKLENMELİ: (1) sürükleyerek taş nişanı (CORE'un `I.throwAt` yolu üzerinden), S-M; (2) görev başına rekor + ±fark, S; (3) günlük "gece koşulu" (`newSim(idx, opts)` kancası, her kombinasyon botla doğrulanmış), M; (4) telefon HUD'u, S-M.
- EKLENMEMELİ: oto-nişan, PWA, prosedürel harita, dövüş.
- Not: raporun 1. işi **düşürüldü** (GİTTİ). Revert sonrası Taş düğmesi eski "ileri at" davranışında (T, kod; dokunmatik test yeniden koşulmadı).

## 5. Genel "eklenmemeli" listesi

| Fikir | Neden | Kanıt (raporlar) |
|---|---|---|
| Gerçek offline PWA / service worker | Blob/data URL SW spesifikasyonca reddediliyor. Gerçek SW ayrı `sw.js` ister, tek dosya kısıtını aşar. Sabit adlı cache-first önbellek oyuncuyu eski sürüme kilitler. | 6 relay denedi (hamsi, karagoz, marti, pamukkale, peri, topkapi): hepsi ölü ya da 404 (D); K: MDN register() |
| Çevrimiçi skor tablosu, hesap, bulut kaydı, paylaşılan hayalet, çok oyunculu | Sunucu, hesap ve kullanıcı verisi gerektirir, kısıtı aşar | 21/21 rapor |
| Reklam, ödüllü video, portal SDK, IAP, analitik gönderimi | Harici ağ + veri + ücretsiz ilke | çoğu rapor |
| Kalıcı yükseltme dükkânı / ikinci para birimi / enerji | Skor dengesini ve günlük adaleti bozar, F2P hissi verir | marti, dolmus, lale, cay (kozmetik hariç) |
| Ekran sarsıntısı, tam ekran flaş, hit-stop, neon parlama "juice"'u | Erişilebilirlik (K: XAG 117/118) ve UHD bütçesi; relay denemeleri hep geriledi | dolmus, hamsi, kapadokya, cay, mimar (D) |
| Post-processing (bloom/SSAO), gerçek zamanlı yansıma, ağır gölge | Intel UHD 620 + telefon bütçesi | 12+ rapor |
| Görünmez ya da açıklanmayan ceza (gizli ağ, kg eşiği, anında su ölümü) | Oyuncu neyle cezalandırıldığını göremez, adil değil | bogaz, hamsi, marti (D) |
| Doğrulayıcısı olmayan prosedürel/sonsuz içerik | Çözülebilirlik garantisini ve bot kapısını bozar | carsi, karagoz, peri, mimar, topkapi, pamukkale |
| Kaynaksız "otantik" terim ya da bilgi | Türk oyuncu yanlışı hemen fark eder | hamsi (lidaki/vantrik), lale (Divan sıfatları gözden geçirilmeli), simit (askıda simit) |
| Gerçek oyun/marka adı, karakteri, sanatı, müziği | Brief kuralı | 21/21 |
| Kanıtsız relay oynanış değişikliği; ARENA-KIT bloğunu oyun içinde yamamak | CLAUDE.md "yeşil ≠ test edildi"; kit bloğu düzenlenmez | 9 Kasım revert'inin nedeni |
| Düşman/etiket başına DOM öğesi, sınırsız DOM efekti | Layout maliyeti; instanced 3D zaten var | kale, simit (D) |
| Telefona ek düğme ya da 6. istasyon | Dokunma hedefleri 44 px altına iner | cay, kirkpinar, peri |

## 6. Önerilen güncelleme sırası

**Dalga 0: güvenlik ağı ve kit (önce bu; tahmini 3-5 ajan-günü)**
1. Ortak gate şablonu (`tools/gate.mjs`): taban/aday sim karşılaştırması + 390×844 "ekran içinde" assert'i + konsol 0 hata. Önce bir oyunda pilot; adaylar kale (`hisarSim` tek sayı) ya da bogaz. Sonra 20 oyuna `schema/degisim.py` kapısıyla yayılır. Oyun başına 1-3 saat.
2. Oyuna özel senaryo testleri: marti dalış, ebru pinch, kale `?auto`→localStorage, topkapi dokunmatik taş, fay biome göçü.
3. Kit v1.0.1 (S): `?auto`/`nosave` iken `touchProfile` yazmasın. Gün anahtarı kararı (§7-2) uygulanır. Sürüm atlatma toplu değişiklik kuralıyla yapılır.
4. Merge politikası: relay/worker çıktısı PR + gate olmadan main'e girmez.
5. Revert'in kendisini doğrula: 19 oyunda `?auto` bot sonucu raporlardaki relay öncesi değerlere döndü mü? (bogaz 1557/2938, kale 15/522/218, hamsi 3★). Bu turda **koşulmadı**.

**Dalga 1: DURUYOR kritik hatalar (≈20 S işi, 3-4 ajan-günü)**
- kale `#top` sarması; lale HUD + sonsuz mod; simit HUD; fay biome kartı + göç; kirkpinar `L` + `#subs`; ebru pinch niyet bekleme; cay Low kontrast + selftest; pamukkale `L` + metinler; mehter ilk deneyim + tuş çakışması; dolmus "OYNA" onayı + mood baloncuk + `--barh`; cini `.scoreRow`; kapadokya Altın Saat örtüşmesi + vizör kumandası; mimar günlüğü açılmış siparişle sınırlama; peri Google Fonts; README/meta eski iddiaları (gate çıktısıyla).

**Dalga 2: ortak erişilebilirlik ve telefon (4-6 ajan-günü)**
- reducedMotion 11 oyunda (S×11). Renkten bağımsız işaret (cini, ebru, dolmus, pamukkale, mimar; S-M). Dokunmatik metinler (7 oyun, S). Toast `role="status"` (cay, kapadokya, topkapi) ve mehter `#judge`. Kalan HUD taşmaları (mehter, karagoz, topkapi, pamukkale, peri, kervan, hamsi sonar, mimar).
- Yazı boyutu: §7-4 kararına göre.
- GoatCounter/Fonts: §7-1 kararına göre (S×20).

**Dalga 3: oyun başına en değerli 1-2 özellik (10-15 ajan-günü, her biri gate'le)**
- bogaz rehberli yanaşma
- carsi yeni segmentler + hayalet
- cay sonsuz vardiya + sakin mod
- cini klavye + portre kamera
- dolmus vardiya seçimi + radyo
- ebru PNG paylaşım + tohumlu günlük
- fay ilk deneyim + deprem hikâyesi
- hamsi ağ karnesi + sonar
- kale barikat ipucu + Harp Defteri
- kapadokya sürüklenme öngörüsü
- karagoz kademeli ipucu
- kervan söylenti botu + pazar defteri
- kirkpinar neden kartı + basılı tutma
- lale ilk çiçek + melez rehberi
- marti koşu özeti + günlük hayalet
- mehter dört şeritli Kolay
- mimar onarım rehberi + kademeli ipucu
- pamukkale 3★ tutarlılığı + akış önizlemesi
- peri günlük değiştiriciler
- simit itibar dökümü + askıda
- topkapi sürükle-nişan + gece koşulu

## 7. Kullanıcının karar vermesi gerekenler

1. **GoatCounter (20 oyun) ve Google Fonts (18 oyun).** (a) İkisini de kaldır; fontları self-host et ya da `system-ui` kullan. (b) Fontları kaldır, GoatCounter'ı brief'e açık istisna olarak yaz. (c) İkisini de istisna yap ve README'de belirt.
2. **Günlük gün anahtarı.** (a) Kit UTC kalsın, oyunlar UTC'ye uysun (cini, olası fay/kapadokya/marti; Türkiye'de gün 03:00'te döner). (b) Kit v1.0.1 yerel güne geçsin (bütün serileri etkiler). (c) Kit'e `daily(game,{dayKey})` parametresi eklensin.
3. **Kit v1.0.1 sürümü** (`?auto` profil yazımını engelleme): onaylıyor musun? Toplu değişiklik akışı: pilot → `degisim.py` → onay.
4. **Yazı boyutu kaydırıcısı.** (a) 21 oyunda HUD fontlarını `--arena-text-scale`'e bağla (M-L). (b) Kit, desteklemeyen oyunda kaydırıcıyı gizlesin. (c) Olduğu gibi kalsın (bugün işlevsiz).
5. **Geri alınmamış eski agy-gemini commit'leri** (UI REBIRTH'ler, fay kart sistemi). (a) Yalnız ölçülen sorunları onar. (b) UI REBIRTH'leri de oyun başına değerlendirip gerekirse geri al (kale, lale, simit, bogaz HUD sorunlarının kaynağı).
6. **Kale zırhı.** (a) Yumuşak sayaç kalsın (kod bugün böyle), README düzeltilsin. (b) Tam bağışıklık istenir; o zaman dalga/kule dengesi yeniden kurulur.
7. **fay-hatti kartları.** (a) Gerçek kilit açma. (b) Her N tahtada bir, sade. (c) Kaldır. Ayrıca günlükte ipucu (en fazla 2★) olsun mu: evet/hayır.
8. **Mehter.** Kolay varsayılan + "Ruh tükenmez": evet/hayır. Kolay rekorları ayrı anahtar mı, karışık mı?
9. **Pamukkale 3★.** (a) Seviye verisini ayarla. (b) `spillMax` eşiği. (c) "Su akarken yerleştirme" bilinçli kabul edilsin, önce test edilsin.
10. **Titreşim anahtarı** 20 oyunda etkisiz. (a) Seçili oyunlara az ve anlamlı haptik ekle (marti, peri, ebru). (b) Kit anahtarı haptiği olmayan oyunda gizlesin.
11. **Tek el auto-run** (carsi) ve **dokunmatik nişan** (topkapi) gibi revert edilen fikirler doğru biçimde yeniden yapılsın mı, yoksa kapansın mı?
12. **Hayalet/rekor kayıtları** (carsi, kapadokya, marti; oyun başına ≤10 KB localStorage) kabul mü?

## 8. Doğrulanmayanlar ve sınırlar

- **Performans:** bütün raporlar headless Chromium + SwiftShader ile, yük ortalaması 20-80 olan 4 çekirdekli paylaşımlı makinede ölçüldü. Bütün fps ve süre değerleri **geçersiz**. README'lerdeki "UHD 620'de 60 fps" iddialarının hiçbiri doğrulanmadı. Draw call ve üçgen sayıları göreli olarak kullanılabilir. topkapi'nin 83 call ↔ README 39-47 farkı açık soru.
- **Gerçek cihaz yok:** dokunma, pinch, uzun basma, iOS Safari, `navigator.share({files})` ve gerçek font yüksekliği (dolmus testinde fontlar boş döndü) yalnız öykünmeyle görüldü.
- **Revert sonrası yeniden koşu yapılmadı:** GİTTİ sınıflandırması grep'e dayanıyor (kod parçası yok). Bot sonuçlarının relay öncesi değerlere döndüğü **T** (kale 15/522/218, bogaz 3★, hamsi 3★, carsi 10/10). Dalga 0 adım 5'te ölçülmeli.
- **DURUYOR bulguların ölçümü relay'li sürümde alındı.** Kod parçası duruyor, ama düzen ölçüleri (ör. carsi HUD, cay dock, kirkpinar başlık) relay CSS'iyle birlikte alındığı için bazıları BELİRSİZ işaretlendi.
- **Zayıf ya da çelişkili iddialar:**
  - topkapi "`E` istemi dokunmatikte": CSS ile çelişiyor, yanlış görünüyor.
  - ebru pinch hatası relay'e bağlanmıştı: kod relay'den bağımsız, hâlâ duruyor.
  - kapadokya "titreşim kapatılamıyor": kit anahtarı zaten sarıyordu.
  - hamsi 3★ → 2★ (n=1, artık önemsiz).
  - pamukkale 3★ taraması yalnız statik yerleştirme; 9, 15, 17-20 taranmadı.
  - peri bot 14 vuruş kestirmeyle, insan zorluğunu temsil etmiyor.
  - kervan README'nin tohum kümesi bilinmiyor.
  - simit careless ölçümü Node harness'iyle, sayfadaki adımlamayla birebir değil.
  - carsi rüzgâr etkisizliği sabitlerden hesap (T).
- **Erişilemeyen kaynaklar:** poki.com, gameaccessibilityguidelines.com, docs.crazygames.com, gamedeveloper.com, ddrkirby.com ve blog.amandaghassaei.com bazı oturumlarda ağ izninde değildi. O raporlar arama özetlerine dayandı (cini, ebru, fay, kale, mehter, peri, cay).
- **Firefox/WebKit** hiçbir raporda koşulmadı (CI'daki smoke üç tarayıcıyı kapsıyor ama yalnız yükleme testi).
- **Kapsam dışı:** gerçek oyuncu verisi yok (GoatCounter verisi okunmadı). Zorluk yargıları bot verisine ve tahmine dayanıyor.

## Ek: revert sonrası smoke (B, 9 Kas ~21:00Z)
20 Three.js oyununun güncel `main`'inde `tools/smoke.mjs chromium` (SRI + yükleme + tamper): **20/20 RESULT OK**; `arena-kit/inject.py --kontrol`: **20/20 OK** (D). fay-hatti: headless 0 hata, 0 ağ isteği (D). Bot sonuçlarının relay öncesine döndüğü bu turda koşulmadı (T).

Oyun başına ayrıntılı raporlar bu klasörde: `<oyun>.md`. Araştırma yönergesi: `BRIEF.md`.

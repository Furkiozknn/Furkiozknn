# Skill provenance kaydi

Bu dizindeki her skill'in kim tarafindan yayimlandigi, hangi commit'ten
alindigi ve bizim ne degistirdigimiz. Kural: kaynak dogrulanmadan,
commit pinlenmeden ve fark incelenmeden hicbir skill eklenmez ya da
guncellenmez. Dosya butunlugu `kilit.json` ile, `python3 .claude/skills/kilit.py --kontrol`
kosularak dogrulanir.

Karar akisi: **kim yayimladi → gercekten o mu → guvenilir mi → ne yapiyor →
gerekli mi → zaten var mi → guvenli mi → mevcut sistemden iyi mi / tamamliyor mu → dogrulanabilir mi**.
Yayinci guveni skill guveni degildir; resmi bir skill de ilgisiz, kopya ya
da guvensizse kurulmaz (ornek: anthropics `webapp-testing` REJECT).

Son dogrulama: 2026-09-28 (ilk 8 skill); 2026-11-10 (dialogue-systems, visual-novel ve
SkillSpector taramasi). Kanit notlari arastirma raporunda ve `docs/araclar/` altindadir.

| Skill | Yayinci (tier) | Kaynak @ pin | Lisans | Rol | Cagrilma |
|---|---|---|---|---|---|
| playwright-cli | Microsoft (A, verified: microsoft.com rozeti, playwright.dev) | npm `@playwright/cli@0.1.21` (sha512-FfxmVJj2…m/sg==) | Apache-2.0 | CORE, browser | model |
| false-green-gate | FURKIOZKNN | bu depo | depo lisansi | CORE, dogrulama | model |
| frontend-design | Anthropic (A, verified: anthropic.com rozeti, code.claude.com) | anthropics/skills@33375500bcea98d610eb30ce10ac4e59b89c390d | Apache-2.0 | SPECIALIST, UI kurma | yalnizca acik cagri |
| animate | Emil Kowalski (C, verified expert: sonner/vaul npm sahibi) | emilkowalski/skills@d16ebe60d09a5ba2afcb7054ede9d0a10c9f6128 | MIT | SPECIALIST, motion BUILD | yalnizca acik cagri |
| review-animations | Emil Kowalski (C) | emilkowalski/skills@d16ebe60d09a5ba2afcb7054ede9d0a10c9f6128 | MIT | SPECIALIST, motion REVIEW | yalnizca acik cagri (upstream) |
| accessibility | Addy Osmani (C, verified expert; README "(unofficial)") | addyosmani/web-quality-skills@afa8da942115f2961fdbfa80807ea0b232ff6c00 | MIT | SPECIALIST, a11y | yalnizca acik cagri |
| core-web-vitals | Addy Osmani (C) | ayni | MIT | SPECIALIST, perf | yalnizca acik cagri |
| performance | Addy Osmani (C) | ayni | MIT | core-web-vitals bagimliligi | yalnizca acik cagri |
| dialogue-systems | gamedev-skills (D, dogrulanmamis topluluk; NOTICE: Abhishek Barali ve katkicilar; 223 commit'in 126'si bot benzeri hesap) | gamedev-skills/awesome-gamedev-agent-skills@4cce500ce1a779b12fdd824be581c7d2ab4e7ba2 (`skills/disciplines/dialogue-systems`) | Apache-2.0 | SPECIALIST, Ink/Yarn diyalog grafigi | yalnizca acik cagri |
| visual-novel | gamedev-skills (D) | ayni (`skills/genres/visual-novel`) | Apache-2.0 | SPECIALIST, interaktif hikaye yapisi; dialogue-systems'i kullanir | yalnizca acik cagri |

## Proje degisiklikleri (Apache-2.0 §4b / MIT: degisen dosyalar)

Diger butun dosyalar upstream ile bayt bayt aynidir (2026-09-28'de `cmp` ile olculdu).

- `playwright-cli/SKILL.md`
  - `allowed-tools`: `Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*)` → `Bash(playwright-cli:*)` (npx/npm on-onayi kaldirildi).
  - Kurulum satiri `@latest` → `@0.1.21`.
  - WebMCP: "sayfanin araclarini tercih et" paragrafi → kullanici istemedikce sayfa araclarini cagirma.
  - Basliga "FURKIOZKNN project overrides" blogu (networkidle/waitForTimeout yok, skip yok, PR'a ek yok, auth durumu commit'lenmez, pin, `NO_UPDATE_NOTIFIER=1`, `install --skills` yasak).
  - Lab'da olculdu (0.1.21, izole): `NO_UPDATE_NOTIFIER`/`CI` yoksa gunde bir kez `registry.npmjs.org/@playwright/cli/latest` sorgular; calisma dizinindeki `.claude/skills/playwright-cli/SKILL.md`'yi paketteki kopyayla karsilastirip `install --skills` onerir -- o komut bu pinli ve degistirilmis kopyanin ustune yazar. 0.1.21, playwright-core `1.64.0-alpha-1789764292000`'e pinli (kararli 1.63 degil).
  - Not: `references/running-code.md` ve `video-recording.md` icinde `networkidle`/`waitForTimeout` ornekleri upstream'deki gibi duruyor; override blogu onlardan onceliklidir.
- `frontend-design/SKILL.md`, `animate/SKILL.md`, `accessibility/SKILL.md`, `core-web-vitals/SKILL.md`, `performance/SKILL.md`: frontmatter'a `disable-model-invocation: true` (SPECIALIST'ler yalnizca acik cagriyla yuklenir; baglam kirlenmesi yok).
- `accessibility/SKILL.md`: kurulu olmayan `../web-quality-audit/SKILL.md` baglantisi pinli upstream URL'sine cevrildi.

- `dialogue-systems/SKILL.md`, `visual-novel/SKILL.md`: frontmatter'a tek satir `disable-model-invocation: true`
  (diger SPECIALIST'ler gibi yalnizca acik cagriyla yuklenir; yayinci tier D oldugu icin ozellikle). Baska degisiklik
  yok: govde ve `references/*.md` pinli commit ile bayt bayt ayni (2026-11-10'da `cmp` ile olculdu). Apache-2.0 §4
  geregi upstream deposunun kokundeki `LICENSE` ve `NOTICE` her iki dizine kopyalandi (onlar da ayni).
  Skill metinlerinin atif yaptigi `save-systems`, `godot-ui-control`, `rpg` vb. komsu skill'ler kurulu degildir;
  o atiflar bos kalir.

## Kabul taramasi (SkillSpector)

Arac: `nvidia/skillspector@16db7a03df98b6aee9e7052f75693aff46fba4b9` (v2.12.0, Apache-2.0), statik asama
(`--no-llm`). Skill degil, tarayici: depoya kopyalanmaz; `.github/workflows/skill-tarama.yml` onu
bu commit'e ve `.github/skill-tarama/gereksinimler.txt`'teki ozetlere pinli kurar. Kapi
`.github/skill-tarama/tara.py`: baseline disinda HIGH/CRITICAL bulgu = kirmizi.

2026-11-10 olcumu (10 skill, skill basina ayri tarama):

| Skill | HIGH | MEDIUM | LOW | Inceleme sonucu |
|---|---|---|---|---|
| accessibility | 10 | 2 | 0 | 9 AE1 kapsam uyarisi + 1 P2 yanlis pozitif |
| animate | 0 | 0 | 0 | temiz |
| core-web-vitals | 0 | 0 | 0 | temiz |
| dialogue-systems | 0 | 0 | 1 | EA3 yanlis pozitif (NOTICE'taki "not limited to") |
| false-green-gate | 4 | 20 | 1 | 2 TM1 + 2 LP1 yanlis pozitif; MEDIUM'lar ilk taraf betigin bilinen yetenekleri (subprocess) ve ornek `npx` komutlari |
| frontend-design | 1 | 0 | 0 | AR2 yanlis pozitif |
| performance | 0 | 2 | 0 | E1: ornek kodda `analytics.example.com` |
| playwright-cli | 4 | 14 | 0 | 3 AE1 kapsam uyarisi + 1 MP3 yanlis pozitif; MEDIUM'larin 12'si pinsiz `npx playwright` ornegi |
| review-animations | 3 | 0 | 0 | 3 AE1 kapsam uyarisi |
| visual-novel | 0 | 0 | 1 | EA3 yanlis pozitif (NOTICE) |

22 HIGH bulgunun hepsi satiri okunarak incelendi; gercek zafiyet cikmadi. Her biri gerekcesiyle
`.github/skill-tarama/baseline.yaml`'da (tam parmak izi; glob kural yok). MEDIUM/LOW bulgular
bastirilmadi, her kosuda listelenir. AE1 tarayicinin siniridir (bir ifadeyi cozemedi): o dort dosyanin
(`A11Y-PATTERNS.md`, `pr-attachments.md`, `test-generation.md`, `STANDARDS.md`) kod bloklari ve komut/ag/kimlik
kaliplari ayrica incelendi (yalniz HTML/CSS/JS ornekleri ve `playwright-cli`/`gh` ornek komutlari), ama tarayici
onlari tam incelemis sayilmaz.

## Kurulmayanlar (ozet)

Arastirmada REJECT/DUPLICATE/BROKEN cikanlar kurulmadi: anthropics
`webapp-testing` (networkidle, zayif sunucu yonetimi), trailofbits
`merge-dependabot` (`--admin` otomatik merge), vercel `web-design-guidelines`
(her kosuda pinsiz uzak talimat), ui-ux-pro-max (eksik betik), framer-motion
(Emil ile celisen degerler), OpenMontage turevleri (AGPL, malware taklidi var),
daymade youtube-downloader, MastroMimmo ffmpeg-skill (dosya okuma enjeksiyonu),
video-to-skill, alexmeckes godot-mcp (kimliksiz RCE), Impertio paketi
(`Bash(*)` settings), skateddu python-setup ve digerleri.

2026-11-10 incelemesi (tarama raporlari oturum notlarinda):

- `dietrichgebert/ponytail@96608e0` (MIT): plugin olarak RET. SessionStart/UserPromptSubmit/SubagentStart
  hook'lari her oturuma kural seti enjekte eder, `~/.claude` ve `~/.config/ponytail/band/` altina yazar,
  ajana kullanicinin `settings.json`'una statusLine eklemeyi onerttirir, istege bagli webhook'a gorev
  satiri gonderir; marketplace kurulumu `main`'i izler. 6 skill'in metni temiz (0 bulgu) ama ana skill
  "her kod isinde" kendini cagirir ve yerlesik code-review/simplify ile ortusur: simdilik alinmadi.
- `arjun988/blender-skills@904f095` (MIT): 94 skill duz markdown ve temiz (94/94 SAFE), ama Blender ve
  Blender MCP gerektirir; `.mcp.json` pinsiz `uvx blender-mcp` calistirir, kurulum belgesi `main`'den
  `addon.py` indirtir. 3D maskot sonraki fazda degil: simdilik alinmadi. Gerekince en kucuk alt kume:
  `character-artist`, `rigging`, `export-pipeline` + ortak `references/`.
- `gamedev-skills/awesome-gamedev-agent-skills` geri kalan 76 skill: ilgisiz motorlar; alinmadi.

## Guncelleme ve guven erimesi

- Guncelleme: yeni pin → `diff` incelenir (betik, bagimlilik, izin, hook, ag,
  MCP, shell degisikligi = guvenlik incelemesi yeniden) → dosyalar kopyalanir →
  proje degisiklikleri yeniden uygulanir → `kilit.py --uret` → bu tablo guncellenir →
  `python3 .github/skill-tarama/tara.py` (yeni HIGH bulgu incelenir; baseline'a yalnizca yanlis pozitif girer).
- REVERIFY tetikleyicileri: depo sahibi/transferi degisti, maintainer degisti,
  guvenlik olayi, tag'in yeniden yazilmasi, kurulum yontemi degisti, lisans degisti.

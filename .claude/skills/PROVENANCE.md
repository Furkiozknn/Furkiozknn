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

Son dogrulama: 2026-09-28. Kanit notlari arastirma raporundadir.

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

## Kurulmayanlar (ozet)

Arastirmada REJECT/DUPLICATE/BROKEN cikanlar kurulmadi: anthropics
`webapp-testing` (networkidle, zayif sunucu yonetimi), trailofbits
`merge-dependabot` (`--admin` otomatik merge), vercel `web-design-guidelines`
(her kosuda pinsiz uzak talimat), ui-ux-pro-max (eksik betik), framer-motion
(Emil ile celisen degerler), OpenMontage turevleri (AGPL, malware taklidi var),
daymade youtube-downloader, MastroMimmo ffmpeg-skill (dosya okuma enjeksiyonu),
video-to-skill, alexmeckes godot-mcp (kimliksiz RCE), Impertio paketi
(`Bash(*)` settings), skateddu python-setup ve digerleri.

## Guncelleme ve guven erimesi

- Guncelleme: yeni pin → `diff` incelenir (betik, bagimlilik, izin, hook, ag,
  MCP, shell degisikligi = guvenlik incelemesi yeniden) → dosyalar kopyalanir →
  proje degisiklikleri yeniden uygulanir → `kilit.py --uret` → bu tablo guncellenir.
- REVERIFY tetikleyicileri: depo sahibi/transferi degisti, maintainer degisti,
  guvenlik olayi, tag'in yeniden yazilmasi, kurulum yontemi degisti, lisans degisti.

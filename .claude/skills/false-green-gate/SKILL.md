---
name: false-green-gate
description: Verify that a "green" result is real before reporting it — test runs (pytest/unittest/vitest JUnit XML, Playwright JSON report, Godot headless log), media outputs (ffprobe + full decode), CI commands and diffs that add skips. Use before saying tests pass, CI is green, a download/render/clip succeeded, or when adding or changing tests, test commands or CI steps.
allowed-tools: Bash(python3 .claude/skills/false-green-gate/scripts/kapi.py:*)
---

# false-green-gate

"Komut 0 dondu" kanit degildir. Bu skill bir kosunun **biraktigi izi**
okur ve yesilin gercek olup olmadigina karar verir. FURKIOZKNN'in
`sifirtest` kuralinin calisma zamani karsiligidir (o kural PR #20 ile
`schema/politika.py`'ye geliyor): politika workflow metnine bakar, bu kapi
kosunun ciktisina.

## Ne zaman

- "Testler gecti", "CI yesil", "indirme/render/klip tamam" demeden once.
- Test, test komutu, CI adimi, snapshot ya da `skip` eklerken/degistirirken.
- Bir ajanin (Playwright healer dahil) yaptigi test degisikligini kabul etmeden once.

## Ne zaman degil

- Kodun dogru olup olmadigina karar vermek icin (o testin isi); bu kapi
  yalnizca testin gercekten kostugunu ve bir sey iddia ettigini dogrular.
- Gorsel dogruluk (tasarim) ya da erisilebilirlik yargisi icin.

## Kullanim

Kapiyi her zaman bu yolla cagir (allowed-tools on-onayi bu onekle eslesir).
Raporu kosudan once sil ve kosucunun cikis kodunu ver: eski bir rapor yeni
bir kosuyu kanitlamaz.

```bash
rm -f /tmp/r.xml; python3 -m pytest -q --junitxml=/tmp/r.xml; rc=$?
python3 .claude/skills/false-green-gate/scripts/kapi.py junit /tmp/r.xml --taban 120 --kosucu-cikis $rc --en-fazla-yas 900

rm -f /tmp/pw.json; npx playwright test --reporter=json > /tmp/pw.json; rc=$?
python3 .claude/skills/false-green-gate/scripts/kapi.py playwright /tmp/pw.json --taban 10 --kosucu-cikis $rc

godot --headless --path . --scene res://tests/t.tscn > /tmp/g.log 2>&1; rc=$?
python3 .claude/skills/false-green-gate/scripts/kapi.py godot /tmp/g.log --taban 114 --kosucu-cikis $rc

python3 .claude/skills/false-green-gate/scripts/kapi.py medya out.mp4 --video --ses --min-sure 5 --tam-cozum [--siyah] [--sessiz]
python3 .claude/skills/false-green-gate/scripts/kapi.py komut .github/workflows/*.yml
python3 .claude/skills/false-green-gate/scripts/kapi.py fark --taban-ref origin/main
```

`--taban` zorunludur ve en az 1'dir: bilinen test sayisinin altina dusus
bir bolumun sessizce kaybolmasidir. Tabani repodaki mevcut sayidan al,
tahmin etme.

## Kurallar

| Kod | Kip | FAIL kosulu |
|---|---|---|
| FG-01 | junit/playwright/godot | hic test kosmadi |
| FG-02 | hepsi | kosan < taban |
| FG-03 | hepsi | basarisiz / beklenmeyen / kalan test var |
| FG-04 | junit/playwright | atlanan > `--izinli-skip` |
| FG-05 | junit/playwright | yalnizca retry ile gecen (flaky) test var |
| FG-06 | playwright | `test.fail()` ile "basarisiz olmasi beklenen" test > izin |
| FG-07 | playwright | raporda test-disi hata (global setup/config) |
| FG-08 | godot | `=== G/T gecti ===` satiri yok (takim bitmedi) |
| FG-09 | godot | gunlukte `SCRIPT ERROR` / `Parse Error` (ozet "N/N gecti" dese bile) |
| FG-10 | medya | dosya yok/bos, ffprobe yok ya da akis bulamadi |
| FG-11 | medya | istenen video/ses akisi yok, sure < `--min-sure` |
| FG-12 | medya | tam cozmede hata (stderr; cikis kodu 0 olsa bile) |
| FG-13 | medya | baslik kare sayisi ile cozulen kare uyusmuyor; tek kare |
| FG-14 | medya | video ~tamamen siyah / ses sessiz |
| FG-15 | komut | `--pass-with-no-tests` / `--passWithNoTests` |
| FG-16 | komut | test komutunun hatasi yutuluyor (`\|\| true`, `\|\| echo`, cok satirli `\` devami dahil) ya da ciktisi pipefail olmadan pipe'a gidiyor |
| FG-17 | komut | CI'da snapshot guncelleme (`--update-snapshots`, `-u`) |
| FG-18 | hepsi | kanit okunamadi / ayni rapor iki kez / gecersiz ref (okunamayan kanit PASS degildir) |
| FG-19 | komut | WARN: `--last-failed` / `--only-changed` (tam kosu degil) |
| FG-20 | komut | WARN: `continue-on-error` ve test kosucusu ayni dosyada |
| FG-21 | fark | test dosyasina yeni `skip`/`skipIf`/`fixme`/`fail`/`only`/`todo`/`xfail`/`importorskip`/`SkipTest` eklendi (merge-base'e gore, izlenmeyen dosyalar dahil) |
| FG-22 | fark | WARN: snapshot tabani degisti (insan incelemesi) |
| FG-23 | junit/playwright/godot | `--kosucu-cikis` 0 degil (rapor yesil gorunse bile) |
| FG-24 | junit/playwright | rapor `--en-fazla-yas` saniyeden eski |
| FG-25 | komut | WARN: `set +e` ve test kosucusu ayni dosyada |

`fark` yalnizca test dosyalarina bakar (`tests/`, `test_*.py`, `*_test.py`,
`*.spec.*`, `*.test.*`, `__tests__/`, `e2e/`, `.gd`); yorum satirlari sayilmaz.
Bilincli bir istisna ayni satirda `kapi: izinli` ile isaretlenir ve WARN
olarak raporlanir; gerekcesi incelemede sorulur.

## Hard rules

1. Kapi FAIL derse sonucu "yesil" diye raporlama; bulguyu kanit JSON'u ile birlikte bildir.
2. Kapiyi gecmek icin taban dusurme, `--izinli-*` artirma ya da test atlama; bunlar kullanicinin kararidir ve gerekcesi yazilir.
3. Kapiyi kosan ajan, kapinin denetledigi degisikligi yapan ajanla ayni ise sonucu "bagimsiz dogrulandi" diye sunma.
4. Medya dosyasi icin yalnizca yerel yol ver; URL verme (kapi `file:` + `-protocol_whitelist file` ile calisir).

## Output

Son satir tek satirlik JSON: `{"kapi","sonuc":"PASS|FAIL","olcum":{...},"bulgular":[...]}`.
Raporda sonucu ve `olcum`'daki sayilari aynen aktar.

## Kendi sinamasi

`python3 .claude/skills/false-green-gate/test_kapi.py` — her kural icin PASS
ve FAIL fiksturu; bagimsiz incelemenin buldugu 13 hatanin her biri icin bir
regresyon testi. Her FAIL kurali tek tek WARN'a cevrildiginde takimin
kirmiziya dondugu olculur (mutasyon taramasi).

## Bilinen sinirlar

- Godot kipi yalnizca `SCRIPT ERROR` / `Parse Error` arar; motorun
  `ERROR:` satirlari (cikista "resources still in use" gibi) bilerek sayilmaz.
- Medya kipinde "tek kare" kontrolu yalnizca tam 1 kareyi yakalar.
- `komut` kipi metin tabanlidir; betik icinden cagrilan bir test komutunu goremez.
- `fark` kipinde merge-base bulunduktan sonra `git diff`'in basarisiz oldugu
  savunma dali testle tetiklenemiyor (mutasyon taramasinda tek hayatta kalan).
- Alt surec zaman asimi varsayilan 600 s; `KAPI_ZAMAN_ASIMI` ile degisir,
  asildiginda FAIL (FG-12 / FG-18).
- `test_kapi.py` atlanan her testi hata sayar (ffmpeg ya da git yoksa kirmizi);
  bilincli istisna icin `KAPI_ATLAMA_IZNI=1`.

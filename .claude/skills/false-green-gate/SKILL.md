---
name: false-green-gate
description: Verify that a "green" result is real before reporting it — test runs (pytest/unittest/vitest JUnit XML, Playwright JSON report, Godot headless log), media outputs (ffprobe + full decode), CI commands and diffs that add skips. Use before saying tests pass, CI is green, a download/render/clip succeeded, or when adding or changing tests, test commands or CI steps.
allowed-tools: Bash(python3 .claude/skills/false-green-gate/scripts/kapi.py:*)
---

# false-green-gate

"Komut 0 dondu" kanit degildir. Bu skill bir kosunun **biraktigi izi**
okur ve yesilin gercek olup olmadigina karar verir. FURKIOZKNN'in
`sifirtest` kuralinin (schema/politika.py) calisma zamani karsiligidir:
politika workflow metnine bakar, bu kapi kosunun ciktisina.

## Ne zaman

- "Testler gecti", "CI yesil", "indirme/render/klip tamam" demeden once.
- Test, test komutu, CI adimi, snapshot ya da `skip` eklerken/degistirirken.
- Bir ajanin (Playwright healer dahil) yaptigi test degisikligini kabul etmeden once.

## Ne zaman degil

- Kodun dogru olup olmadigina karar vermek icin (o testin isi); bu kapi
  yalnizca testin gercekten kostugunu ve bir sey iddia ettigini dogrular.
- Gorsel dogruluk (tasarim) ya da erisilebilirlik yargisi icin.

## Kullanim

```bash
K=.claude/skills/false-green-gate/scripts/kapi.py
python3 -m pytest --junitxml=/tmp/r.xml -q; python3 $K junit /tmp/r.xml --taban 120
npx playwright test --reporter=json > /tmp/pw.json; python3 $K playwright /tmp/pw.json --taban 10
godot --headless --path . --scene res://tests/t.tscn 2>&1 | tee /tmp/g.log; python3 $K godot /tmp/g.log --taban 114
python3 $K medya out.mp4 --video --ses --min-sure 5 --tam-cozum [--siyah] [--sessiz]
python3 $K komut .github/workflows/*.yml
python3 $K fark --taban-ref origin/main
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
| FG-16 | komut | test komutunun hatasi yutuluyor (`\|\| true`) |
| FG-17 | komut | CI'da snapshot guncelleme (`--update-snapshots`, `-u`) |
| FG-18 | hepsi | kanit okunamadi (okunamayan rapor PASS degildir) |
| FG-19 | komut | WARN: `--last-failed` / `--only-changed` (tam kosu degil) |
| FG-20 | komut | WARN: `continue-on-error` ve test kosucusu ayni dosyada |
| FG-21 | fark | yeni `skip`/`fixme`/`fail`/`only`/`xfail` isareti eklendi |
| FG-22 | fark | WARN: snapshot tabani degisti (insan incelemesi) |

## Hard rules

1. Kapi FAIL derse sonucu "yesil" diye raporlama; bulguyu kanit JSON'u ile birlikte bildir.
2. Kapiyi gecmek icin taban dusurme, `--izinli-*` artirma ya da test atlama; bunlar kullanicinin kararidir ve gerekcesi yazilir.
3. Kapiyi kosan ajan, kapinin denetledigi degisikligi yapan ajanla ayni ise sonucu "bagimsiz dogrulandi" diye sunma.
4. Medya dosyasi icin yalnizca yerel yol ver; URL verme (kapi `file:` + `-protocol_whitelist file` ile calisir).

## Output

Son satir tek satirlik JSON: `{"kapi","sonuc":"PASS|FAIL","olcum":{...},"bulgular":[...]}`.
Raporda sonucu ve `olcum`'daki sayilari aynen aktar.

## Kendi sinamasi

`python3 .claude/skills/false-green-gate/test_kapi.py` — 50 test, her kural
icin PASS ve FAIL fiksturu. Kuralin kendisi zayiflatildiginda (FAIL→WARN)
her mutantin bu takim tarafindan yakalandigi ayrica olculdu (29/29).

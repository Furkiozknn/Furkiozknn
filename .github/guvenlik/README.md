# Guvenlik kapisi ve ajan izinleri

Bu klasor iki seyi kaydeder: CI'daki guvenlik tarayicilarinin **kurulum
kaydi** (kim yayimliyor, hangi surum, hangi ozet, nasil olculdu) ve
`.claude/settings.json`'daki ajan izin kurallarinin gerekcesi.

## Kurulum kaydi

Son dogrulama: 2026-09-28. Hepsi ucretsiz ve acik kaynak.

| Arac | Yayinci (tier) | Surum ve pin | Lisans | Rol | Kapi mi |
|---|---|---|---|---|---|
| zizmor | William Woodruff / zizmorcore (B: PyPI Trusted Publishing, Trail of Bits kokenli, Astral destekli) | PyPI `zizmor==1.30.1`, `manylinux_2_28_x86_64` tekerlegi `sha256:eee12266…232a8e`, `--require-hashes --no-deps` | MIT | is akisi guvenligi (pinsiz eylem, sablon enjeksiyonu, artipacked, asiri izin) | evet |
| betterleaks | betterleaks (C: gitleaks'in ozgun yazari Zach Rice'in catali) | `go install …@v1.8.1`, modul ozeti `h1:tTSQAdQe+S4MF69o6VtpRDlml1b73F1xNUUA3PcrHiI=`, Go 1.25.12 (`go.mod` toolchain), `GOTOOLCHAIN=local` | MIT | git gecmisinde sizmis anahtar | evet |

| lychee | lycheeverse, yayinci mre / Matthias Endler (B: 2020'den beri, crates.io'da 222 bin indirme, Apache-2.0 OR MIT) | GitHub release `lychee-v0.24.2`, `lychee-x86_64-unknown-linux-gnu.tar.gz` `sha256:1f4e0ef7…1c9a` (ozet dosyasi ayni kaynaktan: butunluk kaniti, yayinci kaniti degil; crates.io kaynak ozeti `d4aa20c1…7b48`) | Apache-2.0 OR MIT | Markdown yerel link + baslik capasi, **cevrimdisi** | evet (`baglanti.yml`) |

lychee olcumleri (izole, 2026-09-28):

- Ekosistemin 27 deposunda 631 yerel link/capa: 1 gercek kirik (ajans-os `[1.0.1](...)`), 1 sahte kirmizi (buradane: emoji+U+FE0F basligi; GitHub capayi tutuyor, lychee bulamiyor). Turkce basliklar (ş, ğ, ı) dogru cozuldu.
- Sahte yesil: hic dosya eslesmeyince `0 Total`, cikis 0; capalar varsayilan olarak denetlenmez; `--offline` kipte uzak linkler sessizce "excluded". Hepsi `.github/baglanti/kontrol.py` ile kapali, `test_kontrol.py` 8 test; sarmalayicinin 4 korumasi tek tek kaldirildiginda takim kirmizi (5. koruma erisilemezdi, silindi).
- Ag yokken uzak link denetimi kirmizi doner (sahte yesil degil); CI bu yuzden cevrimdisi kipte.

Kurulmayanlar ve nedeni (ayni laboratuvar olcumu, 12 bilincli hatali fikstur):

- **osv-scanner v2.6.0**: bu depoda bagimlilik dosyasi yok; `No package sources found`, cikis 128. Kilit dosyasi olan depolar icin onerilir (`--no-resolve`, cevrimdisi veritabani).
- **gitleaks**: betterleaks ile ayni isi yapiyor (DUPLICATE).
- **actionlint**: zizmor'un bulduklarinin alt kumesi + shellcheck notlari; kapi olarak ek deger olculmedi.
- **pip-audit, grype**: burada Python/Go kilit dosyasi yok.
- **trivy**: 2026 tedarik zinciri olayindan sonra ikili dogrulanamadi (REJECT).

## Olculen tuzaklar (neden boyle yazildi)

- `zizmor --format sarif` bulgu olsa da **0 doner**; kapi `--format github` ile kosar (bulguda 13/14 doner).
- `betterleaks --validation` bulunan anahtari dogrulamak icin **canli API'lere gonderir**; kullanilmiyor.
- Sig klonda betterleaks yalnizca son commit'i tarar ve temiz der; is `fetch-depth: 0` + `is-shallow-repository` kontrolu yapar.
- Satir ici `gitleaks:allow` yorumu bir PR'in kapiyi susturmasina izin verir; `--ignore-gitleaks-allow` ile kapali.
- Dusuk entropili sahte anahtar (tekrar eden parca) betterleaks'te **sessizce gecer**. Oz sinamanin ilk surumu bunu yakaladi; sahte anahtar artik yuksek entropili ve deterministik.
- Varsayilan kurallarla `.claude/skills/kilit.json`'daki sha256 ozetleri `generic-api-key` sayiliyor (6 bulgu). Istisna AND kosullu: yalnizca o dosya **ve** tam 64 hex. Ayni dosyaya konan gercek bir anahtar hala yakalanir (oz sinama 3. ve 4. durum).

## Oz sinama

`oz_sinama.sh zizmor|betterleaks` gercek depodan once her tarayicinin bilinen
kotu girdide kirmiziya donebildigini kanitlar. Kapi yesilse ama oz sinama
kirmiziysa, yesil hicbir sey soylemiyor demektir.

## Yukseltme

Yeni surum → laboratuvarda fiksturlerle yeniden olc (bulgu sayisi, cikis
kodlari, `--format github` davranisi) → ozeti degistir → bu tabloyu
guncelle. Bu klasordeki bir degisiklik ya da `guvenlik.yml` degisikligi
guvenlik incelemesidir (insan).

## `.claude/settings.json` -- ajan izinleri

Proje ayari; bu depoda calisan her Claude Code oturumuna uygulanir.

- **deny**: geri alinamayan, para harcayan, yayimlayan ya da sir tasiyan
  islemler. `git push --force`/`--delete`/etiket push'u, `gh pr merge`,
  `gh pr review --approve`, release, `gh secret`, PyPI/npm publish, `.env`
  okuma; bagli MCP sunucularinda merge/auto-merge, dosya silme, satin alma
  (Vercel `buy_*`), ortam degiskeni/anahtar/token, uretime terfi, e-posta
  gonderme/cop, Drive paylasma/cop, Supabase SQL/migration/dal silme,
  higgsfield yayimlama/sir/uzak komut, Vercel oturum komutu ve DNS kaydi.
- **ask**: geri alinabilir ama disa donuk yazmalar: `git tag`, `main`'e
  push, API ile dogrudan dosya yazma (dal korumasini atlar), PR incelemesi
  (approve ayni aracta), Slack mesaji, takvim olayi, ve higgsfield sunucusunun
  tamami (`generate_*` kredi harcar; yukaridaki deny'lar yine onceliklidir).

Sinirlar (acikca):

- Bash kurallari metin eslesmesidir, guvenlik siniri degil. `git -C . push -f`,
  `sh -c "…"`, `VAR=1 git push -f` ya da bir git takma adi eslesmeyi atlar.
  Gercek sinir GitHub'daki dal korumasi ve token yetkileridir (insan ayari).
- MCP arac adlari baglayiciya gore degisir; buradaki adlar bu ortamdaki
  (`mcp__github__…`, `mcp__Vercel__…`) adlardir. Baska bir istemcide farkli
  bir onekle gelen ayni arac bu kurala takilmaz.
- Kurallar kullanici ayariyla birlesir; deny her zaman onceliklidir.

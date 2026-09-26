#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is akisi ve tedarik zinciri politikasi: 27 deponun ortak kurallari.

NEDEN VAR
---------
25 Eylul 2026'daki envanter, ayni kusurlarin depo depo tekrarlandigini
gosterdi -- ve hicbirinin tek tek duzeltilmesinin kalici olmadigini:

  - 128 isin 108'inde `timeout-minutes` yoktu. Takilan bir test (donmeyen
    bir `await`, sonsuz bir dongu) GitHub'in varsayilani olan 6 saat boyunca
    kosuyor; derin-kazi'de bu tam olarak goruldu.
  - 16 Dependabot yapilandirmasinin hicbiri gruplamiyordu. Haftada her
    action icin ayri PR: 36 acik Dependabot PR'i, her biri elle birlestirilmeyi
    bekliyor. upload-artifact / download-artifact ciftinin "birlikte
    birlestir" kurali da bu yuzden bir insanin hafizasinda duruyordu.
  - 11 depoda Dependabot hic yoktu; action surumleri depodan depoya
    dagilmisti (actions/checkout v4, v5, v6 ve v7 ayni anda).
  - buradane'nin frontend/package-lock.json ve backend/uv.lock dosyalari
    hicbir guncellemenin kapsaminda degildi.

Bir kurali bir depoda duzeltmek bugunu kurtarir; kurali burada yazmak bir
sonraki depoda ayni kusurun geri gelmesini engeller. Bu dosya kurallarin
tek kaynagi. Iki yerden cagrilir:

    python3 schema/politika.py --kok klonlar/      # klonlanmis depolar
    python3 schema/politika.py --depo . --kati     # bu deponun kendi CI'i
    denetim.py                                    # gunluk, GitHub API ile

Kural motoru agsiz ve saf: girdi {yol: metin} sozlugu, cikti bulgu listesi.
Dosyayi nereden okudugunu bilmez; o yuzden klondan da API'den de ayni
sonucu verir ve testleri ag olmadan kosar.

SEVIYELER
---------
  FAIL  bir guvenlik ya da dogruluk kusuru: kirmiziyi yesil gosterebilir,
        ya da disaridan gelen metni kabukta calistirir.
  WARN  guvenilirlik / bakim maliyeti: bugun calisir, bir gun pahaliya patlar.

Bilerek OLMAYANLAR (kural yazmak kolay, ama yanlis alarm uretir):
  - `inputs.*` ifadelerinin `run:` icinde kullanimi. workflow_dispatch'i
    yalnizca depoya yazabilen biri tetikleyebilir; guven siniri degil.
  - `continue-on-error`. Depolarda bilincli kullaniliyor (repo-vet'in kendi
    kendini denetlemesi); kurali gerekcesiyle birlikte istisna yazmadan
    koymak her gun ayni satiri raporlardi.
  - Ortak (reusable) yayin is akisi. PyPI Trusted Publishing yeniden
    kullanilabilir bir is akisinin icinden calismiyor
    (pypa/gh-action-pypi-publish bunu acikca soyluyor); 12 yayin kopyasini
    birlestirmek ilk surumlerden hemen once hepsinin yayin yolunu kirardi.

Yalnizca PyYAML gerekir (is akisi dosyalari YAML). Yoksa `yaml_yok()`
bunu soyler; cagiran taraf "bakilamadi" yazar, "temiz" yazmaz.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # denetim.py bunu "politika bakilamadi" diye raporlar
    yaml = None

FAIL, WARN = "FAIL", "WARN"

# GitHub'in kendi kuruluslari. Geri kalan her `uses:` ucuncu taraf kodudur
# ve CI'da depo jetonuyla calisir: bir etiket (v7) yeniden yazilabilir, bir
# commit SHA'si yazilamaz.
BIRINCI_TARAF = ("actions/", "github/")

# Disaridan (PR acan, yorum yazan herkes) gelen metin. Bunlar `run:` icine
# `${{ }}` ile gomulurse kabukta komut olarak calisir; `actions/github-script`
# in `script:` alanina gomulurse ayni sey JavaScript olarak olur.
# workflow_run'da yalnizca metin alanlari: `.id`, `.conclusion` guvenli.
_DIS_BAGLAM = (
    r"github\.event(?:\.|\[['\"])(?:issue|pull_request|comment|review|review_comment|discussion"
    r"|discussion_comment|pages|head_commit|commits)\b"
    r"|github\.event(?:\.|\[['\"])workflow_run(?:['\"]\])?\.(?:head_branch|display_title|head_commit"
    r"|pull_requests|head_repository)\b"
    r"|github\.head_ref\b")
# Baglam `${{` nin hemen ardinda olmak zorunda degil: toJSON(...), format(...)
# ya da koseli parantezli yazim da ayni metni kabuga tasir.
GUVENSIZ_IFADE = re.compile(r"\$\{\{((?:(?!\}\}).)*?(?:" + _DIS_BAGLAM + r")(?:(?!\}\}).)*)\}\}")

# Bir test kosucusunun ciktisi boruya giriyorsa (`pytest | tee log`), borunun
# cikis kodu SONDAKI komutundur. GitHub'in varsayilan kabugu `bash -e {0}`;
# pipefail YOK. Yani `tee` 0 dondururken dusen test yesil gorunur. `shell:
# bash` acikca yazildiginda ise GitHub `bash --noprofile --norc -eo pipefail`
# kullanir.
TEST_KOSUCU = re.compile(
    r"\b(pytest|unittest|cargo\s+test|npm\s+(run\s+)?test|npx\s+vitest|vitest"
    r"|node\s+--test|playwright\s+test|godot)\b")
BORU = re.compile(r"(?<!\|)\|(?!\|)")

KILIT_EKOSISTEM = {"uv.lock": ("uv", "pip"), "package-lock.json": ("npm",),
                   "Cargo.lock": ("cargo",)}
# Bu dizinlerdeki kilit dosyasi bir bagimlilik degil, test verisidir: bu
# deponun kendi schema/fikstur/'u gibi. node_modules zaten baskasinin kilidi.
KILIT_DISI = {"node_modules", "fixtures", "fixture", "fikstur", "testdata"}


# Denetim raporunda kullanilan kisa adlar.
KURAL_ADI = {
    "sure": "timeout-minutes yok", "pin": "SHA'siz ucuncu taraf action",
    "izin": "permissions tanimsiz", "dependabot": "Dependabot eksik",
    "grup": "gruplanmamis Dependabot", "kilit": "kapsam disi kilit dosyasi",
    "tetik": "riskli tetikleyici", "enjeksiyon": "kabukta dis girdi",
    "boru": "pipefail'siz test borusu", "yaml": "okunamayan YAML",
    "dbgecersiz": "gecersiz Dependabot yapilandirmasi",
}


def yaml_yok():
    return yaml is None


def _yukle(metin):
    """YAML'i yukler; `on:` anahtarini True'ya ceviren YAML 1.1 tuzagina
    dusmeden (GitHub `on` yazar, PyYAML onu bool okur)."""
    class Yukleyici(yaml.SafeLoader):
        pass
    Yukleyici.add_constructor(
        "tag:yaml.org,2002:bool", lambda y, d: y.construct_scalar(d))
    return yaml.load(metin, Loader=Yukleyici) or {}


def _tetikler(y):
    on = y.get("on")
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    if isinstance(on, dict):
        return set(on)
    return set()


def _pipefail_acik(run, kabuk):
    return kabuk == "bash" or re.search(r"\bset\s+-[a-z]*o\s+pipefail|pipefail", run) is not None


def is_akisi_bulgulari(yol, metin):
    """Tek bir is akisi dosyasi -> [(seviye, kural, mesaj)]."""
    ad = yol.rsplit("/", 1)[-1]
    try:
        y = _yukle(metin)
    except yaml.YAMLError as e:
        return [(FAIL, "yaml", "%s okunamadi: %s" % (ad, str(e).splitlines()[0]))]
    if not isinstance(y, dict):
        return [(FAIL, "yaml", "%s bir is akisi degil" % ad)]

    b = []
    tetik = _tetikler(y)
    isler = y.get("jobs") or {}
    ust_izin = "permissions" in y
    ust_kabuk = ((y.get("defaults") or {}).get("run") or {}).get("shell")

    tehlikeli = tetik & {"pull_request_target", "workflow_run"}
    for t in sorted(tehlikeli):
        # Bu tetikleyiciler depo jetonuyla ve sirlarla kosar; PR'in kodunu
        # checkout edip calistirmak tam da "pwn request" saldirisidir.
        guvensiz_checkout = re.search(
            r"ref:\s*\$\{\{\s*github\.event\.(pull_request\.head|workflow_run\.head)", metin)
        b.append((FAIL if guvensiz_checkout else WARN, "tetik",
                  "%s: %s tetikleyicisi%s" % (
                      ad, t, " ve PR'in kendi kodunun checkout'u" if guvensiz_checkout
                      else " (gerekcesi dosyada yazmali)")))

    zamansiz, izinsiz = [], []
    for jn, j in isler.items():
        if not isinstance(j, dict):
            continue
        if "uses" in j:  # yeniden kullanilabilir is akisi cagrisi
            continue
        if j.get("timeout-minutes") is None:
            zamansiz.append(jn)
        if not ust_izin and "permissions" not in j:
            izinsiz.append(jn)
        is_kabuk = ((j.get("defaults") or {}).get("run") or {}).get("shell") or ust_kabuk
        for i, s in enumerate(j.get("steps") or [], 1):
            if not isinstance(s, dict):
                continue
            adim = s.get("name") or ("adim %d" % i)
            u = s.get("uses")
            if isinstance(u, str) and not u.startswith("./"):
                ad_, _, ref = u.partition("@")
                if u.startswith("docker://"):
                    if "@sha256:" not in u:
                        b.append((WARN, "pin", "%s:%s: %s digest ile sabitlenmemis" % (ad, jn, u)))
                elif not ad_.startswith(BIRINCI_TARAF) and not re.fullmatch(r"[0-9a-f]{40}", ref):
                    b.append((WARN, "pin", "%s:%s: %s commit SHA'siyla sabitlenmemis" % (ad, jn, u)))
            betik = (s.get("with") or {}).get("script") if isinstance(s.get("with"), dict) else None
            if isinstance(u, str) and u.startswith("actions/github-script") and isinstance(betik, str):
                m = GUVENSIZ_IFADE.search(betik)
                if m:
                    b.append((FAIL, "enjeksiyon",
                              "%s:%s (%s): disaridan gelen `%s` github-script'te JavaScript olarak"
                              % (ad, jn, adim, m.group(1).strip()[:48])))
            r = s.get("run")
            if isinstance(r, str):
                m = GUVENSIZ_IFADE.search(r)
                if m:
                    b.append((FAIL, "enjeksiyon",
                              "%s:%s (%s): disaridan gelen `%s` dogrudan kabukta"
                              % (ad, jn, adim, m.group(1).strip()[:48])))
                kabuk = s.get("shell") or is_kabuk
                if kabuk not in ("pwsh", "powershell", "python", "cmd") and not _pipefail_acik(r, kabuk):
                    for satir in r.splitlines():
                        if satir.lstrip().startswith("#"):
                            continue
                        parca = BORU.split(satir)
                        if len(parca) > 1 and any(TEST_KOSUCU.search(p) for p in parca[:-1]):
                            b.append((FAIL, "boru",
                                      "%s:%s (%s): test ciktisi pipefail olmadan boruda -- "
                                      "dusen test yesil gorunur: `%s`"
                                      % (ad, jn, adim, satir.strip()[:70])))
                            break
    if zamansiz:
        b.append((WARN, "sure", "%s: timeout-minutes yok: %s (varsayilan 6 saat)"
                  % (ad, ", ".join(zamansiz))))
    if izinsiz:
        b.append((WARN, "izin", "%s: permissions tanimsiz: %s (jeton depo ayarindaki "
                  "varsayilanla gelir)" % (ad, ", ".join(izinsiz))))
    return b


def _dependabot(metin):
    """-> (guncellemeler, sorun). sorun None degilse GitHub dosyanin TAMAMINI reddeder."""
    try:
        y = _yukle(metin)
    except yaml.YAMLError as e:
        return [], "YAML okunamadi: %s" % str(e).splitlines()[0]
    if not isinstance(y, dict):
        return [], "bir yapilandirma degil"
    guncellemeler = [u for u in (y.get("updates") or []) if isinstance(u, dict)]
    # 11 depoda `version: 2` bir yorum satirinin sonuna yapismisti
    # ("...guncelliyor.version: 2"): YAML icin o bir yorum, dosyada surum yok.
    # GitHub yapilandirmanin tamamini reddeder ve hicbir guncelleme acilmaz --
    # hic kirmizi yanmadan. Dogrulayici yalnizca dosya bir PR'da degisince kosar.
    if str(y.get("version")) != "2":
        return guncellemeler, "`version: 2` yok -- GitHub dosyanin tamamini reddeder, hicbir guncelleme acilmaz"
    return guncellemeler, None


def _kilit_bos_mu(yol, metin):
    """Bagimliligi olmayan bir projenin kilidi guncellenecek bir sey tasimaz."""
    if metin is None:
        return False
    if yol.endswith("Cargo.lock"):
        return metin.count("[[package]]") <= 1
    if yol.endswith("package-lock.json"):
        try:
            j = json.loads(metin)
        except ValueError:
            return False
        paketler = j.get("packages") or {}
        return len([k for k in paketler if k]) == 0 and not j.get("dependencies")
    return False


def depo_bulgulari(dosyalar):
    """Bir deponun ilgili dosyalari -> [(seviye, kural, mesaj)].

    `dosyalar`: {depo-ici yol: metin ya da None}. None "dosya var, icerigi
    okunmadi" demektir (kilitler icin yalnizca varligi yeterli olabilir).
    Beklenen yollar: .github/workflows/*.yml, .github/dependabot.yml ve
    deponun herhangi bir yerindeki uv.lock / package-lock.json / Cargo.lock.
    """
    b = []
    akislar = {y: m for y, m in dosyalar.items()
               if y.startswith(".github/workflows/") and y.endswith((".yml", ".yaml"))}
    for y in sorted(akislar):
        if akislar[y] is not None:
            b.extend(is_akisi_bulgulari(y, akislar[y]))

    db_yol = next((y for y in (".github/dependabot.yml", ".github/dependabot.yaml")
                   if y in dosyalar), None)
    guncellemeler = None
    if db_yol and dosyalar[db_yol]:
        guncellemeler, sorun = _dependabot(dosyalar[db_yol])
        if sorun:
            b.append((FAIL, "dbgecersiz", "%s: %s" % (db_yol.rsplit("/", 1)[-1], sorun)))
    action_var = any("uses:" in (m or "") for m in akislar.values())

    if guncellemeler is None:
        if action_var:
            b.append((WARN, "dependabot", "Dependabot yok: action surumleri kendiliginden "
                      "guncellenmiyor"))
        guncellemeler = []
    else:
        if action_var and not any(u.get("package-ecosystem") == "github-actions"
                                  for u in guncellemeler):
            b.append((WARN, "dependabot", "Dependabot github-actions'i kapsamiyor"))
        for u in guncellemeler:
            if not u.get("groups"):
                b.append((WARN, "grup", "Dependabot %s (%s) gruplanmamis: her paket "
                          "ayri PR" % (u.get("package-ecosystem"), u.get("directory", "/"))))

    for yol, metin in sorted(dosyalar.items()):
        dosya = yol.rsplit("/", 1)[-1]
        if dosya not in KILIT_EKOSISTEM or KILIT_DISI & set(yol.split("/")[:-1]):
            continue
        if _kilit_bos_mu(yol, metin):
            continue
        dizin = _dizin(yol.rsplit("/", 1)[0] if "/" in yol else "")
        kapsayan = [u for u in guncellemeler
                    if u.get("package-ecosystem") in KILIT_EKOSISTEM[dosya]
                    and _dizin(u.get("directory", "/")) == dizin]
        if not kapsayan:
            b.append((WARN, "kilit", "%s hicbir Dependabot girdisinin kapsaminda degil" % yol))
    return b


def _dizin(d):
    """'/', '', 'frontend', '/frontend/' -> '/' ya da '/frontend'."""
    return "/" + str(d or "").strip("/")


def durum(bulgular):
    seviyeler = {s for s, _, _ in bulgular}
    return FAIL if FAIL in seviyeler else WARN if WARN in seviyeler else "PASS"


def klondan_oku(kok):
    """Bir calisma agacindan politikanin baktigi dosyalari toplar."""
    kok = Path(kok)
    d = {}
    for p in sorted((kok / ".github" / "workflows").glob("*.y*ml")):
        d[".github/workflows/" + p.name] = p.read_text(encoding="utf-8", errors="replace")
    for ad in ("dependabot.yml", "dependabot.yaml"):
        p = kok / ".github" / ad
        if p.is_file():
            d[".github/" + ad] = p.read_text(encoding="utf-8", errors="replace")
    for kilit in KILIT_EKOSISTEM:
        for p in kok.rglob(kilit):
            goreli = p.relative_to(kok).as_posix()
            if "node_modules/" in goreli or goreli.startswith((".git/", ".venv/")):
                continue
            d[goreli] = p.read_text(encoding="utf-8", errors="replace")
    return d


def _yazdir(sonuc, ayrinti=True):
    for ad in sorted(sonuc):
        bl = sonuc[ad]
        print("%-4s  %-28s %s" % (durum(bl), ad, "" if not bl else "%d bulgu" % len(bl)))
        if ayrinti:
            for s, k, m in bl:
                print("        %s %-10s %s" % (s, k, m))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--kok", help="her alt dizini bir depo olan klasor")
    g.add_argument("--depo", help="tek bir deponun calisma agaci")
    ap.add_argument("--kati", action="store_true", help="WARN da cikis kodunu 1 yapar")
    ap.add_argument("--json", help="sonucu bu dosyaya da yaz")
    ap.add_argument("--ozet", action="store_true", help="yalnizca depo basina durum")
    a = ap.parse_args(argv)
    if yaml_yok():
        print("PyYAML yok: politika bakilamadi (python3 -m pip install pyyaml==6.0.3).")
        return 2

    if a.depo:
        sonuc = {Path(a.depo).resolve().name: depo_bulgulari(klondan_oku(a.depo))}
    else:
        sonuc = {p.name: depo_bulgulari(klondan_oku(p))
                 for p in sorted(Path(a.kok).iterdir()) if (p / ".git").exists()}
    _yazdir(sonuc, ayrinti=not a.ozet)
    sayim = {s: sum(1 for bl in sonuc.values() if durum(bl) == s) for s in ("PASS", "WARN", "FAIL")}
    print("\n%d depo: %d PASS, %d WARN, %d FAIL" % (len(sonuc), sayim["PASS"], sayim["WARN"], sayim["FAIL"]))
    if a.json:
        Path(a.json).write_text(json.dumps(
            {ad: {"durum": durum(bl), "bulgular": [{"seviye": s, "kural": k, "mesaj": m}
                                                   for s, k, m in bl]}
             for ad, bl in sorted(sonuc.items())}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    if sayim["FAIL"] or (a.kati and sayim["WARN"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Toplu bir degisiklik yalnizca beklenen seyi mi degistirdi -- commit'ten ONCE.

    # tek depo (pilot): calisma agaci, taban commit'e gore
    python3 schema/degisim.py --kok klon/mcp-vet --taban origin/main \\
        --dosya '.github/workflows/*.yml' --silinebilir '^\\s*(-\\s*)?uses:'

    # pilot gectikten sonra hepsi, patlama yaricapi ile
    python3 schema/degisim.py --kok klon/* --taban HEAD --dosya ... --azami-depo 27

NEDEN VAR
---------
25 Eylul 2026'da action'lari SHA'ya sabitleyen bir regex (`uses:\\s*...`)
satir sonunu da yuttu: alti depoda `uses:` satirinin altindaki sekiz yorum
satiri ve bos satirlar sessizce silindi. Testler gecti, politika PASS dedi,
CI yesildi -- cunku hicbiri "bu dosyada baska ne degisti" diye sormuyor.
Hatayi bagimsiz bir dogrulama ajani diff'i okuyarak buldu. Bu betik o okumayi
makineye yaptirir: donusumun kendi testleri degil, ciktisinin diff'i yargilanir.

KAPILAR (herhangi biri FAIL -> depo FAIL)
-----------------------------------------
  dosya_disi   degisen dosya --dosya kaliplarinin hicbirine uymuyor
  silme        dosya silinmis / adi degismis / tipi ya da kipi degismis
  bos_satir    bos bir satir silinmis
  yorum        yorum satiri silinmis (bir --silinebilir kalibi onu acikca
               hedeflemiyorsa) ya da bir satirin sonundaki yorum kaybolmus
  beklenmeyen  silinen satir --silinebilir kaliplarinin hicbirine uymuyor
               (--silinebilir yoksa donusum yalnizca EKLEYEBILIR)
  bosluk       yalnizca bosluk / satir sonu (CRLF) degismis
  son_satir    dosyanin sonundaki satir sonu kaybolmus
  sozdizimi    degisen .yml/.yaml/.json/.toml artik okunmuyor
               (--bozuk-olabilir: bilerek bozuk fikstur)
  politika     schema/politika.py: yeni bir FAIL cikti ya da WARN sayisi artti
  patlama      --azami-depo'dan fazla depo degisiyor (hicbiri gecmis sayilmaz)

Degismeyen depo PASS'tir ve "degisiklik yok" diye yazilir: 27 depoya
uygulanan bir donusumun 3 depoda hicbir sey yapmamasi da bir bilgidir.

Cikis kodu: 0 hepsi PASS, 1 en az bir FAIL, 2 bakilamadi (git yok, taban yok).
Bakilamayan depo "gecti" sayilmaz.
"""

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

BURASI = Path(__file__).resolve().parent


def _politika_modulu():
    spec = importlib.util.spec_from_file_location("degisim_politika", BURASI / "politika.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _politika_modulu()

YORUM_SATIRI = re.compile(r"^\s*(#|//)")
POLITIKA_YOLU = re.compile(
    r"^\.github/(workflows/[^/]+\.ya?ml|dependabot\.ya?ml)$|(^|/)(uv\.lock|package-lock\.json|Cargo\.lock)$")


class Bakilamadi(Exception):
    pass


def _git(kok, *arg):
    # Bayt olarak okunur: metin kipi \r\n'yi \n'ye cevirir ve CRLF degisimi gorunmez olur.
    # Kullanicinin git ayarlari ciktinin bicimini degistirmesin.
    r = subprocess.run(["git", "-C", str(kok), "-c", "core.quotepath=off", "-c", "diff.noprefix=false",
                        "-c", "diff.mnemonicPrefix=false", *arg], capture_output=True)
    if r.returncode != 0:
        raise Bakilamadi("git %s: %s" % (" ".join(arg[:2]),
                                         r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r.stdout.decode("utf-8", "surrogateescape")


def satir_sonu_yorumu(satir):
    """'x: 1  # neden' -> 'neden'. Tirnakli bir degerin icindeki # yorum degildir.

    Tirnak yalnizca bir degerin BASINDA acilir (satir basi, bosluk, `:[{,`
    sonrasi): "Don't skip # keep" icindeki kesme isareti bir tirnak degildir.
    """
    tirnak, onceki = None, " "
    for i, c in enumerate(satir):
        if tirnak:
            if c == tirnak:
                tirnak = None
        elif c in "'\"" and onceki in " \t:[{,-":
            tirnak = c
        elif c == "#" and onceki in " \t":
            return satir[i + 1:].strip() or None
        onceki = c
    return None


def kaliba_uyar(yol, kalip):
    """Kabuk globu gibi: `*` ve `?` bir dizin sinirini gecmez, `**` gecer."""
    r, i = "", 0
    while i < len(kalip):
        if kalip.startswith("**", i):
            r, i = r + ".*", i + 2
        elif kalip[i] == "*":
            r, i = r + "[^/]*", i + 1
        elif kalip[i] == "?":
            r, i = r + "[^/]", i + 1
        else:
            r, i = r + re.escape(kalip[i]), i + 1
    return re.fullmatch(r, yol) is not None


def _yol_coz(hedef):
    """'+++ b/my file.yml\t' ya da C-tirnakli '"b/a\\"b.yml"' -> depo ici yol."""
    hedef = hedef.rstrip("\t")
    if hedef.startswith('"') and hedef.endswith('"'):
        hedef = hedef[1:-1].encode("latin-1", "backslashreplace").decode("unicode_escape") \
            .encode("latin-1").decode("utf-8", "surrogateescape")
    return hedef


def diff_ayristir(metin):
    """`git diff -U0` -> {yol: {"silinen": [...], "eklenen": [...], "son_satir": bool}}.

    Baslik satirlari (---/+++) yalnizca ilk @@'dan once okunur: icerigi "-- x"
    olan silinmis bir satir diff'te "--- x" gorunur ve baslik sanilmamalidir.
    """
    dosyalar, yol, hunk, onceki = {}, None, False, None
    for satir in metin.split("\n"):
        if satir.startswith("diff --git "):
            yol, hunk = None, False
        elif not hunk:
            if satir.startswith("+++ "):
                hedef = _yol_coz(satir[4:])
                # Silinen dosya (+++ /dev/null) --name-status'ta zaten FAIL.
                yol = None if hedef == "/dev/null" else hedef[2:] if hedef.startswith("b/") else hedef
                if yol is not None:
                    dosyalar.setdefault(yol, {"silinen": [], "eklenen": [], "son_satir": False,
                                              "eski_eksik": False})
            elif satir.startswith("@@") and yol is not None:
                hunk = True
        elif satir.startswith("@@"):
            pass
        elif satir.startswith("\\"):
            # "\ No newline at end of file" kendinden onceki satiri niteler: '-' eski
            # dosyada, '+' yeni dosyada satir sonu yok. Zaten eksikse gerileme degil.
            if onceki == "-":
                dosyalar[yol]["eski_eksik"] = True
            elif onceki == "+" and not dosyalar[yol]["eski_eksik"]:
                dosyalar[yol]["son_satir"] = True
        elif satir.startswith("-"):
            dosyalar[yol]["silinen"].append(satir[1:])
        elif satir.startswith("+"):
            dosyalar[yol]["eklenen"].append(satir[1:])
        onceki = satir[:1]
    return dosyalar


def satir_bulgulari(yol, silinen, eklenen, silinebilir):
    """Bir dosyanin -/+ satirlari -> [(kural, mesaj)]."""
    b = []
    eklenen_yorumlar = [y for y in map(satir_sonu_yorumu, eklenen) if y] + [
        e.strip().lstrip("#/").strip() for e in eklenen if YORUM_SATIRI.match(e)]
    # Aynen yeniden eklenen satir silinmemis, yer degistirmistir: icerik korunur.
    kalan = Counter(eklenen)
    soyulmus = Counter(e.strip() for e in eklenen)
    for s in silinen:
        kisa = s.strip()[:80]
        if kalan[s] > 0:
            kalan[s] -= 1
            soyulmus[s.strip()] -= 1
            continue
        if s.strip() and soyulmus[s.strip()] > 0 and not yol.endswith(".json"):
            soyulmus[s.strip()] -= 1
            b.append(("bosluk", "%s: yalnizca bosluk/satir sonu degismis: `%s`" % (yol, kisa)))
            continue
        if not s.strip():
            b.append(("bos_satir", "%s: bos satir silinmis" % yol))
            continue
        izinli = any(re.search(k, s) for k in silinebilir)
        # Yorum satiri yalnizca bir kalip onu ACIKCA hedefliyorsa silinebilir;
        # olaydaki `uses:` kalibi hicbir yorum satirina uymaz.
        # Metni aynen baska bir yorumun icinde duran yorum uzatilmistir, silinmemis.
        govde = s.strip().lstrip("#/").strip()
        if YORUM_SATIRI.match(s) and not izinli and govde and any(
                govde in e for e in eklenen_yorumlar):
            continue
        if YORUM_SATIRI.match(s) and not izinli:
            b.append(("yorum", "%s: yorum satiri silinmis: `%s`" % (yol, kisa)))
            continue
        if not izinli:
            b.append(("beklenmeyen", "%s: beklenmeyen silme: `%s`" % (yol, kisa)))
            continue
        yorum = (satir_sonu_yorumu(s) if yol.endswith((".yml", ".yaml", ".toml"))
                 and not YORUM_SATIRI.match(s) else None)
        # Yorum baska bir YORUMUN icinde kalabilir ("# v7.6.0; <eski yorum>"), ama
        # satirin kod kismindaki bir kelime onu kurtarmaz.
        if yorum and not any(yorum in e for e in eklenen_yorumlar):
            b.append(("yorum", "%s: satir sonu yorumu kaybolmus: `# %s`" % (yol, yorum[:60])))
    return b


def sozdizimi(yol, metin):
    try:
        if yol.endswith((".yml", ".yaml")):
            if P.yaml_yok():
                return None
            P._yukle(metin)
        elif yol.endswith(".json"):
            json.loads(metin)
        elif yol.endswith(".toml") and tomllib is not None:
            tomllib.loads(metin)
    except Exception as e:  # noqa: BLE001 -- her ayristirici kendi hatasini atar
        return "%s okunmuyor: %s" % (yol, str(e).splitlines()[0][:120])
    return None


def _tabandaki_politika_dosyalari(kok, taban):
    d = {}
    for yol in _git(kok, "ls-tree", "-r", "--name-only", taban).splitlines():
        if POLITIKA_YOLU.search(yol) and "node_modules/" not in yol:
            d[yol] = _git(kok, "show", "%s:%s" % (taban, yol))
    return d


def _agactaki_politika_dosyalari(kok):
    """Calisma agaci; ama taban tarafiyla ayni evren: izlenen ve ignore
    edilmeyen dosyalar. build/ altindaki bir kilit gerileme sayilmaz."""
    d = {}
    for yol in _git(kok, "ls-files", "--cached", "--others", "--exclude-standard").splitlines():
        p = Path(kok) / yol
        if POLITIKA_YOLU.search(yol) and "node_modules/" not in yol and p.is_file():
            d[yol] = p.read_text(encoding="utf-8", errors="replace")
    return d


def politika_gerilemesi(kok, taban):
    """-> [(kural, mesaj)]. Yeni FAIL ya da artan WARN gerilemedir."""
    if P.yaml_yok():
        return [("politika", "PyYAML yok: politika karsilastirilamadi")]
    once = P.depo_bulgulari(_tabandaki_politika_dosyalari(kok, taban))
    sonra = P.depo_bulgulari(_agactaki_politika_dosyalari(kok))
    b = []
    once_fail = {m for s, _, m in once if s == P.FAIL}
    for s, k, m in sonra:
        if s == P.FAIL and m not in once_fail:
            b.append(("politika", "yeni FAIL (%s): %s" % (k, m)))
    w_once = sum(1 for s, _, _ in once if s == P.WARN)
    w_sonra = sum(1 for s, _, _ in sonra if s == P.WARN)
    if w_sonra > w_once:
        b.append(("politika", "WARN sayisi artti: %d -> %d" % (w_once, w_sonra)))
    return b


def depo_denetle(kok, taban, dosya_kaliplari, silinebilir, bozuk_olabilir=()):
    """Bir calisma agaci -> dict(depo, durum, bulgular, dosyalar, eklenen, silinen)."""
    kok = Path(kok).resolve()
    if not (kok / ".git").exists():
        raise Bakilamadi("%s bir git calisma agaci degil" % kok)
    _git(kok, "rev-parse", "--verify", "--quiet", taban + "^{commit}")

    bulgular, dosya_listesi = [], []
    for satir in _git(kok, "diff", "--name-status", "-M", "--no-ext-diff", taban).splitlines():
        parca = satir.split("\t")
        tur, yol = parca[0], parca[-1]
        dosya_listesi.append(yol)
        if tur[0] in "DRTC":
            bulgular.append(("silme", "%s: %s (%s)" % (
                " -> ".join(parca[1:]), {"D": "silinmis", "R": "adi degismis", "T": "tipi degismis",
                                         "C": "kopyalanmis"}[tur[0]], tur)))
    for satir in _git(kok, "diff", "--summary", "--no-ext-diff", taban).splitlines():
        if satir.strip().startswith("mode change"):
            bulgular.append(("silme", "kip degismis: %s" % satir.strip()))
    yeniler = [y for y in _git(kok, "ls-files", "--others", "--exclude-standard").splitlines() if y]
    ic_ice = [y for y in yeniler if y.endswith("/") or (kok / y).is_dir()]
    if ic_ice:
        raise Bakilamadi("izlenmeyen ic ice git deposu: %s" % ", ".join(ic_ice[:3]))
    dosya_listesi += yeniler

    for yol in dosya_listesi:
        if dosya_kaliplari and not any(kaliba_uyar(yol, k) for k in dosya_kaliplari):
            bulgular.append(("dosya_disi", "%s: izin verilen dosyalarin disinda" % yol))

    fark = diff_ayristir(_git(kok, "diff", "-U0", "--text", "--no-color", "--no-ext-diff", "--no-renames", taban))
    eklenen = sum(len(f["eklenen"]) for f in fark.values())
    silinen = sum(len(f["silinen"]) for f in fark.values())
    for yol, f in sorted(fark.items()):
        bulgular.extend(satir_bulgulari(yol, f["silinen"], f["eklenen"], silinebilir))
        if f["son_satir"]:
            bulgular.append(("son_satir", "%s: dosya sonundaki satir sonu kaybolmus" % yol))
    for yol in yeniler:
        eklenen += len((kok / yol).read_text(encoding="utf-8", errors="replace").splitlines())

    for yol in sorted(set(dosya_listesi)):
        p = kok / yol
        if p.is_file() and not any(kaliba_uyar(yol, k) for k in bozuk_olabilir):
            hata = sozdizimi(yol, p.read_text(encoding="utf-8", errors="replace"))
            if hata:
                bulgular.append(("sozdizimi", hata))

    if any(POLITIKA_YOLU.search(y) for y in dosya_listesi):
        bulgular.extend(politika_gerilemesi(kok, taban))

    return {"depo": kok.name, "durum": "FAIL" if bulgular else "PASS",
            "degisti": bool(dosya_listesi), "dosyalar": sorted(set(dosya_listesi)),
            "eklenen": eklenen, "silinen": silinen,
            "bulgular": [{"kural": k, "mesaj": m} for k, m in bulgular]}


def denetle(kokler, taban, dosya_kaliplari=(), silinebilir=(), azami_depo=None, bozuk_olabilir=()):
    """-> (sonuclar, bakilamayan, patlama_mesaji)."""
    sonuclar, bakilamayan = [], {}
    for kok in kokler:
        try:
            sonuclar.append(depo_denetle(kok, taban, list(dosya_kaliplari), list(silinebilir),
                                         list(bozuk_olabilir)))
        except Bakilamadi as e:
            bakilamayan[Path(kok).name] = str(e)
    degisen = sum(1 for s in sonuclar if s["degisti"])
    patlama = None
    if azami_depo is not None and degisen > azami_depo:
        patlama = "%d depo degisiyor, esik %d: hicbiri gecmis sayilmaz" % (degisen, azami_depo)
        for s in sonuclar:
            if s["degisti"]:
                s["durum"] = "FAIL"
                s["bulgular"].append({"kural": "patlama", "mesaj": patlama})
    return sonuclar, bakilamayan, patlama


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kok", nargs="+", required=True, help="bir ya da daha cok calisma agaci")
    ap.add_argument("--taban", required=True, help="karsilastirilacak commit (ornek: HEAD, origin/main)")
    ap.add_argument("--dosya", action="append", default=[],
                    help="degismesine izin verilen yol kalibi (* dizin sinirini gecmez, ** gecer); tekrarlanabilir")
    ap.add_argument("--silinebilir", action="append", default=[],
                    help="silinmesine izin verilen satir regex'i; yoksa yalnizca ekleme kabul")
    ap.add_argument("--bozuk-olabilir", action="append", default=[],
                    help="bilerek okunmayan dosya kalibi (ornek: bozuk YAML fiksturu); sozdizimi atlanir")
    ap.add_argument("--azami-depo", type=int, help="bundan fazla depo degisiyorsa hepsi FAIL")
    ap.add_argument("--json", help="sonucu bu dosyaya da yaz")
    a = ap.parse_args(argv)

    sonuclar, bakilamayan, patlama = denetle(a.kok, a.taban, a.dosya, a.silinebilir, a.azami_depo,
                                               a.bozuk_olabilir)
    for s in sonuclar:
        ozet = ("%d dosya, +%d -%d" % (len(s["dosyalar"]), s["eklenen"], s["silinen"])
                if s["degisti"] else "degisiklik yok")
        print("%-4s  %-28s %s" % (s["durum"], s["depo"], ozet))
        for b in s["bulgular"]:
            print("        %-11s %s" % (b["kural"], b["mesaj"]))
    for ad, neden in sorted(bakilamayan.items()):
        print("????  %-28s BAKILAMADI: %s" % (ad, neden))
    gecen = sum(1 for s in sonuclar if s["durum"] == "PASS")
    print("\n%d depo: %d PASS, %d FAIL, %d bakilamadi%s" % (
        len(sonuclar) + len(bakilamayan), gecen, len(sonuclar) - gecen, len(bakilamayan),
        "" if not patlama else " -- PATLAMA: " + patlama))
    if a.json:
        Path(a.json).write_text(json.dumps({"sonuclar": sonuclar, "bakilamadi": bakilamayan,
                                            "patlama": patlama}, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
    if any(s["durum"] == "FAIL" for s in sonuclar):
        return 1
    return 2 if bakilamayan else 0


if __name__ == "__main__":
    sys.exit(main())

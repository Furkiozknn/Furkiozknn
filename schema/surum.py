#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bir surum etiketi atilmaya hazir mi -- ve hangi commit'e.

    python3 schema/surum.py godot-refcheck --pr 12     # PR birlestikten sonra
    python3 schema/surum.py mcp-vet                    # varsayilan dalin ucu

NEDEN VAR
---------
Hesaptaki en pahali el isi, geri alinmasi en zor olani: etiketi dogru
commit'e atmak. Etiket PyPI yayinini tetikler; PyPI'a giden bir surum
silinemez, ayni surum numarasi bir daha kullanilamaz.

Tuzak somut. Acik bir PR'in API'deki `merge_commit_sha` alani bos degildir:
GitHub'in arka planda kurdugu bir DENEME birlesmesinin SHA'sidir ve o commit
varsayilan dalda yoktur. 25 Eylul 2026'da godot-refcheck #12 acikken bu alan
77d154d... diyordu. PR birlestiginde ayni alan gercek birlesme commit'ini
gosterir. Birlesmeden once okunan deger bir etikete yazilirsa etiket, hicbir
dalda olmayan bir commit'i isaret eder.

Bu betik etiketi atmaz. Soyledigi tek sey: su SHA, su surum, su komut -- ya
da neden henuz degil. Etiketi atmak insanin karari olarak kalir.

KONTROLLER
----------
  1. (--pr ile) PR gercekten birlesmis mi, varsayilan dala mi birlesmis;
     SHA yalnizca o zaman `merge_commit_sha`'dan alinir
  2. SHA varsayilan dalin gecmisinde mi (compare API)
  3. surum o commit'teki pyproject.toml / Cargo.toml / package.json'dan
  4. CHANGELOG.md'de o surumun bolumu var mi
  5. etiket zaten var mi (varsa nereyi gosterdigi yazilir)
  6. o commit'teki kontrol kosulari bitti ve gecti mi
  7. (Python paketiyse) PyPI'da bu surum zaten var mi

Cikis kodu: 0 hazir, 1 hazir degil, 2 bakilamadi (ag / hiz siniri).
Bakilamayan bir sey "hazir" sayilmaz.
"""

import argparse
import base64
import importlib.util
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent


def _derle():
    spec = importlib.util.spec_from_file_location("surum_derle", KOK / "schema" / "derle.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = _derle()
API, OWNER = D.API, D.OWNER
GECEN = ("success", "skipped", "neutral")


class Bakilamadi(Exception):
    pass


def _gh(yol, get):
    """404 -> None; hiz siniri ve diger hatalar -> Bakilamadi."""
    try:
        return get(f"{API}/repos/{OWNER}/{yol}")
    except D.HizSiniri as e:
        raise Bakilamadi("GitHub hiz siniri (%s)" % e) from e
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise Bakilamadi("GitHub %d: %s" % (e.code, yol)) from e
    except OSError as e:
        raise Bakilamadi("ag hatasi: %s" % e) from e


def _dosya(ad, yol, sha, get):
    blob = _gh(f"{ad}/contents/{yol}?ref={sha}", get)
    if not blob or "content" not in blob:
        return None
    return base64.b64decode(blob["content"]).decode("utf-8", "replace")


def surumu_oku(dosyalar):
    """{ad: metin} -> (surum, kaynak, pypi_adi). Ilk bulunan manifest kazanir."""
    for ad, desen in (("pyproject.toml", r'(?m)^version\s*=\s*"([^"]+)"'),
                      ("Cargo.toml", r'(?m)^version\s*=\s*"([^"]+)"')):
        metin = dosyalar.get(ad)
        if metin:
            m = re.search(desen, metin)
            if m:
                pypi = None
                if ad == "pyproject.toml":
                    n = re.search(r'(?m)^name\s*=\s*"([^"]+)"', metin)
                    pypi = n.group(1) if n else None
                return m.group(1), ad, pypi
    metin = dosyalar.get("package.json")
    if metin:
        try:
            v = json.loads(metin).get("version")
        except ValueError:
            v = None
        if v:
            return v, "package.json", None
    return None, None, None


def changelog_bolumu_var(metin, surum):
    """'## [0.3.0]', '## 0.3.0 -- ...', '## v0.3.0' hepsi sayilir; '0.3.00' sayilmaz."""
    if not metin:
        return False
    desen = r"(?m)^##\s*\[?v?%s\]?(?=$|\s|\]|—|-|\()" % re.escape(surum)
    return re.search(desen, metin) is not None


def hazirlik(ad, pr=None, surum=None, get=D._get, pypi_surumleri=None):
    """-> dict(hazir, sha, surum, nedenler, bilgi). Ag hatasi Bakilamadi atar."""
    nedenler, bilgi = [], []
    depo = _gh(ad, get)
    if depo is None:
        return {"hazir": False, "sha": None, "surum": None,
                "nedenler": ["%s/%s bulunamadi" % (OWNER, ad)], "bilgi": []}
    dal = depo["default_branch"]

    if pr is not None:
        p = _gh(f"{ad}/pulls/{pr}", get)
        if p is None:
            return {"hazir": False, "sha": None, "surum": None,
                    "nedenler": ["PR #%d yok" % pr], "bilgi": []}
        if not p.get("merged"):
            return {"hazir": False, "sha": None, "surum": None, "bilgi": [],
                    "nedenler": ["PR #%d henuz birlesmemis. Su an gorunen merge_commit_sha "
                                 "(%s) bir DENEME birlesmesi; varsayilan dalda yok, etikete "
                                 "yazilmamali." % (pr, (p.get("merge_commit_sha") or "-")[:10])]}
        if (p.get("base") or {}).get("ref") != dal:
            nedenler.append("PR #%d %s dalina birlesmis, varsayilan dal %s"
                            % (pr, (p.get("base") or {}).get("ref"), dal))
        sha = p["merge_commit_sha"]
        bilgi.append("PR #%d birlesmis; birlesme commit'i %s" % (pr, sha[:12]))
    else:
        c = _gh(f"{ad}/commits/{dal}", get)
        sha = c["sha"]
        bilgi.append("%s dalinin ucu %s" % (dal, sha[:12]))

    kars = _gh(f"{ad}/compare/{sha}...{dal}", get)
    if not kars or kars.get("status") not in ("identical", "ahead"):
        nedenler.append("%s, %s dalinin gecmisinde degil (compare: %s)"
                        % (sha[:12], dal, (kars or {}).get("status")))

    dosyalar = {y: _dosya(ad, y, sha, get) for y in ("pyproject.toml", "Cargo.toml", "package.json")}
    v, kaynak, pypi_adi = surumu_oku(dosyalar)
    if v is None:
        return {"hazir": False, "sha": sha, "surum": None, "bilgi": bilgi,
                "nedenler": nedenler + ["o commit'te surum okunamadi (pyproject/Cargo/package.json)"]}
    bilgi.append("surum %s (%s)" % (v, kaynak))
    if surum and surum.lstrip("v") != v:
        nedenler.append("istenen surum %s ama o commit %s diyor" % (surum, v))

    degisiklikler = _dosya(ad, "CHANGELOG.md", sha, get)
    if degisiklikler is None:
        nedenler.append("o commit'te CHANGELOG.md yok")
    elif not changelog_bolumu_var(degisiklikler, v):
        nedenler.append("CHANGELOG.md'de %s bolumu yok" % v)

    etiket = "v" + v
    ref = _gh(f"{ad}/git/ref/tags/{etiket}", get)
    if ref is not None:
        hedef = (ref.get("object") or {}).get("sha", "")
        nedenler.append("%s etiketi zaten var (%s nesnesini gosteriyor)" % (etiket, hedef[:12]))

    kosular = _gh(f"{ad}/commits/{sha}/check-runs?per_page=100", get) or {}
    liste = kosular.get("check_runs") or []
    if not liste:
        nedenler.append("o commit'te hic kontrol kosusu yok (CI sonucu bilinmiyor)")
    else:
        bitmemis = [k["name"] for k in liste if k.get("status") != "completed"]
        dusen = [k["name"] for k in liste
                 if k.get("status") == "completed" and k.get("conclusion") not in GECEN]
        if bitmemis:
            nedenler.append("bitmemis kontrol: %s" % ", ".join(sorted(bitmemis)[:6]))
        if dusen:
            nedenler.append("gecmeyen kontrol: %s" % ", ".join(sorted(dusen)[:6]))
        if not bitmemis and not dusen:
            bilgi.append("%d kontrol kosusunun hepsi gecti" % len(liste))

    if pypi_adi:
        onceki = (pypi_surumleri or _pypi_surumleri)(pypi_adi)
        if onceki is None:
            bilgi.append("PyPI'da %s henuz yok (ilk yayin; Trusted Publisher tanimli olmali)" % pypi_adi)
        elif v in onceki:
            nedenler.append("PyPI'da %s %s zaten yayinlanmis; ayni surum bir daha yuklenemez"
                            % (pypi_adi, v))

    return {"hazir": not nedenler, "sha": sha, "surum": v, "nedenler": nedenler, "bilgi": bilgi,
            "etiket": etiket}


def _pypi_surumleri(ad):
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{ad}/json", timeout=20) as r:
            return set(json.load(r).get("releases") or {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise Bakilamadi("PyPI %d" % e.code) from e
    except OSError as e:
        raise Bakilamadi("PyPI'a ulasilamadi: %s" % e) from e


def komut(ad, sonuc):
    return ("git fetch origin\n"
            "git tag -a %s %s -m \"%s %s\"\n"
            "git push origin %s" % (sonuc["etiket"], sonuc["sha"], ad, sonuc["surum"], sonuc["etiket"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("depo")
    ap.add_argument("--pr", type=int, help="etiket bu PR'in birlesme commit'ine")
    ap.add_argument("--surum", help="beklenen surum (ornek 0.3.0); farkliysa hazir degil")
    a = ap.parse_args(argv)
    try:
        s = hazirlik(a.depo, a.pr, a.surum)
    except Bakilamadi as e:
        print("BAKILAMADI: %s -- hazir sayilmaz." % e)
        return 2
    for b in s["bilgi"]:
        print("  - " + b)
    if not s["hazir"]:
        print("HAZIR DEGIL:")
        for n in s["nedenler"]:
            print("  x " + n)
        return 1
    print("HAZIR. Etiketi atmak senin kararin; komut:\n")
    print(komut(a.depo, s))
    return 0


if __name__ == "__main__":
    sys.exit(main())

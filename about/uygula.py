#!/usr/bin/env python3
"""Depolarin GitHub "About" alanini about/about.json'dan uygular.

Neden ayri bir dosya: aciklama, depo sayfasindan cok daha fazla yerde
okunuyor -- sabitlenmis kartlar, arama sonuclari, baglanti onizlemeleri.
Hepsi ilk ~100 karakteri gosteriyor. 25 Eylul 2026'da 28 deponun
aciklamalari 130-330 karakterdi; yani ziyaretcinin gordugu, yarim
kalmis bir cumleydi. Bu dosya her birini tek, tam bir cumleye indiriyor.

Bu betik ayarlari degistirebilen tek yer: GitHub'in depo ayarlari API ile
yazilir ve bir oturum jetonu bunu yapamayabilir. `gh` ile giris yapmis bir
makinede calistirin.

    python3 about/uygula.py              # yalnizca farki gosterir, hicbir sey yazmaz
    python3 about/uygula.py --uygula     # gh repo edit ile yazar
    python3 about/uygula.py --kontrol    # agsiz: dosya kurallara uyuyor mu (CI)

Konular (topics) yalnizca eklenir, hic silinmez: bir kayitta `topics_add`
varsa ve o konu depoda yoksa eklenir. Ornek: asset-provenance-toolkit'in
project-meta.json'u mp4, ffmpeg ve video diyor ama GitHub'da yoklar.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
OWNER = "Furkiozknn"
AZAMI = 120


def yukle():
    return json.loads((KOK / "about.json").read_text(encoding="utf-8"))


def kontrol(veri):
    sorunlar = []
    for ad, a in veri.items():
        d = a.get("description", "")
        if not d:
            sorunlar.append("%s: aciklama bos" % ad)
        if len(d) > AZAMI:
            sorunlar.append("%s: aciklama %d karakter (en fazla %d)" % (ad, len(d), AZAMI))
        if "&" in d and ";" in d:
            sorunlar.append("%s: aciklamada HTML varligi kalmis" % ad)
        if not d.rstrip().endswith((".", ")")):
            sorunlar.append("%s: aciklama tam bir cumle olarak bitmiyor" % ad)
        for t in a.get("topics_add", []):
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,49}", t):
                sorunlar.append("%s: gecersiz konu %r" % (ad, t))
        h = a.get("homepage", "")
        if not h.startswith("https://"):
            sorunlar.append("%s: homepage https ile baslamiyor" % ad)
    return sorunlar


def simdiki(ad):
    cikti = subprocess.run(["gh", "api", "repos/%s/%s" % (OWNER, ad)],
                           capture_output=True, text=True)
    if cikti.returncode != 0:
        return None
    d = json.loads(cikti.stdout)
    return {"description": d.get("description") or "", "homepage": d.get("homepage") or "",
            "topics": d.get("topics") or []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uygula", action="store_true")
    ap.add_argument("--kontrol", action="store_true")
    args = ap.parse_args()
    veri = yukle()

    sorunlar = kontrol(veri)
    if args.kontrol or sorunlar:
        for s in sorunlar:
            print("HATA  " + s)
        if not sorunlar:
            print("about.json kurallara uyuyor (%d depo)." % len(veri))
        return 1 if sorunlar else 0

    if not shutil.which("gh"):
        print("gh bulunamadi: https://cli.github.com, sonra `gh auth login`.")
        return 1

    degisen = 0
    for ad, yeni in veri.items():
        eski = simdiki(ad)
        if eski is None:
            print("ATLANDI  %s (okunamadi)" % ad)
            continue
        fark = {k: v for k, v in yeni.items()
                if k in ("description", "homepage") and eski.get(k) != v}
        eksik = [t for t in yeni.get("topics_add", []) if t not in eski["topics"]]
        if eksik:
            fark["topics_add"] = eksik
        if not fark:
            continue
        degisen += 1
        print("\n%s" % ad)
        for k, v in fark.items():
            print("  %s\n    - %s\n    + %s" % (k, eski.get(k), v))
        if args.uygula:
            komut = ["gh", "repo", "edit", "%s/%s" % (OWNER, ad)]
            if "description" in fark:
                komut += ["--description", fark["description"]]
            if "homepage" in fark:
                komut += ["--homepage", fark["homepage"]]
            for t in fark.get("topics_add", []):
                komut += ["--add-topic", t]
            subprocess.run(komut, check=True)
    print("\n%d depo %s." % (degisen, "guncellendi" if args.uygula else
                              "degisecek (yazmak icin --uygula)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

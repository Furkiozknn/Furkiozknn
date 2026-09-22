#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Otomatik tazelemenin onundeki son kapi: bu degisiklik deger kaybettiriyor mu?

`dogrula.py` dosyanin *seklini* ve iddialarinin dogrulugunu denetler. Ama
sekil olarak kusursuz bir dosya yine de yanlis olabilir: uretici bir dali
kaybederse alan `null` olur, sema bundan sikayet etmez (cogu alan
nullable'dir) ve gercek bir bilgi sessizce silinir.

Bu tam olarak yasandi: `package.json`'daki "private" bayragi olcut
yapilinca masal'in 1.0.0 surumu metadata'dan dustu ve dosya butun
kapilardan gecti. Insan gozu yakaladi. Bu dosya o gozun yerine geciyor.

Kural basit ve tek yonlu: **dolu bir degerin bosalmasi supheli, bos bir
degerin dolmasi degil.** Bir alan gercekten kayboldugunda (depodan LICENSE
silindi, hero gorsel kaldirildi) kapi kasitli olarak kapanir ve degisiklik
elle onaylanir -- yilda bir iki kez olan bir sey icin dogru takas.

    python3 schema/koruma.py eski.json yeni.json
    -> kayip varsa satir satir yazar ve 1 ile cikar
"""

import json
import sys

# Kaybolmasi supheli olan alanlar. Hepsi ya bir insanin yazdigi ya da
# depodan olculen gercek bilgi; hicbiri "yeniden uretilince degisir"
# cinsinden degil.
KRITIK = (
    "version",
    "summary",
    "license",
    "tests",
    "primary_language",
    "media.hero",
    "key_features",
    "topics",
    "platform",
    "technologies",
    "social.headline",
    "docs.readme",
    "docs.license_file",
)


def _oku(veri, yol):
    for parca in yol.split("."):
        if not isinstance(veri, dict):
            return None
        veri = veri.get(parca)
    return veri


def kayip_alanlar(eski, yeni):
    """Doluyken bosalan kritik alanlar. Bos liste donerse degisiklik guvenli."""
    kayiplar = []
    for yol in KRITIK:
        a, b = _oku(eski, yol), _oku(yeni, yol)
        if not a:
            continue                      # zaten bostu, dolmasi sorun degil
        if b:
            continue
        kayiplar.append("%s: %r -> %r" % (yol, a, b))
    return kayiplar


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[-2].strip())
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        eski = json.load(f)
    with open(sys.argv[2], encoding="utf-8") as f:
        yeni = json.load(f)
    kayiplar = kayip_alanlar(eski, yeni)
    for k in kayiplar:
        print("KAYIP " + k)
    return 1 if kayiplar else 0


if __name__ == "__main__":
    raise SystemExit(main())

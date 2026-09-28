#!/usr/bin/env python3
"""Depodaki Markdown dosyalarinin yerel linklerini ve baslik capalarini
lychee ile denetler; lychee'nin kendi basina "yesil" dedigi iki durumu
kirmiziya cevirir.

Neden bir sarmalayici:
  - lychee hic dosya eslesmediginde "0 Total" yazip 0 doner (olculdu).
    Burada kontrol edilen link sayisi --en-az'in altindaysa FAIL.
  - --offline kipinde uzak linkler sessizce "excluded" sayilir; ozet
    satiri bunu ayrica yazar ki "hepsi OK" diye okunmasin.
  - Varsayilan olarak baslik capalari (#bolum) denetlenmez;
    --include-fragments hep acik.

Kullanim:
  python3 .github/baglanti/kontrol.py --lychee ./lychee [--en-az 10] [dosya.md ...]
Dosya verilmezse `git ls-files '*.md'` kullanilir.
Cikis: 0 PASS, 1 FAIL (kirik link, eksik sayim, okunamayan rapor), 2 kullanim.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lychee", required=True)
    p.add_argument("--en-az", type=int, default=1,
                   help="kontrol edilen yerel link sayisi bunun altindaysa FAIL")
    p.add_argument("dosyalar", nargs="*")
    a = p.parse_args()
    if a.en_az < 1:
        p.error("--en-az en az 1 olmali")

    dosyalar = a.dosyalar or subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"], check=True,
        capture_output=True, text=True).stdout.split("\0")
    dosyalar = [d for d in dosyalar if d]
    if not dosyalar:
        print("FAIL: denetlenecek Markdown dosyasi yok")
        return 1

    fd, rapor = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        r = subprocess.run(
            [a.lychee, "--no-progress", "--offline", "--include-fragments",
             "--format", "json", "--output", rapor, "--", *dosyalar],
            capture_output=True, text=True, timeout=600)
        try:
            with open(rapor, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError) as e:
            print(f"FAIL: lychee raporu okunamadi ({e}); cikis {r.returncode}")
            print(r.stderr[-2000:])
            return 1
    finally:
        os.unlink(rapor)

    basarili = d.get("successful", 0)
    hata, haric = d.get("errors", 0), d.get("excludes", 0)
    for kaynak, hatalar in sorted((d.get("error_map") or {}).items()):
        for h in hatalar:
            durum = h.get("status")
            metin = durum.get("text") if isinstance(durum, dict) else durum
            print(f"KIRIK  {kaynak}: {h.get('url')}  ({metin})")

    print(f"{len(dosyalar)} dosya; yerel link/capa: {basarili} OK, {hata} kirik; "
          f"uzak link: {haric} (cevrimdisi kipte denetlenmez)")
    if r.returncode not in (0, 2):
        print(f"FAIL: lychee beklenmeyen cikis {r.returncode}")
        print(r.stderr[-2000:])
        return 1
    if hata or r.returncode == 2:
        print("FAIL: kirik yerel link ya da capa")
        return 1
    if basarili < a.en_az:
        print(f"FAIL: yalnizca {basarili} yerel link denetlendi (< --en-az {a.en_az})")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

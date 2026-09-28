#!/usr/bin/env python3
"""Skill kilidi: .claude/skills altindaki her dosyanin sha256'si kilit.json'da.

    python3 .claude/skills/kilit.py --kontrol   # CI / oturum basi: sapma varsa 1
    python3 .claude/skills/kilit.py --uret      # yalnizca bilincli guncellemeden sonra

Bir skill "pinli" demek yalnizca kaynak commit'ini yazmak degil: kurulu
dosyalarin o commit'teki haliyle (ve PROVENANCE.md'de listelenen proje
degisiklikleriyle) ayni kaldigini da gostermek. Kilit, sessiz bir
duzenlemeyi, eklenen bir betigi ya da silinen bir referansi yakalar.
Guncelleme politikasi: yeni surumun farki incelenmeden --uret calistirilmaz.
"""
import hashlib
import json
import os
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
KILIT = os.path.join(KOK, "kilit.json")
HARIC = {"kilit.json", "__pycache__"}


def dosyalar():
    out = {}
    for d, alt, adlar in os.walk(KOK):
        alt[:] = sorted(a for a in alt if a not in HARIC)
        for ad in sorted(adlar):
            if ad in HARIC or ad.endswith(".pyc"):
                continue
            yol = os.path.join(d, ad)
            rel = os.path.relpath(yol, KOK).replace(os.sep, "/")
            with open(yol, "rb") as f:
                out[rel] = hashlib.sha256(f.read()).hexdigest()
    return out


def main(argv):
    if argv == ["--uret"]:
        with open(KILIT, "w", encoding="utf-8") as f:
            json.dump(dosyalar(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"kilit yazildi: {len(dosyalar())} dosya")
        return 0
    if argv != ["--kontrol"]:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(KILIT, encoding="utf-8") as f:
            beklenen = json.load(f)
    except (OSError, ValueError) as e:
        print(f"KILIT: kilit.json okunamadi: {e}", file=sys.stderr)
        return 1
    simdi = dosyalar()
    sorun = []
    for rel in sorted(set(beklenen) | set(simdi)):
        if rel not in simdi:
            sorun.append(f"eksik: {rel}")
        elif rel not in beklenen:
            sorun.append(f"kilitte yok (yeni dosya): {rel}")
        elif simdi[rel] != beklenen[rel]:
            sorun.append(f"degisti: {rel}")
    for s in sorun:
        print(f"KILIT: {s}", file=sys.stderr)
    if sorun:
        return 1
    print(f"KILIT: {len(simdi)} dosya kilitle ayni")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

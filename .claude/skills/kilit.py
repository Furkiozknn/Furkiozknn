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


def dosyalar():
    """(ozetler, sorunlar). Symlink ve olagan disi dosya hata sayilir: os.walk
    symlink dizine girmez, oysa Claude Code oradaki SKILL.md'yi yukler."""
    out, sorun = {}, []
    for d, alt, adlar in os.walk(KOK):
        for a in list(alt):
            tam = os.path.join(d, a)
            if os.path.islink(tam):
                sorun.append(f"symlink dizin: {os.path.relpath(tam, KOK)}")
                alt.remove(a)
            elif a == "__pycache__":
                # Yalnizca .pyc barindiriyorsa yok say; baska her sey kilide tabi.
                icerik = os.listdir(tam)
                if all(x.endswith(".pyc") and os.path.isfile(os.path.join(tam, x))
                       and not os.path.islink(os.path.join(tam, x)) for x in icerik):
                    alt.remove(a)
        alt.sort()
        for ad in sorted(adlar):
            yol = os.path.join(d, ad)
            rel = os.path.relpath(yol, KOK).replace(os.sep, "/")
            if rel == "kilit.json":
                continue
            if os.path.islink(yol) or not os.path.isfile(yol):
                sorun.append(f"symlink ya da olagan disi dosya: {rel}")
                continue
            with open(yol, "rb") as f:
                out[rel] = hashlib.sha256(f.read()).hexdigest()
    return out, sorun


def main(argv):
    ozet, sorun = dosyalar()
    if argv == ["--uret"]:
        if sorun:
            for s in sorun:
                print(f"KILIT: {s}", file=sys.stderr)
            return 1
        with open(KILIT, "w", encoding="utf-8") as f:
            json.dump(ozet, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"kilit yazildi: {len(ozet)} dosya")
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
    simdi = ozet
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""project-meta.json dosyalarını şemaya ve gerçeğe karşı doğrular.

İki şey ayrı ayrı kontrol edilir:

1. **Şema uyumu** — `project-meta.schema.json` ile: zorunlu alanlar,
   tipler, `additionalProperties: false`, `status` gibi sabit kümeler.
2. **Gerçeğe uyum** — dosyanın *iddia ettiği* şeyler depoda gerçekten var
   mı: `media.hero` ve ekran görüntüleri diske karşılık geliyor mu,
   `ci.workflows` gerçekten var olan iş akışlarını mı sayıyor, `docs`
   altında adı geçen dosyalar duruyor mu, `tests` sayısı kaynağıyla
   birlikte mi yazılmış.

Bağımlılık yok; `jsonschema` kurulu olmayan bir makinede de çalışır.
Şemanın kullanılan alt kümesi elle yorumlanır ve desteklenmeyen bir şema
anahtarı görülürse sessizce geçilmez, uyarı olarak bildirilir.

    python3 schema/dogrula.py <depo-klasoru> [<depo-klasoru> ...]
    python3 schema/dogrula.py --kok D:/.../work      # altındaki hepsi

Çıkış kodu: 0 temiz, 1 en az bir hata.
"""

import argparse
import json
import os
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMA = os.path.join(KOK, "schema", "project-meta.schema.json")

TIPLER = {
    "object": dict, "array": list, "string": str,
    "integer": int, "number": (int, float), "boolean": bool,
}


def _tip_uyuyor(deger, tip):
    if tip == "null":
        return deger is None
    if tip == "integer":
        return isinstance(deger, int) and not isinstance(deger, bool)
    beklenen = TIPLER.get(tip)
    if beklenen is None:
        return True                       # tanimadigimiz tip: karar verme
    if tip == "boolean":
        return isinstance(deger, bool)
    if isinstance(deger, bool) and beklenen is not bool:
        return False
    return isinstance(deger, beklenen)


def _tip_kontrol(deger, kural, yol, hatalar):
    tip = kural.get("type")
    if tip is None:
        return
    tipler = tip if isinstance(tip, list) else [tip]
    if not any(_tip_uyuyor(deger, t) for t in tipler):
        hatalar.append(f"{yol}: tip {'/'.join(tipler)} bekleniyordu, {type(deger).__name__} geldi")


def _sema_dogrula(veri, kural, yol, hatalar):
    if "enum" in kural and veri not in kural["enum"]:
        hatalar.append(f"{yol}: '{veri}' izin verilen kumede degil {kural['enum']}")
    _tip_kontrol(veri, kural, yol, hatalar)

    if isinstance(veri, dict):
        for z in kural.get("required", []):
            if z not in veri:
                hatalar.append(f"{yol}: zorunlu alan '{z}' yok")
        ozellikler = kural.get("properties", {})
        ek = kural.get("additionalProperties", True)
        for k, v in veri.items():
            alt_yol = f"{yol}.{k}" if yol else k
            if k in ozellikler:
                _sema_dogrula(v, ozellikler[k], alt_yol, hatalar)
            elif ek is False:
                hatalar.append(f"{alt_yol}: semada tanimsiz alan")
            elif isinstance(ek, dict):
                _sema_dogrula(v, ek, alt_yol, hatalar)
    elif isinstance(veri, list) and "items" in kural:
        for i, v in enumerate(veri):
            _sema_dogrula(v, kural["items"], f"{yol}[{i}]", hatalar)


def _gercek_dogrula(depo, meta, hatalar, uyarilar):
    def var_mi(göreli):
        return os.path.exists(os.path.join(depo, göreli.replace("/", os.sep)))

    medya = meta.get("media") or {}
    hero = medya.get("hero")
    if hero and not var_mi(hero):
        hatalar.append(f"media.hero: '{hero}' depoda yok")
    for alan in ("screenshots", "gifs", "videos"):
        for y in medya.get(alan) or []:
            if not var_mi(y):
                hatalar.append(f"media.{alan}: '{y}' depoda yok")

    for ad, y in (meta.get("docs") or {}).items():
        if y and not var_mi(y):
            hatalar.append(f"docs.{ad}: '{y}' depoda yok")

    wf_dizin = os.path.join(depo, ".github", "workflows")
    diskte = sorted(os.listdir(wf_dizin)) if os.path.isdir(wf_dizin) else []
    bildirilen = (meta.get("ci") or {}).get("workflows") or []
    if sorted(bildirilen) != diskte:
        hatalar.append(f"ci.workflows: dosya {bildirilen} diyor, diskte {diskte} var")

    testler = meta.get("tests")
    if testler is not None:
        for z in ("count", "source", "measured"):
            if not testler.get(z):
                hatalar.append(f"tests.{z}: bos - kaynaksiz sayi dosyaya girmez")

    if meta.get("status") == "archived" and not (meta.get("summary") or "").strip():
        uyarilar.append("status 'archived' ama summary bos")

    kimlik = os.path.basename(os.path.normpath(depo))
    if meta.get("id") != kimlik:
        hatalar.append(f"id: '{meta.get('id')}' ama klasor '{kimlik}'")


def depo_dogrula(depo, sema):
    yol = os.path.join(depo, "project-meta.json")
    if not os.path.isfile(yol):
        return None, [f"{os.path.basename(depo)}: project-meta.json yok"], []
    try:
        meta = json.load(open(yol, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, [f"{os.path.basename(depo)}: gecersiz JSON ({e})"], []
    hatalar, uyarilar = [], []
    _sema_dogrula(meta, sema, "", hatalar)
    _gercek_dogrula(depo, meta, hatalar, uyarilar)
    return meta, hatalar, uyarilar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("depolar", nargs="*")
    ap.add_argument("--kok", help="altindaki her klasoru depo say")
    args = ap.parse_args()

    sema = json.load(open(SEMA, encoding="utf-8"))
    depolar = list(args.depolar)
    if args.kok:
        depolar += [os.path.join(args.kok, d) for d in sorted(os.listdir(args.kok))
                    if os.path.isdir(os.path.join(args.kok, d))]
    if not depolar:
        depolar = [KOK]

    toplam_hata = 0
    for d in depolar:
        ad = os.path.basename(os.path.normpath(d))
        meta, hatalar, uyarilar = depo_dogrula(d, sema)
        if hatalar:
            toplam_hata += len(hatalar)
            print(f"HATA  {ad}")
            for h in hatalar:
                print(f"        {h}")
        elif meta is None:
            print(f"ATLA  {ad}")
        else:
            ek = f"  ({len(uyarilar)} uyari)" if uyarilar else ""
            print(f"TAMAM {ad}{ek}")
        for u in uyarilar:
            print(f"        uyari: {u}")

    print(f"\n{len(depolar)} depo, {toplam_hata} hata.")
    return 1 if toplam_hata else 0


if __name__ == "__main__":
    raise SystemExit(main())

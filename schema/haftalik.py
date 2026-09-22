#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bu hafta hangi projede ne değişti — ve bunun üzerine ne söylenebilir.

Her deponun `project-meta.json` dosyasını ve GitHub API'sini okuyup verilen
pencerede gerçekten ne olduğunu çıkarır: kaç commit, hangi türden, yeni
release var mı, hangi dosyalar değişti. Ardından her proje için bir gönderi
taslağı üretir.

Taslaklardaki her cümle ya `project-meta.json` içindeki yazılı bir alandan
ya da bu penceredeki gerçek git/release verisinden gelir. Sıfat uydurulmaz,
sayı uydurulmaz: veri yoksa cümle de yoktur.

    python3 schema/haftalik.py              # son 7 gün
    python3 schema/haftalik.py --gun 14
    python3 schema/haftalik.py --json       # makine-okunur çıktı
    GITHUB_TOKEN=... python3 schema/haftalik.py

Yalnızca standart kütüphane kullanılır.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNER = "Furkiozknn"
API = "https://api.github.com"
KOK = Path(__file__).resolve().parent.parent

# Conventional commit türleri -> insan dili
TUR = {
    "feat": "yeni özellik",
    "fix": "düzeltme",
    "docs": "belge",
    "ci": "CI",
    "perf": "başarım",
    "refactor": "yeniden düzenleme",
    "test": "test",
    "chore": "bakım",
    "meta": "metadata",
    "build": "derleme",
    "style": "biçim",
}
BASLIK = re.compile(r"^(?P<tur>[a-z]+)(\([^)]*\))?!?:\s")


def _get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "haftalik-ozet",
    })
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _belki(url):
    try:
        return _get(url)
    except urllib.error.HTTPError as e:
        if e.code in (404, 409):      # 409 = bos depo
            return None
        raise


def _depolar():
    out, sayfa = [], 1
    while True:
        parca = _get(f"{API}/users/{OWNER}/repos?per_page=100&page={sayfa}&sort=pushed")
        if not parca:
            break
        out.extend(parca)
        if len(parca) < 100:
            break
        sayfa += 1
    return [r for r in out if not r.get("fork")]


def _meta(ad, dal):
    blob = _belki(f"{API}/repos/{OWNER}/{ad}/contents/project-meta.json?ref={dal}")
    if blob is None:
        return None
    return json.loads(base64.b64decode(blob["content"]).decode("utf-8"))


def _commitler(ad, dal, since):
    veri = _belki(f"{API}/repos/{OWNER}/{ad}/commits?sha={dal}&since={since}&per_page=100")
    if not veri:
        return []
    out = []
    for c in veri:
        if c.get("parents") and len(c["parents"]) > 1:
            continue                                  # merge commit sayilmaz
        basl = (c["commit"]["message"] or "").splitlines()[0].strip()
        m = BASLIK.match(basl)
        out.append({"sha": c["sha"][:7], "baslik": basl,
                    "tur": m.group("tur") if m else None,
                    "tarih": c["commit"]["committer"]["date"][:10]})
    return out


def _releaseler(ad, esik):
    veri = _belki(f"{API}/repos/{OWNER}/{ad}/releases?per_page=20")
    if not veri:
        return []
    return [{"tag": r["tag_name"], "ad": r["name"], "url": r["html_url"],
             "tarih": (r["published_at"] or "")[:10]}
            for r in veri
            if r.get("published_at") and r["published_at"] >= esik and not r["draft"]]


def _tur_ozeti(commitler):
    sayac = Counter(c["tur"] for c in commitler if c["tur"])
    etiketsiz = sum(1 for c in commitler if not c["tur"])
    parcalar = [f"{n} {TUR.get(t, t)}" for t, n in sayac.most_common()]
    if etiketsiz:
        parcalar.append(f"{etiketsiz} diğer")
    return parcalar


def _taslak(meta, commitler, releaseler):
    """Gönderi taslağı. Her cümlenin arkasında bir veri olmalı."""
    ad = meta["id"]
    satirlar = []

    yeni = releaseler[0] if releaseler else None
    if yeni:
        satirlar.append(f"{ad} {yeni['tag']} çıktı.")
    else:
        surum = meta.get("version")
        satirlar.append(f"{ad}{' v' + surum if surum else ''} —")

    basli = (meta.get("social") or {}).get("headline")
    if basli:
        satirlar.append(basli)

    ozet = _tur_ozeti(commitler)
    if ozet:
        satirlar.append(f"Bu pencerede {len(commitler)} commit: " + ", ".join(ozet) + ".")

    testler = meta.get("tests")
    if testler and testler.get("count"):
        satirlar.append(f"{testler['count']} test geçiyor.")

    metin = " ".join(s.strip() for s in satirlar if s).strip()
    link = (meta.get("social") or {}).get("primary_link") or meta["repository"]
    etiketler = " ".join("#" + h for h in (meta.get("social") or {}).get("hashtags", [])[:4])

    kisa = f"{metin}\n{link}"
    if len(kisa) + len(etiketler) + 1 <= 280:
        kisa = f"{kisa}\n{etiketler}"
    return {"kisa": kisa, "uzun": f"{metin}\n\n{link}\n\n{etiketler}".strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    esik_dt = datetime.now(timezone.utc) - timedelta(days=args.gun)
    esik = esik_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    hareketli, sessiz, metasiz = [], [], []
    for r in _depolar():
        ad, dal = r["name"], r["default_branch"]
        if r["pushed_at"] < esik and not r["archived"]:
            sessiz.append(ad)
            continue
        if r["archived"]:
            continue
        meta = _meta(ad, dal)
        if meta is None:
            metasiz.append(ad)
            continue
        commitler = _commitler(ad, dal, esik)
        releaseler = _releaseler(ad, esik)
        if not commitler and not releaseler:
            sessiz.append(ad)
            continue
        hareketli.append({
            "id": ad,
            "repository": meta["repository"],
            "version": meta.get("version"),
            "commit_sayisi": len(commitler),
            "tur_ozeti": _tur_ozeti(commitler),
            "commitler": commitler,
            "releaseler": releaseler,
            "taslak": _taslak(meta, commitler, releaseler),
        })

    hareketli.sort(key=lambda p: (-len(p["releaseler"]), -p["commit_sayisi"]))
    belge = {
        "uretildi": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pencere_gun": args.gun,
        "pencere_baslangic": esik,
        "hareketli": hareketli,
        "sessiz": sorted(sessiz),
        "project_meta_eksik": sorted(metasiz),
    }

    (KOK / "schema" / "hafta.json").write_text(
        json.dumps(belge, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    if args.json:
        json.dump(belge, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    print(f"# Son {args.gun} gün — {len(hareketli)} projede hareket var\n")
    for p in hareketli:
        print(f"## {p['id']}" + (f" (v{p['version']})" if p["version"] else ""))
        for rel in p["releaseler"]:
            print(f"- release: **{rel['tag']}** ({rel['tarih']}) {rel['url']}")
        if p["commit_sayisi"]:
            print(f"- {p['commit_sayisi']} commit: " + ", ".join(p["tur_ozeti"]))
            for c in p["commitler"][:5]:
                print(f"    {c['tarih']}  {c['sha']}  {c['baslik'][:88]}")
            if p["commit_sayisi"] > 5:
                print(f"    ... +{p['commit_sayisi'] - 5}")
        print("\n  taslak (kısa):")
        for satir in p["taslak"]["kisa"].splitlines():
            print(f"    {satir}")
        print()
    if belge["sessiz"]:
        print("Bu pencerede hareket yok: " + ", ".join(belge["sessiz"]))
    if belge["project_meta_eksik"]:
        print("project-meta.json eksik: " + ", ".join(belge["project_meta_eksik"]))
    print("\n(schema/hafta.json yazıldı — taslaklar gönderilmeden önce okunmalı.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

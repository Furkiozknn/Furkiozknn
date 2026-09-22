#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Her deponun kökündeki `project-meta.json` dosyasını üretir.

İki girdi var ve ikisi de bu depoda:

- **Mekanik alanlar** klonun kendisinden (sürüm, iş akışları, README'nin
  gösterdiği görseller, hangi belge dosyaları var) ve GitHub API'sinden
  (açıklama, konular, lisans, dil, ana sayfa) okunur.
- **Yazılı alanlar** `schema/meta-source.json` içinde durur: kategori,
  platform, teknolojiler, öne çıkan özellikler, test sayısı ve o sayıyı
  yazdıran koşu, sosyal başlık.

Hiçbir alan tahminle doldurulmaz: bilinmeyen değer `null` kalır.

Önceden bu betik ve yazılı kaynak yalnızca tek bir makinede duruyordu;
yani metadata katmanının yarısı o diskle birlikte kaybolabilirdi. Artık
ikisi de depoda: taze bir klon ve bir jeton, katmanı sıfırdan yeniden
üretmeye yeter.

    python3 schema/uret.py --kok /klonlarin/durdugu/klasor
    python3 schema/uret.py --kok ... --yaz-olmayan   # eksik kaydı uyarır

Yeni bir depo açıldığında `schema/meta-source.json` içine de bir kayıt
gerekir; yoksa o depo atlanır ve sonunda adıyla bildirilir.

Bağımlılık yok.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

OWNER = "Furkiozknn"
API = "https://api.github.com"
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "schema", "meta-source.json")

GORSEL = re.compile(r'!\[[^\]]*\]\(([^)\s]+)\)|<img[^>]*src="([^"]+)"')


def _get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "project-meta-uret",
    })
    jeton = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if jeton:
        req.add_header("Authorization", f"Bearer {jeton}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


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
    return {r["name"]: r for r in out}


def surum(d):
    p = os.path.join(d, "pyproject.toml")
    if os.path.isfile(p):
        for satir in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r'\s*version\s*=\s*"([^"]+)"', satir)
            if m:
                return m.group(1)
    # Claude Code eklentisi: bildirilen surum burada durur. package.json'dan
    # once bakilir, cunku bir eklenti deposundaki package.json cogu zaman
    # yalnizca modul turunu sabitlemek icin vardir ve "0.0.0" tasir.
    p = os.path.join(d, ".claude-plugin", "plugin.json")
    if os.path.isfile(p):
        try:
            v = json.load(open(p, encoding="utf-8")).get("version")
            if v and v != "0.0.0":
                return v
        except Exception:
            pass
    p = os.path.join(d, "package.json")
    if os.path.isfile(p):
        try:
            v = json.load(open(p, encoding="utf-8")).get("version")
            # "private": true tek basina bir sey soylemiyor -- bir uygulama
            # kutuphane olmadigi icin private olur ama surumunu yine de
            # bildirir (masal 1.0.0). Ayirt edici olan "0.0.0" yer tutucusu.
            if v and v != "0.0.0":
                return v
        except Exception:
            pass
    # Manifest sürüm bildirmiyorsa deponun kendi en yeni etiketi.
    try:
        t = subprocess.run(["git", "-C", d, "describe", "--tags", "--abbrev=0"],
                           capture_output=True, text=True, timeout=30)
        etiket = t.stdout.strip()
        if t.returncode == 0 and etiket:
            return etiket.lstrip("v")
    except Exception:
        pass
    return None


def medya(d):
    """Yalnızca README'nin gerçekten gösterdiği yerel görseller."""
    yol = os.path.join(d, "README.md")
    hero, kareler, gifler = None, [], []
    if os.path.isfile(yol):
        metin = open(yol, encoding="utf-8", errors="replace").read()
        for m in GORSEL.finditer(metin):
            u = (m.group(1) or m.group(2) or "").strip()
            if not u or u.startswith(("http://", "https://", "data:")):
                continue
            if hero is None:
                hero = u
            if u.lower().endswith(".gif"):
                gifler.append(u)
            elif u.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                kareler.append(u)
    return {"hero": hero,
            "screenshots": list(dict.fromkeys(kareler)),
            "gifs": list(dict.fromkeys(gifler)),
            "videos": []}


def ilk(d, *adlar):
    for a in adlar:
        if os.path.isfile(os.path.join(d, a)):
            return a
    return None


def uret(ad, s, d, r, bugun):
    wf_dizin = os.path.join(d, ".github", "workflows")
    akislar = sorted(os.listdir(wf_dizin)) if os.path.isdir(wf_dizin) else []
    lisans = (r.get("license") or {}).get("spdx_id")
    if lisans in ("NOASSERTION", "", None):
        lisans = None
    ana_sayfa = r.get("homepage") or None
    return {
        "schema_version": "1.0.0",
        "id": ad,
        "owner": OWNER,
        "repository": f"https://github.com/{OWNER}/{ad}",
        "homepage": ana_sayfa,
        "releases": f"https://github.com/{OWNER}/{ad}/releases",
        "status": "archived" if r.get("archived") else s["status"],
        "category": s["category"],
        "platform": s["platform"],
        "primary_language": r.get("language"),
        "technologies": s["technologies"],
        "version": s.get("version") or surum(d),
        "license": lisans,
        "topics": sorted(r.get("topics") or []),
        "summary": r.get("description"),
        "key_features": s["key_features"],
        "media": medya(d),
        "tests": s.get("tests"),
        "ci": {
            "workflows": akislar,
            "badge": (f"https://github.com/{OWNER}/{ad}/actions/workflows/{akislar[0]}/badge.svg"
                      if akislar else None),
        },
        "docs": {
            "readme": ilk(d, "README.md"),
            "changelog": ilk(d, "CHANGELOG.md"),
            "version_history": ilk(d, "SURUM-GECMISI.md"),
            "roadmap": ilk(d, "ROADMAP.md", "YOL-HARITASI.md"),
            "security": ilk(d, "SECURITY.md"),
            "contributing": ilk(d, "CONTRIBUTING.md", "KATKIDA-BULUNMA.md"),
            "license_file": ilk(d, "LICENSE", "LICENSE.md"),
        },
        "social": {
            "headline": s["social"]["headline"],
            "hashtags": s["social"]["hashtags"],
            "primary_link": ana_sayfa or f"https://github.com/{OWNER}/{ad}",
        },
        "provenance": {
            "generated_at": bugun,
            "generator": "schema/uret.py",
            "rule": "mechanical fields read from the repository and the GitHub API; "
                    "editorial fields hand-written and reviewed; "
                    "no field is generated from a guess",
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", required=True, help="klonlarin durdugu klasor")
    args = ap.parse_args()

    kaynak = json.load(open(KAYNAK, encoding="utf-8"))
    depolar = _depolar()
    bugun = datetime.date.today().isoformat()

    yazildi, klonsuz = [], []
    for ad, s in kaynak.items():
        d = os.path.join(args.kok, ad)
        if not os.path.isdir(d):
            klonsuz.append(ad)
            continue
        meta = uret(ad, s, d, depolar.get(ad, {}), bugun)
        with open(os.path.join(d, "project-meta.json"), "w",
                  encoding="utf-8", newline="\n") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            f.write("\n")
        yazildi.append(ad)

    kayitsiz = sorted(set(depolar) - set(kaynak) - {"kor"})
    print(f"{len(yazildi)} dosya yazildi.")
    if klonsuz:
        print("klon bulunamadi: " + ", ".join(sorted(klonsuz)))
    if kayitsiz:
        print("meta-source.json'da kaydi olmayan depo: " + ", ".join(kayitsiz))
        print("  -> kayit eklenmeden bu depolar metadata katmanina giremez")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hesap capinda denetim: ekosistem kendi kendini kontrol eder.

Bu betik hicbir seyi duzeltmez. Yalnizca olcer ve ayrismayi yazar;
duzeltme karari insana ya da bir sonraki oturuma aittir.

Depo basina olculenler:
  - project-meta.json varsayilan dalda duruyor mu
  - schema/meta-source.json icinde kaydi var mi (yoksa iskelet uretilir)
  - metadata'nin mekanik yarisi canli gercekle ayristi mi
    (description, topics, license, homepage, status, ci.workflows)
  - LICENSE ve README yerinde mi
  - hic is akisi var mi
  - varsayilan dalda en son tamamlanan kosular kirmizi mi
  - yayindaki adres (homepage) hala aciliyor mu

Cikti: markdown rapor (stdout) + schema/denetim.json.

Cikis kodu **her zaman 0**. Baska bir deponun eksigi bu deponun CI'ini
kirmizi yakmaz; sinyal, acilan/guncellenen konudur.

Yalnizca standart kutuphane. Dependabot uyarilari bilerek disarida:
onlar genel okumaya kapali, GITHUB_TOKEN baska bir depoda goremez;
goremedigi bir seyi "temiz" diye yazmaktansa hic yazmiyor.

    GITHUB_TOKEN=... python3 schema/denetim.py
"""

import hashlib
import importlib.util
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAK = KOK / "schema" / "meta-source.json"
CIKTI = KOK / "schema" / "denetim.json"


def _derle():
    """derle.py icindeki API yardimcilarini odunc alir.

    Ayni istek mantigini iki yerde yazmamak icin: derle.py tek kaynak.
    """
    yol = KOK / "schema" / "derle.py"
    spec = importlib.util.spec_from_file_location("meta_derle", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = _derle()
OWNER = D.OWNER
API = D.API


def _belki(url, varsayilan=None):
    """404'u veri olarak kabul eder; digerlerini yukari birakir."""
    try:
        return D._get(url)
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            return varsayilan
        raise


def _kok_dosyalari(ad, dal):
    girdiler = _belki(f"{API}/repos/{OWNER}/{ad}/contents/?ref={dal}", [])
    return {g["name"] for g in girdiler or []}


def _is_akislari(ad, dal):
    girdiler = _belki(f"{API}/repos/{OWNER}/{ad}/contents/.github/workflows?ref={dal}", [])
    return sorted(g["name"] for g in girdiler or []
                  if g["name"].endswith((".yml", ".yaml")))


def _kirmizi_kosular(ad, dal, akislar):
    """Deponun KENDI is akislarinin en son tamamlanan kosusuna bakar.

    Iki filtre var, ikisi de bilerek:
      - Tek tek kosulara degil, akis basina *en son* kosuya bakilir. Iki
        hafta once kirmizi yanip sonra duzelen bir akis bugun sorun degil.
      - GitHub'in kendi yonettigi kosular (Dependabot guncelleyicisi,
        varsayilan kurulumlu CodeQL) `path` alani `.github/workflows/`
        altinda olmadigi icin disarida kalir. Onlar deponun CI'i degil;
        arsivli bir depoda kuyrukta asili kalan ya da bilerek reddedilmis
        bir bagimlilik yukseltmesi yuzunden surekli kirmizi yanan bir
        kosu, her gun tekrar bildirilecek bir bulgu degildir.
    """
    kendi = {".github/workflows/" + a for a in akislar}
    veri = _belki(f"{API}/repos/{OWNER}/{ad}/actions/runs"
                  f"?branch={dal}&status=completed&per_page=50", {})
    son = {}
    for k in (veri or {}).get("workflow_runs", []):
        if k.get("path") not in kendi:
            continue
        son.setdefault(k["path"], k)
    return sorted(k["name"] for k in son.values()
                  if k["conclusion"] in ("failure", "timed_out", "startup_failure"))


def _canli_mi(url):
    """Yayindaki adres hala aciliyor mu.

    Bir Pages sitesi sessizce olebilir: depo yesil, README dogru, baglanti
    olu. Kimse tiklamadan fark edilmez -- bu yuzden her gun tiklanir.
    None doner: agdan bir cevap alinamadi, yani "olu" demek dogru olmaz.
    """
    istek = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "ekosistem-denetim",
    })
    try:
        with urllib.request.urlopen(istek, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def _iskelet(r):
    """Kayitsiz bir depo icin meta-source.json taslagi.

    Mekanik olan doldurulur; yazili alanlar `null` birakilir. Bir sonraki
    oturum bunlari **kodu okuyarak** yazar -- tahminle degil. Bos birakmak
    makul gorunen bir yalandan iyidir.
    """
    return {
        "status": "archived" if r["archived"] else "active",
        "category": None,
        "platform": [],
        "technologies": [],
        "key_features": [],
        "tests": None,
        "social": {"headline": None, "hashtags": []},
    }


def _ayrismalar(meta, r, akislar, kok):
    """Metadata'nin mekanik yarisi ile canli gercek arasindaki fark."""
    f = []
    canli_konu = sorted(r.get("topics") or [])
    canli_lisans = (r.get("license") or {}).get("spdx_id")
    if canli_lisans in ("NOASSERTION", ""):
        canli_lisans = None
    canli_ana = (r.get("homepage") or "").strip() or None
    canli_durum = "archived" if r["archived"] else None

    if (meta.get("summary") or None) != (r.get("description") or None):
        f.append("summary <-> depo description ayrismis")
    if sorted(meta.get("topics") or []) != canli_konu:
        f.append("topics ayrismis: dosyada %d, depoda %d"
                 % (len(meta.get("topics") or []), len(canli_konu)))
    if meta.get("license") != canli_lisans:
        f.append("license ayrismis: dosyada %r, depoda %r"
                 % (meta.get("license"), canli_lisans))
    if meta.get("homepage") != canli_ana:
        f.append("homepage ayrismis: dosyada %r, depoda %r"
                 % (meta.get("homepage"), canli_ana))
    if canli_durum and meta.get("status") != "archived":
        f.append("depo arsivli ama status %r" % (meta.get("status"),))
    if sorted((meta.get("ci") or {}).get("workflows") or []) != akislar:
        f.append("ci.workflows ayrismis: dosyada %s, depoda %s"
                 % ((meta.get("ci") or {}).get("workflows"), akislar))
    belgeler = meta.get("docs") or {}
    for alan, ad in (("readme", "README"), ("license_file", "LICENSE")):
        yazan = belgeler.get(alan)
        if yazan and yazan not in kok:
            f.append("docs.%s=%r dosyasi depoda yok" % (alan, yazan))
    return f


def _depoyu_olc(r, kaynak):
    ad, dal = r["name"], r["default_branch"]
    bulgular, iskelet = [], None
    kok = _kok_dosyalari(ad, dal)
    akislar = _is_akislari(ad, dal)

    if ad not in kaynak:
        bulgular.append(("kayit", "schema/meta-source.json icinde kaydi yok"))
        iskelet = _iskelet(r)

    meta = D._meta(ad, dal)
    if meta is None:
        bulgular.append(("metadata", "project-meta.json varsayilan dalda yok"))
    else:
        for m in _ayrismalar(meta, r, akislar, kok):
            bulgular.append(("ayrisma", m))

    ana = (meta or {}).get("homepage") or (r.get("homepage") or "").strip() or None
    if ana:
        kod = _canli_mi(ana)
        if kod is not None and kod >= 400:
            bulgular.append(("baglanti", "yayindaki adres %s -> HTTP %d" % (ana, kod)))

    if "LICENSE" not in kok and "LICENSE.md" not in kok:
        bulgular.append(("belge", "LICENSE yok"))
    if not any(a.lower().startswith("readme.") for a in kok):
        bulgular.append(("belge", "README yok"))
    if not (r.get("description") or "").strip():
        bulgular.append(("vitrin", "depo description bos"))
    if not (r.get("topics") or []):
        bulgular.append(("vitrin", "depo topics bos"))

    if r["archived"]:
        # Arsivli depoda is akisi kosmaz; kirmizi aramak yanlis alarm uretir.
        return bulgular, iskelet
    if not akislar:
        bulgular.append(("ci", "hic is akisi yok"))
    else:
        for w in _kirmizi_kosular(ad, dal, akislar):
            bulgular.append(("ci", "son kosu kirmizi: %s" % w))
    return bulgular, iskelet


BASLIK = {
    "kayit": "Metadata katmanina girmemis depo",
    "metadata": "project-meta.json eksik",
    "ayrisma": "Metadata canli gercekle ayrismis",
    "belge": "Temel belge eksik",
    "vitrin": "Vitrin alani bos",
    "ci": "CI",
    "baglanti": "Yayindaki adres cevap vermiyor",
}
SIRA = ["metadata", "kayit", "ci", "baglanti", "ayrisma", "belge", "vitrin"]


def _rapor(bulgular, iskeletler, depo_sayisi):
    if not bulgular:
        return "Denetim temiz: %d depo, bulgu yok." % depo_sayisi
    s = ["**%d depoda %d bulgu.**" % (len({b[0] for b in bulgular}), len(bulgular)), ""]
    for tur in SIRA:
        alt = [b for b in bulgular if b[1] == tur]
        if not alt:
            continue
        s.append("### %s" % BASLIK[tur])
        s.append("")
        for depo, _, mesaj in alt:
            s.append("- **%s** -- %s" % (depo, mesaj))
        s.append("")
    if iskeletler:
        s.append("### Yeni depo icin hazir kayit")
        s.append("")
        s.append("Asagidaki taslak `schema/meta-source.json` icine eklenir. "
                 "Mekanik alanlar dolu; `null` ve bos liste olanlar **kodu "
                 "okuyarak** yazilir, tahminle doldurulmaz.")
        s.append("")
        s.append("```json")
        s.append(json.dumps(iskeletler, indent=2, ensure_ascii=False))
        s.append("```")
        s.append("")
    return "\n".join(s).rstrip() + "\n"


def main():
    kaynak = json.loads(KAYNAK.read_text(encoding="utf-8"))
    depolar = [r for r in D._repos() if not r.get("fork")]

    bulgular, iskeletler = [], {}
    for r in sorted(depolar, key=lambda x: x["name"].lower()):
        alt, iskelet = _depoyu_olc(r, kaynak)
        for tur, mesaj in alt:
            bulgular.append((r["name"], tur, mesaj))
        if iskelet is not None:
            iskeletler[r["name"]] = iskelet

    # Kayitli ama artik var olmayan depo: silinmis ya da adi degismis.
    adlar = {r["name"] for r in depolar}
    for ad in sorted(set(kaynak) - adlar):
        bulgular.append((ad, "kayit",
                         "meta-source.json'da var ama boyle bir depo yok "
                         "(silinmis, adi degismis ya da gizli)"))

    metin = _rapor(bulgular, iskeletler, len(depolar))
    parmak = hashlib.sha256(
        "\n".join("|".join(b) for b in sorted(bulgular)).encode("utf-8")
    ).hexdigest()[:16]

    CIKTI.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owner": OWNER,
        "repo_count": len(depolar),
        "finding_count": len(bulgular),
        "fingerprint": parmak,
        "note": "Bulgular olculmustur; hicbiri otomatik duzeltilmez. "
                "Dependabot uyarilari kapsam disi: genel okumaya kapali.",
        "findings": [{"repo": a, "kind": b, "message": c} for a, b, c in bulgular],
        "onboarding_skeletons": iskeletler,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print(metin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merkezi proje panosu: yonetim/gorevler.json + yonetim/portfoy.json -> yonetim/PANO.md

    python3 yonetim/pano.py            # dogrula ve PANO.md'yi yaz
    python3 yonetim/pano.py --kontrol  # dogrula; PANO.md guncel degilse cikis 1 (CI)
    python3 yonetim/pano.py --tara /home/user   # portfoy.json'da her oyunun kit surumunu klonlardan oku

Tek kaynak gorevler.json'dur; PANO.md ondan uretilir, elle duzenlenmez.

DURUMLAR: Bekliyor, Devam Ediyor, Test Ediliyor, Tamamlandi (Tamamlandı), Engellendi
KURALLAR (biri bozulursa cikis 1):
  - id benzersiz ve G-NNN bicimli; oncelik P0..P3
  - bagimli listesindeki her id var; bagimlilikta dongu yok
  - Tamamlandı: kanit bos degil, kapandi tarihi var
  - Engellendi: engel.neden ve engel.gereken var (gercek neden ve gereken erisim/mudahale)
  - aktif (tamamlanmamis) gorevler arasinda ayni baslik iki kez yok (tekrar onleme)
Bir Bekliyor gorevin bagimliliklarinin hepsi Tamamlandı degilse "hazir degil" sayilir;
"Siradaki is" hazir gorevlerin en yuksek oncelikli ve en eski olanidir.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

KOK = os.path.dirname(os.path.abspath(__file__))
DURUMLAR = ["Devam Ediyor", "Test Ediliyor", "Bekliyor", "Engellendi", "Tamamlandı"]
ONCELIK = ["P0", "P1", "P2", "P3"]
OYUNLAR = ["bogaz-vapuru", "carsi-kacisi", "cay-ocagi", "cini-ustasi", "dolmus", "ebru", "fay-hatti", "hamsi",
           "kale-savunmasi", "kapadokya-balonu", "karagoz", "kervan", "kirkpinar", "lale-bahcesi", "marti",
           "mehter", "mimar-sinan", "pamukkale", "peri-golf", "simit-firini", "topkapi-gecesi"]


def _norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


def dogrula(veri, portfoy=None):
    """Hata listesi dondurur (bos = gecerli)."""
    hata = []
    gorevler = veri.get("gorevler", [])
    ids = {}
    for g in gorevler:
        gid = g.get("id", "?")
        if not re.fullmatch(r"G-\d{3}", gid):
            hata.append(f"{gid}: id G-NNN bicimli olmali")
        if gid in ids:
            hata.append(f"{gid}: id tekrar ediyor")
        ids[gid] = g
        if g.get("durum") not in DURUMLAR:
            hata.append(f"{gid}: gecersiz durum {g.get('durum')!r}")
        if g.get("oncelik") not in ONCELIK:
            hata.append(f"{gid}: gecersiz oncelik {g.get('oncelik')!r}")
        if not g.get("baslik"):
            hata.append(f"{gid}: baslik yok")
        if g.get("durum") == "Tamamlandı":
            if not g.get("kanit"):
                hata.append(f"{gid}: Tamamlandı ama kanit yok")
            if not g.get("kapandi"):
                hata.append(f"{gid}: Tamamlandı ama kapandi tarihi yok")
        if g.get("durum") == "Engellendi":
            e = g.get("engel") or {}
            if not e.get("neden") or not e.get("gereken"):
                hata.append(f"{gid}: Engellendi ama engel.neden / engel.gereken eksik")
    for g in gorevler:
        for b in g.get("bagimli", []):
            if b not in ids:
                hata.append(f"{g.get('id')}: bilinmeyen bagimlilik {b}")
    # dongu
    renk = {}

    def gez(gid, yol):
        renk[gid] = 1
        for b in ids.get(gid, {}).get("bagimli", []):
            if b not in ids:
                continue
            if renk.get(b) == 1:
                hata.append("bagimlilik dongusu: " + " -> ".join(yol + [b]))
            elif not renk.get(b):
                gez(b, yol + [b])
        renk[gid] = 2

    for gid in ids:
        if not renk.get(gid):
            gez(gid, [gid])
    # tekrar onleme
    gorulen = {}
    for g in gorevler:
        if g.get("durum") == "Tamamlandı":
            continue
        n = _norm(g.get("baslik", ""))
        if n in gorulen:
            hata.append(f"{g.get('id')}: {gorulen[n]} ile ayni baslik (tekrar)")
        gorulen[n] = g.get("id")
    if portfoy is not None:
        adlar = [o.get("oyun") for o in portfoy.get("oyunlar", [])]
        for o in OYUNLAR:
            if o not in adlar:
                hata.append(f"portfoy: {o} yok")
        for a in adlar:
            if adlar.count(a) > 1:
                hata.append(f"portfoy: {a} tekrar ediyor")
    return sorted(set(hata))


def hazir_mi(g, ids):
    return g["durum"] == "Bekliyor" and all(ids[b]["durum"] == "Tamamlandı" for b in g.get("bagimli", []) if b in ids)


def sira(gorevler):
    ids = {g["id"]: g for g in gorevler}
    aktif = [g for g in gorevler if g["durum"] not in ("Tamamlandı", "Engellendi")]
    anahtar = lambda g: (DURUMLAR.index(g["durum"]) if g["durum"] != "Bekliyor" else 2, ONCELIK.index(g["oncelik"]), g["id"])
    aktif.sort(key=anahtar)
    hazir = sorted([g for g in aktif if hazir_mi(g, ids)], key=lambda g: (ONCELIK.index(g["oncelik"]), g["id"]))
    return aktif, hazir


def _hucre(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def yaz(veri, portfoy):
    gorevler = veri["gorevler"]
    ids = {g["id"]: g for g in gorevler}
    aktif, hazir = sira(gorevler)
    engel = sorted([g for g in gorevler if g["durum"] == "Engellendi"], key=lambda g: (ONCELIK.index(g["oncelik"]), g["id"]))
    bitti = sorted([g for g in gorevler if g["durum"] == "Tamamlandı"], key=lambda g: (g.get("kapandi", ""), g["id"]), reverse=True)
    say = {d: sum(1 for g in gorevler if g["durum"] == d) for d in DURUMLAR}
    o = []
    o.append("# Proje panosu\n")
    o.append(f"<!-- yonetim/pano.py uretti; elle duzenleme: kaynak yonetim/gorevler.json -->\n")
    o.append(f"Güncellendi: {veri.get('guncellendi', '?')}\n")
    o.append("| " + " | ".join(DURUMLAR) + " |")
    o.append("|" + "---|" * len(DURUMLAR))
    o.append("| " + " | ".join(str(say[d]) for d in DURUMLAR) + " |\n")
    if hazir:
        g = hazir[0]
        o.append(f"**Sıradaki iş:** {g['id']} ({g['oncelik']}) {g['baslik']}\n")
    if veri.get("kalici_onaylar"):
        o.append("## Kalıcı kullanıcı onayları\n")
        for k in veri["kalici_onaylar"]:
            o.append(f"- {k['tarih']}: {k['kapsam']}")
        o.append("")
    o.append("## Aktif işler\n")
    o.append("| Id | Öncelik | Durum | İş | Alan | Bağımlı | Not |")
    o.append("|---|---|---|---|---|---|---|")
    for g in aktif:
        dur = g["durum"] + ("" if g["durum"] != "Bekliyor" or hazir_mi(g, ids) else " (hazır değil)")
        o.append(f"| {g['id']} | {g['oncelik']} | {dur} | {_hucre(g['baslik'])} | {_hucre(g.get('alan'))} | {', '.join(g.get('bagimli', []))} | {_hucre(g.get('not'))} |")
    o.append("\n## Engellenen işler\n")
    o.append("| Id | Öncelik | İş | Gerçek neden | Gereken |")
    o.append("|---|---|---|---|---|")
    for g in engel:
        e = g["engel"]
        o.append(f"| {g['id']} | {g['oncelik']} | {_hucre(g['baslik'])} | {_hucre(e['neden'])} | {_hucre(e['gereken'])} |")
    o.append("\n## Portföy\n")
    kol = portfoy.get("kolonlar", [])
    o.append("| Oyun | " + " | ".join(k["baslik"] for k in kol) + " |")
    o.append("|---|" + "---|" * len(kol))
    for oy in sorted(portfoy.get("oyunlar", []), key=lambda x: x["oyun"]):
        o.append(f"| {oy['oyun']} | " + " | ".join(_hucre(oy.get(k["anahtar"], "")) for k in kol) + " |")
    o.append("\n## Geçmiş (tamamlanan, en yeni önce)\n")
    for g in bitti:
        o.append(f"- **{g['id']}** {g.get('kapandi')} · {g['baslik']}")
        for k in g["kanit"]:
            o.append(f"  - {k}")
    return "\n".join(o) + "\n"


def tara(portfoy, klonlar):
    for oy in portfoy["oyunlar"]:
        f = os.path.join(klonlar, oy["oyun"], "index.html")
        try:
            m = re.search(r"ARENA-KIT:BEGIN v([\d.]+)", open(f, encoding="utf-8").read())
            oy["kit"] = m.group(1) if m else "yok"
        except OSError:
            pass
    return portfoy


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrol", action="store_true")
    ap.add_argument("--tara")
    a = ap.parse_args(argv)
    gp, pp, mp = (os.path.join(KOK, n) for n in ("gorevler.json", "portfoy.json", "PANO.md"))
    veri = json.load(open(gp, encoding="utf-8"))
    portfoy = json.load(open(pp, encoding="utf-8"))
    if a.tara:
        portfoy = tara(portfoy, a.tara)
        with open(pp, "w", encoding="utf-8") as f:
            json.dump(portfoy, f, ensure_ascii=False, indent=1)
            f.write("\n")
    hata = dogrula(veri, portfoy)
    for h in hata:
        print("HATA", h)
    if hata:
        return 1
    metin = yaz(veri, portfoy)
    if a.kontrol:
        eski = open(mp, encoding="utf-8").read() if os.path.exists(mp) else ""
        if eski != metin:
            print("PANO.md guncel degil: python3 yonetim/pano.py")
            return 1
        print("pano: ok")
        return 0
    with open(mp, "w", encoding="utf-8") as f:
        f.write(metin)
    aktif, hazir = sira(veri["gorevler"])
    print(f"pano: {len(veri['gorevler'])} gorev, {len(aktif)} aktif, siradaki: {hazir[0]['id'] if hazir else '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

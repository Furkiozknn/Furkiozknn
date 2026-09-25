"""README'nin "Recently" bolumu: son yazilar ve son surumler.

Bir profil, ziyaretcisine hesabin canli olup olmadigini soylemeli -- ama
elle tutulan bir "son haberler" listesi, yazildigi gun eskimeye baslar. Bu
betik o bolumu iki kaynaktan uretir:

  - `yazilar/*.md`: her yazinin basindaki `---` blogu (title, date, summary)
  - GitHub API: her deponun en son yayimlanmis surumu

ve README'de `<!-- vitrin:bas -->` ile `<!-- vitrin:son -->` arasini yeniden
yazar. Isaretlerin disina dokunmaz.

    python3 schema/vitrin.py            # yazilar + surumler (ag gerekir)
    python3 schema/vitrin.py --agsiz    # yalnizca yazilar; surum satirlari korunur
    python3 schema/vitrin.py --kontrol  # README yazilar/ ile uyusuyor mu (agsiz)

Yalnizca standart kutuphane.
"""

import argparse
import importlib.util
import re
import sys
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
README = KOK / "README.md"
YAZILAR = KOK / "yazilar"
BAS, SON = "<!-- vitrin:bas -->", "<!-- vitrin:son -->"
YAZI_SAYISI, SURUM_SAYISI = 3, 4

AY = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def on_bilgi(metin):
    """`---` ile acilan blogun anahtar: deger satirlari. Yoksa {}."""
    m = re.match(r"---\n(.*?)\n---\n", metin, re.S)
    if not m:
        return {}
    alanlar = {}
    for satir in m.group(1).splitlines():
        a, ayrac, d = satir.partition(":")
        if ayrac:
            alanlar[a.strip()] = d.strip().strip('"')
    return alanlar


def yazilar(dizin=YAZILAR):
    """Yayimlanmis yazilar, yeniden eskiye. `draft: true` olanlar disarida.

    Tarihi okunamayan bir yazi listeye sessizce girmez: hata verir. Sirasi
    tarihe bagli bir listede tarihsiz bir satir, yanlis yere oturur.
    """
    bulunan = []
    for yol in sorted(dizin.glob("*.md")):
        if yol.name.lower() == "readme.md":
            continue
        b = on_bilgi(yol.read_text(encoding="utf-8"))
        if b.get("draft", "").lower() == "true":
            continue
        eksik = [a for a in ("title", "date", "summary") if not b.get(a)]
        if eksik:
            raise ValueError("%s: on bilgide eksik alan: %s" % (yol.name, ", ".join(eksik)))
        bulunan.append({"title": b["title"], "date": date.fromisoformat(b["date"]),
                        "summary": b["summary"], "path": "yazilar/" + yol.name})
    # Ayni gunun yazilari dosya adina gore: sira her calismada ayni kalsin.
    bulunan.sort(key=lambda y: y["path"])
    return sorted(bulunan, key=lambda y: y["date"], reverse=True)


def gun(d):
    return "%d %s %d" % (d.day, AY[d.month - 1], d.year)


def _derle():
    spec = importlib.util.spec_from_file_location("derle", KOK / "schema" / "derle.py")
    derle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(derle)
    return derle


def surumler():
    """Her deponun en son surumu, yeniden eskiye. derle.py'nin istemcisiyle."""
    derle = _derle()
    depolar = derle._repos()
    if not depolar:
        # Bos bir liste "hic surum yok" degil, "API bir sey dondurmedi" demek.
        # Sessizce devam etmek Releases satirlarini README'den silerdi.
        raise SystemExit("vitrin: GitHub depo listesi bos dondu; README'ye dokunulmadi")
    bulunan = []
    for r in depolar:
        if r.get("fork") or r.get("archived") or r.get("private"):
            continue
        s = derle._release(r["name"])
        if s:
            bulunan.append({"repo": r["name"], "tag": s["tag"], "url": s["url"],
                            "date": date.fromisoformat(s["published_at"][:10])})
    return sorted(bulunan, key=lambda s: (s["date"], s["repo"]), reverse=True)


def blok(yazi_listesi, surum_satirlari):
    """Isaretlerin arasina girecek metin. `surum_satirlari` hazir markdown."""
    satirlar = [BAS, ""]
    if yazi_listesi:
        satirlar.append("**Writing**")
        satirlar.append("")
        for y in yazi_listesi[:YAZI_SAYISI]:
            satirlar.append("- [%s](%s) — %s <sub>%s</sub>"
                            % (y["title"], y["path"], y["summary"], gun(y["date"])))
        satirlar.append("")
    if surum_satirlari:
        satirlar.append("**Releases**")
        satirlar.append("")
        satirlar.extend(surum_satirlari)
        satirlar.append("")
    satirlar.append(SON)
    return "\n".join(satirlar)


def surum_satirlari(liste):
    return ["- [%s %s](%s) <sub>%s</sub>" % (s["repo"], s["tag"], s["url"], gun(s["date"]))
            for s in liste[:SURUM_SAYISI]]


def mevcut_blok(metin):
    i, j = metin.find(BAS), metin.find(SON)
    if i < 0 or j < i:
        raise ValueError("README'de %s ... %s isaretleri yok" % (BAS, SON))
    return i, j + len(SON)


def mevcut_surum_satirlari(metin):
    i, j = mevcut_blok(metin)
    ic = metin[i:j]
    k = ic.find("**Releases**")
    if k < 0:
        return []
    return [s for s in ic[k:].splitlines() if s.startswith("- ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agsiz", action="store_true", help="surumleri API'den okuma")
    ap.add_argument("--kontrol", action="store_true",
                    help="yalnizca README'nin yazilar/ ile uyustugunu dogrula")
    args = ap.parse_args()

    metin = README.read_text(encoding="utf-8")
    i, j = mevcut_blok(metin)
    liste = yazilar()

    if args.kontrol or args.agsiz:
        surum = mevcut_surum_satirlari(metin)
    else:
        surum = surum_satirlari(surumler())
    yeni = blok(liste, surum)

    if args.kontrol:
        if metin[i:j] != yeni:
            print("README'nin Recently bolumu yazilar/ ile uyusmuyor: "
                  "python3 schema/vitrin.py --agsiz")
            return 1
        print("Recently bolumu guncel (%d yazi, %d surum satiri)." % (len(liste), len(surum)))
        return 0

    if metin[i:j] == yeni:
        print("degisiklik yok")
        return 0
    README.write_text(metin[:i] + yeni + metin[j:], encoding="utf-8", newline="\n")
    print("README guncellendi (%d yazi, %d surum satiri)." % (len(liste), len(surum)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

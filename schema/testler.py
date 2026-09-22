#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yayimlanan test sayisi: olc, ve gorunen her yerde ayni yaz.

    python3 schema/testler.py                  # kontrol (agsiz) + olcum (jeton varsa)
    python3 schema/testler.py --kontrol        # yalnizca agsiz tutarlilik kapisi
    DEPO_JETONU=... python3 schema/testler.py --olc
    DEPO_JETONU=... python3 schema/testler.py --yaz

NEDEN VAR
---------
Tek bir sayi -- "4.700 test" -- su anda yedi yerde duruyor: hero.svg'nin
icinde, README'nin alt metninde, rozet adresinde, iki tablonun Toplam
satirinda, altbilgi baglantisinda, TESTLER.md'nin basliginda ve Toplam
satirinda; her deponun kendi sayisi da ayrica meta-source.json'da ve o
deponun project-meta.json'unda. Hepsi elle yazilmisti.

`denetim.py` bu ayrismayi her gun GORUYOR -- TESTLER.md basligini metadata
toplamiyla, README tablosunu metadata ile karsilastiriyor -- ama hicbirini
DUZELTEMIYOR, ve bir seyi daha hic gormuyor: TESTLER.md'nin KENDI tablo
satirlarini kimse metadata ile karsilastirmiyordu. Baslik ile Toplam
tutarken satirlarin eskimesi mumkundu.

Bu betik o bosluga bakiyor. `yenile.yml`'in metadata icin yaptigi seyin
ayni: denetim olcer, bu duzeltir.

OLCUM KAYNAGI
-------------
Sayilar buradan uydurulmuyor. Metadata kurali zaten "bir sayi ancak onu
yazdiran kosu satiriyla birlikte yayimlanir" diyor; `tests.source` o satiri
backtick icinde tasiyor. `--olc`, deponun en yeni BASARILI ci.yml kosusunun
logunu indirip o satiri yeniden okuyor ve bugunku sayiyi oradan aliyor.
Birlesik kaynaklar (`96 backend + 228 frontend`) tek bir satirdan
okunamadigi icin OLCULEMEZ sayiliyor ve ellenmiyor -- yanlis sayilmiyor,
sadece insana birakiliyor.

Denetimin log okuma mantigi burada tekrar yazilmadi; `denetim.py` ice
aktarilip `kalip` / `_log_metni` / `sayiyi_bul` odunc aliniyor. Iki yerde
iki farkli okuyucu olsaydi, ikisinin ayni sayiyi okudugunu da birinin
dogrulamasi gerekirdi.

Cikis kodu: --kontrol ya da --olc'de tutarsizlik/sapma varsa 1.
"""

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAK = KOK / "schema" / "meta-source.json"
TESTLER = KOK / "TESTLER.md"
README = KOK / "README.md"
HERO = KOK / "assets" / "hero.svg"

AY = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _denetim():
    """denetim.py'nin log okuyucusunu odunc alir (tek kaynak)."""
    spec = importlib.util.spec_from_file_location(
        "ekosistem_denetim", KOK / "schema" / "denetim.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def yuk():
    return json.loads(KAYNAK.read_text(encoding="utf-8"))


def sayilar(kaynak):
    """{depo: count} -- tests blogu olan ve ARSIVLI OLMAYAN girdiler.

    Arsivli depo profilde sayilmiyor; TESTLER.md bunu acikca yaziyor ve
    denetim.py ayni ayrimi GitHub API'sindeki `archived` bayragiyla
    yapiyor. Burada `status` alani kullaniliyor: bu betigin agsiz kipi
    (--kontrol, CI kapisi) hicbir istek yapmadan ayni cevabi vermeli.
    """
    return {ad: g["tests"]["count"]
            for ad, g in kaynak.items()
            if isinstance(g.get("tests"), dict) and g["tests"].get("count")
            and g.get("status") != "archived"}


def bicim(n):
    return f"{n:,}"


# --------------------------------------------------------------------------
# agsiz kontrol
# --------------------------------------------------------------------------

SATIR = re.compile(r"\]\(https://github\.com/Furkiozknn/([A-Za-z0-9._-]+)\)")


def _tablo_satirlari(metin):
    """{depo: (satir, o satirdaki son sayi)} -- markdown tablo satirlari."""
    bulunan = {}
    for s in metin.splitlines():
        if not s.startswith("|"):
            continue
        d = SATIR.search(s)
        if not d:
            continue
        # TESTLER.md sayiyi duz yaziyor, README backtick icinde.
        ham = re.findall(r"`([\d,]+)`", s) or re.findall(r"\|\s*([\d,]+)\s*\|", s)
        if ham:
            bulunan[d.group(1)] = (s, int(ham[-1].replace(",", "")))
    return bulunan


def kontrol(kaynak):
    """Yayimlanan her yer, meta-source.json ile ayni seyi mi soyluyor."""
    sorunlar = []
    beklenen = sayilar(kaynak)
    toplam = sum(beklenen.values())

    testler = TESTLER.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    hero = HERO.read_text(encoding="utf-8")

    m = re.search(r"#\s*Where the ([\d,]+) comes from", testler)
    if not m:
        sorunlar.append("TESTLER.md basligindaki sayi okunamadi")
    elif int(m.group(1).replace(",", "")) != toplam:
        sorunlar.append("TESTLER.md basligi %s diyor, metadata toplami %s"
                        % (m.group(1), bicim(toplam)))

    # TESTLER.md'nin KENDI tablo satirlari. denetim.py bunlara hic bakmiyor.
    for ad, (_, yazan) in _tablo_satirlari(testler).items():
        if ad in beklenen and yazan != beklenen[ad]:
            sorunlar.append("TESTLER.md tablosunda %s icin %d yaziyor, metadata %d"
                            % (ad, yazan, beklenen[ad]))
    eksik = sorted(set(beklenen) - set(_tablo_satirlari(testler)))
    if eksik:
        sorunlar.append("TESTLER.md tablosunda satiri olmayan depo(lar): "
                        + ", ".join(eksik))

    for ad, (_, yazan) in _tablo_satirlari(readme).items():
        if ad in beklenen and yazan != beklenen[ad]:
            sorunlar.append("README tablosunda %s icin %d yaziyor, metadata %d"
                            % (ad, yazan, beklenen[ad]))

    # Tablo disi tanitim satirlari. Tablo dogru kalirken hemen ustundeki
    # cumlenin eskimesi, okurun once gordugu sayinin yanlis olmasi demek.
    for satir in readme.splitlines():
        if not (satir.lstrip().startswith(">") and "<sub>" in satir):
            continue
        d = SATIR.search(satir)
        n = re.search(r"<sub>`([\d,]+) tests`</sub>", satir)
        if d and n and d.group(1) in beklenen:
            yazan = int(n.group(1).replace(",", ""))
            if yazan != beklenen[d.group(1)]:
                sorunlar.append("README tanitim satirinda %s icin %d yaziyor, metadata %d"
                                % (d.group(1), yazan, beklenen[d.group(1)]))

    for yer, metin in (("TESTLER.md", testler), ("README.md", readme)):
        for satir in metin.splitlines():
            if not (satir.startswith("|") and "Total" in satir):
                continue
            ham = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", satir)]
            buyuk = [x for x in ham if x > 100]
            if buyuk and buyuk[-1] != toplam:
                sorunlar.append("%s Toplam satiri %s diyor, toplam %s"
                                % (yer, bicim(buyuk[-1]), bicim(toplam)))

    for yer, metin in (("README.md", readme), ("assets/hero.svg", hero)):
        if bicim(toplam) not in metin and str(toplam) not in metin:
            sorunlar.append("%s icinde %s sayisi hic gecmiyor" % (yer, bicim(toplam)))

    # Tek backtick grubu tasiyan bir kaynak "olculebilir" sayiliyor: o satir
    # yayimlanan sayiyi yazmali. Yazmiyorsa kaynak aslinda birlesiktir ve
    # yanlis etiketlenmistir -- ve gunluk denetim o satiri okuyup her sabah
    # sahte bir sapma bildirir. (Bu kontrol yazilirken buradane tam olarak
    # bu duruma dusmustu: 334 yayimlaniyor, kaynak satiri `106 passed`.)
    for ad, g in kaynak.items():
        t = g.get("tests")
        if not isinstance(t, dict) or ad not in beklenen:
            continue
        hepsi = re.findall(r"`([^`]*\d[^`]*)`", t.get("source") or "")
        if len(hepsi) != 1:
            continue
        ic = re.findall(r"\d[\d,]*", hepsi[0])
        if ic and int(ic[0].replace(",", "")) != t["count"]:
            sorunlar.append(
                "%s: kaynak satiri %s yaziyor ama sayi %d -- tek satirlik bir "
                "kaynak yayimlanan sayiyi yazmali (birlesikse backtick koyma)"
                % (ad, ic[0], t["count"]))

    suit = len(beklenen)
    if not re.search(r"across %d repositories with suites" % suit, readme):
        sorunlar.append("README Toplam satirindaki suit sayisi %d degil" % suit)
    if not re.search(r"%d with suites" % suit, hero):
        sorunlar.append("hero.svg '%d with suites' demiyor" % suit)

    return sorunlar


# --------------------------------------------------------------------------
# olcum
# --------------------------------------------------------------------------

def tum_sayilar(metin, desen, D):
    """Kalibin log metnindeki BUTUN eslesmeleri.

    denetim.py'nin `sayiyi_bul`u ilkini aliyor. Bir kosu tek is oldugu
    surece dogru; ai-workflow-engine'e ikinci bir is (sozlesme testleri)
    eklendigi anda ayni log hem `72 passed` hem `8 passed` tasiyor ve ilk
    eslesme 8 cikiyor. Olculen sayiyi YAZAN bir arac icin bu kabul
    edilemez: farkli sayilar eslesiyorsa dogru cevap "belirsiz"dir,
    ilkini secmek degil.
    """
    desen, metin = D.sadelestir(desen), D.sadelestir(metin)
    kalip_re = re.sub(r"\d+", r"(\\d+)", re.escape(desen))
    return [int(m.group(1)) for m in re.finditer(kalip_re, metin or "")
            if m.groups()]


class HizSiniri(Exception):
    """GitHub hiz siniri (403 ya da 429). Olcum yarim birakilir.

    Bu ayrimin onemi su: hiz siniri yendigimizde HER depo "kosu logu
    okunamadi" diye gorunuyordu -- yani "bu deponun kosusu yok" ile
    "bugun cok istek attik" ayni satiri yaziyordu. Ikincisini birincisi
    sanip bir sayiyi silmek ya da 'olculemez' diye isaretlemek, olcmenin
    tam tersi olurdu.
    """


def _istek(url, D):
    """GitHub'a istek; 403/429'u YUTMAZ.

    denetim.py'nin `_belki`si 403'u 404 gibi ele alip bos liste donuyor.
    Bir denetim icin savunulabilir; burada degil: GitHub'in ikincil hiz
    siniri da 403 dondugu icin "bu deponun is akisi yok" ile "cok hizli
    istek attin" ayni bos listeye donusuyordu -- ve 24 depoluk bir olcum
    turunun sonunda HEPSI 'ci.yml yok' diye gorunuyordu. Sayi yazan bir
    araci bu sessizlik uzerine kuramayiz.
    """
    istek = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {D.GENIS}",
        "User-Agent": "ekosistem-testler"})
    try:
        with urllib.request.urlopen(istek, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        govde = ""
        try:
            govde = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        if e.code in (403, 429) and "rate limit" in govde.lower():
            raise HizSiniri("%s (%s)" % (url.rsplit("/repos/", 1)[-1], e.code)) from e
        raise


def is_akislari(ad, dal, D):
    girdiler = _istek(f"{D.API}/repos/{D.OWNER}/{ad}/contents/"
                      f".github/workflows?ref={dal}", D)
    return sorted(g["name"] for g in girdiler or []
                  if g["name"].endswith((".yml", ".yaml")))


def neden_okunamadi(ad, dal, akislar, D):
    """`_log_metni` None dondugunde SEBEBI soyler.

    denetim.py'nin okuyucusu butun hatalari yutup None donuyor; bir
    denetim icin makul (goremedigi seyi yazmaz), ama sayiyi YAZACAK bir
    arac icin degil: "bu deponun ci.yml'i yok", "hic basarili kosu yok",
    "log 40 MB'tan buyuk" ve "GitHub 429 dondu" ayni sessizlige
    donusuyordu, ve sonuncusu butun depolari birden 'olculemez'
    gosteriyordu.
    """
    if "ci.yml" not in akislar:
        return "ci.yml yok"
    veri = _istek(f"{D.API}/repos/{D.OWNER}/{ad}/actions/runs"
                  f"?branch={dal}&status=success&per_page=20", D)
    kosu = next((k for k in (veri or {}).get("workflow_runs", [])
                 if k.get("path") == ".github/workflows/ci.yml"), None)
    if kosu is None:
        return "%s dalinda basarili ci.yml kosusu yok" % dal
    istek = urllib.request.Request(
        f"{D.API}/repos/{D.OWNER}/{ad}/actions/runs/{kosu['id']}/logs",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {D.GENIS}",
                 "User-Agent": "ekosistem-testler"})
    try:
        with urllib.request.urlopen(istek, timeout=90) as r:
            uzunluk = int(r.headers.get("Content-Length") or 0)
        return ("log %.0f MB (tavan 40 MB)" % (uzunluk / 1048576)
                if uzunluk > 40 * 1024 * 1024 else "log indirildi ama cozulemedi")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise HizSiniri(ad) from e
        return "log HTTP %d" % e.code
    except Exception as e:
        return "log alinamadi: %s" % type(e).__name__


def olc(kaynak, D, yalniz=None, bekleme=1.0):
    """{depo: (yayimlanan, olculen|None, aciklama)}

    Her depo icin bir kosu logu (zip) indiriliyor; 24 depo pesi sira
    istendiginde GitHub ikincil hiz sinirini uyguluyor. `bekleme` aralari
    aciyor, `yalniz` tek bir depoyu olcmeyi mumkun kiliyor.
    """
    sonuc = {}
    for ad, g in sorted(kaynak.items()):
        if yalniz and ad not in yalniz:
            continue
        t = g.get("tests")
        if not isinstance(t, dict) or not t.get("count"):
            continue
        desen = D.kalip(t.get("source"))
        if not desen:
            sonuc[ad] = (t["count"], None, "birlesik kaynak - olculemez")
            continue
        ana = is_akislari(ad, "main", D)
        akislar = ana or is_akislari(ad, "master", D)
        dal = "main" if ana else "master"
        metin = D._log_metni(ad, dal, akislar)
        time.sleep(bekleme)
        if metin is None:
            sonuc[ad] = (t["count"], None, neden_okunamadi(ad, dal, akislar, D))
            continue
        hepsi = tum_sayilar(metin, desen, D)
        ayri = sorted(set(hepsi))
        if not hepsi:
            sonuc[ad] = (t["count"], None, "kalip %r logda bulunamadi" % desen)
        elif len(ayri) > 1:
            sonuc[ad] = (t["count"], None,
                         "belirsiz: ayni kalip %s sayilarini esliyor (birden fazla is?)"
                         % ", ".join(str(x) for x in ayri))
        else:
            sonuc[ad] = (t["count"], ayri[0], "")
    return sonuc


# --------------------------------------------------------------------------
# yazma
# --------------------------------------------------------------------------

#: Bir tablo hucresindeki sayi: duz, `backtick` icinde, **kalin**, ya da
#: ikisi birden (`**\`4,700\`**`). Toplam satirlari kalin yazildigi icin
#: yalnizca duz ve backtick'li bicimleri taniyan bir desen onlari atliyordu
#: -- ve atladigi yer tam olarak en cok goze carpan sayiydi.
HUCRE = re.compile(r"(\|\s*(?:\*\*)?`?)([\d,]+)(`?(?:\*\*)?\s*\|)")


AY_KISA = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
           7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


def _olculdu(iso):
    """'2026-09-22' -> '22 Sep 2026'; ayristirilamazsa oldugu gibi birakir."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", iso or "")
    if not m:
        return iso or ""
    y, a, g = (int(x) for x in m.groups())
    return "%d %s %d" % (g, AY_KISA[a], y)


def testler_tablosu(kaynak):
    """TESTLER.md'nin tablo govdesi, bastan uretilir.

    Dort sutunun dordu de meta-source.json'da duruyor: sayi, kaynak satiri,
    olcum tarihi ve deponun adi. Tabloyu elle tutmak, dordunden birini
    unutmak demekti -- ve unutulan genellikle `Source` sutunu oluyordu,
    yani sayinin nereden geldigini soyleyen sutun.
    """
    satirlar = []
    for ad, n in sorted(sayilar(kaynak).items(), key=lambda x: (-x[1], x[0])):
        t = kaynak[ad]["tests"]
        satirlar.append("| [%s](https://github.com/Furkiozknn/%s) | %s | %s | %s |"
                        % (ad, ad, bicim(n), t.get("source", ""), _olculdu(t.get("measured"))))
    satirlar.append("| **Total** | **%s** | | |" % bicim(sum(sayilar(kaynak).values())))
    return satirlar


def _satiri_guncelle(satir, yeni):
    """Tablo satirindaki SON sayiyi degistirir, bicimi bozmadan."""
    eslesmeler = list(HUCRE.finditer(satir))
    if not eslesmeler:
        return satir
    m = eslesmeler[-1]
    return satir[:m.start()] + m.group(1) + bicim(yeni) + m.group(3) + satir[m.end():]


def yaz(kaynak, olculen, bugun, depo_sayisi=None, commit_sayisi=None):
    """meta-source.json + TESTLER.md + README.md + hero.svg.

    `depo_sayisi` ve `commit_sayisi` verilirse manset cumlesindeki o iki
    sayi da ayni gecisle guncellenir. Ikisi de bu dosyadan olculemez (canli
    API olgulari); verilmezse hicbir yerde ellenmez -- tahmin edilecegine,
    verilmeyen sey degistirilmez.
    """
    degisen = {}
    for ad, (yayin, olcum, _) in olculen.items():
        if olcum is not None and olcum != yayin:
            degisen[ad] = olcum
            kaynak[ad]["tests"]["count"] = olcum
            kaynak[ad]["tests"]["measured"] = bugun.strftime("%Y-%m-%d")
    KAYNAK.write_text(json.dumps(kaynak, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8", newline="\n")

    beklenen = sayilar(kaynak)
    toplam = sum(beklenen.values())
    suit = len(beklenen)
    tarih = "%d %s %d" % (bugun.day, AY[bugun.month - 1], bugun.year)

    # TESTLER.md'nin tablosu bastan uretiliyor; README'ninki (vitrin metni
    # tasidigi icin) yerinde guncelleniyor.
    metin = TESTLER.read_text(encoding="utf-8")
    satirlar = metin.splitlines()
    bas = next(i for i, x in enumerate(satirlar) if x.startswith("|---|---:|"))
    son = next(i for i, x in enumerate(satirlar) if x.startswith("| **Total**"))
    satirlar[bas + 1:son + 1] = testler_tablosu(kaynak)
    TESTLER.write_text("\n".join(satirlar) + "\n", encoding="utf-8", newline="\n")

    for yol in (TESTLER, README):
        metin = yol.read_text(encoding="utf-8")
        cikti = []
        for s in metin.splitlines():
            # Tablo disi tanitim satirlari: "> ... [repo](...) ... <sub>`N tests`</sub>"
            # Bunlar da bir sayi yayimliyor ve elle tutuluyordu; ayni gecis
            # onlari da esitliyor, yoksa tablo dogru kalirken hemen ustundeki
            # cumle eskiyor.
            if s.lstrip().startswith(">") and "<sub>" in s:
                d2 = SATIR.search(s)
                if d2 and d2.group(1) in beklenen:
                    s = re.sub(r"<sub>`[\d,]+ tests`</sub>",
                               "<sub>`%s tests`</sub>" % bicim(beklenen[d2.group(1)]), s)
            d = SATIR.search(s) if s.startswith("|") else None
            if d and d.group(1) in beklenen:
                s = _satiri_guncelle(s, beklenen[d.group(1)])
                if d.group(1) in degisen and yol is TESTLER:
                    s = re.sub(r"\|\s*\d+ [A-Z][a-z]{2} \d{4}\s*\|$",
                               "| %s |" % tarih, s)
            elif s.startswith("|") and "Total" in s:
                s = _satiri_guncelle(s, toplam)
                s = re.sub(r"across \d+ repositories with suites",
                           "across %d repositories with suites" % suit, s)
            cikti.append(s)
        metin = "\n".join(cikti) + ("\n" if metin.endswith("\n") else "")
        metin = re.sub(r"(Where the )[\d,]+( comes from)",
                       r"\g<1>%s\g<2>" % bicim(toplam), metin)
        metin = re.sub(r"(claims )[\d,]+( tests)",
                       r"\g<1>%s\g<2>" % bicim(toplam), metin)
        if depo_sayisi:
            # DAR olmak zorunda. Ilk surum `\b[\d,]+ public repositories\b`
            # kullaniyordu ve README'deki "Calibrated on 30 public
            # repositories" cumlesini de degistirdi -- o sayi repo-vet'in
            # DISARIDAKI kalibrasyon kumesi, bu hesabin depo sayisi degil.
            # Bir tazeleme araci, guncelledigi seyden baskasina dokunmamali.
            metin = re.sub(r"\b[\d,]+( public repositories,)",
                           r"%d\g<1>" % depo_sayisi, metin)          # hero cumlesi
            metin = re.sub(r"(alt=\")[\d,]+( public repositories\")",
                           r"\g<1>%d\g<2>" % depo_sayisi, metin)     # rozet alt metni
            metin = re.sub(r"(\*\*)[\d,]+( public repositories\.\*\*)",
                           r"\g<1>%d\g<2>" % depo_sayisi, metin)     # TESTLER.md basligi
        if commit_sayisi:
            metin = re.sub(r"\b[\d,]+( commits\.)", r"%s\g<1>" % bicim(commit_sayisi), metin)
            metin = re.sub(r"\b[\d,]+( commits\b)(?!\.)", r"%s\g<1>" % bicim(commit_sayisi), metin)
        if yol is README:
            metin = re.sub(r"tests-[\d,%C]+_passing", "tests-%s_passing"
                           % bicim(toplam).replace(",", "%2C"), metin)
            metin = re.sub(r"[\d,]+ tests passing", "%s tests passing" % bicim(toplam), metin)
            metin = re.sub(r"[\d,]+ tests,", "%s tests," % bicim(toplam), metin)
            if depo_sayisi:
                metin = re.sub(r"public_repos-[\d,%C]+-", "public_repos-%d-"
                               % depo_sayisi, metin)
        yol.write_text(metin, encoding="utf-8", newline="\n")

    # hero.svg: her sayinin bir id'si var (`sayi-tests`, `sayi-repos`,
    # `sayi-commits`) ve cumle aria-label'da bir kez daha geciyor. Id'ler
    # tam da bunun icin eklendi: konuma ya da komsu etikete bakan bir regex,
    # grafik yeniden duzenlendigi gun sessizce yanlis hucreyi yazardi.
    hero = HERO.read_text(encoding="utf-8")
    hero = re.sub(r'(id="sayi-tests"[^>]*>)[\d,]+',
                  r"\g<1>%s" % bicim(toplam), hero)
    hero = re.sub(r"\b[\d,]+ tests\b", "%s tests" % bicim(toplam), hero)
    hero = re.sub(r">\d+ with suites<", ">%d with suites<" % suit, hero)
    if commit_sayisi:
        hero = re.sub(r"\b[\d,]+( commits\.)", r"%d\g<1>" % commit_sayisi, hero)
        hero = re.sub(r'(id="sayi-commits"[^>]*>)[\d,]+',
                      r"\g<1>%s" % bicim(commit_sayisi), hero)
    if depo_sayisi:
        hero = re.sub(r"\b[\d,]+( public repositories,)",
                      r"%d\g<1>" % depo_sayisi, hero)
        hero = re.sub(r'(id="sayi-repos"[^>]*>)[\d,]+',
                      r"\g<1>%d" % depo_sayisi, hero)
    HERO.write_text(hero, encoding="utf-8", newline="\n")
    return degisen, toplam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrol", action="store_true", help="yalnizca agsiz tutarlilik")
    ap.add_argument("--olc", action="store_true", help="kosu loglarindan yeniden olc")
    ap.add_argument("--yaz", action="store_true", help="olc ve olculeni her yere yaz")
    ap.add_argument("--tazele", action="store_true",
                    help="agsiz: meta-source.json'daki sayilari gorunen her yere yaz")
    ap.add_argument("--depo-sayisi", type=int, default=None,
                    help="herkese acik depo sayisi (verilmezse ellenmez)")
    ap.add_argument("--commit-sayisi", type=int, default=None,
                    help="manset commit sayisi (verilmezse ellenmez)")
    ap.add_argument("--depo", action="append", default=[],
                    help="yalnizca bu depo(lar)i olc; birden fazla kez verilebilir")
    ap.add_argument("--bekleme", type=float, default=1.0,
                    help="iki log indirmesi arasindaki saniye (varsayilan 1)")
    a = ap.parse_args()
    if not (a.kontrol or a.olc or a.yaz or a.tazele):
        a.kontrol = a.olc = True

    kaynak = yuk()
    kod = 0

    if a.olc or a.yaz:
        D = _denetim()
        if not D.GENIS:
            print("DEPO_JETONU yok: kosu loglari okunamaz, olcum atlandi.")
            if a.yaz:
                return 2
        else:
            try:
                sonuc = olc(kaynak, D, yalniz=set(a.depo) or None, bekleme=a.bekleme)
            except HizSiniri as e:
                print("GitHub hiz siniri (%s'da durdu). Olcum yarim; hicbir sey "
                      "yazilmadi. Bir sure sonra --bekleme degerini artirarak "
                      "ya da --depo ile parca parca tekrar dene." % e)
                return 2
            sapan = 0
            for ad, (yayin, olcum, not_) in sorted(sonuc.items()):
                if olcum is None:
                    print("  ?  %-28s %5d  (%s)" % (ad, yayin, not_))
                elif olcum != yayin:
                    print("  !  %-28s %5d -> %d" % (ad, yayin, olcum))
                    sapan += 1
                else:
                    print("  ok %-28s %5d" % (ad, yayin))
            if a.yaz:
                degisen, toplam = yaz(kaynak, sonuc, datetime.now(timezone.utc),
                                      depo_sayisi=a.depo_sayisi,
                                      commit_sayisi=a.commit_sayisi)
                print("\n%d depo guncellendi, toplam %s" % (len(degisen), bicim(toplam)))
                kaynak = yuk()
            elif sapan:
                kod = 1

    if a.tazele:
        # Olcum yok: meta-source.json dogru kabul edilir ve gorunen her yer
        # ona esitlenir. Yeni bir depo eklendiginde ya da bir sayi elle
        # duzeltildiginde kullanilan kip; yedi yeri elle guncellemek, yedi
        # yerin birinde unutmak demekti.
        _, toplam = yaz(kaynak, {}, datetime.now(timezone.utc),
                        depo_sayisi=a.depo_sayisi, commit_sayisi=a.commit_sayisi)
        print("Tazelendi: %s test, %d suit." % (bicim(toplam), len(sayilar(kaynak))))
        kaynak = yuk()
        a.kontrol = True

    if a.kontrol or a.yaz:
        sorunlar = kontrol(kaynak)
        if sorunlar:
            print("\nTUTARSIZ:")
            for s in sorunlar:
                print("  - " + s)
            kod = 1
        else:
            print("\nYayimlanan her yer ayni sayiyi soyluyor (%s test, %d suit)."
                  % (bicim(sum(sayilar(kaynak).values())), len(sayilar(kaynak))))
    return kod


if __name__ == "__main__":
    raise SystemExit(main())

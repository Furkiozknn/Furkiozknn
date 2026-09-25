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
  - (DEPO_JETONU varsa) acik Dependabot uyarisi var mi
  - (DEPO_JETONU varsa) yayimlanan test sayisi en yeni CI kosusunun
    yazdigi sayiyla ayni mi
  - en yeni etiketin release'i var mi, PyPI'a gitmis mi
  - 'active' diyen bir depo aylardir sessiz mi
  - alisilmis Pages adresi acik ama metadata bos mu
  - README'nin soyledigi kurulum komutu bugun calisir mi

Cikti: markdown rapor (stdout) + schema/denetim.json.

Cikis kodu **her zaman 0**. Baska bir deponun eksigi bu deponun CI'ini
kirmizi yakmaz; sinyal, acilan/guncellenen konudur.

Yalnizca standart kutuphane. Dependabot uyarilari GITHUB_TOKEN ile baska
bir depoda okunamaz; o yuzden varsayilan olarak kapsam disi -- goremedigi
bir seyi "temiz" diye yazmaktansa hic yazmiyor. DEPO_JETONU tanimliysa
(Dependabot alerts: Read) kapsama giriyor ve denetim.json bunu
`dependabot_checked` alaninda soyluyor.

    GITHUB_TOKEN=... python3 schema/denetim.py
"""

import base64
import hashlib
import io
import importlib.util
import json
import os
import re
import urllib.error
import urllib.request
import zipfile
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


def _politika_modulu():
    """schema/politika.py: is akisi ve tedarik zinciri kurallari (tek kaynak)."""
    yol = KOK / "schema" / "politika.py"
    spec = importlib.util.spec_from_file_location("ekosistem_politika", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _politika_modulu()


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


def _kapanmis_akislar(ad):
    """GitHub'in kendiliginden kapattigi zamanlanmis is akislari.

    Public bir depoda 60 gun hic hareket olmazsa GitHub zamanlanmis is
    akislarini kapatir (`disabled_inactivity`) ve kimseye haber vermez: akis
    listede durur, kirmizi yanmaz, sadece bir daha hic kosmaz. Kirmizi kosu
    kontrolu bunu goremez, cunku ortada kosu yok. Elle kapatilan
    (`disabled_manually`) bilincli bir karar sayilir ve raporlanmaz.
    """
    veri = _belki(f"{API}/repos/{OWNER}/{ad}/actions/workflows?per_page=100", {})
    return sorted(w.get("path", w.get("name", "?")).rsplit("/", 1)[-1]
                  for w in (veri or {}).get("workflows", [])
                  if w.get("state") == "disabled_inactivity")


GENIS = os.environ.get("DEPO_JETONU") or ""
UYARI_OKUNAN = []          # uyarilari gercekten okunabilen depolar
SAYI_OKUNAN = []           # yayimlanan test sayisi kosuya karsi GERCEKTEN karsilastirilan depolar
SAYI_BAKILAMADI = {}       # depo -> neden karsilastirilamadi
OKUNAMADI = []             # hiz siniri yuzunden hic olculemeyen depolar
KURULUM_ONBELLEK = {}      # paket adi -> PyPI surumleri (tur basina)
POLITIKA_BAKILAMADI = {}   # depo -> neden is akisi politikasina bakilamadi


def _uyarilar(ad):
    """Acik Dependabot uyarilari.

    GITHUB_TOKEN bunu baska bir depoda goremez; goremedigi bir seyi
    "temiz" diye yazmaktansa hic yazmamak dogru. DEPO_JETONU tanimliysa
    (Dependabot alerts: Read yetkisiyle) kapak aciliyor ve uyarilar da
    gunluk denetime giriyor. Jeton yoksa None doner -- "uyari yok" degil,
    "bakilamadi".
    """
    if not GENIS:
        return None
    istek = urllib.request.Request(
        f"{API}/repos/{OWNER}/{ad}/dependabot/alerts?state=open&per_page=100",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {GENIS}",
                 "User-Agent": "ekosistem-denetim"})
    try:
        with urllib.request.urlopen(istek, timeout=30) as r:
            veri = json.load(r)
        UYARI_OKUNAN.append(ad)
        return veri
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            # Deponun Dependabot'u kapali ya da jeton yetkisiz. Ikisi de
            # "uyari yok" degil; bulgu uretmez ama okundu da sayilmaz.
            return None
        raise
    except Exception:
        return None


LOG_TAVANI = 40 * 1024 * 1024        # bir kosu logu bundan buyukse indirilmez


def kalip(kaynak):
    """tests.source icindeki OLCULEBILIR kalip; yoksa None.

    Metadata kurali zaten "bir sayi ancak onu yazdiran kosu satiriyla
    birlikte yayimlanir" diyor. O satir backtick icinde duruyorsa makine de
    okuyabilir -- ve okuyabildigi seyi her gun yeniden olcebilir.

    Birlesik kaynaklar dogrulanamaz sayilir, yanlis sayilmaz: buradane'in
    sayisi "96 backend + 228 frontend", derin-kazi'ninki iki ayri kosu
    satirinin toplami. Tek bir satir tek bir sayiyi yazdirmiyorsa bu
    kontrolun soyleyecegi bir sey yok -- ve olmayan bir seyi soylemeye
    calisan bir kontrol, gurultuden baska bir sey uretmez.
    """
    hepsi = re.findall(r"`([^`]*\d[^`]*)`", kaynak or "")
    return hepsi[0] if len(hepsi) == 1 else None


def _log_metni(ad, dal, akislar):
    """Deponun en yeni basarili ci.yml kosusunun log metni.

    Yalnizca `ci.yml`: bir oyun deposunun yapi kosusunun logu on megabayt
    olabilir ve icinde test sayisi yoktur. Aranan sey testin kendisi.
    """
    if "ci.yml" not in akislar:
        return None
    veri = _belki(f"{API}/repos/{OWNER}/{ad}/actions/runs"
                  f"?branch={dal}&status=success&per_page=20", {})
    kosu = None
    for k in (veri or {}).get("workflow_runs", []):
        if k.get("path") == ".github/workflows/ci.yml":
            kosu = k
            break
    if kosu is None:
        return None
    istek = urllib.request.Request(
        f"{API}/repos/{OWNER}/{ad}/actions/runs/{kosu['id']}/logs",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {GENIS}",
                 "User-Agent": "ekosistem-denetim"})
    try:
        with urllib.request.urlopen(istek, timeout=90) as r:
            uzunluk = int(r.headers.get("Content-Length") or 0)
            if uzunluk > LOG_TAVANI:
                return None
            ham = r.read(LOG_TAVANI + 1)
        if len(ham) > LOG_TAVANI:
            return None
        parcalar = []
        with zipfile.ZipFile(io.BytesIO(ham)) as z:
            for x in z.namelist():
                if x.endswith(".txt"):
                    parcalar.append(z.read(x).decode("utf-8", "replace"))
        return "\n".join(parcalar)
    except Exception:
        return None


TURKCE = str.maketrans("\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc",
                       "cgiosuCGIOSU")


def sadelestir(s):
    """Turkce harfleri ASCII karsiliklarina indirger.

    Kosu `=== SONU\u00c7: 853 ge\u00e7ti, 0 hata ===` yaziyor; metadata dosyalari
    bilerek ASCII tutuldugu icin ayni satir orada `=== SONUC: 853 gecti,
    0 hata ===` olarak duruyor. Sayi ayni, yazim farkli. Esnek olmasi
    gereken taraf veri degil, eslestirici.
    """
    return (s or "").translate(TURKCE)


def sayiyi_bul(metin, desen):
    """Kalibi log metninde arar ve ilk sayiyi dondurur.

    Kalip duz metin olarak kacisliyor, sonra icindeki her sayi grubu bir
    yakalama grubuna cevriliyor: `=== 115/115 gecti ===` kalibi bugun 122
    yazan bir satiri da bulur, ve aradaki farki soyleyebilir.
    """
    desen, metin = sadelestir(desen), sadelestir(metin)
    kalip_re = re.sub(r"\d+", r"(\\d+)", re.escape(desen))
    m = re.search(kalip_re, metin or "")
    if not m or not m.groups():
        return None
    try:
        return int(m.group(1))
    except (ValueError, IndexError):
        return None


def sayilari_bul(metin, desen):
    """Kalibin log metnindeki BUTUN eslesmeleri.

    `sayiyi_bul` ilkini aliyor ve bir kosu tek is oldugu surece bu dogru.
    Ikinci bir is eklendigi anda ayni log birden fazla sayi tasiyor ve ilk
    eslesme yanlis olani olabiliyor. testler.py bu ayrimi bir tur once
    ogrendi; denetim ogrenmemisti, ve gunluk konuya yazan taraf o.
    Farkli sayilar esleiyorsa dogru cevap "belirsiz"dir, ilkini secmek degil.
    """
    desen, metin = sadelestir(desen), sadelestir(metin)
    kalip_re = re.sub(r"\d+", r"(\\d+)", re.escape(desen))
    return [int(m.group(1)) for m in re.finditer(kalip_re, metin or "") if m.groups()]


def _sayi_ayni_mi(ad, meta, kaynak):
    """Deponun kendi project-meta.json'u ile meta-source.json ayni sayiyi mi soyluyor.

    Iki dosya var ve ikisi de yayimlaniyor: hub sayfasi
    (`veri/projeler.json`) depolarin kendi project-meta.json'larindan
    toplaniyor, profil sayfasi meta-source.json'dan. Bu kontrol yokken
    ikisi sessizce ayristi: buradane depoda 334 profilde 347, turkce-ajanlar
    depoda 111 profilde 160 diyordu -- ve her iki tarafta da tutarlilik
    kontrolleri yesildi, cunku her biri yalniz KENDI tarafina bakiyordu.
    Iki yayimlanan sayinin birbirine bakmamasi, tam olarak bir sayinin
    yanlis olabilecegi yerdir.
    """
    a = (meta.get("tests") or {}).get("count")
    b = ((kaynak.get(ad) or {}).get("tests") or {}).get("count")
    if not isinstance(a, int) or not isinstance(b, int) or a == b:
        return []
    return ["project-meta.json %d diyor, meta-source.json %d -- hub sayfasi "
            "birincisini, profil sayfasi ikincisini yayimliyor" % (a, b)]


def _test_sayisi(ad, dal, meta, akislar):
    """Yayimlanan test sayisi, kosunun bugun yazdigi sayiyla ayni mi.

    Bu, sistemin kendi hakkinda soyledigi en yuklu cumle: profil sayfasi
    "4.496 test" diyor ve TESTLER.md her sayinin hangi kosu satirindan
    geldigini yaziyor. Ama o satir bir kez okunup elle yazilmisti; bir
    depoya yedi test eklenince sayi sessizce eskir ve iki kopya da ayni
    eski sayiyi gosterdigi icin kimse fark etmez. Burada sayinin kaynagina
    geri gidiliyor.
    """
    testler = meta.get("tests") if meta else None
    if not testler or not testler.get("count"):
        return None                       # yayimlanan sayi yok: karsilastiracak bir sey de yok
    if not GENIS:
        SAYI_BAKILAMADI[ad] = "DEPO_JETONU yok: kosu logu okunamaz"
        return None
    desen = kalip(testler.get("source"))
    if not desen:
        SAYI_BAKILAMADI[ad] = "birlesik kaynak: tek bir kalibi yok"
        return None
    metin = _log_metni(ad, dal, akislar)
    if metin is None:
        SAYI_BAKILAMADI[ad] = "okunabilir bir ci.yml kosu logu bulunamadi"
        return None
    hepsi = sayilari_bul(metin, desen)
    if not hepsi:
        return ("tests.source kalibi (%r) en yeni basarili CI kosusunda "
                "bulunamadi -- sayinin kaynagi degismis olabilir" % desen)
    ayri = sorted(set(hepsi))
    if len(ayri) > 1:
        # Ayni kalip birden fazla sayiyi esliyor (kosuda birden fazla is).
        # Ilkini secip "yayimlanan sayi yanlis" demek, bilinmeyeni bilinen
        # gibi sunmaktir -- ve bu tam olarak bir kez oldu:
        # mini-creative-toolkit'in logunda hem 135 hem 327 var.
        SAYI_BAKILAMADI[ad] = ("belirsiz: kalip %s sayilarini esliyor"
                               % ", ".join(str(x) for x in ayri))
        return None
    SAYI_OKUNAN.append(ad)
    if ayri[0] != testler["count"]:
        return ("tests.count %d diyor, en yeni CI kosusu %d yazdi"
                % (testler["count"], ayri[0]))
    return None


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


KURULUM = re.compile(
    r"(?:pip3?\s+install|pipx\s+install|uv\s+pip\s+install|uv\s+tool\s+install|uvx)"
    r"([^\n`]*)")

# Kendisinden SONRAKI sozcugu de yutan bayraklar: ardindan gelen sey bir
# dagitim adi degil, bir dosya ya da yol.
YUTAN = {"-r", "--requirement", "-e", "--editable", "-c", "--constraint",
         "--index-url", "-i", "--extra-index-url", "--find-links", "-f",
         "--python", "-p", "--with", "--index"}

# Bir dagitim adi olamayacak isaretler.
AD_DISI = ("+", ":", "/", "\\", "$", "<", ">", "=", "\"", "'")
DOSYA_SONU = (".txt", ".py", ".toml", ".cfg", ".lock", ".json", ".yaml", ".yml")


KOD_BLOGU = re.compile(r"```[^\n]*\n(.*?)```", re.S)


def kod_bloklari(metin):
    """Yalnizca ``` citleri arasindaki metin.

    Kontrolun sordugu soru "ziyaretcinin kopyalayip calistiracagi komut
    calisiyor mu". Bir cumlenin icinde gecen komut adi calistirilmak icin
    orada degil: "yayimlandiginda `pip install x` kisa yol olacak" demek,
    `pip install x` demek degildir.
    """
    return "\n".join(KOD_BLOGU.findall(metin or ""))


def kurulum_adlari(metin):
    """README'nin kod bloklarinda kurmayi soyledigi dagitim adlari.

    Yalnizca gercekten bir REGISTRY adi olanlar sayilir. `git+https://...`
    ile kurulum, `-e .`, `-r requirements.txt` ya da bir yol bir dagitim
    adi degildir ve PyPI'da aranmaz. `uvx --from <sey> <komut>` bicimi de
    disarida: oradaki dagitim `--from`un ardindaki sey, sondaki sozcuk ise
    calistirilan komutun adi -- ikisini karistirmak yanlis bulgu uretir.
    """
    adlar = set()
    for kuyruk in KURULUM.findall(kod_bloklari(metin)):
        parcalar = kuyruk.split()
        if "--from" in parcalar:
            continue
        i = 0
        while i < len(parcalar):
            s = parcalar[i]
            if s in YUTAN:
                i += 2
                continue
            if s.startswith("-"):
                i += 1
                continue
            aday = s.strip("`,;")
            if (aday and not aday.startswith(".")
                    and not any(k in aday for k in AD_DISI)
                    and not aday.lower().endswith(DOSYA_SONU)):
                adlar.add(aday)
            break
    return adlar


def _readme_metni(ad, dal):
    blob = _belki(f"{API}/repos/{OWNER}/{ad}/readme?ref={dal}")
    if not blob or "content" not in blob:
        return None
    return base64.b64decode(blob["content"]).decode("utf-8", "replace")


def _kurulum_calisiyor_mu(ad, dal, onbellek):
    """README'nin ilk soyledigi kurulum komutu bugun calisir mi.

    Bir ziyaretcinin carptigi ilk sey budur. `pip install filanca` diyen
    bir README, o dagitim PyPI'da yoksa projeyi bozuk gosterir -- ve bunu
    kimse depoyu okuyarak fark etmez, yalnizca komutu deneyen fark eder.
    Tam olarak bu oldu: prompt-template-manager `uv tool install ptm-cli`
    diyordu, ptm-cli yayimlanmamisti.
    """
    f = []
    metin = _readme_metni(ad, dal)
    if metin is None:
        return f
    for paket in sorted(kurulum_adlari(metin)):
        if paket not in onbellek:
            onbellek[paket] = _pypi_surumleri(paket)
        surumler = onbellek[paket]
        if surumler is not None and not surumler:
            f.append("README `%s` kurmayi soyluyor ama PyPI'da boyle bir "
                     "dagitim yok -- ziyaretcinin denedigi ilk komut duser"
                     % paket)
    return f


def _pypi_surumleri(paket):
    """PyPI'da yayimlanmis surumler. Jeton gerektirmez, herkese acik."""
    try:
        with urllib.request.urlopen(
                "https://pypi.org/pypi/%s/json" % paket, timeout=25) as r:
            return set(json.load(r).get("releases") or {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return set()                  # paket hic yayimlanmamis
        return None
    except Exception:
        return None


def _pypi_adi(ad, dal):
    """pyproject.toml'daki paket adi. Depo adiyla ayni olmak zorunda degil."""
    blob = _belki(f"{API}/repos/{OWNER}/{ad}/contents/pyproject.toml?ref={dal}")
    if not blob or "content" not in blob:
        return None
    metin = base64.b64decode(blob["content"]).decode("utf-8", "replace")
    m = re.search(r'^\s*name\s*=\s*"([^"]+)"', metin, re.M)
    return m.group(1) if m else None


def _surum_zinciri(ad, dal, akislar):
    """Etiket atildi ama zincirin geri kalani tamamlanmadi mi.

    Iki kopuk arasak yeter, ikisi de sessizce olur:
      - en yeni etiketin GitHub Release'i yok (etiket atildi, yayin yok)
      - PyPI'a yayin yapan bir depoda etiket var ama PyPI'da o surum yok
        (yayin kosusu dustu ya da hic kosmadi)

    Eski ara etiketlerin release'i olmamasi normaldir; yalnizca EN YENI
    etikete bakiliyor, yoksa her gun ayni on satir yazilirdi.
    """
    f = []
    etiketler = _belki(f"{API}/repos/{OWNER}/{ad}/tags?per_page=10", [])
    if not etiketler:
        return f
    yeni = etiketler[0]["name"]
    releaseler = _belki(f"{API}/repos/{OWNER}/{ad}/releases?per_page=20", []) or []
    yayinda = {r["tag_name"] for r in releaseler if not r.get("draft")}
    if yeni not in yayinda:
        f.append("en yeni etiket %s var ama GitHub Release'i yok" % yeni)

    if "yayinla.yml" in akislar:
        paket = _pypi_adi(ad, dal)
        if paket:
            surumler = _pypi_surumleri(paket)
            beklenen = yeni.lstrip("v")
            if surumler is not None and beklenen not in surumler:
                f.append("etiket %s atilmis ama PyPI'da %s %s yok"
                         % (yeni, paket, beklenen))
    return f


def _politika_dosyalari(ad, dal):
    """Politikanin baktigi dosyalar, tek agac istegi + gereken icerikler.

    uv.lock icerigi okunmaz: kural yalnizca varligina bakiyor, ve buyuk bir
    kilidi her gun indirmenin karsiligi yok. Cargo.lock ve package-lock.json
    okunur, cunku "hic bagimliligi yok" istisnasi icerige bakiyor.
    """
    agac = _belki(f"{API}/repos/{OWNER}/{ad}/git/trees/{dal}?recursive=1")
    if not agac or agac.get("truncated"):
        return None
    dosyalar = {}
    for g in agac.get("tree") or []:
        yol = g.get("path", "")
        if g.get("type") != "blob" or "node_modules/" in yol:
            continue
        akis = yol.startswith(".github/workflows/") and yol.endswith((".yml", ".yaml"))
        db = yol in (".github/dependabot.yml", ".github/dependabot.yaml")
        kilit = yol.rsplit("/", 1)[-1] in P.KILIT_EKOSISTEM
        if not (akis or db or kilit):
            continue
        if yol.endswith("uv.lock"):
            dosyalar[yol] = None
            continue
        blob = _belki(f"{API}/repos/{OWNER}/{ad}/contents/{yol}?ref={dal}")
        if not blob or "content" not in blob:
            return None
        dosyalar[yol] = base64.b64decode(blob["content"]).decode("utf-8", "replace")
    return dosyalar


def _politika(ad, dal):
    """FAIL'ler tek tek; WARN'lar depo basina tek satirda sayilir.

    Ilk envanterde 27 deponun toplam 178 WARN satiri vardi. Hepsi konuya
    tek tek yazilsa, bir FAIL o kalabalikta kaybolurdu.
    """
    if P.yaml_yok():
        POLITIKA_BAKILAMADI[ad] = "PyYAML yok"
        return []
    dosyalar = _politika_dosyalari(ad, dal)
    if dosyalar is None:
        POLITIKA_BAKILAMADI[ad] = "dosyalar okunamadi"
        return []
    bulgular = P.depo_bulgulari(dosyalar)
    cikti = ["FAIL %s" % m for s, _, m in bulgular if s == P.FAIL]
    uyarilar = {}
    for s, k, _ in bulgular:
        if s == P.WARN:
            uyarilar[k] = uyarilar.get(k, 0) + 1
    if uyarilar:
        cikti.append("WARN " + ", ".join("%s x%d" % (P.KURAL_ADI.get(k, k), n)
                                         for k, n in sorted(uyarilar.items())))
    return cikti


def _bayat_mi(r, meta, gun=180):
    """'active' diyen ama aylardir dokunulmamis depo.

    Bir portfoyu sessizce eskiten sey budur: durum alani 'active' kalir,
    okuyan kisi surmekte olan bir is sanir. Arsivlemek ya da 'prototype'
    demek bir karardir -- burada yalnizca fark bildiriliyor.
    """
    if r["archived"] or not meta or meta.get("status") != "active":
        return None
    try:
        son = datetime.strptime(r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except Exception:
        return None
    gecen = (datetime.now(timezone.utc) - son).days
    if gecen > gun:
        return "status 'active' ama son push %d gun once" % gecen
    return None


def _gizli_pages(ad, meta):
    """Yayina alinmis ama metadata'ya girmemis Pages sitesi.

    Oyunlardan biri 'sayfaya_yayinla' kutusuyla yayina cikinca adres
    dogar ama kimse metadata'ya yazmaz. Alisilmis adrese bakip soylemek
    bir istek; unutulmus bir yayin ise gorunmez bir kazanc.
    """
    if not meta or meta.get("homepage"):
        return None
    url = "https://%s.github.io/%s/" % (OWNER.lower(), ad)
    kod = _canli_mi(url)
    if kod == 200:
        return "Pages yayinda (%s) ama metadata homepage bos" % url
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
        for m in _sayi_ayni_mi(ad, meta, kaynak):
            bulgular.append(("olcum", m))

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

    uyari = _uyarilar(ad)
    if uyari:
        ciddi = [u for u in uyari
                 if (u.get("security_advisory") or {}).get("severity")
                 in ("high", "critical")]
        bulgular.append(("guvenlik", "%d acik Dependabot uyarisi%s"
                         % (len(uyari),
                            " (%d high/critical)" % len(ciddi) if ciddi else "")))

    bayat = _bayat_mi(r, meta)
    if bayat:
        bulgular.append(("vitrin", bayat))

    if r["archived"]:
        # Arsivli depoda is akisi kosmaz; kirmizi aramak yanlis alarm uretir.
        return bulgular, iskelet, meta

    gizli = _gizli_pages(ad, meta)
    if gizli:
        bulgular.append(("baglanti", gizli))

    for m in _surum_zinciri(ad, dal, akislar):
        bulgular.append(("surum", m))

    for m in _politika(ad, dal):
        bulgular.append(("politika", m))

    for m in _kurulum_calisiyor_mu(ad, dal, KURULUM_ONBELLEK):
        bulgular.append(("vitrin", m))

    sapma = _test_sayisi(ad, dal, meta, akislar)
    if sapma:
        bulgular.append(("olcum", sapma))
    if not akislar:
        bulgular.append(("ci", "hic is akisi yok"))
    else:
        for w in _kirmizi_kosular(ad, dal, akislar):
            bulgular.append(("ci", "son kosu kirmizi: %s" % w))
        for w in _kapanmis_akislar(ad):
            bulgular.append(("ci", "GitHub 60 gun hareketsizlik yuzunden kapatmis: %s "
                                   "(Actions -> is akisi -> Enable workflow)" % w))
    return bulgular, iskelet, meta


def _profil_sayilari(metalar, depo_sayisi):
    """Profil sayfasinin manset sayilari hala dogru mu.

    Profil "24 public repositories, 4,496 tests" diyor ve TESTLER.md o
    sayinin nereden geldigini yaziyor. Bir depoya test eklenince ya da yeni
    bir depo acilinca bu sayilar sessizce yanlis olur -- ve yanlis bir sayi,
    hic sayi olmamasindan kotudur. Kaynak TESTLER.md basligi: sayinin tek
    bir kanonik yeri olsun diye.
    """
    f = []
    testler = KOK / "TESTLER.md"
    readme = KOK / "README.md"
    if not testler.is_file() or not readme.is_file():
        return f

    m = re.search(r"#\s*Where the ([\d,]+) comes from", testler.read_text(encoding="utf-8"))
    if not m:
        f.append(("Furkiozknn", "vitrin", "TESTLER.md basligindaki sayi okunamadi"))
        return f
    iddia = int(m.group(1).replace(",", ""))

    # Arsivli depo profilde sayilmiyor (TESTLER.md bunu acikca yaziyor).
    toplam = sum(meta["tests"]["count"] for r, meta in metalar.values()
                 if meta.get("tests") and not r["archived"])
    if toplam != iddia:
        f.append(("Furkiozknn", "vitrin",
                  "TESTLER.md %d test diyor, metadata toplami %d" % (iddia, toplam)))

    metin = readme.read_text(encoding="utf-8")

    # Tablodaki her satirin kendi sayisi da tutmali. Toplam dogru ama
    # satirlar yanlis olabilir -- iki depo birbirini gotururse toplam
    # farki yutar, satira bakan okuyucu yanlis sayiyi gorur.
    satirlar = {}
    for s in metin.splitlines():
        if not s.startswith("|") or "github.com/" not in s:
            continue
        d = re.search(r"\]\(https://github\.com/%s/([A-Za-z0-9._-]+)\)" % OWNER, s)
        if d:
            satirlar[d.group(1)] = s
    for ad, (r, meta) in sorted(metalar.items()):
        if r["archived"] or not meta.get("tests"):
            continue
        s = satirlar.get(ad)
        if s is None:
            f.append(("Furkiozknn", "vitrin",
                      "README tablosunda %s satiri yok (suiti var)" % ad))
            continue
        sayilar = re.findall(r"`([\d,]+)`", s)
        if not sayilar:
            continue
        yazan = int(sayilar[-1].replace(",", ""))
        if yazan != meta["tests"]["count"]:
            f.append(("Furkiozknn", "vitrin",
                      "README tablosunda %s icin %d yaziyor, metadata %d diyor"
                      % (ad, yazan, meta["tests"]["count"])))

    if m.group(1) not in metin:
        f.append(("Furkiozknn", "vitrin",
                  "README, TESTLER.md'deki %s sayisini hic gecirmiyor" % m.group(1)))
    if not re.search(r"\b%d public repositories\b" % depo_sayisi, metin):
        f.append(("Furkiozknn", "vitrin",
                  "README'deki public repo sayisi %d ile uyusmuyor" % depo_sayisi))
    return f


BASLIK = {
    "kayit": "Metadata katmanina girmemis depo",
    "metadata": "project-meta.json eksik",
    "ayrisma": "Metadata canli gercekle ayrismis",
    "belge": "Temel belge eksik",
    "vitrin": "Vitrin alani bos",
    "ci": "CI",
    "baglanti": "Yayindaki adres cevap vermiyor",
    "guvenlik": "Acik guvenlik uyarisi",
    "olcum": "Yayimlanan sayi kosunun yazdigiyla ayni degil",
    "surum": "Surum zinciri yarim kalmis",
    "politika": "Is akisi ve tedarik zinciri politikasi (schema/politika.py)",
}
SIRA = ["metadata", "guvenlik", "olcum", "kayit", "ci", "surum", "politika",
        "baglanti", "ayrisma", "belge", "vitrin"]


def _okunamayan_satiri():
    """Hiz siniri yuzunden hic olculemeyen depolar.

    Rapor bunlari yazmazsa "28 depo, bulgu yok" cumlesi, yarisina hic
    bakilmamis bir kosuda da ayni sekilde yazilir.
    """
    if not OKUNAMADI:
        return ""
    return ("GitHub hiz siniri: %d depo hic olculemedi (%s). Bunlar hakkinda "
            "bu kosunun soyleyecegi bir sey yok." % (len(OKUNAMADI), ", ".join(OKUNAMADI[:8])
            + (" ..." if len(OKUNAMADI) > 8 else "")))


def _kapsam_satiri():
    """Yayimlanan test sayilarindan kaci gercekten kosuya karsi bakildi.

    "Bakilamadi" ile "temiz" ayni cumleye giremez. Bu kontrol, sistemin
    kendi hakkinda soyledigi en yuklu cumleyi -- profil sayfasindaki toplam
    test sayisini -- kosunun bugun yazdigi satira geri baglayan kontrol; ve
    DEPO_JETONU olmadan sessizce atlaniyordu, yani gunluk denetim aylarca
    "temiz" yazarken o cumleye hic bakmamis olabilirdi. Simdi sayiyor.
    """
    okunan, bakilamayan = len(SAYI_OKUNAN), len(SAYI_BAKILAMADI)
    if not okunan and not bakilamayan:
        return ""
    if not bakilamayan:
        return "Yayimlanan test sayisi %d depoda kosuya karsi dogrulandi." % okunan
    nedenler = {}
    for ad, neden in SAYI_BAKILAMADI.items():
        nedenler.setdefault(neden, []).append(ad)
    parca = "; ".join("%d: %s" % (len(v), k) for k, v in sorted(nedenler.items()))
    return ("Yayimlanan test sayisi %d depoda kosuya karsi dogrulandi, "
            "%d depoda **bakilamadi** (%s). Bakilamayan bir sayi temiz degildir."
            % (okunan, bakilamayan, parca))


def _politika_satiri():
    """Politikasina bakilamayan depo "temiz" sayilmaz; sayisi yazilir."""
    if not POLITIKA_BAKILAMADI:
        return ""
    nedenler = {}
    for ad, neden in POLITIKA_BAKILAMADI.items():
        nedenler.setdefault(neden, []).append(ad)
    return ("Is akisi politikasina %d depoda **bakilamadi** (%s)."
            % (len(POLITIKA_BAKILAMADI),
               "; ".join("%d: %s" % (len(v), k) for k, v in sorted(nedenler.items()))))


def _rapor(bulgular, iskeletler, depo_sayisi):
    ustbilgi = [x for x in (_okunamayan_satiri(), _kapsam_satiri(), _politika_satiri()) if x]
    if not bulgular:
        metin = "Denetim temiz: %d depo, bulgu yok." % (depo_sayisi - len(OKUNAMADI))
        return metin + ("\n\n" + "\n\n".join(ustbilgi) if ustbilgi else "")
    s = ["**%d depoda %d bulgu.**" % (len({b[0] for b in bulgular}), len(bulgular)), ""]
    for x in ustbilgi:
        s.extend([x, ""])
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
    # Depo listesi olmadan denetim diye bir sey yok, yani bu olumcul -- ama
    # olumcul olmasi yigin izi basmasi anlamina gelmiyor. Ayrica nedeni
    # soylemek gerekiyor: `_get` GITHUB_TOKEN/GH_TOKEN okuyor, kosu loglarini
    # okuyan taraf DEPO_JETONU; yalnizca ikincisi tanimliyken istekler
    # KIMLIKSIZ gidiyor ve saatte 60'ta duruyor. CI'da GITHUB_TOKEN hazir
    # oldugu icin orada hic gorulmez, yerelde hemen gorulur.
    try:
        depolar = [r for r in D._repos() if not r.get("fork")]
    except D.HizSiniri:
        kimlikli = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
        print("GitHub hiz siniri: depo listesi alinamadi, denetim kosulamadi.")
        print("Istekler %s gidiyor%s." % (
            "kimlikli" if kimlikli else "KIMLIKSIZ",
            "" if kimlikli else " -- GITHUB_TOKEN ya da GH_TOKEN tanimlayin "
                               "(DEPO_JETONU yalniz kosu loglari icin kullaniliyor)"))
        return 2

    bulgular, iskeletler, metalar = [], {}, {}
    KURULUM_ONBELLEK.clear()
    SAYI_OKUNAN.clear()
    SAYI_BAKILAMADI.clear()
    OKUNAMADI.clear()
    POLITIKA_BAKILAMADI.clear()
    for r in sorted(depolar, key=lambda x: x["name"].lower()):
        # Hiz siniri "bakilamadi" demek, "temiz" degil -- ve kesinlikle
        # "butun denetimi dusur" degil. Bu tur bir yigin izi yuzunden
        # gunluk denetim hicbir sey yazamadan oluyordu.
        try:
            alt, iskelet, meta = _depoyu_olc(r, kaynak)
        except D.HizSiniri:
            OKUNAMADI.append(r["name"])
            continue
        if meta is not None:
            metalar[r["name"]] = (r, meta)
        for tur, mesaj in alt:
            bulgular.append((r["name"], tur, mesaj))
        if iskelet is not None:
            iskeletler[r["name"]] = iskelet

    bulgular.extend(_profil_sayilari(metalar, len(depolar)))

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
        "dependabot_checked": len(UYARI_OKUNAN),
        "test_counts_verified": len(SAYI_OKUNAN),
        "repos_unreadable": list(OKUNAMADI),
        "test_counts_unverified": dict(sorted(SAYI_BAKILAMADI.items())),
        "policy_unchecked": dict(sorted(POLITIKA_BAKILAMADI.items())),
        "note": "Bulgular olculmustur; hicbiri otomatik duzeltilmez."
                + ("" if UYARI_OKUNAN else " Dependabot uyarilari kapsam disi: "
                   "DEPO_JETONU tanimli degil ya da yetkisiz; GITHUB_TOKEN "
                   "onlari baska bir depoda goremiyor."),
        "findings": [{"repo": a, "kind": b, "message": c} for a, b, c in bulgular],
        "onboarding_skeletons": iskeletler,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print(metin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

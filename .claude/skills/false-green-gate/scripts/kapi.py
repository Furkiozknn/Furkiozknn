#!/usr/bin/env python3
"""false-green-gate: "komut 0 dondu" ile "is gercekten oldu"yu ayiran kapi.

Bir test kosucusunun ya da medya aracinin cikis kodu tek basina kanit
degil. Bu betik kosunun BIRAKTIGI kaniti okur (JUnit XML, Playwright JSON
raporu, Godot gunlugu, medya dosyasi, workflow/betik metni, git farki) ve
yesilin gercek olup olmadigina karar verir.

    kapi.py junit      RAPOR.xml... --taban N [--izinli-skip K]
    kapi.py playwright RAPOR.json   --taban N [--izinli-skip K] [--izinli-beklenen-hata K]
    kapi.py godot      GUNLUK       --taban N
    kapi.py medya      DOSYA [--min-sure S] [--video] [--ses] [--tam-cozum] [--siyah] [--sessiz]
    kapi.py komut      DOSYA...
    kapi.py fark       [--taban-ref REF]

Cikis: 0 = PASS, 1 = FAIL (en az bir FAIL bulgusu), 2 = kullanim hatasi.
Her kosu son satirda tek satirlik JSON kanit basar.

Yalnizca standart kutuphane; medya kipi ffprobe/ffmpeg ister.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


class Sonuc:
    def __init__(self, kip):
        self.kip = kip
        self.bulgular = []
        self.olcum = {}

    def fail(self, kod, mesaj):
        self.bulgular.append({"kod": kod, "seviye": "FAIL", "mesaj": mesaj})

    def warn(self, kod, mesaj):
        self.bulgular.append({"kod": kod, "seviye": "WARN", "mesaj": mesaj})

    def bitir(self):
        basarisiz = any(b["seviye"] == "FAIL" for b in self.bulgular)
        for b in self.bulgular:
            print(f"{b['seviye']} {b['kod']}: {b['mesaj']}", file=sys.stderr)
        karar = "FAIL" if basarisiz else "PASS"
        print(json.dumps({"kapi": self.kip, "sonuc": karar, "olcum": self.olcum,
                          "bulgular": self.bulgular}, ensure_ascii=False, sort_keys=True))
        return 1 if basarisiz else 0


def _sayilar_ortak(s, toplam, kosan, basarisiz, atlanan, taban, izinli_skip):
    s.olcum.update({"toplam": toplam, "kosan": kosan, "basarisiz": basarisiz,
                    "atlanan": atlanan, "taban": taban})
    if kosan == 0:
        s.fail("FG-01", f"hic test kosmadi (toplam {toplam}, atlanan {atlanan})")
    elif kosan < taban:
        s.fail("FG-02", f"{kosan} test kostu, taban {taban}; bir bolum atlanmis ya da toplanmamis olabilir")
    if basarisiz:
        s.fail("FG-03", f"{basarisiz} test basarisiz")
    if atlanan > izinli_skip:
        s.fail("FG-04", f"{atlanan} test atlandi, izin verilen {izinli_skip}")


# --- junit ---------------------------------------------------------------

def junit(args):
    s = Sonuc("junit")
    toplam = basarisiz = atlanan = yeniden = 0
    for yol in args.raporlar:
        try:
            kok = ET.parse(yol).getroot()
        except (OSError, ET.ParseError) as e:
            s.fail("FG-18", f"{yol}: JUnit raporu okunamadi ({e.__class__.__name__}); okunamayan rapor kanit degildir")
            continue
        vakalar = list(kok.iter("testcase"))
        if kok.tag not in ("testsuites", "testsuite"):
            s.fail("FG-18", f"{yol}: kok eleman '{kok.tag}', JUnit degil")
            continue
        for v in vakalar:
            toplam += 1
            if v.find("skipped") is not None:
                atlanan += 1
            elif v.find("failure") is not None or v.find("error") is not None:
                basarisiz += 1
            # pytest-rerunfailures <rerun*>, surefire <flaky*>: sonunda gecse de kararsiz
            if any(c.tag.startswith(("rerun", "flaky")) for c in v):
                yeniden += 1
    kosan = toplam - atlanan
    _sayilar_ortak(s, toplam, kosan, basarisiz, atlanan, args.taban, args.izinli_skip)
    s.olcum["yeniden_kosulan"] = yeniden
    if yeniden:
        s.fail("FG-05", f"{yeniden} test ancak yeniden kosunca gecti (flaky); retry yesili yesil degildir")
    return s.bitir()


# --- playwright ----------------------------------------------------------

def _pw_testleri(suite):
    for spec in suite.get("specs", []):
        for t in spec.get("tests", []):
            yield spec, t
    for alt in suite.get("suites", []) or []:
        yield from _pw_testleri(alt)


def playwright(args):
    s = Sonuc("playwright")
    try:
        with open(args.rapor, encoding="utf-8") as f:
            rapor = json.load(f)
        st = rapor["stats"]
        beklenen, beklenmeyen = int(st["expected"]), int(st["unexpected"])
        flaky, atlanan = int(st["flaky"]), int(st["skipped"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        s.fail("FG-18", f"{args.rapor}: Playwright JSON raporu okunamadi ({e.__class__.__name__})")
        return s.bitir()
    toplam = beklenen + beklenmeyen + flaky + atlanan
    kosan = beklenen + beklenmeyen + flaky
    _sayilar_ortak(s, toplam, kosan, beklenmeyen, atlanan, args.taban, args.izinli_skip)
    s.olcum["flaky"] = flaky
    if flaky:
        s.fail("FG-05", f"{flaky} test ancak retry ile gecti (flaky)")
    if rapor.get("errors"):
        s.fail("FG-07", f"raporda {len(rapor['errors'])} test-disi hata var (config/global setup)")
    # test.fail(): beklenen durum 'failed'; test basarisiz olunca 'expected' sayilir.
    ters = [spec.get("title", "?") for suite in rapor.get("suites", [])
            for spec, t in _pw_testleri(suite)
            if t.get("expectedStatus") not in (None, "passed", "skipped")]
    s.olcum["beklenen_hata"] = len(ters)
    if len(ters) > args.izinli_beklenen_hata:
        s.fail("FG-06", f"{len(ters)} test basarisiz olmasi BEKLENEREK isaretli (test.fail): {', '.join(ters[:5])}")
    return s.bitir()


# --- godot ---------------------------------------------------------------

GODOT_SONUC = re.compile(r"^=== ([0-9]+)/([0-9]+) gecti ===$", re.M)
GODOT_HATA = re.compile(r"SCRIPT ERROR|Parse Error")


def godot(args):
    s = Sonuc("godot")
    try:
        with open(args.gunluk, encoding="utf-8", errors="replace") as f:
            metin = f.read()
    except OSError as e:
        s.fail("FG-18", f"gunluk okunamadi: {e}")
        return s.bitir()
    hatalar = [satir for satir in metin.splitlines() if GODOT_HATA.search(satir)]
    if hatalar:
        s.fail("FG-09", f"gunlukte {len(hatalar)} betik hatasi var; bir test bolumu sessizce yarida kalmis olabilir: {hatalar[0][:120]}")
    sonuclar = GODOT_SONUC.findall(metin)
    if not sonuclar:
        s.fail("FG-08", "'=== G/T gecti ===' satiri yok; takim sonuna kadar kosmadi")
        return s.bitir()
    gecen, toplam = (int(x) for x in sonuclar[-1])
    _sayilar_ortak(s, toplam, gecen, toplam - gecen, 0, args.taban, 0)
    return s.bitir()


# --- medya ---------------------------------------------------------------

DECODE_HATA = re.compile(r"File ended prematurely|Invalid data found|error while decoding|"
                         r"partial file|moov atom not found|Truncat|corrupt", re.I)


def _calistir(argv, zaman=600):
    return subprocess.run(argv, capture_output=True, text=True, timeout=zaman,
                          stdin=subprocess.DEVNULL)


def _guvenli_yol(yol):
    # Mutlak yol + 'file:' oneki: '-' ile baslayan ad secenek, 'concat:' /
    # 'http:' gibi bir onek protokol sanilmaz; -protocol_whitelist file da
    # dosyanin icinden (HLS/concat listesi) baska kaynak acilmasini engeller.
    return os.path.abspath(yol)


def medya(args):
    s = Sonuc("medya")
    yol = _guvenli_yol(args.dosya)
    if not os.path.isfile(yol) or os.path.getsize(yol) == 0:
        s.fail("FG-10", f"dosya yok ya da bos: {args.dosya}")
        return s.bitir()
    s.olcum["boyut"] = os.path.getsize(yol)
    try:
        p = _calistir(["ffprobe", "-v", "error", "-protocol_whitelist", "file",
                       "-show_format", "-show_streams", "-of", "json", "file:" + yol], 120)
    except FileNotFoundError:
        s.fail("FG-10", "ffprobe bulunamadi; dogrulanamayan medya PASS sayilmaz")
        return s.bitir()
    try:
        bilgi = json.loads(p.stdout or "{}")
    except ValueError:
        bilgi = {}
    akislar = bilgi.get("streams", [])
    if p.returncode != 0 or not akislar:
        s.fail("FG-10", f"ffprobe akis bulamadi (cikis {p.returncode}): {p.stderr.strip()[:160]}")
        return s.bitir()
    video = [a for a in akislar if a.get("codec_type") == "video"
             and not a.get("disposition", {}).get("attached_pic")]
    ses = [a for a in akislar if a.get("codec_type") == "audio"]
    try:
        sure = float(bilgi.get("format", {}).get("duration", 0) or 0)
    except ValueError:
        sure = 0.0
    s.olcum.update({"sure": sure, "video_akis": len(video), "ses_akis": len(ses),
                    "bicim": bilgi.get("format", {}).get("format_name")})
    if video:
        v = video[0]
        s.olcum.update({"genislik": v.get("width"), "yukseklik": v.get("height"),
                        "video_codec": v.get("codec_name")})
    if ses:
        s.olcum["ses_codec"] = ses[0].get("codec_name")
    if args.video and not video:
        s.fail("FG-11", "video akisi yok")
    if args.ses and not ses:
        s.fail("FG-11", "ses akisi yok")
    if sure < args.min_sure:
        s.fail("FG-11", f"sure {sure:.3f}s, en az {args.min_sure}s bekleniyordu")
    if args.tam_cozum:
        # Baslik yalan soyleyebilir (yarisi kesik faststart MP4 hala tam sureyi
        # bildirir); yalnizca tam cozme ve stderr gercegi gosterir. -xerror yetmez:
        # kesik MKV onunla bile 0 doner.
        p = _calistir(["ffmpeg", "-nostdin", "-v", "error", "-protocol_whitelist", "file",
                       "-i", "file:" + yol, "-f", "null", "-"])
        hatalar = [x for x in p.stderr.splitlines() if x.strip()]
        s.olcum["cozme_hata_satiri"] = len(hatalar)
        if p.returncode != 0 or any(DECODE_HATA.search(x) for x in hatalar):
            s.fail("FG-12", f"tam cozmede hata (cikis {p.returncode}): {(hatalar or ['?'])[0][:160]}")
        if video:
            q = _calistir(["ffprobe", "-v", "error", "-protocol_whitelist", "file",
                           "-select_streams", "v:0", "-count_frames",
                           "-show_entries", "stream=nb_frames,nb_read_frames",
                           "-of", "json", "file:" + yol])
            try:
                st = json.loads(q.stdout)["streams"][0]
                baslik, okunan = int(st.get("nb_frames") or 0), int(st.get("nb_read_frames") or 0)
            except (ValueError, KeyError, IndexError):
                baslik = okunan = 0
            s.olcum.update({"kare_baslik": baslik, "kare_okunan": okunan})
            if baslik and okunan < 0.95 * baslik:
                s.fail("FG-13", f"baslik {baslik} kare diyor, cozulen {okunan}; dosya kesik")
            if okunan == 1 and sure > 1:
                s.fail("FG-13", "cikti tek kareden ibaret")
    if args.siyah and video and sure > 0:
        p = _calistir(["ffmpeg", "-nostdin", "-v", "info", "-protocol_whitelist", "file",
                       "-i", "file:" + yol, "-map", "0:v:0", "-vf", "blackdetect=d=0.1:pix_th=0.10",
                       "-an", "-f", "null", "-"])
        siyah = sum(float(x) for x in re.findall(r"black_duration:([0-9.]+)", p.stderr))
        s.olcum["siyah_sure"] = round(siyah, 3)
        if siyah >= 0.95 * sure:
            s.fail("FG-14", f"video neredeyse tamamen siyah ({siyah:.2f}/{sure:.2f}s)")
    if args.sessiz and ses and sure > 0:
        p = _calistir(["ffmpeg", "-nostdin", "-v", "info", "-protocol_whitelist", "file",
                       "-i", "file:" + yol, "-map", "0:a:0", "-af", "volumedetect",
                       "-vn", "-f", "null", "-"])
        m = re.search(r"max_volume: (-?[0-9.]+|-inf) dB", p.stderr)
        tepe = float("-inf") if not m or m.group(1) == "-inf" else float(m.group(1))
        s.olcum["ses_tepe_db"] = None if tepe == float("-inf") else tepe
        if tepe < -60:
            s.fail("FG-14", f"ses sessiz (tepe {m.group(1) if m else '?'} dB)")
    return s.bitir()


# --- komut (workflow / betik metni) --------------------------------------

KOSUCU = r"(?:playwright\s+test|vitest|jest|pytest|npm\s+(?:run\s+)?test|npx\s+playwright\s+test|godot\b[^\n]*--headless|python3?\s+-m\s+(?:pytest|unittest))"
KOMUT_KURALLARI = [
    ("FG-15", "FAIL", re.compile(r"--pass-with-no-tests|--passWithNoTests"),
     "sifir testle yesil donmeye izin veren bayrak"),
    ("FG-16", "FAIL", re.compile(KOSUCU + r"[^\n]*(?:\|\|\s*(?:true|:|exit\s+0)\b|;\s*true\s*$)", re.M),
     "test komutunun hatasi yutuluyor (|| true)"),
    ("FG-17", "FAIL", re.compile(r"(?:playwright\s+test|vitest|jest)[^\n]*(?:--update-snapshots|\s-u\b)"),
     "CI'da snapshot guncelleme: karsilastirma yerine yeni taban yaziliyor"),
    ("FG-19", "WARN", re.compile(r"--last-failed|--only-changed|--lf\b"),
     "yalnizca bir alt kume kosuluyor; PR hizlandirmasi olabilir ama tam kosunun yerine gecmez"),
]


def komut(args):
    s = Sonuc("komut")
    for yol in args.dosyalar:
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError as e:
            s.fail("FG-18", f"{yol}: okunamadi ({e})")
            continue
        for kod, seviye, desen, aciklama in KOMUT_KURALLARI:
            for m in desen.finditer(metin):
                satir = metin.count("\n", 0, m.start()) + 1
                (s.fail if seviye == "FAIL" else s.warn)(kod, f"{yol}:{satir}: {aciklama}")
        if re.search(r"continue-on-error:\s*true", metin) and re.search(KOSUCU, metin):
            s.warn("FG-20", f"{yol}: continue-on-error var; test adiminda ise kirmizi gizlenir")
    return s.bitir()


# --- fark (git) ----------------------------------------------------------

ATLAMA = re.compile(r"\b(?:test|it|describe)\.(?:skip|fixme|fail|only)\s*\(|\b(?:xit|xdescribe|fit|fdescribe)\s*\("
                    r"|@pytest\.mark\.(?:skip|skipif|xfail)\b|\bpytest\.(?:skip|xfail)\s*\(|@unittest\.(?:skip|expectedFailure)\b"
                    r"|\bself\.skipTest\s*\(")


def fark(args):
    s = Sonuc("fark")
    try:
        p = _calistir(["git", "diff", "--unified=0", "--no-color", args.taban_ref, "--"], 120)
    except FileNotFoundError:
        s.fail("FG-18", "git bulunamadi")
        return s.bitir()
    if p.returncode != 0:
        s.fail("FG-18", f"git diff basarisiz: {p.stderr.strip()[:160]}")
        return s.bitir()
    dosya, eklenen = "?", 0
    for satir in p.stdout.splitlines():
        if satir.startswith("+++ "):
            dosya = satir[6:] if satir.startswith("+++ b/") else satir[4:]
        elif satir.startswith("+") and not satir.startswith("+++"):
            if ATLAMA.search(satir):
                eklenen += 1
                s.fail("FG-21", f"{dosya}: yeni atlama/odak isareti eklendi: {satir[1:].strip()[:120]}")
        if re.match(r"^\+\+\+ b/.*(?:-snapshots/|__snapshots__/)", satir):
            s.warn("FG-22", f"{dosya}: snapshot tabani degisti; gorsel fark insan tarafindan incelenmeli")
    s.olcum["yeni_atlama"] = eklenen
    return s.bitir()


def ana(argv=None):
    ap = argparse.ArgumentParser(prog="kapi.py", description=__doc__.split("\n\n")[0])
    alt = ap.add_subparsers(dest="kip", required=True)
    j = alt.add_parser("junit"); j.add_argument("raporlar", nargs="+")
    j.add_argument("--taban", type=int, required=True); j.add_argument("--izinli-skip", type=int, default=0)
    w = alt.add_parser("playwright"); w.add_argument("rapor")
    w.add_argument("--taban", type=int, required=True); w.add_argument("--izinli-skip", type=int, default=0)
    w.add_argument("--izinli-beklenen-hata", type=int, default=0)
    g = alt.add_parser("godot"); g.add_argument("gunluk"); g.add_argument("--taban", type=int, required=True)
    m = alt.add_parser("medya"); m.add_argument("dosya")
    m.add_argument("--min-sure", type=float, default=0.1)
    for b in ("--video", "--ses", "--tam-cozum", "--siyah", "--sessiz"):
        m.add_argument(b, action="store_true")
    k = alt.add_parser("komut"); k.add_argument("dosyalar", nargs="+")
    f = alt.add_parser("fark"); f.add_argument("--taban-ref", default="origin/main")
    a = ap.parse_args(argv)
    if getattr(a, "taban", 1) < 1:
        ap.error("--taban en az 1 olmali; sifir taban sifir testi kabul eder")
    return {"junit": junit, "playwright": playwright, "godot": godot,
            "medya": medya, "komut": komut, "fark": fark}[a.kip](a)


if __name__ == "__main__":
    sys.exit(ana())

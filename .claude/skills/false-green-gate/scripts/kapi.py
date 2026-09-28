#!/usr/bin/env python3
"""false-green-gate: "komut 0 dondu" ile "is gercekten oldu"yu ayiran kapi.

Bir test kosucusunun ya da medya aracinin cikis kodu tek basina kanit
degil. Bu betik kosunun BIRAKTIGI kaniti okur (JUnit XML, Playwright JSON
raporu, Godot gunlugu, medya dosyasi, workflow/betik metni, git farki) ve
yesilin gercek olup olmadigina karar verir.

    kapi.py junit      RAPOR.xml... --taban N [--izinli-skip K] [--kosucu-cikis RC] [--en-fazla-yas SN]
    kapi.py playwright RAPOR.json   --taban N [--izinli-skip K] [--izinli-beklenen-hata K] [--kosucu-cikis RC] [--en-fazla-yas SN]
    kapi.py godot      GUNLUK       --taban N [--kosucu-cikis RC]
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
import time
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


def _kosu_kaniti(s, args, raporlar):
    """Kosucunun cikis kodu ve raporun tazeligi: eski bir rapor yeni bir kosuyu kanitlamaz."""
    rc = getattr(args, "kosucu_cikis", None)
    if rc is not None:
        s.olcum["kosucu_cikis"] = rc
        if rc != 0:
            s.fail("FG-23", f"kosucu {rc} ile cikti; rapor ne derse desin kosu basarili degil")
    yas = getattr(args, "en_fazla_yas", None)
    gorulen = set()
    for yol in raporlar:
        gercek = os.path.realpath(yol)
        if gercek in gorulen:
            s.fail("FG-18", f"{yol}: ayni rapor iki kez verildi; sayilar katlanir")
        gorulen.add(gercek)
        if yas is not None and os.path.exists(yol):
            gecen = time.time() - os.path.getmtime(yol)
            if gecen > yas:
                s.fail("FG-24", f"{yol}: rapor {gecen:.0f}s once yazilmis (en fazla {yas}s); eski bir kosuya ait olabilir")


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
        if kok.tag not in ("testsuites", "testsuite"):
            s.fail("FG-18", f"{yol}: kok eleman '{kok.tag}', JUnit degil")
            continue
        for v in kok.iter("testcase"):
            toplam += 1
            # Once hata: atlanip teardown'da patlayan test <skipped/> VE <error/> tasir.
            if v.find("failure") is not None or v.find("error") is not None:
                basarisiz += 1
            elif v.find("skipped") is not None:
                atlanan += 1
            # pytest-rerunfailures <rerun*>, surefire <flaky*>: sonunda gecse de kararsiz
            if any(c.tag.startswith(("rerun", "flaky")) for c in v):
                yeniden += 1
    kosan = toplam - atlanan
    _sayilar_ortak(s, toplam, kosan, basarisiz, atlanan, args.taban, args.izinli_skip)
    s.olcum["yeniden_kosulan"] = yeniden
    if yeniden:
        s.fail("FG-05", f"{yeniden} test ancak yeniden kosunca gecti (flaky); retry yesili yesil degildir")
    _kosu_kaniti(s, args, args.raporlar)
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
    # Taban ayri testlere karsi olculur, kosumlara degil: --repeat-each ya da
    # birden cok proje tek bir gercek testi N kez saydirir.
    ayri = set()
    for suite in rapor.get("suites", []):
        for spec, t in _pw_testleri(suite):
            if t.get("status") != "skipped":
                ayri.add((spec.get("file"), spec.get("line"), spec.get("column"), spec.get("title")))
    kosan = len(ayri)
    _sayilar_ortak(s, toplam, kosan, beklenmeyen, atlanan, args.taban, args.izinli_skip)
    s.olcum.update({"flaky": flaky, "kosum": beklenen + beklenmeyen + flaky})
    # Tazelik rapordaki zamanla: dosya tarihi cp/touch ile yenilenir.
    if args.en_fazla_yas is not None:
        try:
            from datetime import datetime
            bas = datetime.fromisoformat(str(st.get("startTime", "")).replace("Z", "+00:00")).timestamp()
            bitis = bas + float(st.get("duration", 0)) / 1000
            if time.time() - bitis > args.en_fazla_yas:
                s.fail("FG-24", f"rapordaki kosu {time.time() - bitis:.0f}s once bitmis (en fazla {args.en_fazla_yas:.0f}s)")
        except (ValueError, TypeError):
            s.fail("FG-24", "raporda gecerli stats.startTime yok; tazelik kanitlanamiyor")
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
    _kosu_kaniti(s, args, [args.rapor])
    return s.bitir()


# --- godot ---------------------------------------------------------------

# Ekosistemdeki dort oyunun gercek sonuc satirlari (her reponun tests/kapi.sh'i).
# (desen, gruplar -> (gecen, toplam), zorunlu ek satir)
GODOT_BICIM = {
    "kanca": (r"^=== (\d+)/(\d+) gecti ===\s*$", lambda a, b: (a, b), None),
    "yercekimi": (r"^(\d+) dogrulama, (\d+) hata\s*$", lambda n, h: (n - h, n), r"^TESTLER GECTI\s*$"),
    "derin": (r"^== (\d+) sınama, (\d+) hata ==\s*$", lambda n, h: (n - h, n), None),
    "tek": (r"=== SONUÇ: (\d+) geçti, (\d+) hata ===", lambda g, h: (g, g + h), None),
}
GODOT_HATA = re.compile(r"SCRIPT ERROR|Parse Error")


def godot(args):
    s = Sonuc("godot")
    try:
        with open(args.gunluk, encoding="utf-8", errors="replace") as f:
            metin = f.read()
    except OSError as e:
        s.fail("FG-18", f"gunluk okunamadi: {e}")
        return s.bitir()
    metin = re.sub(r"\x1b\[[0-9;]*m", "", metin)  # renk kodlari sonuc satirini gizlemesin
    hatalar = [satir for satir in metin.splitlines() if GODOT_HATA.search(satir)]
    if hatalar:
        s.fail("FG-09", f"gunlukte {len(hatalar)} betik hatasi var; bir test bolumu sessizce yarida kalmis olabilir: {hatalar[0][:120]}")
    desen, cevir, zorunlu = GODOT_BICIM[args.bicim]
    s.olcum["bicim"] = args.bicim
    sonuclar = re.findall(desen, metin, re.M)
    if not sonuclar:
        s.fail("FG-08", f"{args.bicim} bicimli sonuc satiri yok; takim sonuna kadar kosmadi")
        _kosu_kaniti(s, args, [])
        return s.bitir()
    if zorunlu and not re.search(zorunlu, metin, re.M):
        s.fail("FG-08", f"zorunlu bitis satiri yok ({zorunlu})")
    gecen, toplam = cevir(*(int(x) for x in sonuclar[-1]))
    _sayilar_ortak(s, toplam, gecen, toplam - gecen, 0, args.taban, 0)
    _kosu_kaniti(s, args, [])
    return s.bitir()


# --- medya ---------------------------------------------------------------

DECODE_HATA = re.compile(r"File ended prematurely|Invalid data found|error while decoding|"
                         r"partial file|moov atom not found|Truncat|corrupt", re.I)


GORUNTU_KODEK = {"png", "mjpeg", "bmp", "webp", "tiff", "gif"}


def _sayi(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


class ZamanAsimi(Exception):
    pass


def _calistir(argv, zaman=None):
    if zaman is None:
        zaman = float(os.environ.get("KAPI_ZAMAN_ASIMI", "600"))
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=zaman,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise ZamanAsimi(f"{argv[0]} {zaman}s icinde bitmedi")


def _ffmpeg_yolu(yol):
    # Mutlak yol + 'file:' oneki: '-' ile baslayan ad secenek, 'concat:' /
    # 'http:' gibi bir onek protokol sanilmaz; -protocol_whitelist file da
    # dosyanin icinden (HLS/concat listesi) baska kaynak acilmasini engeller.
    return "file:" + os.path.abspath(yol)


def _sure(bilgi, akislar):
    """format.duration yoksa (canli/MediaRecorder webm) akis surelerine dus."""
    adaylar = [bilgi.get("format", {}).get("duration")] + [a.get("duration") for a in akislar]
    for aday in adaylar:
        try:
            if aday not in (None, "N/A") and float(aday) > 0:
                return float(aday), "baslik"
        except ValueError:
            continue
    return 0.0, None


def medya(args):
    s = Sonuc("medya")
    try:
        return _medya(s, args)
    except ZamanAsimi as e:
        s.fail("FG-12", f"zaman asimi: {e}")
        return s.bitir()


def _medya(s, args):
    if not os.path.isfile(args.dosya) or os.path.getsize(args.dosya) == 0:
        s.fail("FG-10", f"dosya yok ya da bos: {args.dosya}")
        return s.bitir()
    girdi = _ffmpeg_yolu(args.dosya)
    s.olcum["boyut"] = os.path.getsize(args.dosya)
    try:
        p = _calistir(["ffprobe", "-v", "error", "-protocol_whitelist", "file",
                       "-show_format", "-show_streams", "-of", "json", girdi])
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
    # Kapak resmi her kapta attached_pic olarak isaretlenmez (MKV'de ayri bir
    # video izi olur); olculecek iz: goruntu kodegi olmayan, en uzun olan.
    video.sort(key=lambda a: (a.get("codec_name") in GORUNTU_KODEK, -_sayi(a.get("duration"))))
    ses = [a for a in akislar if a.get("codec_type") == "audio"]
    sure, kaynak = _sure(bilgi, akislar)
    if not kaynak:
        # Baslikta sure yok: son zaman damgasini cozerek olc.
        q = _calistir(["ffmpeg", "-nostdin", "-v", "error", "-stats", "-protocol_whitelist", "file",
                       "-i", girdi, "-f", "null", "-"])
        zamanlar = re.findall(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)", q.stderr)
        if zamanlar:
            h, m, sn = zamanlar[-1]
            sure, kaynak = int(h) * 3600 + int(m) * 60 + float(sn), "cozme"
    s.olcum.update({"sure": sure, "sure_kaynagi": kaynak, "video_akis": len(video),
                    "ses_akis": len(ses), "bicim": bilgi.get("format", {}).get("format_name")})
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
    # Olcumler raporlanan akis uzerinde yapilir (kapak resmi v:0 olabilir).
    vi = str(video[0]["index"]) if video else None
    si = str(ses[0]["index"]) if ses else None
    if args.tam_cozum:
        # Baslik yalan soyleyebilir (yarisi kesik faststart MP4 hala tam sureyi
        # bildirir); yalnizca tam cozme ve stderr gercegi gosterir. -xerror yetmez:
        # kesik MKV onunla bile 0 doner.
        p = _calistir(["ffmpeg", "-nostdin", "-v", "error", "-protocol_whitelist", "file",
                       "-i", girdi, "-f", "null", "-"])
        hatalar = [x for x in p.stderr.splitlines() if x.strip()]
        s.olcum["cozme_hata_satiri"] = len(hatalar)
        if p.returncode != 0 or any(DECODE_HATA.search(x) for x in hatalar):
            s.fail("FG-12", f"tam cozmede hata (cikis {p.returncode}): {(hatalar or ['?'])[0][:160]}")
        if vi is not None:
            q = _calistir(["ffprobe", "-v", "error", "-protocol_whitelist", "file",
                           "-select_streams", vi, "-count_frames",
                           "-show_entries", "stream=nb_frames,nb_read_frames",
                           "-of", "json", girdi])
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
            # Eksik HLS parcasi: kare sayisi ve sure tutarli gorunur, tam cozme
            # temizdir; tek iz zaman damgasindaki sicramadir (yt-dlp "Skipping
            # fragment" deyip 0 doner). Degisken kare hizli kaynaklarda (ekran
            # kaydi) uzun duraklama olagan olabilir: --degisken-kare ile WARN.
            q = _calistir(["ffprobe", "-v", "error", "-protocol_whitelist", "file",
                           "-select_streams", vi, "-show_entries", "packet=pts_time",
                           "-of", "csv=p=0", girdi])
            zamanlar = sorted(_sayi(x) for x in q.stdout.split() if x.strip() not in ("", "N/A"))
            try:
                pay, payda = (int(x) for x in str(video[0].get("r_frame_rate", "0/1")).split("/"))
                kare_suresi = payda / pay if pay else 0.04
            except ValueError:
                kare_suresi = 0.04
            esik = max(1.0, 10 * kare_suresi)
            bosluklar = [(a, b) for a, b in zip(zamanlar, zamanlar[1:]) if b - a > esik]
            s.olcum["zaman_boslugu"] = [[round(a, 3), round(b, 3)] for a, b in bosluklar[:5]]
            if bosluklar:
                a, b = bosluklar[0]
                (s.warn if args.degisken_kare else s.fail)(
                    "FG-13", f"zaman damgasinda {len(bosluklar)} bosluk ({a:.2f}s -> {b:.2f}s); eksik parca/segment")
    if args.siyah and vi is not None and sure > 0:
        p = _calistir(["ffmpeg", "-nostdin", "-v", "info", "-protocol_whitelist", "file",
                       "-i", girdi, "-map", "0:" + vi, "-vf", "blackdetect=d=0.1:pix_th=0.10",
                       "-an", "-f", "null", "-"])
        siyah = sum(float(x) for x in re.findall(r"black_duration:([0-9.]+)", p.stderr))
        s.olcum["siyah_sure"] = round(siyah, 3)
        if siyah >= 0.95 * sure:
            s.fail("FG-14", f"video neredeyse tamamen siyah ({siyah:.2f}/{sure:.2f}s)")
    if args.sessiz and si is not None and sure > 0:
        p = _calistir(["ffmpeg", "-nostdin", "-v", "info", "-protocol_whitelist", "file",
                       "-i", girdi, "-map", "0:" + si, "-af", "volumedetect",
                       "-vn", "-f", "null", "-"])
        m = re.search(r"max_volume: (-?[0-9.]+|-inf) dB", p.stderr)
        tepe = float("-inf") if not m or m.group(1) == "-inf" else float(m.group(1))
        s.olcum["ses_tepe_db"] = None if tepe == float("-inf") else tepe
        if tepe < -60:
            s.fail("FG-14", f"ses sessiz (tepe {m.group(1) if m else '?'} dB)")
    return s.bitir()


# --- komut (workflow / betik metni) --------------------------------------

# Kosucu adi baska bir kelimenin parcasi olmamali (pytest-cov, jest-junit).
KOSUCU = (r"(?<![\w-])(?:playwright\s+test|vitest|jest|pytest|npm\s+(?:run\s+)?test|"
          r"godot\b.*--headless|python3?\s+-m\s+(?:pytest|unittest))(?![\w-])")
KURULUM = re.compile(r"\b(?:pip3?|uv\s+pip|npm|pnpm|yarn|apt(?:-get)?)\s+(?:install|add|i)\b")
YUTMA = re.compile(r"\|\|\s*(?:true|:|exit\s+0|echo\b)|;\s*true\s*$")
KOMUT_KURALLARI = [
    ("FG-15", "FAIL", re.compile(r"--pass-with-no-tests|--passWithNoTests"),
     "sifir testle yesil donmeye izin veren bayrak"),
    ("FG-17", "FAIL", re.compile(r"(?:playwright\s+test|vitest|jest)\b.*(?:--update-snapshots(?!=none)|\s-u\b)"),
     "CI'da snapshot guncelleme: karsilastirma yerine yeni taban yaziliyor"),
    ("FG-19", "WARN", re.compile(r"--last-failed|--only-changed|--lf\b"),
     "yalnizca bir alt kume kosuluyor; PR hizlandirmasi olabilir ama tam kosunun yerine gecmez"),
]


def _mantiksal_satirlar(metin):
    """Yorumlari at, '\\' ile devam eden satirlari birlestir; (satir_no, metin)."""
    out, biriken, bas = [], "", None
    for no, satir in enumerate(metin.splitlines(), 1):
        if re.match(r"\s*#", satir) and not biriken:
            continue
        if bas is None:
            bas = no
        if satir.rstrip().endswith("\\"):
            biriken += satir.rstrip()[:-1] + " "
            continue
        out.append((bas, biriken + satir))
        biriken, bas = "", None
    if biriken:
        out.append((bas, biriken))
    return out


def komut(args):
    s = Sonuc("komut")
    for yol in args.dosyalar:
        try:
            with open(yol, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError as e:
            s.fail("FG-18", f"{yol}: okunamadi ({e})")
            continue
        pipefail = re.search(r"pipefail|shell:\s*bash\b", metin)
        kosucu_var = False
        for no, satir in _mantiksal_satirlar(metin):
            kosucu = re.search(KOSUCU, satir) and not KURULUM.search(satir)
            kosucu_var = kosucu_var or bool(kosucu)
            if kosucu and YUTMA.search(satir[re.search(KOSUCU, satir).start():]):
                s.fail("FG-16", f"{yol}:{no}: test komutunun hatasi yutuluyor (|| true / || echo)")
            if kosucu and not pipefail and re.search(KOSUCU + r".*(?<!\|)\|(?!\|)", satir):
                s.fail("FG-16", f"{yol}:{no}: test ciktisi pipe'a gidiyor ve pipefail yok; kosucunun hatasi kaybolur")
            for kod, seviye, desen, aciklama in KOMUT_KURALLARI:
                if desen.search(satir):
                    (s.fail if seviye == "FAIL" else s.warn)(kod, f"{yol}:{no}: {aciklama}")
        if kosucu_var and re.search(r"continue-on-error:\s*true", metin):
            s.warn("FG-20", f"{yol}: continue-on-error var; test adiminda ise kirmizi gizlenir")
        if kosucu_var and re.search(r"(?m)^\s*(?:-\s*run:\s*)?set\s+\+e\b", metin):
            s.warn("FG-25", f"{yol}: set +e var; kosucunun cikis kodu sonra kontrol edilmiyorsa kirmizi gizlenir")
    return s.bitir()


# --- fark (git) ----------------------------------------------------------

ATLAMA = re.compile(
    r"\b(?:test|it|describe|suite|context|bench)(?:\.\w+)*\.(?:skip|skipIf|fixme|fail|only|todo)\b"
    r"|\b(?:xit|xdescribe|xtest|fit|fdescribe)\s*\("
    r"|@pytest\.mark\.(?:skip|skipif|xfail)\b|\bpytest\.(?:skip|xfail|importorskip)\s*\("
    r"|@unittest\.(?:skip\w*|expectedFailure)\b|\bunittest\.SkipTest\b|\bself\.skipTest\s*\(")
TEST_DOSYASI = re.compile(r"(?:^|/)(?:tests?|__tests__|e2e|spec)/|(?:^|/)test_[^/]*\.py$|_test\.py$"
                          r"|\.(?:spec|test)\.[cm]?[jt]sx?$|\.gd$")
IZINLI = "kapi: izinli"


def _git(*argv):
    return _calistir(["git", "-c", "core.quotepath=off", *argv])


def fark(args):
    s = Sonuc("fark")
    if args.taban_ref.startswith("-"):
        s.fail("FG-18", f"gecersiz taban ref: {args.taban_ref!r}")
        return s.bitir()
    try:
        # '-' ile baslayan ref yukarida reddedildi; git'e secenek olarak gidemez.
        mb = _git("merge-base", args.taban_ref, "HEAD")
    except FileNotFoundError:
        s.fail("FG-18", "git bulunamadi")
        return s.bitir()
    if mb.returncode != 0:
        s.fail("FG-18", f"merge-base bulunamadi ({args.taban_ref}): {mb.stderr.strip()[:160]}")
        return s.bitir()
    taban = mb.stdout.strip()
    s.olcum["merge_base"] = taban
    # Taban ile calisma agaci arasi; harici diff araci ve onek ayarlari etkisiz.
    p = _git("diff", "--no-ext-diff", "--no-color", "--unified=0",
             "--src-prefix=a/", "--dst-prefix=b/", taban, "--")
    if p.returncode != 0:
        s.fail("FG-18", f"git diff basarisiz: {p.stderr.strip()[:160]}")
        return s.bitir()
    eklenen = []  # (dosya, satir)
    dosya = None
    for satir in p.stdout.splitlines():
        if satir.startswith("+++ "):
            dosya = satir[6:] if satir.startswith("+++ b/") else None
            if dosya and re.search(r"(?:-snapshots|__snapshots__)/", dosya):
                s.warn("FG-22", f"{dosya}: snapshot tabani degisti; gorsel fark insan tarafindan incelenmeli")
        elif satir.startswith("+") and dosya:
            eklenen.append((dosya, satir[1:]))
    # Izlenmeyen yeni dosyalar da farkin parcasi.
    u = _git("ls-files", "--others", "--exclude-standard", "-z")
    for ad in filter(None, u.stdout.split("\0")):
        try:
            with open(ad, encoding="utf-8", errors="replace") as fh:
                eklenen.extend((ad, x) for x in fh.read().splitlines())
        except OSError:
            continue
    sayi = izinli = 0
    for ad, satir in eklenen:
        if not TEST_DOSYASI.search(ad) or not ATLAMA.search(satir):
            continue
        if re.match(r"\s*(?:#|//)", satir):
            continue
        if IZINLI in satir:
            izinli += 1
            continue
        sayi += 1
        s.fail("FG-21", f"{ad}: yeni atlama/odak isareti eklendi: {satir.strip()[:120]}")
    s.olcum.update({"yeni_atlama": sayi, "izinli_isaret": izinli})
    if izinli:
        s.warn("FG-21", f"{izinli} satir '{IZINLI}' ile muaf tutuldu; incelemede gerekcesine bakilmali")
    return s.bitir()


def ana(argv=None):
    ap = argparse.ArgumentParser(prog="kapi.py", description=__doc__.split("\n\n")[0])
    alt = ap.add_subparsers(dest="kip", required=True)

    def kosu(p):
        # Zorunlu: config yuklenemeyince Playwright eski JSON'u yerinde birakir;
        # cikis kodu olmadan eski bir rapor yeni kosu gibi okunur.
        p.add_argument("--kosucu-cikis", type=int, required=True, help="test kosucusunun cikis kodu ($?)")

    j = alt.add_parser("junit"); j.add_argument("raporlar", nargs="+")
    j.add_argument("--taban", type=int, required=True); j.add_argument("--izinli-skip", type=int, default=0)
    j.add_argument("--en-fazla-yas", type=float, help="rapor bu kadar saniyeden eskiyse FAIL"); kosu(j)
    w = alt.add_parser("playwright"); w.add_argument("rapor")
    w.add_argument("--taban", type=int, required=True); w.add_argument("--izinli-skip", type=int, default=0)
    w.add_argument("--izinli-beklenen-hata", type=int, default=0)
    w.add_argument("--en-fazla-yas", type=float); kosu(w)
    g = alt.add_parser("godot"); g.add_argument("gunluk"); g.add_argument("--taban", type=int, required=True)
    g.add_argument("--bicim", choices=sorted(GODOT_BICIM), default="kanca",
                   help="sonuc satiri bicimi (kanca: '=== G/T gecti ===')")
    kosu(g)
    m = alt.add_parser("medya"); m.add_argument("dosya")
    m.add_argument("--min-sure", type=float, default=0.1)
    for b in ("--video", "--ses", "--tam-cozum", "--siyah", "--sessiz", "--degisken-kare"):
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

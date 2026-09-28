#!/usr/bin/env python3
"""false-green-gate'in kendi sinamasi: her kural icin bir PASS ve bir FAIL.

    python3 .claude/skills/false-green-gate/test_kapi.py

Kapi yalnizca kirmiziya donebildigi kanitlandiginda kapidir; bu yuzden her
FAIL fiksturu kapinin GERCEKTEN 1 dondurdugunu, her PASS fiksturu de
temiz kosuyu reddetmedigini sinar. Medya fiksturleri ffmpeg ile burada
uretilir (depoya ikili dosya girmez).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KAPI = os.path.join(BURASI, "scripts", "kapi.py")
FIK = os.path.join(BURASI, "fikstur")


def kos(*argv, cwd=None):
    p = subprocess.run([sys.executable, KAPI, *argv], capture_output=True, text=True, cwd=cwd)
    son = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "{}"
    return p.returncode, json.loads(son), p.stderr


def kos_env(env, *argv, cwd=None):
    p = subprocess.run([sys.executable, KAPI, *argv], capture_output=True, text=True, cwd=cwd,
                       env={**os.environ, **env})
    return p.returncode, json.loads(p.stdout.strip().splitlines()[-1]), p.stderr


def kodlar(kanit):
    return sorted({b["kod"] for b in kanit.get("bulgular", []) if b["seviye"] == "FAIL"})


def f(*parca):
    return os.path.join(FIK, *parca)


class JunitTesti(unittest.TestCase):
    def test_temiz(self):
        rc, k, _ = kos("junit", f("junit", "temiz.xml"), "--taban", "3")
        self.assertEqual((rc, k["sonuc"]), (0, "PASS"))
        self.assertEqual(k["olcum"]["kosan"], 3)

    def test_sifir_test(self):
        rc, k, _ = kos("junit", f("junit", "sifir.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-01", kodlar(k))

    def test_tabanin_alti(self):
        rc, k, _ = kos("junit", f("junit", "temiz.xml"), "--taban", "4")
        self.assertEqual(rc, 1); self.assertIn("FG-02", kodlar(k))

    def test_hepsi_atlanmis(self):
        rc, k, _ = kos("junit", f("junit", "hepsi-atlanmis.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertEqual(kodlar(k), ["FG-01", "FG-04"])

    def test_izinli_atlama(self):
        rc, k, _ = kos("junit", f("junit", "bir-atlama.xml"), "--taban", "2", "--izinli-skip", "1")
        self.assertEqual(rc, 0, k)

    def test_basarisiz(self):
        rc, k, _ = kos("junit", f("junit", "basarisiz.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-03", kodlar(k))

    def test_retry_ile_gecen(self):
        rc, k, _ = kos("junit", f("junit", "rerun.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-05", kodlar(k))

    def test_bozuk_rapor(self):
        rc, k, _ = kos("junit", f("junit", "bozuk.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_olmayan_rapor(self):
        rc, k, _ = kos("junit", f("junit", "yok.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_junit_olmayan_kok(self):
        rc, k, _ = kos("junit", f("junit", "html.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_sifir_taban_reddedilir(self):
        p = subprocess.run([sys.executable, KAPI, "junit", f("junit", "sifir.xml"), "--taban", "0"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


class PlaywrightTesti(unittest.TestCase):
    def test_temiz(self):
        rc, k, _ = kos("playwright", f("playwright", "temiz.json"), "--taban", "2")
        self.assertEqual((rc, k["sonuc"]), (0, "PASS"), k)

    def test_sifir(self):
        rc, k, _ = kos("playwright", f("playwright", "sifir.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-01", kodlar(k))

    def test_flaky(self):
        rc, k, _ = kos("playwright", f("playwright", "flaky.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-05", kodlar(k))

    def test_test_fail_ters_yesil(self):
        rc, k, _ = kos("playwright", f("playwright", "test-fail.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-06", kodlar(k))

    def test_test_fail_izinli(self):
        rc, k, _ = kos("playwright", f("playwright", "test-fail.json"), "--taban", "1",
                       "--izinli-beklenen-hata", "1")
        self.assertEqual(rc, 0, k)

    def test_global_hata(self):
        rc, k, _ = kos("playwright", f("playwright", "global-hata.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-07", kodlar(k))

    def test_atlama(self):
        rc, k, _ = kos("playwright", f("playwright", "atlama.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-04", kodlar(k))

    def test_beklenmeyen(self):
        rc, k, _ = kos("playwright", f("playwright", "beklenmeyen.json"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-03", kodlar(k))

    def test_stats_yok(self):
        rc, k, _ = kos("playwright", f("junit", "temiz.xml"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))


class GodotTesti(unittest.TestCase):
    def test_temiz(self):
        rc, k, _ = kos("godot", f("godot", "temiz.log"), "--taban", "114")
        self.assertEqual(rc, 0, k)

    def test_betik_hatasi_ama_hepsi_gecti(self):
        # Gercek olay (kanca, 25 Eylul 2026): "114/114 gecti", cikis 0, ama bir
        # fonksiyon SCRIPT ERROR ile yarida kesilmis.
        rc, k, _ = kos("godot", f("godot", "betik-hatasi.log"), "--taban", "100")
        self.assertEqual(rc, 1); self.assertIn("FG-09", kodlar(k))

    def test_sonuc_satiri_yok(self):
        rc, k, _ = kos("godot", f("godot", "yarida.log"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-08", kodlar(k))

    def test_taban_alti(self):
        rc, k, _ = kos("godot", f("godot", "temiz.log"), "--taban", "120")
        self.assertEqual(rc, 1); self.assertIn("FG-02", kodlar(k))

    def test_kalan(self):
        rc, k, _ = kos("godot", f("godot", "kalan.log"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-03", kodlar(k))

    def test_gunluk_yok(self):
        rc, k, _ = kos("godot", f("godot", "yok.log"), "--taban", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))


class KomutTesti(unittest.TestCase):
    def test_temiz_workflow(self):
        rc, k, _ = kos("komut", f("komut", "temiz.yml"))
        self.assertEqual(rc, 0, k)

    def test_bos_test_bayragi(self):
        rc, k, _ = kos("komut", f("komut", "bos-test.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-15", kodlar(k))

    def test_hata_yutma(self):
        rc, k, _ = kos("komut", f("komut", "yutma.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-16", kodlar(k))

    def test_snapshot_guncelleme(self):
        rc, k, _ = kos("komut", f("komut", "snapshot.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-17", kodlar(k))

    def test_continue_on_error_uyari(self):
        rc, k, _ = kos("komut", f("komut", "coe.yml"))
        self.assertEqual(rc, 0)
        self.assertIn("FG-20", [b["kod"] for b in k["bulgular"]])

    def test_dosya_yok(self):
        rc, k, _ = kos("komut", f("komut", "yok.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))


@unittest.skipUnless(shutil.which("git"), "git yok")
class FarkTesti(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        g = lambda *a: subprocess.run(["git", *a], cwd=self.d, check=True, capture_output=True)
        g("init", "-q", "-b", "ana"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
        with open(os.path.join(self.d, "a.spec.ts"), "w") as fh:
            fh.write("test('x', async () => { expect(1).toBe(1) })\n")
        g("add", "."); g("commit", "-qm", "ilk")
        self.g = g

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_temiz_fark(self):
        with open(os.path.join(self.d, "a.spec.ts"), "a") as fh:
            fh.write("test('y', async () => { expect(2).toBe(2) })\n")
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 0, k)

    def test_yeni_skip(self):
        with open(os.path.join(self.d, "a.spec.ts"), "a") as fh:
            fh.write("test.skip('y', async () => {})\n")
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-21", kodlar(k))

    def test_yeni_pytest_skip(self):
        with open(os.path.join(self.d, "t.py"), "w") as fh:
            fh.write("import pytest\n@pytest.mark.skip(reason='sonra')\ndef test_a():\n    pass\n")
        self.g("add", "-N", "t.py")
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-21", kodlar(k))

    def test_gecersiz_ref(self):
        rc, k, _ = kos("fark", "--taban-ref", "olmayan-dal", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_git_yok(self):
        rc, k, _ = kos_env({"PATH": "/nonexistent"}, "fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))


FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")


@unittest.skipUnless(FFMPEG, "ffmpeg/ffprobe yok")
class MedyaTesti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()

        def uret(ad, *argv):
            yol = os.path.join(cls.d, ad)
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *argv, yol], check=True)
            return yol
        cls.iyi = uret("iyi.mp4", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=25:duration=3",
                       "-f", "lavfi", "-i", "sine=frequency=440:duration=3", "-shortest",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart")
        cls.siyah = uret("siyah.mp4", "-f", "lavfi", "-i", "color=black:size=160x120:rate=25:duration=3",
                         "-c:v", "libx264", "-pix_fmt", "yuv420p")
        cls.sessiz = uret("sessiz.mp4", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=25:duration=3",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "3",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac")
        cls.sessiz_akissiz = uret("sadece-video.mp4", "-f", "lavfi", "-i",
                                  "testsrc=size=160x120:rate=25:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p")
        cls.sifir = uret("sifir.mp4", "-f", "lavfi", "-i", "testsrc=size=160x120:rate=25:duration=3",
                         "-t", "0", "-c:v", "libx264")
        cls.kesik = os.path.join(cls.d, "kesik.mp4")
        with open(cls.iyi, "rb") as src, open(cls.kesik, "wb") as dst:
            veri = src.read(); dst.write(veri[: len(veri) // 2])
        cls.bos = os.path.join(cls.d, "bos.mp4"); open(cls.bos, "wb").close()
        cls.tire = os.path.join(cls.d, "-tire.mp4"); shutil.copy(cls.iyi, cls.tire)
        cls.sadece_ses = uret("ses.m4a", "-f", "lavfi", "-i", "sine=duration=3", "-c:a", "aac")
        tek_v = uret("tek-v.mp4", "-f", "lavfi", "-i", "color=red:size=160x120:rate=25",
                     "-frames:v", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p")
        cls.tek_kare = uret("tek-kare.mp4", "-i", tek_v, "-i", cls.sadece_ses,
                            "-map", "0:v", "-map", "1:a", "-c", "copy")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_iyi(self):
        rc, k, _ = kos("medya", self.iyi, "--video", "--ses", "--tam-cozum", "--siyah", "--sessiz", "--min-sure", "2")
        self.assertEqual(rc, 0, k)
        self.assertEqual((k["olcum"]["genislik"], k["olcum"]["yukseklik"]), (160, 120))

    def test_bos_dosya(self):
        rc, k, _ = kos("medya", self.bos)
        self.assertEqual(rc, 1); self.assertIn("FG-10", kodlar(k))

    def test_sifir_sure(self):
        # ffmpeg -t 0: cikis 0, 262 baytlik akissiz dosya
        rc, k, _ = kos("medya", self.sifir, "--video")
        self.assertEqual(rc, 1); self.assertTrue({"FG-10", "FG-11"} & set(kodlar(k)), k)

    def test_ses_akisi_yok(self):
        rc, k, _ = kos("medya", self.sessiz_akissiz, "--ses")
        self.assertEqual(rc, 1); self.assertIn("FG-11", kodlar(k))

    def test_kesik_dosya(self):
        # Baslik hala 75 kare / 3 s diyor; iki bagimsiz kanit da yakalamali:
        # cozme stderr'i (FG-12) ve baslik-cozulen kare farki (FG-13).
        rc, k, _ = kos("medya", self.kesik, "--video", "--tam-cozum")
        self.assertEqual(rc, 1, k)
        self.assertTrue({"FG-12", "FG-13"} <= set(kodlar(k)), k)

    def test_video_akisi_yok(self):
        rc, k, _ = kos("medya", self.sadece_ses, "--video")
        self.assertEqual(rc, 1); self.assertIn("FG-11", kodlar(k))

    def test_sure_kisa(self):
        rc, k, _ = kos("medya", self.iyi, "--min-sure", "10")
        self.assertEqual(rc, 1); self.assertIn("FG-11", kodlar(k))

    def test_tek_kare(self):
        rc, k, _ = kos("medya", self.tek_kare, "--video", "--tam-cozum")
        self.assertEqual(rc, 1); self.assertIn("FG-13", kodlar(k))

    def test_ffprobe_yok(self):
        rc, k, _ = kos_env({"PATH": "/nonexistent"}, "medya", self.iyi)
        self.assertEqual(rc, 1); self.assertIn("FG-10", kodlar(k))

    def test_siyah(self):
        rc, k, _ = kos("medya", self.siyah, "--video", "--siyah")
        self.assertEqual(rc, 1); self.assertIn("FG-14", kodlar(k))

    def test_sessiz(self):
        rc, k, _ = kos("medya", self.sessiz, "--ses", "--sessiz")
        self.assertEqual(rc, 1); self.assertIn("FG-14", kodlar(k))

    def test_tire_ile_baslayan_ad(self):
        # '-tire.mp4' ffmpeg'e secenek olarak gitmemeli.
        rc, k, _ = kos("medya", os.path.relpath(self.tire, os.getcwd()), "--video", "--tam-cozum")
        self.assertEqual(rc, 0, k)


class MutasyonTesti(unittest.TestCase):
    """Kapinin kendisi zayiflatildiginda bu dosya kirmiziya donmeli."""

    def test_kapi_bozulunca_yakalanir(self):
        with open(KAPI, encoding="utf-8") as fh:
            kaynak = fh.read()
        bozuk = kaynak.replace('s.fail("FG-01"', 's.warn("FG-01"', 1)
        self.assertNotEqual(bozuk, kaynak)
        d = tempfile.mkdtemp()
        try:
            yol = os.path.join(d, "kapi.py")
            with open(yol, "w", encoding="utf-8") as fh:
                fh.write(bozuk)
            p = subprocess.run([sys.executable, yol, "junit", f("junit", "sifir.xml"), "--taban", "1"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, "mutant PASS vermeli ki gercek kapidaki fark anlamli olsun")
        finally:
            shutil.rmtree(d)
        rc, _, _ = kos("junit", f("junit", "sifir.xml"), "--taban", "1")
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    sonuc = unittest.main(exit=False, verbosity=1).result
    # Bu dosyanin kendisi de sifirtest'e tabi: hic test kosmadiysa ya da
    # bir sinif atlandiysa yesil sayma.
    kosan = sonuc.testsRun - len(sonuc.skipped)
    if kosan == 0:
        print("KAPI: hic test kosmadi", file=sys.stderr); sys.exit(1)
    if sonuc.skipped:
        print(f"UYARI: {len(sonuc.skipped)} test atlandi: " +
              "; ".join(sorted({r for _, r in sonuc.skipped})), file=sys.stderr)
    sys.exit(0 if sonuc.wasSuccessful() else 1)

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

    def test_atlanip_teardownda_patlayan(self):
        # pytest: "1 passed, 1 skipped, 1 error" -> <skipped/> VE <error/> ayni vakada
        rc, k, _ = kos("junit", f("junit", "skip-ve-hata.xml"), "--taban", "1", "--izinli-skip", "1")
        self.assertEqual(rc, 1); self.assertIn("FG-03", kodlar(k))

    def test_kosucu_cikis_kodu(self):
        # pytest conftest'te coker (cikis 4) ve eski rapor yerinde kalir
        rc, k, _ = kos("junit", f("junit", "temiz.xml"), "--taban", "3", "--kosucu-cikis", "4")
        self.assertEqual(rc, 1); self.assertIn("FG-23", kodlar(k))

    def test_ayni_rapor_iki_kez(self):
        rc, k, _ = kos("junit", f("junit", "temiz.xml"), f("junit", "temiz.xml"), "--taban", "6")
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_eski_rapor(self):
        d = tempfile.mkdtemp()
        try:
            yol = os.path.join(d, "r.xml"); shutil.copy(f("junit", "temiz.xml"), yol)
            os.utime(yol, (0, 0))
            rc, k, _ = kos("junit", yol, "--taban", "3", "--en-fazla-yas", "600")
            self.assertEqual(rc, 1); self.assertIn("FG-24", kodlar(k))
            os.utime(yol, None)
            rc, k, _ = kos("junit", yol, "--taban", "3", "--en-fazla-yas", "600", "--kosucu-cikis", "0")
            self.assertEqual(rc, 0, k)
        finally:
            shutil.rmtree(d)

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

    def test_renkli_ve_crlf_sonuc_satiri(self):
        rc, k, _ = kos("godot", f("godot", "renkli.log"), "--taban", "114")
        self.assertEqual(rc, 0, k)

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

    def test_yanlis_pozitif_yok(self):
        # pip install pytest-cov || true, yorum satiri, --update-snapshots=none
        rc, k, _ = kos("komut", f("komut", "yanlis-pozitif.yml"))
        self.assertEqual(rc, 0, k)

    def test_cok_satirli_yutma(self):
        rc, k, _ = kos("komut", f("komut", "cok-satir.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-16", kodlar(k))

    def test_pipefailsiz_tee(self):
        rc, k, _ = kos("komut", f("komut", "tee.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-16", kodlar(k))

    def test_pipefailli_tee(self):
        rc, k, _ = kos("komut", f("komut", "tee-pipefail.yml"))
        self.assertEqual(rc, 0, k)

    def test_echo_ile_yutma(self):
        rc, k, _ = kos("komut", f("komut", "echo.yml"))
        self.assertEqual(rc, 1); self.assertIn("FG-16", kodlar(k))

    def test_set_arti_e_uyari(self):
        rc, k, _ = kos("komut", f("komut", "set-e.yml"))
        self.assertIn("FG-25", [b["kod"] for b in k["bulgular"]])


@unittest.skipUnless(shutil.which("git"), "git yok")  # kapi: izinli -- git yoksa kosamaz; __main__ atlamayi hata sayar
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
            fh.write("test.skip('y', async () => {})\n")  # kapi: izinli
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-21", kodlar(k))

    def test_yeni_pytest_skip(self):
        with open(os.path.join(self.d, "test_t.py"), "w") as fh:
            fh.write("import pytest\n@pytest.mark.skip(reason='sonra')\ndef test_a():\n    pass\n")  # kapi: izinli
        self.g("add", "-N", "test_t.py")
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-21", kodlar(k))

    def test_gecersiz_ref(self):
        rc, k, _ = kos("fark", "--taban-ref", "olmayan-dal", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_git_yok(self):
        rc, k, _ = kos_env({"PATH": "/nonexistent"}, "fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))

    def test_ref_enjeksiyonu(self):
        hedef = os.path.join(self.d, "pwned.txt")
        rc, k, _ = kos("fark", "--taban-ref=--output=" + hedef, cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-18", kodlar(k))
        self.assertFalse(os.path.exists(hedef))

    def test_izlenmeyen_dosya(self):
        with open(os.path.join(self.d, "yeni.spec.ts"), "w") as fh:
            fh.write("it.only('z', () => {})\n")  # kapi: izinli
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1); self.assertIn("FG-21", kodlar(k))

    def test_kacan_bicimler(self):
        bicimler = ["it.only.each([1])('a', () => {})", "test.skipIf(x)('a', () => {})",  # kapi: izinli
                    "describe.concurrent.skip('a', () => {})", "it.todo('a')"]  # kapi: izinli
        with open(os.path.join(self.d, "a.spec.ts"), "a") as fh:
            fh.write("\n".join(bicimler) + "\n")
        with open(os.path.join(self.d, "test_b.py"), "w") as fh:
            fh.write("import unittest\n@unittest.skipIf(True, 'x')\nclass A(unittest.TestCase):\n"  # kapi: izinli
                     "    def test_a(self):\n        raise unittest.SkipTest('x')\n"  # kapi: izinli
                     "pytest.importorskip('numpy')\n")  # kapi: izinli
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 1)
        self.assertEqual(k["olcum"]["yeni_atlama"], 7, k)

    def test_belge_ve_yorum_sayilmaz(self):
        with open(os.path.join(self.d, "NOT.md"), "w") as fh:
            fh.write("Kullanma: test.skip()\n")  # kapi: izinli
        with open(os.path.join(self.d, "a.spec.ts"), "a") as fh:
            fh.write("// test.skip ornegi degil\n")  # kapi: izinli
        rc, k, _ = kos("fark", "--taban-ref", "HEAD", cwd=self.d)
        self.assertEqual(rc, 0, k)

    def test_merge_base_yanlis_kirmizi_yok(self):
        # Taban dalinda sonradan silinen bir skip, dokunmayan dali kirmiziya cevirmemeli.
        with open(os.path.join(self.d, "s.spec.ts"), "w") as fh:
            fh.write("test.skip('eski', () => {})\n")  # kapi: izinli
        self.g("add", "."); self.g("commit", "-qm", "eski skip")
        self.g("branch", "ozellik")
        with open(os.path.join(self.d, "s.spec.ts"), "w") as fh:
            fh.write("test('eski', () => {})\n")
        self.g("commit", "-qam", "skip kaldirildi")
        self.g("checkout", "-q", "ozellik")
        rc, k, _ = kos("fark", "--taban-ref", "ana", cwd=self.d)
        self.assertEqual(rc, 0, k)


FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")


@unittest.skipUnless(FFMPEG, "ffmpeg/ffprobe yok")  # kapi: izinli -- ffmpeg yoksa kosamaz; __main__ atlamayi hata sayar
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

    def test_zaman_asimi(self):
        rc, k, _ = kos_env({"KAPI_ZAMAN_ASIMI": "0.001"}, "medya", self.iyi, "--tam-cozum")
        self.assertEqual(rc, 1); self.assertIn("FG-12", kodlar(k))

    def test_ffprobe_yok(self):
        rc, k, _ = kos_env({"PATH": "/nonexistent"}, "medya", self.iyi)
        self.assertEqual(rc, 1); self.assertIn("FG-10", kodlar(k))

    def test_sure_basligi_olmayan_webm(self):
        yol = os.path.join(self.d, "canli.webm")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "testsrc=size=160x120:rate=25:duration=4", "-c:v", "libvpx", "-f", "webm",
                        "-live", "1", yol], check=True)
        rc, k, _ = kos("medya", yol, "--video", "--min-sure", "3")
        self.assertEqual(rc, 0, k); self.assertEqual(k["olcum"]["sure_kaynagi"], "cozme")

    def test_kapak_resmi_ilk_akis(self):
        png = os.path.join(self.d, "kapak.png")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "color=white:size=64x64", "-frames:v", "1", png], check=True)
        yol = os.path.join(self.d, "kapakli.mkv")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", png, "-i", self.iyi,
                        "-map", "0", "-map", "1", "-c", "copy", "-disposition:v:0", "attached_pic", yol], check=True)
        rc, k, _ = kos("medya", yol, "--video", "--ses", "--tam-cozum", "--siyah")
        self.assertEqual(rc, 0, k)

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
        print(f"KAPI: {len(sonuc.skipped)} test atlandi: " +
              "; ".join(sorted({r for _, r in sonuc.skipped})), file=sys.stderr)
        # Atlanan test gecmis sayilmaz; bilincli istisna ortamda acikca verilir.
        if os.environ.get("KAPI_ATLAMA_IZNI") != "1":
            sys.exit(1)
    sys.exit(0 if sonuc.wasSuccessful() else 1)

"""kontrol.py'nin oz sinamasi: gercek lychee ikilisiyle, her FAIL yolu
icin bir fikstur ve temiz bir PASS. LYCHEE ortam degiskeni ikilinin yolu.
Atlanan test yok: LYCHEE tanimli degilse takim kirmizi.
"""
import os
import subprocess
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KONTROL = os.path.join(BURASI, "kontrol.py")
LYCHEE = os.environ.get("LYCHEE", "")


def kos(klasor, *dosyalar, en_az=1):
    r = subprocess.run(
        [sys.executable, KONTROL, "--lychee", LYCHEE, "--en-az", str(en_az), *dosyalar],
        cwd=klasor, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


class Kontrol(unittest.TestCase):
    def setUp(self):
        self.assertTrue(LYCHEE and os.access(LYCHEE, os.X_OK),
                        "LYCHEE ortam degiskeni calistirilabilir lychee'yi gostermeli")
        self.t = tempfile.mkdtemp()

    def yaz(self, ad, metin):
        with open(os.path.join(self.t, ad), "w", encoding="utf-8") as f:
            f.write(metin)

    def test_temiz_pass(self):
        self.yaz("b.md", "# Başlık\n\n## Şehir Ağı\n")
        self.yaz("a.md", "[b](b.md) [capa](b.md#şehir-ağı) [uzak](https://example.com/)\n")
        rc, out = kos(self.t, "a.md", "b.md", en_az=2)
        self.assertEqual(rc, 0, out)
        self.assertIn("uzak link: 1", out)

    def test_kirik_yerel_link_fail(self):
        self.yaz("a.md", "[yok](yok.md)\n")
        rc, out = kos(self.t, "a.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("KIRIK", out)

    def test_kirik_capa_fail(self):
        self.yaz("b.md", "# Baslik\n")
        self.yaz("a.md", "[capa](b.md#olmayan-bolum)\n")
        rc, out = kos(self.t, "a.md", "b.md")
        self.assertEqual(rc, 1, out)

    def test_yalnizca_uzak_link_en_az_fail(self):
        # cevrimdisi kipte uzak linkler denetlenmez: "0 kirik" yesil degildir
        self.yaz("a.md", "[uzak](https://example.com/)\n")
        rc, out = kos(self.t, "a.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("--en-az", out)

    def test_dosya_yok_fail(self):
        subprocess.run(["git", "init", "-q", self.t], check=True)
        rc, out = kos(self.t)
        self.assertEqual(rc, 1, out)
        self.assertIn("Markdown dosyasi yok", out)

    def test_saglam_ve_kirik_birlikte_fail(self):
        # --en-az karsilansa da tek bir kirik link FAIL'dir
        self.yaz("b.md", "# B\n")
        self.yaz("a.md", "[b](b.md) [b2](b.md#b) [yok](yok.md)\n")
        rc, out = kos(self.t, "a.md", "b.md", en_az=1)
        self.assertEqual(rc, 1, out)
        self.assertIn("KIRIK", out)

    def test_lychee_beklenmeyen_cikis_fail(self):
        # temiz bir rapor yazip 3 donen lychee: rapor yesil diye PASS denmez
        sahte = os.path.join(self.t, "sahte-lychee")
        with open(sahte, "w") as f:
            f.write("#!/bin/sh\nwhile [ \"$1\" != --output ]; do shift; done\n"
                    "printf '{\"total\":5,\"successful\":5,\"errors\":0,\"excludes\":0}' > \"$2\"\n"
                    "exit 3\n")
        os.chmod(sahte, 0o755)
        self.yaz("a.md", "x\n")
        r = subprocess.run([sys.executable, KONTROL, "--lychee", sahte, "a.md"],
                           cwd=self.t, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("beklenmeyen cikis 3", r.stdout)

    def test_olmayan_dosya_fail(self):
        rc, out = kos(self.t, "hic-yok.md")
        self.assertEqual(rc, 1, out)


if __name__ == "__main__":
    unittest.main()

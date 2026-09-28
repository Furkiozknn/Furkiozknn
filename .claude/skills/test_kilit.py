#!/usr/bin/env python3
"""kilit.py'nin sinamasi: kilidin atlatilamadigini gosterir.

    python3 .claude/skills/test_kilit.py

Her test kilit.py'yi gecici bir kopyada, kucuk sahte bir skill agaciyla kosar.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

KILIT_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kilit.py")


class KilitTesti(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.dis = tempfile.mkdtemp()
        shutil.copy(KILIT_PY, self.d)
        os.makedirs(os.path.join(self.d, "animate"))
        with open(os.path.join(self.d, "animate", "SKILL.md"), "w") as f:
            f.write("---\nname: animate\ndescription: x\n---\n")
        self.assertEqual(self.kos("--uret"), 0)

    def tearDown(self):
        shutil.rmtree(self.d); shutil.rmtree(self.dis)

    def kos(self, arg):
        return subprocess.run([sys.executable, os.path.join(self.d, "kilit.py"), arg],
                              capture_output=True, text=True).returncode

    def yaz(self, rel, icerik="x"):
        yol = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        with open(yol, "w") as f:
            f.write(icerik)

    def test_temiz(self):
        self.assertEqual(self.kos("--kontrol"), 0)

    def test_degisen_dosya(self):
        self.yaz("animate/SKILL.md", "---\nname: animate\ndescription: y\n---\n")
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_yeni_skill(self):
        self.yaz("yeni/SKILL.md")
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_silinen_dosya(self):
        os.remove(os.path.join(self.d, "animate", "SKILL.md"))
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_symlink_dizin(self):
        os.makedirs(os.path.join(self.dis, "kotu"))
        with open(os.path.join(self.dis, "kotu", "SKILL.md"), "w") as f:
            f.write("---\nname: kotu\ndescription: x\n---\n")
        os.symlink(os.path.join(self.dis, "kotu"), os.path.join(self.d, "kotu"))
        self.assertEqual(self.kos("--kontrol"), 1)
        self.assertEqual(self.kos("--uret"), 1)

    def test_symlink_dosya(self):
        with open(os.path.join(self.dis, "r.md"), "w") as f:
            f.write("x")
        os.symlink(os.path.join(self.dis, "r.md"), os.path.join(self.d, "animate", "r.md"))
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_pycache_icine_gizleme(self):
        self.yaz("animate/__pycache__/notlar.md")
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_pycache_yalnizca_pyc(self):
        self.yaz("animate/__pycache__/x.cpython-312.pyc")
        self.assertEqual(self.kos("--kontrol"), 0)

    def test_alt_dizinde_kilit_adi(self):
        self.yaz("animate/kilit.json", "{}")
        self.assertEqual(self.kos("--kontrol"), 1)

    def test_pyc_disarida(self):
        self.yaz("animate/yardimci.pyc")
        self.assertEqual(self.kos("--kontrol"), 1)


if __name__ == "__main__":
    sonuc = unittest.main(exit=False, verbosity=1).result
    if sonuc.testsRun == 0:
        sys.exit(1)
    sys.exit(0 if sonuc.wasSuccessful() else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""schema/politika.py ve schema/degisim.py testleri.

Kaynak: kapanan PR #20'nin dali (claude/bonus-credit-usage-j6x5wv), commit
afc1ae4. Siniflar oradaki schema/test_schema.py'den degistirilmeden alindi;
main'de olmayan araclara (surum, vitrin, yenile) dayanan siniflar alinmadi.

    python3 schema/test_politika.py

Bagimlilik yok.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)


def _yukle(ad):
    yol = os.path.join(BURASI, ad + ".py")
    spec = importlib.util.spec_from_file_location("t_" + ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


denetim = _yukle("denetim")
politika = _yukle("politika")
degisim = _yukle("degisim")


class PolitikaTesti(unittest.TestCase):
    """schema/politika.py: her kural hem yakaliyor hem susuyor mu."""

    TEMIZ = (
        "name: CI\n"
        "on: [push, pull_request]\n"
        "permissions:\n  contents: read\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-24.04\n"
        "    timeout-minutes: 15\n"
        "    steps:\n"
        "      - uses: actions/checkout@v5\n"
        "      - uses: astral-sh/setup-uv@0123456789abcdef0123456789abcdef01234567  # v7.1.0\n"
        "      - run: |\n"
        "          set -euo pipefail\n"
        "          uv run pytest -v | tee log.txt\n")
    DEPENDABOT = (
        "version: 2\nupdates:\n"
        "  - package-ecosystem: github-actions\n    directory: /\n"
        "    schedule: {interval: monthly}\n"
        "    groups:\n      actions: {patterns: ['*']}\n")

    def _kurallar(self, dosyalar):
        return sorted({k for _, k, _ in politika.depo_bulgulari(dosyalar)})

    def setUp(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")

    def test_temiz_depo_pass(self):
        d = {".github/workflows/ci.yml": self.TEMIZ, ".github/dependabot.yml": self.DEPENDABOT}
        self.assertEqual(politika.depo_bulgulari(d), [])
        self.assertEqual(politika.durum([]), "PASS")

    def test_timeout_yoksa_uyarir(self):
        wf = self.TEMIZ.replace("    timeout-minutes: 15\n", "")
        b = politika.is_akisi_bulgulari(".github/workflows/ci.yml", wf)
        self.assertEqual([(s, k) for s, k, _ in b], [("WARN", "sure")])

    def test_ucuncu_taraf_etiketle_pinlenmemis(self):
        wf = self.TEMIZ.replace("0123456789abcdef0123456789abcdef01234567  # v7.1.0", "v7")
        self.assertEqual(self._kurallar({".github/workflows/ci.yml": wf,
                                         ".github/dependabot.yml": self.DEPENDABOT}), ["pin"])
        # GitHub'in kendi action'lari ve yerel action'lar kapsam disi.
        wf2 = self.TEMIZ.replace("      - uses: astral-sh/setup-uv@0123456789abcdef0123456789abcdef01234567  # v7.1.0\n",
                                 "      - uses: ./.github/actions/kur\n")
        self.assertEqual(politika.is_akisi_bulgulari("ci.yml", wf2), [])

    def test_pipefail_olmadan_test_borusu_fail(self):
        # tee 0 doner, varsayilan kabukta pipefail yok: dusen test yesil gorunur.
        wf = self.TEMIZ.replace("          set -euo pipefail\n", "")
        b = politika.is_akisi_bulgulari("ci.yml", wf)
        self.assertEqual([(s, k) for s, k, _ in b], [("FAIL", "boru")])
        self.assertEqual(politika.durum(b), "FAIL")

    def test_shell_bash_acikca_yazilinca_pipefail_var(self):
        wf = self.TEMIZ.replace("          set -euo pipefail\n", "").replace(
            "      - run: |\n", "      - shell: bash\n        run: |\n")
        self.assertEqual(politika.is_akisi_bulgulari("ci.yml", wf), [])

    def test_test_olmayan_boru_ve_mantiksal_veya_yakalanmaz(self):
        wf = self.TEMIZ.replace("          uv run pytest -v | tee log.txt\n",
                                "          uv run pytest -v || exit 1\n"
                                "          grep -m1 version pyproject.toml | cut -d= -f2\n").replace(
            "          set -euo pipefail\n", "")
        self.assertEqual(politika.is_akisi_bulgulari("ci.yml", wf), [])

    def test_guvensiz_ifade_kabukta_fail(self):
        wf = self.TEMIZ.replace("          uv run pytest -v | tee log.txt\n",
                                '          echo "${{ github.event.pull_request.title }}"\n')
        b = politika.is_akisi_bulgulari("ci.yml", wf)
        self.assertEqual([(s, k) for s, k, _ in b], [("FAIL", "enjeksiyon")])
        # Ayni deger env ile verilince kabuk onu veri olarak gorur.
        wf2 = self.TEMIZ.replace("          uv run pytest -v | tee log.txt\n",
                                 '          echo "$BASLIK"\n')
        self.assertEqual(politika.is_akisi_bulgulari("ci.yml", wf2), [])

    def test_pull_request_target_pr_kodunu_checkout_ederse_fail(self):
        wf = self.TEMIZ.replace("on: [push, pull_request]", "on: [pull_request_target]").replace(
            "      - uses: actions/checkout@v5\n",
            "      - uses: actions/checkout@v5\n        with:\n"
            "          ref: ${{ github.event.pull_request.head.sha }}\n")
        b = politika.is_akisi_bulgulari("ci.yml", wf)
        self.assertIn(("FAIL", "tetik"), [(s, k) for s, k, _ in b])
        wf2 = self.TEMIZ.replace("on: [push, pull_request]", "on: [pull_request_target]")
        self.assertEqual([(s, k) for s, k, _ in politika.is_akisi_bulgulari("ci.yml", wf2)],
                         [("WARN", "tetik")])

    def test_izin_tanimsizsa_uyarir(self):
        wf = self.TEMIZ.replace("permissions:\n  contents: read\n", "")
        b = politika.is_akisi_bulgulari("ci.yml", wf)
        self.assertEqual([(s, k) for s, k, _ in b], [("WARN", "izin")])

    def test_on_anahtari_bool_okunmaz(self):
        # YAML 1.1'de `on` true demek; okunursa tetikleyiciler kaybolur ve
        # pull_request_target hic gorulmez.
        wf = self.TEMIZ.replace("on: [push, pull_request]", "on:\n  pull_request_target:\n")
        self.assertIn("tetik", {k for _, k, _ in politika.is_akisi_bulgulari("ci.yml", wf)})

    def test_dependabot_yoksa_ve_gruplanmamissa(self):
        self.assertEqual(self._kurallar({".github/workflows/ci.yml": self.TEMIZ}), ["dependabot"])
        tek = self.DEPENDABOT.split("    groups:")[0]
        self.assertEqual(self._kurallar({".github/workflows/ci.yml": self.TEMIZ,
                                         ".github/dependabot.yml": tek}), ["grup"])

    def test_yoruma_yapismis_version_fail(self):
        # 11 deponun varsayilan dalindaki gercek bicim: YAML icin bu bir yorum.
        bozuk = ('# "uv" ekosistemi ikisini birlikte guncelliyor.version: 2\n'
                 + self.DEPENDABOT.split("\n", 1)[1])
        d = {".github/workflows/ci.yml": self.TEMIZ, ".github/dependabot.yml": bozuk}
        b = politika.depo_bulgulari(d)
        self.assertEqual([(s, k) for s, k, _ in b], [("FAIL", "dbgecersiz")])
        self.assertEqual(politika.durum(b), "FAIL")
        # Ayni icerik, version kendi satirinda: temiz.
        d[".github/dependabot.yml"] = bozuk.replace("guncelliyor.version: 2", "guncelliyor.\nversion: 2")
        self.assertEqual(politika.depo_bulgulari(d), [])

    def test_alt_dizindeki_kilit_kendi_girdisini_ister(self):
        # buradane: frontend/package-lock.json, backend/uv.lock.
        d = {".github/workflows/ci.yml": self.TEMIZ, ".github/dependabot.yml": self.DEPENDABOT,
             "frontend/package-lock.json": json.dumps({"packages": {"": {}, "node_modules/x": {}}}),
             "backend/uv.lock": "version = 1\n"}
        mesajlar = [m for _, k, m in politika.depo_bulgulari(d) if k == "kilit"]
        self.assertEqual(len(mesajlar), 2)
        ek = ("  - package-ecosystem: npm\n    directory: /frontend\n"
              "    schedule: {interval: monthly}\n    groups:\n      npm: {patterns: ['*']}\n"
              "  - package-ecosystem: uv\n    directory: backend/\n"
              "    schedule: {interval: monthly}\n    groups:\n      uv: {patterns: ['*']}\n")
        d[".github/dependabot.yml"] = self.DEPENDABOT + ek
        self.assertEqual(politika.depo_bulgulari(d), [])

    def test_bagimliliksiz_cargo_kilidi_sessiz(self):
        # godot-refcheck: sifir bagimlilik; kilidin guncellenecek bir sey yok.
        d = {".github/workflows/ci.yml": self.TEMIZ, ".github/dependabot.yml": self.DEPENDABOT,
             "Cargo.lock": "version = 4\n\n[[package]]\nname = \"godot-refcheck\"\n"}
        self.assertEqual(politika.depo_bulgulari(d), [])
        d["Cargo.lock"] += "\n[[package]]\nname = \"serde\"\n"
        self.assertEqual(self._kurallar(d), ["kilit"])

    def test_bozuk_yaml_fail_olur_sessizce_gecilmez(self):
        b = politika.is_akisi_bulgulari("ci.yml", "jobs: [\n")
        self.assertEqual([(s, k) for s, k, _ in b], [("FAIL", "yaml")])

    def test_bu_deponun_kendi_is_akislari_temiz(self):
        # Kurallari koyan depo onlara ilk uyan olmali.
        kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        b = politika.depo_bulgulari(politika.klondan_oku(kok))
        self.assertEqual(b, [], "\n".join(m for _, _, m in b))


class EnjeksiyonIfadeTesti(unittest.TestCase):
    """GUVENSIZ_IFADE: baglam `${{` nin hemen ardinda olmak zorunda degil."""

    def test_enjeksiyon_fonksiyon_ve_koseli_parantez_icinde(self):
        for ifade in ("${{ toJSON(github.event.issue.title) }}",
                      "${{ github.event['pull_request'].title }}",
                      "${{ github.event.workflow_run.pull_requests[0].head.ref }}",
                      "${{ github.event.workflow_run.head_repository.description }}",
                      "${{ format('{0}', github.head_ref) }}"):
            self.assertIsNotNone(politika.GUVENSIZ_IFADE.search(ifade), ifade)
        for ifade in ("${{ github.event.workflow_run.id }}", "${{ inputs.depo }}",
                      "${{ github.event_name }}", "${{ github.sha }}"):
            self.assertIsNone(politika.GUVENSIZ_IFADE.search(ifade), ifade)


class PolitikaFiksturTesti(unittest.TestCase):
    """schema/fikstur/politika: her kuralin bilinen-kotu ve bilinen-iyi ornegi.

    Bir kural eklendiginde ya da degistiginde iki sey birden bozulabilir:
    yakalamasi gerekeni kacirir (kotu vaka susar) ya da temiz bir seyi
    yakalar (iyi vaka ses verir). Beklenen bulgu kumesi birebir karsilastirilir,
    yani fazladan cikan tek bir WARN de testi kirar.
    """

    KOK = os.path.join(BURASI, "fikstur", "politika")

    def setUp(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")
        with open(os.path.join(self.KOK, "vakalar.json"), encoding="utf-8") as f:
            self.vakalar = json.load(f)

    def test_her_vaka_beklenen_bulguyu_birebir_verir(self):
        for ad, v in sorted(self.vakalar.items()):
            with self.subTest(vaka=ad):
                bulgu = politika.depo_bulgulari(politika.klondan_oku(os.path.join(self.KOK, ad)))
                self.assertEqual(sorted({(s, k) for s, k, _ in bulgu}),
                                 sorted(tuple(x) for x in v["beklenen"]), v["neden"])

    def test_vaka_dizinleri_ve_kayitlar_ayni(self):
        dizinler = {d for d in os.listdir(self.KOK) if os.path.isdir(os.path.join(self.KOK, d))}
        self.assertEqual(dizinler, set(self.vakalar))

    def test_her_kuralin_kotu_ve_iyi_vakasi_var(self):
        for kural in politika.KURAL_ADI:
            with self.subTest(kural=kural):
                self.assertTrue(any(kural in [k for _, k in v["beklenen"]]
                                    for ad, v in self.vakalar.items() if ad.startswith("kotu-")),
                                "%s icin yakalanmasi gereken vaka yok" % kural)
                self.assertTrue(any(kural in v["korur"]
                                    for ad, v in self.vakalar.items() if ad.startswith("iyi-")),
                                "%s icin yanlis alarm korumasi yok" % kural)

    def test_iyi_vakalar_bulgusuz(self):
        for ad, v in self.vakalar.items():
            if ad.startswith("iyi-"):
                self.assertEqual(v["beklenen"], [], ad)

    def test_fikstur_dizinindeki_kilit_bagimlilik_sayilmaz(self):
        kilit = json.dumps({"lockfileVersion": 3, "packages": {"": {}, "node_modules/a": {"version": "1"}}})
        temel = {".github/workflows/ci.yml": PolitikaTesti.TEMIZ, ".github/dependabot.yml": PolitikaTesti.DEPENDABOT}
        for yol in ("tests/fixtures/package-lock.json", "schema/fikstur/x/package-lock.json",
                    "a/testdata/package-lock.json"):
            self.assertNotIn("kilit", [k for _, k, _ in politika.depo_bulgulari(dict(temel, **{yol: kilit}))], yol)
        # Yalnizca tam dizin adi: "fixturesx" bir fikstur dizini degil.
        self.assertIn("kilit", [k for _, k, _ in politika.depo_bulgulari(
            dict(temel, **{"fixturesx/package-lock.json": kilit}))])


class DegisimTesti(unittest.TestCase):
    """schema/degisim.py: toplu donusumun diff'i, donusumun kendisinden bagimsiz.

    25 Eylul 2026: action'lari SHA'ya sabitleyen regex, "istege bagli satir
    sonu yorumu" kalibindaki bosluk sinifiyla satir sonunu gecip alttaki yorum satirini da "satir sonu yorumu" sandi;
    alti depoda sekiz yorum satiri silindi. Testler, politika ve CI yesildi.
    """

    AKIS = (
        "name: CI\n"
        "on: [push]\n"
        "permissions:\n  contents: read\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-24.04\n"
        "    timeout-minutes: 10\n"
        "    steps:\n"
        "      - uses: actions/checkout@v5\n"
        "      - uses: astral-sh/setup-uv@v7\n"
        "\n"
        "      # Kilit dosyasi degismeden kurulum: uv.lock ile pyproject\n"
        "      # ayrisirsa burada durur.\n"
        "      - run: uv sync --locked\n")
    SHA = "37802adc94f370d6bfd71619e3f0bf239e1f3b78"
    USES = [r"^\s*(-\s*)?uses:"]

    def setUp(self):
        if shutil.which("git") is None:
            self.skipTest("git yok")
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _depo(self, dosyalar=None, ad="depo"):
        kok = os.path.join(self.tmp, ad)
        os.makedirs(kok)
        for yol, metin in (dosyalar or {".github/workflows/ci.yml": self.AKIS}).items():
            tam = os.path.join(kok, yol)
            os.makedirs(os.path.dirname(tam), exist_ok=True)
            with open(tam, "w", encoding="utf-8", newline="") as f:
                f.write(metin)
        for k in (["init", "-q"], ["add", "-A"],
                  ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "taban"]):
            subprocess.run(["git", "-C", kok, *k], check=True, capture_output=True)
        return kok

    def _yaz(self, kok, yol, metin):
        tam = os.path.join(kok, yol)
        os.makedirs(os.path.dirname(tam) or kok, exist_ok=True)
        with open(tam, "w", encoding="utf-8", newline="") as f:
            f.write(metin)

    def _oku(self, kok, yol=".github/workflows/ci.yml"):
        with open(os.path.join(kok, yol), encoding="utf-8", newline="") as f:
            return f.read()

    def _kurallar(self, kok, dosya=(".github/workflows/*.yml",), silinebilir=None):
        s = degisim.depo_denetle(kok, "HEAD", list(dosya),
                                 self.USES if silinebilir is None else silinebilir)
        return sorted({b["kural"] for b in s["bulgular"]}), s

    # --- regresyon: olayin kendisi -------------------------------------------------

    def test_olaydaki_regex_yorum_satirini_yutar_ve_fail(self):
        kok = self._depo()
        hatali = re.sub(r"(uses:\s*astral-sh/setup-uv@)v7(\s*#[^\n]*)?",
                        r"\g<1>%s # v7.6.0" % self.SHA, self._oku(kok))
        self._yaz(kok, ".github/workflows/ci.yml", hatali)
        kurallar, _ = self._kurallar(kok)
        self.assertIn("yorum", kurallar)
        self.assertIn("bos_satir", kurallar)

    def test_duzeltilmis_regex_pass(self):
        kok = self._depo()
        dogru = re.sub(r"(uses:[ \t]*astral-sh/setup-uv@)v7([ \t]*#[^\n]*)?",
                       r"\g<1>%s # v7.6.0" % self.SHA, self._oku(kok))
        self._yaz(kok, ".github/workflows/ci.yml", dogru)
        kurallar, s = self._kurallar(kok)
        self.assertEqual(kurallar, [])
        self.assertEqual((s["eklenen"], s["silinen"]), (1, 1))

    # --- negatifler ------------------------------------------------------------------

    def test_satir_sonu_yorumu_kaybolursa_fail(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS.replace(
            "setup-uv@v7\n", "setup-uv@v7  # 0.9 ile kilit bicimi degisti\n")})
        metin = self._oku(kok).replace("setup-uv@v7  # 0.9 ile kilit bicimi degisti",
                                       "setup-uv@%s # v7.6.0" % self.SHA)
        self._yaz(kok, ".github/workflows/ci.yml", metin)
        self.assertEqual(self._kurallar(kok)[0], ["yorum"])

    def test_yorum_korunursa_pass(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS.replace(
            "setup-uv@v7\n", "setup-uv@v7  # 0.9 ile kilit bicimi degisti\n")})
        metin = self._oku(kok).replace("setup-uv@v7  #", "setup-uv@%s  # v7.6.0;" % self.SHA)
        self._yaz(kok, ".github/workflows/ci.yml", metin)
        self.assertEqual(self._kurallar(kok)[0], [])

    def test_acikca_hedeflenen_yorum_silinebilir(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml",
                  self._oku(kok).replace("      # ayrisirsa burada durur.\n", ""))
        self.assertEqual(self._kurallar(kok)[0], ["yorum"])
        self.assertEqual(self._kurallar(kok, silinebilir=self.USES + [r"^\s*# ayrisirsa"])[0], [])

    def test_bilerek_bozuk_fikstur_atlanir(self):
        kok = self._depo()
        self._yaz(kok, "fikstur/bozuk.json", "{\n")
        s = degisim.depo_denetle(kok, "HEAD", [], [], ["fikstur/*"])
        self.assertEqual(s["bulgular"], [])
        s = degisim.depo_denetle(kok, "HEAD", [], [])
        self.assertEqual([b["kural"] for b in s["bulgular"]], ["sozdizimi"])

    def test_izinsiz_satir_silme_fail(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace("      - run: uv sync --locked\n", ""))
        self.assertEqual(self._kurallar(kok)[0], ["beklenmeyen"])

    def test_silinebilir_yoksa_yalnizca_ekleme(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml",
                  self._oku(kok).replace("setup-uv@v7", "setup-uv@%s # v7" % self.SHA))
        self.assertEqual(self._kurallar(kok, silinebilir=[])[0], ["beklenmeyen"])

    def test_yalnizca_bosluk_degisimi_fail(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace("run: uv sync", "run:  uv sync"))
        # "run:  uv sync" ile "run: uv sync" strip'te farkli; ic bosluk "beklenmeyen" sayilir.
        self.assertEqual(self._kurallar(kok)[0], ["beklenmeyen"])
        kok2 = self._depo(ad="iki")
        self._yaz(kok2, ".github/workflows/ci.yml", self._oku(kok2).replace(
            "      - run: uv sync --locked\n", "      - run: uv sync --locked   \n"))
        self.assertEqual(self._kurallar(kok2)[0], ["bosluk"])

    def test_crlf_donusumu_fail(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace("\n", "\r\n"))
        self.assertIn("bosluk", self._kurallar(kok)[0])

    def test_son_satir_sonu_kaybolursa_fail(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).rstrip("\n"))
        self.assertIn("son_satir", self._kurallar(kok)[0])

    def test_zaten_eksik_son_satir_gerileme_degil(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS.rstrip("\n")})
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok) + "  # son")
        self.assertNotIn("son_satir", self._kurallar(kok)[0])

    def test_kapsam_disi_dosya_fail(self):
        kok = self._depo()
        self._yaz(kok, "README.md", "yeni\n")
        self.assertEqual(self._kurallar(kok)[0], ["dosya_disi"])

    def test_dosya_silme_ve_ad_degistirme_fail(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS, ".github/workflows/b.yml": self.AKIS})
        os.remove(os.path.join(kok, ".github/workflows/b.yml"))
        self.assertIn("silme", self._kurallar(kok)[0])
        kok2 = self._depo(ad="iki")
        subprocess.run(["git", "-C", kok2, "mv", ".github/workflows/ci.yml", ".github/workflows/test.yml"],
                       check=True)
        self.assertIn("silme", self._kurallar(kok2)[0])

    def test_bozuk_yaml_fail(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok) + "      - run: [\n")
        self.assertIn("sozdizimi", self._kurallar(kok)[0])

    def test_bozuk_json_fail(self):
        kok = self._depo({"project-meta.json": '{"a": 1}\n'})
        self._yaz(kok, "project-meta.json", '{"a": 1,}\n')
        self.assertIn("sozdizimi", self._kurallar(kok, dosya=("*.json",), silinebilir=[".*"])[0])

    def test_politika_gerilemesi_fail(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok) + "      - run: uv run pytest | tee log\n")
        kurallar, s = self._kurallar(kok)
        self.assertEqual(kurallar, ["politika"])
        self.assertIn("boru", s["bulgular"][0]["mesaj"])

    def test_warn_artisi_fail(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml",
                  self._oku(kok).replace("    timeout-minutes: 10\n", ""))
        kurallar, _ = self._kurallar(kok, silinebilir=[r"timeout-minutes"])
        self.assertEqual(kurallar, ["politika"])

    def test_patlama_yaricapi(self):
        kokler = []
        for ad in ("a", "b", "c"):
            k = self._depo(ad=ad)
            self._yaz(k, ".github/workflows/ci.yml", self._oku(k) + "# ek\n")
            kokler.append(k)
        kokler.append(self._depo(ad="d"))
        sonuc, bakilamayan, patlama = degisim.denetle(kokler, "HEAD", [".github/workflows/*.yml"],
                                                      self.USES, azami_depo=2)
        self.assertIsNotNone(patlama)
        self.assertEqual([s["durum"] for s in sonuc], ["FAIL", "FAIL", "FAIL", "PASS"])
        self.assertEqual(bakilamayan, {})
        sonuc, _, patlama = degisim.denetle(kokler, "HEAD", [".github/workflows/*.yml"],
                                            self.USES, azami_depo=3)
        self.assertIsNone(patlama)

    def test_git_olmayan_dizin_ve_yok_taban_bakilamadi(self):
        bos = os.path.join(self.tmp, "bos")
        os.makedirs(bos)
        _, bakilamayan, _ = degisim.denetle([bos], "HEAD")
        self.assertIn("bos", bakilamayan)
        kok = self._depo()
        _, bakilamayan, _ = degisim.denetle([kok], "yok-boyle-bir-dal")
        self.assertIn("depo", bakilamayan)

    def test_cli_cikis_kodlari(self):
        kok = self._depo()
        self.assertEqual(degisim.main(["--kok", kok, "--taban", "HEAD"]), 0)
        self._yaz(kok, "x.txt", "x\n")
        self.assertEqual(degisim.main(["--kok", kok, "--taban", "HEAD", "--dosya", "*.yml"]), 1)
        self.assertEqual(degisim.main(["--kok", os.path.join(self.tmp, "yok"), "--taban", "HEAD"]), 2)

    # --- 26 Eylul bagimsiz incelemesinin buldugu delikler (her biri once kirmizi) --------

    def test_gitattributes_binary_satir_kontrolunu_kapatamaz(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS, ".gitattributes": "*.yml -diff\n"})
        self._yaz(kok, ".github/workflows/ci.yml",
                  self._oku(kok).replace("      # ayrisirsa burada durur.\n", "").replace("\n\n", "\n"))
        kurallar, _ = self._kurallar(kok)
        self.assertIn("yorum", kurallar)
        self.assertIn("bos_satir", kurallar)

    def test_satir_sonu_yorumu_alt_dize_eslesmesiyle_kurtulmaz(self):
        kok = self._depo({".github/workflows/ci.yml": self.AKIS.replace(
            "actions/checkout@v5\n", "actions/setup-python@v5 # python\n")})
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace(
            "actions/setup-python@v5 # python", "actions/setup-python@%s" % self.SHA))
        self.assertEqual(self._kurallar(kok)[0], ["yorum"])

    def test_kesme_isaretli_satirin_yorumu_da_sayilir(self):
        self.assertEqual(degisim.satir_sonu_yorumu("  name: Don't skip # keep"), "keep")
        self.assertIsNone(degisim.satir_sonu_yorumu("  run: echo 'a # b'"))
        self.assertEqual(degisim.satir_sonu_yorumu("  run: echo 'a # b'  # c"), "c")

    def test_bosluklu_dosya_adi_yorum_denetiminden_kacmaz(self):
        yol = ".github/workflows/my file.yml"
        kok = self._depo({yol: self.AKIS.replace("setup-uv@v7\n", "setup-uv@v7  # zeta nedeni\n")})
        self._yaz(kok, yol, self._oku(kok, yol).replace("setup-uv@v7  # zeta nedeni", "setup-uv@%s" % self.SHA))
        self.assertEqual(self._kurallar(kok)[0], ["yorum"])

    def test_izlenmeyen_ignore_kilit_politikayi_kirletmez(self):
        if politika.yaml_yok():
            self.skipTest("PyYAML yok")
        kok = self._depo({".github/workflows/ci.yml": self.AKIS, ".gitignore": "build/\n",
                          ".github/dependabot.yml": PolitikaTesti.DEPENDABOT})
        self._yaz(kok, "build/package-lock.json", json.dumps(
            {"lockfileVersion": 3, "packages": {"": {}, "node_modules/a": {"version": "1"}}}))
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok) + "# ek\n")
        self.assertEqual(self._kurallar(kok)[0], [])

    def test_json_yeniden_uretimi_bosluk_sayilmaz(self):
        kok = self._depo({"project-meta.json": '{\n  "x": {\n    "b": [\n      1\n    ]\n  }\n}\n'})
        self._yaz(kok, "project-meta.json", '{\n  "b": [\n    1\n  ]\n}\n')
        self.assertEqual(self._kurallar(kok, dosya=("project-meta.json",), silinebilir=[".*"])[0], [])

    def test_ic_ice_depo_bakilamadi(self):
        kok = self._depo()
        alt = os.path.join(kok, "alt")
        os.makedirs(alt)
        subprocess.run(["git", "-C", alt, "init", "-q"], check=True)
        self._yaz(alt, "x.txt", "x\n")
        _, bakilamayan, _ = degisim.denetle([kok], "HEAD")
        self.assertIn("depo", bakilamayan)

    def test_kip_degisimi_fail(self):
        kok = self._depo()
        os.chmod(os.path.join(kok, ".github/workflows/ci.yml"), 0o755)
        subprocess.run(["git", "-C", kok, "config", "core.fileMode", "true"], check=True)
        self.assertIn("silme", self._kurallar(kok)[0])

    def test_yildiz_dizin_sinirini_gecmez(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/alt/kotu.yml", "name: x\n")
        self.assertEqual(self._kurallar(kok)[0], ["dosya_disi"])
        self.assertTrue(degisim.kaliba_uyar("a/b/c.yml", "a/**"))
        self.assertTrue(degisim.kaliba_uyar("project-meta.json", "project-meta.json"))

    # --- yanlis alarm korumalari -------------------------------------------------------

    def test_yalnizca_ekleme_pass(self):
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace(
            "    timeout-minutes: 10\n",
            "    # olculen en uzun kosu 41 sn\n    timeout-minutes: 10\n\n"))
        self.assertEqual(self._kurallar(kok)[0], [])

    def test_uzatilan_yorum_satiri_kayip_sayilmaz(self):
        # 26 Eylul: denetim.yml'deki bir yorumun sonuna gerekce eklendi; git
        # bunu "silindi + eklendi" diye gosterir, metin ise aynen duruyor.
        kok = self._depo()
        self._yaz(kok, ".github/workflows/ci.yml", self._oku(kok).replace(
            "      # ayrisirsa burada durur.\n", "      # ayrisirsa burada durur. Ek gerekce.\n"))
        self.assertEqual(self._kurallar(kok)[0], [])
        # ...ama metni degisen yorum hala kayiptir.
        kok2 = self._depo(ad="iki")
        self._yaz(kok2, ".github/workflows/ci.yml", self._oku(kok2).replace(
            "      # ayrisirsa burada durur.\n", "      # baska bir sey.\n"))
        self.assertEqual(self._kurallar(kok2)[0], ["yorum"])
        # Bos bir "#" satiri her yorumun "icinde" degildir.
        kok3 = self._depo({".github/workflows/ci.yml": self.AKIS.replace(
            "      # ayrisirsa burada durur.\n", "      # ayrisirsa burada durur.\n      #\n")}, ad="uc")
        self._yaz(kok3, ".github/workflows/ci.yml", self._oku(kok3).replace("      #\n", ""))
        self.assertEqual(self._kurallar(kok3)[0], ["yorum"])

    def test_yer_degistiren_satir_silme_sayilmaz(self):
        kok = self._depo()
        m = self._oku(kok)
        blok = ("      # Kilit dosyasi degismeden kurulum: uv.lock ile pyproject\n"
                "      # ayrisirsa burada durur.\n")
        m = m.replace(blok, "").replace("      - uses: actions/checkout@v5\n",
                                        blok + "      - uses: actions/checkout@v5\n")
        self._yaz(kok, ".github/workflows/ci.yml", m)
        self.assertEqual(self._kurallar(kok)[0], [])

    def test_tirnak_icindeki_diyez_yorum_degil(self):
        self.assertIsNone(degisim.satir_sonu_yorumu('      run: echo "a # b"'))
        self.assertEqual(degisim.satir_sonu_yorumu("      uses: x/y@v1  # neden"), "neden")
        self.assertIsNone(degisim.satir_sonu_yorumu("      uses: x/y@v1#frag"))

    def test_eksi_eksi_ile_baslayan_icerik_baslik_sanilmaz(self):
        fark = ("diff --git a/x.yml b/x.yml\n--- a/x.yml\n+++ b/x.yml\n@@ -1 +1 @@\n"
                "--- belge\n+yeni\n")
        d = degisim.diff_ayristir(fark)
        self.assertEqual(d["x.yml"]["silinen"], ["-- belge"])
        self.assertEqual(d["x.yml"]["eklenen"], ["yeni"])

    def test_degismeyen_depo_pass_ve_raporlanir(self):
        kok = self._depo()
        s = degisim.depo_denetle(kok, "HEAD", [], [])
        self.assertEqual((s["durum"], s["degisti"]), ("PASS", False))


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""schema/ altindaki araclarin testleri.

Neden var: bu betikler artik yuk tasiyor. `yenile.yml` haftada bir
`uret.py`'nin ciktisini 24 deponun icine yaziyor, `denetim.py` her gun
neyin bozuk oldugunu soyluyor. Bir gerileme burada sessizce gecerse yanlis
metadata yayimlanir ya da bozuk olan bir sey "temiz" gorunur.

Buradaki testlerin cogu **gercekten yasanmis** bir hatadan turedi; her
birinin basinda hangi hata oldugu yaziyor. Hic olmamis bir seyi test
etmiyoruz.

    python3 schema/test_schema.py           # ya da
    python3 -m unittest discover -s schema -p "test_*.py"

Bagimlilik yok.
"""

import importlib.util
import json
import os
import re
import sys
import shutil
import subprocess
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))


def _yukle(ad):
    yol = os.path.join(BURASI, ad + ".py")
    spec = importlib.util.spec_from_file_location("t_" + ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


uret = _yukle("uret")
testler = _yukle("testler")
koruma = _yukle("koruma")
dogrula = _yukle("dogrula")
haftalik = _yukle("haftalik")
denetim = _yukle("denetim")
vitrin = _yukle("vitrin")
derle = _yukle("derle")
politika = _yukle("politika")


class GeciciDepo:
    """Diskte kucuk bir sahte depo."""

    def __enter__(self):
        self.yol = tempfile.mkdtemp(prefix="meta-test-")
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.yol, ignore_errors=True)

    def yaz(self, goreli, icerik=""):
        tam = os.path.join(self.yol, goreli.replace("/", os.sep))
        os.makedirs(os.path.dirname(tam), exist_ok=True)
        with open(tam, "w", encoding="utf-8", newline="\n") as f:
            f.write(icerik)
        return tam

    def json_yaz(self, goreli, veri):
        return self.yaz(goreli, json.dumps(veri, indent=2, ensure_ascii=False))


class SurumTesti(unittest.TestCase):
    """Bildirilen surum nereden okunuyor."""

    def test_pyproject_once_gelir(self):
        with GeciciDepo() as d:
            d.yaz("pyproject.toml", '[project]\nname = "x"\nversion = "2.3.4"\n')
            d.json_yaz("package.json", {"version": "9.9.9"})
            self.assertEqual(uret.surum(d.yol), "2.3.4")

    def test_eklenti_manifesti_package_jsondan_once(self):
        # Yasanan hata: turkce-ajanlar surumunu .claude-plugin/plugin.json
        # icinde 0.3.0 diye bildiriyor, package.json ise yalnizca modul
        # turunu sabitlemek icin var ve 0.0.0 tasiyor. Uretici yalnizca
        # package.json'a baktigi icin metadata "surum yok" diyordu.
        with GeciciDepo() as d:
            d.json_yaz(".claude-plugin/plugin.json", {"version": "0.3.0"})
            d.json_yaz("package.json", {"version": "0.0.0", "private": True})
            self.assertEqual(uret.surum(d.yol), "0.3.0")

    def test_sifirlar_yer_tutucudur(self):
        with GeciciDepo() as d:
            d.json_yaz("package.json", {"version": "0.0.0"})
            self.assertIsNone(uret.surum(d.yol))

    def test_private_paket_de_surum_bildirir(self):
        # Yasanan hata: "private": true bayragini olcut yapinca masal'in
        # 1.0.0 surumu metadata'dan dustu. Bir uygulama kutuphane olmadigi
        # icin private olur; bu surumunu bildirmedigi anlamina gelmez.
        with GeciciDepo() as d:
            d.json_yaz("package.json", {"version": "1.0.0", "private": True})
            self.assertEqual(uret.surum(d.yol), "1.0.0")

    def test_manifest_yoksa_en_yeni_etiket(self):
        with GeciciDepo() as d:
            ortam = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                         GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            for komut in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "bos"],
                          ["tag", "v1.4.0"]):
                subprocess.run(["git", "-C", d.yol] + komut, check=True,
                               env=ortam, capture_output=True)
            self.assertEqual(uret.surum(d.yol), "1.4.0")


class MedyaTesti(unittest.TestCase):
    """Metadata yalnizca README'nin gercekten gosterdigi yerel gorselleri sayar."""

    def test_uzak_ve_data_urlleri_sayilmaz(self):
        with GeciciDepo() as d:
            d.yaz("README.md",
                  "![a](assets/hero.png)\n"
                  "![b](https://img.shields.io/badge/x-y.svg)\n"
                  '<img src="data:image/png;base64,AAAA">\n'
                  "![c](docs/ekran.png)\n")
            d.yaz("assets/hero.png", "x")
            d.yaz("docs/ekran.png", "x")
            m = uret.medya(d.yol)
            self.assertEqual(m["hero"], "assets/hero.png")
            self.assertNotIn("https://img.shields.io/badge/x-y.svg", json.dumps(m))
            self.assertNotIn("data:image", json.dumps(m))

    def test_animasyonlu_webp_ekran_goruntusu_sayilmaz(self):
        # nova-drift'in oynanis kaydi animasyonlu bir WebP; ekran goruntusu
        # listesine dusuyordu ve gifs bos kaliyordu.
        vp8x = lambda bayrak: b"RIFF\x00\x00\x00\x00WEBPVP8X\x0a\x00\x00\x00" + bytes([bayrak]) + b"\x00" * 9
        with GeciciDepo() as d:
            d.yaz("README.md", "![a](assets/oyun.webp)\n![b](assets/kare.webp)\n")
            os.makedirs(os.path.join(d.yol, "assets"), exist_ok=True)
            with open(os.path.join(d.yol, "assets/oyun.webp"), "wb") as f:
                f.write(vp8x(0x02))
            with open(os.path.join(d.yol, "assets/kare.webp"), "wb") as f:
                f.write(vp8x(0x00))
            m = uret.medya(d.yol)
            self.assertEqual(m["gifs"], ["assets/oyun.webp"])
            self.assertEqual(m["screenshots"], ["assets/kare.webp"])

    def test_readme_yoksa_hero_yok(self):
        with GeciciDepo() as d:
            self.assertIsNone(uret.medya(d.yol)["hero"])


class SemaTesti(unittest.TestCase):
    """Sema yorumlayicisi gercekten reddediyor mu."""

    def setUp(self):
        with open(dogrula.SEMA, encoding="utf-8") as f:
            self.sema = json.load(f)
        self.gecerli = {
            "schema_version": "1.0.0", "id": "x", "owner": "Furkiozknn",
            "repository": "https://github.com/Furkiozknn/x",
            "status": "active", "category": "developer-tool",
            "summary": "bir sey",
            "provenance": {"generated_at": "2026-09-22", "generator": "t", "rule": "t"},
        }

    def _hatalar(self, veri):
        h = []
        dogrula._sema_dogrula(veri, self.sema, "", h)
        return h

    def test_gecerli_belge_gecer(self):
        self.assertEqual(self._hatalar(self.gecerli), [])

    def test_zorunlu_alan_eksikse_duser(self):
        v = dict(self.gecerli)
        del v["summary"]
        self.assertTrue(any("summary" in h for h in self._hatalar(v)))

    def test_status_kumesi_kapali(self):
        v = dict(self.gecerli, status="yayinda")
        self.assertTrue(self._hatalar(v))

    def test_bilinmeyen_alan_kabul_edilmez(self):
        # Sema additionalProperties: false. Uydurulan bir alan sessizce
        # iceri girmemeli -- metadata'nin butun degeri bu.
        v = dict(self.gecerli, indirme_sayisi=12000)
        self.assertTrue(self._hatalar(v))

    def test_tests_sayi_ister(self):
        v = dict(self.gecerli, tests={"count": "cok", "source": "x", "measured": "2026-09-22"})
        self.assertTrue(self._hatalar(v))


class GerceklikTesti(unittest.TestCase):
    """Dosyanin iddia ettigi sey depoda gercekten var mi."""

    def _olc(self, depo, meta):
        h, u = [], []
        dogrula._gercek_dogrula(depo, meta, h, u)
        return h

    def test_olmayan_gorsel_yakalanir(self):
        with GeciciDepo() as d:
            meta = {"id": os.path.basename(d.yol),
                    "media": {"hero": "assets/yok.png", "screenshots": [],
                              "gifs": [], "videos": []}}
            self.assertTrue(any("hero" in h for h in self._olc(d.yol, meta)))

    def test_is_akisi_listesi_diskle_ayrisirsa_yakalanir(self):
        # Yasanan hata: dort depoya yeni bir is akisi eklendi ve
        # ci.workflows listeleri bir adim geride kaldi. Bunu soyleyen
        # kontrol buydu.
        with GeciciDepo() as d:
            d.yaz(".github/workflows/ci.yml", "name: ci\n")
            d.yaz(".github/workflows/yeni.yml", "name: yeni\n")
            meta = {"id": os.path.basename(d.yol), "ci": {"workflows": ["ci.yml"]}}
            self.assertTrue(any("ci.workflows" in h for h in self._olc(d.yol, meta)))

    def test_kaynaksiz_test_sayisi_kabul_edilmez(self):
        with GeciciDepo() as d:
            meta = {"id": os.path.basename(d.yol),
                    "tests": {"count": 500, "source": "", "measured": "2026-09-22"}}
            self.assertTrue(any("tests.source" in h for h in self._olc(d.yol, meta)))

    def test_id_klasor_adiyla_ayni_olmali(self):
        with GeciciDepo() as d:
            self.assertTrue(any("id" in h for h in self._olc(d.yol, {"id": "baska-depo"})))


class AyrismaTesti(unittest.TestCase):
    """Metadata'nin mekanik yarisi canli gercekle karsilastiriliyor."""

    def setUp(self):
        self.repo = {"name": "x", "archived": False, "topics": ["a", "b"],
                     "description": "bir sey", "license": {"spdx_id": "MIT"},
                     "homepage": "https://ornek.gecerli/"}
        self.meta = {"summary": "bir sey", "topics": ["b", "a"], "license": "MIT",
                     "homepage": "https://ornek.gecerli/", "status": "active",
                     "ci": {"workflows": ["ci.yml"]},
                     "docs": {"readme": "README.md", "license_file": "LICENSE"}}
        self.akislar = ["ci.yml"]
        self.kok = {"README.md", "LICENSE"}

    def test_tutuyorsa_bulgu_yok(self):
        self.assertEqual(
            denetim._ayrismalar(self.meta, self.repo, self.akislar, self.kok), [])

    def test_description_ayrismasi(self):
        self.repo["description"] = "baska bir sey"
        self.assertTrue(denetim._ayrismalar(self.meta, self.repo, self.akislar, self.kok))

    def test_topic_eklenince_yakalanir(self):
        self.repo["topics"] = ["a", "b", "c"]
        self.assertTrue(denetim._ayrismalar(self.meta, self.repo, self.akislar, self.kok))

    def test_arsivlenen_depo_status_guncellenmeli(self):
        self.repo["archived"] = True
        self.assertTrue(denetim._ayrismalar(self.meta, self.repo, self.akislar, self.kok))

    def test_noassertion_lisans_null_sayilir(self):
        self.repo["license"] = {"spdx_id": "NOASSERTION"}
        self.meta["license"] = None
        self.assertEqual(
            denetim._ayrismalar(self.meta, self.repo, self.akislar, self.kok), [])


class ProfilSayilariTesti(unittest.TestCase):
    """Profil sayfasinin manset sayilari metadata ile tutuyor mu."""

    def _metalar(self, kanca=115, masal=92):
        return {
            "kanca": ({"name": "kanca", "archived": False},
                      {"tests": {"count": kanca}}),
            "masal": ({"name": "masal", "archived": False},
                      {"tests": {"count": masal}}),
        }

    def _sahte_profil(self, toplam, satirlar):
        d = tempfile.mkdtemp(prefix="profil-test-")
        with open(os.path.join(d, "TESTLER.md"), "w", encoding="utf-8") as f:
            f.write("# Where the %s comes from\n" % toplam)
        with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
            f.write("2 public repositories, %s tests\n\n" % toplam)
            for ad, n in satirlar:
                f.write("| x | **[%s](https://github.com/Furkiozknn/%s)** | bir sey | `%d` |\n"
                        % (ad, ad, n))
        return d

    def _olc(self, toplam, satirlar, metalar, depo_sayisi=2):
        d = self._sahte_profil(toplam, satirlar)
        eski = denetim.KOK
        try:
            denetim.KOK = __import__("pathlib").Path(d)
            return denetim._profil_sayilari(metalar, depo_sayisi)
        finally:
            denetim.KOK = eski
            shutil.rmtree(d, ignore_errors=True)

    def test_tutuyorsa_bulgu_yok(self):
        self.assertEqual(
            self._olc("207", [("kanca", 115), ("masal", 92)], self._metalar()), [])

    def test_toplam_kayinca_yakalanir(self):
        b = self._olc("207", [("kanca", 122), ("masal", 92)], self._metalar(kanca=122))
        self.assertTrue(any("metadata toplami" in x[2] for x in b))

    def test_toplam_tutarken_satirlar_kayabilir(self):
        # Asil sebep bu: iki depo ters yonde kayarsa toplam farki yutar,
        # ama satira bakan okuyucu yanlis sayiyi gorur.
        b = self._olc("207", [("kanca", 115), ("masal", 92)],
                      self._metalar(kanca=122, masal=85))
        mesajlar = " ".join(x[2] for x in b)
        self.assertNotIn("metadata toplami", mesajlar)
        self.assertIn("kanca", mesajlar)
        self.assertIn("masal", mesajlar)

    def test_tabloda_olmayan_depo_yakalanir(self):
        b = self._olc("207", [("kanca", 115)], self._metalar())
        self.assertTrue(any("masal" in x[2] for x in b))

    def test_depo_sayisi_ayrismasi(self):
        b = self._olc("207", [("kanca", 115), ("masal", 92)], self._metalar(),
                      depo_sayisi=3)
        self.assertTrue(any("public repo" in x[2] for x in b))


class TaslakTesti(unittest.TestCase):
    """Gonderi taslaklari: her cumlenin arkasinda bir veri olmali."""

    def setUp(self):
        self.meta = {
            "id": "kanca", "repository": "https://github.com/Furkiozknn/kanca",
            "version": "0.5.2",
            "media": {"hero": "docs/01.png"},
            "tests": {"count": 115, "source": "CI", "measured": "2026-09-22"},
            "social": {"headline": "Tek tus, tek ip.",
                       "hashtags": ["godot", "gamedev", "indiedev", "godot4", "fazla"],
                       "primary_link": "https://github.com/Furkiozknn/kanca"},
        }

    def test_kisa_taslak_280i_asmaz(self):
        commitler = [{"tur": "feat"}] * 40
        t = haftalik._taslak(self.meta, commitler, [])
        self.assertLessEqual(len(t["kisa"]), 280)

    def test_veri_yoksa_cumle_de_yok(self):
        yalin = {"id": "x", "repository": "https://github.com/Furkiozknn/x",
                 "social": {"headline": None, "hashtags": [], "primary_link": None}}
        t = haftalik._taslak(yalin, [], [])
        self.assertNotIn("test", t["uzun"])
        self.assertNotIn("commit", t["uzun"])

    def test_release_varsa_basa_gecer(self):
        r = [{"tag": "v0.5.2", "ad": "x", "url": "u", "tarih": "2026-09-22"}]
        self.assertTrue(haftalik._taslak(self.meta, [], r)["kisa"].startswith("kanca v0.5.2"))

    def test_gorsel_adresi_metadatadan_turer(self):
        self.assertEqual(
            haftalik._gorsel(self.meta, "main"),
            "https://raw.githubusercontent.com/Furkiozknn/kanca/main/docs/01.png")

    def test_hero_yoksa_gorsel_yok(self):
        self.assertIsNone(haftalik._gorsel({"id": "x", "media": {}}, "main"))


class RaporTesti(unittest.TestCase):
    """Denetim raporu ve parmak izi."""

    def test_temiz_durumda_tek_satir(self):
        self.assertIn("temiz", denetim._rapor([], {}, 24))

    def test_iskelet_yazili_alanlari_bos_birakir(self):
        # Iskeletin tamami dolu gelirse bir sonraki oturum onu dogru
        # sanip birakir. Bos alan, yazilmasi gereken alandir.
        i = denetim._iskelet({"archived": False})
        self.assertIsNone(i["category"])
        self.assertEqual(i["key_features"], [])
        self.assertIsNone(i["social"]["headline"])

    def test_arsivli_depo_iskeleti_archived_der(self):
        self.assertEqual(denetim._iskelet({"archived": True})["status"], "archived")

    def test_bulgular_turlerine_gore_grupllanir(self):
        b = [("a", "ci", "kirmizi"), ("b", "belge", "LICENSE yok")]
        m = denetim._rapor(b, {}, 24)
        self.assertIn("CI", m)
        self.assertIn("Temel belge eksik", m)


class KorumaTesti(unittest.TestCase):
    """Tazeleme deger kaybettiriyorsa push edilmemeli."""

    def _meta(self, **degis):
        m = {"version": "1.0.0", "summary": "bir sey", "license": "MIT",
             "primary_language": "Python",
             "tests": {"count": 10, "source": "CI", "measured": "2026-09-22"},
             "media": {"hero": "assets/hero.png"},
             "key_features": ["a"], "topics": ["x"], "platform": ["web"],
             "technologies": ["Python"],
             "social": {"headline": "bir cumle"},
             "docs": {"readme": "README.md", "license_file": "LICENSE"}}
        m.update(degis)
        return m

    def test_ayni_dosya_kayipsiz(self):
        self.assertEqual(koruma.kayip_alanlar(self._meta(), self._meta()), [])

    def test_surum_dususu_yakalanir(self):
        # Yasanan hata: package.json'daki "private" bayragi olcut yapilinca
        # masal'in 1.0.0 surumu metadata'dan dustu ve butun kapilardan gecti.
        k = koruma.kayip_alanlar(self._meta(), self._meta(version=None))
        self.assertEqual(len(k), 1)
        self.assertIn("version", k[0])

    def test_ic_ice_alan_da_izlenir(self):
        k = koruma.kayip_alanlar(self._meta(), self._meta(media={"hero": None}))
        self.assertTrue(any("media.hero" in x for x in k))

    def test_bosalan_liste_yakalanir(self):
        k = koruma.kayip_alanlar(self._meta(), self._meta(key_features=[]))
        self.assertTrue(any("key_features" in x for x in k))

    def test_bostan_doluya_gecis_serbest(self):
        # Tek yonlu kural: bos bir alanin dolmasi iyi haberdir.
        self.assertEqual(
            koruma.kayip_alanlar(self._meta(version=None), self._meta()), [])

    def test_deger_degismesi_kayip_degildir(self):
        self.assertEqual(
            koruma.kayip_alanlar(self._meta(), self._meta(version="2.0.0")), [])


class OlcumTesti(unittest.TestCase):
    """Yayimlanan test sayisi, kosunun yazdigi satira geri goturulebiliyor mu."""

    def test_tek_kalip_okunur(self):
        self.assertEqual(denetim.kalip("CI log: `=== 115/115 gecti ===`"),
                         "=== 115/115 gecti ===")

    def test_birlesik_kaynak_dogrulanmaz(self):
        # derin-kazi'nin sayisi iki ayri kosu satirinin toplami; buradane'inki
        # backend + frontend. Tek bir satira karsilik gelmeyen bir sayiyi
        # tek bir satira karsi olcmeye calismak gurultuden baska bir sey
        # uretmez -- bunlar "dogrulanamaz" sayilir, "yanlis" degil.
        self.assertIsNone(denetim.kalip(
            "CI log: 304 unit (`== 304 sinama, 0 hata ==`) + 156 gameplay "
            "(`== 156 sinama, 0 hata ==`)"))
        self.assertIsNone(denetim.kalip("96 backend (CI log) + 228 frontend (vitest)"))

    def test_kalipsiz_kaynak(self):
        self.assertIsNone(denetim.kalip("27 validator + 32 export + 33 format checks"))
        self.assertIsNone(denetim.kalip(""))

    def test_sayi_logdan_okunur(self):
        log = "bir sey\n==== 289 passed in 1.2s ====\nbaska sey"
        self.assertEqual(denetim.sayiyi_bul(log, "289 passed"), 289)

    def test_degismis_sayi_yakalanir(self):
        log = "======== 327 passed in 61.62s ========"
        self.assertEqual(denetim.sayiyi_bul(log, "326 passed"), 327)

    def test_turkce_harfler_eslesmeyi_bozmaz(self):
        # Kosu "SONU\u00c7: 853 ge\u00e7ti" yaziyor, metadata ASCII tutuldugu icin
        # "SONUC: 853 gecti" diyor. Ayni satir, farkli yazim.
        log = "2026-09-22T06:25Z === SONU\u00c7: 853 ge\u00e7ti, 0 hata ==="
        self.assertEqual(
            denetim.sayiyi_bul(log, "=== SONUC: 853 gecti, 0 hata ==="), 853)

    def test_bulunamayan_kalip_none_doner(self):
        self.assertIsNone(denetim.sayiyi_bul("hicbir sey", "42 passed"))

    def test_ilk_sayi_alinir(self):
        self.assertEqual(denetim.sayiyi_bul("=== 115/115 gecti ===",
                                            "=== 115/115 gecti ==="), 115)

    def test_iki_isli_log_belirsizdir(self):
        # mini-creative-toolkit'in logunda hem 135 hem 327 var (iki is).
        # `sayiyi_bul` ilkini alip "yayimlanan 327 yanlis, kosu 135 yazdi"
        # diyordu -- bilinmeyeni bilinen gibi sunmak. Denetim artik ayrimi
        # yapiyor, ve mantik tek yerde: testler.py buraya delege ediyor.
        log = "=== 135 passed in 2s ===\nsonra\n=== 327 passed in 61s ==="
        self.assertEqual(denetim.sayilari_bul(log, "327 passed"), [135, 327])
        # Rakamlar genellestiriliyor (sayi degisince yakalanabilsin diye),
        # ama rakam disi metin aynen aranir.
        self.assertEqual(denetim.sayilari_bul(log, "999 passed"), [135, 327])
        self.assertEqual(denetim.sayilari_bul(log, "999 sinama"), [])

    def test_belirsiz_log_bulgu_degil_bakilamadi(self):
        denetim.SAYI_OKUNAN.clear()
        denetim.SAYI_BAKILAMADI.clear()
        onceki_genis, onceki_log = denetim.GENIS, denetim._log_metni
        denetim.GENIS = "x"
        denetim._log_metni = lambda *a, **k: "=== 135 passed ===\n=== 327 passed ==="
        try:
            sonuc = denetim._test_sayisi(
                "mct", "main", {"tests": {"count": 327, "source": "`327 passed`"}}, {})
        finally:
            denetim.GENIS, denetim._log_metni = onceki_genis, onceki_log
        self.assertIsNone(sonuc, "belirsizlik bir BULGU degil")
        self.assertIn("belirsiz", denetim.SAYI_BAKILAMADI["mct"])
        self.assertEqual(denetim.SAYI_OKUNAN, [], "belirsiz log dogrulanmis sayilmaz")
        denetim.SAYI_BAKILAMADI.clear()


class KapsamTesti(unittest.TestCase):
    """"Bakilamadi" ile "temiz" ayni cumleye giremez.

    _test_sayisi, DEPO_JETONU yokken sessizce None donuyordu ve gunluk
    denetim raporu bunu hic yazmiyordu. Yani "Denetim temiz" cumlesi,
    sistemin kendi hakkinda soyledigi en yuklu sayiya hic bakilmamis
    oldugu gunlerde de ayni sekilde yaziliyordu.
    """

    def setUp(self):
        denetim.SAYI_OKUNAN.clear()
        denetim.SAYI_BAKILAMADI.clear()

    def tearDown(self):
        denetim.SAYI_OKUNAN.clear()
        denetim.SAYI_BAKILAMADI.clear()

    def test_hicbir_sey_olculmediyse_satir_yok(self):
        self.assertEqual(denetim._kapsam_satiri(), "")

    def test_hepsi_okunduysa_sade_cumle(self):
        denetim.SAYI_OKUNAN.extend(["a", "b"])
        self.assertEqual(denetim._kapsam_satiri(),
                         "Yayimlanan test sayisi 2 depoda kosuya karsi dogrulandi.")

    def test_bakilamayan_varsa_sayisi_ve_nedeni_yazilir(self):
        denetim.SAYI_OKUNAN.append("a")
        denetim.SAYI_BAKILAMADI["b"] = "DEPO_JETONU yok: kosu logu okunamaz"
        denetim.SAYI_BAKILAMADI["c"] = "DEPO_JETONU yok: kosu logu okunamaz"
        denetim.SAYI_BAKILAMADI["d"] = "birlesik kaynak: tek bir kalibi yok"
        satir = denetim._kapsam_satiri()
        self.assertIn("1 depoda kosuya karsi dogrulandi", satir)
        self.assertIn("3 depoda **bakilamadi**", satir)
        self.assertIn("2: DEPO_JETONU yok", satir)
        self.assertIn("1: birlesik kaynak", satir)
        self.assertIn("Bakilamayan bir sayi temiz degildir", satir)

    def test_temiz_rapor_da_kapsami_soyler(self):
        denetim.SAYI_BAKILAMADI["b"] = "DEPO_JETONU yok: kosu logu okunamaz"
        metin = denetim._rapor([], {}, 28)
        self.assertIn("Denetim temiz", metin)
        self.assertIn("bakilamadi", metin)

    def test_bulgulu_rapor_da_kapsami_soyler(self):
        denetim.SAYI_OKUNAN.append("a")
        metin = denetim._rapor([("x", "olcum", "bir sey")], {}, 28)
        self.assertIn("kosuya karsi dogrulandi", metin)

    def test_yayimlanan_sayisi_olmayan_depo_bakilamadi_sayilmaz(self):
        # Test sayisi yayimlamayan bir depo icin karsilastiracak bir sey yok;
        # onu "bakilamadi" diye saymak gercek boslugu gurultuye gomerdi.
        self.assertIsNone(denetim._test_sayisi("x", "main", {"tests": {}}, {}))
        self.assertIsNone(denetim._test_sayisi("x", "main", None, {}))
        self.assertEqual(denetim.SAYI_BAKILAMADI, {})

    def test_jeton_yokken_sebep_kaydedilir(self):
        onceki = denetim.GENIS
        denetim.GENIS = ""
        try:
            self.assertIsNone(denetim._test_sayisi(
                "x", "main", {"tests": {"count": 12, "source": "`12 passed`"}}, {}))
        finally:
            denetim.GENIS = onceki
        self.assertIn("DEPO_JETONU", denetim.SAYI_BAKILAMADI["x"])


class IkiKaynakTesti(unittest.TestCase):
    """Iki yayimlanan sayi birbirine bakmiyorsa ikisi de dogru sanilir.

    Hub sayfasi depolarin kendi project-meta.json'larindan toplaniyor,
    profil sayfasi meta-source.json'dan. Her iki tarafin tutarlilik
    kontrolu de yalniz kendi tarafina bakiyordu, ve ikisi sessizce
    ayristi.
    """

    KAYNAK = {"x": {"tests": {"count": 347}}, "y": {"tests": {"count": 5}}}

    def test_ayrisma_bildirilir(self):
        (m,) = denetim._sayi_ayni_mi("x", {"tests": {"count": 334}}, self.KAYNAK)
        self.assertIn("334", m)
        self.assertIn("347", m)
        self.assertIn("hub", m)

    def test_ayni_sayi_sessiz(self):
        self.assertEqual(denetim._sayi_ayni_mi("y", {"tests": {"count": 5}}, self.KAYNAK), [])

    def test_kaydi_olmayan_depo_sessiz(self):
        self.assertEqual(denetim._sayi_ayni_mi("z", {"tests": {"count": 5}}, self.KAYNAK), [])

    def test_sayi_olmayan_taraf_sessiz(self):
        # Sayi yayimlamayan bir depo "ayrismis" degildir.
        self.assertEqual(denetim._sayi_ayni_mi("x", {}, self.KAYNAK), [])
        self.assertEqual(denetim._sayi_ayni_mi("x", {"tests": {"count": None}}, self.KAYNAK), [])


class HizSiniriTesti(unittest.TestCase):
    """Hiz siniri "bakilamadi" demek; ne "temiz" ne de "denetimi dusur"."""

    def setUp(self):
        denetim.OKUNAMADI.clear()
        denetim.SAYI_OKUNAN.clear()
        denetim.SAYI_BAKILAMADI.clear()

    tearDown = setUp

    def _hata(self, kod, basliklar=None, govde=b""):
        import urllib.error, io, email.message
        m = email.message.Message()
        for k, v in (basliklar or {}).items():
            m[k] = v
        return urllib.error.HTTPError("http://x", kod, "n", m, io.BytesIO(govde))

    def test_403_kota_bitmisse_hiz_siniri(self):
        e = self._hata(403, {"x-ratelimit-remaining": "0"})
        self.assertTrue(self._siniflandir(e))

    def test_429_her_zaman_hiz_siniri(self):
        self.assertTrue(self._siniflandir(self._hata(429)))

    def test_govdedeki_metin_de_sayilir(self):
        self.assertTrue(self._siniflandir(self._hata(403, {}, b'{"message":"API rate limit exceeded"}')))

    def test_yetkisiz_403_hiz_siniri_degildir(self):
        # Her 403 kota degil: yetkisiz bir uc de 403 doner ve onu "sonra
        # bakariz" diye gecistirmek gercek bir yetki sorununu gizlerdi.
        e = self._hata(403, {"x-ratelimit-remaining": "4999"}, b'{"message":"Resource not accessible"}')
        self.assertFalse(self._siniflandir(e))

    def _siniflandir(self, e):
        """derle._get'in HTTPError'u nasil siniflandirdigini tek yerden sinar."""
        import urllib.request
        sonuc = {}

        def sahte(req, timeout=None):
            raise e

        gercek = urllib.request.urlopen
        urllib.request.urlopen = sahte
        try:
            denetim.D._get("http://x")
        except denetim.D.HizSiniri:
            sonuc["hiz"] = True
        except urllib.error.HTTPError:
            sonuc["hiz"] = False
        finally:
            urllib.request.urlopen = gercek
        return sonuc.get("hiz", False)

    def test_okunamayan_depo_raporda_yaziyor(self):
        denetim.OKUNAMADI.extend(["a", "b"])
        metin = denetim._rapor([], {}, 28)
        self.assertIn("hiz siniri", metin.lower())
        self.assertIn("2 depo hic olculemedi", metin)
        # "28 depo, bulgu yok" demiyor: bakilan 26.
        self.assertIn("26 depo", metin)

    def test_okunamayan_yoksa_satir_da_yok(self):
        self.assertEqual(denetim._okunamayan_satiri(), "")
        self.assertIn("28 depo", denetim._rapor([], {}, 28))

    def test_depo_listesi_alinamazsa_yigin_izi_degil_cumle(self):
        # Olumcul, ama yigin izi basarak degil. Ve nedenini soylemeli:
        # _get GITHUB_TOKEN/GH_TOKEN okuyor, kosu loglarini okuyan taraf
        # DEPO_JETONU; yalniz ikincisi tanimliyken istekler kimliksiz gider.
        import io, os, contextlib
        gercek = denetim.D._repos
        denetim.D._repos = lambda: (_ for _ in ()).throw(denetim.D.HizSiniri("x"))
        eski = {k: os.environ.pop(k, None) for k in ("GITHUB_TOKEN", "GH_TOKEN")}
        tampon = io.StringIO()
        try:
            with contextlib.redirect_stdout(tampon):
                kod = denetim.main()
        finally:
            denetim.D._repos = gercek
            for k, v in eski.items():
                if v is not None:
                    os.environ[k] = v
        metin = tampon.getvalue()
        self.assertEqual(kod, 2)
        self.assertIn("hiz siniri", metin.lower())
        self.assertIn("KIMLIKSIZ", metin)
        self.assertIn("GITHUB_TOKEN", metin)


class BayatlikTesti(unittest.TestCase):
    """'active' diyen ama aylardir sessiz depo."""

    def _repo(self, gun):
        from datetime import datetime, timedelta, timezone
        an = datetime.now(timezone.utc) - timedelta(days=gun)
        return {"archived": False, "pushed_at": an.strftime("%Y-%m-%dT%H:%M:%SZ")}

    def test_taze_depo_sessiz(self):
        self.assertIsNone(denetim._bayat_mi(self._repo(3), {"status": "active"}))

    def test_aylardir_sessiz_depo_bildirilir(self):
        self.assertIsNotNone(denetim._bayat_mi(self._repo(400), {"status": "active"}))

    def test_prototype_ve_arsiv_bildirilmez(self):
        self.assertIsNone(denetim._bayat_mi(self._repo(400), {"status": "prototype"}))
        r = self._repo(400)
        r["archived"] = True
        self.assertIsNone(denetim._bayat_mi(r, {"status": "active"}))


class KurulumTesti(unittest.TestCase):
    """README'nin kurmayi soyledigi dagitim adlari."""

    def _blok(self, *satirlar):
        return "```bash\n" + "\n".join(satirlar) + "\n```"

    def test_pypi_adi_bulunur(self):
        self.assertEqual(denetim.kurulum_adlari(self._blok("uv tool install ptm-cli")),
                         {"ptm-cli"})
        self.assertEqual(denetim.kurulum_adlari(self._blok("pip install mcp-vet")),
                         {"mcp-vet"})
        self.assertEqual(denetim.kurulum_adlari(self._blok("pipx install ptm-cli")),
                         {"ptm-cli"})

    def test_git_url_paket_adi_degildir(self):
        # Duzeltmeden sonra README'de duran komut tam olarak bu; PyPI'da
        # aranacak bir ad yok, yani bulgu da yok.
        self.assertEqual(denetim.kurulum_adlari(self._blok(
            "uv tool install git+https://github.com/Furkiozknn/prompt-template-manager")),
            set())
        self.assertEqual(denetim.kurulum_adlari(self._blok(
            "uvx --from git+https://github.com/x/y ptm --help")), set())

    def test_yerel_kurulum_sayilmaz(self):
        self.assertEqual(denetim.kurulum_adlari(self._blok("pip install -e .")), set())
        self.assertEqual(
            denetim.kurulum_adlari(self._blok("pip install -r requirements.txt")), set())

    def test_bayraklar_paket_sanilmaz(self):
        self.assertEqual(
            denetim.kurulum_adlari(self._blok("uv pip install --system pyyaml")),
            {"pyyaml"})

    def test_cumle_icindeki_komut_calistirilacak_komut_degildir(self):
        # Yasanan yanlis bulgu: README "yayimlandiginda `uv tool install
        # ptm-cli` kisa yol olacak" diyordu ve kontrol bunu ziyaretcinin
        # calistiracagi komut sandi. Kopyalanan sey kod blogudur.
        prose = ("Once `ptm-cli` is published, `uv tool install ptm-cli` will be "
                 "the shorter route.")
        self.assertEqual(denetim.kurulum_adlari(prose), set())
        self.assertEqual(
            denetim.kurulum_adlari(prose + "\n" + self._blok("pip install mcp-vet")),
            {"mcp-vet"})

    def test_bos_metin(self):
        self.assertEqual(denetim.kurulum_adlari(""), set())
        self.assertEqual(denetim.kurulum_adlari(None), set())


class TestlerAraciTesti(unittest.TestCase):
    """testler.py: bir sayi kac yerde goruluyorsa hepsi ayni seyi soylemeli."""

    def _kaynak(self, **fazla):
        temel = {
            "a-repo": {"status": "active",
                       "tests": {"count": 10, "source": "`10 passed`",
                                 "measured": "2026-09-22"}},
            "b-repo": {"status": "active",
                       "tests": {"count": 5, "source": "`5 passed`",
                                 "measured": "2026-09-01"}},
            "arsiv": {"status": "archived",
                      "tests": {"count": 99, "source": "`99 passed`",
                                "measured": "2026-01-01"}},
            "suitsiz": {"status": "active"},
        }
        temel.update(fazla)
        return temel

    def test_arsivli_depo_toplama_girmez(self):
        # TESTLER.md bunu acikca yaziyor; denetim.py API'deki `archived`
        # bayragina bakiyor, bu arac agsiz kipte `status` alanina bakmak
        # zorunda -- iki yerin ayni cevabi vermesi gerekiyor.
        self.assertEqual(sorted(testler.sayilar(self._kaynak())), ["a-repo", "b-repo"])

    def test_bicim_binlik_ayirici(self):
        self.assertEqual(testler.bicim(5037), "5,037")

    def test_duz_hucredeki_sayi_guncellenir(self):
        satir = "| [x](https://github.com/Furkiozknn/x) | 28 | `28 passed` | 1 Sep 2026 |"
        self.assertIn("| 38 |", testler._satiri_guncelle(satir, 38))

    def test_backtickli_hucre_guncellenir(self):
        satir = "| x | **[y](https://github.com/Furkiozknn/y)** | ne yapar | `28` |"
        self.assertIn("`38`", testler._satiri_guncelle(satir, 38))

    def test_kalin_toplam_hucresi_guncellenir(self):
        # Ilk surum yalnizca duz ve backtick'li bicimleri taniyordu ve
        # `| **Total** | **4,700** | | |` satirini atliyordu -- yani en cok
        # goze carpan sayiyi.
        satir = "| **Total** | **4,700** | | |"
        self.assertEqual(testler._satiri_guncelle(satir, 5037),
                         "| **Total** | **5,037** | | |")

    def test_satirdaki_SON_sayi_degisir(self):
        satir = "| 🔎 | **[y](https://github.com/Furkiozknn/y)** | 30 projede denendi | `97` |"
        yeni = testler._satiri_guncelle(satir, 103)
        self.assertIn("30 projede", yeni)      # aciklamadaki sayi korunur
        self.assertIn("`103`", yeni)

    def test_tablo_sayiya_gore_siralanir(self):
        satirlar = testler.testler_tablosu(self._kaynak())
        self.assertIn("a-repo", satirlar[0])
        self.assertIn("b-repo", satirlar[1])
        self.assertTrue(satirlar[-1].startswith("| **Total** | **15**"))

    def test_tarih_okunur_bicime_donusur(self):
        self.assertEqual(testler._olculdu("2026-09-22"), "22 Sep 2026")
        self.assertEqual(testler._olculdu("bilinmiyor"), "bilinmiyor")

    def test_ayni_kalip_iki_farkli_sayi_eslerse_belirsiz(self):
        # ai-workflow-engine'e ikinci bir is eklendiginde ayni log hem
        # `72 passed` hem `8 passed` tasiyor. Ilkini secmek yanlis sayiyi
        # yayimlamak demekti.
        log = "job A\n8 passed in 0.2s\njob B\n72 passed in 1.1s"
        self.assertEqual(sorted(set(testler.tum_sayilar(log, "72 passed", denetim))),
                         [8, 72])

    def test_tek_is_tek_sayi(self):
        log = "=== 319 passed in 2s ==="
        self.assertEqual(testler.tum_sayilar(log, "319 passed", denetim), [319])

    def test_iki_tema_ayni_sayiyi_tasir(self):
        # README hero'yu <picture> ile iki temada gosteriyor. Biri
        # guncellenip digeri unutulursa acik temadaki okur eski sayiyi gorur.
        def sayilar(yol):
            return re.findall(r'id="(sayi-[a-z]+)"[^>]*>([\d,]+)',
                              yol.read_text(encoding="utf-8"))
        koyu, acik = testler.HEROLAR
        self.assertTrue(koyu.is_file() and acik.is_file())
        # Iki sayi: repolar ve testler. Commit sayisi 25 Eylul'de kalkti --
        # guclu profillerin hicbiri gostermiyor ve bir seyi kanitlamiyor.
        self.assertEqual([k for k, _ in sayilar(koyu)], ["sayi-repos", "sayi-tests"])
        self.assertEqual(sayilar(koyu), sayilar(acik))


class VitrinTesti(unittest.TestCase):
    """vitrin.py: profilin "Recently" bolumu yazilar/ ve surumlerden."""

    def _yazi(self, d, ad, **alan):
        govde = "".join("%s: %s\n" % kv for kv in alan.items())
        d.yaz("yazilar/" + ad, "---\n" + govde + "---\n\n# baslik\n")

    def test_yazilar_yeniden_eskiye_taslak_disarida(self):
        from pathlib import Path
        with GeciciDepo() as d:
            self._yazi(d, "eski.md", title="Eski", date="2026-09-01", summary="a")
            self._yazi(d, "yeni.md", title="Yeni", date="2026-09-20", summary="b")
            self._yazi(d, "taslak.md", title="T", date="2026-09-30", summary="c",
                       draft="true")
            d.yaz("yazilar/README.md", "dizin")
            liste = vitrin.yazilar(Path(d.yol) / "yazilar")
        self.assertEqual([y["title"] for y in liste], ["Yeni", "Eski"])

    def test_eksik_alanli_yazi_sessizce_girmez(self):
        # Tarihsiz bir satir, tarihe gore siralanan listede yanlis yere oturur.
        from pathlib import Path
        with GeciciDepo() as d:
            self._yazi(d, "x.md", title="X", summary="s")
            with self.assertRaises(ValueError):
                vitrin.yazilar(Path(d.yol) / "yazilar")

    def test_ayni_gunun_yazilari_hep_ayni_sirada(self):
        from pathlib import Path
        with GeciciDepo() as d:
            self._yazi(d, "b.md", title="B", date="2026-09-25", summary="s")
            self._yazi(d, "a.md", title="A", date="2026-09-25", summary="s")
            liste = vitrin.yazilar(Path(d.yol) / "yazilar")
        self.assertEqual([y["title"] for y in liste], ["A", "B"])

    def test_blok_isaretler_arasinda_ve_sinirli(self):
        from datetime import date
        yazi = [{"title": "T%d" % i, "date": date(2026, 9, i + 1), "summary": "s",
                 "path": "yazilar/%d.md" % i} for i in range(5)]
        surum = ["- [r v%d](u) <sub>x</sub>" % i for i in range(2)]
        b = vitrin.blok(yazi, surum)
        self.assertTrue(b.startswith(vitrin.BAS) and b.endswith(vitrin.SON))
        self.assertEqual(b.count("](yazilar/"), vitrin.YAZI_SAYISI)
        self.assertIn("**Releases**", b)
        self.assertIn("<sub>1 Sep 2026</sub>", b)

    def test_surum_satirlari_korunur(self):
        # Agsiz kip, API'nin yazdigi surum satirlarini silmemeli.
        metin = ("x\n" + vitrin.BAS + "\n\n**Releases**\n\n- [a v1](u) <sub>d</sub>\n\n"
                 + vitrin.SON + "\ny")
        self.assertEqual(vitrin.mevcut_surum_satirlari(metin), ["- [a v1](u) <sub>d</sub>"])

    def test_bos_depo_listesi_surumleri_silmez(self):
        # API bos liste dondururse vitrin durmali; "surum yok" diye
        # Releases satirlarini sessizce silmemeli.
        import types
        sahte = types.ModuleType("derle")
        sahte._repos = lambda: []
        sahte._release = lambda ad: None
        gercek = vitrin._derle
        vitrin._derle = lambda: sahte
        try:
            with self.assertRaises(SystemExit):
                vitrin.surumler()
        finally:
            vitrin._derle = gercek

    def test_readme_isaretleri_ve_yazilari_tutarli(self):
        # Gercek README ve gercek yazilar/: CI'daki --kontrol ile ayni soru.
        metin = vitrin.README.read_text(encoding="utf-8")
        i, j = vitrin.mevcut_blok(metin)
        self.assertEqual(metin[i:j], vitrin.blok(vitrin.yazilar(),
                                                  vitrin.mevcut_surum_satirlari(metin)))



class DerleTesti(unittest.TestCase):
    """derle.py: projects.json her depoyu API'den toplar."""

    def test_bos_depo_listesi_projeleri_silmez(self):
        # API bos liste dondururse derle durmali, projects.json'u sifir
        # projeyle yeniden yazmamali.
        yol = os.path.join(BURASI, "projects.json")
        def oku():
            if not os.path.exists(yol):
                return None
            with open(yol, encoding="utf-8") as f:
                return f.read()
        once = oku()
        gercek, derle._repos = derle._repos, lambda: []
        eski_argv = sys.argv
        sys.argv = ["derle.py"]
        try:
            self.assertEqual(derle.main(), 1)
        finally:
            derle._repos = gercek
            sys.argv = eski_argv
        sonra = oku()
        self.assertEqual(once, sonra)


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


class DenetimPolitikaTesti(unittest.TestCase):
    """denetim.py politikayi API'den okur; FAIL tek tek, WARN depo basina."""

    def setUp(self):
        if denetim.P.yaml_yok():
            self.skipTest("PyYAML yok")
        self.gercek = denetim._belki
        denetim.POLITIKA_BAKILAMADI.clear()

    def tearDown(self):
        denetim._belki = self.gercek
        denetim.POLITIKA_BAKILAMADI.clear()

    def _sahte(self, dosyalar, truncated=False):
        import base64 as b64
        def belki(url, varsayilan=None):
            if "/git/trees/" in url:
                return {"truncated": truncated,
                        "tree": [{"path": y, "type": "blob"} for y in dosyalar]
                        + [{"path": "src/app.py", "type": "blob"}]}
            yol = url.split("/contents/", 1)[1].split("?", 1)[0]
            self.okunan.append(yol)
            return {"content": b64.b64encode(dosyalar[yol].encode()).decode()}
        self.okunan = []
        denetim._belki = belki

    def test_warn_depo_basina_tek_satir_fail_ayri(self):
        wf = PolitikaTesti.TEMIZ.replace("    timeout-minutes: 15\n", "").replace(
            "0123456789abcdef0123456789abcdef01234567  # v7.1.0", "v7")
        kotu = wf.replace("          set -euo pipefail\n", "")
        self._sahte({".github/workflows/ci.yml": wf, ".github/workflows/b.yml": kotu,
                     "backend/uv.lock": "x"})
        cikti = denetim._politika("depo", "main")
        self.assertEqual(len([c for c in cikti if c.startswith("FAIL")]), 1)
        warn = [c for c in cikti if c.startswith("WARN")]
        self.assertEqual(len(warn), 1)
        self.assertIn("timeout-minutes yok x2", warn[0])
        self.assertIn("Dependabot eksik x1", warn[0])
        self.assertIn("kapsam disi kilit dosyasi x1", warn[0])
        # uv.lock icerigi hic indirilmez; varligi yeterli.
        self.assertNotIn("backend/uv.lock", self.okunan)

    def test_okunamayan_agac_temiz_sayilmaz(self):
        self._sahte({".github/workflows/ci.yml": "x"}, truncated=True)
        self.assertEqual(denetim._politika("depo", "main"), [])
        self.assertEqual(denetim.POLITIKA_BAKILAMADI, {"depo": "dosyalar okunamadi"})
        self.assertIn("1 depoda **bakilamadi**", denetim._politika_satiri())


class KapanmisAkisTesti(unittest.TestCase):
    """60 gun hareketsizlikle kapanan zamanlanmis akis sessiz kalmamali."""

    def test_yalnizca_hareketsizlikten_kapananlar(self):
        gercek = denetim._belki
        denetim._belki = lambda url, v=None: {"workflows": [
            {"path": ".github/workflows/denetim.yml", "state": "disabled_inactivity"},
            {"path": ".github/workflows/eski.yml", "state": "disabled_manually"},
            {"path": ".github/workflows/ci.yml", "state": "active"}]}
        try:
            self.assertEqual(denetim._kapanmis_akislar("depo"), ["denetim.yml"])
        finally:
            denetim._belki = gercek

    def test_okunamazsa_bulgu_uydurmaz(self):
        gercek = denetim._belki
        denetim._belki = lambda url, v=None: v
        try:
            self.assertEqual(denetim._kapanmis_akislar("depo"), [])
        finally:
            denetim._belki = gercek


if __name__ == "__main__":
    unittest.main(verbosity=2)

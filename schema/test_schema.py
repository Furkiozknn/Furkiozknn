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
koruma = _yukle("koruma")
dogrula = _yukle("dogrula")
haftalik = _yukle("haftalik")
denetim = _yukle("denetim")


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


if __name__ == "__main__":
    unittest.main(verbosity=2)

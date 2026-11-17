#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""python3 yonetim/test_pano.py -- merkezi panonun kurallari (bagimliliksiz)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pano  # noqa: E402


def g(i, durum="Bekliyor", oncelik="P1", **k):
    d = {"id": i, "baslik": k.pop("baslik", "is " + i), "durum": durum, "oncelik": oncelik}
    d.update(k)
    return d


class Kurallar(unittest.TestCase):
    def test_gecerli(self):
        v = {"gorevler": [g("G-001", "Tamamlandı", kanit=["PR #1"], kapandi="2026-11-17"), g("G-002", bagimli=["G-001"])]}
        self.assertEqual(pano.dogrula(v), [])

    def test_durum_ve_oncelik(self):
        h = pano.dogrula({"gorevler": [g("G-001", "Bitti"), g("G-002", oncelik="P9")]})
        self.assertTrue(any("gecersiz durum" in x for x in h))
        self.assertTrue(any("gecersiz oncelik" in x for x in h))

    def test_id(self):
        h = pano.dogrula({"gorevler": [g("G-001"), g("G-001", baslik="baska"), g("X-1")]})
        self.assertTrue(any("tekrar ediyor" in x for x in h))
        self.assertTrue(any("G-NNN" in x for x in h))

    def test_tamamlandi_kanit_ister(self):
        h = pano.dogrula({"gorevler": [g("G-001", "Tamamlandı")]})
        self.assertTrue(any("kanit yok" in x for x in h))
        self.assertTrue(any("kapandi" in x for x in h))

    def test_engellendi_neden_ister(self):
        h = pano.dogrula({"gorevler": [g("G-001", "Engellendi", engel={"neden": "hesap yok"})]})
        self.assertTrue(any("engel.gereken" in x for x in h))

    def test_bagimlilik(self):
        h = pano.dogrula({"gorevler": [g("G-001", bagimli=["G-009"])]})
        self.assertTrue(any("bilinmeyen" in x for x in h))
        h = pano.dogrula({"gorevler": [g("G-001", bagimli=["G-002"]), g("G-002", bagimli=["G-001"])]})
        self.assertTrue(any("dongu" in x for x in h))

    def test_tekrar_onleme_aktifte(self):
        h = pano.dogrula({"gorevler": [g("G-001", baslik="Dolmuş reels'i zamanla"), g("G-002", baslik="dolmus reels i zamanla")]})
        self.assertTrue(any("ayni baslik" in x for x in h))
        # tamamlanmis bir isin basligi yeniden acilabilir (gecmis korunur)
        h = pano.dogrula({"gorevler": [g("G-001", "Tamamlandı", baslik="X", kanit=["k"], kapandi="d"), g("G-002", baslik="X")]})
        self.assertEqual(h, [])

    def test_siradaki_is_bagimliliga_uyar(self):
        v = [g("G-001", oncelik="P0", bagimli=["G-002"]), g("G-002", "Devam Ediyor", oncelik="P2"), g("G-003", oncelik="P1")]
        aktif, hazir = pano.sira(v)
        self.assertEqual([x["id"] for x in hazir], ["G-003"])  # G-001 P0 ama bagimliligi bitmedi
        self.assertEqual(aktif[0]["id"], "G-002")  # devam eden is ustte

    def test_pano_tamamlananlari_gecmise_alir(self):
        v = {"guncellendi": "t", "gorevler": [g("G-001", "Tamamlandı", kanit=["PR #1"], kapandi="2026-11-17"), g("G-002")]}
        metin = pano.yaz(v, {"kolonlar": [], "oyunlar": []})
        aktif, gecmis = metin.split("## Geçmiş")
        self.assertNotIn("G-001", aktif.split("## Engellenen")[0])
        self.assertIn("G-001", gecmis)
        self.assertIn("PR #1", gecmis)

    def test_portfoy_21_oyun(self):
        p = {"oyunlar": [{"oyun": o} for o in pano.OYUNLAR[:-1]]}
        h = pano.dogrula({"gorevler": []}, p)
        self.assertTrue(any(pano.OYUNLAR[-1] in x for x in h))

    def test_gercek_dosyalar(self):
        import json
        kok = os.path.dirname(os.path.abspath(__file__))
        v = json.load(open(os.path.join(kok, "gorevler.json"), encoding="utf-8"))
        p = json.load(open(os.path.join(kok, "portfoy.json"), encoding="utf-8"))
        self.assertEqual(pano.dogrula(v, p), [])


if __name__ == "__main__":
    unittest.main(verbosity=1)

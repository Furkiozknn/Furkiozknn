#!/usr/bin/env python3
"""Tests for arena-kit/inject.py (stdlib unittest).   python3 arena-kit/test_inject.py"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("inject", HERE / "inject.py")
inject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inject)

GAME = """<!doctype html>
<html><head>
<meta charset="utf-8">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js"}}</script>
</head><body><script type="module">import * as THREE from 'three';</script></body></html>
"""


class InjectTest(unittest.TestCase):
    def setUp(self):
        self.block, self.ver, self.digest = inject.kit_block()

    def test_insert_before_importmap_and_nothing_else_changes(self):
        new, action = inject.apply(GAME, self.block)
        self.assertEqual(action, "inserted")
        self.assertLess(new.index("ARENA-KIT:BEGIN"), new.index('<script type="importmap">'))
        self.assertEqual(new.replace(self.block, ""), GAME)  # pure addition

    def test_second_run_is_a_no_op(self):
        once, _ = inject.apply(GAME, self.block)
        twice, action = inject.apply(once, self.block)
        self.assertEqual(action, "current")
        self.assertEqual(once, twice)

    def test_refresh_replaces_only_the_block(self):
        old = self.block.replace(self.digest, "000000000000").replace("var VERSION = '", "var VERSION = 'old-")
        stale, _ = inject.apply(GAME, old)
        fresh, action = inject.apply(stale, self.block)
        self.assertEqual(action, "updated")
        self.assertEqual(fresh.count("ARENA-KIT:BEGIN"), 1)
        self.assertEqual(fresh.replace(self.block, ""), GAME)

    def test_anchor_on_a_shared_line(self):
        html = GAME.replace('<meta charset="utf-8">\n<script type="importmap">', '<meta charset="utf-8"><script type="importmap">')
        new, action = inject.apply(html, self.block)
        self.assertEqual(action, "inserted")
        self.assertIn(self.block + '<script type="importmap">', new)

    def test_no_importmap_falls_back_to_head_end(self):
        html = '<!doctype html>\n<html><head>\n<meta charset="utf-8">\n</head><body><script>var x=1;</script></body></html>\n'
        new, action = inject.apply(html, self.block)
        self.assertEqual(action, "inserted")
        self.assertLess(new.index("ARENA-KIT:BEGIN"), new.index("</head>"))
        self.assertEqual(new.replace(self.block, ""), html)  # pure addition
        self.assertEqual(inject.apply(new, self.block)[1], "current")

    def test_missing_anchor_and_duplicate_blocks_are_errors(self):
        with self.assertRaises(ValueError):
            inject.apply("<html></html>", self.block)
        doubled = inject.apply(GAME, self.block)[0].replace('<script type="importmap">', self.block + '<script type="importmap">')
        with self.assertRaises(ValueError):
            inject.apply(doubled, self.block)

    def test_cli_kontrol_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            g = pathlib.Path(d) / "oyun"
            g.mkdir()
            (g / "index.html").write_text(GAME, encoding="utf-8")
            run = lambda *a: subprocess.run([sys.executable, str(HERE / "inject.py"), *a, str(g)], capture_output=True, text=True)
            self.assertEqual(run("--kontrol").returncode, 1)  # missing
            self.assertEqual(run().returncode, 0)            # inject
            self.assertEqual(run("--kontrol").returncode, 0)  # current


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Put arena-kit/kit.js inline into a game's index.html, or check that it is there and current.

    python3 arena-kit/inject.py ../hamsi ../dolmus           # insert or refresh the block
    python3 arena-kit/inject.py --kontrol ../hamsi ../dolmus  # exit 1 if a block is missing or stale

The block sits right before <script type="importmap"> (a classic script, so window.Arena exists
before the game's module runs); a game without an import map (e.g. fay-hatti, no CDN modules) gets it
right before </head>. It is delimited so a later run replaces it in place:

    <script>/*ARENA-KIT:BEGIN v1.0.0 sha256:<12 hex>*/
    ...kit.js...
    /*ARENA-KIT:END*/</script>

Nothing else in index.html is touched, so schema/degisim.py can judge the change as additions only
(first run) or as a replacement of the block lines (refresh). Standard library only.
"""
import argparse
import hashlib
import pathlib
import re
import sys

KIT = pathlib.Path(__file__).with_name("kit.js")
BLOCK = re.compile(r"<script>/\*ARENA-KIT:BEGIN [^*]*\*/\n.*?\n/\*ARENA-KIT:END\*/</script>\n", re.S)
ANCHOR = '<script type="importmap">'
FALLBACK = "</head>"  # games with no import map


def kit_block():
    src = KIT.read_text(encoding="utf-8")
    if "</script" in src.lower():
        raise SystemExit("kit.js must not contain '</script' (it is inlined into HTML)")
    if "ARENA-KIT:" in src:
        raise SystemExit("kit.js must not contain the marker text 'ARENA-KIT:' (it would confuse the block search)")
    ver = re.search(r"var VERSION = '([^']+)'", src).group(1)
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()[:12]
    return f"<script>/*ARENA-KIT:BEGIN v{ver} sha256:{digest}*/\n{src.rstrip()}\n/*ARENA-KIT:END*/</script>\n", ver, digest


def apply(html, block):
    """Return (new_html, action) where action is inserted / updated / current."""
    found = BLOCK.findall(html)
    if len(found) > 1:
        raise ValueError("more than one ARENA-KIT block")
    if found:
        if found[0] == block:
            return html, "current"
        return BLOCK.sub(lambda _m: block, html, count=1), "updated"
    i = html.find(ANCHOR)
    if i < 0:
        i = html.find(FALLBACK)
    if i < 0:
        raise ValueError("no <script type=\"importmap\"> or </head> anchor")
    line_start = html.rfind("\n", 0, i) + 1
    if html[line_start:i].strip():  # anchor shares a line with other markup -> insert right before it
        return html[:i] + block + html[i:], "inserted"
    return html[:line_start] + block + html[line_start:], "inserted"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("games", nargs="+", help="game repository directories")
    ap.add_argument("--kontrol", action="store_true", help="only check; exit 1 if missing or stale")
    a = ap.parse_args(argv)
    block, ver, digest = kit_block()
    bad = 0
    for g in a.games:
        p = pathlib.Path(g) / "index.html"
        try:
            html = p.read_text(encoding="utf-8")
            new, action = apply(html, block)
        except (OSError, ValueError) as e:
            print(f"HATA   {g}: {e}")
            bad += 1
            continue
        if a.kontrol:
            ok = action == "current"
            bad += not ok
            print(f"{'TAMAM ' if ok else 'ESKI  ' if action == 'updated' else 'YOK   '} {g}")
        else:
            if action != "current":
                p.write_text(new, encoding="utf-8")
            print(f"{action:9} {g}  (kit v{ver} {digest})")
    print(f"{len(a.games)} oyun, {bad} sorun")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

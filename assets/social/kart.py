#!/usr/bin/env python3
"""assets/social/*.png kartlarini kartlar.json'dan uretir (1280x640).

Kartlar GitHub'in "Social preview" alanina elle yuklenir; API yok. Bu
betik onlari yeniden uretilebilir kiliyor: bir aciklama degisince kart
da yeniden cizilir, tasarim bir sablondan, metin tek bir dosyadan gelir.

    python3 assets/social/kart.py              # hepsini yeniden ciz
    python3 assets/social/kart.py mcp-vet      # yalnizca biri

Gerekenler: Playwright (Python) ve bir Chromium. Kart metninde test
sayisi yok: sayilar degisir, yuklenmis bir gorsel degismez.
"""

import html
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
RENK = {  # alan -> vurgu rengi; profildeki "What I build" alanlariyla ayni
    "denetim": "#58a6ff",
    "altyapi": "#e3b341",
    "mcp": "#3fb950",
    "uygulama": "#39c5cf",
    "oyun": "#db61a2",
}

SABLON = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1280px;height:640px;background:#0f1117}
.k{position:relative;width:1280px;height:640px;box-sizing:border-box;padding:0 88px;
background:radial-gradient(900px 480px at 100% 0%,#161b26 0%,#0f1117 60%)}
.bar{position:absolute;top:0;left:88px;width:180px;height:6px;background:VURGU}
.ust{position:absolute;top:78px;font:700 22px/1 "DejaVu Sans",sans-serif;letter-spacing:.24em;color:#d4a95c}
h1{position:absolute;top:128px;margin:0;font:700 88px/1.05 "DejaVu Sans Mono",monospace;color:#f2efe6;
max-width:1104px;overflow-wrap:anywhere}
.b{position:absolute;top:BTOP;margin:0;max-width:1060px;font:400 38px/1.3 "DejaVu Serif",serif;color:#ece8de}
.alt{position:absolute;bottom:76px;left:88px;max-width:900px;font:400 25px/1.35 "DejaVu Sans",sans-serif;color:#9ba3ae}
.dil{position:absolute;bottom:78px;right:88px;padding:9px 22px;border:2px solid #2f4661;border-radius:28px;
font:700 22px/1 "DejaVu Sans Mono",monospace;color:VURGU}
</style></head><body><div class="k"><div class="bar"></div>
<div class="ust">GITHUB.COM/FURKIOZKNN</div><h1>AD</h1><p class="b">BASLIK</p>
<div class="alt">ALT</div>DIL</div></body></html>"""


def sayfa(ad, k):
    buyuk = len(ad) > 20  # uzun adlar iki satira sarilir; baslik asagi iner
    return (SABLON.replace("VURGU", RENK[k["alan"]])
            .replace("BTOP", "330px" if buyuk else "240px")
            .replace("AD", html.escape(ad))
            .replace("BASLIK", html.escape(k["baslik"]))
            .replace("ALT", html.escape(k["alt"]))
            .replace("DIL", '<div class="dil">%s</div>' % html.escape(k["dil"]) if k.get("dil") else ""))


def main(adlar):
    from playwright.sync_api import sync_playwright
    kartlar = json.loads((KOK / "kartlar.json").read_text(encoding="utf-8"))
    secili = adlar or sorted(kartlar)
    with sync_playwright() as p:
        yol = Path("/opt/pw-browsers/chromium")
        tarayici = p.chromium.launch(executable_path=str(yol) if yol.exists() else None)
        s = tarayici.new_page(viewport={"width": 1280, "height": 640})
        for ad in secili:
            s.set_content(sayfa(ad, kartlar[ad]))
            s.screenshot(path=str(KOK / ("%s.png" % ad)))
            print("ciz  %s.png" % ad)
        tarayici.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

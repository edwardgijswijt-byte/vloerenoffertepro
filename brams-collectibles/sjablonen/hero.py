#!/usr/bin/env python3
"""Kopbeeld voor de homepage, 2400x1000.

Geen tekst in het beeld: de kop en de knop komen uit Shopify's image-banner
en staan daar overheen. Het beeld levert alleen de opstelling — vier dozen op
een lijn, navy grond, een gouden gloed erachter — en onderin een donkere
verloop zodat de witte tekst leesbaar blijft.

De onderste 44 procent blijft leeg. Zet het beeld in de banner op "aanpassen
aan afbeelding": bij een vaste bandhoogte snijdt Dawn boven en onder weg, en
dan valt de kop over de dozen heen.
"""
import base64, pathlib, subprocess, shutil, tempfile
from PIL import Image

from huisstijl import NAVY, GOLD, FONTS, BASE

BREED, HOOG = 2400, 1000
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'

# opname, hoogte in pixels, naar voren of naar achteren
BASIS = 555               # de lijn waar alle dozen op staan
RIJ = [('IMG_3700', 350, 2), ('IMG_3754', 415, 3), ('IMG_3709', 300, 1),
       ('IMG_3758', 335, 2)]
MAX_VERGROTING = 1.15


def datauri(pad):
    return 'data:image/png;base64,' + base64.b64encode(pathlib.Path(pad).read_bytes()).decode()


def doos(naam, hoog, laag):
    pad = BRON / f'{naam}.png'
    im = Image.open(pad)
    schaal = min(hoog / im.height, MAX_VERGROTING)
    b, h = round(im.width * schaal), round(im.height * schaal)
    dof = 0 if laag == 3 else (0.14 if laag == 2 else 0.3)   # achterste dozen iets doffer
    return (f'<img src="{datauri(pad)}" alt="" style="width:{b}px;height:{h}px;z-index:{laag};'
            f'margin:0 26px;filter:drop-shadow(0 18px 26px rgba(0,0,0,.55)) brightness({1 - dof});'
            f'position:relative">')


def blad():
    dozen = '\n      '.join(doos(*d) for d in RIJ)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
{FONTS}
{BASE}
</style></head>
<body style="margin:0">
  <div style="position:relative;width:{BREED}px;height:{HOOG}px;background:{NAVY};overflow:hidden">

    <div style="position:absolute;inset:0;background:
      radial-gradient(64% 46% at 50% {BASIS / HOOG:.0%}, rgba(201,162,75,.34) 0%, rgba(201,162,75,.13) 44%, rgba(13,27,42,0) 72%)"></div>

    <div style="position:absolute;left:0;right:0;top:{BASIS}px;height:2px;background:
      linear-gradient(90deg,rgba(201,162,75,0) 4%,rgba(201,162,75,.8) 30%,rgba(201,162,75,.8) 70%,rgba(201,162,75,0) 96%)"></div>
    <div style="position:absolute;left:50%;top:{BASIS - 26}px;width:1500px;height:52px;transform:translateX(-50%);
      background:radial-gradient(50% 50% at 50% 50%, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 70%)"></div>

    <div style="position:absolute;left:0;right:0;top:0;height:{BASIS}px;
      display:flex;align-items:flex-end;justify-content:center">
      {dozen}
    </div>

    <div style="position:absolute;left:0;right:0;bottom:0;height:44%;background:
      linear-gradient(180deg,rgba(13,27,42,0) 0%,rgba(13,27,42,.55) 40%,{NAVY} 88%)"></div>
  </div>
</body></html>
"""


def main():
    uit = HIER / 'export' / 'webshop' / '_hero.png'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(blad(), encoding='utf-8')
        subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        f'--window-size={BREED},{HOOG}', f'--screenshot={tmp / "s.png"}',
                        '--virtual-time-budget=4000', str(tmp / 'p.html')],
                       check=True, capture_output=True)
        uit.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp / 's.png', uit)
    print(f'{uit}  {BREED}x{HOOG}  {uit.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

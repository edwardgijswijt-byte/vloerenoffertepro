#!/usr/bin/env python3
"""Productfoto's voor de webshop, in het sjabloon.

    python3 productbeeld.py BC-PE-PCETB IMG_3754 IMG_3753 IMG_3752 IMG_3755 IMG_3756

Elke foto krijgt hetzelfde kader als de advertenties: navy grond, gouden
rand, logo bovenaan, het product op het plateau, de merknaam eronder. Zo
oogt de hele winkel als één geheel, en — belangrijker — verdwijnt de
rafelrand van de uitsnede in de navy achtergrond in plaats van als vuil
op te vallen tegen wit.

Formaat: 1600x1600. Het product wordt hooguit 1,15x vergroot; verder
opblazen maakt bij Shopify's zoom de zachte randen zichtbaar. Bij foto's
van 2048x1536 komt het product daarmee op ongeveer twee derde van de
breedte, en dat is precies de verhouding van het eigen sjabloon.

Bron: fotos/uitgesneden/strak/recht/ — dus rechtgezet en met een
schoongemaakte rand. Draai eerst rechtzetten.py.
"""
import base64, pathlib, subprocess, sys, tempfile, shutil
from PIL import Image

from huisstijl import NAVY, GOLD, CREAM, FONTS, BASE, logo, frame, plateau, footer_mark

ZIJ = 1600
MAX_VERGROTING = 1.15
DEEL = 0.72              # deel van de breedte dat het product mag innemen
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'


def datauri(pad):
    return 'data:image/png;base64,' + base64.b64encode(pathlib.Path(pad).read_bytes()).decode()


def maat(pad):
    """Hoe groot het product mag worden zonder het op te blazen."""
    im = Image.open(pad)
    wens = ZIJ * DEEL
    schaal = min(wens / im.width, MAX_VERGROTING)
    hoogte_ruimte = ZIJ * 0.50                      # tussen logo en plateau
    schaal = min(schaal, hoogte_ruimte / im.height)
    return round(im.width * schaal)


def blad(fotopad):
    """Het logo staat in huisstijl.py als <img src="logo.png">. Dat pad werkt
    in de canvasbestanden, maar niet vanuit de tijdelijke map waarin chromium
    rendert — daar bakken we het bestand zelf in."""
    breed = maat(fotopad)
    inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:56px 0 0">{logo(212)}</div>
    <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 70px 10px">
      <img src="{datauri(fotopad)}" alt="" style="width:{breed}px;height:auto;max-height:100%;
        object-fit:contain;filter:drop-shadow(0 22px 34px rgba(0,0,0,.55))">
    </div>
{plateau(int(ZIJ * 0.50), bar=16, body=48)}
    <div style="flex:none;padding:46px 0 60px">{footer_mark(size=20, gap=26, rule=150)}</div>"""
    inner = inner.replace('src="logo.png"', f'src="{datauri(HIER / "logo.png")}"')
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
{FONTS}
{BASE}
</style></head><body style="margin:0;background:{NAVY}">
{frame(ZIJ, ZIJ, inner, border=8, inset=4)}
</body></html>
"""


def schiet(html, doel):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(html, encoding='utf-8')
        subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        f'--window-size={ZIJ},{ZIJ}', f'--screenshot={tmp / "s.png"}',
                        '--virtual-time-budget=3000', str(tmp / 'p.html')],
                       check=True, capture_output=True)
        doel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp / 's.png', doel)


def main():
    if len(sys.argv) < 3:
        sys.exit('gebruik: productbeeld.py <sku> <opname> [<opname> ...]')
    sku, opnames = sys.argv[1], sys.argv[2:]
    uit = HIER / 'export' / 'webshop'
    for n, naam in enumerate(opnames, start=1):
        bron = BRON / f'{naam}.png'
        if not bron.exists():
            sys.exit(f'{bron} bestaat niet — draai eerst rechtzetten.py')
        doel = uit / f'{sku}-{n}.png'
        schiet(blad(bron), doel)
        print(f'{doel.name:<22} {ZIJ}x{ZIJ}  {naam}, product {maat(bron)}px breed  '
              f'{doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

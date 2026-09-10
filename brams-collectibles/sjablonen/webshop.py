#!/usr/bin/env python3
"""Productfoto's klaarmaken voor de webshop.

    python3 webshop.py BC-PE-PCETB IMG_3754 IMG_3753 IMG_3752 IMG_3755 IMG_3756

De eerste opname wordt het gemerkte beeld op navy — dat is wat in de
collectieoverzichten staat. De rest komt op transparant in de galerij.

Het eerste beeld is het gemerkte vierkant uit export/ (product op navy, op
het gouden plateau). Dat is wat in de collectieoverzichten staat, dus daar
wil je je huisstijl zien. Daarna komen de losse opnames op transparant,
allemaal op hetzelfde vierkante formaat zodat ze in de galerij niet
verspringen.

Uitvoer: export/webshop/<sku>-1.png tot -N.png
"""
import pathlib, sys
from PIL import Image

ZIJ = 1600          # vierkant, ruim genoeg voor Shopify's zoomweergave
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden'


NAVY, GOUD = (13, 27, 42, 255), (201, 162, 75, 255)


def vierkant(pad, zij=ZIJ, vulling=0.88, navy=False):
    """Op een vierkant doek zetten, product op vaste schaal gecentreerd.

    Dezelfde schaal voor elk beeld, ook voor het gemerkte eerste beeld —
    anders springt het product in de galerij van groot naar klein.
    """
    im = Image.open(pad).convert('RGBA')
    doel = int(zij * vulling)
    schaal = min(doel / im.width, doel / im.height)
    im = im.resize((round(im.width * schaal), round(im.height * schaal)), Image.LANCZOS)

    doek = Image.new('RGBA', (zij, zij), NAVY if navy else (0, 0, 0, 0))
    x = (zij - im.width) // 2
    y = (zij - im.height) // 2
    if navy:
        y = int(zij * 0.44) - im.height // 2      # iets hoger, plateau eronder
    doek.paste(im, (x, y), im)

    if navy:
        # het gouden plateau, zoals op de advertentiesjablonen
        breed, hoog = int(zij * 0.52), max(int(zij * 0.010), 3)
        bx, by = (zij - breed) // 2, y + im.height + int(zij * 0.035)
        Image.Image.paste(doek, Image.new('RGBA', (breed, hoog), GOUD), (bx, by))
    return doek


def main():
    if len(sys.argv) < 3:
        sys.exit('gebruik: webshop.py <sku> <opname> [<opname> ...]')
    sku, opnames = sys.argv[1], sys.argv[2:]
    uit = HIER / 'export' / 'webshop'
    uit.mkdir(parents=True, exist_ok=True)

    # Eerste beeld: dezelfde opname als het tweede, maar op navy met het
    # plateau. Dat is wat in de collectieoverzichten staat.
    n = 1
    doel = uit / f'{sku}-{n}.png'
    vierkant(BRON / f'{opnames[0]}.png', navy=True).save(doel)
    print(f'{doel.name:<22} {ZIJ}x{ZIJ}  {opnames[0]}, op navy met plateau')

    # De hoofdopname staat al op navy; die niet nog eens plat herhalen.
    for naam in opnames[1:]:
        n += 1
        doel = uit / f'{sku}-{n}.png'
        vierkant(BRON / f'{naam}.png').save(doel)
        print(f'{doel.name:<22} {ZIJ}x{ZIJ}  {naam}, transparant')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Een pdf-pagina op een Instagram-doek van 4:5 zetten.

    python3 socialbeeld.py bron.pdf export/instagram/flyer

Maakt <naam>-1.png, <naam>-2.png enzovoort, 1080x1350.

Waarom dit nodig is: A5 heeft de verhouding 1:1,419 en Instagram toont hooguit
1:1,25. Laat je Instagram het zelf doen, dan snijdt hij de boven- en onderkant
eraf — bij deze flyer precies het logo en de voetregel. Daarom schalen we op de
hoogte en vullen we links en rechts aan met de navy uit de huisstijl. Er gaat
niets af en er wordt niets uitgerekt; het blad staat op een passe-partout.
"""
import pathlib
import sys

import pymupdf
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from huisstijl import NAVY  # noqa: E402

BREED, HOOG = 1080, 1350


def op_doek(blad, dpi=300):
    px = blad.get_pixmap(dpi=dpi)
    im = Image.frombytes('RGB', (px.width, px.height), px.samples)
    breed = round(im.width * HOOG / im.height)
    if breed > BREED:                       # breder dan 4:5: dan op breedte
        im = im.resize((BREED, round(im.height * BREED / im.width)), Image.LANCZOS)
    else:
        im = im.resize((breed, HOOG), Image.LANCZOS)
    doek = Image.new('RGB', (BREED, HOOG), NAVY)
    doek.paste(im, ((BREED - im.width) // 2, (HOOG - im.height) // 2))
    return doek


def main():
    if len(sys.argv) != 3:
        sys.exit('gebruik: socialbeeld.py <bron.pdf> <doelpad-zonder-extensie>')
    bron, stam = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    stam.parent.mkdir(parents=True, exist_ok=True)
    pdf = pymupdf.open(bron)
    for nr, blad in enumerate(pdf, 1):
        doel = stam.with_name(f'{stam.name}-{nr}.png')
        op_doek(blad).save(doel)
        print(f'{doel.name:<24} {BREED}x{HOOG}  {doel.stat().st_size // 1024} KB')
    pdf.close()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Uitgesneden productfoto's rechtzetten en de rand opschonen.

    python3 rechtzetten.py fotos/uitgesneden/strak/IMG_*.png

Twee dingen die je bij inzoomen ziet en die er niet horen:

  scheef      De doos ligt op stof en staat nooit precies waterpas. Een
              graad of twee valt niet op tot je hem naast een recht kader
              zet — en dan valt het meteen op.

  rafelrand   rembg laat een zoom van half-doorzichtige pixels staan. Op
              navy zie je die niet, op wit leest hij als vuil. We snijden
              die zoom eraf en maken de rand hard.

Uitvoer overschrijft het bronbestand niet: die gaat naar .../recht/.
"""
import pathlib, sys
from PIL import Image, ImageFilter
import numpy as np

MAX_GRADEN = 4.0        # meer dan dit is geen scheefstand maar een hoekopname


def hoek(alpha):
    """Scheefstand in graden, gemeten aan de bovenrand van het product.

    Per kolom de bovenste zichtbare pixel, daar een rechte lijn doorheen.
    Alleen het middendeel telt: bij de hoeken loopt de doos weg en die
    trekken de lijn scheef.
    """
    h, w = alpha.shape
    van, tot = int(w * 0.25), int(w * 0.75)
    xs, ys = [], []
    for x in range(van, tot):
        kolom = np.nonzero(alpha[:, x] > 140)[0]
        if len(kolom):
            xs.append(x)
            ys.append(kolom[0])
    if len(xs) < 40:
        return 0.0
    xs, ys = np.array(xs, float), np.array(ys, float)
    # uitschieters weg: de kartonranden en de reflectie op het acryl
    a, b = np.polyfit(xs, ys, 1)
    rest = ys - (a * xs + b)
    houd = np.abs(rest) < 2.5 * rest.std()
    if houd.sum() > 30:
        a, _ = np.polyfit(xs[houd], ys[houd], 1)
    return float(np.degrees(np.arctan(a)))


def rand_aantrekken(im, ondergrens=64):
    """De half-doorzichtige zoom eraf snijden en de rand hard maken.

    Eerder stond hier een drempel op 150: alles daaronder werd doorzichtig.
    Dat werkt zolang rembg de doos vol ondoorzichtig maakt, maar dat doet hij
    niet altijd. Bij de Ascended Heroes-bundel lag de alpha van de doos zelf
    voor een kwart onder de 150, en die stukken verdwenen dus — het masker
    ging van 72 naar 47 procent dekking en de navy achtergrond scheen dwars
    door het product heen. Vijf van de 47 uitsnedes hadden dat.

    Nu eerst de vorm bepalen op een ruime drempel, daar de gaten in vullen en
    alleen de grootste vlek houden, en die vorm helemaal ondoorzichtig maken.
    De zoom verdwijnt doordat de vorm binair is, niet doordat we hem
    wegdrempelen. MinFilter krimpt hem daarna een pixel, zodat er geen
    achtergrond op de rand blijft plakken."""
    from scipy.ndimage import binary_fill_holes, label
    a = np.asarray(im.getchannel('A'))
    m = a > ondergrens
    if not m.any():
        return im
    m = binary_fill_holes(m)
    lab, n = label(m)
    if n > 1:
        tel = np.bincount(lab.ravel())
        tel[0] = 0
        m = lab == tel.argmax()
    hard = Image.fromarray(np.where(m, 255, 0).astype(np.uint8))
    im.putalpha(hard.filter(ImageFilter.MinFilter(3)))
    return im


def bijsnijden(im):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 12)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def verwerk(pad):
    pad = pathlib.Path(pad)
    im = Image.open(pad).convert('RGBA')
    g = hoek(np.asarray(im)[:, :, 3])

    gedraaid = ''
    if 0.15 < abs(g) <= MAX_GRADEN:
        im = im.rotate(g, resample=Image.BICUBIC, expand=True,
                       fillcolor=(0, 0, 0, 0))
        gedraaid = f'{-g:+.2f}°'
    elif abs(g) > MAX_GRADEN:
        gedraaid = f'({g:+.1f}° — te veel, niet gedraaid)'

    im = rand_aantrekken(im)
    im = bijsnijden(im)

    uit = pad.parent / 'recht'
    uit.mkdir(exist_ok=True)
    im.save(uit / pad.name)
    print(f'{pad.name:<16} {im.width}x{im.height:<9} {gedraaid}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('geef één of meer uitgesneden PNG-bestanden mee')
    for p in sys.argv[1:]:
        verwerk(p)

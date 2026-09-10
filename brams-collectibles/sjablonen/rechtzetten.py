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


def rand_aantrekken(im, krimp=1.5, hardheid=150):
    """De half-doorzichtige zoom eraf snijden en de rand hard maken."""
    a = im.getchannel('A')
    a = a.filter(ImageFilter.MinFilter(3)) if krimp >= 1 else a
    n = np.asarray(a, dtype=np.float32)
    n = np.clip((n - hardheid) * (255.0 / (255 - hardheid)), 0, 255)
    im.putalpha(Image.fromarray(n.astype(np.uint8)))
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

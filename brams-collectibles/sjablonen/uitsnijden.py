#!/usr/bin/env python3
"""Achtergrond verwijderen van productfoto's.

Gebruik:  python3 uitsnijden.py fotos/*.jpg
Uitvoer:  fotos/uitgesneden/<naam>.png  — transparante achtergrond,
          strak bijgesneden en op een vierkant canvas met wat lucht eromheen.

Werkt met rembg (isnet-general-use) als die beschikbaar is. Zo niet, dan valt
het script terug op een eigen masker dat de donkere stoffen achtergrond
wegsnijdt. Een acrylcase is doorzichtig en spiegelt, dus de terugval maakt
het masker bewust ruim en trekt hem daarna weer aan.
"""
import sys, pathlib
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

UIT = pathlib.Path('fotos/uitgesneden')
STRAK = UIT / 'strak'
MAXZIJ = 2000          # langste zijde van de uitvoer
LUCHT  = 0.06          # marge rondom het product, als deel van de langste zijde


def masker_rembg(im, matting=True):
    """Met alpha matting voor een zachte rand; zonder voor alleen de vorm.

    Op een opgehelderde kopie is matting niet alleen overbodig maar ook
    onbetrouwbaar: de oplosser loopt op een bijna wit beeld minutenlang te
    ploeteren op een matrix die niet positief-definiet wil worden. De rand van
    dat masker doet er niet toe, want rechtzetten.py trekt hem daarna toch aan."""
    from rembg import remove, new_session
    sess = new_session('isnet-general-use')
    if matting:
        uit = remove(im, session=sess, alpha_matting=True,
                     alpha_matting_foreground_threshold=250,
                     alpha_matting_background_threshold=15,
                     alpha_matting_erode_size=8)
    else:
        uit = remove(im, session=sess, alpha_matting=False)
    return np.array(uit.convert('RGBA'))[:, :, 3]


def vulling(a):
    """Hoe vol het masker zijn eigen omhullende rechthoek maakt.

    Alles wat we fotograferen is een doos, en een doos vult zijn rechthoek voor
    ongeveer negentig procent. Blijft er de helft over, dan heeft rembg er een
    hap uit genomen. Gaten tellen werkt hier niet: bij een zwarte doos op zwarte
    stof loopt het weggevallen deel tot aan de rand door, en dan is het geen gat
    meer maar een inham."""
    m = a > 128
    if not m.any():
        return 0.0
    ys, xs = np.nonzero(m)
    vlak = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
    return float(m.sum()) / float(vlak)


def masker_dubbelslag(im):
    """Eerst gewoon. Zit het masker vol gaten, dan nog eens op een opgehelderde
    kopie — het masker komt dan wel goed, en leggen we op het origineel.

    Reden: matzwart karton op zwart satijn geeft rembg te weinig verschil. Op
    driemaal helderder met wat extra contrast vindt hij de doos in zijn geheel.
    De kleuren van de uitvoer blijven die van de originele opname."""
    a = masker_rembg(im)
    vol = vulling(a)
    if vol >= 0.70:
        return a, 'rembg'
    op = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(3.0)).enhance(1.4)
    b = masker_rembg(op, matting=False)
    if vulling(b) > vol:
        return b, f'rembg opgehelderd ({vol:.0%} -> {vulling(b):.0%} gevuld)'
    return a, f'rembg ({vol:.0%} gevuld, ophelderen hielp niet)'


def masker_terugval(im):
    """Zonder rembg: de achtergrond is donkere stof, het product is licht en
    scherp. We combineren helderheid met lokaal contrast (stof is egaal,
    karton en acryl niet) en houden daarna de grootste samenhangende vorm."""
    g = np.asarray(im.convert('L'), dtype=np.float32) / 255.0
    # lokaal contrast: verschil met een sterk vervaagde versie
    vaag = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(9)),
                      dtype=np.float32) / 255.0
    detail = np.asarray(im.convert('L').filter(ImageFilter.FIND_EDGES)
                          .filter(ImageFilter.GaussianBlur(6)),
                        dtype=np.float32) / 255.0

    drempel = np.percentile(g, 35)                 # stof zit in de donkere helft
    score = (g - drempel) * 2.2 + detail * 3.0 + (g - vaag) * 1.5
    m = np.clip(score, 0, 1)
    m = (m > 0.35).astype(np.uint8)

    m = grootste_vlek(m)
    m = gaten_vullen(m)
    mi = Image.fromarray(m * 255).filter(ImageFilter.GaussianBlur(2.0))
    a = np.asarray(mi, dtype=np.float32)
    a = np.clip((a - 90) * (255.0 / 90.0), 0, 255)  # rand weer aantrekken
    return a.astype(np.uint8)


def grootste_vlek(m):
    """Grootste 4-verbonden component, zonder scipy."""
    h, w = m.shape
    label = np.zeros((h, w), dtype=np.int32)
    huidig, groottes = 0, {}
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if label[y0, x0]:
            continue
        huidig += 1
        stapel, n = [(y0, x0)], 0
        label[y0, x0] = huidig
        while stapel:
            y, x = stapel.pop()
            n += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not label[yy, xx]:
                    label[yy, xx] = huidig
                    stapel.append((yy, xx))
        groottes[huidig] = n
    if not groottes:
        return m
    beste = max(groottes, key=groottes.get)
    return (label == beste).astype(np.uint8)


def gaten_vullen(m):
    """Alles wat niet vanaf de rand bereikbaar is, hoort bij het product.
    Vangt de doorzichtige acrylcase en lichte plekken binnen de doos."""
    h, w = m.shape
    buiten = np.zeros((h, w), dtype=bool)
    stapel = []
    for x in range(w):
        for y in (0, h - 1):
            if not m[y, x] and not buiten[y, x]:
                buiten[y, x] = True
                stapel.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not m[y, x] and not buiten[y, x]:
                buiten[y, x] = True
                stapel.append((y, x))
    while stapel:
        y, x = stapel.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and not m[yy, xx] and not buiten[yy, xx]:
                buiten[yy, xx] = True
                stapel.append((yy, xx))
    return (~buiten).astype(np.uint8)


def bijsnijden(rgba):
    """Twee uitvoeren van dezelfde uitsnede.

    strak    — precies om het product heen. Voor de sjablonen: de doos is
               liggend, en op een vierkant doek zou hij klein ogen.
    vierkant — op een vierkant doek met lucht eromheen. Voor de webshop,
               waar alle productfoto's dezelfde verhouding moeten hebben.
    """
    a = rgba[:, :, 3]
    ys, xs = np.nonzero(a > 12)
    if len(ys) == 0:
        im = Image.fromarray(rgba)
        return im, im
    strak = Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    lang = max(strak.size)
    marge = int(lang * LUCHT)
    zij = lang + marge * 2
    doek = Image.new('RGBA', (zij, zij), (0, 0, 0, 0))
    doek.paste(strak, ((zij - strak.width) // 2, (zij - strak.height) // 2), strak)
    if zij > MAXZIJ:
        doek = doek.resize((MAXZIJ, MAXZIJ), Image.LANCZOS)
    return strak, doek


def verwerk(pad):
    im = Image.open(pad)
    im = ImageOps.exif_transpose(im).convert('RGB')
    if max(im.size) > 2600:                       # sneller, en scherp genoeg
        im.thumbnail((2600, 2600), Image.LANCZOS)

    try:
        a, hoe = masker_dubbelslag(im)
    except Exception as e:
        print(f'   rembg niet gebruikt ({e.__class__.__name__}), terugval', file=sys.stderr)
        a = masker_terugval(im)
        hoe = 'terugval'

    rgba = np.dstack([np.asarray(im), a])
    strak, vierkant = bijsnijden(rgba)
    UIT.mkdir(parents=True, exist_ok=True)
    STRAK.mkdir(parents=True, exist_ok=True)
    naam = pathlib.Path(pad).stem + '.png'
    vierkant.save(UIT / naam)
    strak.save(STRAK / naam)
    print(f'{pathlib.Path(pad).name:<26} -> {naam:<18} '
          f'strak {strak.width}x{strak.height}  vierkant {vierkant.width}x{vierkant.height}  {hoe}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('geef één of meer fotobestanden mee')
    for p in sys.argv[1:]:
        verwerk(p)

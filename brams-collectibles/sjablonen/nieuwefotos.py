#!/usr/bin/env python3
"""Brams nieuwe opnames uit Drive omzetten naar Marktplaats-beelden.

    python3 nieuwefotos.py            alles wat in fotos/nieuw/ staat
    python3 nieuwefotos.py BC-CR-ETB  alleen dat artikel
    python3 nieuwefotos.py --opnieuw  ook wat al af is

Hervatbaar: wat al een rechtgezette uitsnede en een Marktplaats-beeld heeft
wordt overgeslagen. De reeks duurt drie kwartier en is een keer halverwege
afgebroken; opnieuw beginnen vanaf nul is dan zonde.

In september 2026 heeft Bram alles opnieuw gefotografeerd, op 5712x4284 tegen
2048x1536 eerder. Hij levert per artikel een map met 1.HEIC en 2.HEIC, genoemd
naar het product; MAPPEN hieronder koppelt die namen aan een sku.

Twee dingen over het voorwerk:

- **Eerst bijsnijden op het product, dan pas verkleinen.** De eerste versie
  verkleinde de hele foto naar 2600 pixels. Dat leek te kloppen, want bij het
  151-display kwam er precies dezelfde uitsnede uit als bij 5712. Maar dat
  display vult het beeld; een booster bundle is een klein doosje dat op
  dezelfde afstand is geschoten en daar bleef 531 pixels van over, waar 1170
  in de opname zat. In het kader van 1600 stond dat product dan op 31 procent,
  want opblazen mag niet.

  Nu zoekt `kader()` eerst in een grove uitsnede op 1100 pixels waar het
  product zit, snijdt de foto op volle resolutie bij tot dat vak plus een
  marge, en verkleint pas daarna. Zo houdt een klein product evenveel pixels
  over als een groot.
- **De opnames gaan onder hun sku de pijplijn in**, niet onder 1 en 2. Anders
  heet elke bron in elke map hetzelfde en kun je ze niet naast elkaar zetten.

**Alleen HEIC, en dat is met opzet.** Bij de vier cases staat er naast Brams
eigen opname ook een `1.webp` of `1.png` met varianten als "Alternatief op 1".
Dat zijn afbeeldingen van de distributeur: een montage van de blister voor een
bruine doos met "X6" erop. Die horen niet in een advertentie. Het is andermans
beeld, en de algemene voorwaarden beloven dat de foto van het daadwerkelijke
exemplaar is. Door alleen `*.HEIC` op te halen vallen ze er vanzelf buiten en
wordt Brams foto van de carton met het verzendetiket het hoofdbeeld — wat ook
eerlijker is, want dat is wat de koper krijgt.

Voeg hier dus geen webp of png aan toe zonder daar opnieuw over na te denken.
"""
import pathlib
import subprocess
import sys

import pillow_heif
from PIL import Image

pillow_heif.register_heif_opener()

HIER = pathlib.Path(__file__).parent
NIEUW = HIER / 'fotos' / 'nieuw'
BRON = HIER / 'fotos'
MAX = 3000        # na het bijsnijden; het eindkader is 1600
RUW = 1100        # waarop we zoeken waar het product staat
DEEL = 0.55       # hoeveel van het kader het product mag vullen na bijsnijden

MAPPEN = {
    '151 Booster Bundle Display (10)': 'BC-151-BNDD',
    'Ascended Heroes Booster Bundle Display (10)': 'BC-AH-BNDD',
    'Ascended Heroes Elite Trainer Box Pokemon Centre': 'BC-AH-PCETB',
    'Ascended heroes Booster Bundle (6)': 'BC-AH-BND',
    'Chaos Rising Booster Box (36)': 'BC-CR-BBX',
    'Chaos Rising Booster Bundle (6)': 'BC-CR-BND',
    'Chaos Rising Elite Train Box': 'BC-CR-ETB',
    'Chaos Rising Elite Trainer Box Pokemon Centre': 'BC-CR-PCETB',
    'Chaos Rising Premium Collection Meg Greninja': 'BC-MEV-GREN',
    'Destined Rivals Elite Trainer Box': 'BC-DR-ETB',
    'First Partner Illustration Collection Series 1 Case (6)': 'BC-FP-CASE1',
    'First Partner Illustration Collection Series 2 Case (6)': 'BC-FP-CASE2',
    'First Partner Illustration Collection Series 3 Case (6) - kopie': 'BC-FP-CASE3',
    'Paldean Fates Case Elite Trainer Box (10)': 'BC-PAF-CASE',
    'Pitch Black Elite Trainer Box': 'BC-PB-ETB',
    'Pitch Black Elite Trainer Box Pokemon Centre': 'BC-PB-PCETB',
    'Prismatic Evolutions Elite Trainer Box Pokemon Center': 'BC-PE-PCETB',
    'Prismatic Evolutions Super Premium Collection': 'BC-PE-SPC',
}


def kader(im):
    """Het vak waarin het product staat, gevonden op een verkleinde kopie.

    Een grove uitsnede op 1100 pixels kost een paar seconden en is ruim genoeg
    om te zien waar het product zit; de nauwkeurige uitsnede komt later toch
    nog een keer over de bijgesneden foto heen."""
    import numpy as np
    from uitsnijden import masker_rembg

    klein = im.copy()
    klein.thumbnail((RUW, RUW))
    m = masker_rembg(klein, matting=False) > 128
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    f = im.width / klein.width
    x0, x1 = xs.min() * f, xs.max() * f
    y0, y1 = ys.min() * f, ys.max() * f
    # Zoveel lucht eromheen dat het product DEEL van het kader vult. Te krap
    # bijsnijden werkt averechts: rembg heeft achtergrond nodig om het product
    # van te onderscheiden. Bij zes procent marge viel het masker van het
    # staande 151-display uit elkaar — 35 procent gevuld, en wat er overbleef
    # was een schuin afgesneden bovenstuk.
    marge = (max(x1 - x0, y1 - y0) / DEEL - max(x1 - x0, y1 - y0)) / 2
    return (max(0, int(x0 - marge)), max(0, int(y0 - marge)),
            min(im.width, int(x1 + marge)), min(im.height, int(y1 + marge)))


def draai(*args):
    subprocess.run([sys.executable, *args], cwd=HIER, check=True)


def omzetten(sku, map_):
    """HEIC naar JPG, verkleind, met de sku in de naam. Geeft de stamnamen
    terug in de volgorde 1, 2 — 1 wordt het hoofdbeeld."""
    namen = []
    for heic in sorted((NIEUW / map_).glob('*.HEIC')):
        stam = f'{sku}-N{heic.stem}'
        im = Image.open(heic).convert('RGB')
        vak = kader(im)
        if vak:
            im = im.crop(vak)
        im.thumbnail((MAX, MAX))
        im.save(BRON / f'{stam}.JPG', quality=95)
        namen.append(stam)
    return namen


def af(sku, namen):
    """Al gedaan? Dan moeten alle rechtgezette uitsnedes er zijn en het
    Marktplaats-beeld ook."""
    recht = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'
    return ((HIER / 'export' / 'marktplaats' / f'{sku}.png').exists()
            and all((recht / f'{n}.png').exists() for n in namen))


def main():
    keuze = set(sys.argv[1:])
    opnieuw = '--opnieuw' in keuze
    keuze.discard('--opnieuw')
    gedaan, over = [], []
    for map_, sku in sorted(MAPPEN.items(), key=lambda kv: kv[1]):
        if keuze and sku not in keuze:
            continue
        if not (NIEUW / map_).is_dir():
            over.append((sku, 'map ontbreekt'))
            continue
        namen = omzetten(sku, map_)
        if not namen:
            over.append((sku, 'geen HEIC in de map'))
            continue
        if af(sku, namen) and not opnieuw:
            over.append((sku, 'stond al klaar'))
            continue

        draai('uitsnijden.py', *[f'fotos/{n}.JPG' for n in namen])
        draai('rechtzetten.py', *[f'fotos/uitgesneden/strak/{n}.png' for n in namen])
        draai('marktplaatsbeeld.py', sku, *namen)
        gedaan.append((sku, len(namen)))
        print(f'== {sku} klaar, {len(namen)} opnames', flush=True)

    print()
    for sku, n in gedaan:
        print(f'  {sku:14} {n} opnames')
    for sku, reden in over:
        print(f'  {sku:14} overgeslagen — {reden}')


if __name__ == '__main__':
    main()

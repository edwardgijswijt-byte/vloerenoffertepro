#!/usr/bin/env python3
"""Brams nieuwe opnames uit Drive omzetten naar Marktplaats-beelden.

    python3 nieuwefotos.py            alles wat in fotos/nieuw/ staat
    python3 nieuwefotos.py BC-CR-ETB  alleen dat artikel

In september 2026 heeft Bram alles opnieuw gefotografeerd, op 5712x4284 tegen
2048x1536 eerder. Hij levert per artikel een map met 1.HEIC en 2.HEIC, genoemd
naar het product; MAPPEN hieronder koppelt die namen aan een sku.

Twee dingen die tijd schelen en niets kosten:

- **HEIC eerst verkleinen naar 2600 pixels.** uitsnijden.py levert bij 5712 en
  bij 2600 precies dezelfde uitsnede op — gemeten: 962x1642 tegen 960x1643, in
  beide gevallen 94 procent gevuld — maar doet er drie keer zo lang over. Het
  eindbeeld is 1600 breed, dus meer bron heeft geen zin.
- **De opnames gaan onder hun sku de pijplijn in**, niet onder 1 en 2. Anders
  heet elke bron in elke map hetzelfde en kun je ze niet naast elkaar zetten.
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
MAX = 2600

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


def draai(*args):
    subprocess.run([sys.executable, *args], cwd=HIER, check=True)


def omzetten(sku, map_):
    """HEIC naar JPG, verkleind, met de sku in de naam. Geeft de stamnamen
    terug in de volgorde 1, 2 — 1 wordt het hoofdbeeld."""
    namen = []
    for heic in sorted((NIEUW / map_).glob('*.HEIC')):
        stam = f'{sku}-N{heic.stem}'
        im = Image.open(heic).convert('RGB')
        im.thumbnail((MAX, MAX))
        im.save(BRON / f'{stam}.JPG', quality=95)
        namen.append(stam)
    return namen


def main():
    keuze = set(sys.argv[1:])
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

        draai('uitsnijden.py', *[f'fotos/{n}.JPG' for n in namen])
        draai('rechtzetten.py', *[f'fotos/uitgesneden/strak/{n}.png' for n in namen])
        draai('marktplaatsbeeld.py', sku, namen[0])
        gedaan.append((sku, len(namen)))
        print(f'== {sku} klaar, {len(namen)} opnames', flush=True)

    print()
    for sku, n in gedaan:
        print(f'  {sku:14} {n} opnames')
    for sku, reden in over:
        print(f'  {sku:14} overgeslagen — {reden}')


if __name__ == '__main__':
    main()

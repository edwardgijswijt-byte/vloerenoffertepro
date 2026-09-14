#!/usr/bin/env python3
"""Eén zip waar je per advertentie een map uit pakt.

    python3 advertentiepakket.py    -> export/marktplaats-advertenties.zip

Per artikel een map met de foto's in de volgorde waarin ze geplaatst moeten
worden, en de advertentietekst ernaast. De bestandsnamen beginnen met een
nummer, zodat de uploadvolgorde van Marktplaats vanzelf klopt: 1 is de
hoofdfoto.

De beelden gaan als JPEG de zip in en niet als PNG. Marktplaats hercodeert ze
toch, en zo is het pakket vijf megabyte in plaats van vijftig.
"""
import csv
import io
import pathlib
import re
import sys
import zipfile

from PIL import Image

HIER = pathlib.Path(__file__).parent
BASIS = HIER.parent
sys.path.insert(0, str(BASIS))

import teksten  # noqa: E402

ZIJ = 1600
KWALITEIT = 88


def jpeg(pad):
    im = Image.open(pad).convert('RGB')
    if max(im.size) > ZIJ:
        im.thumbnail((ZIJ, ZIJ))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=KWALITEIT, optimize=True)
    return buf.getvalue()


def mapnaam(r):
    """Op prijs aflopend genummerd, zodat de mappen in dezelfde volgorde staan
    als de plaatslijst. Dan kun je de twee naast elkaar afwerken."""
    naam = r['naam'].replace('&', 'en')
    schoon = ''.join(c if c.isalnum() or c in ' -' else '' for c in naam)
    return re.sub(r'-+', '-', schoon.strip().replace(' ', '-')).strip('-')


def main():
    alles = list(csv.DictReader(open(BASIS / 'register.csv', encoding='utf-8')))
    klaar = [r for r in alles
             if r['aantal'] and r['prijs']
             and (HIER / 'export' / 'marktplaats' / f"{r['sku']}.png").exists()]
    klaar.sort(key=lambda r: -float(r['prijs']))

    doel = HIER / 'export' / 'marktplaats-advertenties.zip'
    regels = ['Marktplaats — advertentiepakket', '',
              f'{len(klaar)} advertenties, hoogste vraagprijs eerst.', '',
              'Per artikel een map met drie soorten bestanden:', '',
              '  plakken.txt      de omschrijving, en verder niets. Alles',
              '                   selecteren en in het omschrijvingsveld',
              '                   plakken. De alinea\'s staan elk op een regel,',
              '                   zodat Marktplaats zelf mag afbreken.',
              '  advertentie.txt  de titel, de vraagprijs en de voorraad.',
              '  1.jpg, 2.jpg     de foto\'s in de volgorde waarin je ze',
              '                   uploadt. Foto 1 is de hoofdfoto.', '']

    with zipfile.ZipFile(doel, 'w', zipfile.ZIP_DEFLATED) as z:
        for nr, r in enumerate(klaar, 1):
            sku, map_ = r['sku'], f'{nr:02d} {mapnaam(r)}'
            # Alleen de Marktplaats-beelden, en dat is met opzet. Hier stonden
            # de webshopbeelden achter als extra hoeken, maar die komen uit de
            # oude opnames — 2048x1536, en Bram was er zelf niet tevreden over.
            # In september 2026 heeft hij alles opnieuw gefotografeerd op
            # 5712x4284. Twee reeksen door elkaar in een advertentie is
            # zichtbaar: andere scherpte, andere kleur.
            mp = HIER / 'export' / 'marktplaats'
            beelden = [mp / f'{sku}.png']
            beelden += sorted(mp.glob(f'{sku}-*.png'),
                              key=lambda p: int(p.stem.rsplit('-', 1)[1]))

            for i, b in enumerate(beelden, 1):
                z.writestr(f'{map_}/{i}.jpg', jpeg(b))

            # Twee bestanden en niet een. Eerst stond de titel, de prijs en
            # de tekst samen in advertentie.txt met een streep ertussen, maar
            # dan moet je bij het plakken de goede helft selecteren. Nu is
            # plakken.txt precies wat er in het omschrijvingsveld hoort:
            # openen, alles selecteren, plakken.
            z.writestr(f'{map_}/plakken.txt', teksten.marktplaats(r, alles) + '\n')
            z.writestr(f'{map_}/advertentie.txt', '\n'.join([
                'Titel:',
                f"{r['naam']} — sealed",
                '',
                f"Vraagprijs: {teksten.prijs(r)}",
                f"Voorraad: {r['aantal']} stuks" if int(r['aantal']) > 1 else 'Voorraad: 1 stuk',
                f"Foto's: {len(beelden)}",
                '',
                'De omschrijving staat in plakken.txt. Dat bestand bevat niets',
                'anders, dus alles selecteren en plakken kan zo.',
                '']))
            aantal = f'{len(beelden)} foto' + ('' if len(beelden) == 1 else "'s")
            regels.append(f'{nr:2d}. {r["naam"]} — {teksten.prijs(r)} — {aantal}')

        niet = [r for r in alles if r['aantal'] and r not in klaar]
        if niet:
            regels += ['', 'Nog niet plaatsbaar:']
            regels += [f'  - {r["naam"]} — geen foto' for r in niet]
        z.writestr('LEES-MIJ.txt', '\n'.join(regels) + '\n')

    print(f'{doel.relative_to(BASIS)}  {doel.stat().st_size // 1024 // 1024} MB  '
          f'{len(klaar)} advertenties')


if __name__ == '__main__':
    main()

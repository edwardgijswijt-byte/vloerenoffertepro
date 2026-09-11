#!/usr/bin/env python3
"""Alle plaatsbare Marktplaats-advertenties in één bestand.

    python3 plaatslijst.py

Uitvoer in teksten/uit/_marktplaats-plaatsen.md. Bedoeld om naast het scherm te
houden tijdens het plaatsen: per advertentie de titel, de vraagprijs, welk
bestand je als hoofdfoto uploadt, en daaronder de tekst om te plakken.

Alleen artikelen die compleet zijn: aantal, prijs, tekst en beeld. Wat ontbreekt
komt onderaan te staan met de reden erbij, zodat je niet halverwege ontdekt dat
er iets mist.
"""
import csv, pathlib, sys

HIER = pathlib.Path(__file__).parent
WORTEL = HIER.parent
sys.path.insert(0, str(WORTEL))
import teksten


def compleet(r):
    ontbreekt = []
    if not r['aantal']:
        ontbreekt.append('aantal')
    if not r['prijs']:
        ontbreekt.append('prijs')
    if not (WORTEL / 'teksten' / 'uit' / f"{r['sku']}.md").exists():
        ontbreekt.append('tekst')
    if not (HIER / 'export' / 'marktplaats' / f"{r['sku']}.png").exists():
        ontbreekt.append('foto')
    return ontbreekt


def main():
    alles = list(csv.DictReader(open(WORTEL / 'register.csv', encoding='utf-8')))
    klaar = [r for r in alles if not compleet(r)]
    klaar.sort(key=lambda r: -float(r['prijs']))

    d = ['# Marktplaats — plaatslijst', '',
         f'{len(klaar)} advertenties klaar om te plaatsen. Hoogste vraagprijs eerst.',
         '', 'Vink af terwijl je gaat. De foto staat in '
         '`sjablonen/export/marktplaats/`; de overige opnames voor de galerij '
         'in `sjablonen/export/webshop/`.', '']

    for i, r in enumerate(klaar, 1):
        d += [f'## {i}. {r["naam"]}', '',
              f'- Vraagprijs **{teksten.prijs(r)}**  ·  voorraad {r["aantal"]} '
              f'{"stuk" if r["aantal"] == "1" else "stuks"}',
              f'- Hoofdfoto `export/marktplaats/{r["sku"]}.png`',
              f'- Galerij `export/webshop/{r["sku"]}-*.png`',
              '', '```', teksten.marktplaats(r, alles), '```', '']

    rest = [(r, compleet(r)) for r in alles if compleet(r)]
    if rest:
        d += ['## Nog niet plaatsbaar', '']
        for r, wat in rest:
            d += [f'- **{r["naam"]}** — mist {", ".join(wat)}']
        d += ['']

    uit = WORTEL / 'teksten' / 'uit' / '_marktplaats-plaatsen.md'
    uit.write_text('\n'.join(d), encoding='utf-8')
    print(f'{uit.relative_to(WORTEL)}  —  {len(klaar)} klaar, {len(rest)} nog niet')


if __name__ == '__main__':
    main()

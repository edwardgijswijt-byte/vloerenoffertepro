#!/usr/bin/env python3
"""Advertentieteksten samenstellen uit register.csv en de tekstblokken.

    python3 teksten.py                 alles wat voorraad heeft
    python3 teksten.py BC-PE-PCETB     één artikel

Uitvoer in teksten/uit/<sku>.md — Marktplaats, socials en webshop onder elkaar,
klaar om te plakken.

De opbouw volgt de advertenties die Bram zelf schreef:
    merkverhaal (nooit anders)
    productnaam en hoogtepunten (per product)
    waarom deze set (per set, gedeeld door alle artikelen uit die set)
    bundelaanbod (alleen als er meer uit dezelfde set op voorraad ligt)
    verzenden of ophalen (nooit anders)

Die volgorde is de reden dat de tekst opgeknipt is. In de losse Word-bestanden
stond de settekst drie keer overgetypt, en in twee ervan eindigde hij op de
verkeerde productnaam. Zo kan dat niet meer.
"""
import csv, pathlib, re, sys

HIER = pathlib.Path(__file__).parent
UIT = HIER / 'teksten' / 'uit'


def blokken(pad):
    """Een .md met '## naam'-koppen inlezen als {naam: tekst}."""
    tekst = pathlib.Path(pad).read_text(encoding='utf-8')
    delen = re.split(r'^## +(.+)$', tekst, flags=re.M)[1:]
    return {k.strip(): v.strip() for k, v in zip(delen[::2], delen[1::2])}


MERK = blokken(HIER / 'teksten' / 'merk.md')


def settekst(slug):
    pad = HIER / 'teksten' / 'sets' / f'{slug}.md'
    if not pad.exists():
        return f'[NOG GEEN SETTEKST voor {slug} — teksten/sets/{slug}.md aanmaken]'
    return blokken(pad).get('tekst', '')


def prijs(r):
    return f"€ {r['prijs']}" if r['prijs'] else '€ [PRIJS]'


def hoogtepunten(r):
    return [h.strip() for h in r['hoogtepunten'].split('|') if h.strip()]


def bundel(r, alles):
    """Bram biedt een bundelprijs als er meer uit dezelfde set ligt."""
    anderen = [a['soort'] for a in alles
               if a['set'] == r['set'] and a['sku'] != r['sku'] and a['aantal']]
    if not anderen:
        return ''
    lijst = ' en '.join([', '.join(anderen[:-1]), anderen[-1]]) if len(anderen) > 1 else anderen[0]
    return (f'Koop je hem in combinatie met een {lijst}, dan maken wij een '
            f'mooie bundelprijs voor je!')


def marktplaats(r, alles):
    d = ['Brams Collectibles', '', MERK['verhaal-lang'], '', r['naam'], '']
    hp = hoogtepunten(r)
    if hp:
        d += ['De hoogtepunten:']
        d += [f'• In perfecte staat en sealed.'] if r['staat'] == 'sealed' else []
        d += [f'• {h}' for h in hp]
        d += ['En nog veel meer!', '']
    d += [settekst(r['set']), '']
    if r['hoes'] == 'ja':
        d += ['Zit in een acryl beschermhoes, die gaat mee bij verkoop.', '']
    b = bundel(r, alles)
    if b:
        d += [b, '']
    d += [MERK['verzenden'].replace('**', ''), '']
    d += [f'Prijs: {prijs(r)}']
    return '\n'.join(d)


def socials(r):
    hp = hoogtepunten(r)
    kern = hp[0] if hp else r['soort']
    tags = ('#pokemontcg #' + r['set'].replace('-', '') +
            ' #sealed #pokemonnederland #tcgnederland #bramscollectibles')
    return '\n'.join([
        f'{r["naam"]}. Sealed{", in acrylhoes" if r["hoes"] == "ja" else ""}.',
        '', kern + '.', '', settekst(r['set']), '',
        'Prijs en beschikbaarheid: link in bio.', '', tags,
    ])


def webshop(r):
    d = [settekst(r['set']), '']
    if r['hoes'] == 'ja':
        d += ['Geleverd in de acryl beschermhoes waarin hij op de foto staat.', '']
    hp = hoogtepunten(r)
    if hp:
        d += ['Inhoud:', '']
        d += [f'- {h}' for h in hp]
        d += ['']
    if r['notitie']:
        d += [r['notitie'], '']
    d += [f'Staat: {r["staat"]}. De foto\'s zijn van dit exemplaar.', '',
          MERK['verzenden']]
    return '\n'.join(d)


def schrijf(r, alles):
    UIT.mkdir(parents=True, exist_ok=True)
    doel = UIT / f'{r["sku"]}.md'
    doel.write_text('\n'.join([
        f'# {r["naam"]}', '',
        f'`{r["sku"]}` · set {r["set"]} · {r["aantal"] or 0} op voorraad · {prijs(r)}',
        '', '---', '', '## Marktplaats', '', '```', marktplaats(r, alles), '```',
        '', '## Instagram / TikTok', '', '```', socials(r), '```',
        '', '## Webshop', '', '```', webshop(r), '```', '',
    ]), encoding='utf-8')
    return doel


if __name__ == '__main__':
    alles = list(csv.DictReader(open(HIER / 'register.csv', encoding='utf-8')))
    keuze = sys.argv[1:] or [r['sku'] for r in alles if r['aantal']]
    for r in alles:
        if r['sku'] in keuze:
            p = schrijf(r, alles)
            print(f'{r["sku"]:<14} -> {p.relative_to(HIER)}')

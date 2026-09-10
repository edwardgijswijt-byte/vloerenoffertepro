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


def bedrag(waarde):
    """Nederlands: komma als decimaalteken, en hele bedragen als 599,-"""
    n = float(waarde)
    return f'{n:.0f},-'.replace('.', ',') if n == int(n) else f'{n:.2f}'.replace('.', ',')


def prijs(r):
    return f'€ {bedrag(r["prijs"])}' if r['prijs'] else '€ [PRIJS]'


def hoogtepunten(r):
    return [h.strip() for h in r['hoogtepunten'].split('|') if h.strip()]


def bundel(r, alles):
    """Bram biedt een bundelprijs als er meer uit dezelfde set ligt."""
    anderen = list(dict.fromkeys(
        a['soort'] for a in alles
        if a['set'] == r['set'] and a['sku'] != r['sku'] and a['aantal'] and a['prijs']))
    if not anderen:
        return ''
    lijst = ' of '.join([', '.join(anderen[:-1]), anderen[-1]]) if len(anderen) > 1 else anderen[0]
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
    if r['publiek']:
        d += [r['publiek'], '']
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


def fotoregel(r):
    """Bij meerdere identieke sealed dozen zijn de foto's van een exemplaar uit
    de voorraad, niet van het exemplaar dat de koper krijgt. Dat moet er staan,
    anders klopt de advertentie niet met wat er in de doos gaat."""
    if (int(r['aantal'] or 0)) > 1:
        return ("De foto's zijn van een exemplaar uit de voorraad; alle exemplaren zijn "
                "ongeopend en identiek.")
    return "De foto's zijn van dit exemplaar."


def webshop(r):
    d = [settekst(r['set']), '']
    if r['hoes'] == 'ja':
        d += ['Geleverd in de acryl beschermhoes waarin hij op de foto staat.', '']
    hp = hoogtepunten(r)
    if hp:
        d += ['Inhoud:', '']
        d += [f'- {h}' for h in hp]
        d += ['']
    if r['publiek']:
        d += [r['publiek'], '']
    d += [f'Staat: {r["staat"]}. {fotoregel(r)}', '',
          MERK['verzenden']]
    return '\n'.join(d)


def naar_html(tekst):
    """De webshoptekst omzetten naar de HTML die Shopify in het product zet.
    Alleen wat webshop() ook echt maakt: alinea's, een opsomming en een kop."""
    uit, lijst = [], []
    for blok in tekst.split('\n\n'):
        blok = blok.strip()
        if not blok:
            continue
        if blok.startswith('- '):
            lijst = [r[2:].strip() for r in blok.split('\n') if r.startswith('- ')]
            uit.append('<ul>\n' + '\n'.join(f'<li>{h}</li>' for h in lijst) + '\n</ul>')
        elif blok.startswith('**') and blok.endswith('**'):
            uit.append(f'<h3>{blok.strip("*")}</h3>')
        else:
            regel = ' '.join(blok.split('\n'))
            if regel.endswith(':') and len(regel) < 40:
                uit.append(f'<p><strong>{regel}</strong></p>')
            else:
                uit.append(f'<p>{regel}</p>')
    return '\n\n'.join(uit)


def schrijf(r, alles):
    UIT.mkdir(parents=True, exist_ok=True)
    doel = UIT / f'{r["sku"]}.md'
    doel.write_text('\n'.join([
        f'# {r["naam"]}', '',
        f'`{r["sku"]}` · set {r["set"]} · {prijs(r)}',
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

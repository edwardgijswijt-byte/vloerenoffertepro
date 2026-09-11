#!/usr/bin/env python3
"""Blogartikelen uit teksten/blog/*.md omzetten naar Shopify-HTML.

    python3 blog.py            alles
    python3 blog.py wat-is-een-elite-trainer-box

Uitvoer in teksten/uit/blog/<naam>.html plus een <naam>.json met titel,
samenvatting en tags, klaar om via de Shopify-koppeling als artikel aan te maken.

Elk bestand begint met een kopblok tussen streepjes: titel, samenvatting, tags
en soort. De samenvatting wordt de meta description en het eerste wat een
taalmodel te pakken krijgt, dus die moet op zichzelf een antwoord zijn en niet
"in dit artikel bespreken we".

De kop "Veelgestelde vragen" krijgt een bijzondere behandeling: de vetgedrukte
regels eronder worden vragen en de alinea erna het antwoord, en daar komt
FAQPage-schema van, dat achter de tekst in het .html-bestand komt te staan. Dat
is de reden dat elk artikel met zo'n blok eindigt — antwoordmachines pakken die
paren er rechtstreeks uit.

Markdown wordt met de hand omgezet en niet met een bibliotheek. Wat hier
voorkomt is beperkt: koppen, alinea's, lijsten, tabellen, vet en links. Een
afhankelijkheid erbij voor zes regelsoorten is het niet waard.
"""
import html
import json
import pathlib
import re
import sys

HIER = pathlib.Path(__file__).parent
WORTEL = HIER.parent
BRON = WORTEL / 'teksten' / 'blog'
UIT = WORTEL / 'teksten' / 'uit' / 'blog'


def kopblok(tekst):
    """Het blok tussen de eerste twee regels met alleen streepjes."""
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', tekst, re.S)
    if not m:
        raise ValueError('geen kopblok gevonden')
    kop = {}
    for regel in m.group(1).splitlines():
        if ':' in regel:
            sleutel, waarde = regel.split(':', 1)
            kop[sleutel.strip()] = waarde.strip()
    return kop, m.group(2)


def inline(t):
    """Vet, links en losse HTML-tekens binnen een regel."""
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    return t


def naar_html(lichaam):
    """Markdown omzetten. Geeft de HTML en de gevonden vraag-antwoordparen."""
    uit = []
    vragen = []
    in_faq = False
    regels = lichaam.split('\n')
    i = 0
    while i < len(regels):
        r = regels[i]

        if r.startswith('## '):
            titel = r[3:].strip()
            in_faq = titel.lower().startswith('veelgestelde')
            uit.append(f'<h2>{inline(titel)}</h2>')
            i += 1

        elif r.startswith('| '):
            tabel = []
            while i < len(regels) and regels[i].startswith('|'):
                tabel.append(regels[i])
                i += 1
            uit.append(tabel_html(tabel))

        elif r.startswith('- '):
            items = []
            while i < len(regels) and (regels[i].startswith('- ') or
                                       (regels[i].startswith('  ') and items)):
                if regels[i].startswith('- '):
                    items.append(regels[i][2:].strip())
                else:
                    items[-1] += ' ' + regels[i].strip()
                i += 1
            uit.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>')

        elif r.strip() == '':
            i += 1

        else:
            vraag = re.match(r'^\*\*(.+?)\*\*$', r.strip()) if in_faq else None
            if vraag:
                # Vraag en antwoord staan zonder witregel onder elkaar, dus de
                # regels tot de volgende lege regel zijn het antwoord.
                i += 1
                antwoord = []
                while i < len(regels) and regels[i].strip():
                    antwoord.append(regels[i].strip())
                    i += 1
                tekst = ' '.join(antwoord)
                vragen.append((vraag.group(1), tekst))
                uit.append(f'<h3>{inline(vraag.group(1))}</h3>')
                uit.append(f'<p>{inline(tekst)}</p>')
            else:
                alinea = []
                while i < len(regels) and regels[i].strip() and not regels[i].startswith(('## ', '- ', '|')):
                    alinea.append(regels[i].strip())
                    i += 1
                uit.append(f'<p>{inline(" ".join(alinea))}</p>')

    return '\n'.join(uit), vragen


def tabel_html(regels):
    rijen = [[c.strip() for c in r.strip('|').split('|')] for r in regels]
    rijen = [r for r in rijen if not all(set(c) <= set('-: ') for c in r)]
    kop, rest = rijen[0], rijen[1:]
    h = '<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in kop) + '</tr></thead>'
    b = '<tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rest) + '</tbody>'
    return f'<table>{h}{b}</table>'


def plat(tekst):
    """Markdown uit een zin halen, voor het schema.

    De vragen en antwoorden komen rechtstreeks uit de markdown, dus er kan
    opmaak in staan. In het FAQPage-schema hoort platte tekst: een antwoord met
    "[booster box](/collections/booster-boxes)" erin is wat een antwoordmachine
    letterlijk voorleest."""
    tekst = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', tekst)
    tekst = re.sub(r'\*\*([^*]+)\*\*', r'\1', tekst)
    return re.sub(r'`([^`]+)`', r'\1', tekst)


def faqschema(vragen):
    """Het FAQPage-schema dat onderaan de artikeltekst mee de winkel in gaat.

    Shopify laat een script-blok in de artikeltekst staan; dat is nagekeken.
    Het hoort hier en niet in een los bestand: eerder werd het met de hand
    achter de tekst geplakt bij het publiceren, en toen de tekst opnieuw werd
    gegenereerd stond het schema op het punt ongemerkt te verdwijnen. Wat in
    het .html-bestand staat is nu precies wat er in Shopify hoort te staan."""
    if not vragen:
        return ''
    inhoud = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': plat(v),
                        'acceptedAnswer': {'@type': 'Answer', 'text': plat(a)}}
                       for v, a in vragen],
    }
    return ('\n<script type="application/ld+json">'
            + json.dumps(inhoud, ensure_ascii=False) + '</script>')


def verwerk(pad):
    kop, lichaam = kopblok(pad.read_text(encoding='utf-8'))
    lijf, vragen = naar_html(lichaam)

    # De samenvatting bovenaan, zodat het antwoord vóór de uitleg staat.
    lijf = f'<p><strong>{inline(kop["samenvatting"])}</strong></p>\n' + lijf
    lijf += faqschema(vragen)

    UIT.mkdir(parents=True, exist_ok=True)
    (UIT / f'{pad.stem}.html').write_text(lijf, encoding='utf-8')
    (UIT / f'{pad.stem}.json').write_text(json.dumps({
        'handle': pad.stem,
        'titel': kop['titel'],
        'samenvatting': kop['samenvatting'],
        'tags': [t.strip() for t in kop.get('tags', '').split(',') if t.strip()],
        'soort': kop.get('soort', ''),
        'vragen': [{'vraag': v, 'antwoord': a} for v, a in vragen],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    return kop['titel'], len(vragen), len(lijf)


def main():
    keuze = sys.argv[1:]
    for pad in sorted(BRON.glob('*.md')):
        if keuze and pad.stem not in keuze:
            continue
        titel, n, lengte = verwerk(pad)
        print(f'{pad.stem:<38} {n} vragen  {lengte:>6} tekens  {titel}')


if __name__ == '__main__':
    main()

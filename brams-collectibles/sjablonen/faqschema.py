#!/usr/bin/env python3
"""FAQPage-schema genereren uit de vragenlijst op de startpagina.

    python3 faqschema.py

Leest theme/templates/index.json en schrijft theme/snippets/brams-faq-schema.liquid.

Waarom gegenereerd en niet met de hand: schema moet zeggen wat er op de pagina
staat. Zet je de vragen met de hand in een snippet, dan wijzigt iemand een tarief
in de thema-editor en staat er in de structured data nog het oude bedrag. Dan
beloof je in de zoekresultaten iets anders dan op de pagina, en dat is precies
waar Google een handmatige maatregel voor uitdeelt.

Draaien na elke wijziging aan de sectie `vragen`.
"""
import html
import json
import pathlib
import re

HIER = pathlib.Path(__file__).parent
WORTEL = HIER.parent
BRON = WORTEL / 'theme' / 'templates' / 'index.json'
DOEL = WORTEL / 'theme' / 'snippets' / 'brams-faq-schema.liquid'


def plat(rijke_tekst):
    """De HTML uit de thema-editor terugbrengen tot lopende tekst.

    Alineagrenzen worden een spatie; los daarvan zou "...de zorg komt van
    ons.Liever ophalen?" aan elkaar plakken."""
    t = re.sub(r'</p>\s*<p>', ' ', rijke_tekst)
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(t).strip()


def main():
    d = json.loads(BRON.read_text(encoding='utf-8'))
    sectie = d['sections'].get('vragen')
    if not sectie:
        raise SystemExit('sectie `vragen` niet gevonden in index.json')

    paren = []
    for sleutel in sectie['block_order']:
        s = sectie['blocks'][sleutel]['settings']
        vraag = (s.get('heading') or '').strip()
        antwoord = plat(s.get('row_content') or '')
        if vraag and antwoord:
            paren.append((vraag, antwoord))

    regels = [
        '{%- comment -%}',
        '  Gegenereerd door sjablonen/faqschema.py uit templates/index.json.',
        '  Niet met de hand bijwerken: wijzig de sectie `vragen` en draai het',
        '  script opnieuw, anders loopt de structured data uit de pas met wat',
        '  er op de pagina staat.',
        '{%- endcomment -%}',
        ',{',
        '  "@type": "FAQPage",',
        '  "@id": {{ request.origin | append: \'/#vragen\' | json }},',
        '  "mainEntity": [',
    ]
    for i, (vraag, antwoord) in enumerate(paren):
        komma = '' if i == len(paren) - 1 else ','
        regels += [
            '    {',
            '      "@type": "Question",',
            f'      "name": {json.dumps(vraag, ensure_ascii=False)},',
            '      "acceptedAnswer": {',
            '        "@type": "Answer",',
            f'        "text": {json.dumps(antwoord, ensure_ascii=False)}',
            '      }',
            f'    }}{komma}',
        ]
    regels += ['  ]', '}', '']

    DOEL.write_text('\n'.join(regels), encoding='utf-8')
    print(f'{DOEL.relative_to(WORTEL)}  —  {len(paren)} vragen')


if __name__ == '__main__':
    main()

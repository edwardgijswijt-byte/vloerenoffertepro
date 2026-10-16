#!/usr/bin/env python3
"""De beleidsteksten in shopify/paginas/ omzetten naar HTML voor Shopify.

    python3 beleidshtml.py            schrijft shopify/paginas/uit/<naam>.html

Wat niet meegaat: regels die met `>` beginnen. Dat zijn de aantekeningen voor
Bram en de jurist ("Laat dit nakijken", "Nog in te vullen"), en die horen niet
op een openbare pagina. Ook de kop `# ...` niet: Shopify zet de titel zelf.

Een alinea waarvan alle regels kort zijn (een adresblok) krijgt een <br> tussen
de regels; een alinea die met de hand op 78 tekens is afgebroken wordt aan
elkaar gezet. Zonder dat onderscheid staat het adres op één regel of de
voorwaarden vol harde enters.
"""
import html
import pathlib
import re

HIER = pathlib.Path(__file__).parent
BRON = HIER.parent / 'shopify' / 'paginas'
UIT = BRON / 'uit'
PAGINAS = ['algemene-voorwaarden', 'herroeping-en-retour', 'verzenden-en-leveren',
           'privacyverklaring', 'modelformulier-herroeping']


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*]+)\*(?![\w*])', r'<em>\1</em>', t)
    return t


def tabel(regels):
    rijen = [[c.strip() for c in r.strip().strip('|').split('|')] for r in regels]
    rijen = [r for r in rijen if not all(set(c) <= set('-: ') for c in r)]
    kop, rest = rijen[0], rijen[1:]
    return ('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in kop)
            + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
                      for r in rest) + '</tbody></table>')


def lijst(regels, i, tag, begin):
    items = []
    while i < len(regels) and (begin.match(regels[i]) or (regels[i].startswith('  ') and items)):
        m = begin.match(regels[i])
        if m:
            items.append(regels[i][m.end():].strip())
        else:
            items[-1] += ' ' + regels[i].strip()
        i += 1
    return f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>', i


def naar_html(md):
    regels = [r.rstrip() for r in md.split('\n') if not r.startswith('>')]
    uit, i = [], 0
    punt, getal = re.compile(r'^- '), re.compile(r'^\d+\. ')
    while i < len(regels):
        r = regels[i]
        if not r.strip() or r.startswith('# '):
            i += 1
        elif r.startswith('### '):
            uit.append(f'<h3>{inline(r[4:])}</h3>'); i += 1
        elif r.startswith('## '):
            uit.append(f'<h2>{inline(r[3:])}</h2>'); i += 1
        elif r.strip() == '---':
            uit.append('<hr>'); i += 1
        elif r.startswith('|'):
            blok = []
            while i < len(regels) and regels[i].startswith('|'):
                blok.append(regels[i]); i += 1
            uit.append(tabel(blok))
        elif punt.match(r):
            h, i = lijst(regels, i, 'ul', punt); uit.append(h)
        elif getal.match(r):
            h, i = lijst(regels, i, 'ol', getal); uit.append(h)
        else:
            blok = []
            while (i < len(regels) and regels[i].strip() and not regels[i].startswith(('#', '|', '>'))
                   and not punt.match(regels[i]) and not getal.match(regels[i])
                   and regels[i].strip() != '---'):
                blok.append(regels[i].strip()); i += 1
            kort = len(blok) > 1 and all(len(x) < 60 for x in blok)
            uit.append('<p>' + inline(('\n' if kort else ' ').join(blok)).replace('\n', '<br>\n') + '</p>')
    while uit and uit[-1] == '<hr>':     # de scheiding vóór een weggelaten aantekening
        uit.pop()
    return '\n'.join(uit)


def main():
    UIT.mkdir(exist_ok=True)
    for naam in PAGINAS:
        h = naar_html((BRON / f'{naam}.md').read_text(encoding='utf-8'))
        (UIT / f'{naam}.html').write_text(h + '\n', encoding='utf-8')
        haken = sorted(set(re.findall(r'\[[A-Z/ -]{3,}\]', h)))
        print(f'{naam:<28} {len(h):>6} tekens  haken: {", ".join(haken) or "geen"}')


if __name__ == '__main__':
    main()

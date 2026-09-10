#!/usr/bin/env python3
"""Een pagina drukklaar maken en er een pdf van bakken.

    python3 drukklaar.py bron.html doel.pdf

Chromium haalt tijdens het printen niets van Google Fonts op. Een pagina die
zijn lettertypes via een <link> laadt valt in de pdf terug op Liberation Sans.
Daarom worden de woff2-bestanden uit fonts-b64.json hier ingebakken.

Daarnaast gaat er printopmaak bij: knoppen en vinkvakjes eruit, één advertentie
per bladzijde, en de tekstblokken zonder schuifbalk zodat ze compleet afdrukken.
"""
import json, pathlib, re, subprocess, sys

HIER = pathlib.Path(__file__).parent
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
NODIG = [('Oswald', 500), ('Oswald', 600), ('Oswald', 700),
         ('Poppins', 400), ('Poppins', 500), ('Poppins', 600)]

DRUK = """
  @media print{
    :root{ --grond:#FFFFFF; --vlak:#FFFFFF; --inkt:#0D1B2A; --zacht:#5A6A78;
      --lijn:#D8D3C6; --lijn-zwak:#EAE6DB; --accent:#8C6E2A; --goed:#3D6B4E;
      --mist:#96421F; --code:#F7F5EF; --schaduw:none; }
    .kopieer, .gedaan{ display:none; }
    .ad{ break-inside:avoid; page-break-inside:avoid; }
    .ad + .ad{ break-before:page; page-break-before:always; }
    pre.tekst{ max-height:none; overflow:visible; }
    .wrap{ max-width:none; padding:0; }
    body{ font-size:11pt; }
    .beeld{ max-height:290px; width:auto; }
  }
"""


def gezichten():
    f = json.load(open(HIER / 'fonts-b64.json'))
    uit = []
    for naam, gewicht in NODIG:
        uit.append(f"  @font-face{{font-family:'{naam}';font-style:normal;"
                   f"font-weight:{gewicht};font-display:block;"
                   f"src:url(data:font/woff2;base64,{f[f'{naam}|{gewicht}']}) format('woff2');}}")
    return '\n'.join(uit)


def drukklaar(html):
    html = re.sub(r'\s*<link rel="preconnect"[^>]*>', '', html)
    html = re.sub(r'\s*<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', '', html)
    html = html.replace('<style>', '<style>\n' + gezichten(), 1)
    html = html.replace('</style>', DRUK + '</style>', 1)
    # de kopieerknoppen zijn weg in druk, dus de uitleg erover ook
    return html.replace('Titel en tekst kun je hier kopiëren en rechtstreeks in Marktplaats\n      plakken. De',
                        'Dit is wat er op Marktplaats komt te staan. De')


def main():
    if len(sys.argv) != 3:
        sys.exit('gebruik: drukklaar.py <bron.html> <doel.pdf>')
    bron, doel = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    druk = bron.with_name(bron.stem + '-druk.html')
    druk.write_text(drukklaar(bron.read_text(encoding='utf-8')), encoding='utf-8')
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', f'--print-to-pdf={doel}',
                    '--virtual-time-budget=8000', str(druk)],
                   check=True, capture_output=True)
    print(f'{doel}  {doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

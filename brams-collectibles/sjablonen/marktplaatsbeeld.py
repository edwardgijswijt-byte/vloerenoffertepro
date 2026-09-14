#!/usr/bin/env python3
"""Hoofdfoto voor Marktplaats, 1600x1600.

    python3 marktplaatsbeeld.py BC-CR-ETB IMG_3700 IMG_3701 ...

Alle foto's van een advertentie, niet alleen de hoofdfoto. De eerste wordt
<sku>.png, de rest <sku>-2.png en verder. Ze horen er allemaal hetzelfde uit
te zien: een koper die doorklikt moet niet ineens een ander sjabloon zien, en
de voetregel van het webshopsjabloon is tekst die hier niet hoort.

Alleen het logo en het product op de navy grond. Geen naam, geen prijs, geen
voetregel — die stonden er eerst wel in, maar Marktplaats zet titel en
vraagprijs zelf al naast de foto, en tekst in het beeld leest bij een kleine
weergave toch niet.

Het formaat ging van 1200x900 naar 1600x1600 toen de opnames van 2048 breed
naar 5712 gingen. Bij de oude foto's was er geen ruimte om groter te gaan
zonder op te blazen; nu wel.

En vierkant, niet liggend. De dozen staan rechtop en zijn dus hoog en smal:
op een liggend vlak van 4:3 mag zo'n doos maar 35 procent van de breedte
innemen voordat hij bovenaan het kader raakt, en dan staat hij verloren in het
midden. Vierkant geeft hem 46 procent. Bij een liggende doos, zoals een
display op zijn kant, verliest vierkant niets.
"""
import base64, csv, pathlib, subprocess, sys, tempfile, shutil
from PIL import Image

from huisstijl import NAVY, GOLD, CREAM, MUTED, FONTS, BASE, logo, frame, plateau, footer_mark

BREED, HOOG = 1600, 1600
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'
REGISTER = {r['sku']: r for r in csv.DictReader(
    open(HIER.parent / 'register.csv', encoding='utf-8'))}


def datauri(pad):
    return 'data:image/png;base64,' + base64.b64encode(pathlib.Path(pad).read_bytes()).decode()


def bedrag(waarde):
    """Nederlands: punt voor de duizendtallen, komma als decimaalteken, en hele
    bedragen als 1.740,- in plaats van 1.740,00."""
    n = float(waarde)
    heel, cent = divmod(round(n * 100), 100)
    duizend = f'{heel:,}'.replace(',', '.')
    return f'{duizend},-' if cent == 0 else f'{duizend},{cent:02d}'


def blad(sku, fotopad):
    """Het blad is nu zo kaal dat de sku er niet meer toe doet, maar hij blijft
    in de aanroep staan omdat de bestandsnaam van de uitvoer erop draait."""
    im = Image.open(fotopad)
    ruimte_h = HOOG * 0.78
    breed = round(im.width * min(ruimte_h / im.height, BREED * 0.70 / im.width, 1.15))

    inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:46px 0 0">{logo(132)}</div>
    <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 50px 10px">
      <img src="{datauri(fotopad)}" alt="" style="width:{breed}px;height:auto;max-height:100%;
        object-fit:contain;filter:drop-shadow(0 18px 30px rgba(0,0,0,.5))">
    </div>
{plateau(int(BREED * 0.44), bar=14, body=42)}
    <div style="flex:none;height:50px"></div>"""
    inner = inner.replace('src="logo.png"', f'src="{datauri(HIER / "logo.png")}"')
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
{FONTS}
{BASE}
</style></head><body style="margin:0;background:{NAVY}">
{frame(BREED, HOOG, inner, border=7, inset=4)}
</body></html>
"""


def schiet(sku, naam, doel):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(blad(sku, BRON / f'{naam}.png'), encoding='utf-8')
        subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        f'--window-size={BREED},{HOOG}', f'--screenshot={tmp / "s.png"}',
                        '--virtual-time-budget=3000', str(tmp / 'p.html')],
                       check=True, capture_output=True)
        shutil.copy(tmp / 's.png', doel)


def main():
    if len(sys.argv) < 3:
        sys.exit('gebruik: marktplaatsbeeld.py <sku> <opname> [<opname> ...]')
    sku, namen = sys.argv[1], sys.argv[2:]
    uit = HIER / 'export' / 'marktplaats'
    uit.mkdir(parents=True, exist_ok=True)

    # Oude extra beelden weg, anders blijft er een foto van een vorige reeks
    # tussen staan die niemand meer herkent.
    for oud in uit.glob(f'{sku}-*.png'):
        oud.unlink()

    for i, naam in enumerate(namen, 1):
        bron = BRON / f'{naam}.png'
        if not bron.exists():
            sys.exit(f'{bron} bestaat niet — draai eerst rechtzetten.py')
        doel = uit / (f'{sku}.png' if i == 1 else f'{sku}-{i}.png')
        schiet(sku, naam, doel)
        print(f'{doel.name:<20} {BREED}x{HOOG}  {naam}  {doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

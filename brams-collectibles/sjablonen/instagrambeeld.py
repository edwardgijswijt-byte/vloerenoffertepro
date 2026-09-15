#!/usr/bin/env python3
"""Instagram-beeld in de huisstijl, 1080x1350.

    python3 instagrambeeld.py BC-CR-ETB BC-CR-ETB-N1 BC-CR-ETB-N2

Waarom 4:5 en niet vierkant zoals bij Marktplaats: in de tijdlijn van Instagram
is 4:5 de hoogste verhouding die volledig getoond wordt. Een vierkant beeld
neemt daar een vijfde minder schermhoogte in bij dezelfde breedte, en op een
telefoon is schermhoogte het enige wat je hebt. Voor een doos die rechtop staat
komt het bovendien beter uit: die is hoog en smal.

1080 breed is de breedte waarop Instagram alles herschaalt. Groter aanleveren
levert niets op behalve een extra hercodering.

Verder hetzelfde sjabloon als de Marktplaats-beelden: alleen het logo en het
product op navy, geen tekst in het beeld. De tekst staat in het bijschrift, en
daar kan Instagram hem ook lezen — in het beeld niet.
"""
import base64
import pathlib
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

from huisstijl import NAVY, GOLD, CREAM, FONTS, BASE, logo, frame, plateau

BREED, HOOG = 1080, 1350
SCHAAL = BREED / 1600          # de maten van het Marktplaats-sjabloon meeschalen
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'


def mt(px):
    """Een maat uit het 1600-sjabloon omrekenen naar dit doek."""
    return max(1, round(px * SCHAAL))


def datauri(pad):
    return ('data:image/png;base64,'
            + base64.b64encode(pathlib.Path(pad).read_bytes()).decode())


def blad(fotopad):
    im = Image.open(fotopad)
    # Dezelfde drie plafonds als bij Marktplaats, maar de hoogte telt hier op
    # een hoger doek. Een staande doos mag daardoor groter dan op het vierkant.
    breed = round(im.width * min(HOOG * 0.74 / im.height,
                                 BREED * 0.86 / im.width, 2.0))
    inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:{mt(46)}px 0 0">{logo(mt(132))}</div>
    <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 {mt(50)}px {mt(10)}px">
      <img src="{datauri(fotopad)}" alt="" style="width:{breed}px;height:auto;max-height:100%;
        object-fit:contain;filter:drop-shadow(0 {mt(18)}px {mt(30)}px rgba(0,0,0,.5))">
    </div>
{plateau(round(BREED * 0.44), bar=mt(14), body=mt(42))}
    <div style="flex:none;height:{mt(50)}px"></div>"""
    inner = inner.replace('src="logo.png"', f'src="{datauri(HIER / "logo.png")}"')
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
{FONTS}
{BASE}
</style></head><body style="margin:0;background:{NAVY}">
{frame(BREED, HOOG, inner, border=mt(7), inset=mt(4))}
</body></html>
"""


def schiet(naam, doel):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(blad(BRON / f'{naam}.png'), encoding='utf-8')
        subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        f'--window-size={BREED},{HOOG}', f'--screenshot={tmp / "s.png"}',
                        '--virtual-time-budget=3000', str(tmp / 'p.html')],
                       check=True, capture_output=True)
        shutil.copy(tmp / 's.png', doel)


def main():
    if len(sys.argv) < 3:
        sys.exit('gebruik: instagrambeeld.py <sku> <opname> [<opname> ...]')
    sku, namen = sys.argv[1], sys.argv[2:]
    uit = HIER / 'export' / 'instagram'
    uit.mkdir(parents=True, exist_ok=True)
    for oud in uit.glob(f'{sku}-*.png'):
        oud.unlink()

    for i, naam in enumerate(namen, 1):
        bron = BRON / f'{naam}.png'
        if not bron.exists():
            sys.exit(f'{bron} bestaat niet — draai eerst rechtzetten.py')
        doel = uit / (f'{sku}.png' if i == 1 else f'{sku}-{i}.png')
        schiet(naam, doel)
        print(f'{doel.name:<20} {BREED}x{HOOG}  {naam}  {doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

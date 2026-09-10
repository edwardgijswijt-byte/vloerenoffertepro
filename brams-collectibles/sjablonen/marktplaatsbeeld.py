#!/usr/bin/env python3
"""Hoofdfoto voor Marktplaats, 1200x900.

    python3 marktplaatsbeeld.py BC-CR-ETB IMG_3700

Marktplaats toont je foto klein en tussen tientallen andere. Daarom staat de
naam en de prijs in het beeld zelf: wie scrollt ziet meteen wat het is en wat
het kost, zonder te klikken. De rest van de galerij zijn gewone opnames.

Naam en prijs komen uit register.csv.
"""
import base64, csv, pathlib, subprocess, sys, tempfile, shutil
from PIL import Image

from huisstijl import NAVY, GOLD, CREAM, MUTED, FONTS, BASE, logo, frame, plateau, footer_mark

BREED, HOOG = 1200, 900
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
BRON = HIER / 'fotos' / 'uitgesneden' / 'strak' / 'recht'
REGISTER = {r['sku']: r for r in csv.DictReader(
    open(HIER.parent / 'register.csv', encoding='utf-8'))}


def datauri(pad):
    return 'data:image/png;base64,' + base64.b64encode(pathlib.Path(pad).read_bytes()).decode()


def blad(sku, fotopad):
    r = REGISTER[sku]
    prijs = f"&euro; {r['prijs']},-" if r['prijs'] else '&euro; [PRIJS]'
    regel = 'Sealed &middot; Verzekerd verzonden &middot; Ophalen mogelijk'
    if r['hoes'] == 'ja':
        regel = 'Sealed &middot; In acrylhoes &middot; Verzekerd verzonden'

    im = Image.open(fotopad)
    ruimte = HOOG * 0.52
    breed = round(im.width * min(ruimte / im.height, BREED * 0.42 / im.width, 1.15))

    inner = f"""    <div style="flex:none;display:flex;align-items:center;gap:22px;padding:22px 30px 14px">
      {logo(84)}
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:5px">
        <div class="os" style="font-size:30px;font-weight:700;letter-spacing:.02em;color:{CREAM};
          text-transform:uppercase;line-height:1.05">{r['naam']}</div>
        <div class="os" style="font-size:15px;font-weight:500;letter-spacing:.19em;color:{MUTED};
          text-transform:uppercase">{regel}</div>
      </div>
      <div class="pp" style="font-size:38px;font-weight:700;color:{GOLD};line-height:1;flex:none;
        font-variant-numeric:tabular-nums;white-space:nowrap">{prijs}</div>
    </div>
    <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 40px 4px">
      <img src="{datauri(fotopad)}" alt="" style="width:{breed}px;height:auto;max-height:100%;
        object-fit:contain;filter:drop-shadow(0 16px 26px rgba(0,0,0,.5))">
    </div>
{plateau(int(BREED * 0.40), bar=11, body=34)}
    <div style="flex:none;padding:16px 0 20px">{footer_mark(size=14, gap=18, rule=120)}</div>"""
    inner = inner.replace('src="logo.png"', f'src="{datauri(HIER / "logo.png")}"')
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
{FONTS}
{BASE}
</style></head><body style="margin:0;background:{NAVY}">
{frame(BREED, HOOG, inner, border=6, inset=3)}
</body></html>
"""


def main():
    if len(sys.argv) != 3:
        sys.exit('gebruik: marktplaatsbeeld.py <sku> <opname>')
    sku, naam = sys.argv[1], sys.argv[2]
    bron = BRON / f'{naam}.png'
    if not bron.exists():
        sys.exit(f'{bron} bestaat niet — draai eerst rechtzetten.py')
    uit = HIER / 'export' / 'marktplaats'
    uit.mkdir(parents=True, exist_ok=True)
    doel = uit / f'{sku}.png'
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(blad(sku, bron), encoding='utf-8')
        subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                        f'--window-size={BREED},{HOOG}', f'--screenshot={tmp / "s.png"}',
                        '--virtual-time-budget=3000', str(tmp / 'p.html')],
                       check=True, capture_output=True)
        shutil.copy(tmp / 's.png', doel)
    print(f'{doel.name:<20} {BREED}x{HOOG}  {naam}  {doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

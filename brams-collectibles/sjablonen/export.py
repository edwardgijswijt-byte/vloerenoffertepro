#!/usr/bin/env python3
"""Sjablonen als PNG wegschrijven, op ware grootte.

python3 export.py                 alles uit canvas.json
python3 export.py Prismatic       alleen wat met Prismatic begint

Uitvoer in export/. Drukwerk gaat op 300 dpi (schaal 3,125x t.o.v. 96 dpi),
online op 1x omdat de maten al in pixels kloppen.
"""
import json, base64, pathlib, re, subprocess, sys, tempfile, shutil

CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent
UIT = HIER / 'export'
DRUKWERK = {'Banner', 'VisiteVoor', 'VisiteAchter', 'Verzendkaart'}
DPI_SCHAAL = 300 / 96          # 96 dpi css-pixels -> 300 dpi drukbestand


def datauri(pad):
    p = HIER / pad
    mime = 'image/png' if p.suffix == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


def standalone(dc_html):
    """Van .dc.html naar een gewone pagina die chromium kan renderen."""
    t = dc_html
    t = t.replace('<script src="./support.js"></script>', '')
    t = t.replace('<x-dc>', '').replace('</x-dc>', '')
    t = t.replace('<helmet>', '').replace('</helmet>', '')
    # alle lokale afbeeldingen inbakken
    for m in set(re.findall(r'src="([^"h][^":]*\.(?:png|jpg|jpeg))"', t)):
        t = t.replace(f'src="{m}"', f'src="{datauri(m)}"')
    t = t.replace('<body>', '<body style="margin:0;background:transparent">')
    return t


def schiet(html, w, h, doel, schaal=1):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / 'p.html').write_text(html, encoding='utf-8')
        subprocess.run([
            CHROME, '--disable-gpu', '--no-sandbox',
            '--hide-scrollbars', '--force-device-scale-factor=%g' % schaal,
            '--default-background-color=00000000',
            f'--window-size={w},{h}',
            f'--screenshot={tmp / "s.png"}',
            f'--virtual-time-budget=2500',
            str(tmp / 'p.html'),
        ], check=True, capture_output=True)
        doel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp / 's.png', doel)


def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ''
    canvas = json.loads((HIER / 'canvas.json').read_text(encoding='utf-8'))
    for ab in canvas['artboards']:
        naam = ab['file'].replace('.dc.html', '')
        if filt and not naam.startswith(filt):
            continue
        html = standalone((HIER / ab['file']).read_text(encoding='utf-8'))
        schaal = DPI_SCHAAL if naam in DRUKWERK else 1
        doel = UIT / f'{naam}.png'
        schiet(html, ab['w'], ab['h'], doel, schaal)
        from PIL import Image
        im = Image.open(doel)
        print(f'{naam:<26} {im.width}x{im.height}  {doel.stat().st_size // 1024:>5} KB'
              f'{"  (300 dpi)" if schaal != 1 else ""}')


if __name__ == '__main__':
    main()

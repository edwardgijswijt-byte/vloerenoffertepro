#!/usr/bin/env python3
"""De vier pictogrammen voor het blok "Waarom bij Brams Collectibles".

Dunne gouden lijntekeningen op transparant, 240x240. Shopify's
multicolumn-blok wil een bestand uit de winkel, dus deze gaan er als
afbeelding in; brams.css houdt ze klein.
"""
import pathlib, subprocess, tempfile, shutil

from huisstijl import GOLD

ZIJ = 240
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
HIER = pathlib.Path(__file__).parent

# naam, svg-inhoud binnen een viewBox van 24
TEKENS = {
    'sealed': '<rect x="4" y="10.5" width="16" height="10" rx="2"/>'
              '<path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><circle cx="12" cy="15.5" r="1.4"/>',
    'plank':  '<path d="M3 7.5h18M3 12h18M3 16.5h18"/>'
              '<path d="M6.5 7.5v-2h4v2M13 12v-2h4.5v2M8 16.5v-2h5v2"/>',
    'prijs':  '<path d="M20.5 12.3 12.8 20a1.7 1.7 0 0 1-2.4 0l-6.9-6.9a1.7 1.7 0 0 1-.5-1.2V4.8'
              'c0-.9.7-1.6 1.6-1.6h7.1c.4 0 .9.2 1.2.5l7.6 7.6c.3.3.3.7 0 1z"/>'
              '<circle cx="7.8" cy="7.8" r="1.5"/>',
    'verzenden': '<path d="M2.5 6.5h10.5v10H2.5z"/><path d="M13 9.5h4l3.5 3.5v3.5H13z"/>'
                 '<circle cx="6.5" cy="18" r="1.8"/><circle cx="16.5" cy="18" r="1.8"/>',
}


def blad(pad):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  html,body{{margin:0;background:transparent}}
</style></head>
<body>
  <svg xmlns="http://www.w3.org/2000/svg" width="{ZIJ}" height="{ZIJ}" viewBox="0 0 24 24"
    fill="none" stroke="{GOLD}" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round">
    {pad}
  </svg>
</body></html>
"""


def main():
    uit = HIER / 'export' / 'pictogrammen'
    uit.mkdir(parents=True, exist_ok=True)
    for naam, pad in TEKENS.items():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / 'p.html').write_text(blad(pad), encoding='utf-8')
            subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                            '--default-background-color=00000000',
                            f'--window-size={ZIJ},{ZIJ}', f'--screenshot={tmp / "s.png"}',
                            '--virtual-time-budget=2000', str(tmp / 'p.html')],
                           check=True, capture_output=True)
            doel = uit / f'brams-icoon-{naam}.png'
            shutil.copy(tmp / 's.png', doel)
            print(f'{doel.name:<28} {ZIJ}x{ZIJ}  {doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

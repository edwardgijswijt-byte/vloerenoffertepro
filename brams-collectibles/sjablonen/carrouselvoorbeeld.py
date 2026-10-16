#!/usr/bin/env python3
"""De carrousel van de startpagina renderen en er schermafbeeldingen van maken.

    /usr/bin/python3 carrouselvoorbeeld.py

Rendert theme/sections/brams-carrousel.liquid met python-liquid, zet de uitvoer
in een kale pagina met de huisstijl-lettertypes en de kleuren van het
kleurenschema, en fotografeert die met Chromium op bureaubladbreedte en op
telefoonbreedte, voor drie standen van de carrousel.

Dit is geen Shopify: Dawn's eigen stijlen (page-width, button, h0) staan hieronder
nagebouwd, ruw maar genoeg om te zien of de indeling klopt. De producten komen
uit voorbeeld.json, een uitvoer van de Admin API.
"""
import json
import pathlib
import re
import subprocess
import sys

from liquid import Environment
from liquid import FileSystemLoader

HIER = pathlib.Path(__file__).parent
WORTEL = HIER.parent
sys.path.insert(0, str(HIER))
from huisstijl import FONTS  # noqa: E402

CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
UIT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HIER / 'export' / 'carrousel'


class Ding(dict):
    def __getattr__(self, naam):
        if naam.startswith('__'):
            raise AttributeError(naam)
        return self.get(naam, '')


def geld(v):
    return '€ ' + f'{float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.').replace(',00', ',-')


# Het CDN van Shopify is vanuit hier niet bereikbaar; het voorbeeld gebruikt
# daarom de eigen bestanden. Pad's wijzen naar waar de zip's zijn uitgepakt.
SCRATCH = pathlib.Path('/tmp/claude-0/-home-user-vloerenoffertepro/0fbb172d-86b0-546f-aebf-1f0b2c2d218f/scratchpad')
LOKAAL = {
    'pokemon-tcg-30th-anniversary-ultra-premium-collection': 'prod5/59.png',
    'pokemon-tcg-30th-anniversary-elite-trainer-box-pokemon-center': 'prod5/53.png',
    'prismatic-evolutions-pokemon-center-elite-trainer-box': 'prod4/5.png',
    'prismatic-evolutions-super-premium-collection': 'prod/25.png',
    'pokemon-tcg-30th-anniversary-greninja-ex-box': 'prod5/54.png',
    'ascended-heroes-pokemon-center-elite-trainer-box': 'prod4/7.png',
    'pokemon-tcg-30th-anniversary-elite-trainer-box': 'prod5/51.png',
    'destined-rivals-elite-trainer-box': 'prod2/19.png',
}


def beeld(p):
    pad = SCRATCH / LOKAAL.get(p['handle'], '')
    if pad.is_file():
        import base64
        return 'data:image/png;base64,' + base64.b64encode(pad.read_bytes()).decode()
    return p['featuredMedia']['preview']['image']['url']


def product(p):
    bedrag = float(p['priceRangeV2']['minVariantPrice']['amount'])
    return Ding(title=p['title'], url='/products/' + p['handle'], type=p['productType'], tags=p['tags'],
                price=bedrag, available=True,
                featured_media=Ding(url=beeld(p)))


def bouw(producten):
    env = Environment(loader=FileSystemLoader(str(WORTEL / 'theme' / 'sections')))
    env.filters['money'] = lambda v: geld(v)
    env.filters['image_url'] = lambda v, **kw: v['url'] if isinstance(v, dict) else v
    env.filters['image_tag'] = lambda v, **kw: f'<img src="{v}" alt="{kw.get("alt", "")}" width="800" height="800">'
    tekst = (WORTEL / 'theme' / 'sections' / 'brams-carrousel.liquid').read_text(encoding='utf-8')
    tekst = re.sub(r'\{%\s*schema\s*%\}.*?\{%\s*endschema\s*%\}', '', tekst, flags=re.S)
    tekst = re.sub(r'\{%-?\s*style\s*-?%\}', '<style>', tekst)
    tekst = re.sub(r'\{%-?\s*endstyle\s*-?%\}', '</style>', tekst)
    verzameling = Ding(products=[product(p) for p in producten], products_count=len(producten))
    instellingen = Ding(heading='Sealed Pokémon TCG, uit eigen voorraad',
                        subheading='Gestart als fan. Voor de verzamelaar. Voor de community.',
                        collection=verzameling, aantal=8, interval=5, color_scheme='scheme-1',
                        padding_top=40, padding_bottom=40)
    return env.from_string(tekst).render(section=Ding(id='voorbeeld', settings=instellingen),
                                         request=Ding(design_mode=False))


PAGINA = """<!doctype html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
{fonts}
:root{{--font-heading-family:'Oswald','Arial Narrow',sans-serif;--font-body-family:'Poppins',Arial,sans-serif;
--brams-navy:#0d1b2a;--brams-gold:#c9a24b}}
html{{font-size:62.5%}}
body{{margin:0;background:#0d1b2a;color:#f2efe6;font-family:var(--font-body-family);font-size:1.6rem}}
.page-width{{max-width:120rem;margin:0 auto;padding:0 1.5rem}}
@media(min-width:750px){{.page-width{{padding:0 5rem}}}}
h1,h2{{font-family:var(--font-heading-family);text-transform:uppercase;font-weight:700;letter-spacing:.012em}}
.h0,.h1{{font-size:clamp(3rem,4.2vw,5.2rem);line-height:1.05}}
.h2{{font-size:clamp(2.4rem,3vw,3.6rem)}}
.button{{display:inline-block;padding:1.3rem 3.4rem;background:#c9a24b;color:#0d1b2a;font-family:var(--font-heading-family);
font-weight:600;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;font-size:1.4rem}}
.center{{text-align:center}}
</style></head><body>{html}</body></html>"""


def foto(html, naam, breed, hoog, wacht=4000, stap=0):
    UIT.mkdir(parents=True, exist_ok=True)
    pagina = UIT / f'{naam}.html'
    pagina.write_text(html, encoding='utf-8')
    subprocess.run([CHROME, '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    f'--window-size={breed},{hoog}', f'--screenshot={UIT / (naam + ".png")}',
                    f'--virtual-time-budget={wacht}', str(pagina)], check=True, capture_output=True)


def main():
    producten = json.loads((HIER / 'voorbeeld.json').read_text(encoding='utf-8'))
    html = bouw(producten)
    basis = PAGINA.format(fonts=FONTS, html=html)
    foto(basis, 'bureaublad-1', 1440, 1000)
    foto(basis, 'telefoon-1', 390, 900)
    # een latere stand: de pagina laten klikken op "volgende" voordat hij fotografeert
    klik = basis.replace('</body>', '<script>window.addEventListener("load",function(){var v=document.querySelector("[data-volgende]");v.click();v.click();v.click();});</script></body>')
    foto(klik, 'bureaublad-4', 1440, 1000)
    foto(klik, 'telefoon-4', 390, 900)
    print(f'klaar: {UIT}')


if __name__ == '__main__':
    main()

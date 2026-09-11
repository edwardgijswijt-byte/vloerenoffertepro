#!/usr/bin/env python3
"""De structured data van het thema renderen en als JSON controleren.

    python3 schemacontrole.py

Rendert snippets/brams-schema.liquid met python-liquid voor elk paginatype en
kijkt of er geldige JSON uit komt. Shopify's Liquid kent filters die
python-liquid niet heeft (image_url, money, structured_data); die staan hieronder
nagebouwd, ruw maar genoeg om de komma's en haakjes te toetsen.

Dit vangt wat je met het blote oog mist: een komma te veel voor een `}`, een
voorwaardelijk veld dat de laatste is in zijn blok, een `{%- case -%}` die op een
paginatype niets teruggeeft en het `@graph` leeg laat. Allemaal fouten die pas
zichtbaar worden als Search Console er weken later over klaagt.
"""
import datetime
import json
import pathlib
import re
import sys

from liquid import Environment
from liquid import FileSystemLoader

WORTEL = pathlib.Path(__file__).parent.parent
THEMA = WORTEL / 'theme'


def zetop(env):
    """De Shopify-filters die in het snippet voorkomen."""
    env.filters['json'] = lambda v, *a: json.dumps(v, ensure_ascii=False)
    env.filters['image_url'] = lambda v, **kw: f'//cdn.example/{v}_1600x.png'
    env.filters['strip_html'] = lambda v: re.sub(r'<[^>]+>', '', str(v))
    env.filters['truncate'] = lambda v, n=50, end='...': str(v)[:n]
    env.filters['divided_by'] = lambda v, d: v / d if isinstance(d, float) else v // d
    env.filters['append'] = lambda v, s: f'{v}{s}'
    env.filters['prepend'] = lambda v, s: f'{s}{v}'
    env.filters['date'] = lambda v, f=None: (v.strftime(f) if hasattr(v, 'strftime')
                                             else str(v))


class Ding(dict):
    """Een Liquid-drop nabootsen: puntnotatie op een dict.

    Alleen voor gewone namen. Vraagt python-liquid naar `__liquid__` of een
    andere dunder, dan moet dat een AttributeError geven; geef je daar een
    lege string op terug, dan probeert de renderer die aan te roepen."""
    def __getattr__(self, naam):
        if naam.startswith('__'):
            raise AttributeError(naam)
        return self.get(naam, '')


PRODUCT = Ding(
    title='Chaos Rising Pokémon Center Elite Trainer Box',
    description='<p>Elf packs en twee Fennekin-promo\'s.</p>',
    url='/products/chaos-rising-pokemon-center-elite-trainer-box',
    type='Elite Trainer Box',
    images=['a.png', 'b.png'],
    selected_or_first_available_variant=Ding(sku='BC-CR-PCETB', price=15500, available=True),
)

ARTIKEL = Ding(
    title='Wat is een Elite Trainer Box en wat zit erin?',
    url='/blogs/gids/wat-is-een-elite-trainer-box',
    excerpt_or_content='<p>Een Elite Trainer Box bevat negen booster packs.</p>',
    published_at=datetime.datetime(2026, 9, 10, 14, 30, tzinfo=datetime.timezone.utc),
    image='artikel.png',
)

COLLECTIE = Ding(
    title='Elite Trainer Boxes',
    description='<p>Alle ETB\'s uit voorraad.</p>',
    url='/collections/elite-trainer-boxes',
    products_count=7,
    products=[Ding(title=f'Doos {i}', url=f'/products/doos-{i}') for i in range(1, 4)],
)

GEVALLEN = {
    'index':      dict(product=None, collection=None),
    'product':    dict(product=PRODUCT, collection=COLLECTIE),
    'product (los, geen collectie)': dict(product=PRODUCT, collection=None, _type='product'),
    'collection': dict(product=None, collection=COLLECTIE),
    'article':    dict(blog=Ding(title='Gids', url='/blogs/gids'), article=ARTIKEL),
    # Een artikel zonder afbeelding: dat veld staat tussen komma's en is het
    # soort veld waar een schema op stukloopt als de guard ontbreekt.
    'article (zonder afbeelding)': dict(
        blog=Ding(title='Gids', url='/blogs/gids'),
        article=Ding(ARTIKEL, image=None), _type='article'),
    'page':       dict(page=Ding(title='Over Brams')),
    'cart':       dict(),
    '404':        dict(),
}


def main():
    env = Environment(loader=FileSystemLoader(str(THEMA / 'snippets'), ext='.liquid'))
    zetop(env)
    sjabloon = env.get_template('brams-schema.liquid')

    fout = 0
    for naam, extra in GEVALLEN.items():
        paginatype = extra.pop('_type', naam)
        context = dict(
            request=Ding(origin='https://bramscollectibles.nl', page_type=paginatype),
            shop=Ding(name='Brams Collectibles'),
            settings=Ding(logo='logo.png'),
            cart=Ding(currency=Ding(iso_code='EUR')),
            **extra,
        )
        uit = sjabloon.render(**context)
        rauw = uit.split('<script type="application/ld+json">')[1].split('</script>')[0]
        try:
            data = json.loads(rauw)
        except json.JSONDecodeError as e:
            fout += 1
            regels = rauw.splitlines()
            print(f'{naam:<32} ONGELDIGE JSON — {e}')
            for r in regels[max(0, e.lineno - 3):e.lineno + 2]:
                print(f'     {r}')
            continue
        soorten = [k.get('@type') for k in data['@graph']]
        print(f'{naam:<32} geldig — {", ".join(soorten)}')
    return 1 if fout else 0


if __name__ == '__main__':
    sys.exit(main())

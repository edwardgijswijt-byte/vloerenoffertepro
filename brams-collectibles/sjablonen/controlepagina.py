#!/usr/bin/env python3
"""Controlepagina: alle artikelen op een rij, om door Bram te laten nakijken.

    python3 controlepagina.py                 -> export/controle.html
    python3 drukklaar.py export/controle.html export/controle.pdf

Eén blok per artikel met alle opnames naast elkaar, de feiten eronder en de
webshoptekst erbij. Bedoeld om één vraag te kunnen beantwoorden: klopt dit met
de doos die hier op de plank staat?

De opnamenummers staan er bewust bij. Wijst Bram een foto af, dan weet je
meteen welk bestand eruit moet, zonder te hoeven zoeken.
"""
import base64
import csv
import html
import io
import pathlib
import sys

from PIL import Image

HIER = pathlib.Path(__file__).parent
BASIS = HIER.parent
sys.path.insert(0, str(BASIS))

import teksten  # noqa: E402

NAVY, PANEL, GOLD, CREAM = '#0D1B2A', '#16253A', '#C9A24B', '#F2EFE6'


def mini(pad, breed=460):
    """Verkleind en als data-URI, anders is het bestand niet te delen."""
    im = Image.open(pad).convert('RGB')
    im.thumbnail((breed, breed * 4))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def opnames(r):
    """De geordende bronopnames uit het register, als die er staan."""
    return [o.strip() for o in (r.get('opnames') or '').split('|') if o.strip()]


def blok(r, alles, nr, totaal):
    sku = r['sku']
    beelden = sorted((HIER / 'export' / 'webshop').glob(f'{sku}-*.png'),
                     key=lambda p: int(p.stem.rsplit('-', 1)[1]))
    bronnen = opnames(r)

    kaarten = []
    for i, b in enumerate(beelden):
        bron = bronnen[i] if i < len(bronnen) else '?'
        merk = ' <span class="hoofd">hoofdfoto</span>' if i == 0 else ''
        kaarten.append(
            f'<figure><img src="{mini(b)}" alt="">'
            f'<figcaption>{i + 1}. {html.escape(bron)}{merk}</figcaption></figure>')

    voorraad = f"{r['aantal']} stuk" + ('s' if int(r['aantal'] or 0) != 1 else '')
    feiten = [
        ('Vraagprijs', teksten.prijs(r)),
        ('Voorraad', voorraad),
        ('Soort', r['soort']),
        ('Gewicht', f"{r['gewicht_g']} gram" if r['gewicht_g'] else '<b>nog niet gewogen</b>'),
        ('Acryl hoes', 'ja' if r['hoes'] == 'ja' else 'nee'),
    ]
    rijen = ''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in feiten)

    return f"""<article class="art">
  <header><span class="nr">{nr} van {totaal}</span>
    <h2>{html.escape(r['naam'])}</h2>
    <code>{sku}</code></header>
  <div class="beelden">{''.join(kaarten)}</div>
  <div class="onder">
    <table>{rijen}</table>
    <div class="tekst"><h3>Wat er op de webshop staat</h3>
      <pre>{html.escape(teksten.webshop(r))}</pre></div>
  </div>
  <div class="vink">Klopt dit?&nbsp; <span class="vak">ja</span>
    <span class="vak">nee, want:</span><span class="lijn"></span></div>
</article>"""


STIJL = f"""
body{{margin:0;background:{CREAM};color:{NAVY};
  font:15px/1.6 Georgia,'Times New Roman',serif}}
.wrap{{max-width:940px;margin:0 auto;padding:40px 28px 80px}}
h1{{font-family:Oswald,'Arial Narrow',Arial,sans-serif;font-weight:700;
  text-transform:uppercase;letter-spacing:.12em;font-size:30px;margin:0 0 6px}}
.lead{{color:#5A6A78;margin:0 0 36px;max-width:64ch}}
.art{{background:#fff;border:1px solid #E3DECF;border-radius:10px;
  padding:26px 28px 22px;margin:0 0 26px}}
.art header{{border-bottom:2px solid {GOLD};padding-bottom:12px;margin-bottom:18px}}
.nr{{float:right;color:#8C8579;font-size:13px}}
h2{{font-family:Oswald,'Arial Narrow',Arial,sans-serif;font-weight:600;
  font-size:21px;margin:0 0 4px;letter-spacing:.02em}}
code{{color:#8C8579;font-size:12px}}
.beelden{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:18px}}
figure{{margin:0;width:150px}}
figure img{{width:100%;border-radius:6px;display:block;background:{NAVY}}}
figcaption{{font-size:11px;color:#5A6A78;padding-top:5px}}
.hoofd{{color:#8C6E2A;font-weight:700}}
.onder{{display:flex;gap:26px;align-items:flex-start}}
table{{border-collapse:collapse;flex:none;width:260px;font-size:14px}}
th{{text-align:left;font-weight:400;color:#5A6A78;padding:3px 14px 3px 0;
  white-space:nowrap;vertical-align:top}}
td{{padding:3px 0}}
.tekst{{flex:1;min-width:0}}
h3{{font-family:Oswald,'Arial Narrow',Arial,sans-serif;font-weight:500;
  text-transform:uppercase;letter-spacing:.14em;font-size:12px;
  color:#5A6A78;margin:0 0 8px}}
pre{{white-space:pre-wrap;font:13px/1.55 Georgia,serif;margin:0;
  background:#F7F5EF;border-radius:6px;padding:14px 16px;max-height:340px;
  overflow:auto}}
.vink{{margin-top:18px;padding-top:14px;border-top:1px solid #EAE6DB;
  font-size:13px;color:#5A6A78}}
.vak{{display:inline-block;border:1px solid #C9C2B2;border-radius:3px;
  padding:2px 10px;margin-right:10px}}
.lijn{{display:inline-block;border-bottom:1px solid #C9C2B2;width:38%;
  vertical-align:bottom}}
@media print{{
  body{{background:#fff}}
  .wrap{{max-width:none;padding:0}}
  .art{{break-inside:avoid;page-break-inside:avoid;border:none;
    border-top:2px solid {GOLD};border-radius:0;padding:18px 0}}
  .art + .art{{break-before:page;page-break-before:always}}
  pre{{max-height:none;overflow:visible}}
}}
"""


def main():
    alles = list(csv.DictReader(open(BASIS / 'register.csv', encoding='utf-8')))
    tonen = [r for r in alles
             if r['aantal'] and list((HIER / 'export' / 'webshop').glob(f"{r['sku']}-*.png"))]
    blokken = [blok(r, alles, i, len(tonen)) for i, r in enumerate(tonen, 1)]

    doel = HIER / 'export' / 'controle.html'
    doel.write_text(f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<title>Brams Collectibles — controle</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap">
<style>{STIJL}</style></head><body><div class="wrap">
<h1>Nakijken voor plaatsing</h1>
<p class="lead">Alle {len(tonen)} artikelen die klaarstaan, met de foto's die
erbij horen en de tekst die op de webshop staat. Het nummer onder elke foto is
de bronopname — noem dat nummer als er een foto niet klopt, dan is hij zo te
vervangen. De drie First Partner-cases staan er niet bij: daar zijn nog geen
foto's van.</p>
{''.join(blokken)}
</div></body></html>""", encoding='utf-8')
    print(f'{doel.relative_to(BASIS)}  {doel.stat().st_size // 1024} KB  '
          f'{len(tonen)} artikelen')


if __name__ == '__main__':
    main()

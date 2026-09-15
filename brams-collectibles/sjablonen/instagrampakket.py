#!/usr/bin/env python3
"""Instagram-posts klaarzetten: beeld, bijschrift, hashtags en alt-tekst.

    python3 instagrampakket.py           -> export/instagram-posts.zip

Per artikel een map met:

    1.jpg, 2.jpg      de beelden op 1080x1350, in de volgorde van plaatsen
    bijschrift.txt    het bijschrift, en verder niets — alles selecteren,
                      plakken
    hashtags.txt      de hashtags, apart zodat je ze als eerste reactie kunt
                      plaatsen als je het bijschrift schoon wilt houden
    alt-tekst.txt     per foto een regel voor het alt-tekstveld

Waarom de hashtags apart staan: in het bijschrift of in de eerste reactie maakt
voor het bereik niets uit — Instagram leest ze allebei. Het verschil is dat een
bijschrift met twintig tags eronder er rommelig uitziet in de tijdlijn. Wie dat
niet erg vindt plakt ze gewoon achter het bijschrift.

Het alt-tekstveld zit onder "Geavanceerde instellingen" bij het plaatsen. De
meeste accounts laten het leeg; Instagram leest het wel mee bij het zoeken, dus
het is bereik dat je gratis kunt hebben.
"""
import csv
import io
import pathlib
import re
import sys
import zipfile

from PIL import Image

HIER = pathlib.Path(__file__).parent
BASIS = HIER.parent
sys.path.insert(0, str(BASIS))
import teksten  # noqa: E402

BEELD = HIER / 'export' / 'instagram'
JPEG_BREED = 1080


def jpeg(pad):
    im = Image.open(pad).convert('RGB')
    if im.width > JPEG_BREED:
        im = im.resize((JPEG_BREED, round(im.height * JPEG_BREED / im.width)),
                       Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=90, optimize=True)
    return buf.getvalue()


def mapnaam(r):
    naam = r['naam'].replace('&', 'en')
    schoon = ''.join(c if c.isalnum() or c in ' -' else '' for c in naam)
    return re.sub(r'-+', '-', schoon.strip().replace(' ', '-')).strip('-')


def spreiden(rijen):
    """De volgorde waarin je plaatst: voorraad eerst, maar geen twee sets
    achter elkaar.

    Twee overwegingen die elkaar tegenwerken. Voorraad aflopend is de goede
    grondvolgorde — op Instagram plaats je over weken verspreid, en dan begin
    je bij wat je nog lang kunt leveren en niet bij het enige exemplaar dat je
    hebt. Maar alle artikelen uit dezelfde set delen dezelfde alinea uit
    teksten/sets/, en van Chaos Rising liggen er vijf. Op Marktplaats geeft dat
    niets: dat zijn losse advertenties voor losse kopers. Een volger ziet ze
    alle vijf, en drie keer achter elkaar dezelfde alinea leest als opvulling.

    Daarom om de beurt uit de sets, grootste set eerst. Binnen een set blijft
    de volgorde op voorraad staan. Zolang geen set meer dan de helft van alles
    is — vijf van achttien hier — komt er nergens twee keer dezelfde set achter
    elkaar."""
    groepen = {}
    for r in rijen:
        groepen.setdefault(r['set'], []).append(r)
    uit, vorige = [], None
    while any(groepen.values()):
        # De volste set eerst, maar nooit twee keer dezelfde achter elkaar.
        # Alleen op omvang kiezen is niet genoeg: na het trekken uit de volste
        # set is die vaak nog steeds de volste, en dan komt hij meteen weer aan
        # de beurt. Zo stonden de drie Chaos Rising-artikelen op 1, 2 en 3.
        keuze = sorted((s for s, g in groepen.items() if g and s != vorige),
                       key=lambda s: -len(groepen[s]))
        if not keuze:                       # alleen de vorige set nog over
            keuze = [s for s, g in groepen.items() if g]
        vorige = keuze[0]
        uit.append(groepen[vorige].pop(0))
    return uit


def lijst(klaar, alles):
    """Alles onder elkaar in een markdownbestand, om naast het scherm te
    houden tijdens het plaatsen. Zelfde gedachte als plaatslijst.py voor
    Marktplaats: je wilt niet halverwege ontdekken dat er van een artikel nog
    geen beeld is."""
    uit = BASIS / 'teksten' / 'uit' / '_instagram-plaatsen.md'
    d = ['# Instagram — posts klaar om te plaatsen', '',
         'Volgorde: meeste voorraad eerst, nooit twee keer dezelfde set achter',
         'elkaar. De hashtags kun je achter het bijschrift plakken of als eerste',
         'reactie plaatsen; voor het bereik maakt dat niet uit.', '']
    d += ['## 00. Openingspost', '',
          'Beeld: het logo.', '',
          '**Bijschrift**', '', '```', teksten.openingspost(alles), '```', '',
          '**Hashtags**', '', '```', ' '.join(teksten.openingstags()), '```', '',
          '---', '']
    for nr, r in enumerate(klaar, 1):
        d += [f'## {nr:02d}. {r["naam"]}', '',
              f'Voorraad {r["aantal"]} · {teksten.prijs(r)} · '
              f'beeld `export/instagram/{r["sku"]}.png`', '',
              '**Bijschrift**', '', '```', teksten.instagram(r, alles), '```', '',
              '**Hashtags**', '', '```', ' '.join(teksten.hashtags(r)), '```', '',
              '**Alt-tekst**', '', '```', teksten.alttekst(r), '```', '',
              '---', '']
    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text('\n'.join(d), encoding='utf-8')
    print(f'{uit.relative_to(BASIS.parent)}  {len(klaar)} posts')


def main():
    alles = list(csv.DictReader(open(BASIS / 'register.csv', encoding='utf-8')))
    klaar = [r for r in alles
             if r['aantal'] and r['prijs'] and (BEELD / f"{r['sku']}.png").exists()]
    klaar.sort(key=lambda r: (-int(r['aantal']), -float(r['prijs'])))
    klaar = spreiden(klaar)

    doel = HIER / 'export' / 'instagram-posts.zip'
    regels = ['Instagram — postpakket', '',
              f'{len(klaar)} posts, in de volgorde waarin je ze het beste plaatst:',
              'de meeste voorraad eerst, maar nooit twee keer dezelfde set',
              'achter elkaar.', '',
              'Per artikel een map:', '',
              '  1.jpg, 2.jpg    de beelden, 1080x1350, in deze volgorde',
              '                  plaatsen. 4:5 is de hoogste verhouding die',
              '                  Instagram nog volledig toont.',
              '  bijschrift.txt  alles selecteren en in het bijschrift plakken',
              '  hashtags.txt    als eerste reactie, of achter het bijschrift',
              '  alt-tekst.txt   per foto een regel. Staat bij het plaatsen',
              '                  onder Geavanceerde instellingen.', '']

    with zipfile.ZipFile(doel, 'w', zipfile.ZIP_DEFLATED) as z:
        # De openingspost heeft geen productbeeld; Bram zet daar het logo neer.
        # Vandaar map 00 en alleen tekst.
        z.writestr('00 Openingspost/bijschrift.txt',
                   teksten.openingspost(alles) + '\n')
        z.writestr('00 Openingspost/hashtags.txt',
                   ' '.join(teksten.openingstags()) + '\n')
        z.writestr('00 Openingspost/alt-tekst.txt',
                   'Het logo van Brams Collectibles: een ronde gouden zegel met '
                   'de naam in wit schrift op een donkerblauwe achtergrond, met '
                   'een ster en het jaartal 2026.\n')
        z.writestr('00 Openingspost/LEES-MIJ.txt',
                   'Deze post gaat als eerste. Het beeld is het logo; dat zet je\n'
                   'er zelf bij. Daarna pas de productposts, in de volgorde van\n'
                   'de mappen hierna.\n')
        regels.append(' 0. Openingspost — het logo als beeld')

        for nr, r in enumerate(klaar, 1):
            sku, map_ = r['sku'], f'{nr:02d} {mapnaam(r)}'
            beelden = [BEELD / f'{sku}.png']
            beelden += sorted(BEELD.glob(f'{sku}-*.png'),
                              key=lambda p: int(p.stem.rsplit('-', 1)[1]))
            for i, b in enumerate(beelden, 1):
                z.writestr(f'{map_}/{i}.jpg', jpeg(b))

            z.writestr(f'{map_}/bijschrift.txt',
                       teksten.instagram(r, alles) + '\n')
            z.writestr(f'{map_}/hashtags.txt',
                       ' '.join(teksten.hashtags(r)) + '\n')
            z.writestr(f'{map_}/alt-tekst.txt', '\n'.join(
                [f'Foto {i}: {teksten.alttekst(r)}'
                 for i in range(1, len(beelden) + 1)]) + '\n')

            foto = f'{len(beelden)} foto' + ('' if len(beelden) == 1 else "'s")
            regels.append(f'{nr:2d}. {r["naam"]} — {r["aantal"]} op voorraad — {foto}')

        zonder = [r for r in alles if r['aantal'] and r not in klaar]
        if zonder:
            regels += ['', 'Nog geen beeld:']
            regels += [f'  - {r["naam"]}' for r in zonder]
        z.writestr('LEES-MIJ.txt', '\n'.join(regels) + '\n')

    lijst(klaar, alles)
    print(f'{doel.relative_to(BASIS.parent)}  '
          f'{doel.stat().st_size // 1024 // 1024} MB  {len(klaar)} posts')


if __name__ == '__main__':
    main()

"""Metatitels en metaomschrijvingen voor producten en collecties.

Wat Google en de AI-zoekmachines in de zoekresultaten tonen. Shopify vult
zonder deze velden zelf iets in: de producttitel, en de eerste regels van de
beschrijving. Dat werkt, maar dan begint elke omschrijving met dezelfde
setintroductie en staat de prijs er nooit in.

De titel krijgt van het thema al " - Brams Collectibles" achteraan
(theme.liquid regel 22), dus die hoort hier niet in.

Bron is register.csv. Draaien: python3 sjablonen/meta.py
"""
import csv
import json
import pathlib
import re
import sys

HIER = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(HIER))
from teksten import bedrag, hoogtepunten, pokemon_center  # noqa: E402

UIT = HIER / 'teksten' / 'uit'

# Hoe een soort in lopende tekst heet. Het register schrijft ETB.
VOLUIT = {
    'ETB': 'Elite Trainer Box',
    'Booster Box': 'Booster Box',
    'Booster Bundle': 'Booster Bundle',
    'Premium Collection': 'Premium Collection',
    'Display': 'Display',
    'Case': 'Case',
}


def tel(r, wat):
    """Een aantal uit de hoogtepunten halen, bijvoorbeeld "booster packs".

    De eerste regel is bij elk artikel de telling, gelezen van het
    achterpaneel, maar niet altijd in dezelfde vorm: naast "15 booster packs"
    staat er ook "9 Mega Evolution - Chaos Rising booster packs" en bij een
    display "10 booster bundles, in totaal 60 booster packs". Het getal dat
    telt is dat vlak voor de woorden zelf, dus we nemen de laatste treffer."""
    tekst = ' | '.join(hoogtepunten(r))
    treffers = re.findall(rf'(\d+)(?:\s+[^\d|]+?)?\s*{wat}', tekst, re.I)
    return int(treffers[-1]) if treffers else None


def metatitel(r):
    """Wat er in het tabblad en in de zoekresultaten boven staat.

    De volledige productnaam plus "kopen". Dat is lang, en Google kort de
    staart af, maar de staart is de winkelnaam die het thema er toch al
    aanplakt. Wat een zoeker intikt staat vooraan."""
    return f'{r["naam"]} kopen'


def inhoudsregel(r):
    """Een zin over wat er in de doos zit, per soort anders.

    De vorm van elke soort ligt vast — een Elite Trainer Box heeft altijd
    sleeves, energiekaarten en een promo, een display is altijd bundels in een
    carton — dus dit is geen gok maar de vorm van het product. Alleen het
    aantal komt per artikel uit het register."""
    p = tel(r, 'booster packs?')
    if r['soort'] == 'Display':
        b = tel(r, 'booster bundles?')
        if b and p:
            return f'{b} bundels, samen {p} packs, in een verzegelde carton.'
        return 'Verzegeld display, zoals het de fabriek verliet.'
    if r['soort'] == 'Case':
        return 'Een volledige verzegelde carton van de distributeur.'
    if not p:
        return ''
    if r['soort'] == 'ETB' and pokemon_center(r):
        return f'{p} packs en extra promo\'s, de Pokémon Center-uitgave.'
    if r['soort'] == 'ETB':
        return f'{p} packs, sleeves, energiekaarten en een promokaart.'
    if r['soort'] == 'Booster Box':
        return f'{p} packs met de originele fabrieksfolie eromheen.'
    if r['soort'] == 'Booster Bundle':
        return f'{p} packs in één verzegelde bundel.'
    if r['soort'] == 'Premium Collection':
        return f'{p} packs plus de promokaarten die alleen in deze box zitten.'
    return f'{p} packs.'


def metatekst(r):
    """Circa 150 tekens: wat het is, wat erin zit, wat het kost.

    Google kapt rond de 155 tekens af, dus het belangrijkste eerst. De prijs
    staat erin omdat dat in een zoekresultaat het verschil maakt tussen wel en
    niet klikken, zeker naast marktplaatsen die hem niet tonen. Geen "op
    voorraad": een metaomschrijving blijft staan, de voorraad niet.

    Bij de lange productnamen — de Pokémon Center-uitgaven eten er zestig
    tekens aan op — past het volledige zinnetje er niet meer bij. Dan valt
    eerst "verzekerd verzonden" weg en daarna de acryl hoes, want die staan
    ook op de productpagina zelf."""
    naam = f'Sealed {r["naam"]}.'
    inhoud = inhoudsregel(r)
    hoes = 'In acryl beschermhoes.' if r['hoes'] == 'ja' else ''
    prijs = f'€ {bedrag(r["prijs"])}.' if r['prijs'] else ''
    staart = 'Verzekerd verzonden.'

    for weglaten in ([], ['staart'], ['staart', 'hoes']):
        delen = [naam, inhoud,
                 '' if 'hoes' in weglaten else hoes,
                 prijs,
                 '' if 'staart' in weglaten else staart]
        tekst = ' '.join(d for d in delen if d)
        if len(tekst) <= 155:
            return tekst
    return tekst


# Collecties staan niet in het register. Titel is wat iemand intikt; de
# omschrijving vult aan wat er op de pagina zelf al staat, niet herhaalt.
COLLECTIES = {
    'elite-trainer-boxes': (
        'Pokémon Elite Trainer Boxes kopen',
        'Sealed Elite Trainer Boxen uit Prismatic Evolutions, Chaos Rising, '
        'Pitch Black, Destined Rivals en Ascended Heroes, inclusief de Pokémon '
        'Center-uitgaven.'),
    'booster-bundles': (
        'Pokémon Booster Bundles kopen',
        'Sealed booster bundles: zes packs in één verzegelde bundel. De '
        'goedkoopste manier om een nieuwe set te proberen. Op voorraad en '
        'verzekerd verzonden.'),
    'booster-boxes': (
        'Pokémon Booster Boxes kopen',
        'Sealed booster boxes met zesendertig packs en de originele '
        'fabrieksfolie. Voor wie een set compleet wil trekken of wil '
        'wegleggen. Verzekerd verzonden.'),
    'premium-collections': (
        'Pokémon Premium Collections kopen',
        'Sealed premium collections rond één Pokémon, met promokaarten die '
        'alleen in die box zitten. Mega Greninja ex en Prismatic Evolutions '
        'op voorraad.'),
    'displays': (
        'Pokémon displays kopen',
        'Verzegelde displays: tien booster bundles in één carton, ongeopend. '
        'Scarlet & Violet 151 en Ascended Heroes op voorraad. Verzekerd '
        'verzonden.'),
    'cases': (
        'Pokémon cases kopen',
        'Volledige verzegelde cartons zoals ze van de distributeur komen, met '
        'de fabrieksverzegeling er nog omheen. Voor wie in het groot '
        'wegzet.'),
    'chaos-rising': (
        'Pokémon Chaos Rising sealed kopen',
        'Sealed Chaos Rising: Elite Trainer Box, Pokémon Center ETB, booster '
        'box en booster bundle. De Mega Evolution-serie met Mega Greninja ex '
        'als hoofdkaart.'),
    'prismatic-evolutions': (
        'Pokémon Prismatic Evolutions sealed kopen',
        'Sealed Prismatic Evolutions: de Pokémon Center Elite Trainer Box en '
        'de Super Premium Collection. De set rond Eevee en zijn evoluties, al '
        'lang uitverkocht.'),
    'scarlet-violet-151': (
        'Pokémon Scarlet & Violet 151 sealed kopen',
        'Sealed Scarlet & Violet 151: het booster bundle display met tien '
        'bundels. De set die de eerste 151 Pokémon terugbrengt, van Bulbasaur '
        'tot Mew.'),
    'pitch-black': (
        'Pokémon Pitch Black sealed kopen',
        'Sealed Pitch Black: de Elite Trainer Box en de Pokémon '
        'Center-uitgave. De donkere kant van de Mega Evolution-serie, met '
        'Zarude als promo.'),
    'destined-rivals': (
        'Pokémon Destined Rivals sealed kopen',
        'Sealed Destined Rivals Elite Trainer Box. Team Rocket tegen de '
        'helden van Kanto en Johto, met Mewtwo en Ho-Oh in de hoofdrol en '
        'Giovanni op de doos.'),
    'paldean-fates': (
        'Pokémon Paldean Fates sealed kopen',
        'Sealed Paldean Fates: een volledige verzegelde case met tien Elite '
        'Trainer Boxen. De set van de Bubble Mew, de shiny rares en gunstige '
        'pull rates.'),
    'ascended-heroes': (
        'Pokémon Ascended Heroes sealed kopen',
        'Sealed Ascended Heroes: Pokémon Center Elite Trainer Box, booster '
        'bundle en display. Mega Attack Rares, een gouden Charizard en de '
        'kans op een God Pack.'),
    'alle-dozen': (
        'Alle sealed Pokémon-dozen',
        'Het volledige assortiment verzegelde Pokémon-dozen dat nu op de '
        'plank ligt, van Elite Trainer Box tot complete case. Verzekerd '
        'verzonden met PostNL.'),
}


# De gidsartikelen. Shopify heeft voor een artikel geen seo-veld zoals bij een
# product; daar gaat het via de metavelden global.title_tag en
# global.description_tag. De omschrijving begint met het antwoord zelf, want
# dat is wat een AI-zoekmachine overneemt als samenvatting.
ARTIKELEN = {
    'wat-is-een-elite-trainer-box': (
        'Wat is een Elite Trainer Box?',
        'Een Elite Trainer Box bevat negen packs, een promokaart, 65 '
        'sleeves, energiekaarten en een verzameldoos. De Pokémon '
        'Center-uitvoering heeft elf packs.'),
    'pokemon-center-uitgaven': (
        'Wat maakt een Pokémon Center-uitgave anders?',
        'Pokémon Center-dozen verschijnen alleen via de officiële kanalen, in '
        'een vaste oplage, met meer packs en een extra promokaart. Ze worden '
        'niet herdrukt.'),
    'booster-bundle-booster-box-of-elite-trainer-box': (
        'Booster bundle, booster box of Elite Trainer Box?',
        'Een booster bundle heeft zes packs, een booster box 36 en een Elite '
        'Trainer Box negen plus sleeves en een promo. Per pack is de box het '
        'voordeligst.'),
    'verzegelde-pokemon-dozen-bewaren': (
        'Verzegelde Pokémon-dozen bewaren',
        'Bewaar verzegelde dozen rechtop, donker, bij 15 tot 22 graden en '
        'onder 55 procent luchtvochtigheid. Een acryl hoes voorkomt deuken en '
        'houdt de folie strak.'),
    'is-verzegelde-pokemon-tcg-een-goede-investering': (
        'Is verzegelde Pokémon TCG een goede investering?',
        'Verzegeld materiaal uit sets die uit productie zijn steeg historisch in '
        'waarde, maar het is geen spaarrekening. Oplage, folie en geduld '
        'bepalen het.'),
}

# De startpagina. Deze twee zijn niet via de Admin API te zetten — Shopify
# bewaart ze onder Onlinewinkel > Voorkeuren — dus ze staan als terugval in
# theme.liquid. Hier voor de volledigheid, zodat alle metateksten op één plek
# staan en je ze kunt vergelijken.
STARTPAGINA = (
    'Sealed Pokémon TCG kopen',
    'Sealed Pokémon TCG: Elite Trainer Boxen, Pokémon Center-uitgaven, '
    'booster boxes, displays en complete cases. Fabrieksverzegeld en '
    'verzekerd verzonden.')


def main():
    alles = list(csv.DictReader(open(HIER / 'register.csv', encoding='utf-8')))
    producten = {r['sku']: {'titel': metatitel(r), 'tekst': metatekst(r)}
                 for r in alles if r['aantal'] and r['prijs']}
    collecties = {h: {'titel': t, 'tekst': o} for h, (t, o) in COLLECTIES.items()}
    artikelen = {h: {'titel': t, 'tekst': o} for h, (t, o) in ARTIKELEN.items()}
    start = {'titel': STARTPAGINA[0], 'tekst': STARTPAGINA[1]}

    UIT.mkdir(parents=True, exist_ok=True)
    doel = UIT / '_meta.json'
    doel.write_text(json.dumps({'startpagina': start, 'producten': producten,
                                'collecties': collecties, 'artikelen': artikelen},
                               ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for groep, items in (('start', {'startpagina': start}), ('product', producten),
                         ('collectie', collecties), ('artikel', artikelen)):
        for sleutel, m in items.items():
            print(f'{groep:9} {sleutel:14} titel {len(m["titel"]):>3}  tekst {len(m["tekst"]):>3}')
            print(f'{"":9} {"":14} {m["tekst"]}')
    te_lang = [(g, k) for g, items in (('product', producten), ('collectie', collecties),
                                      ('artikel', artikelen), ('start', {'startpagina': start}))
               for k, m in items.items() if len(m['tekst']) > 155]
    if te_lang:
        raise SystemExit(f'Te lang voor Google (boven 155 tekens): {te_lang}')
    print(f'\n-> {doel.relative_to(HIER)}')


if __name__ == '__main__':
    main()

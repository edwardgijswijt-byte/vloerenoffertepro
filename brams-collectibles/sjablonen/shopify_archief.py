#!/usr/bin/env python3
"""Een volledig archief van de Shopify-winkel maken, zodat die opnieuw op te bouwen is.

    /usr/bin/python3 shopify_archief.py <map-met-uitgepakte-zips>

Gemaakt op 26 oktober 2026, toen Bram besloot de winkel voorlopig niet te
openen. Alles wat alleen in Shopify stond staat nu in `archief/shopify-2026-10-26/`:

    producten.json         per product: alles wat productSet nodig heeft, inclusief
                           de volledige beschrijving (HTML) en de foto's op volgorde
    afbeeldingen/          de foto's zoals ze in de winkel stonden, per sku
    ongebruikt/            aangeleverde beelden die niet in de winkel zijn gekomen
    collecties.json        de veertien collecties met regels, tekst en sortering
    menu.json              hoofdmenu
    verzending.json        verzendzones en tarieven
    winkel.json            instellingen van de winkel zelf
    HERSTEL.md             in welke volgorde je alles terugzet

De bron voor productteksten blijft register.csv met teksten.py; dit archief is
de stand van de winkel op die dag, en hoeft niet altijd gelijk te zijn aan wat het
register nu oplevert. De Shopify-beschrijving is hier gegenereerd uit het
register en niet uit Shopify gelezen: dat is wat er gepubliceerd is, want zo zijn
alle producten gemaakt.

Het CDN van Shopify is vanuit de werkomgeving niet bereikbaar, dus de foto's komen
uit de bestanden waarmee ze zijn geüpload en niet uit Shopify. Drie ervan
(Paldean Fates-case, de zijkant van de gewone Pitch Black ETB) zijn
opnieuw gemaakt met productbeeld.py uit dezelfde opnames.
"""
import csv
import json
import pathlib
import shutil
import sys

HIER = pathlib.Path(__file__).parent
WORTEL = HIER.parent
sys.path.insert(0, str(WORTEL))
import teksten  # noqa: E402

DOEL = WORTEL / 'archief' / 'shopify-2026-10-26'

# sku -> [(bronbestand, alt-tekst), ...] in de volgorde van de winkel.
# Bron is relatief aan de map met uitgepakte zips: prod/ eerste zip, prod2/ tweede,
# prod3 AH-bundel, prod4 sjabloon-zip, prod5 de 30th-producten. "export:" wijst
# naar sjablonen/export/webshop.
SCRATCH_WIJZIGINGEN = {}

FOTOS = {
    'BC-PE-PCETB': [('prod4/5.png', 'Prismatic Evolutions Pokémon Center Elite Trainer Box, voorkant'),
                    ('prod4/6.png', 'Prismatic Evolutions Pokémon Center Elite Trainer Box, achterkant')],
    'BC-CR-ETB': [('prod2/13.png', 'Chaos Rising Elite Trainer Box, voorkant'),
                  ('prod2/14.png', 'Chaos Rising Elite Trainer Box, achterkant')],
    'BC-CR-BND': [('prod2/11.png', 'Chaos Rising Booster Bundle, voorkant'),
                  ('prod2/12.png', 'Chaos Rising Booster Bundle, achterkant')],
    'BC-MEV-GREN': [('prod2/17.png', 'Mega Greninja ex Premium Collection, voorkant'),
                    ('prod2/18.png', 'Mega Greninja ex Premium Collection, achterkant')],
    'BC-151-BNDD': [('prod4/1.png', 'Pokémon TCG Scarlet & Violet 151 Booster Bundle Display, voorkant'),
                    ('prod4/2.png', 'Pokémon TCG Scarlet & Violet 151 Booster Bundle Display, liggend')],
    'BC-CR-BBX': [('prod2/9.png', 'Chaos Rising Booster Box, voorkant'),
                  ('prod2/10.png', 'Chaos Rising Booster Box, achterkant')],
    'BC-PB-PCETB': [('prod/23.png', 'Pitch Black Pokémon Center Elite Trainer Box, voorkant'),
                    ('prod/24.png', 'Pitch Black Pokémon Center Elite Trainer Box, achterkant met inhoud')],
    'BC-DR-ETB': [('prod2/19.png', 'Destined Rivals Elite Trainer Box, voorkant'),
                  ('prod2/20.png', 'Destined Rivals Elite Trainer Box, achterkant')],
    'BC-PAF-CASE': [('export:BC-PAF-CASE-1.png', 'Paldean Fates Elite Trainer Box Case, verzegelde carton met etiket SV4.5 Elite Trainer Box, 10 per carton'),
                    ('export:BC-PAF-CASE-2.png', 'Paldean Fates Elite Trainer Box Case, voorzijde met ongebroken fabrieksverzegeling')],
    'BC-AH-BND': [('prod3/27.png', 'Ascended Heroes Booster Bundle, voorkant'),
                  ('prod3/28.png', 'Ascended Heroes Booster Bundle, achterkant')],
    'BC-AH-BNDD': [('prod4/3.png', 'Ascended Heroes Booster Bundle Display, voorkant'),
                   ('prod4/4.png', 'Ascended Heroes Booster Bundle Display, liggend')],
    'BC-PE-SPC': [('prod/25.png', 'Prismatic Evolutions Super Premium Collection, voorkant met Eevee'),
                  ('prod/26.png', 'Prismatic Evolutions Super Premium Collection, achterkant met inhoud')],
    'BC-CR-PCETB': [('prod2/15.png', 'Chaos Rising Pokémon Center Elite Trainer Box, voorkant'),
                    ('prod2/16.png', 'Chaos Rising Pokémon Center Elite Trainer Box, achterkant')],
    # De gewone Pitch Black ETB: in de winkel stonden bij het archiveren twee foto's
    # (23.png en 24.png) die de Pokémon Center-uitvoering tonen, en de zijkant. De
    # eerste twee horen bij BC-PB-PCETB. Hier staat wat er hoort te staan.
    'BC-PB-ETB': [('export:BC-PB-ETB-2.png', 'Zijkant')],
    'BC-AH-PCETB': [('prod4/7.png', 'Ascended Heroes Pokémon Center Elite Trainer Box, voorkant'),
                    ('prod4/8.png', 'Ascended Heroes Pokémon Center Elite Trainer Box, achterkant')],
    'BC-30-BINDER': [('prod5/49.png', 'Pokémon TCG 30th Anniversary Binder Collection, voorkant')],
    'BC-30-ETB': [('prod5/51.png', 'Pokémon TCG 30th Anniversary Elite Trainer Box, voorkant')],
    'BC-30-PCETB': [('prod5/53.png', 'Pokémon TCG 30th Anniversary Elite Trainer Box Pokémon Center, voorkant')],
    'BC-30-GREN': [('prod5/54.png', 'Pokémon TCG 30th Anniversary Greninja ex Box, voorkant')],
    'BC-30-POSTER': [('prod5/55.png', 'Pokémon TCG 30th Anniversary Poster Collection, voorkant')],
    'BC-30-SYLV': [('prod5/56.png', 'Pokémon TCG 30th Anniversary Sylveon ex Box, voorkant')],
    'BC-30-UPC': [('prod5/59.png', 'Pokémon TCG 30th Anniversary Ultra Premium Collection, Day- en Night-variant naast elkaar'),
                  ('prod5/57.png', 'Pokémon TCG 30th Anniversary Ultra Premium Collection, Day-variant'),
                  ('prod5/58.png', 'Pokémon TCG 30th Anniversary Ultra Premium Collection, Night-variant')],
    'BC-30-UPC-CASE': [('prod5/60.png', 'Pokémon TCG 30th Anniversary Ultra Premium Collection Case, carton met 2 Day- en 2 Night-dozen')],
    'BC-PE-ETB': [('prod5/61.png', 'Prismatic Evolutions Elite Trainer Box, voorkant'),
                  ('prod5/62.png', 'Prismatic Evolutions Elite Trainer Box, achterkant met inhoud')],
}

# Niet in de winkel gekomen, maar bewaren waard.
ONGEBRUIKT = {
    'prod5/50.png': '30th-etb-franse-doos.png',
    'prod5/52.png': '30th-etb-case-10-stuks.png',
    'prod2/21.png': 'first-partner-serie-1-case.png',
    'prod2/22.png': 'distributeursbeeld-niet-gebruiken.png',
    'prod2/23.png': 'leeg-podium-1.png',
    'prod2/24.png': 'leeg-podium-2.png',
    'prod2/25.png': 'leeg-podium-3.png',
    'prod2/26.png': 'leeg-podium-4.png',
    'prod2/27.png': 'leeg-podium-5.png',
    'prod3/27.png': None,
    'prod4/9.png': 'leeg-podium-6.png',
}

# Wat in Shopify stond en niet uit het register volgt: handle, tags en de
# zoekmachinevelden. Uit de Admin API gelezen op 26 oktober 2026.
STAND = {
    'BC-PE-PCETB': ('prismatic-evolutions-pokemon-center-elite-trainer-box', ['eevee', 'etb', 'pokemon center', 'prismatic evolutions', 'scarlet & violet', 'sealed'],
                    'Prismatic Evolutions Pokémon Center Elite Trainer Box kopen',
                    "Sealed Prismatic Evolutions Pokémon Center Elite Trainer Box. 11 packs en extra promo's, de Pokémon Center-uitgave. In acryl beschermhoes. € 599,-."),
    'BC-CR-ETB': ('chaos-rising-elite-trainer-box', ['chaos rising', 'etb', 'greninja', 'mega evolution', 'sealed'],
                  'Chaos Rising Elite Trainer Box kopen',
                  'Sealed Chaos Rising Elite Trainer Box. 9 packs, sleeves, energiekaarten en een promokaart. € 64,95. Verzekerd verzonden.'),
    'BC-CR-BND': ('chaos-rising-booster-bundle', ['booster bundle', 'chaos rising', 'mega evolution', 'sealed'],
                  'Chaos Rising Booster Bundle kopen',
                  'Sealed Chaos Rising Booster Bundle. 6 packs in één verzegelde bundel. € 34,95. Verzekerd verzonden.'),
    'BC-MEV-GREN': ('mega-greninja-ex-premium-collection', ['chaos rising', 'greninja', 'mega evolution', 'premium collection', 'sealed'],
                    'Mega Greninja ex Premium Collection kopen',
                    'Sealed Mega Greninja ex Premium Collection. 8 packs plus de promokaarten die alleen in deze box zitten. € 49,95. Verzekerd verzonden.'),
    'BC-151-BNDD': ('scarlet-violet-151-booster-bundle-display', ['151', 'booster bundle', 'display', 'mew', 'scarlet & violet', 'sealed'],
                    'Pokémon TCG Scarlet & Violet 151 Booster Bundle Display kopen',
                    'Sealed Pokémon TCG Scarlet & Violet 151 Booster Bundle Display. 10 bundels, samen 60 packs, in een verzegelde carton. € 1.740,-. Verzekerd verzonden.'),
    'BC-CR-BBX': ('chaos-rising-booster-box', ['booster box', 'chaos rising', 'greninja', 'mega evolution', 'sealed'],
                  'Chaos Rising Booster Box kopen',
                  'Sealed Chaos Rising Booster Box. 36 packs met de originele fabrieksfolie eromheen. € 194,95. Verzekerd verzonden.'),
    'BC-PB-PCETB': ('pitch-black-pokemon-center-elite-trainer-box', ['etb', 'mega evolution', 'pitch black', 'pokemon center', 'sealed', 'zarude'],
                    'Pitch Black Pokémon Center Elite Trainer Box kopen',
                    "Sealed Pitch Black Pokémon Center Elite Trainer Box. 11 packs en extra promo's, de Pokémon Center-uitgave. € 170,-. Verzekerd verzonden."),
    'BC-DR-ETB': ('destined-rivals-elite-trainer-box', ['destined rivals', 'etb', 'mewtwo', 'scarlet & violet', 'sealed', 'team rocket'],
                  'Destined Rivals Elite Trainer Box kopen',
                  'Sealed Destined Rivals Elite Trainer Box. 9 packs, sleeves, energiekaarten en een promokaart. € 119,95. Verzekerd verzonden.'),
    'BC-PAF-CASE': ('paldean-fates-elite-trainer-box-case', ['paldean fates', 'pokemon tcg', 'sealed'],
                    'Paldean Fates Elite Trainer Box Case kopen',
                    'Sealed Paldean Fates Elite Trainer Box Case. Een volledige verzegelde carton van de distributeur. € 3.999,-. Verzekerd verzonden.'),
    'BC-AH-BND': ('ascended-heroes-booster-bundle', ['ascended heroes', 'pokemon tcg', 'sealed'],
                  'Ascended Heroes Booster Bundle kopen',
                  'Sealed Ascended Heroes Booster Bundle. 6 packs in één verzegelde bundel. € 89,95. Verzekerd verzonden.'),
    'BC-AH-BNDD': ('ascended-heroes-booster-bundle-display', ['ascended heroes', 'pokemon tcg', 'sealed'],
                   'Ascended Heroes Booster Bundle Display kopen',
                   'Sealed Ascended Heroes Booster Bundle Display. 10 bundels, samen 60 packs, in een verzegelde carton. € 1.140,-. Verzekerd verzonden.'),
    'BC-PE-SPC': ('prismatic-evolutions-super-premium-collection', ['pokemon tcg', 'prismatic evolutions', 'sealed'],
                  'Prismatic Evolutions Super Premium Collection kopen',
                  'Sealed Prismatic Evolutions Super Premium Collection. 15 packs plus de promokaarten die alleen in deze box zitten. € 269,95. Verzekerd verzonden.'),
    'BC-CR-PCETB': ('chaos-rising-pokemon-center-elite-trainer-box', ['chaos rising', 'pokemon tcg', 'sealed'],
                    'Chaos Rising Pokémon Center Elite Trainer Box kopen',
                    "Sealed Chaos Rising Pokémon Center Elite Trainer Box. 11 packs en extra promo's, de Pokémon Center-uitgave. € 155,-. Verzekerd verzonden."),
    'BC-PB-ETB': ('pitch-black-elite-trainer-box', ['pitch black', 'pokemon tcg', 'sealed'],
                  'Pitch Black Elite Trainer Box kopen',
                  'Sealed Pitch Black Elite Trainer Box. 9 packs, sleeves, energiekaarten en een promokaart. € 65,-. Verzekerd verzonden.'),
    'BC-AH-PCETB': ('ascended-heroes-pokemon-center-elite-trainer-box', ['ascended heroes', 'pokemon tcg', 'sealed'],
                    'Ascended Heroes Pokémon Center Elite Trainer Box kopen',
                    "Sealed Ascended Heroes Pokémon Center Elite Trainer Box. 11 packs en extra promo's, de Pokémon Center-uitgave. In acryl beschermhoes. € 525,-."),
    'BC-30-BINDER': ('pokemon-tcg-30th-anniversary-binder-collection', ['30th celebration', 'pokemon tcg', 'sealed'],
                     '30th Anniversary Binder Collection kopen',
                     'Sealed 30th Anniversary Binder Collection met 5 boosterpacks en een exclusieve 9-pocket binder. € 75,-. Verzenden of ophalen.'),
    'BC-30-ETB': ('pokemon-tcg-30th-anniversary-elite-trainer-box', ['30th celebration', 'pokemon tcg', 'pre-order', 'sealed'],
                  '30th Anniversary Elite Trainer Box kopen',
                  'Sealed 30th Anniversary Elite Trainer Box met 9 boosterpacks en een full-art foil promo van Nidorina. € 139,95. Pre-order.'),
    'BC-30-PCETB': ('pokemon-tcg-30th-anniversary-elite-trainer-box-pokemon-center', ['30th celebration', 'pokemon tcg', 'pre-order', 'sealed'],
                    '30th Anniversary Pokémon Center Elite Trainer Box kopen',
                    "Sealed 30th Anniversary Pokémon Center Elite Trainer Box met 11 boosterpacks en twee Nidorina-promo's. € 425,-. Pre-order."),
    'BC-30-GREN': ('pokemon-tcg-30th-anniversary-greninja-ex-box', ['30th celebration', 'pokemon tcg', 'sealed'],
                   '30th Anniversary Greninja ex Box kopen',
                   "Sealed 30th Anniversary Greninja ex Box met 4 boosterpacks en twee Greninja ex-promo's. € 59,95. Verzenden of ophalen."),
    'BC-30-POSTER': ('pokemon-tcg-30th-anniversary-poster-collection', ['30th celebration', 'pokemon tcg', 'sealed'],
                     '30th Anniversary Poster Collection kopen',
                     "Sealed 30th Anniversary Poster Collection met 3 boosterpacks, 3 promo's van de Kanto-vogels en een poster. € 55,-."),
    'BC-30-SYLV': ('pokemon-tcg-30th-anniversary-sylveon-ex-box', ['30th celebration', 'pokemon tcg', 'sealed'],
                   '30th Anniversary Sylveon ex Box kopen',
                   "Sealed 30th Anniversary Sylveon ex Box met 4 boosterpacks en twee Sylveon ex-promo's. € 59,95. Verzenden of ophalen."),
    'BC-30-UPC': ('pokemon-tcg-30th-anniversary-ultra-premium-collection', ['30th celebration', 'pokemon tcg', 'pre-order', 'sealed'],
                  '30th Anniversary Ultra Premium Collection kopen',
                  "Sealed 30th Anniversary Ultra Premium Collection, Day of Night. 29 boosterpacks en twee promo's. € 424,95. Pre-order."),
    'BC-30-UPC-CASE': ('pokemon-tcg-30th-anniversary-ultra-premium-collection-case', ['30th celebration', 'pokemon tcg', 'pre-order', 'sealed'],
                       '30th Anniversary Ultra Premium Collection Case kopen',
                       'Sealed case met 2 Day en 2 Night Ultra Premium Collection van 30th Anniversary. € 1.700,-. Pre-order.'),
    'BC-PE-ETB': ('prismatic-evolutions-elite-trainer-box', ['pokemon tcg', 'prismatic evolutions', 'sealed'],
                  'Prismatic Evolutions Elite Trainer Box kopen',
                  'Sealed Prismatic Evolutions Elite Trainer Box met 9 boosterpacks en een full-art foil promo van Eevee. € 159,95. Verzenden of ophalen.'),
}

# Producten die in de winkel stonden maar niet op de normale manier uit het
# register komen: de soort die Shopify als producttype kreeg.
TYPE = {'ETB': 'Elite Trainer Box'}

COLLECTIES = [
    ('frontpage', 'Uitgelicht', '<p>Een greep uit wat er nu op de plank ligt.</p>', 'MANUAL', None, 'Handmatig; de producten staan in producten van de carrousel op de startpagina.'),
    ('elite-trainer-boxes', 'Elite Trainer Boxes', '<p>Sealed Elite Trainer Boxes. Negen tot elf packs, sleeves, energiekaarten, dobbelstenen en een promo die je nergens los koopt. Alles ligt hier op de plank.</p>', 'PRICE_DESC', ('TYPE', 'Elite Trainer Box'), ''),
    ('booster-bundles', 'Booster Bundles', '<p>Zes packs in een sealed bundel. De makkelijkste manier om een set te proberen zonder meteen een hele booster box te kopen.</p>', 'PRICE_DESC', ('TYPE', 'Booster Bundle'), ''),
    ('booster-boxes', 'Booster Boxes', '<p>Zesendertig packs, sealed en met de originele fabrieksfolie. Voor wie een set compleet wil trekken of wil bewaren.</p>', 'PRICE_DESC', ('TYPE', 'Booster Box'), ''),
    ('premium-collections', 'Premium Collections', '<p>Boxen rond één Pokémon. Packs plus promokaarten die alleen in die box zitten — vaak een oversize of lenticulaire kaart.</p>', 'PRICE_DESC', ('TYPE', 'Premium Collection'), ''),
    ('chaos-rising', 'Chaos Rising', '<p>De Mega Evolution-serie. Chaos Rising brengt Mega Greninja ex als hoofdkaart, met Fennekin als promo in de Elite Trainer Box.</p>', 'PRICE_DESC', ('TAG', 'chaos rising'), ''),
    ('prismatic-evolutions', 'Prismatic Evolutions', '<p>De set rond Eevee en zijn evoluties. Gewild en al een tijd uitverkocht bij Pokémon Center — wat er nog is, is wat er nog is.</p>', 'PRICE_DESC', ('TAG', 'prismatic evolutions'), ''),
    ('scarlet-violet-151', 'Scarlet & Violet 151', '<p>De set die de eerste 151 Pokémon terugbrengt, van Bulbasaur tot Mew. Blijft gevraagd, ook jaren na verschijnen.</p>', 'PRICE_DESC', ('TAG', '151'), ''),
    ('displays', 'Displays', '<p>Verzegelde displays: tien booster bundles in één doos, nog zoals ze de fabriek verlieten. Voor wie een set in één keer binnenhaalt of wil wegleggen.</p>', 'PRICE_DESC', ('TYPE', 'Display'), ''),
    ('pitch-black', 'Pitch Black', '<p>De donkere kant van de Mega Evolution-serie. Mega Darkrai, Mega Zeraora ex, Mega Chandelure ex en Mega Excadrill ex, met Zarude als promo in de Elite Trainer Box.</p>', 'PRICE_DESC', ('TAG', 'pitch black'), ''),
    ('destined-rivals', 'Destined Rivals', '<p>Team Rocket tegen de helden van Kanto en Johto. Mewtwo en Ho-Oh in de hoofdrol, met Giovanni op de doos.</p>', 'PRICE_DESC', ('TAG', 'destined rivals'), ''),
    ('cases', 'Cases', '<p>Een volledige verzegelde carton, zoals hij van de distributeur komt. Ongeopend, met de fabrieksverzegeling er nog omheen.</p>', 'PRICE_DESC', ('TYPE', 'Case'), ''),
    ('paldean-fates', 'Paldean Fates', None, 'PRICE_DESC', ('TAG', 'paldean fates'), 'Tekst staat in teksten/sets/paldean-fates.md.'),
    ('ascended-heroes', 'Ascended Heroes', None, 'PRICE_DESC', ('TAG', 'ascended heroes'), 'Tekst staat in teksten/sets/ascended-heroes.md.'),
    ('alle-dozen', 'Alle dozen', '<p>Alle verzegelde Pokémon-dozen die nu op voorraad zijn, van Elite Trainer Box tot complete case.</p>', 'PRICE_DESC', ('VENDOR', 'Brams Collectibles'), ''),
    ('30th-celebration', '30th Celebration', '<p>De 30th Celebration-producten: Elite Trainer Boxen, ex Boxen, Binder en Poster Collection, Ultra Premium Collection en cases.</p>', 'MOST_RELEVANT', ('TAG', '30th celebration'), 'Collectiebeeld: afbeeldingen/BC-30-ETB-1.png.'),
]

FRONTPAGE_VOLGORDE = ['BC-30-UPC', 'BC-30-PCETB', 'BC-PE-PCETB', 'BC-PE-SPC', 'BC-30-GREN', 'BC-AH-PCETB', 'BC-30-ETB', 'BC-DR-ETB']


def bron(scratch, pad):
    if pad.startswith('export:'):
        return HIER / 'export' / 'webshop' / pad[len('export:'):]
    return scratch / pad


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    scratch = pathlib.Path(sys.argv[1])
    DOEL.mkdir(parents=True, exist_ok=True)
    (DOEL / 'afbeeldingen').mkdir(exist_ok=True)
    (DOEL / 'ongebruikt').mkdir(exist_ok=True)
    register = {r['sku']: r for r in csv.DictReader(open(WORTEL / 'register.csv', encoding='utf-8'))}
    alles = list(register.values())

    producten, ontbreekt = [], []
    for sku, (handle, tags, seo_titel, seo_tekst) in STAND.items():
        r = register[sku]
        fotos = []
        for n, (pad, alt) in enumerate(FOTOS[sku], 1):
            src = bron(scratch, pad)
            if not src.is_file():
                ontbreekt.append(str(src))
                continue
            naam = f'{sku}-{n}.png'
            shutil.copy(src, DOEL / 'afbeeldingen' / naam)
            fotos.append({'bestand': f'afbeeldingen/{naam}', 'alt': alt})
        gewicht = int(r['gewicht_g']) if r['gewicht_g'] else None
        producten.append({
            'sku': sku, 'handle': handle, 'title': r['naam'],
            'productType': TYPE.get(r['soort'], r['soort']), 'vendor': 'Brams Collectibles',
            'tags': tags, 'status': 'ACTIVE',
            'descriptionHtml': teksten.naar_html(teksten.webshop(r)),
            'seo': {'title': seo_titel, 'description': seo_tekst},
            'prijs': r['prijs'], 'voorraad': int(r['aantal']), 'gewicht_gram': gewicht,
            'inventoryPolicy': 'DENY', 'media': fotos,
        })
    (DOEL / 'producten.json').write_text(json.dumps(producten, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    for pad, naam in ONGEBRUIKT.items():
        if not naam:
            continue
        src = scratch / pad
        if src.is_file():
            shutil.copy(src, DOEL / 'ongebruikt' / naam)
        else:
            ontbreekt.append(str(src))

    collecties = [{'handle': h, 'title': t, 'descriptionHtml': d, 'sortOrder': s,
                   'regel': {'kolom': k[0], 'is_gelijk_aan': k[1]} if k else None, 'opmerking': o}
                  for h, t, d, s, k, o in COLLECTIES]
    (DOEL / 'collecties.json').write_text(json.dumps({'collecties': collecties,
        'uitgelicht_volgorde': FRONTPAGE_VOLGORDE,
        'opmerking': 'Alle slimme collecties behalve Uitgelicht. Elke collectie had een eigen afbeelding (sjabloonbeeld 1600x1600 van een product uit die collectie). 30th Celebration: afbeeldingen/BC-30-ETB-1.png.'},
        ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    menu = {'hoofdmenu': [
        {'titel': 'Home', 'url': '/'},
        {'titel': 'Soort', 'url': '/collections/all', 'items': [
            {'titel': t, 'collectie': h} for t, h in [
                ('Elite Trainer Boxes', 'elite-trainer-boxes'), ('Booster Boxes', 'booster-boxes'),
                ('Booster Bundles', 'booster-bundles'), ('Premium Collections', 'premium-collections'),
                ('Displays', 'displays'), ('Cases', 'cases')]]},
        {'titel': 'Set', 'url': '/collections/all', 'items': [
            {'titel': t, 'collectie': h} for t, h in [
                ('30th Celebration', '30th-celebration'), ('Chaos Rising', 'chaos-rising'),
                ('Pitch Black', 'pitch-black'), ('Ascended Heroes', 'ascended-heroes'),
                ('Prismatic Evolutions', 'prismatic-evolutions'), ('Destined Rivals', 'destined-rivals'),
                ('Scarlet & Violet 151', 'scarlet-violet-151'), ('Paldean Fates', 'paldean-fates')]]},
        {'titel': 'Alles', 'url': '/collections/all'},
        {'titel': 'Gids', 'blog': 'gids'},
        {'titel': 'Contact', 'pagina': 'contact'}],
        'voettekstmenu': [{'titel': 'Zoeken', 'url': '/search'}],
        'opmerking': 'De voettekst had alleen Zoeken. Beleidspagina\'s horen er nog bij zodra ze bestaan.'}
    (DOEL / 'menu.json').write_text(json.dumps(menu, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    def trede(naam, prijs, vanaf, tot=None):
        return {'naam': naam, 'prijs_eur': prijs, 'bestelbedrag_vanaf': vanaf, 'bestelbedrag_tot': tot}
    verzending = {
        'profiel': 'Algemeen profiel', 'conditie': 'op totaalbedrag van de bestelling, niet op gewicht',
        'zones': [
            {'zone': 'Nederland', 'landen': ['Netherlands'], 'tarieven': [
                trede('Verzekerd verzonden — PostNL', 6.95, 0, 99.99),
                trede('Verzekerd verzonden — PostNL', 9.95, 100, 499.99),
                trede('Verzekerd verzonden — PostNL, hoge waarde', 14.95, 500)]},
            {'zone': 'EU (Europeese Unie)', 'landen': ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Germany', 'Denmark', 'Estonia', 'Finland', 'France', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden'], 'tarieven': [
                trede('Verzekerd verzonden — EU', 14.95, 0, 499.99),
                trede('Verzekerd verzonden — EU, hoge waarde', 24.95, 500)]},
            {'zone': 'International', 'landen': ['United Arab Emirates', 'Australia', 'Canada', 'Switzerland', 'United Kingdom', 'Hong Kong', 'Israel', 'Japan', 'South Korea', 'Malaysia', 'Norway', 'New Zealand', 'Singapore', 'United States'], 'tarieven': [
                trede('Verzekerd verzonden — buiten de EU', 24.95, 0, 499.99),
                trede('Verzekerd verzonden — buiten de EU, hoge waarde', 49.95, 500)]}],
        'ophalen': 'gratis, op afspraak (in Shopify als aparte optie bij het afrekenen)',
        'opmerking': 'Bedragen zijn een voorstel op basis van PostNL-tarieven; er is nog geen doos gewogen. Zie teksten/vragen-aan-bram.md punt 11 over verzenden buiten de EU.'}
    (DOEL / 'verzending.json').write_text(json.dumps(verzending, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    winkel = {
        'naam': 'Brams Collectibles', 'intern_adres': 'mwbxzp-qm.myshopify.com', 'plan': 'Basic',
        'aangemaakt': '2026-09-10', 'valuta': 'EUR', 'tijdzone': 'Europe/Amsterdam',
        'domein': {'primair': 'bramscollectibles.nl', 'registrar': 'Hostnet',
                   'dns': 'A-record apex naar 23.227.38.65, CNAME www naar shops.myshopify.com. (met punt)'},
        'winkelmail_toen': 'edward@sozials.com', 'winkelmail_hoort_te_zijn': 'bramr94@gmail.com',
        'thema': {'repo': 'edwardgijswijt-byte/brams-collectibles-theme', 'branch': 'main',
                  'naam_in_shopify': 'brams-collectibles-theme/main', 'basis': 'Dawn 16.0.0'},
        'verkoopkanalen_per_product': ['Webshop', 'Shop'],
        'locatie': 'Winkellocatie',
        'wachtwoord': 'De winkel stond achter een wachtwoord; het wachtwoord staat niet in dit archief.',
        'bedrijf': {'kvk': '42024670', 'btw': '8693.52.751.B.01',
                    'adres': 'Nachtegaallaan 55, 3741 WT Baarn', 'email': 'bramr94@gmail.com',
                    'opmerking': 'Zie teksten/bedrijfsgegevens.md voor wat nog openstaat (rechtspersoon, btw-positie).'},
        'blog': {'gids': '5 artikelen, bron in teksten/blog/, uitvoer in teksten/uit/blog/'},
        'paginas': ['Contact (leeg)', 'Modelformulier voor herroeping (verborgen) — shopify/paginas/modelformulier-herroeping.md'],
        'beleid_in_shopify_toen': 'alleen het standaard privacybeleid van Shopify met edward@sozials.com; de eigen teksten staan in shopify/paginas/ en shopify/paginas/uit/',
    }
    (DOEL / 'winkel.json').write_text(json.dumps(winkel, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    print(f'{len(producten)} producten, {sum(len(p["media"]) for p in producten)} foto\'s')
    if ontbreekt:
        print('NIET GEVONDEN:'); [print('  ', o) for o in ontbreekt]
        sys.exit(1)


if __name__ == '__main__':
    main()

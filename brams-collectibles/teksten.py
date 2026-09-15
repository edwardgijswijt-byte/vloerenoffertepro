#!/usr/bin/env python3
"""Advertentieteksten samenstellen uit register.csv en de tekstblokken.

    python3 teksten.py                 alles wat voorraad heeft
    python3 teksten.py BC-PE-PCETB     één artikel

Uitvoer in teksten/uit/<sku>.md — Marktplaats, socials en webshop onder elkaar,
klaar om te plakken.

De opbouw volgt de advertenties die Bram zelf schreef:
    merkverhaal (nooit anders)
    productnaam en hoogtepunten (per product)
    waarom deze set (per set, gedeeld door alle artikelen uit die set)
    bundelaanbod (alleen als er meer uit dezelfde set op voorraad ligt)
    verzenden of ophalen (nooit anders)

Die volgorde is de reden dat de tekst opgeknipt is. In de losse Word-bestanden
stond de settekst drie keer overgetypt, en in twee ervan eindigde hij op de
verkeerde productnaam. Zo kan dat niet meer.
"""
import csv, pathlib, re, sys

HIER = pathlib.Path(__file__).parent
UIT = HIER / 'teksten' / 'uit'


def blokken(pad):
    """Een .md met '## naam'-koppen inlezen als {naam: tekst}."""
    tekst = pathlib.Path(pad).read_text(encoding='utf-8')
    delen = re.split(r'^## +(.+)$', tekst, flags=re.M)[1:]
    return {k.strip(): v.strip() for k, v in zip(delen[::2], delen[1::2])}


MERK = blokken(HIER / 'teksten' / 'merk.md')


def settekst(slug):
    pad = HIER / 'teksten' / 'sets' / f'{slug}.md'
    if not pad.exists():
        return f'[NOG GEEN SETTEKST voor {slug} — teksten/sets/{slug}.md aanmaken]'
    return blokken(pad).get('tekst', '')


def bedrag(waarde):
    """Nederlands: punt voor de duizendtallen, komma als decimaalteken, en hele
    bedragen als 1.740,- in plaats van 1.740,00."""
    n = float(waarde)
    heel, cent = divmod(round(n * 100), 100)
    duizend = f'{heel:,}'.replace(',', '.')
    return f'{duizend},-' if cent == 0 else f'{duizend},{cent:02d}'


def prijs(r):
    return f'€ {bedrag(r["prijs"])}' if r['prijs'] else '€ [PRIJS]'


def hoogtepunten(r):
    return [h.strip() for h in r['hoogtepunten'].split('|') if h.strip()]


def pokemon_center(r):
    """Het blok over de Pokemon Center-oplages, als het er een is.

    Staat in merk.md en is dus voor elk Pokemon Center-artikel hetzelfde:
    Prismatic, Pitch Black, Chaos Rising, Ascended Heroes. Herkenning aan de
    naam, zodat je het niet per artikel kunt vergeten aan te vinken."""
    return 'Pokémon Center' in r['naam']


def bundel(r, alles):
    """Bram biedt een bundelprijs als er meer uit dezelfde set ligt.

    Normaal noemen we de soorten: "in combinatie met een Booster Box of
    Booster Bundle". Maar Pitch Black heeft twee Elite Trainer Boxen, de
    gewone en die van het Pokemon Center, en dan kwam er "koop je hem in
    combinatie met een ETB" te staan onder een advertentie voor een ETB.
    Zijn eigen soort telt daarom niet mee, en blijft er niets over, dan
    noemen we het andere artikel bij naam — dat is toch duidelijker."""
    zelfde_set = [a for a in alles
                  if a['set'] == r['set'] and a['sku'] != r['sku'] and a['aantal'] and a['prijs']]
    if not zelfde_set:
        return ''
    soorten = list(dict.fromkeys(a['soort'] for a in zelfde_set if a['soort'] != r['soort']))
    if soorten:
        lijst = (' of '.join([', '.join(soorten[:-1]), soorten[-1]])
                 if len(soorten) > 1 else soorten[0])
        return (f'Koop je hem in combinatie met een {lijst}, dan maken wij een '
                f'mooie bundelprijs voor je!')
    namen = [a['naam'] for a in zelfde_set]
    lijst = ' of de '.join([', de '.join(namen[:-1]), namen[-1]]) if len(namen) > 1 else namen[0]
    return (f'Koop je hem samen met de {lijst}, dan maken wij een '
            f'mooie bundelprijs voor je!')


def omslaan(tekst, breedte=78):
    """Regels afbreken op dezelfde breedte als de vaste tekstblokken.

    De blokken uit merk.md en teksten/sets/ zijn met de hand op 78 tekens
    gezet. Wat we er zelf bij schrijven — de bundelregel, Brams zin uit de
    kolom publiek — kwam als één lange regel mee, tot 164 tekens. In het
    invulveld van Marktplaats valt dat niet op, in de geplaatste advertentie
    wel: één alinea die anders uitloopt dan de rest."""
    import textwrap
    return '\n\n'.join(textwrap.fill(deel, breedte) for deel in tekst.split('\n\n'))


def ontvouwen(tekst):
    """De regelafbrekingen binnen een alinea eruit halen.

    De blokken uit merk.md en teksten/sets/ staan met de hand afgebroken op 78
    tekens, en omslaan() doet hetzelfde met wat we er zelf bij schrijven. Dat
    leest prettig in de repo en in de plaatslijst. Maar het invulveld van
    Marktplaats breekt zelf af op de breedte van de kolom, en die harde enters
    blijven staan: je krijgt een alinea die halverwege afbreekt en op een nieuwe
    regel verdergaat. Wie dat wil rechtzetten moet de hele tekst nalopen.

    Dus voor het plakken: elke alinea op een regel, alinea's gescheiden door een
    lege regel. Een regel die met een opsommingsteken begint blijft op zichzelf
    staan, anders plakken de punten aan elkaar.

    Wat we niet doen is ook de lege regels weghalen. Marktplaats houdt de
    witregel tussen alinea's wel netjes aan; het zijn alleen de enters binnen
    een alinea die niet kloppen."""
    uit = []
    for deel in tekst.split('\n\n'):
        blok, lopend = [], []
        for regel in deel.split('\n'):
            if regel.lstrip().startswith(('•', '-')):
                if lopend:
                    blok.append(' '.join(lopend))
                    lopend = []
                blok.append(regel.strip())
            else:
                lopend.append(regel.strip())
        if lopend:
            blok.append(' '.join(lopend))
        uit.append('\n'.join(blok))
    return '\n\n'.join(uit)


def marktplaats(r, alles):
    d = ['Brams Collectibles', '', MERK['verhaal-lang'], '', r['naam'], '']
    hp = hoogtepunten(r)
    if hp:
        d += ['De hoogtepunten:']
        d += [f'• In perfecte staat en sealed.'] if r['staat'] == 'sealed' else []
        d += [f'• {h}' for h in hp]
        if r['soort'] in ('ETB', 'Premium Collection'):
            d += ['En nog veel meer!']      # in een ETB zit meer dan je opsomt
        d += ['']
    if r['publiek']:
        d += [omslaan(r['publiek']), '']
    d += [settekst(r['set']), '']
    if pokemon_center(r):
        d += [MERK['pokemon-center'].replace('**', ''), '']
    if r['hoes'] == 'ja':
        d += ['Zit in een acryl beschermhoes, die gaat mee bij verkoop.', '']
    b = bundel(r, alles)
    if b:
        d += [omslaan(b), '']
    d += [MERK['verzenden'].replace('**', ''), '']
    d += [f'Prijs: {prijs(r)}']
    return ontvouwen('\n'.join(d))


# ---------------------------------------------------------------- Instagram

# Hashtags in drie lagen: wat je altijd meegeeft, wat bij de set hoort en wat
# bij het soort doos hoort. Zo staat er onder elke post dezelfde basis en
# daarbovenop precies de tags waarop een verzamelaar van díé set zoekt.
#
# Waarom niet dertig tags: Instagram staat er dertig toe, maar een post die
# onder dertig verschillende onderwerpen wordt gehangen komt in geen enkele
# ervan bovenaan. Vijftien tot twintig gerichte tags is hier de maat, en de
# helft daarvan is set- of soortspecifiek.
#
# Deze lijst is opgebouwd uit de set- en soortnamen zelf; hij is niet getoetst
# aan wat op Instagram werkelijk loopt. Wat er is afgesloten of verstopt door
# Instagram kan hier niet worden nagegaan — die controle is handwerk in de app.
TAGS_BASIS = ['pokemontcg', 'pokemonkaarten', 'sealedpokemon', 'pokemonsealed',
              'pokemonnederland', 'tcgnederland', 'bramscollectibles']

TAGS_SET = {
    'sv-151':               ['pokemon151', 'scarletviolet151', 'kanto151'],
    'prismatic-evolutions': ['prismaticevolutions', 'eeveelutions', 'eevee'],
    'chaos-rising':         ['chaosrising', 'megaevolution'],
    'pitch-black':          ['pitchblack', 'megaevolution', 'megadarkrai'],
    'destined-rivals':      ['destinedrivals', 'teamrocket'],
    'ascended-heroes':      ['ascendedheroes', 'megaevolution'],
    'first-partner':        ['firstpartnerpack', 'firstpartnercollection'],
    'paldean-fates':        ['paldeanfates', 'shinypokemon', 'shinymimikyu'],
}

TAGS_SOORT = {
    'ETB':                ['elitetrainerbox', 'pokemonetb'],
    'Booster Box':        ['boosterbox', 'pokemonboosterbox'],
    'Booster Bundle':     ['boosterbundle'],
    'Display':            ['boosterdisplay', 'pokemondisplay'],
    'Case':               ['sealedcase', 'pokemoncase'],
    'Premium Collection': ['premiumcollection'],
}

TAGS_VERZAMELEN = ['pokemoncollector', 'sealedcollection', 'pokemonverzamelaar']

# Artikelen die zelf een onderwerp zijn waar mensen op zoeken, los van de set.
# Alleen invullen waar dat echt zo is: een tag die niemand intikt kost een plek
# in de lijst en levert niets op.
TAGS_ARTIKEL = {
    'BC-MEV-GREN': ['megagreninja'],
    'BC-PE-SPC': ['superpremiumcollection'],
}


def hashtags(r):
    """De tags voor één artikel, zonder dubbele, in een vaste volgorde."""
    tags = list(TAGS_BASIS)
    tags += TAGS_SET.get(r['set'], [])
    tags += TAGS_SOORT.get(r['soort'], [])
    tags += TAGS_ARTIKEL.get(r['sku'], [])
    if pokemon_center(r):
        tags += ['pokemoncenter', 'pokemoncenteretb']
    tags += TAGS_VERZAMELEN
    return ['#' + t for t in dict.fromkeys(tags)]


def alttekst(r):
    """Wat er op de foto staat, voor het alt-tekstveld van Instagram.

    Twee redenen om dit in te vullen: een schermlezer heeft er iets aan, en
    Instagram leest het mee bij het zoeken. Het staat er standaard niet in, dus
    het is gratis vindbaarheid die de meeste accounts laten liggen."""
    kant = 'op een donkerblauwe achtergrond met het logo van Brams Collectibles'
    return f'Verzegelde {r["naam"]}, {kant}.'


def instagram(r, alles, oproep='dm'):
    """Bijschrift voor Instagram.

    De opbouw is die van de andere teksten, maar de volgorde is omgedraaid:
    hier staat de productnaam bovenaan en het merkverhaal niet in de post. Dat
    is geen stijlkeuze. Instagram knipt een bijschrift in de tijdlijn af rond
    de honderdvijfentwintig tekens, dus wat daarna komt leest alleen wie op
    "meer" tikt. En Instagram doorzoekt sinds een paar jaar ook de tekst van
    het bijschrift zelf, niet alleen de hashtags — dus de setnaam en de
    productnaam horen in de eerste regels te staan en niet onderaan.

    `oproep` bepaalt de laatste regel. Zolang de winkel achter een wachtwoord
    staat is "link in bio" een doodlopende weg; dan is een dm de enige oproep
    die werkt."""
    hp = hoogtepunten(r)
    d = [r['naam'], '']
    d += [f'{hp[0]}. Fabrieksverzegeld, nooit open geweest.' if hp
          else 'Fabrieksverzegeld, nooit open geweest.', '']
    if len(hp) > 1:
        # Een case is geen doos maar een carton met dozen erin, en een display
        # ook niet. "In de doos" onder een carton met tien ETB's leest fout.
        kop = {'Case': 'In de carton:', 'Display': 'In het display:'}.get(
            r['soort'], 'In de doos:')
        d += [kop] + [f'• {h}' for h in hp[1:6]] + ['']
    if r['publiek']:
        d += [r['publiek'], '']
    if pokemon_center(r):
        d += [MERK['pokemon-center'].replace('**', '').split('\n\n', 1)[1], '']
    d += [settekst(r['set']), '']
    b = bundel(r, alles)
    if b:
        d += [b, '']
    if oproep == 'bio':
        d += [f'{prijs(r)} — link in bio.']
    else:
        d += [f'{prijs(r)} — stuur een dm voor beschikbaarheid of om op te halen.']
    # Zelfde reden als bij Marktplaats: de bronblokken staan met de hand
    # afgebroken op 78 tekens en Instagram breekt zelf af op schermbreedte.
    # Die harde enters blijven staan en dan valt een alinea halverwege stil.
    return ontvouwen('\n'.join(d))


def socials(r):
    hp = hoogtepunten(r)
    kern = hp[0] if hp else r['soort']
    tags = ('#pokemontcg #' + r['set'].replace('-', '') +
            ' #sealed #pokemonnederland #tcgnederland #bramscollectibles')
    return '\n'.join([
        f'{r["naam"]}. Sealed{", in acrylhoes" if r["hoes"] == "ja" else ""}.',
        '', kern + '.', '', settekst(r['set']), '',
        'Prijs en beschikbaarheid: link in bio.', '', tags,
    ])


def fotoregel(r):
    """Bij meerdere identieke sealed dozen zijn de foto's van een exemplaar uit
    de voorraad, niet van het exemplaar dat de koper krijgt. Dat moet er staan,
    anders klopt de advertentie niet met wat er in de doos gaat."""
    if (int(r['aantal'] or 0)) > 1:
        return ("De foto's zijn van een exemplaar uit de voorraad; alle exemplaren zijn "
                "ongeopend en identiek.")
    return "De foto's zijn van dit exemplaar."


GIDS = {
    'wat-is-een-elite-trainer-box': 'Wat is een Elite Trainer Box en wat zit erin?',
    'pokemon-center-uitgaven': 'Wat maakt een Pokémon Center-uitgave anders?',
    'booster-bundle-booster-box-of-elite-trainer-box':
        'Booster bundle, booster box of Elite Trainer Box — wat kun je het beste kopen?',
    'verzegelde-pokemon-dozen-bewaren': 'Verzegelde Pokémon-dozen bewaren',
    'is-verzegelde-pokemon-tcg-een-goede-investering':
        'Is verzegelde Pokémon TCG een goede investering?',
}


def gidslinks(r):
    """De gidsartikelen die bij dit artikel horen, hoogstens drie.

    Losse artikelen over losse onderwerpen leveren weinig op; een groepje dat
    naar elkaar en naar de producten verwijst wel. Dit is de kant van product
    naar gids. Welke links je krijgt hangt af van `soort` en van de naam, zodat
    een nieuw artikel in het register ze vanzelf meekrijgt en niemand ze met de
    hand hoeft bij te plakken.

    Bewaren staat er altijd bij: dat is de vraag die elke koper van verzegeld
    materiaal een keer stelt, ongeacht wat hij koopt."""
    keuze = []
    if r['soort'] == 'ETB':
        keuze.append('wat-is-een-elite-trainer-box')
        if pokemon_center(r):
            keuze.append('pokemon-center-uitgaven')
    else:
        keuze.append('booster-bundle-booster-box-of-elite-trainer-box')
    if r['soort'] in ('Display', 'Case') or 'Pokémon Center' in r['naam']:
        keuze.append('is-verzegelde-pokemon-tcg-een-goede-investering')
    keuze.append('verzegelde-pokemon-dozen-bewaren')

    uniek = list(dict.fromkeys(keuze))[:3]
    return [(f'/blogs/gids/{h}', GIDS[h]) for h in uniek]


def webshop(r):
    d = [settekst(r['set']), '']
    if pokemon_center(r):
        d += [MERK['pokemon-center'], '']
    if r['hoes'] == 'ja':
        d += ['Geleverd in de acryl beschermhoes waarin hij op de foto staat.', '']
    hp = hoogtepunten(r)
    if hp:
        d += ['Inhoud:', '']
        d += [f'- {h}' for h in hp]
        d += ['']
    if r['publiek']:
        d += [omslaan(r['publiek']), '']
    d += [f'Staat: {r["staat"]}. {fotoregel(r)}', '']
    links = gidslinks(r)
    if links:
        d += ['Meer weten:', '']
        d += [f'- [{titel}]({url})' for url, titel in links]
        d += ['']
    d += [MERK['verzenden']]
    return '\n'.join(d)


def koppeling(t):
    """[tekst](url) omzetten naar een anker.

    Alleen in de webshoptekst: op Marktplaats en in de socialtekst zijn links
    naar de eigen winkel niet klikbaar en soms niet eens toegestaan."""
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)


def naar_html(tekst):
    """De webshoptekst omzetten naar de HTML die Shopify in het product zet.
    Alleen wat webshop() ook echt maakt: alinea's, een opsomming, een kop en
    de links naar de gidsartikelen."""
    uit, lijst = [], []
    for blok in tekst.split('\n\n'):
        blok = blok.strip()
        if not blok:
            continue
        if blok.startswith('- '):
            lijst = [r[2:].strip() for r in blok.split('\n') if r.startswith('- ')]
            uit.append('<ul>\n' + '\n'.join(f'<li>{koppeling(h)}</li>' for h in lijst) + '\n</ul>')
        elif blok.startswith('**') and blok.endswith('**'):
            uit.append(f'<h3>{blok.strip("*")}</h3>')
        else:
            regel = ' '.join(blok.split('\n'))
            if regel.endswith(':') and len(regel) < 40:
                uit.append(f'<p><strong>{regel}</strong></p>')
            else:
                uit.append(f'<p>{koppeling(regel)}</p>')
    return '\n\n'.join(uit)


def schrijf(r, alles):
    UIT.mkdir(parents=True, exist_ok=True)
    doel = UIT / f'{r["sku"]}.md'
    doel.write_text('\n'.join([
        f'# {r["naam"]}', '',
        f'`{r["sku"]}` · set {r["set"]} · {prijs(r)}',
        '', '---', '', '## Marktplaats', '', '```', marktplaats(r, alles), '```',
        '', '## Instagram / TikTok', '', '```', socials(r), '```',
        '', '## Webshop', '', '```', webshop(r), '```', '',
    ]), encoding='utf-8')
    return doel


if __name__ == '__main__':
    alles = list(csv.DictReader(open(HIER / 'register.csv', encoding='utf-8')))
    keuze = sys.argv[1:] or [r['sku'] for r in alles if r['aantal']]
    for r in alles:
        if r['sku'] in keuze:
            p = schrijf(r, alles)
            print(f'{r["sku"]:<14} -> {p.relative_to(HIER)}')

#!/usr/bin/env python3
"""Achtergrond verwijderen van productfoto's.

Gebruik:  python3 uitsnijden.py fotos/*.jpg
Uitvoer:  fotos/uitgesneden/<naam>.png  — transparante achtergrond,
          strak bijgesneden en op een vierkant canvas met wat lucht eromheen.

Werkt met rembg (isnet-general-use) als die beschikbaar is. Zo niet, dan valt
het script terug op een eigen masker dat de donkere stoffen achtergrond
wegsnijdt. Een acrylcase is doorzichtig en spiegelt, dus de terugval maakt
het masker bewust ruim en trekt hem daarna weer aan.
"""
import sys, pathlib
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

UIT = pathlib.Path('fotos/uitgesneden')
STRAK = UIT / 'strak'
MAXZIJ = 2000          # langste zijde van de uitvoer
LUCHT  = 0.06          # marge rondom het product, als deel van de langste zijde


def masker_rembg(im, matting=True):
    """Met alpha matting voor een zachte rand; zonder voor alleen de vorm.

    Op een opgehelderde kopie is matting niet alleen overbodig maar ook
    onbetrouwbaar: de oplosser loopt op een bijna wit beeld minutenlang te
    ploeteren op een matrix die niet positief-definiet wil worden. De rand van
    dat masker doet er niet toe, want rechtzetten.py trekt hem daarna toch aan."""
    from rembg import remove, new_session
    sess = new_session('isnet-general-use')
    if matting:
        uit = remove(im, session=sess, alpha_matting=True,
                     alpha_matting_foreground_threshold=250,
                     alpha_matting_background_threshold=15,
                     alpha_matting_erode_size=8)
    else:
        uit = remove(im, session=sess, alpha_matting=False)
    return np.array(uit.convert('RGBA'))[:, :, 3]


def vulling(a):
    """Hoe vol het masker zijn eigen omhullende rechthoek maakt.

    Alles wat we fotograferen is een doos, en een doos vult zijn rechthoek voor
    ongeveer negentig procent. Blijft er de helft over, dan heeft rembg er een
    hap uit genomen. Gaten tellen werkt hier niet: bij een zwarte doos op zwarte
    stof loopt het weggevallen deel tot aan de rand door, en dan is het geen gat
    meer maar een inham."""
    m = a > 128
    if not m.any():
        return 0.0
    ys, xs = np.nonzero(m)
    vlak = (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)
    return float(m.sum()) / float(vlak)


def omvang(a):
    """Het oppervlak van de omhullende rechthoek van de grootste vlek.

    Waarom de grootste vlek en niet het hele masker: masker_dubbelslag zet de
    rechthoek van het gematte masker af tegen die van het ruwe om te zien of de
    matting een band heeft opgegeten. Bij de Chaos Rising Pokemon Centre-doos
    pakte het ruwe masker een los stukje plakband van de tafel mee. Dat is
    honderd pixels, maar het ligt een eind onder de doos, dus de rechthoek van
    het ruwe masker werd anderhalf keer zo groot en het gematte masker leek
    ineens een band kwijt. Het werd afgekeurd terwijl het voor 96 procent
    gevuld was en het ruwe voor 65. Daarna ging de reparatie er overheen en was
    het helemaal mis."""
    from scipy.ndimage import label
    lab, n = label(a > 128)
    if n == 0:
        return 0
    tel = np.bincount(lab.ravel())
    tel[0] = 0
    ys, xs = np.nonzero(lab == tel.argmax())
    return (ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)


def masker_dubbelslag(im):
    """Eerst gewoon. Deugt het masker niet, dan nog eens op een opgehelderde
    kopie — het masker komt dan wel goed, en leggen we op het origineel.

    Reden: matzwart karton op zwart satijn geeft rembg te weinig verschil. Op
    driemaal helderder met wat extra contrast vindt hij de doos in zijn geheel.
    De kleuren van de uitvoer blijven die van de originele opname.

    Twee metingen, want ze vangen elk iets anders. `vulling` ziet een hap uit
    de doos. Maar snijdt de matting een hele band weg — de lichte bovenrand van
    de Ascended Heroes-bundel kreeg alpha 12, dwars over de volle breedte —
    dan krimpt de omhullende rechthoek mee en blijft de vulling keurig hoog.
    Daarom ernaast een masker zonder matting: dat is ruwer aan de rand maar
    geeft wel de hele doos. Scheelt de rechthoek meer dan een tiende, dan heeft
    de matting een stuk opgegeten en nemen we het ruwe masker."""
    a = masker_rembg(im)
    ruw = masker_rembg(im, matting=False)
    krimp = omvang(a) / omvang(ruw) if omvang(ruw) else 1.0
    if krimp < 0.90:
        beste, hoe = ruw, f'zonder matting (matting sneed tot {krimp:.0%} weg)'
    else:
        beste, hoe = a, 'gewoon'
    if vulling(beste) >= 0.70:
        return beste, f'rembg {hoe} ({vulling(beste):.0%} gevuld)'

    op = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(3.0)).enhance(1.4)
    b = masker_rembg(op, matting=False)
    if vulling(b) > vulling(beste):
        beste, hoe = b, 'opgehelderd'
    if vulling(beste) >= 0.70:
        return beste, f'rembg {hoe} ({vulling(beste):.0%} gevuld)'

    c = masker_omhullende(im, beste)
    if vulling(c) > vulling(beste):
        return c, f'omhullende na rembg {hoe} ({vulling(beste):.0%} -> {vulling(c):.0%} gevuld)'
    return beste, f'rembg {hoe} ({vulling(beste):.0%} gevuld, niets hielp)'


def masker_omhullende(im, a):
    """Laatste redmiddel als rembg de doos niet heel krijgt.

    Waarom dit mag: alles wat we fotograferen is een doos, en een doos is
    convex. De omtrek die rembg vindt klopt meestal wel; wat misgaat zit
    binnenin. Bij de Destined Rivals-doos las hij het zwarte artwork als
    achtergrond en stond Giovanni als gat in het masker. Gaten vullen was
    niet genoeg — Mewtwo loopt tot aan de doosrand door, dus dat is een
    inham en geen gat. De omhullende trekt het in een keer recht.

    De omhullende neemt wel wat achtergrond mee waar hij over een holle
    hoek springt. Dat snijden we er weer af op kleur: de muur achter de
    doos is egaal, dus bemonster hem in de hoeken van de opname en gooi
    binnen de omhullende alles weg wat daar dicht bij ligt. Bij de
    Destined Rivals-doos zat het eerste percentiel van de doos zelf op
    afstand 16 en de rest op 194, dus een drempel van 30 raakt alleen het
    randje."""
    from scipy.ndimage import binary_fill_holes, label
    from skimage.morphology import convex_hull_image
    m = binary_fill_holes(a > 128)
    if not m.any():
        return a
    lab, n = label(m)
    if n > 1:
        tel = np.bincount(lab.ravel())
        tel[0] = 0
        m = lab == tel.argmax()
    h = convex_hull_image(m)
    rgb = np.asarray(im.convert('RGB')).astype(np.int16)
    hoek = np.concatenate([rgb[:80, :80].reshape(-1, 3), rgb[:80, -80:].reshape(-1, 3)])
    muur = np.median(hoek, axis=0)
    ver = np.sqrt(((rgb - muur) ** 2).sum(axis=2)) > 30
    return np.where(binary_fill_holes(h & ver), 255, 0).astype(np.uint8)


def masker_rechthoek(a):
    """Alles wat we fotograferen is een doos, en een doos die recht voor de lens
    staat is in beeld een rechthoek. Blijft rembg met een hap eruit zitten — bij
    een donkere doos tegen een donkere achtergrond gebeurt dat — dan legt de
    kleinste gedraaide rechthoek om het masker de doos weer heel.

    Waarom dit beter is dan de omhullende: die is wel convex maar niet recht.
    Mist rembg de rechteronderhoek, dan springt de omhullende schuin van de
    rechterbovenhoek naar linksonder en snijdt de doos diagonaal doormidden.
    Precies dat ging mis bij de Prismatic Super-Premium Collection: het masker
    vulde zijn rechthoek voor 75 procent, de omhullende maakte er 79 van en de
    doos was zijn halve rechterkant kwijt. De gedraaide rechthoek komt op 94
    procent en de doos is heel.

    Voorwaarde is wel dat de doos recht voor de lens staat. Staat hij schuin,
    dan is hij in beeld een trapezium en pakt de rechthoek de hoeken
    achtergrond mee. Daarom alleen voor opnames in MET_RECHTHOEK."""
    from scipy.ndimage import label, binary_fill_holes
    from scipy.spatial import ConvexHull
    from skimage.draw import polygon
    lab, n = label(a > 128)
    if n == 0:
        return a
    tel = np.bincount(lab.ravel())
    tel[0] = 0
    m = binary_fill_holes(lab == tel.argmax())
    ys, xs = np.nonzero(m)
    punten = np.column_stack([xs, ys]).astype(float)
    omtrek = punten[ConvexHull(punten).vertices]
    beste = None
    for i in range(len(omtrek)):                 # roterende schuifmaat
        rib = omtrek[(i + 1) % len(omtrek)] - omtrek[i]
        lang = np.hypot(*rib)
        if lang < 1e-9:
            continue
        rib = rib / lang
        draai = np.array([[rib[0], rib[1]], [-rib[1], rib[0]]])
        p = omtrek @ draai.T
        lo, hi = p.min(axis=0), p.max(axis=0)
        opp = (hi - lo).prod()
        if beste is None or opp < beste[0]:
            hoeken = np.array([[lo[0], lo[1]], [hi[0], lo[1]],
                               [hi[0], hi[1]], [lo[0], hi[1]]])
            beste = (opp, hoeken @ draai)
    uit = np.zeros(a.shape, np.uint8)
    rr, cc = polygon(beste[1][:, 1], beste[1][:, 0], a.shape)
    uit[rr, cc] = 255
    return uit


def masker_terugval(im):
    """Zonder rembg: de achtergrond is donkere stof, het product is licht en
    scherp. We combineren helderheid met lokaal contrast (stof is egaal,
    karton en acryl niet) en houden daarna de grootste samenhangende vorm."""
    g = np.asarray(im.convert('L'), dtype=np.float32) / 255.0
    # lokaal contrast: verschil met een sterk vervaagde versie
    vaag = np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(9)),
                      dtype=np.float32) / 255.0
    detail = np.asarray(im.convert('L').filter(ImageFilter.FIND_EDGES)
                          .filter(ImageFilter.GaussianBlur(6)),
                        dtype=np.float32) / 255.0

    drempel = np.percentile(g, 35)                 # stof zit in de donkere helft
    score = (g - drempel) * 2.2 + detail * 3.0 + (g - vaag) * 1.5
    m = np.clip(score, 0, 1)
    m = (m > 0.35).astype(np.uint8)

    m = grootste_vlek(m)
    m = gaten_vullen(m)
    mi = Image.fromarray(m * 255).filter(ImageFilter.GaussianBlur(2.0))
    a = np.asarray(mi, dtype=np.float32)
    a = np.clip((a - 90) * (255.0 / 90.0), 0, 255)  # rand weer aantrekken
    return a.astype(np.uint8)


def grootste_vlek(m):
    """Grootste 4-verbonden component, zonder scipy."""
    h, w = m.shape
    label = np.zeros((h, w), dtype=np.int32)
    huidig, groottes = 0, {}
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if label[y0, x0]:
            continue
        huidig += 1
        stapel, n = [(y0, x0)], 0
        label[y0, x0] = huidig
        while stapel:
            y, x = stapel.pop()
            n += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not label[yy, xx]:
                    label[yy, xx] = huidig
                    stapel.append((yy, xx))
        groottes[huidig] = n
    if not groottes:
        return m
    beste = max(groottes, key=groottes.get)
    return (label == beste).astype(np.uint8)


def gaten_vullen(m):
    """Alles wat niet vanaf de rand bereikbaar is, hoort bij het product.
    Vangt de doorzichtige acrylcase en lichte plekken binnen de doos."""
    h, w = m.shape
    buiten = np.zeros((h, w), dtype=bool)
    stapel = []
    for x in range(w):
        for y in (0, h - 1):
            if not m[y, x] and not buiten[y, x]:
                buiten[y, x] = True
                stapel.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not m[y, x] and not buiten[y, x]:
                buiten[y, x] = True
                stapel.append((y, x))
    while stapel:
        y, x = stapel.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and not m[yy, xx] and not buiten[yy, xx]:
                buiten[yy, xx] = True
                stapel.append((yy, xx))
    return (~buiten).astype(np.uint8)


# Opnames waar de tafelrand onder de doos is meegepakt. Zie voetstuk_weg.
# Met het oog vastgesteld, om dezelfde reden als bij MET_RECHTHOEK: een doos die
# door perspectief naar onderen breder wordt en een doos die op een tafelrand
# staat geven in cijfers hetzelfde beeld. Gemeten op helderheid, op R-B en op
# horizontale randsterkte — geen van drieen scheidt ze.
MET_VOETSTUK = {
    'BC-151-BNDD-N2', 'BC-AH-BNDD-N2', 'BC-AH-PCETB-N2',
    'BC-FP-CASE2-N2', 'BC-PE-SPC-N1',
}

# Opnames waar de tafel niet breder is dan de doos en voetstuk_weg hem dus niet
# ziet. Bij de Ascended Heroes-bundeldisplay staat de doos op een houten balk
# van precies dezelfde breedte. Hier de hoogte waarop het masker wordt
# afgesneden, als deel van de hoogte van het masker zelf — met de hand
# opgemeten aan de sprong in helderheid op de onderrand van de doos.
HANDSNEE = {'BC-AH-BNDD-N2': 0.776, 'BC-PE-SPC-N1': 0.80}

# Opnames van een doos die recht voor de lens staat en waar rembg een hap uit
# het masker neemt. Zie masker_rechthoek. Met het oog vastgesteld, want een
# trapezium door perspectief en een echte hap zien er in cijfers hetzelfde uit.
MET_RECHTHOEK = {
    'BC-PE-SPC-N1', 'BC-PE-SPC-N2',
    'BC-MEV-GREN-N1', 'BC-MEV-GREN-N2',
}


def voetstuk_weg(a, speling=0.012, houvast=0.03):
    """De tafelrand onder de doos wegsnijden — alleen waar dat gevraagd wordt.

    Bram zet de doos op de rand van zijn tafel en plakt hem vast met
    schilderstape. Bij sommige opnames pakt rembg die tafelrand mee: de doos
    staat dan op een plak hout met twee stukken tape eraan.

    Dit werd eerst automatisch gedaan, op de waarneming dat het tafelblad
    zijwaarts buiten de doos uitsteekt en het masker daar dus breder wordt.
    Dat is bij het 151-display ook zo, maar het is geen bruikbaar kenmerk: een
    doos die iets van boven is geschoten loopt naar onderen óók breder, door
    perspectief. Die regel sneed vervolgens de onderkant van de Chaos Rising
    Pokemon Center-doos, het Ascended Heroes-display en de First Partner
    serie 2-carton af. Helderheid, kleur en randkracht scheiden ze evenmin —
    alle drie gemeten, alle drie onbruikbaar.

    Automatisch raden kost hier meer dan het oplevert. Wie een opname ziet met
    tafel eronder zet hem in MET_VOETSTUK; de rest blijft ongemoeid.
    """
    m = a > 128
    if not m.any():
        return a
    breed = m.sum(axis=1)
    rijen = np.nonzero(breed > 0)[0]
    top, onder = rijen[0], rijen[-1]
    hoog = onder - top + 1
    if hoog < 50:
        return a
    kern = np.median(breed[top + int(hoog * 0.10):top + int(hoog * 0.60)])
    if kern <= 0:
        return a

    vast = max(3, int(hoog * houvast))
    for y in range(top + int(hoog * 0.55), onder - vast):
        if np.all(breed[y:y + vast] / kern > 1 + speling):
            if (onder - y) < hoog * 0.04:
                return a
            uit = a.copy()
            uit[y:] = 0
            return uit
    return a


def bijsnijden(rgba):
    """Twee uitvoeren van dezelfde uitsnede.

    strak    — precies om het product heen. Voor de sjablonen: de doos is
               liggend, en op een vierkant doek zou hij klein ogen.
    vierkant — op een vierkant doek met lucht eromheen. Voor de webshop,
               waar alle productfoto's dezelfde verhouding moeten hebben.
    """
    a = rgba[:, :, 3]
    ys, xs = np.nonzero(a > 12)
    if len(ys) == 0:
        im = Image.fromarray(rgba)
        return im, im
    strak = Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    lang = max(strak.size)
    marge = int(lang * LUCHT)
    zij = lang + marge * 2
    doek = Image.new('RGBA', (zij, zij), (0, 0, 0, 0))
    doek.paste(strak, ((zij - strak.width) // 2, (zij - strak.height) // 2), strak)
    if zij > MAXZIJ:
        doek = doek.resize((MAXZIJ, MAXZIJ), Image.LANCZOS)
    return strak, doek


def witbalans(rgb, a, aandeel=0.05, klem=(0.6, 1.7)):
    """De kleurzweem uit de opname halen, gemeten aan het product zelf.

    Bram fotografeert 's avonds binnen. De witte 151-doos komt er lila uit: de
    hooglichten meten R167 G187 B250 waar ze neutraal horen te zijn. Dat zit in
    de opname, niet in onze verwerking — de HEIC draagt een Display P3-profiel,
    maar netjes naar sRGB omzetten maakt het niet beter.

    We corrigeren op het product en niet op de hele foto, want de muur en de
    tafel eromheen hebben hun eigen kleur. Van de vijf procent lichtste
    productpixels nemen we de helft die het minst verzadigd is: dat zijn de
    glansplekken op de krimpfolie en die horen neutraal te zijn. De winst die
    ze naar grijs brengt gaat over het hele beeld.

    De klem houdt hem eerlijk. Bij een doos die van zichzelf sterk gekleurd is
    zou een ongeremde correctie de kleur van het product zelf gaan wegpoetsen,
    en dan verkoop je iets anders dan er in de doos zit.
    """
    m = a > 200
    if m.sum() < 500:
        return rgb
    pix = rgb[m].astype(float)
    lum = pix.mean(axis=1)
    licht = pix[lum >= np.percentile(lum, 100 * (1 - aandeel))]
    verz = licht.max(axis=1) - licht.min(axis=1)
    neutraal = licht[verz <= np.percentile(verz, 50)]
    if len(neutraal) < 50:
        return rgb
    k = neutraal.mean(axis=0)
    if k.min() < 1:
        return rgb
    winst = np.clip(k.mean() / k, *klem)
    return np.clip(rgb.astype(float) * winst, 0, 255).astype(np.uint8)


def verwerk(pad):
    im = Image.open(pad)
    im = ImageOps.exif_transpose(im).convert('RGB')
    if max(im.size) > 2600:                       # sneller, en scherp genoeg
        im.thumbnail((2600, 2600), Image.LANCZOS)

    try:
        a, hoe = masker_dubbelslag(im)
        if pathlib.Path(pad).stem in MET_RECHTHOEK:
            recht = masker_rechthoek(a)
            if vulling(recht) > vulling(a):
                hoe += f' ({vulling(a):.0%} -> {vulling(recht):.0%} via rechthoek)'
                a = recht
        if pathlib.Path(pad).stem in MET_VOETSTUK:
            gesneden = voetstuk_weg(a)
            if not np.array_equal(gesneden, a):
                hoe += ', voetstuk weg'
                a = gesneden
        deel = HANDSNEE.get(pathlib.Path(pad).stem)
        if deel:
            rijen = np.nonzero((a > 128).any(axis=1))[0]
            if len(rijen):
                grens = rijen[0] + int((rijen[-1] - rijen[0] + 1) * deel)
                a = a.copy()
                a[grens:] = 0
                hoe += f', met de hand op {deel:.0%} afgesneden'
    except Exception as e:
        print(f'   rembg niet gebruikt ({e.__class__.__name__}), terugval', file=sys.stderr)
        a = masker_terugval(im)
        hoe = 'terugval'

    rgb = witbalans(np.asarray(im), a)
    rgba = np.dstack([rgb, a])
    strak, vierkant = bijsnijden(rgba)
    UIT.mkdir(parents=True, exist_ok=True)
    STRAK.mkdir(parents=True, exist_ok=True)
    naam = pathlib.Path(pad).stem + '.png'
    vierkant.save(UIT / naam)
    strak.save(STRAK / naam)
    print(f'{pathlib.Path(pad).name:<26} -> {naam:<18} '
          f'strak {strak.width}x{strak.height}  vierkant {vierkant.width}x{vierkant.height}  {hoe}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('geef één of meer fotobestanden mee')
    for p in sys.argv[1:]:
        verwerk(p)

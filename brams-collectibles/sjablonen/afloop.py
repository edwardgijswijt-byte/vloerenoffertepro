#!/usr/bin/env python3
"""Afloop en snijmaat toevoegen aan een bestaand ontwerp, zonder het te wijzigen.

    python3 afloop.py bron.pdf doel.pdf

Voor een pdf die op snijmaat is aangeleverd maar zonder afloop — wat Canva
oplevert als je bij het exporteren geen afloop aanzet. De drukker wil A5 plus
3 mm rondom, dus 154x216, met daarin aangegeven waar de snee komt.

Wat dit script wel doet:

- het ontwerp midden op een pagina van 154x216 zetten, op precies 148x210
- de TrimBox op die 148x210 leggen, zodat de preflight van de drukker niet
  hoeft te gokken welk deel afloop is
- de 3 mm afloop vullen door de buitenrand van het ontwerp te spiegelen, wat
  ook is wat de drukker doet als je bij hem "Spiegelen" aanklikt

Wat het **niet** doet is iets aan het ontwerp veranderen. Geen andere marges,
geen andere tekst, geen andere indeling. Dat is het hele punt.

Twee dingen om te weten over het schalen en het spiegelen:

**Het ontwerp wordt 0,1 procent bijgeschaald.** Canva levert hier 148,17 x
209,89 en niet 148 x 210. Dat is een tiende millimeter, met het blote oog niet
te zien, maar de drukker meet het wel en meldt het dan als afwijkend formaat.
Daarom gaat het ontwerp exact op 148x210.

**Gespiegelde afloop is een noodgreep, geen oplossing.** Hij voorkomt een witte
rand als de snijmachine ernaast zit, maar wat er binnen de snijlijn staat blijft
staan waar het staat. Loopt er een dunne lijn tot aan de snijlijn, dan wordt die
lijn na het snijden aan de ene kant breder dan aan de andere — daar helpt geen
afloop tegen. Dat is een kwestie van het ontwerp, niet van het bestand.
"""
import io
import pathlib
import re
import sys

import pymupdf
from PIL import Image

MM = 72 / 25.4
SNIJ_B, SNIJ_H = 148, 210
AFLOOP = 3
PAG_B, PAG_H = SNIJ_B + 2 * AFLOOP, SNIJ_H + 2 * AFLOOP
DPI = 600                      # waarop de randstroken worden gespiegeld


def inktvak(blad, dpi=600):
    """Het vak waar werkelijk inkt staat, in punten op de bronpagina.

    Nodig omdat Canva hier 148,167 mm breed exporteert terwijl het ontwerp
    147,913 breed is: er zit een strookje wit van een kwart millimeter aan de
    rechterkant. Schaal je de hele pagina naar 148 mm, dan komt dat witte
    strookje precies op de snijlijn te liggen en heb je een witte haarlijn langs
    de rand — het probleem dat we juist aan het oplossen zijn. Door op het
    inktvak te schalen valt het wit buiten beeld."""
    import numpy as np
    px = blad.get_pixmap(dpi=dpi)
    a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width, px.n)
    inkt = ~((a[:, :, :3] > 245).all(axis=2))
    if not inkt.any():
        return blad.rect
    ys, xs = np.nonzero(inkt)
    f = 72 / dpi
    return pymupdf.Rect(xs.min() * f, ys.min() * f, (xs.max() + 1) * f, (ys.max() + 1) * f)


def strook(beeld, kant):
    """De buitenste 3 mm van het beeld, gespiegeld naar buiten toe."""
    px = int(round(AFLOOP / 25.4 * DPI))
    b, h = beeld.size
    if kant == 'boven':
        return beeld.crop((0, 0, b, px)).transpose(Image.FLIP_TOP_BOTTOM)
    if kant == 'onder':
        return beeld.crop((0, h - px, b, h)).transpose(Image.FLIP_TOP_BOTTOM)
    if kant == 'links':
        return beeld.crop((0, 0, px, h)).transpose(Image.FLIP_LEFT_RIGHT)
    if kant == 'rechts':
        return beeld.crop((b - px, 0, b, h)).transpose(Image.FLIP_LEFT_RIGHT)
    # hoeken: twee keer spiegelen
    x0 = 0 if 'links' in kant else b - px
    y0 = 0 if 'boven' in kant else h - px
    return (beeld.crop((x0, y0, x0 + px, y0 + px))
            .transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM))


def plaats(blz, beeld, vak):
    buf = io.BytesIO()
    beeld.convert('RGB').save(buf, 'PNG')
    blz.insert_image(vak, stream=buf.getvalue())


def vlak_maken(pdf):
    """Doorzichtige beelden op hun eigen achtergrondkleur zetten.

    De drukker meldt bij elk Canva-bestand dat hij het heeft afgevlakt, en
    waarschuwt dan dat dat "soms voor problemen zorgt met transparante of
    uitgeknipte afbeeldingen": er kan kleurverschil ontstaan tussen het beeld
    en de achtergrond eromheen. Hier staan twee beelden met een alfakanaal, het
    logo en de foto van de Elite Trainer Box.

    Allebei staan ze op een egaal vlak — gemeten is de omgeving van het logo
    voor honderd procent #0D1B2A en die van de doos voor honderd procent
    #16253A. Dan kunnen we ze zelf alvast op die kleur zetten. Het resultaat is
    op het oog hetzelfde, maar er staat geen doorzichtigheid meer in het
    bestand, dus er valt niets meer af te vlakken en er kan geen kleurverschil
    ontstaan.

    Staat een beeld niet op een egale ondergrond, dan blijft het zoals het is:
    dan zou dichtplakken op één kleur juist een rand maken."""
    import numpy as np
    gedaan = 0
    for blz in pdf:
        for inf in blz.get_image_info(xrefs=True):
            xref = inf['xref']
            if not xref or '/SMask' not in (pdf.xref_object(xref, compressed=True) or ''):
                continue
            vak = pymupdf.Rect(inf['bbox'])
            px = blz.get_pixmap(dpi=200, clip=vak + (-6, -6, 6, 6))
            a = np.frombuffer(px.samples, dtype=np.uint8)
            a = a.reshape(px.height, px.width, px.n)[:, :, :3]
            m = max(1, int(2 * 200 / 25.4))
            omheen = np.concatenate([a[:m].reshape(-1, 3), a[-m:].reshape(-1, 3),
                                     a[:, :m].reshape(-1, 3), a[:, -m:].reshape(-1, 3)])
            kleuren, tel = np.unique(omheen, axis=0, return_counts=True)
            if tel.max() / tel.sum() < 0.98:        # geen egale ondergrond
                continue
            grond = tuple(int(v) for v in kleuren[tel.argmax()])

            masker = re.search(r'/SMask (\d+) 0 R', pdf.xref_object(xref, compressed=True))
            if not masker:
                continue
            kleur = Image.open(io.BytesIO(pdf.extract_image(xref)['image'])).convert('RGB')
            alfa = Image.open(io.BytesIO(
                pdf.extract_image(int(masker.group(1)))['image'])).convert('L')
            if alfa.size != kleur.size:
                alfa = alfa.resize(kleur.size, Image.LANCZOS)
            plat = Image.new('RGB', kleur.size, grond)
            plat.paste(kleur, (0, 0), alfa)
            buf = io.BytesIO()
            plat.save(buf, 'PNG')
            blz.replace_image(xref, stream=buf.getvalue())
            gedaan += 1
    return gedaan


def afloop_erbij(bron_pad, doel_pad):
    bron = pymupdf.open(bron_pad)
    uit = pymupdf.open()
    a = AFLOOP * MM
    for nr, blad in enumerate(bron):
        blz = uit.new_page(width=PAG_B * MM, height=PAG_H * MM)

        vak = inktvak(blad)
        px = blad.get_pixmap(dpi=DPI, clip=vak)
        beeld = Image.frombytes('RGB', (px.width, px.height), px.samples)
        binnen = pymupdf.Rect(a, a, (AFLOOP + SNIJ_B) * MM, (AFLOOP + SNIJ_H) * MM)

        # De stroken lopen OVER de snijlijn heen naar binnen. Zonder die
        # overlap blijft er op de naad tussen strook en ontwerp een witte
        # haarlijn van een tiende millimeter staan — twee losse tekeningen die
        # allebei tot precies dezelfde coordinaat lopen dekken die grens niet.
        # Het ontwerp gaat er daarna overheen, dus de overlap is onzichtbaar.
        # `over` laat de stroken over de snijlijn heen naar binnen lopen, `uit`
        # laat ze een halve millimeter buiten de pagina doorlopen. Allebei om
        # dezelfde reden: twee tekeningen die tot precies dezelfde coordinaat
        # lopen dekken die grens niet, en dan blijft er een witte haarlijn van
        # een tiende millimeter staan. Naar binnen is dat onzichtbaar omdat het
        # ontwerp er daarna overheen gaat, naar buiten omdat het buiten de
        # pagina valt.
        R, over, buiten = pymupdf.Rect, 0.5 * MM, 0.5 * MM
        B, H = PAG_B * MM, PAG_H * MM
        plaats(blz, strook(beeld, 'boven'),
               R(binnen.x0, -buiten, binnen.x1, a + over))
        plaats(blz, strook(beeld, 'onder'),
               R(binnen.x0, binnen.y1 - over, binnen.x1, H + buiten))
        plaats(blz, strook(beeld, 'links'),
               R(-buiten, binnen.y0, a + over, binnen.y1))
        plaats(blz, strook(beeld, 'rechts'),
               R(binnen.x1 - over, binnen.y0, B + buiten, binnen.y1))
        for kant, hoek in [
                ('linksboven', R(-buiten, -buiten, a + over, a + over)),
                ('rechtsboven', R(binnen.x1 - over, -buiten, B + buiten, a + over)),
                ('linksonder', R(-buiten, binnen.y1 - over, a + over, H + buiten)),
                ('rechtsonder', R(binnen.x1 - over, binnen.y1 - over,
                                  B + buiten, H + buiten))]:
            plaats(blz, strook(beeld, kant), hoek)

        blz.show_pdf_page(binnen, bron, nr, clip=vak)
        blz.set_trimbox(binnen)
        blz.set_bleedbox(blz.mediabox)

    plat = vlak_maken(uit)
    if plat:
        print(f'  {plat} doorzichtige beelden op hun achtergrondkleur gezet')
    uit.save(doel_pad, garbage=3, deflate=True)
    n = uit.page_count
    uit.close()
    bron.close()
    return n


def main():
    if len(sys.argv) != 3:
        sys.exit('gebruik: afloop.py <bron.pdf> <doel.pdf>')
    bron, doel = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    doel.parent.mkdir(parents=True, exist_ok=True)
    n = afloop_erbij(bron, doel)

    pdf = pymupdf.open(doel)
    blz = pdf[0]
    print(f'{doel}  {n} bladzijde(n)')
    print(f'  pagina   {blz.mediabox.width / MM:.1f} x {blz.mediabox.height / MM:.1f} mm'
          f'   (met afloop)')
    print(f'  snijmaat {blz.trimbox.width / MM:.1f} x {blz.trimbox.height / MM:.1f} mm'
          f'   (A5)')
    pdf.close()


if __name__ == '__main__':
    main()

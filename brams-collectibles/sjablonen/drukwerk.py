#!/usr/bin/env python3
"""Drukklaar A5-drukwerk in de huisstijl, van nul opgebouwd.

    python3 drukwerk.py            -> export/drukwerk/flyer-a5.pdf

**Let op: dit is niet de flyer die gedrukt wordt.** Die is in Canva gemaakt en
wordt met `afloop.py` drukklaar gezet, zodat het ontwerp blijft wat het is.
Wat hier staat is een eigen opzet in dezelfde huisstijl, gemaakt voordat het
Canva-bestand er was. De inhoud onder het logo is grotendeels invulling van
mijn hand en niet van Bram. Gebruik het als vertrekpunt voor nieuw drukwerk,
niet als vervanging van iets wat al ontworpen is.

Waarom dit bestaat: de eerste flyer is in Canva gemaakt en kwam bij de drukker
terug met drie opmerkingen. Twee waren routine, een was een fout. Het bestand
was 161x223 in plaats van 148x210, dus 6,5 mm te groot aan elke kant, en
bovendien met een andere verhouding (1:1,385 tegen 1:1,419 voor A5). Schalen
kan dan niet zonder dat er iets af gaat of wordt uitgerekt.

Wat hier anders gaat:

- **Het formaat ligt vast in millimeters.** De pagina is 154x216: A5 van
  148x210 plus 3 mm afloop rondom. Chromium krijgt dat via `@page size` en
  daarna zetten we met PyMuPDF de TrimBox op de snijmaat. Dat laatste is het
  verschil tussen "hopen dat de drukker het goed meet" en het hem vertellen:
  zijn preflight leest de TrimBox en weet precies waar de snee komt.
- **Het navy loopt door tot de afloopgrens.** De gouden rand was in het
  Canva-ontwerp het buitenste element en liep tot aan de snijlijn. Snijden gaat
  met een tolerantie van een tot twee millimeter die niet aan alle vier de
  zijden gelijk is, dus zo'n rand wordt zichtbaar ongelijk: links dikker dan
  rechts. Hier zit de rand 7 mm binnen de snijlijn.
- **Geen doorzichtigheid en geen slagschaduw.** De drukker vlakt een bestand
  met doorzichtigheid af en waarschuwt dan dat er kleurverschil kan ontstaan
  tussen een uitgeknipt beeld en de achtergrond. Dat probleem vermijden we door
  het niet te maken: alles is vlakke kleur.

Wat dit bestand *niet* doet is naar CMYK omzetten. Chromium levert RGB en
ghostscript staat hier niet. De drukker zet het zelf om — dat deed hij bij het
Canva-bestand ook. De bouwwaarden voor navy en goud staan in
teksten/huisstijl.md; geef die door als de kleur er echt toe doet.
"""
import json
import pathlib
import subprocess
import sys

HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER))
from huisstijl import NAVY, GOLD, CREAM  # noqa: E402

CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'

SNIJ_B, SNIJ_H = 148, 210      # A5, de maat na het snijden
AFLOOP = 3                     # rondom, dus de pagina wordt 154x216
RAND = 7                       # de gouden rand, vanaf de snijlijn naar binnen
VEILIG = 5                     # niets belangrijks dichter bij de snijlijn

PAG_B, PAG_H = SNIJ_B + 2 * AFLOOP, SNIJ_H + 2 * AFLOOP
MM = 72 / 25.4                 # millimeter naar punt, de eenheid van pdf

# Chromium rondt het paginaformaat af op hele punten. Vraag je om 154x216 mm,
# dan komt er 154,18 x 215,90 uit — een tiende millimeter te breed en een tiende
# te kort. Snijd je dat daarna terug naar 154x216, dan wordt de pagina aan de
# bovenkant een tiende millimeter hoger dan wat er geschilderd is, en dat is op
# papier een witte haarlijn langs de snee.
#
# Daarom wordt er ruimer gerenderd dan nodig en pas daarna uitgesneden. Het
# ontwerp staat midden op een doek dat aan alle kanten RUIM mm groter is, en de
# mediabox wordt achteraf midden in dat doek gelegd. Wat Chromium met de laatste
# tiende millimeter doet valt dan binnen het navy in plaats van erbuiten.
RUIM = 4
DOEK_B, DOEK_H = PAG_B + 2 * RUIM, PAG_H + 2 * RUIM


def gezichten(nodig):
    f = json.load(open(HIER / 'fonts-b64.json'))
    return '\n'.join(
        f"@font-face{{font-family:'{n}';font-style:normal;font-weight:{g};"
        f"font-display:block;src:url(data:font/woff2;base64,{f[f'{n}|{g}']}) "
        f"format('woff2');}}" for n, g in nodig)


def datauri(pad):
    import base64
    return ('data:image/png;base64,'
            + base64.b64encode(pathlib.Path(pad).read_bytes()).decode())


def logo_op_navy():
    """Het logo plat op de navy achtergrond, zonder alpha.

    logo.png is rond uitgesneden en heeft dus een alfakanaal. Chromium maakt
    daar in de pdf een SMask van, en dat is precies de doorzichtigheid waar de
    drukker over waarschuwt: "dit zorgt soms voor problemen met transparante of
    uitgeknipte afbeeldingen, bekijk of er geen kleurverschil zit tussen de
    afbeelding en de rest van je achtergrond."

    Het logo staat hier toch al op navy, dus we kunnen het van tevoren op die
    kleur zetten. Het resultaat is op het oog hetzelfde en in de pdf staat een
    gewone RGB-afbeelding zonder masker. Dan valt er niets meer af te vlakken
    en kan er dus ook geen kleurverschil ontstaan."""
    import base64
    import io
    from PIL import Image
    logo = Image.open(HIER / 'logo.png').convert('RGBA')
    grond = Image.new('RGB', logo.size, NAVY)
    grond.paste(logo, (0, 0), logo)
    buf = io.BytesIO()
    grond.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def flyer(inhoud):
    """Het blad. `inhoud` is de html tussen het logo en de voet."""
    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><style>
{gezichten([('Oswald', 500), ('Oswald', 600), ('Oswald', 700),
            ('Poppins', 400), ('Poppins', 500), ('Poppins', 600),
            ('Kaushan', 400)])}
  @page{{ size:{DOEK_B}mm {DOEK_H}mm; margin:0; }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  html{{ background:{NAVY}; }}
  html,body{{ width:{DOEK_B}mm; height:{DOEK_H}mm; position:relative; }}
  body{{
    background:{NAVY};              /* loopt door tot in de afloop */
    -webkit-print-color-adjust:exact; print-color-adjust:exact;
    font-family:'Poppins',Arial,sans-serif; color:{CREAM};
  }}
  .grond{{                          /* navy over het hele doek */
    position:absolute; inset:0; background:{NAVY};
  }}
  .snij{{                           /* het vlak dat overblijft na het snijden */
    position:absolute; left:{RUIM + AFLOOP}mm; top:{RUIM + AFLOOP}mm;
    width:{SNIJ_B}mm; height:{SNIJ_H}mm;
  }}
  .rand{{                           /* de gouden rand, binnen de veilige zone */
    position:absolute; left:{RAND}mm; top:{RAND}mm;
    right:{RAND}mm; bottom:{RAND}mm;
    border:1.1mm solid {GOLD};
  }}
  .blad{{
    position:absolute; left:{RAND + 6}mm; top:{RAND + 6}mm;
    right:{RAND + 6}mm; bottom:{RAND + 6}mm;
    display:flex; flex-direction:column; align-items:center;
    text-align:center;
  }}
  .logo{{ width:46mm; height:46mm; margin-top:3mm; }}
  .leus{{
    font-family:'Kaushan',Georgia,serif; color:{GOLD};
    font-size:13pt; line-height:1.5; margin-top:6mm; max-width:104mm;
  }}
  .onder-leus{{ font-size:10.5pt; font-weight:500; margin-top:3mm; }}
  .knop{{
    margin-top:7mm; background:{GOLD}; color:{NAVY};
    font-family:'Oswald',Arial,sans-serif; font-weight:600;
    font-size:14pt; letter-spacing:.4pt;
    padding:3.4mm 8mm; border-radius:3mm;
  }}
  .plek{{                           /* wat Bram nog moet aanleveren */
    margin-top:8mm; width:100%; padding:9mm 6mm;
    border:0.4mm dashed {GOLD};
    font-family:'Oswald',Arial,sans-serif; font-size:9.5pt;
    letter-spacing:.8pt; color:{GOLD};
  }}
  .plek small{{ display:block; margin-top:2.5mm; font-family:'Poppins',Arial,sans-serif;
    font-size:7.5pt; letter-spacing:0; color:{CREAM}; }}
  .beloften{{
    margin-top:auto; font-family:'Oswald',Arial,sans-serif; font-weight:500;
    font-size:9.5pt; letter-spacing:1.6pt; color:{GOLD}; line-height:2.1;
  }}
  .voet{{
    margin-top:7mm; font-family:'Oswald',Arial,sans-serif;
    font-weight:500; font-size:11.5pt; letter-spacing:1.2pt; color:{GOLD};
  }}
  .fijn{{ font-size:8pt; font-weight:400; color:{CREAM}; opacity:1;
    letter-spacing:0; margin-top:1.5mm; font-family:'Poppins',Arial,sans-serif; }}
</style></head>
<body>
  <div class="grond"></div>
  <div class="snij">
    <div class="rand"></div>
    <div class="blad">
      <img class="logo" src="{logo_op_navy()}" alt="Brams Collectibles">
{inhoud}
    </div>
  </div>
</body></html>
"""


def zetten(html, doel):
    """Chromium maakt de pdf, PyMuPDF zet de snijmaat erin.

    Zonder TrimBox moet de drukker zelf gokken waar de snee komt en meet hij
    de MediaBox — dat is hoe het Canva-bestand als 161x223 werd gelezen. Met
    een TrimBox van 148x210 midden op een MediaBox van 154x216 staat het er
    zwart op wit: dit is de snijmaat, de rest is afloop."""
    import pymupdf as fitz
    bron = doel.with_suffix('.html')
    bron.write_text(html, encoding='utf-8')
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--no-pdf-header-footer', f'--print-to-pdf={doel}',
                    '--virtual-time-budget=8000', str(bron)],
                   check=True, capture_output=True)
    bron.unlink()

    # Het doek uitsnijden op de echte paginamaat. Niet door de mediabox te
    # verschuiven — dan komt de oorsprong niet meer op nul te liggen en gaat
    # elke lezer anders om met de overige kaders — maar door een verse pagina
    # van 154x216 te maken en het doek daar middenop te zetten. show_pdf_page
    # plaatst het als vorm-object, dus de tekst blijft tekst en de vlakken
    # blijven vector.
    doek = fitz.open(doel)
    bron = doek[0].rect
    uit = fitz.open()
    blz = uit.new_page(width=PAG_B * MM, height=PAG_H * MM)
    kant_x = (bron.width - PAG_B * MM) / 2
    kant_y = (bron.height - PAG_H * MM) / 2
    blz.show_pdf_page(fitz.Rect(-kant_x, -kant_y,
                                -kant_x + bron.width, -kant_y + bron.height), doek, 0)
    blz.set_trimbox(fitz.Rect(AFLOOP * MM, AFLOOP * MM,
                              PAG_B * MM - AFLOOP * MM, PAG_H * MM - AFLOOP * MM))
    blz.set_bleedbox(blz.mediabox)
    uit.save(doel.with_suffix('.tmp.pdf'), garbage=3, deflate=True)
    uit.close(); doek.close()
    doel.with_suffix('.tmp.pdf').replace(doel)

    pdf = fitz.open(doel)
    blz = pdf[0]
    def mm(r):
        return f'{r.width / MM:.1f} x {r.height / MM:.1f} mm'
    print(f'{doel.relative_to(HIER.parent.parent)}')
    print(f'  pagina  {mm(blz.mediabox)}   (met afloop)')
    print(f'  snijmaat {mm(blz.trimbox)}   (A5)')
    pdf.close()


# De drie beloften komen uit de loopbalk op de startpagina
# (theme/templates/index.json, sectie "loopbalk"), zodat de flyer en de winkel
# hetzelfde zeggen. De weggeef-actie staat als open vak: hoe je meedoet, tot
# wanneer en wat je kunt winnen is niet af te leiden uit iets wat hier ligt, en
# dat verzin je niet op een flyer die duizend keer gedrukt wordt.
INHOUD = """      <div class="leus">Gestart als fan. Voor de verzamelaar.<br>Voor de community.</div>
      <div class="onder-leus">Voor de strijders op release day.</div>
      <div class="knop">DOE MEE AAN DE WEGGEEF-ACTIE</div>
      <div class="plek">HIER KOMEN DE SPELREGELS
        <small>Hoe je meedoet &middot; tot wanneer &middot; wat er te winnen is</small>
      </div>
      <div class="beloften">
        SEALED UIT EIGEN VOORRAAD<br>
        VERZEKERD VERZONDEN<br>
        OPHALEN OP AFSPRAAK
      </div>
      <div class="voet">BRAMSCOLLECTIBLES.NL
        <div class="fijn">Sealed Pok&eacute;mon TCG</div>
      </div>"""


def main():
    uit = HIER / 'export' / 'drukwerk'
    uit.mkdir(parents=True, exist_ok=True)
    zetten(flyer(INHOUD), uit / 'flyer-a5.pdf')


if __name__ == '__main__':
    main()

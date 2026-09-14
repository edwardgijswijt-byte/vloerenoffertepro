# Huisstijl Brams Collectibles

Alles hieronder komt uit `sjablonen/huisstijl.py` en `theme/assets/brams.css`.
Dat zijn de twee plekken waar de stijl vastligt; wijk je ervan af, dan wijkt de
advertentie af van de webshop.

## Kleuren

| Naam | Hex | Waar |
|---|---|---|
| Navy | `#0D1B2A` | achtergrond, overal |
| Panel | `#16253A` | vlak binnen de rand, iets lichter dan navy |
| Goud | `#C9A24B` | rand, plateau, links |
| Crème | `#F2EFE6` | tekst op navy |
| Grijsblauw | `#8FA0AF` | bijschriften, minder belangrijke tekst |

Twee lichte gouden tinten die niet gelijk zijn, en dat is een slordigheid die
er ooit in is geslopen:

| Naam | Hex | Waar |
|---|---|---|
| Goud licht (sjablonen) | `#E0BE72` | hover op een link in de advertentiesjablonen |
| Goud licht (webshop) | `#E0BEA2` | `--brams-gold-licht` in brams.css |

Als je ergens een lichter goud nodig hebt: neem `#E0BE72`. Die is een echte
lichtere versie van `#C9A24B`; de andere trekt naar roze.

## Verlopen

Het donkere vlak onder de gouden balk van het plateau:

    linear-gradient(180deg, #14243A 0%, #0A1524 100%)

## Letters

| Rol | Letter | Gewicht |
|---|---|---|
| Koppen, cijfers | Oswald | 500 |
| Lopende tekst | Poppins | 600 en 700 |
| Cursief bijschrift | Georgia | italic |

Terugval als de letter er niet is: Oswald → Arial Narrow, Arial. Poppins →
Helvetica Neue, Arial. Georgia → Times New Roman.

## Het logo

`sjablonen/logo.png` — 448x448, transparante achtergrond. In het
Marktplaats-beeld staat hij op 132 px breed, bovenaan gecentreerd, met 46 px
lucht erboven.

## Maatvoering van het huidige Marktplaats-beeld

Doek 1600x1600. Daarbinnen:

- 4 px navy rondom, dan een gouden rand van 7 px
- logo van 132 px, 46 px vanaf de bovenrand
- het product, maximaal 78% van de hoogte en 82% van de breedte
- het gouden plateau: 704 px breed (44% van het doek), balk van 14 px,
  daaronder het verloopvlak van 42 px
- 50 px lucht onderaan

Het plateau is geen rechthoek maar een trapezium. De balk loopt van 2% naar
100% aan de bovenkant en van 0 naar 98% aan de onderkant; het vlak eronder van
0-100% naar 7-93%. Dat geeft het perspectief van een podium.

## Zin die bij de huisstijl hoort

    Gestart als fan · Voor de verzamelaar · Voor de community

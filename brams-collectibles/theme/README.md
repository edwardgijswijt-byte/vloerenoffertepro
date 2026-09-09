# Brams Collectibles — Shopify-thema

Dawn 16.0.0 met de huisstijl van Brams Collectibles erop. Alleen vier dingen
wijken af van de originele Dawn:

| Bestand | Wat |
|---|---|
| `config/settings_data.json` | Kleurenschema's, knoppen, kaarten, radii en merkgegevens |
| `assets/brams.css` | Lettertypes en de accenten die niet in de instellingen passen |
| `assets/logo.png` | Het logo |
| `layout/theme.liquid` | Laadt Google Fonts en `brams.css` na `base.css` |

De rest is onaangeroerde Dawn. Dat is bewust: hoe minder je van het basisthema
afwijkt, hoe soepeler updates gaan.

## Kleurenschema's

| Schema | Achtergrond | Waarvoor |
|---|---|---|
| scheme-1 | `#0D1B2A` navy | Standaard. Hero, de meeste secties |
| scheme-2 | `#16253A` paneel | Kaarten, panelen |
| scheme-3 | `#F2EFE6` cream | Lichte secties, voor afwisseling |
| scheme-4 | `#C9A24B` goud | Accentvlak, sale-badge |
| scheme-5 | `#0A1522` diep navy | Voettekst, uitverkocht-badge |

Wijs per sectie een schema toe in de theme editor. Wissel navy en cream af zodat
de pagina ritme krijgt.

## Lettertypes

Oswald voor koppen, Poppins voor lopende tekst en prijzen. Ze worden geladen via
Google Fonts en overschrijven Dawn's font-picker in `brams.css`.

Wil je in plaats daarvan Shopify's eigen fontlader gebruiken, kies dan Oswald en
Poppins in **Theme settings → Typography** en verwijder de `--font-*`-regels
bovenaan `brams.css`. Dat scheelt één externe verbinding.

## Installeren

**Route A — direct uploaden (snelst).** Maak een zip van de *inhoud* van deze map
(dus `assets/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`,
`templates/` in de root van de zip, niet de map `theme` zelf). Dan in Shopify:
**Online Store → Themes → Add theme → Upload zip file**.

`brams-collectibles-theme.zip` in de bovenliggende map is al zo gemaakt.

**Route B — koppelen aan GitHub.** Shopify verwacht het thema in de **root** van
een repository; submappen worden niet ondersteund. Deze map staat in een
submap, dus daarvoor is een eigen repository nodig waarin deze bestanden in de
root staan. Daarna: **Online Store → Themes → Add theme → Connect from GitHub**.

Vanaf dat moment is elke push naar de gekoppelde branch een update van je winkel.

## Nog te doen in de theme editor

- Logo instellen onder **Theme settings → Logo** (`logo.png` staat al in assets).
- Favicon instellen.
- Instagram- en TikTok-link invullen onder **Social media**.
- Menu's opbouwen onder **Navigation**. Voorstel, gebaseerd op wat werkt in deze
  markt: Pokémon (per set) · Sealed · Singles · Graded · **Inkoop** · Over Bram ·
  Contact.
- De vijf beleidspagina's koppelen onder **Settings → Policies** en in het
  footermenu.

De inkooppagina hoort in het hoofdmenu, niet weggestopt in de footer. Dat is de
kant van het bedrijf waar de marge zit.

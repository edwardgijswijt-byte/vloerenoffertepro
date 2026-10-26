# Shopify-winkel: archief en herstel

Stand van 26 oktober 2026. Bram wil de winkel voorlopig niet openen. Dit archief
bevat alles wat alleen in Shopify stond, zodat de winkel later in een middag
terug te zetten is. Alles wat uit de repo komt (register, teksten, thema,
beleidsteksten, blogartikelen, scripts) staat daar al en staat niet nog eens in
deze map.

## Wat in deze map staat

| Bestand | Inhoud |
|---|---|
| `producten.json` | 24 producten, elk met alles wat `productSet` nodig heeft: titel, handle, type, tags, SEO, prijs, voorraad, gewicht, de volledige beschrijving in HTML en de foto's op volgorde met alt-tekst |
| `afbeeldingen/` | de 41 productfoto's zoals ze in de winkel stonden, genoemd `<sku>-<nummer>.png` |
| `ongebruikt/` | aangeleverde beelden die niet in de winkel zijn gekomen: de Franse 30th-ETB, de 30th-ETB-case (10 stuks), de First Partner-case serie 1, een distributeursbeeld en lege podia |
| `collecties.json` | de 16 collecties met regels, beschrijving en sortering, plus de volgorde van "Uitgelicht" |
| `menu.json` | hoofdmenu en voettekstmenu |
| `verzending.json` | zones, landen en tarieven |
| `winkel.json` | instellingen: domein en DNS, thema, locatie, bedrijfsgegevens |

## Twee dingen die niet kloppen met de winkel zoals hij stond

1. **De gewone Pitch Black ETB** (`BC-PB-ETB`) had in Shopify drie foto's, maar
   twee ervan (`23.png` en `24.png`) tonen de **Pokémon Center-uitvoering**. Die
   horen bij `BC-PB-PCETB`. In het archief staat alleen de zijkant van de gewone
   doos, `BC-PB-ETB-1.png`. Bij herstel dus niet de twee verkeerde terugzetten.
   De voorkant van de gewone doos is er nog niet.
2. **De Paldean Fates-case en de zijkant van de gewone Pitch Black ETB** zijn
   opnieuw gemaakt met `productbeeld.py` uit dezelfde opnames, omdat Shopify's
   CDN vanuit de werkomgeving niet bereikbaar was. Ze zijn gelijk van opzet maar
   niet bit voor bit hetzelfde als wat in de winkel stond.

De beschrijvingen in `producten.json` zijn gegenereerd uit het register en niet
uit Shopify gelezen. Zo zijn alle producten ook gemaakt, maar een handmatige
aanpassing in de beheerkant zou hier ontbreken. Er is niet gecontroleerd of er
zo'n aanpassing was.

## Kosten

Bram betaalt Shopify zolang het plan loopt, ook als de winkel dicht staat achter
het wachtwoord. Het wachtwoord stopt de bezoekers, niet de rekening. De winkel is
op 10 september 2026 aangemaakt op plan Basic.

Wat hieronder staat komt uit externe artikelen over Shopify en is niet bij
Shopify zelf nagekeken. Controleer het in het beheer, onder **Instellingen, Plan**.

- **Winkel deactiveren** (sluiten): de abonnementskosten stoppen. Volgens externe
  bronnen bewaart Shopify de gegevens daarna ongeveer twee jaar. Terugkomen kan
  door een nieuw plan te kiezen. Dit is de manier om geen kosten te hebben.
- **Pause and Build**: de winkel blijft bereikbaar voor de eigenaar, maar er kan
  niet verkocht worden. Er zit een maandbedrag aan, volgens externe bronnen
  ongeveer 9 dollar. Dat is niet nul.
- **Apps** met een eigen abonnement blijven doorbetalen. Er zijn geen apps
  geïnstalleerd, dus daar valt niets te beëindigen.

Het domein `bramscollectibles.nl` staat bij Hostnet, niet bij Shopify. Dat kost
daar door, ook als de winkel gesloten is. Zodra Shopify de winkel sluit wijst het
domein naar een Shopify-pagina die niets meer toont. Zet het domein dan op pauze
of laat het naar een eigen pagina wijzen, of laat de DNS-records staan als je het
snel weer wilt gebruiken.

**Volgorde voor sluiten**

1. Controleer dat dit archief in de repo staat en gepusht is, en dat de werkbranch
   in `main` is opgenomen.
2. Laat Edward in Shopify onder Producten **exporteren naar CSV** en bewaar dat
   bestand. Het is een tweede kopie van alle productgegevens in Shopify's eigen
   formaat, bruikbaar voor een import.
3. Controleer onder Instellingen, Plan wat het abonnement kost en wanneer het
   stopt, en kies dan Winkel deactiveren.
4. Bewaar de gegevens van de Shopify-account (mailadres en wachtwoordbeheer) op
   een plek waar Bram erbij kan. Zonder dat is terugkomen lastig.

## Terugzetten

Er is geen script dat dit in één keer doet: de Shopify-koppeling werkt per
opdracht. Wie dit doet (Claude of iemand met API-toegang) volgt deze volgorde.

1. **Winkel terug.** Plan kiezen in dezelfde account, of een nieuwe winkel
   aanmaken. Bij een nieuwe winkel verandert het interne adres
   (`mwbxzp-qm.myshopify.com`) en moeten verwijzingen daarnaar mee.
2. **Domein.** A-record van `bramscollectibles.nl` naar `23.227.38.65` en een
   CNAME van `www` naar `shops.myshopify.com.` (met de punt) bij Hostnet. Neem het
   A-record niet over uit een lookup van `shops.myshopify.com`.
3. **Thema.** In Shopify de GitHub-repo
   `edwardgijswijt-byte/brams-collectibles-theme`, branch `main`, koppelen en het
   thema publiceren. Alle kleurinstellingen, de startpagina met de carrousel en de
   structured data zitten in die repo. Het logo in de kopregel is handwerk, één
   keer.
4. **Producten.** Voor elk product in `producten.json`:
   - foto's uploaden via `stagedUploadsCreate` en `curl -F`, zie
     `CLAUDE.md`, onderdeel Shopify;
   - `productSet` met titel, `descriptionHtml`, `productType`, `tags`, `seo`, prijs,
     sku, voorraad op locatie "Winkellocatie", `inventoryPolicy: DENY`;
   - `status: ACTIVE` meegeven en achteraf controleren;
   - daarna `publishablePublish` op de kanalen **Webshop** en **Shop**.
5. **Collecties.** Uit `collecties.json`. Alles slim behalve "Uitgelicht".
   Elke collectie heeft een afbeelding nodig, anders zet Dawn een T-shirt neer.
   Gebruik een sjabloonbeeld van een product uit die collectie. Publiceer ze op
   Webshop en Shop.
6. **Uitgelicht.** Handmatige collectie, sortering `MANUAL`, producten in de
   volgorde van `uitgelicht_volgorde`. De carrousel op de startpagina leest deze
   collectie.
7. **Menu.** Uit `menu.json`, met `menuUpdate`.
8. **Verzending.** Uit `verzending.json`: een verzendprofiel met drie zones en
   tarieven op totaalbedrag, plus ophalen als aparte optie.
9. **Blog.** `python3 sjablonen/blog.py` maakt de HTML in `teksten/uit/blog/`; de
   vijf artikelen in de blog `gids` zetten, met de tags uit de bronbestanden.
10. **Pagina's en beleid.** `shopify/paginas/uit/` heeft de HTML voor voorwaarden,
    privacy, herroeping en verzenden. De koppeling mag geen beleid schrijven
    (`write_legal_policies`), dus die plakt iemand zelf onder Instellingen, Beleid.
    Het modelformulier is een aparte pagina met handle `modelformulier-herroeping`.
11. **Instellingen.** Winkelmail op `bramr94@gmail.com`, betaalprovider, btw-keuze,
    adres en contactgegevens (`teksten/bedrijfsgegevens.md`). De open vragen staan
    in `teksten/vragen-bram-opening.md`.
12. **Test.** Proefbestelling met de echte provider, terugbetaling, orderbevestiging
    bij Bram controleren. Het wachtwoord eraf als laatste.

## Wat niet in het archief zit

- **Bestanden in Shopify onder Instellingen, Bestanden:** het kopbeeld
  `brams-hero.png`, de pictogrammen `brams-icoon-*.png` en de collectiebeelden.
  Ze zijn te maken met `sjablonen/hero.py`, `sjablonen/pictogrammen.py` en
  `sjablonen/productbeeld.py`. De carrousel gebruikt het kopbeeld niet meer.
- **Het winkelwachtwoord, de betaalinstellingen en de toegang van de Shopify-account.**
- **Bestellingen en klanten:** die waren er niet.
- **De originele opnames** (`IMG_*.JPG`): die staan in Drive, in een map per sku.
  De uitgesneden versies (`sjablonen/fotos/uitgesneden/`) staan wel in de repo.

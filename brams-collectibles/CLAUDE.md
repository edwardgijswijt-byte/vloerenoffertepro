# Brams Collectibles

Pokémon TCG-handel in Nederland. Winkel op Shopify, advertenties op Marktplaats,
beeld op Instagram en TikTok, drukwerk voor beurzen. Vijftien artikelen, ongeveer
driehonderd dozen — dus veel dubbele.

## Het register is de bron

`register.csv` bevat één regel per **artikel**, niet per doos. Naam, set, aantal,
staat, inkoop, prijs, gewicht, hoogtepunten. Alles wat daarna komt — advertentie‑
teksten, sjabloonbeelden, de prijs op de webshop — wordt hieruit afgeleid.

Verandert een prijs, dan verandert hij hier en nergens anders.

De kolom `set` verwijst naar `teksten/sets/<set>.md`. De kolom `hoogtepunten` is
één veld met `|` ertussen.

## Van foto naar winkel

Vier stappen, in deze volgorde. Draaien vanuit `sjablonen/`.

```
python3 uitsnijden.py fotos/IMG_*.JPG          achtergrond eruit
python3 rechtzetten.py fotos/uitgesneden/strak/IMG_*.png    scheefstand en rand
python3 productbeeld.py <sku> IMG_3754 IMG_3753 ...         sjabloon eromheen
python3 build.py && python3 export.py                       advertenties
```

`uitsnijden.py` levert twee uitvoeren: `uitgesneden/` (vierkant doek, voor waar
een vaste verhouding nodig is) en `uitgesneden/strak/` (precies om het product,
voor de sjablonen). `rechtzetten.py` schrijft naar `uitgesneden/strak/recht/`, en
dat is waar `productbeeld.py` uit leest.

De eerste opname die je aan `productbeeld.py` meegeeft wordt het hoofdbeeld.

## Regels die uit schade zijn geleerd

**Nooit opblazen.** Foto's van 2048×1536 bevatten ongeveer 920 pixels product.
Zet je dat in een kader van 1600 op 88% vulling, dan rek je 1,5× uit en valt het
bij Shopify's zoom uit elkaar. `productbeeld.py` schaalt hooguit 1,15× en laat het
product liever kleiner in het kader staan. Fotografeer liever dichterbij dan dat
je achteraf vergroot.

**Meet de scheefstand.** Een doos op stof staat zelden waterpas. Twee graden zie
je niet op de foto zelf, wel zodra er een recht kader omheen staat. Boven de vier
graden niet corrigeren: dat is dan een hoekopname, geen fout.

**Navy verbergt de uitsnede.** rembg laat een zoom van half-doorzichtige pixels
staan, bijna 4% van het beeld. Tegen wit leest dat als vuil, tegen navy niet.
Daarom staan de productfoto's in het sjabloon en niet los op transparant. Dat is
niet alleen huisstijl, het is ook wat de randen redt.

**Eén fotoserie per artikel, niet per doos.** Twintig identieke sealed dozen zijn
twintig keer hetzelfde plaatje. Let op: de algemene voorwaarden zeggen nu dat
foto's van het daadwerkelijke exemplaar zijn. Bij singles en graded moet dat ook
zo blijven — daar is elk exemplaar anders.

**Map per artikel in Drive, genoemd naar de sku.** Anders ben je een dag kwijt aan
uitzoeken welke `IMG_xxxx.JPG` bij wat hoort.

**Lees de naam van de doos, niet uit de lijst.** Brams invullijst koppelde
fotogroep 9 aan een Pitch Black Elite Trainer Box; op die dozen staat Mega
Evolution Chaos Rising met het Pokemon Center-logo. Een groep verderop klopte
weer wel. Zo'n verschuiving zet een prijs van zestig euro op een artikel dat er
honderden waard is. Zoom in op het logo voordat je een sku aanmaakt.

**Inhoudslijsten van de doos lezen, niet van een webshop.** Fotografeer het
achterpaneel scherp genoeg om te lezen; daar staat precies wat erin zit. Zo kwam
aan het licht dat de Pokémon Center-ETB elf packs heeft en twee Eevee-promo's,
tegen negen en één bij de gewone versie. Dat verschil verklaart de prijs.

## Pdf maken van een pagina

Chromium haalt tijdens het printen niets van Google Fonts op. Een pagina die
zijn lettertypes via een `<link>` laadt valt in de pdf terug op Liberation Sans
en ziet er nergens naar uit. Bak ze in als data-URI; de woff2-bestanden staan in
`sjablonen/fonts-b64.json` (Oswald 500/600/700, Poppins 400/500/600/700).

Een gepubliceerde pagina is bovendien privé en vraagt toegang tot dezelfde
Claude-omgeving. Voor een externe klant is een pdf de weg.

## Teksten staan in lagen

```
teksten/merk.md          verhaal en "verzenden of ophalen" — nooit anders
teksten/sets/<set>.md    de alinea over de set, gedeeld door alles uit die set
register.csv             naam, hoogtepunten, staat, prijs
teksten.py               stelt Marktplaats, socials en webshop samen
```

De settekst hoort bij de **set**, niet bij het product. Chaos Rising ETB, Booster
Box en Bundle delen er één. In de oorspronkelijke Word-bestanden stond die drie
keer overgetypt, en in twee ervan eindigde hij op de verkeerde productnaam. Bij
driehonderd advertenties zie je zoiets niet meer terug.

De teksten zijn van Bram. Niet herschrijven zonder overleg.

## Shopify

Winkel `mwbxzp-qm.myshopify.com`, plan Basic, EUR, Nederland.

De Shopify-koppeling kan producten aanmaken en bijwerken, voorraad zetten en via
GraphQL vrijwel alles wat de Admin API kan.

**Foto's uploaden kan wel, ondanks wat de koppeling zegt.** `create-product` wil
publieke URL's, maar er is een omweg die werkt:

1. `stagedUploadsCreate` vraagt een tijdelijke uploadplek aan
2. het bestand met `curl -F` naar die Google Cloud Storage-URL posten
3. de `resourceUrl` daarna meegeven aan `productCreateMedia` of `update-product`

**Shopify schrijft terug naar GitHub.** Slaat iemand iets op in de thema-editor,
dan pusht Shopify dat naar de repo. Altijd eerst `git fetch` en samenvoegen
voordat je pusht, anders krijg je een afwijzing of overschrijf je zijn werk.
Shopify's kopie kan achterlopen: bij het samenvoegen zette hij een verwijderd
blok terug.

Shopify zet daarbij `current` in `settings_data.json` om van een verwijzing naar
de preset naar de volledige instellingen, en plakt er een commentaarblok boven.
Dat mag daar; een gewone JSON-lezer struikelt erover.

**Wat de koppeling niet mag:** een thema publiceren, en terecht. Dat doe je zelf.

**Controleer de status na elke productbewerking.** Op 10 september sprongen drie
producten van concept naar actief tijdens het bijwerken van hun webshoptekst,
zonder dat daar om gevraagd was. Welke aanroep het deed is niet te achterhalen:
een vierde product kreeg in dezelfde bewerking dezelfde wijziging en bleef wel
op concept. Geef `status` daarom altijd expliciet mee, en kijk erna of hij staat
waar je hem wilt hebben.

Verandert er iets dat je niet hebt gedaan, ga dan niet uit van wat je aanneemt.
Het logboek weet het:

```
query { product(id: "gid://shopify/Product/...") {
  status
  events(first: 20, sortKey: CREATED_AT, reverse: true) {
    nodes { createdAt message appTitle attributeToUser } } } }
```

Wijzigingen van deze koppeling staan er als "Shopify Claude Connector App".

## Thema

Dawn 16.0.0 met vier afwijkingen, verder ongewijzigd zodat Dawn-updates schoon
binnenkomen:

```
config/settings_data.json   vijf kleurenschema's, preset "Brams Collectibles"
assets/brams.css            huisstijllaag over base.css
assets/logo.png             logo, rond uitgesneden met alpha
layout/theme.liquid         Oswald en Poppins, plus brams.css na base.css
```

Het thema staat op twee plekken: hier in `theme/`, en in de losse repo
`edwardgijswijt-byte/brams-collectibles-theme` die aan Shopify hangt. Wijzig hier,
kopieer daarheen, push beide. Deze repo blijft de bron.

Het logo in de kopregel kan niet vanuit het thema worden gezet: Shopify verwacht
daar een bestand uit de winkel, niet uit `assets/`. Dat is handwerk, één keer.

## Collecties

Alles slim, niets handmatig — dan vullen ze zichzelf zodra er een product bijkomt.

```
elite-trainer-boxes    TYPE = Elite Trainer Box
booster-boxes          TYPE = Booster Box
booster-bundles        TYPE = Booster Bundle
premium-collections    TYPE = Premium Collection
displays               TYPE = Display
chaos-rising           TAG = chaos rising
prismatic-evolutions   TAG = prismatic evolutions
scarlet-violet-151     TAG = 151
pitch-black            TAG = pitch black
```

Dus: `soort` in het register wordt het producttype, `set` wordt een tag. Zet die
twee goed bij het aanmaken en het product landt vanzelf in twee collecties.

Elke collectie heeft een eigen afbeelding gekregen. Dat moest: Dawn valt terug
op de eerste productfoto, maar conceptproducten staan niet op de winkel, dus een
collectie met alleen concepten kreeg Dawn's placeholder van een T-shirt. De
sjabloonbeelden van 1600x1600 doen het als tegel prima.

Let op bij `create-collection`: de titel wordt letterlijk overgenomen, dus een
`&` in de titel wordt `&amp;` en de handle `scarlet-amp-violet-151`. De
`descriptionHtml` juist niet — die wil gewone HTML, geen entiteiten. Achteraf
rechtzetten met `collectionUpdate`.

**Aanmaken is niet hetzelfde als op de winkel zetten.** Een nieuwe collectie of
een nieuw product staat op geen enkel verkoopkanaal, ook al zegt de koppeling
dat hij naar de webshop publiceert. Op de winkelkant bestaat hij dan niet, en
Dawn zet er zijn eigen opvulplaatje van een T-shirt neer. Dat kostte een middag
zoeken naar een fout in het thema die er niet was.

Controleren en rechtzetten:

```
query  { collections(first: 20) { nodes { handle resourcePublicationsCount { count } } } }
query  { products(first: 20)    { nodes { handle status resourcePublicationsCount { count } } } }
query  { publications(first: 10) { nodes { id name } } }

mutation { publishablePublish(id: "gid://shopify/Collection/...",
  input: [{publicationId: "<Webshop>"}, {publicationId: "<Shop>"}]) { userErrors { message } } }
```

Staat het aantal op nul, dan is dat de oorzaak — niet het sjabloon. Een product
op concept kan niet gepubliceerd worden; die telt pas mee zodra hij actief is.

## Verzenden

De kosten zijn voor de koper — dat staat in Brams eigen tekst en zo staat het nu
ook in Shopify. In de winkel stond een regel "gratis verzenden boven de 55
euro"; die is eruit, anders ging een doos van 599 euro voor niets de deur uit.

Drempels op ordertotaal, niet op gewicht: het gewicht van een doos plus
verzenddoos is nog niet gewogen, de waarde weten we wel.

```
Nederland     € 6,95    t/m € 100
              € 9,95    € 100 - € 500
              € 14,95   vanaf € 500      extra verzekerd
EU            € 14,95 / € 24,95
Buiten de EU  € 24,95 / € 49,95          invoerrechten voor de koper
Ophalen       gratis, op afspraak
```

Deze bedragen zijn een voorstel op basis van PostNL-tarieven, niet Brams eigen
cijfers. Zodra er een doos op de weegschaal is geweest en er een
verzendcontract ligt, moeten ze langs de meetlat.

## Startpagina

Negen secties, naar het voorbeeld dat Bram aandroeg (pocketgames.nl):

```
image-banner          kopbeeld uit sjablonen/hero.py, kop en een knop
custom-liquid         doorlopende balk met de vaste beloften
collection-list       vier soortcollecties als vierkante tegels
collage               uitgelicht: drie sets, een groot en twee klein
featured-collection   nieuw op voorraad
multicolumn           waarom bij Brams, vier gouden pictogrammen
rich-text             Brams verhaal, ingekort uit teksten/merk.md
collapsible-content   veelgestelde vragen, inclusief de verzendtarieven
newsletter            mailadres voor nieuwe voorraad, op goud
```

Het kopbeeld is een eigen render en geen Dawn-placeholder. `hero.py` zet vier
dozen op een gouden lijn tegen navy en houdt de onderste helft leeg, want daar
zet Shopify de kop en de knop overheen. Verandert de voorraad, dan pas je `RIJ`
aan en upload je het beeld opnieuw als `brams-hero.png`.

De pictogrammen komen uit `sjablonen/pictogrammen.py`: dunne gouden lijnen op
transparant, 240x240. Dawn's multicolumn wil een bestand uit de winkel, dus ze
staan in Shopify Files als `brams-icoon-*.png`. Zonder de regel in `brams.css`
rekt Dawn ze op tot kolombreedte.

**Alleen collecties in de tegels en in het uitgelicht-blok.** Producten die op
concept staan bestaan niet op de winkelkant, dus een tegel die naar zo'n product
wijst blijft leeg. Collecties bestaan altijd en hebben een eigen afbeelding.
Een collectie zonder producten hoort er ook niet in — die leidt naar een lege
pagina. Booster Boxes staat er daarom nog niet bij.

Multicolumn zonder afbeelding is veilig — die laat het beeld gewoon weg.
Collection-list niet: die zet er Dawn's placeholder van een T-shirt neer.
Vandaar de eigen collectiebeelden.

De verzendtarieven staan op twee plekken: in Shopify en in de vragenlijst op de
startpagina. Wijzig je ze, wijzig ze dan allebei.

## Kleuren en letters

```
navy    #0D1B2A    grond en kader
paneel  #16253A    vlak achter de productfoto
goud    #C9A24B    kader, prijs, plateau, voetregel
cream   #F2EFE6    tekst op navy, nooit als groot vlak
```

Oswald bold in kapitalen voor koppen. Poppins voor prijzen, met vaste
cijferbreedte. Georgia voor lopende tekst. Geen Pokémon-logo's in het merk zelf;
productnamen alleen als tekst.

## Prijzen

Een prijs uit de ene set zegt niets over een andere. Ik hield 30 euro voor een
Chaos Rising-bundel aan als maat voor een 151-bundel; die kost 170. Chaos Rising
loopt nog, 151 is uit productie. Wil je weten of een bedrag klopt, kijk dan naar
diezelfde set en niet naar wat er verder in het register staat.

Meet niets op aan foto's van verschillende opnames. Ik heb een doos gemeten door
zijn breedte in pixels af te zetten tegen die van een andere doos, in de aanname
dat beide van dezelfde afstand zijn gefotografeerd. Dat weet je niet, en de
conclusie was dan ook fout. Wil je het formaat weten, leg er een liniaal naast.

Cardmarket is de maat. Noteer per artikel vier getallen met de datum erbij:
trendprijs, 30-daags, 7-daags en 1-daags gemiddelde, plus hoeveel stuks er in de
markt staan.

De trendprijs loopt achter. Bij een dalende markt is het 7-daags gemiddelde wat
kopers vandaag betalen — bij de Prismatic scheelde dat 60 euro.

## Nog open

- Prijs Prismatic staat op € 599, bewust boven de markt. Herzien na zes weken.
- Inkoop staat uit; Bram pakt dat later op. Het blok staat in de geschiedenis.
- De waardevermindering-clausule moet langs een jurist voordat de kassa opengaat.
- Alles tussen `[haken]` moet nog worden ingevuld: KvK, btw-id, adres, contact.
- Verzendtarieven zijn een voorstel; nog wegen en langs een verzendcontract leggen.
- Het menu is nog Dawn's standaard. Bewust: eerst vullen, dan indelen.

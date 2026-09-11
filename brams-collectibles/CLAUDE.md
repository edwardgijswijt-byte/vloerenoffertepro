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
python3 marktplaatsbeeld.py <sku> IMG_3754                  hoofdfoto Marktplaats
python3 build.py && python3 export.py                       advertenties
python3 plaatslijst.py                                      alles om te plaatsen
```

`advertentiepakket.py` maakt één zip waar je per advertentie een map uit pakt:
de foto's genummerd op uploadvolgorde en de tekst ernaast, mappen op vraagprijs
aflopend. Dat is wat je doorstuurt aan wie de advertenties plaatst. De beelden
gaan als JPEG mee en niet als PNG — Marktplaats hercodeert ze toch, en zo is het
pakket 7 MB in plaats van 54.

`controlepagina.py` zet alle artikelen op een rij met hun opnames, de feiten
en de webshoptekst, om door Bram te laten nakijken. Via `drukklaar.py` wordt
dat een pdf die je kunt doorsturen. De opnamenummers staan bij elke foto, dus
als hij er een afkeurt weet je meteen welk bestand eruit moet.

`plaatslijst.py` zet de complete advertenties onder elkaar in
`teksten/uit/_marktplaats-plaatsen.md`, op vraagprijs gesorteerd, met per stuk
het fotobestand erbij. Wat niet compleet is komt onderaan met de reden. Handig
naast het scherm tijdens het plaatsen, en het voorkomt dat je halverwege
ontdekt dat er van één artikel nog geen Marktplaats-beeld is — dat was er bij
vier artikelen niet.

`uitsnijden.py` levert twee uitvoeren: `uitgesneden/` (vierkant doek, voor waar
een vaste verhouding nodig is) en `uitgesneden/strak/` (precies om het product,
voor de sjablonen). `rechtzetten.py` schrijft naar `uitgesneden/strak/recht/`, en
dat is waar `productbeeld.py` uit leest.

De eerste opname die je aan `productbeeld.py` meegeeft wordt het hoofdbeeld.

**Die volgorde staat sinds 11 september in het register, in de kolom
`opnames`.** Daarvoor stond hij nergens: welke opnames in welk product gingen en
in welke volgorde was per artikel een aanroep op de opdrachtregel. Alleen de
kolom `notitie` noemde bij veertien van de achttien artikelen wat IMG-nummers,
in proza, inclusief opnames die juist waren afgekeurd. Opnieuw genereren
betekende dus gokken, en dat is in dit project al een keer misgegaan: ik heb
correcte productbeelden overschreven met verzonnen volgordes, en dat kwam pas
aan het licht door de verschillen per pixel te meten.

De kolom is niet ingevuld naar beste weten maar **teruggerekend door te meten**.
Het sjabloon is deterministisch op renderruis na, dus alle 67 uitsnedes zijn
opnieuw door `productbeeld.py` gehaald en elk bestaand galerijbeeld is daartegen
vergeleken. De juiste bron ligt gemiddeld onder de 5 grijswaarden van het
origineel, de eerstvolgende kandidaat op 10 of meer. Alle 51 beelden kwamen
eruit met een marge van minstens twee keer; geen enkel twijfelgeval.

Dat leverde meteen een correctie op: de notitie bij de Chaos Rising Booster Box
zei dat IMG_3712 "slecht blijft". Gemeten is hij 96 procent gevuld, de beste van
zijn groep, en hij is het hoofdbeeld. Die notitie stamde van vóór de aangepaste
`rand_aantrekken` en klopte niet meer.

`export/marktplaats/` staat sinds diezelfde dag ook in de repo. Die vijftien
beelden staan nergens anders: de advertenties zijn nog niet geplaatst.
`export/webshop/` blijft eruit — 49 MB, en die beelden staan al in Shopify, wat
de duurzame kopie is. Met de kolom `opnames` erbij zijn ze nu wel echt opnieuw
te maken.

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

**Een lichte achtergrond lost niet alles op.** De Destined Rivals-doos is
opnieuw geschoten tegen een lila muur in plaats van zwart satijn, en rembg kreeg
hem alsnog niet heel: het zwarte artwork op de doos las hij als achtergrond, dus
Giovanni en Mewtwo stonden als gaten in het masker. Gaten vullen hielp maar
half — Mewtwo loopt tot aan de doosrand door, en dan is het een inham. Wat wel
werkt: alles wat we fotograferen is een doos, en een doos is convex, dus de
omhullende van het masker. Het stukje achtergrond dat daarbij mee naar binnen
glipt snijdt `masker_omhullende` er weer af op kleur, met de muur bemonsterd in
de bovenhoeken van de opname. Die stap draait alleen als het masker onder de
zeventig procent gevuld blijft, dus aan de goede opnames komt hij niet.

**Lees het etiket op de carton.** Bij een case zit alles wat je moet weten op
het verzendetiket: artikelnummer, de volledige productnaam, hoeveel er in de
doos zit en de releasedatum. De Paldean Fates-case bleek zo `SV4.5 ELITE TRAINER
BOX EN, QTY 10 per Carton`. Wat er per Elite Trainer Box in zit staat er niet
op, en dat mag je dus ook niet invullen naar het gewone Scarlet & Violet-format
— dat is gokken, geen lezen.

**Een fotogroep kan meer dan een doos bevatten.** Fotogroep 9 leek eerst
helemaal Chaos Rising Pokemon Center, omdat de drie opnames die als eerste waren
opgehaald dat waren. Haal je de hele groep op, dan blijken IMG_3733 en IMG_3734
de gewone Pitch Black ETB te zijn — het achterpaneel noemt negen packs en een
Zarude-promo, de andere zes dozen elf packs en twee Fennekin-promo's. Brams
etiket op die groep klopte dus half, en mijn conclusie dat hij zich vergist had
ook. Werk een groep helemaal af voordat je er iets over concludeert.

**Lees de naam van de doos, niet uit de lijst.** Zo'n verschuiving zet een prijs
van zestig euro op een artikel dat er honderden waard is. Zoom in op het logo
voordat je een sku aanmaakt.

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
teksten/merk.md          verhaal, "Pokemon Center" en "verzenden of ophalen"
teksten/sets/<set>.md    de alinea over de set, gedeeld door alles uit die set
register.csv             naam, hoogtepunten, staat, prijs
teksten.py               stelt Marktplaats, socials en webshop samen
```

Het blok **pokemon-center** gaat automatisch mee bij elk artikel met "Pokemon
Center" in de naam. Vier artikelen delen die alinea; je kunt hem dus niet ergens
vergeten.

"En nog veel meer!" komt alleen onder de hoogtepunten bij een ETB of een Premium
Collection. Daar zit meer in dan je opsomt. Bij een bundel, een booster box of
een display is de lijst compleet en zou die regel een leugen zijn. Bram maakt
dat onderscheid zelf ook.

De settekst hoort bij de **set**, niet bij het product. Chaos Rising ETB, Booster
Box en Bundle delen er één. In de oorspronkelijke Word-bestanden stond die drie
keer overgetypt, en in twee ervan eindigde hij op de verkeerde productnaam. Bij
driehonderd advertenties zie je zoiets niet meer terug.

De teksten zijn van Bram. Niet herschrijven zonder overleg.

## Shopify

Winkel op `bramscollectibles.nl` sinds 11 september, plan Basic, EUR,
Nederland. Het interne adres blijft `mwbxzp-qm.myshopify.com` — dat verandert
nooit en is waar je in de API naar verwijst.

Het domein staat bij Hostnet, niet bij Shopify: een A-record op 23.227.38.65
en een CNAME van `www` naar `shops.myshopify.com.` Let op die punt achteraan,
want Hostnet werkt met absolute namen en zonder punt plakt hij er de zone
achter. En neem het A-record niet over uit een lookup van
`shops.myshopify.com`: dat geeft een roterend adres van de loadbalancer
(23.227.38.74 toen we het deden), niet het vaste apex-adres.

Nergens in het thema of in de teksten staat een hardgecodeerd winkeldomein.
De structured data gebruikt `request.origin` en alle interne links zijn
relatief, dus een domeinwissel werkt vanzelf door.

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

Het merkthema is **live**: `brams-collectibles-theme/main` heeft de rol MAIN,
Horizon staat ongepubliceerd. De winkel zit nog wel achter het wachtwoord, dus
publiek is er niets te zien.

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

**Kopieer per bestand, nooit de hele map.** Drie bestanden lopen structureel
uiteen omdat Shopify ze zelf schrijft en er zijn auto-generated-banner boven
plakt: `sections/footer-group.json`, `sections/header-group.json` en
`templates/product.json`. De versie in de themarepo is daar de echte. Kopieer je
de map in zijn geheel, dan draai je iemands werk uit de thema-editor terug.

Doe dus altijd eerst `diff -rq` tussen de twee bomen, kijk per bestand of het
verschil van jou is, en kopieer alleen die.

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
cases                  TYPE = Case
chaos-rising           TAG = chaos rising
prismatic-evolutions   TAG = prismatic evolutions
scarlet-violet-151     TAG = 151
pitch-black            TAG = pitch black
destined-rivals        TAG = destined rivals
ascended-heroes        TAG = ascended heroes
paldean-fates          TAG = paldean fates
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

Negen zichtbare secties plus een onzichtbaar scriptblok:

```
image-banner          kopbeeld uit sjablonen/hero.py, kop en een knop
custom-liquid         doorlopende balk met de vaste beloften
featured-collection   de carrousel: alle dozen, slider op desktop, veegbaar
custom-liquid         het script dat de carrousel laat doorschuiven
collection-list       zes soortcollecties als vierkante tegels
multicolumn           waarom bij Brams, vier gouden pictogrammen
collection-list       zeven setcollecties als vierkante tegels
rich-text             Brams verhaal, ingekort uit teksten/merk.md
collapsible-content   veelgestelde vragen, inclusief de verzendtarieven
newsletter            mailadres voor nieuwe voorraad, op goud
```

**Geen twee blokken naast elkaar met dezelfde vorm.** Dat is de regel waar de
volgorde op rust. De pagina toonde op 11 september vijf blokken achter elkaar
die op elkaar leken — producten, tegels, tegels, tegels, producten — en dat
leest als één muur waar een bezoeker doorheen scrollt zonder iets te zien.

Twee blokken zijn er toen uit gegaan omdat ze dubbel waren:

- **"Nieuw op voorraad"** haalde vier producten uit `all`. Dat zijn dezelfde
  producten die vlak erboven al in de carrousel staan, in dezelfde kaartvorm.
  De titel klopte bovendien niet: er is niets nieuwer dan de rest.
- **"Uitgelicht"** toonde drie sets, die even verderop compleet in "Of zoek op
  set" staan. Een willekeurige greep naast een volledige lijst.

De twee tegelrijen die overblijven staan niet tegen elkaar aan: `waarom` staat
ertussen, en dat is als enige blok vier tekstkolommen met pictogrammen in
plaats van beeldkaarten. Zet je er iets tussen, kies dan een blok met een
andere vorm — niet nog een rij kaarten.

Wil je een blok toevoegen, kijk dan eerst naar de vorm van zijn buren. Een
collection-list naast een collection-list is altijd te veel van hetzelfde, hoe
verschillend de inhoud ook is.

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
pagina. En let op: het gaat om producten die **actief** zijn. Een collectie vol
concepten telt in de beheerkant wel mee maar staat op de winkelkant leeg.

Sinds 11 september staan alle vijftien producten actief en op beide
verkoopkanalen, dus alle veertien collecties zijn gevuld. Het uitgelicht-blok
toont nog maar drie sets terwijl er zeven zijn met actieve producten; daar is
dus ruimte.

Nakijken welke collecties echt gevuld zijn:

```
query { collections(first: 25) { nodes { handle
  products(first: 30) { nodes { status } } } } }
```

Multicolumn zonder afbeelding is veilig — die laat het beeld gewoon weg.
Collection-list niet: die zet er Dawn's placeholder van een T-shirt neer.
Vandaar de eigen collectiebeelden.

De verzendtarieven staan op twee plekken: in Shopify en in de vragenlijst op de
startpagina. Wijzig je ze, wijzig ze dan allebei.

## Vindbaarheid

Twee dingen die los van elkaar staan: klassieke zoekmachines, en
antwoordmachines die een antwoord samenstellen en daarbij bronnen noemen
(ChatGPT, Perplexity, Google's AI-overzichten). Het tweede vraagt om andere
tekst: eerst het antwoord, dan de uitleg.

### Structured data

Dawn levert een dunne Organization, een WebSite met SearchAction, en op
productpagina's `{{ product | structured_data }}`. Dat laatste dekt naam, prijs,
beschikbaarheid en url en verder niets — geen merk, geen sku, geen staat van het
artikel. Voor een winkel die alleen verzegelde dozen verkoopt is juist
`itemCondition` het veld dat telt.

```
snippets/brams-schema.liquid       Organization met @id, Product, BreadcrumbList,
                                   CollectionPage met ItemList, BlogPosting
snippets/brams-faq-schema.liquid   gegenereerd, niet met de hand bijwerken
sjablonen/faqschema.py             genereert dat uit templates/index.json
sjablonen/schemacontrole.py        rendert alles en toetst of het geldige JSON is
```

Draai `schemacontrole.py` na elke wijziging aan het snippet. Hij rendert met
python-liquid voor negen paginatypes en parst de uitvoer als JSON. Dat vangt de
komma te veel die je pas weken later in Search Console terugziet.

Let bij het uitbreiden op de stubs: een filter dat niets doet laat elke toets
slagen. `strip_html` gaf eerst de tekst ongewijzigd terug, dus de controle zei
"geldig" terwijl er HTML in een `description` had kunnen staan. En een
testgeval met alleen een titel bewijst niets over velden die daarna komen —
vandaar dat er nu een artikel mét en een artikel zónder afbeelding in staat.
Een voorwaardelijk veld tussen komma's is precies waar een schema op stukloopt.

Het merk is **Pokémon**, niet Brams Collectibles. Dat laatste is de verkoper en
staat als `seller` in de offer. Ze door elkaar halen is een feitelijke fout die
in de rijke zoekresultaten terechtkomt.

`hasMerchantReturnPolicy` staat er bewust niet in. Het retourbeleid is niet
vastgesteld; een retourtermijn in de structured data zetten die niet in de
voorwaarden staat is een toezegging doen die niemand heeft gedaan.

### robots.txt

Niet aangeraakt, en dat is een besluit. Er circuleren veel stukken die zeggen
dat Shopify AI-crawlers blokkeert en dat je een eigen `robots.txt.liquid` moet
schrijven. Dat klopt in 2026 niet meer: Shopify's standaard laat GPTBot,
ClaudeBot, PerplexityBot, OAI-SearchBot en Google-Extended gewoon toe en
blokkeert alleen admin, cart, checkout en account. Een eigen bestand schrijven
levert dus niets op en kan wel de sitemapverwijzing of de filterregels slopen.

Controleer het wel als er ooit een SEO- of beveiligingsapp bijkomt: die zetten
er soms blanket disallow-regels in.

### Blogartikelen

```
teksten/blog/<naam>.md      bron, met kopblok
sjablonen/blog.py           markdown naar Shopify-HTML plus FAQ-schema
teksten/uit/blog/           uitvoer
```

Elk artikel volgt dezelfde opbouw, en die opbouw is het hele punt:

1. **De samenvatting uit het kopblok** komt vetgedrukt bovenaan. Dat is het
   eerste wat een taalmodel te pakken krijgt, dus die moet op zichzelf een
   antwoord zijn en niet "in dit artikel bespreken we".
2. **"Het korte antwoord"** als eerste kop, veertig tot zestig woorden.
3. Daarna pas uitleg, tabellen en nuance.
4. **"Veelgestelde vragen"** als laatste kop. `blog.py` herkent de vetgedrukte
   regels daaronder als vragen en maakt er FAQPage-schema van. Dat blok moet er
   dus staan, anders krijgt het artikel geen schema.

Shopify laat `<script type="application/ld+json">` in de artikeltekst staan;
dat is nagekeken op het eerste artikel. Dat blok staat sinds 11 september in het
`.html`-bestand zelf. Daarvoor werd het met de hand achter de tekst geplakt bij
het publiceren, en stond het op het punt te verdwijnen zodra de tekst opnieuw
werd gegenereerd. Wat in `teksten/uit/blog/<naam>.html` staat is nu precies wat
er in Shopify hoort te staan — niets meer met de hand erbij.

De vraag- en antwoordtekst in het schema gaat door `plat()`: markdown-opmaak
eruit. Een antwoord waar letterlijk `[booster box](/collections/booster-boxes)`
in staat is wat een antwoordmachine voorleest.

De artikelen staan in de blog `gids`. Vijf stuks, drie soorten: uitleg,
vergelijking en handleiding. Dat is bewust een cluster rond één onderwerp met
onderlinge links — losse artikelen over losse onderwerpen leveren minder op dan
een paar die naar elkaar verwijzen.

Het cluster loopt twee kanten op: de productbeschrijvingen linken naar de
gidsartikelen (`gidslinks()` in `teksten.py`) en de artikelen linken terug naar
collecties en naar elkaar. Achtentwintig links naar veertien bestemmingen.
Link naar **collecties**, niet naar producten: een collectie blijft bestaan, een
uitverkocht product ook maar een opgeheven artikel niet.

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

## Btw en rechtsvorm

Bram verkoopt dit voorlopig als **verkoop uit privécollectie**, dus zonder btw
en zonder btw-identificatienummer. Daarom kunnen de marges zo krap: er gaat geen
btw af. De KvK-inschrijving is aangevraagd maar bewust nog niet gepubliceerd.

Reken dus nergens met btw, en zet geen btw-regel in de webshop of op een
factuur zolang dit geldt. Verandert dit, dan verandert elke prijs mee.

Het gaat om ongeveer 66.000 euro voorraad in circa 300 dozen. Die omvang plus
inkoop, webshop en advertenties is groot genoeg om één keer aan een boekhouder
voor te leggen; dat staat als punt in `teksten/vragen-aan-bram.md`.

## Nog open

- Prijs Prismatic staat op € 599, bewust boven de markt. Herzien na zes weken.
- De waardevermindering-clausule moet langs een jurist voordat de kassa opengaat.
- Adres en contactgegevens staan nog als lege haken in de voorwaarden.
- PostNL-tarieven zijn akkoord bevonden; nog wel een doos wegen.
- De drie First Partner-cases staan nog niet in Shopify: geen foto's, en het is
  niet vastgesteld welke doos serie 1, 2 of 3 is. Dat is een prijsverschil van
  500 om 320.
- De winkel staat nog op wachtwoord. Dat eraf halen is de laatste stap, en pas
  nadat de voorwaarden langs een jurist zijn en het adres is ingevuld.

De openstaande vragen aan Bram staan in `teksten/vragen-aan-bram.md`.

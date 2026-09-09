# Brams Collectibles — landingspagina

Statische site. Eén HTML-bestand plus het logo. Geen build, geen dependencies,
geen server nodig.

```
brams-collectibles/
  index.html          de hele pagina, inclusief CSS
  assets/logo.png     het logo (448 px, transparant)
```

## Publiceren

**Cloudflare Pages** (aanbevolen — gratis tier mag commercieel gebruikt worden):

1. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git
2. Kies deze repository
3. Build command: **leeg laten**
4. Build output directory: `brams-collectibles`
5. Deploy, daarna Custom domains → `bramscollectibles.nl` toevoegen

**Vercel** kan ook, maar let op: het gratis Hobby-plan is uitsluitend voor
niet-commercieel gebruik. Een bedrijfssite vereist Pro.

## Nog invullen

Alle plekken tussen vierkante haken staan klaar om vervangen te worden:

| Plaatshouder | Wat erin komt |
|---|---|
| `[PRIJS]` | Prijs per product (4×) |
| `[MARKTPLAATS-LINK]` | Directe link naar de advertentie (4×) |
| `[MARKTPLAATS-PROFIEL]` | Link naar het verkopersprofiel (2×) |
| `[WHATSAPPNUMMER]` | Nummer in internationaal formaat zonder + of spaties, bijv. `31612345678` |
| `[TELEFOON]` | Nummer zoals je het wilt tonen |
| `[EMAIL]` | E-mailadres |
| `[INSTAGRAM]` / `[TIKTOK]` | Profiel-URL's |
| `[KVK-NUMMER]` / `[BTW-ID]` | Verplicht zodra je zakelijk verkoopt |

Zoek en vervang in `index.html`; verder is er niets aan te passen.

## Wat deze pagina bewust niet doet

Er is **geen winkelwagen en geen betaling**. Daardoor gelden de verplichtingen
voor een webshop hier nog niet: geen algemene voorwaarden, geen
herroepingsinformatie, geen retourbeleid. Verkoop loopt tot die tijd via
Marktplaats.

De hoofdactie is **inkoop**, niet verkoop. Dat is waar de marge zit: sealed
doorverkopen levert 15–20% brutomarge, ingekochte singles ruim het dubbele.

Zodra de Shopify-winkel live gaat verhuist de verkoop daarheen en blijft deze
pagina eventueel staan als merk- en inkooppagina.

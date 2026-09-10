#!/usr/bin/env python3
"""Controlepagina voor de vijf Marktplaats-advertenties."""
import base64, html, json, pathlib

BASIS = pathlib.Path('/home/user/vloerenoffertepro/brams-collectibles')
SJA = BASIS / 'sjablonen'
ADS = json.loads(pathlib.Path('/tmp/ads.json').read_text(encoding='utf-8'))

TITELS = {
    'BC-PE-PCETB': 'Pokémon Prismatic Evolutions Pokémon Center ETB — sealed',
    'BC-CR-ETB':   'Pokémon Chaos Rising Elite Trainer Box — sealed',
    'BC-CR-BND':   'Pokémon Chaos Rising Booster Bundle — sealed, 6 packs',
    'BC-MEV-GREN': 'Pokémon Mega Greninja ex Premium Collection — sealed',
    'BC-151-BND':  'Pokémon Scarlet & Violet 151 Booster Bundle — sealed',
}


def mini(pad, breed=760):
    from PIL import Image
    import io
    im = Image.open(pad).convert('RGB')
    im.thumbnail((breed, breed), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def fotos(sku):
    lijst = [f'marktplaats/{sku}.png']
    web = sorted((SJA / 'export' / 'webshop').glob(f'{sku}-*.png'),
                 key=lambda p: int(p.stem.rsplit('-', 1)[1]))
    lijst += [f'webshop/{p.name}' for p in web[1:]]
    return lijst


blokken = []
for n, a in enumerate(ADS, start=1):
    sku, prijs = a['sku'], a['prijs']
    klaar = bool(prijs)
    titel = TITELS[sku]
    beeld = mini(SJA / 'export' / 'marktplaats' / f'{sku}.png')
    fl = fotos(sku)
    blokken.append(f"""
  <article class="ad" id="ad-{sku}">
    <header class="ad-kop">
      <div class="ad-nr">{n}</div>
      <div class="ad-naam">
        <h2>{html.escape(a['naam'])}</h2>
        <div class="sku">{sku} · {a['gewicht']} g{' · acrylhoes' if a['hoes'] == 'ja' else ''}</div>
      </div>
      <div class="staat {'goed' if klaar else 'mist'}">{'Prijs staat' if klaar else 'Prijs ontbreekt'}</div>
    </header>

    <img class="beeld" src="{beeld}" alt="Marktplaats-hoofdfoto voor {html.escape(a['naam'])}">

    <div class="veld">
      <div class="veld-kop"><span class="label">Titel</span>
        <span class="tel">{len(titel)} tekens</span>
        <button class="kopieer" data-doel="t-{sku}">Kopieer</button></div>
      <div class="waarde" id="t-{sku}">{html.escape(titel)}</div>
    </div>

    <div class="paar">
      <div class="veld">
        <div class="veld-kop"><span class="label">Vraagprijs</span></div>
        <div class="waarde {'' if klaar else 'leeg'}">{('€ ' + prijs + ',-') if klaar else 'nog invullen'}</div>
      </div>
      <div class="veld">
        <div class="veld-kop"><span class="label">Aantal op voorraad</span></div>
        <div class="waarde {'' if a['aantal'] else 'leeg'}">{a['aantal'] or 'nog invullen'}</div>
      </div>
    </div>

    <div class="veld">
      <div class="veld-kop"><span class="label">Advertentietekst</span>
        <span class="tel">{len(a['tekst'])} tekens</span>
        <button class="kopieer" data-doel="b-{sku}">Kopieer</button></div>
      <pre class="waarde tekst" id="b-{sku}">{html.escape(a['tekst'])}</pre>
    </div>

    <div class="veld">
      <div class="veld-kop"><span class="label">Foto's uploaden, in deze volgorde</span></div>
      <ol class="fotolijst">{''.join(f'<li>{html.escape(f)}</li>' for f in fl)}</ol>
    </div>

    <label class="gedaan"><input type="checkbox" id="g-{sku}" data-sku="{sku}">
      <span>Geplaatst op Marktplaats</span></label>
  </article>""")

klaar_n = sum(1 for a in ADS if a['prijs'])

pagina = f"""<title>Vijf advertenties, klaar voor Marktplaats</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Poppins:wght@400;500;600&display=swap">
<style>
  :root{{
    --grond:#F2EFE6; --vlak:#FFFFFF; --inkt:#0D1B2A; --zacht:#5A6A78;
    --lijn:rgba(13,27,42,.14); --lijn-zwak:rgba(13,27,42,.07);
    --accent:#A8863A; --goed:#4E7A5E; --mist:#A9532F;
    --code:#F7F5EF; --schaduw:0 1px 2px rgba(13,27,42,.07);
  }}
  @media (prefers-color-scheme: dark){{
    :root:not([data-theme="light"]){{
      --grond:#0D1B2A; --vlak:#16253A; --inkt:#F2EFE6; --zacht:#8FA0AF;
      --lijn:rgba(242,239,230,.16); --lijn-zwak:rgba(242,239,230,.08);
      --accent:#C9A24B; --goed:#7FB08E; --mist:#D98159;
      --code:#101E31; --schaduw:0 1px 2px rgba(0,0,0,.3);
    }}
  }}
  :root[data-theme="dark"]{{
    --grond:#0D1B2A; --vlak:#16253A; --inkt:#F2EFE6; --zacht:#8FA0AF;
    --lijn:rgba(242,239,230,.16); --lijn-zwak:rgba(242,239,230,.08);
    --accent:#C9A24B; --goed:#7FB08E; --mist:#D98159;
    --code:#101E31; --schaduw:0 1px 2px rgba(0,0,0,.3);
  }}
  *{{box-sizing:border-box;}}
  body{{background:var(--grond); color:var(--inkt);
    font-family:'Poppins','Helvetica Neue',Arial,sans-serif; font-size:15px; line-height:1.55;
    -webkit-font-smoothing:antialiased;}}
  .wrap{{max-width:960px; margin:0 auto; padding:0 20px; padding-block:0 80px;}}
  h1{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:clamp(25px,4vw,35px);
    font-weight:700; text-transform:uppercase; letter-spacing:.012em; margin:0; text-wrap:balance;}}
  header.top{{padding-block:36px 8px;}}
  .onder{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:11px; font-weight:600;
    letter-spacing:.24em; text-transform:uppercase; color:var(--accent); margin-top:6px;}}
  .inleiding{{max-width:62ch; color:var(--zacht); font-size:14px; margin:14px 0 0;}}

  .samenvatting{{display:flex; flex-wrap:wrap; gap:10px; margin-top:22px;}}
  .chip{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:11px; font-weight:600;
    letter-spacing:.14em; text-transform:uppercase; border:1px solid var(--lijn);
    padding:6px 11px; color:var(--zacht);}}
  .chip b{{color:var(--inkt); font-weight:700;}}
  .chip.let{{border-color:var(--mist); color:var(--mist);}}

  .ad{{background:var(--vlak); border:1px solid var(--lijn); box-shadow:var(--schaduw);
    padding:22px; margin-top:26px; display:flex; flex-direction:column; gap:16px;}}
  .ad-kop{{display:flex; align-items:flex-start; gap:14px; flex-wrap:wrap;}}
  .ad-nr{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:13px; font-weight:700;
    color:var(--accent); border:1px solid var(--accent); width:26px; height:26px; flex:none;
    display:grid; place-content:center; font-variant-numeric:tabular-nums;}}
  .ad-naam{{flex:1; min-width:200px;}}
  .ad-naam h2{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:19px; font-weight:700;
    text-transform:uppercase; letter-spacing:.015em; margin:0; line-height:1.15; text-wrap:balance;}}
  .sku{{font-size:12px; color:var(--zacht); font-variant-numeric:tabular-nums; margin-top:3px;}}
  .staat{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:10px; font-weight:600;
    letter-spacing:.16em; text-transform:uppercase; padding:4px 9px; border:1px solid; white-space:nowrap;}}
  .staat.goed{{color:var(--goed); border-color:var(--goed);}}
  .staat.mist{{color:var(--mist); border-color:var(--mist);}}

  .beeld{{width:100%; max-width:100%; height:auto; border:1px solid var(--lijn-zwak);}}

  .veld{{display:flex; flex-direction:column; gap:6px;}}
  .veld-kop{{display:flex; align-items:center; gap:12px;}}
  .label{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:10.5px; font-weight:600;
    letter-spacing:.2em; text-transform:uppercase; color:var(--accent);}}
  .tel{{font-size:11.5px; color:var(--zacht); font-variant-numeric:tabular-nums;}}
  .kopieer{{margin-left:auto; font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:10.5px;
    font-weight:600; letter-spacing:.14em; text-transform:uppercase; cursor:pointer;
    background:transparent; color:var(--accent); border:1px solid var(--accent); padding:4px 11px;}}
  .kopieer:hover{{background:var(--accent); color:var(--vlak);}}
  .kopieer:focus-visible, input:focus-visible{{outline:2px solid var(--accent); outline-offset:2px;}}
  .waarde{{background:var(--code); border:1px solid var(--lijn-zwak); padding:11px 13px;
    font-size:14px; overflow-x:auto;}}
  .waarde.leeg{{color:var(--mist); font-style:italic;}}
  pre.tekst{{margin:0; white-space:pre-wrap; font-family:inherit; font-size:13.5px; line-height:1.6;
    max-height:340px; overflow-y:auto;}}
  .paar{{display:grid; grid-template-columns:1fr 1fr; gap:14px;}}
  .fotolijst{{margin:0; padding-left:22px; font-size:13px; color:var(--zacht);
    font-variant-numeric:tabular-nums;}}
  .fotolijst li{{padding:1px 0;}}
  .gedaan{{display:flex; align-items:center; gap:9px; font-size:13.5px; cursor:pointer;
    border-top:1px solid var(--lijn-zwak); padding-top:14px;}}
  .gedaan input{{width:17px; height:17px; accent-color:var(--goed); cursor:pointer;}}

  .noot{{margin-top:34px; border-left:3px solid var(--accent); background:var(--vlak);
    border:1px solid var(--lijn); border-left:3px solid var(--accent); padding:18px 20px;
    box-shadow:var(--schaduw);}}
  .noot h3{{font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:14px; font-weight:700;
    letter-spacing:.04em; text-transform:uppercase; margin:0 0 8px;}}
  .noot p{{margin:0 0 9px; font-size:13.5px; color:var(--zacht); max-width:66ch;}}
  .noot p:last-child{{margin-bottom:0;}}
  footer{{margin-top:44px; padding-top:18px; border-top:1px solid var(--lijn);
    font-family:'Oswald','Arial Narrow',Arial,sans-serif; font-size:11px; letter-spacing:.24em;
    text-transform:uppercase; color:var(--accent); font-weight:600;}}
  @media (prefers-reduced-motion:reduce){{*{{transition:none !important;}}}}
  @media (max-width:520px){{ .paar{{grid-template-columns:1fr;}} }}
</style>

<div class="wrap">
  <header class="top">
    <h1>Vijf advertenties, klaar voor Marktplaats</h1>
    <div class="onder">Brams Collectibles · nakijken en plaatsen</div>
    <p class="inleiding">Titel en tekst kun je hier kopiëren en rechtstreeks in Marktplaats
      plakken. De foto's staan klaar in de repo; upload ze in de volgorde die per advertentie
      staat, want de eerste is wat mensen in de zoekresultaten zien.</p>
    <div class="samenvatting">
      <span class="chip"><b>5</b> advertenties</span>
      <span class="chip"><b>{klaar_n}</b> met prijs</span>
      <span class="chip let"><b>{5 - klaar_n}</b> zonder prijs</span>
      <span class="chip">Categorie <b>Hobby en Vrije tijd › Verzamelkaartspellen › Pokémon</b></span>
    </div>
  </header>
{''.join(blokken)}

  <div class="noot">
    <h3>Vier van de vijf missen nog een prijs</h3>
    <p>Alleen de Prismatic staat op € 599. De andere vier kun je pas plaatsen als je weet wat
      je vraagt. Kijk per artikel op Cardmarket naar de trendprijs én het 7-daags gemiddelde —
      dat laatste is wat kopers vandaag betalen, en bij de Prismatic scheelde dat zestig euro.</p>
    <p>Twee teksten zijn niet van Bram: de alinea over Scarlet &amp; Violet 151, en die over
      Mega Greninja leunt op de Chaos Rising-tekst. Lees ze na en zet ze in je eigen woorden
      voordat ze live gaan.</p>
    <p>Bij Mega Greninja staat nog geen inhoudslijst. Die is van de achterkant van de doos te
      lezen (foto IMG_3711); zeg het als je die erbij wilt.</p>
  </div>

  <footer>Brams Collectibles</footer>
</div>

<script>
document.querySelectorAll('.kopieer').forEach(function (knop) {{
  knop.addEventListener('click', async function () {{
    var doel = document.getElementById(knop.dataset.doel);
    if (!doel) return;
    var oud = knop.textContent;
    try {{
      await navigator.clipboard.writeText(doel.innerText);
      knop.textContent = 'Gekopieerd';
    }} catch (e) {{
      var r = document.createRange();
      r.selectNodeContents(doel);
      var s = window.getSelection();
      s.removeAllRanges(); s.addRange(r);
      knop.textContent = 'Selecteer en kopieer';
    }}
    setTimeout(function () {{ knop.textContent = oud; }}, 1800);
  }});
}});

var SLEUTEL = 'brams-marktplaats';
var gedaan = {{}};
try {{ gedaan = JSON.parse(localStorage.getItem(SLEUTEL) || '{{}}'); }} catch (e) {{}}
document.querySelectorAll('.gedaan input').forEach(function (vak) {{
  vak.checked = gedaan[vak.dataset.sku] === true;
  vak.addEventListener('change', function () {{
    gedaan[vak.dataset.sku] = vak.checked;
    try {{ localStorage.setItem(SLEUTEL, JSON.stringify(gedaan)); }} catch (e) {{}}
  }});
}});
</script>
"""

doel = pathlib.Path('/tmp/claude-0/-home-user-vloerenoffertepro/0fbb172d-86b0-546f-aebf-1f0b2c2d218f/scratchpad/pagina/marktplaats.html')
doel.parent.mkdir(parents=True, exist_ok=True)
doel.write_text(pagina, encoding='utf-8')
print('geschreven:', doel, len(pagina) // 1024, 'KB')

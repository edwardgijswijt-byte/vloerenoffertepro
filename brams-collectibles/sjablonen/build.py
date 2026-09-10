#!/usr/bin/env python3
"""Advertentiesjablonen voor Marktplaats, Instagram, TikTok en drukwerk."""
import csv, json, pathlib

from huisstijl import (NAVY, PANEL, GOLD, CREAM, MUTED, TAGLINE,
                       logo, frame, plateau, photo_card, pill, footer_mark, doc)

# Het register is de bron voor prijzen. Staat er geen prijs in, dan blijft
# [PRIJS] staan zodat je het meteen ziet.
REGISTER = {r['sku']: r for r in csv.DictReader(
    open(pathlib.Path(__file__).parent.parent / 'register.csv', encoding='utf-8'))}


def bedrag(sku):
    p = REGISTER.get(sku, {}).get('prijs', '')
    return f'&euro; {p},-' if p else '&euro; [PRIJS]'

# ════════════════════ verkoopposten — staand 1080x1350 ════════════════════
def verkoop_staand(titel, prijs, label='Te koop', regel=None, foto=None):
    sub = (f'<div class="gg" style="font-size:23px;color:{CREAM};opacity:.7;text-align:center;line-height:1.4;max-width:44ch">{regel}</div>'
           if regel else '')
    inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:52px 0 30px">{logo(150)}</div>
{photo_card(foto=foto)}
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:16px;padding:32px 60px 42px">
      {pill(label)}
      <div class="os" style="font-size:46px;font-weight:700;line-height:1.06;letter-spacing:.01em;color:{CREAM};
        text-transform:uppercase;text-align:center;text-wrap:balance">{titel}</div>
      {sub}
      <div class="pp" style="font-size:40px;font-weight:700;color:{GOLD};line-height:1;font-variant-numeric:tabular-nums">{prijs}</div>
{footer_mark()}
    </div>"""
    return frame(1080, 1350, inner)


# ═══════════════════════ verkooppost — vierkant 1080 ══════════════════════
def verkoop_vierkant(titel, prijs, label='Te koop', foto=None):
    inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:38px 0 22px">{logo(112)}</div>
{photo_card(radius=26, inset=20, sub='Vaste hoek, vaste belichting', plat_w=470, foto=foto)}
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:13px;padding:22px 50px 30px">
      {pill(label, size=19, px=22, py=11)}
      <div class="os" style="font-size:37px;font-weight:700;line-height:1.05;letter-spacing:.01em;color:{CREAM};
        text-transform:uppercase;text-align:center;text-wrap:balance">{titel}</div>
      <div class="pp" style="font-size:33px;font-weight:700;color:{GOLD};line-height:1;font-variant-numeric:tabular-nums">{prijs}</div>
{footer_mark(size=14, gap=18, rule=88)}
    </div>"""
    return frame(1080, 1080, inner)


# ══════════════════════ story / TikTok 1080x1920 ══════════════════════════
def story(titel, prijs='&euro; [PRIJS]', kop='Nieuw op voorraad', foto=None):
    inner = f"""    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:18px;padding:160px 0 36px">
      {logo(190)}
      <div class="os" style="font-size:24px;font-weight:600;letter-spacing:.3em;color:{GOLD};text-transform:uppercase">{kop}</div>
    </div>
{photo_card(radius=36, inset=28, sub='Staand uitgesneden, product gecentreerd', plat_w=620, foto=foto)}
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:22px;padding:40px 70px 180px">
      <div class="os" style="font-size:60px;font-weight:700;line-height:1.05;letter-spacing:.01em;color:{CREAM};
        text-transform:uppercase;text-align:center;text-wrap:balance">{titel}</div>
      <div class="pp" style="font-size:56px;font-weight:700;color:{GOLD};line-height:1;font-variant-numeric:tabular-nums">{prijs}</div>
      {pill('Link in bio', size=26, px=34, py=17)}
    </div>"""
    return frame(1080, 1920, inner)


# ════════════════════ Marktplaats hoofdfoto 1200x900 ══════════════════════
def marktplaats(titel, prijs='&euro; [PRIJS]',
                regel='Sealed &middot; Verzekerd verzonden &middot; Ophalen mogelijk', foto=None):
    inner = f"""    <div style="flex:none;display:flex;align-items:center;gap:22px;padding:22px 30px 16px">
      {logo(84)}
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:5px">
        <div class="os" style="font-size:30px;font-weight:700;letter-spacing:.02em;color:{CREAM};text-transform:uppercase;line-height:1.05">{titel}</div>
        <div class="os" style="font-size:15px;font-weight:500;letter-spacing:.19em;color:{MUTED};text-transform:uppercase">{regel}</div>
      </div>
      <div class="pp" style="font-size:38px;font-weight:700;color:{GOLD};line-height:1;flex:none;font-variant-numeric:tabular-nums">{prijs}</div>
    </div>
{photo_card(radius=22, inset=16, label='Productfoto', sub='Marktplaats toont hem klein &mdash; houd het beeld rustig', plat_w=520, foto=foto)}
    <div style="flex:none;padding:14px 0 18px">{footer_mark(size=14, gap=18, rule=120)}</div>"""
    return frame(1200, 900, inner)


# ═════════════════════════ inkooppost 1080x1350 ═══════════════════════════
def punt(nr, kop, tekst):
    return f"""      <div style="display:flex;align-items:flex-start;gap:20px">
        <div class="pp" style="width:44px;height:44px;flex:none;border:2px solid {GOLD};border-radius:999px;
          display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:{GOLD}">{nr}</div>
        <div style="display:flex;flex-direction:column;gap:4px;padding-top:4px">
          <div class="os" style="font-size:30px;font-weight:700;letter-spacing:.015em;color:{CREAM};text-transform:uppercase;line-height:1.1">{kop}</div>
          <div class="gg" style="font-size:21px;line-height:1.4;color:{CREAM};opacity:.72">{tekst}</div>
        </div>
      </div>"""

inkoop_inner = f"""    <div style="flex:none;display:flex;justify-content:center;padding:52px 0 26px">{logo(150)}</div>
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:16px;padding:0 62px">
      {pill('Wij kopen op')}
      <div class="os" style="font-size:58px;font-weight:700;line-height:1.02;letter-spacing:.008em;color:{CREAM};
        text-transform:uppercase;text-align:center;text-wrap:balance">Wij kopen jouw Pokémon-verzameling</div>
      <div class="gg" style="font-size:23px;line-height:1.4;color:{CREAM};opacity:.72;text-align:center;max-width:32ch">
        Zolderdoos, verzamelmap of complete collectie. Ik ben benieuwd naar je verhaal en kijk graag mee.</div>
    </div>
    <div style="flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;gap:24px;padding:30px 62px">
{punt(1, 'Taxatie op marktwaarde', 'Kaart voor kaart getoetst aan de actuele Cardmarket-trendprijs.')}
{punt(2, 'Tot [70]% van de waarde', 'Sealed, singles, graded slabs en bulk — alles bespreekbaar.')}
{punt(3, 'Direct betaald per bank', 'Met inkoopovereenkomst op papier. Geen contant gedoe.')}
    </div>
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:14px;padding:0 62px 40px">
      <div class="os" style="font-size:32px;font-weight:700;letter-spacing:.02em;color:{GOLD};text-transform:uppercase;text-align:center">Stuur een foto via DM</div>
{footer_mark()}
    </div>"""

# ═══════════════ visitekaartje 91x61 mm incl. 3 mm afloop (96 dpi) ════════
KV_W, KV_H, BLEED = 344, 231, 11          # 91x61 mm, afloop 3 mm = 11 px

visite_voor = f"""<div style="width:{KV_W}px;height:{KV_H}px;background:{NAVY};padding:{BLEED}px">
  <div style="width:100%;height:100%;border:2px solid {GOLD};display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:9px">
    {logo(88)}
    <div class="os" style="font-size:11px;font-weight:600;letter-spacing:.26em;color:{GOLD};text-transform:uppercase">Pokémon TCG · Nederland</div>
  </div>
</div>"""

visite_achter = f"""<div style="width:{KV_W}px;height:{KV_H}px;background:{NAVY};padding:{BLEED}px">
  <div style="width:100%;height:100%;border:2px solid {GOLD};display:flex;flex-direction:column;
    justify-content:space-between;padding:18px 20px">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">
      <div style="display:flex;flex-direction:column;gap:2px;min-width:0">
        <div class="os" style="font-size:21px;font-weight:700;letter-spacing:.02em;color:{CREAM};text-transform:uppercase;line-height:1.05">Bram Remmerswaal</div>
        <div class="os" style="font-size:9.5px;font-weight:600;letter-spacing:.24em;color:{GOLD};text-transform:uppercase">Eigenaar</div>
      </div>
      {logo(40)}
    </div>
    <div style="display:flex;flex-direction:column;gap:4px">
      <div class="pp" style="font-size:11px;font-weight:600;color:{CREAM};opacity:.9">[06 12 34 56 78]</div>
      <div class="pp" style="font-size:11px;font-weight:600;color:{CREAM};opacity:.9">[bram@bramscollectibles.nl]</div>
      <div class="pp" style="font-size:11px;font-weight:600;color:{GOLD}">[bramscollectibles.nl]</div>
    </div>
    <div style="border-top:1px solid rgba(201,162,75,.5);padding-top:8px">
      <div class="os" style="font-size:8.5px;font-weight:600;letter-spacing:.2em;color:{GOLD};text-transform:uppercase">Gestart als fan · Voor de verzamelaar · Voor de community</div>
    </div>
  </div>
</div>"""

# ══════════════ verzendkaartje A6 111x154 mm incl. afloop ═════════════════
VZ_W, VZ_H = 420, 582

verzend = f"""<div style="width:{VZ_W}px;height:{VZ_H}px;background:{NAVY};padding:{BLEED}px">
  <div style="width:100%;height:100%;border:2px solid {GOLD};display:flex;flex-direction:column;
    align-items:center;padding:20px 22px 18px;gap:11px">
    {logo(78)}
    <div class="os" style="font-size:23px;font-weight:700;letter-spacing:.02em;color:{CREAM};text-transform:uppercase;text-align:center;line-height:1.1">Bedankt voor je aankoop</div>
    <div style="width:58px;height:2px;background:{GOLD}"></div>
    <div class="gg" style="font-size:13px;line-height:1.45;color:{CREAM};opacity:.82;text-align:center">
      Ik weet hoe belangrijk het is. Jouw nieuwe aanwinst is met aandacht ingepakt.
      Klopt er iets niet? Stuur me een bericht, dan lossen we het op.
    </div>
    <div style="flex:1"></div>
    <div style="width:100%;background:{PANEL};border:1.5px solid {GOLD};border-radius:11px;padding:11px 14px;
      display:flex;flex-direction:column;gap:4px;align-items:center">
      <div class="os" style="font-size:14px;font-weight:700;letter-spacing:.05em;color:{GOLD};text-transform:uppercase;text-align:center;line-height:1.15">Zelf een verzameling te koop?</div>
      <div class="gg" style="font-size:12px;line-height:1.35;color:{CREAM};opacity:.8;text-align:center">
        Zolderdoos of complete collectie — stuur een foto, ik kijk graag mee.</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:2px;align-items:center">
      <div class="pp" style="font-size:11.5px;font-weight:600;color:{GOLD}">[bramscollectibles.nl]</div>
      <div class="pp" style="font-size:10.5px;font-weight:600;color:{CREAM};opacity:.75">[@bramscollectibles]</div>
    </div>
    <div class="os" style="font-size:8.5px;font-weight:600;letter-spacing:.19em;color:{GOLD};text-transform:uppercase;text-align:center;line-height:1.5">Gestart als fan<br>Voor de verzamelaar · Voor de community</div>
  </div>
</div>"""

# ═════════════ beursbanner — roll-up 85x200 cm op schaal 1:4 ═════════════
BAN_W, BAN_H = 803, 1890

def ban_punt(kop, tekst):
    return f"""      <div style="display:flex;align-items:flex-start;gap:14px">
        <svg viewBox="0 0 24 24" style="width:26px;height:26px;flex:none;margin-top:4px" fill="none" stroke="{GOLD}"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7"/></svg>
        <div style="display:flex;flex-direction:column;gap:1px">
          <div class="os" style="font-size:31px;font-weight:700;letter-spacing:.02em;color:{CREAM};text-transform:uppercase;line-height:1.1">{kop}</div>
          <div class="gg" style="font-size:19px;line-height:1.35;color:{CREAM};opacity:.7">{tekst}</div>
        </div>
      </div>"""

banner_inner = f"""    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:22px;padding:64px 50px 0">
      {logo(272)}
      <div class="os" style="font-size:30px;font-weight:600;letter-spacing:.3em;color:{GOLD};text-transform:uppercase;text-align:center">Pokémon TCG</div>
    </div>
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:18px;padding:44px 56px 0">
      <div class="os" style="font-size:62px;font-weight:700;line-height:1.02;color:{CREAM};text-transform:uppercase;text-align:center;">Sealed<br>Singles<br>Graded</div>
      <div style="width:120px;height:2px;background:{GOLD}"></div>
      <div class="gg" style="font-size:23px;line-height:1.45;color:{CREAM};opacity:.78;text-align:center;max-width:26ch">
        Voor vrienden regelde ik de mooiste parels. Nu doe ik dat ook voor jou.</div>
    </div>
    <div style="flex:none;display:flex;flex-direction:column;gap:30px;padding:46px 62px 0">
{ban_punt('Wij kopen op', 'Zolderdoos, verzamelmap of complete collectie.')}
{ban_punt('Taxatie op marktwaarde', 'Getoetst aan de actuele Cardmarket-trendprijs.')}
{ban_punt('Direct betaald per bank', 'Met inkoopovereenkomst op papier.')}
    </div>
    <div style="flex:1;min-height:24px"></div>
    <div style="flex:none;display:flex;flex-direction:column;align-items:center;gap:22px;padding:0 56px 76px">
      <div style="background:{GOLD};color:{NAVY};padding:20px 36px;border-radius:999px" class="os">
        <span style="font-size:30px;font-weight:700;letter-spacing:.1em;text-transform:uppercase">[bramscollectibles.nl]</span>
      </div>
      <div class="os" style="font-size:19px;font-weight:600;letter-spacing:.22em;color:{GOLD};text-transform:uppercase;text-align:center;line-height:1.7">Gestart als fan<br>Voor de verzamelaar · Voor de community</div>
    </div>"""

# ═══════════════════════════ merkblad 1400x1000 ═══════════════════════════
def swatch(hexc, naam, gebruik):
    return f"""<div style="display:flex;flex-direction:column;border:1px solid rgba(242,239,230,.2)">
  <div style="height:96px;background:{hexc}"></div>
  <div style="padding:13px 15px;display:flex;flex-direction:column;gap:3px">
    <div class="os" style="font-size:18px;font-weight:700;letter-spacing:.05em;color:{CREAM};text-transform:uppercase">{naam}</div>
    <div class="pp" style="font-size:14px;font-weight:600;letter-spacing:.06em;color:{GOLD}">{hexc}</div>
    <div class="gg" style="font-size:14px;line-height:1.32;color:{CREAM};opacity:.62">{gebruik}</div>
  </div>
</div>"""

merk_inner = f"""    <div style="flex:none;display:flex;align-items:center;gap:24px;padding:34px 42px 20px">
      {logo(92)}
      <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:3px">
        <div class="os" style="font-size:38px;font-weight:700;letter-spacing:.02em;color:{CREAM};text-transform:uppercase">Merkblad</div>
        <div class="gg" style="font-size:18px;color:{CREAM};opacity:.68">Eén systeem voor Marktplaats, Instagram, TikTok, drukwerk en de website.</div>
      </div>
    </div>
    <div style="flex:none;height:2px;background:{GOLD};margin:0 42px"></div>
    <div style="flex:none;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;padding:22px 42px 0">
      {swatch(NAVY, 'Navy Blue', 'Ondergrond en kader. De basis van alles.')}
      {swatch(GOLD, 'Brams Gold', 'Accent: kader, prijs, pill, plateau, voetregel.')}
      {swatch(CREAM, 'Cream', 'Tekst op navy. Nooit als groot vlak.')}
      {swatch(PANEL, 'Paneel', 'Vlak achter de productfoto in de kaart.')}
    </div>
    <div style="flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:22px 42px 30px">
      <div style="display:flex;flex-direction:column;gap:14px;border:1px solid rgba(242,239,230,.2);padding:20px 22px">
        <div class="os" style="font-size:13px;font-weight:600;letter-spacing:.22em;color:{GOLD};text-transform:uppercase">Letters</div>
        <div style="display:flex;flex-direction:column;gap:2px">
          <div class="os" style="font-size:34px;font-weight:700;letter-spacing:.015em;color:{CREAM};text-transform:uppercase;line-height:1.05">Chaos Rising ETB</div>
          <div class="pp" style="font-size:13px;font-weight:600;letter-spacing:.1em;color:{CREAM};opacity:.55;text-transform:uppercase">Oswald Bold — koppen, altijd kapitaal</div>
        </div>
        <div style="height:1px;background:rgba(242,239,230,.16)"></div>
        <div style="display:flex;flex-direction:column;gap:2px">
          <div class="pp" style="font-size:34px;font-weight:700;color:{GOLD};line-height:1">&euro; 54,95</div>
          <div class="pp" style="font-size:13px;font-weight:600;letter-spacing:.1em;color:{CREAM};opacity:.55;text-transform:uppercase">Poppins Bold — prijzen en knoppen</div>
        </div>
        <div style="height:1px;background:rgba(242,239,230,.16)"></div>
        <div style="display:flex;flex-direction:column;gap:3px">
          <div class="gg" style="font-size:18px;line-height:1.4;color:{CREAM};opacity:.8">Lopende tekst in Georgia — leesbaar en op elk apparaat aanwezig.</div>
          <div class="pp" style="font-size:13px;font-weight:600;letter-spacing:.1em;color:{CREAM};opacity:.55;text-transform:uppercase">Georgia — beschrijvingen</div>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px;border:1px solid rgba(242,239,230,.2);padding:20px 22px">
        <div class="os" style="font-size:13px;font-weight:600;letter-spacing:.22em;color:{GOLD};text-transform:uppercase">Vaste regels</div>
        <div class="gg" style="font-size:18px;line-height:1.4;color:{CREAM};opacity:.82">Elke foto uit dezelfde fotobooth: navy achterwand, licht van twee kanten, vaste hoek.</div>
        <div class="gg" style="font-size:18px;line-height:1.4;color:{CREAM};opacity:.82">Product staat op het gouden plateau. Gouden kader rondom, logo bovenaan gecentreerd.</div>
        <div class="gg" style="font-size:18px;line-height:1.4;color:{CREAM};opacity:.82">Geen Pokémon-logo's of -illustraties in het merk zelf. Productnamen alleen als tekst.</div>
        <div class="gg" style="font-size:18px;line-height:1.4;color:{CREAM};opacity:.82">Drukwerk met 3 mm afloop: visitekaartje 85×55 mm, verzendkaart A6.</div>
        <div style="margin-top:auto;border-top:1px solid rgba(201,162,75,.4);padding-top:12px">
          <div class="os" style="font-size:15px;font-weight:600;letter-spacing:.22em;color:{GOLD};text-transform:uppercase;line-height:1.6">Gestart als fan<br>Voor de verzamelaar<br>Voor de community</div>
        </div>
      </div>
    </div>"""

# ═══════════════ eerste echte product: Prismatic Evolutions ══════════════
# De uitgesneden foto's komen uit uitsnijden.py. Staat een bestand er nog niet,
# dan houdt het sjabloon de gestippelde plek — bouwen kan dus altijd.
PRIS_TITEL = 'Prismatic Evolutions Pok&eacute;mon Center Elite Trainer Box'
PRIS_KORT = 'Prismatic Evolutions Pok&eacute;mon Center ETB'
# Inhoud van het achterpaneel van de doos zelf gelezen (IMG_3756):
# 11 packs, twee full-art Eevee-promo's waarvan een met Pokémon Center-logo.
PRIS_REGEL = ('11 booster packs &middot; 2 full-art promo&rsquo;s van Eevee<br>'
              'Sealed &middot; in acryl beschermhoes')


def foto(naam, vierkant=False):
    """Pad naar een uitgesneden foto, of None als die er nog niet is.

    strak    — precies om het product heen, voor de sjablonen.
    vierkant — op een vierkant doek, voor de webshop.
    """
    tak = 'fotos/uitgesneden' if vierkant else 'fotos/uitgesneden/strak'
    pad = pathlib.Path(tak) / f'{naam}.png'
    return str(pad) if pad.exists() else None


# Welke opname waar heen gaat. Zes foto's van hetzelfde exemplaar:
#   3752/3753 schuin van voren, 3754 recht van voren,
#   3755/3757 zijkant, 3756 achterkant met de inhoudslijst.
PRIS_VOOR = foto('IMG_3754')            # hoofdbeeld: recht van voren
PRIS_HOEK = foto('IMG_3753')            # schuin, geeft diepte op story
PRIS_ACHTER = foto('IMG_3756')          # achterkant met inhoud
PRIS_ZIJ = foto('IMG_3755')             # zijkant
PRIS_WEB = foto('IMG_3754', vierkant=True)

# ── website: product op transparant, zonder kader ──
def web_los(foto_pad, zij=1600):
    """Alleen het product, transparant. Voor de webshop en de landingspagina,
    waar de site zelf al de achtergrond levert."""
    binnen = (f'<img src="{foto_pad}" alt="" style="max-width:86%;max-height:86%;width:auto;height:auto;'
              f'object-fit:contain">' if foto_pad else
              f'<div class="pp" style="font-size:20px;color:{MUTED}">nog geen uitgesneden foto</div>')
    return f"""<div style="width:{zij}px;height:{zij}px;background:transparent;
  display:flex;align-items:center;justify-content:center">
  {binnen}
</div>"""


# ── website: product op navy met plateau, vierkant ──
def web_navy(foto_pad, zij=1600):
    binnen = (f'<img src="{foto_pad}" alt="" style="max-width:80%;max-height:100%;width:auto;height:auto;'
              f'object-fit:contain;filter:drop-shadow(0 22px 34px rgba(0,0,0,.55))">' if foto_pad else
              f'<div class="pp" style="font-size:20px;color:{MUTED}">nog geen uitgesneden foto</div>')
    return f"""<div style="width:{zij}px;height:{zij}px;background:{NAVY};display:flex;flex-direction:column;
  align-items:center;justify-content:flex-end;padding:0 0 {int(zij*0.09)}px">
  <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px">
    {binnen}
  </div>
{plateau(int(zij*0.52), bar=int(zij*0.011), body=int(zij*0.034))}
</div>"""


# ─────────────────────────────────────────────────────────── schrijven ──
bestanden = {
  'Main.dc.html':         verkoop_staand('Chaos Rising Elite Trainer Box', '&euro; [PRIJS]',
                                          regel='9 booster packs · exclusieve full-art foil promo van Fennekin'),
  'BoosterBox.dc.html':   verkoop_staand('Chaos Rising Booster Box', '&euro; [PRIJS]',
                                          regel='36 booster packs · Greninja in de hoofdrol'),
  'Bundle.dc.html':       verkoop_vierkant('Chaos Rising Booster Bundle', '&euro; [PRIJS]'),
  'PitchBlack.dc.html':   verkoop_staand('Pitch Black Elite Trainer Box', '&euro; [PRIJS]',
                                          regel='9 booster packs · exclusieve full-art foil promo van Zarude'),
  'Story.dc.html':        story('Chaos Rising Elite Trainer Box'),
  'Marktplaats.dc.html':  marktplaats('Chaos Rising Elite Trainer Box'),
  'Inkoop.dc.html':       frame(1080, 1350, inkoop_inner),
  'Banner.dc.html':       frame(BAN_W, BAN_H, banner_inner, border=8, inset=4),
  'VisiteVoor.dc.html':   visite_voor,
  'VisiteAchter.dc.html': visite_achter,
  'Verzendkaart.dc.html': verzend,
  'Merkblad.dc.html':     frame(1400, 1000, merk_inner),

  # Prismatic Evolutions — de vier kanalen
  'PrismaticFeed.dc.html':   verkoop_staand(PRIS_KORT, bedrag('BC-PE-PCETB'), regel=PRIS_REGEL, foto=PRIS_VOOR),
  'PrismaticVierkant.dc.html': verkoop_vierkant(PRIS_KORT, bedrag('BC-PE-PCETB'), foto=PRIS_VOOR),
  'PrismaticStory.dc.html':  story(PRIS_KORT, bedrag('BC-PE-PCETB'), foto=PRIS_HOEK or PRIS_VOOR),
  'PrismaticMarkt.dc.html':  marktplaats(PRIS_KORT, bedrag('BC-PE-PCETB'), foto=PRIS_VOOR),
  'PrismaticWeb.dc.html':    web_los(PRIS_WEB),
  'PrismaticWebNavy.dc.html': web_navy(PRIS_WEB),
}
out = pathlib.Path('.')
for naam, body in bestanden.items():
    (out / naam).write_text(doc(body), encoding='utf-8')

canvas = {
  "pages": [
    {"id": "page-1", "name": "Online"},
    {"id": "page-2", "name": "Drukwerk"},
    {"id": "page-3", "name": "Prismatic Evolutions"}
  ],
  "artboards": [
    {"file": "Main.dc.html",         "page": "page-1", "x": 0,    "y": 0,    "w": 1080, "h": 1350, "title": "Chaos Rising ETB — staand"},
    {"file": "BoosterBox.dc.html",   "page": "page-1", "x": 1200, "y": 0,    "w": 1080, "h": 1350, "title": "Chaos Rising Booster Box"},
    {"file": "PitchBlack.dc.html",   "page": "page-1", "x": 2400, "y": 0,    "w": 1080, "h": 1350, "title": "Pitch Black ETB"},
    {"file": "Inkoop.dc.html",       "page": "page-1", "x": 3600, "y": 0,    "w": 1080, "h": 1350, "title": "Inkoop — wij kopen op"},
    {"file": "Story.dc.html",        "page": "page-1", "x": 4800, "y": 0,    "w": 1080, "h": 1920, "title": "Story / TikTok-cover"},
    {"file": "Bundle.dc.html",       "page": "page-1", "x": 0,    "y": 2100, "w": 1080, "h": 1080, "title": "Booster Bundle — vierkant"},
    {"file": "Marktplaats.dc.html",  "page": "page-1", "x": 1200, "y": 2100, "w": 1200, "h": 900,  "title": "Marktplaats hoofdfoto"},
    {"file": "Merkblad.dc.html",     "page": "page-1", "x": 2520, "y": 2100, "w": 1400, "h": 1000, "title": "Merkblad"},

    {"file": "PrismaticFeed.dc.html",     "page": "page-3", "x": 0,    "y": 0, "w": 1080, "h": 1350, "title": "Instagram feed 4:5"},
    {"file": "PrismaticVierkant.dc.html", "page": "page-3", "x": 1200, "y": 0, "w": 1080, "h": 1080, "title": "Instagram vierkant 1:1"},
    {"file": "PrismaticStory.dc.html",    "page": "page-3", "x": 2400, "y": 0, "w": 1080, "h": 1920, "title": "Story / TikTok 9:16"},
    {"file": "PrismaticMarkt.dc.html",    "page": "page-3", "x": 3600, "y": 0, "w": 1200, "h": 900,  "title": "Marktplaats hoofdfoto"},
    {"file": "PrismaticWeb.dc.html",      "page": "page-3", "x": 3600, "y": 1000, "w": 1600, "h": 1600, "title": "Webshop — transparant"},
    {"file": "PrismaticWebNavy.dc.html",  "page": "page-3", "x": 5320, "y": 1000, "w": 1600, "h": 1600, "title": "Webshop — op navy"},

    {"file": "Banner.dc.html",       "page": "page-2", "x": 0,   "y": 0,   "w": BAN_W, "h": BAN_H, "title": "Beursbanner 85×200 cm (schaal 1:4)"},
    {"file": "VisiteVoor.dc.html",   "page": "page-2", "x": 920, "y": 0,   "w": KV_W,  "h": KV_H,  "title": "Visitekaartje voor"},
    {"file": "VisiteAchter.dc.html", "page": "page-2", "x": 920, "y": 360, "w": KV_W,  "h": KV_H,  "title": "Visitekaartje achter"},
    {"file": "Verzendkaart.dc.html", "page": "page-2", "x": 1380,"y": 0,   "w": VZ_W,  "h": VZ_H,  "title": "Verzendkaart A6"}
  ],
  "annotations": [
    {"id": "prijzen", "page": "page-1", "x": 0, "y": -210, "w": 1080,
     "text": "[PRIJS] staat overal als plek voor je eigen bedrag. Productnamen en regels komen uit je advertentieteksten.\nHet gouden plateau staat onder elke productfoto, zoals in je eigen sjabloon."},
    {"id": "inkoop-nb", "page": "page-1", "x": 3600, "y": -210, "w": 1080,
     "text": "Deze post vult je inkoop. Bevestig het percentage — nu staat er [70]."},
    {"id": "druk-nb", "page": "page-2", "x": 0, "y": -230, "w": 803,
     "text": "Drukwerk. De banner staat op schaal 1:4 (85x200 cm) — geef hem zo aan de drukker, die schaalt naar ware grootte.\nVisitekaartje en verzendkaart hebben 3 mm afloop rondom: het kader mag tot aan de snijrand doorlopen."},
    {"id": "contact-nb", "page": "page-2", "x": 920, "y": -230, "w": 344,
     "text": "Alles tussen [haken] vervangen: telefoon, e-mail, domein en je Instagram-naam."}
  ],
  "launch": {"view": "canvas", "page": "page-3"}
}
(out / 'canvas.json').write_text(json.dumps(canvas, indent=2, ensure_ascii=False), encoding='utf-8')

for p in sorted(out.glob('*.dc.html')):
    print(f"{p.name:<24} {p.stat().st_size//1024:>4} KB")

#!/usr/bin/env python3
"""De huisstijllaag: kleuren, letters en de bouwstenen van het sjabloon.

Op de maatvoering van Brams eigen advertentiesjabloon (810x1013 pt),
inclusief het gouden plateau. Zowel de advertenties (build.py) als de
productfoto's voor de webshop (productbeeld.py) tekenen hiermee, zodat er
maar één plek is waar het kader, het logo en het plateau vastliggen."""
import json, pathlib

F = json.load(open('fonts-b64.json'))
NAVY, PANEL, GOLD, CREAM = '#0D1B2A', '#16253A', '#C9A24B', '#F2EFE6'
MUTED = '#8FA0AF'
TAGLINE = 'Gestart als fan · Voor de verzamelaar · Voor de community'

FONTS = f"""    @font-face{{font-family:'Oswald';font-style:normal;font-weight:200 700;font-display:block;
      src:url(data:font/woff2;base64,{F['Oswald|500']}) format('woff2');}}
    @font-face{{font-family:'Poppins';font-style:normal;font-weight:600;font-display:block;
      src:url(data:font/woff2;base64,{F['Poppins|600']}) format('woff2');}}
    @font-face{{font-family:'Poppins';font-style:normal;font-weight:700;font-display:block;
      src:url(data:font/woff2;base64,{F['Poppins|700']}) format('woff2');}}"""

BASE = f"""    *{{box-sizing:border-box;}}
    body{{margin:0;-webkit-font-smoothing:antialiased;}}
    a{{color:{GOLD};text-decoration:none;}} a:hover{{color:#E0BE72;}}
    .os{{font-family:'Oswald','Arial Narrow',Arial,sans-serif;}}
    .pp{{font-family:'Poppins','Helvetica Neue',Arial,sans-serif;}}
    .gg{{font-family:Georgia,'Times New Roman',serif;}}
    img{{display:block;max-width:100%;}}"""


def logo(w):
    return f'<img src="logo.png" alt="Brams Collectibles" style="width:{w}px;height:{w}px">'


def frame(w, h, inner, border=6, inset=3):
    return f"""<div style="width:{w}px;height:{h}px;background:{NAVY};padding:{inset}px">
  <div style="width:100%;height:100%;border:{border}px solid {GOLD};display:flex;flex-direction:column">
{inner}
  </div>
</div>"""


def plateau(w=578, bar=11, body=34):
    """Het gouden podium onder de productfoto."""
    return f"""      <div style="width:{w}px;max-width:82%;margin:0 auto;flex:none">
        <div style="height:{bar}px;background:{GOLD};clip-path:polygon(2% 0, 100% 0, 98% 100%, 0 100%)"></div>
        <div style="height:{body}px;background:linear-gradient(180deg,#14243A 0%,#0A1524 100%);
          clip-path:polygon(0 0, 100% 0, 93% 100%, 7% 100%)"></div>
      </div>"""


def photo_card(radius=32, inset=25, met_plateau=True, label='Sleep hier de productfoto',
               sub='Vaste hoek, vaste belichting, navy achterwand', plat_w=578,
               foto=None, foto_breed=88):
    """De fotokaart. Zonder foto de gestippelde plek, met foto het uitgesneden
    product dat op het gouden plateau staat."""
    plat = plateau(plat_w) if met_plateau else ''
    if foto:
        return f"""    <div style="flex:1;min-height:0;background:{PANEL};border:3px solid {GOLD};border-radius:{radius}px;
      padding:{inset}px;display:flex;flex-direction:column;justify-content:flex-end">
      <div style="flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding-bottom:4px">
        <img src="{foto}" alt="" style="max-height:100%;max-width:{foto_breed}%;width:auto;height:auto;
          object-fit:contain;filter:drop-shadow(0 16px 24px rgba(0,0,0,.5))">
      </div>
{plat}
    </div>"""
    return f"""    <div style="flex:1;min-height:0;background:{PANEL};border:3px solid {GOLD};border-radius:{radius}px;
      padding:{inset}px;display:flex;flex-direction:column;justify-content:flex-end">
      <div style="flex:1;min-height:0;border:1.5px dashed rgba(242,239,230,.3);border-radius:{max(radius-11,8)}px;
        display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">
        <svg viewBox="0 0 24 24" style="width:42px;height:42px" fill="none" stroke="{CREAM}" stroke-opacity=".55"
          stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="4.5" width="18" height="15" rx="2.5"/><circle cx="8.6" cy="9.8" r="1.7"/>
          <path d="m3.6 17.4 4.9-4.6 3.4 3.1 3.6-3.4 5 4.7"/>
        </svg>
        <div class="pp" style="font-size:21px;font-weight:600;color:{CREAM};opacity:.85;text-align:center">{label}</div>
        <div class="gg" style="font-size:18px;color:{CREAM};opacity:.5;font-style:italic;text-align:center">{sub}</div>
      </div>
{plat}
    </div>"""


def pill(text, size=22, px=26, py=13):
    return (f'<div class="os" style="background:{GOLD};color:{NAVY};font-size:{size}px;font-weight:700;'
            f'letter-spacing:.16em;text-transform:uppercase;padding:{py}px {px}px;border-radius:999px;'
            f'align-self:center;line-height:1">{text}</div>')


def footer_mark(size=16, gap=22, rule=110, tekst='Brams Collectibles'):
    return f"""    <div style="display:flex;align-items:center;justify-content:center;gap:{gap}px;flex:none">
      <div style="width:{rule}px;height:1px;background:{GOLD};opacity:.75"></div>
      <div class="os" style="font-size:{size}px;font-weight:600;letter-spacing:.26em;color:{GOLD};text-transform:uppercase;white-space:nowrap">{tekst}</div>
      <div style="width:{rule}px;height:1px;background:{GOLD};opacity:.75"></div>
    </div>"""


def doc(body):
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <style>
{FONTS}
{BASE}
  </style>
</helmet>
{body}
</x-dc>
</body>
</html>
"""



#!/usr/bin/env python3
"""Bestanden naar Shopify's tijdelijke uploadplek posten.

    python3 naarshopify.py doelen.json

Shopify's koppeling wil publieke URL's voor productfoto's, en die hebben we
niet. De omweg: vraag met stagedUploadsCreate een tijdelijke plek aan, post
het bestand daarheen, en geef de resourceUrl daarna door aan
productCreateMedia. Dat aanvragen gaat via de koppeling; het posten kan
alleen hiervandaan, en dat is wat dit script doet.

doelen.json is wat stagedUploadsCreate teruggaf, met per doel het lokale
bestand erbij:

    [{"bestand": "BC-CR-ETB-1.png",
      "parameters": [{"name": "key", "value": "..."}, ...]}]
"""
import json, pathlib, subprocess, sys

URL = 'https://shopify-staged-uploads.storage.googleapis.com/'


def post(doel):
    velden = []
    for p in doel['parameters']:
        velden += ['-F', f"{p['name']}={p['value']}"]
    velden += ['-F', f"file=@{doel['bestand']}"]
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                        '-X', 'POST', URL] + velden, capture_output=True, text=True)
    return r.stdout.strip()


if __name__ == '__main__':
    doelen = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    fout = 0
    for d in doelen:
        code = post(d)
        print(f"{d['bestand']:<24} HTTP {code}")
        fout += code != '201'
    sys.exit(1 if fout else 0)

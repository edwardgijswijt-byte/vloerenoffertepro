#!/usr/bin/env python3
"""Van pdf-pagina's een reel maken: 1080x1920, mp4.

    python3 reel.py bron.pdf export/instagram/flyer-reel.mp4

Voor een flyer of ander blad dat je als reel wilt plaatsen in plaats van als
carrousel. Een reel wordt door Instagram ook aan niet-volgers getoond, een
carrousel vrijwel alleen aan je eigen volgers — op een nieuw account is dat het
hele verschil.

Drie dingen die hier bewust zo staan:

**Het blad staat binnen de veilige zone.** Een reel is 1080x1920, maar je ziet
dat kader nooit helemaal: Instagram legt er bovenaan zijn kopregel overheen en
onderaan de naam, het bijschrift, de geluidsbalk en de knoppenkolom. De eerste
versie hiervan vulde de hoogte netjes op en toen stond de QR-code van de flyer
achter de knoppen. Meta's eigen richtlijn is de bovenste 14 en de onderste 20
procent vrijhouden; dat is hier 270 pixels boven en 384 onder, dus het blad past
in een strook van 1266 hoog. Op A5 komt dat neer op 894 breed.

Dat het blad daardoor kleiner wordt is geen gebrek maar de prijs van het
formaat. Het alternatief — vullend maken — kost links en rechts een centimeter,
en daar zit bij deze flyer de gouden rand.

**Langzaam inzoomen, en nooit verder dan passend.** Van 94 naar 100 procent, dus
op het laatste beeld staat het blad precies passend en is er nergens iets
afgesneden. Beweging is nodig — een reel die stilstaat wordt weggeswipet — maar
een blad vol tekst moet wel leesbaar blijven, dus het is traag.

**De tweede pagina krijgt meer tijd.** Daar staat de uitleg van de actie. Een
kijker die pagina 1 in anderhalve seconde snapt heeft voor pagina 2 vijf
seconden nodig.

Er zit geen geluid op, alleen een stille audiosporen zodat Instagram het bestand
zonder mopperen accepteert. Muziek kies je in de app, en dat kan alleen op de
telefoon: de muziekbibliotheek van Instagram zit niet in de browserversie.
"""
import pathlib
import subprocess
import sys

import imageio_ffmpeg
import pymupdf
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from huisstijl import NAVY  # noqa: E402

BREED, HOOG = 1080, 1920
FPS = 30
SECONDEN = [4.0, 6.0]          # per pagina; pagina 2 heeft meer tekst
ZOOM = (0.94, 1.00)            # nooit boven 1: dan zou er iets afvallen

# Wat Instagram over je reel heen legt. Meta houdt zelf 14 procent boven en 20
# procent onder aan; dat is de kopregel, en onderaan de naam, het bijschrift,
# de geluidsbalk en de knoppenkolom.
VEILIG_BOVEN = round(HOOG * 0.14)
VEILIG_ONDER = round(HOOG * 0.20)
VEILIG_HOOG = HOOG - VEILIG_BOVEN - VEILIG_ONDER


def paginabeeld(blad):
    """De pagina op ruime resolutie, zodat inzoomen scherp blijft."""
    px = blad.get_pixmap(dpi=300)
    return Image.frombytes('RGB', (px.width, px.height), px.samples)


def kader(beeld, schaal):
    """Het blad passend in de veilige strook, gecentreerd binnen die strook.

    Passend op de hoogte van de strook en niet op de breedte van het doek: een
    staand blad loopt anders onderuit het kader. Blijkt het blad dan breder dan
    het doek — bij een liggend blad — dan alsnog op de breedte."""
    hoog = round(VEILIG_HOOG * schaal)
    breed = round(beeld.width * hoog / beeld.height)
    if breed > BREED:
        breed = BREED
        hoog = round(beeld.height * breed / beeld.width)
    doek = Image.new('RGB', (BREED, HOOG), NAVY)
    doek.paste(beeld.resize((breed, hoog), Image.LANCZOS),
               ((BREED - breed) // 2,
                VEILIG_BOVEN + (VEILIG_HOOG - hoog) // 2))
    return doek


def main():
    if len(sys.argv) != 3:
        sys.exit('gebruik: reel.py <bron.pdf> <doel.mp4>')
    bron, doel = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    doel.parent.mkdir(parents=True, exist_ok=True)

    pdf = pymupdf.open(bron)
    beelden = [paginabeeld(b) for b in pdf]
    pdf.close()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proces = subprocess.Popen(
        [ff, '-y', '-loglevel', 'error',
         '-f', 'rawvideo', '-pix_fmt', 'rgb24',
         '-s', f'{BREED}x{HOOG}', '-r', str(FPS), '-i', '-',
         '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
         '-shortest',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
         '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.0',
         '-movflags', '+faststart',
         '-c:a', 'aac', '-b:a', '128k',
         str(doel)],
        stdin=subprocess.PIPE)

    tel = 0
    for beeld, duur in zip(beelden, SECONDEN):
        n = round(duur * FPS)
        for i in range(n):
            deel = i / max(n - 1, 1)
            schaal = ZOOM[0] + (ZOOM[1] - ZOOM[0]) * deel
            proces.stdin.write(kader(beeld, schaal).tobytes())
            tel += 1
    proces.stdin.close()
    if proces.wait() != 0:
        sys.exit('ffmpeg is misgegaan')

    print(f'{doel}  {BREED}x{HOOG}  {tel / FPS:.1f} s  '
          f'{doel.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

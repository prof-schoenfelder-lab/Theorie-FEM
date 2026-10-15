"""Kursübersicht für die Startseite: Weg von den Grundlagen über den Ablauf der FEM zu den Elementen."""

import math
from pathlib import Path

from nlzeichnen import feder, notiz
from tmzeichnen import FARBE, Abbildung, kreis, linie, pfeil, polylinie, text

ZIEL = Path(__file__).resolve().parent.parent / "grafiken" / "uebersicht"
BLAU, ROT, GRUEN = "#0050b4", "#d40000", "#006414"
RAND, FLAECHE = "#c9ced4", "#f4f6f8"
SANS = "'Source Sans Pro','Helvetica Neue',Arial,sans-serif"


def _box(x, y, b, h, fuell=FLAECHE, rand=RAND):
    return f'<rect x="{x}" y="{y}" width="{b}" height="{h}" rx="10" fill="{fuell}" stroke="{rand}" stroke-width="1.2"/>'


def _titel(x, y, nr, zeilen, farbe=BLAU):
    t = [f'<circle cx="{x + 15}" cy="{y}" r="13" fill="{farbe}"/>',
         f'<text x="{x + 15}" y="{y + 5.5}" fill="#fff" font-family="{SANS}" font-size="16" font-weight="700" '
         f'text-anchor="middle">{nr}</text>']
    for i, z in enumerate(zeilen):
        t.append(f'<text x="{x + 36}" y="{y + 6 + i * 19}" fill="#1d2329" font-family="{SANS}" font-size="16.5" '
                 f'font-weight="{600 if i == 0 else 400}">{z}</text>')
    return "".join(t)


def _klein(x, y, z, farbe="#5a636d", anker="start", groesse=13.5):
    return (f'<text x="{x}" y="{y}" fill="{farbe}" font-family="{SANS}" font-size="{groesse}" '
            f'text-anchor="{anker}">{z}</text>')


# ---------------------------------------------------------------- kleine Symbole
def _sym_feder(x, y):
    return "".join([linie(x, y - 16, x, y + 16, "#000", 2), feder(x, y, x + 70, y, 4, 7),
                    f'<rect x="{x + 70}" y="{y - 14}" width="8" height="28" fill="#a6a6a6" stroke="#000"/>',
                    pfeil(x + 80, y, x + 104, y, ROT, 1.6, (8, 5))])


def _sym_energie(x, y):
    pts = [(x + i * 2.08, y + 12 - 0.011 * (i * 2.08 - 52) ** 2) for i in range(51)]
    return "".join([linie(x, y + 18, x + 104, y + 18, "#777", 1), polylinie(pts, BLAU, 2),
                    kreis(x + 52, y + 12, 3.5, ROT, ROT), _klein(x + 60, y + 4, "min Π", ROT, groesse=12.5)])


def _sym_ritz(x, y):
    ex = [(x + i * 2.08, y + 16 - 34 * math.sin(i / 50 * math.pi / 2)) for i in range(51)]
    ap = [(x + i * 2.08, y + 16 - 34 * (i / 50) * (1.6 - 0.6 * i / 50)) for i in range(51)]
    return "".join([linie(x, y + 18, x + 104, y + 18, "#777", 1), polylinie(ex, BLAU, 2),
                    polylinie(ap, ROT, 1.6, strich="5 3"),
                    _klein(x + 104, y - 24, "exakt", BLAU, "end", 12), _klein(x - 6, y + 10, "Ansatz", ROT, "end", 12)])


def _sym_stab(x, y, quadratisch=False):
    t = [f'<polygon points="{x},{y - 12} {x + 104},{y - 4} {x + 104},{y + 4} {x},{y + 12}" fill="#e6e6e6" stroke="#000" stroke-width="1"/>']
    n = 5 if quadratisch else 3
    for i in range(n):
        t.append(kreis(x + i * 104 / (n - 1), y, 3.2))
    return "".join(t)


def _sym_fachwerk(x, y):
    p = [(x, y + 16), (x + 52, y + 16), (x + 104, y + 16), (x + 26, y - 16), (x + 78, y - 16)]
    st = [(0, 1), (1, 2), (0, 3), (3, 1), (1, 4), (4, 2), (3, 4)]
    return "".join([linie(*p[a], *p[b], "#555", 2.2) for a, b in st] + [kreis(*q, 3.2) for q in p])


def _sym_balken(x, y):
    pts = [(x + i * 2.08, y - 4 + 14 * math.sin(math.pi * i / 50)) for i in range(51)]
    return "".join([linie(x, y - 4, x + 104, y - 4, "#999", 4), polylinie(pts, ROT, 2),
                    pfeil(x + 52, y - 28, x + 52, y - 9, ROT, 1.6, (8, 5))])


def _sym_rahmen(x, y):
    return "".join([polylinie([(x + 10, y + 18), (x + 10, y - 16), (x + 94, y - 16), (x + 94, y + 18)], "#555", 4),
                    polylinie([(x + 10, y + 18), (x + 18, y - 12), (x + 102, y - 12), (x + 94, y + 18)], ROT, 1.6, strich="5 3")])


def _sym_scheibe(x, y):
    t = []
    for i in range(4):
        for j in range(2):
            t.append(f'<rect x="{x + 6 + i * 23}" y="{y - 16 + j * 16}" width="23" height="16" fill="#e6e6e6" stroke="#555" stroke-width="1"/>')
    for i in range(5):
        for j in range(3):
            t.append(kreis(x + 6 + i * 23, y - 16 + j * 16, 2.2))
    return "".join(t)


def kursweg():
    abb = Abbildung(1000, 520, "Kursübersicht Theorie der FEM")
    e = abb.ebene("karte", "Kursübersicht")

    # Zeile 1: Grundlagen
    e.append(_klein(20, 30, "GRUNDLAGEN AUS DER TECHNISCHEN MECHANIK", "#8a929b", groesse=13))
    karten = [(20, "0", ["Mathematica", "K p = q am Federsystem"], _sym_feder),
              (350, "1", ["Energieprinzipien", "Minimum der pot. Energie"], _sym_energie),
              (680, "2", ["Rayleigh-Ritz", "Ansatz für das ganze Bauteil"], _sym_ritz)]
    for x, nr, z, sym in karten:
        e.append(_box(x, 44, 300, 120))
        e.append(_titel(x + 14, 72, nr, z))
        e.append(sym(x + 170, 128))
    for xa in (320, 650):
        e.append(pfeil(xa + 2, 104, xa + 28, 104, "#8a929b", 2, (10, 7)))

    # Übergang
    e.append(pfeil(830, 166, 830, 206, "#8a929b", 2, (10, 7)))
    e.append(_klein(842, 192, "elementweiser Ansatz", "#5a636d"))

    # Zeile 2: Ablauf der FEM
    e.append(_box(20, 212, 960, 104, "#ffffff", "#9aa3ad"))
    e.append(_titel(34, 240, "3", ["Ablauf der FEM am Normalkraftstab"]))
    phasen = [(50, BLAU, "Preprocessing", "Elemente  ·  Kᵉ  ·  Λᵉ"),
              (360, ROT, "Solution", "K p = q"),
              (670, GRUEN, "Postprocessing", "u  ·  ε  ·  σ")]
    for x, farbe, titel, inhalt in phasen:
        e.append(f'<rect x="{x}" y="258" width="280" height="44" rx="7" fill="{farbe}" fill-opacity="0.09" stroke="{farbe}" stroke-width="1.2"/>')
        e.append(_klein(x + 14, 285, titel, farbe, groesse=15.5))
        e.append(_klein(x + 266, 285, inhalt, "#1d2329", "end", 15))
    for xa in (330, 640):
        e.append(pfeil(xa + 2, 280, xa + 28, 280, "#8a929b", 2, (9, 6)))

    # Zeile 3: Elemente
    e.append(_klein(20, 352, "ELEMENTE", "#8a929b", groesse=13))
    elemente = [("4", ["Stab quadratisch", "Eigengewicht"], lambda x, y: _sym_stab(x, y, True)),
                ("5", ["Fachwerkstab", "2D"], _sym_fachwerk),
                ("6", ["Balken", "Biegung"], _sym_balken),
                ("7", ["Rahmen", "Stab + Balken"], _sym_rahmen),
                ("8", ["2D-Rechteck", "Scheibe"], _sym_scheibe)]
    b = 180
    for i, (nr, z, sym) in enumerate(elemente):
        x = 20 + i * (b + 15)
        e.append(_box(x, 366, b, 140))
        e.append(_titel(x + 10, 394, nr, z))
        e.append(sym(x + 38, 466))
    return abb.speichern(ZIEL / "kursweg.svg")


if __name__ == "__main__":
    print(kursweg())

"""Grafiken zu Vorlesung 0: Einführung in Mathematica, Struktur K p = q.

- Kurvendiskussion f(x) = x³ + 5x² − 3x − 20 (Übung „erste Schritte“)
- Schnittgrößen am Träger (TM-Aufgabe 7.1), Normalkraftstab unter Eigengewicht
- Federsystem aus dem Vorlesungsbeispiel 2025: c1 = 2k, c2 = 4k, c3 = k, f1 = 3F, f2 = −F
- Umformung der Gleichungen des Federsystems zu K p = q (Formeln als Ebenen, eine je Schritt)
"""

import math
import re
from pathlib import Path
from xml.sax.saxutils import escape

from nlzeichnen import Diagramm, feder
from nlzeichnen import notiz
from tmzeichnen import (FARBE, SCHRIFT, Abbildung, balken, balkenzug, einspannung, festlager, kraft, kreis, linie, loslager, mass,
                        pfeil, streckenlast, text, verlauf, winkelbogen)

ZIEL = Path(__file__).resolve().parent.parent / "grafiken" / "einfuehrung"
EX, ROT, GR = FARBE["linear"], FARBE["nichtlinear"], FARBE["mass"]
GRAU = "#7a7a7a"


# ---------------------------------------------------------------- Kurvendiskussion
def f(x):
    return x**3 + 5 * x**2 - 3 * x - 20


def _nullstellen():
    out, a = [], -6.0
    while a < 3:
        b = a + 0.01
        if f(a) * f(b) <= 0:
            lo, hi = a, b
            for _ in range(60):
                m = (lo + hi) / 2
                lo, hi = (m, hi) if f(lo) * f(m) > 0 else (lo, m)
            out.append((lo + hi) / 2)
        a = b
    return out


def kurve():
    abb = Abbildung(640, 375, "Kurvendiskussion")
    D = Diagramm(60, 330, 500, 300, 3.0, 15.0, xmin=-6.0, ymin=-25.0)
    r = _nullstellen()
    e1 = (-10 - math.sqrt(100 + 36)) / 6, (-10 + math.sqrt(100 + 36)) / 6

    e = abb.ebene("achsen", "Achsen")
    e.append(D.achsen("x", "f(x)", [(-6, "−6"), (-4, "−4"), (-2, ""), (2, "")],
                      [(-20, "−20"), (-10, "−10"), (10, "10")], raster=True))

    e = abb.ebene("kurve", "Funktion")
    e.append(D.kurve(f, -6, 3, farbe=EX))
    e.append(D.text(-5.8, 14, "f(x) = x^3 + 5x^2 − 3x − 20", EX, anker="start", groesse=17))

    e = abb.ebene("flaeche", "Fläche")
    pts = [(r[1], 0)] + [(r[1] + (r[2] - r[1]) * i / 80, f(r[1] + (r[2] - r[1]) * i / 80)) for i in range(81)] + [(r[2], 0)]
    e.append(D.flaeche(pts, FARBE["bereich_nl"], 0.95))
    e.append(D.kurve(f, r[1], r[2], farbe=EX))
    e.append(D.text(-1.0, -7, "A = −53,6", ROT, groesse=17, italic=False))

    e = abb.ebene("nullstellen", "Nullstellen")
    for x in r:
        e.append(D.punkt(x, 0, ROT, 4.4))
    e.append(D.text(r[0], 0, "−4,74", ROT, dx=-4, dy=-14, groesse=14, italic=False, anker="end"))
    e.append(D.text(r[1], 0, "−2,19", ROT, dx=6, dy=-14, groesse=14, italic=False, anker="start"))
    e.append(D.text(r[2], 0, "1,93", ROT, dx=4, dy=-14, groesse=14, italic=False, anker="start"))

    e = abb.ebene("extrema", "Extrema")
    for x in e1:
        e.append(D.hilfslinien(x, f(x)))
        e.append(D.punkt(x, f(x), GR, 4.4, hohl=True))
    e.append(D.text(e1[0], f(e1[0]), "Max (−3,61 | 8,94)", GR, dy=-16, groesse=14, italic=False))
    e.append(D.text(e1[1], f(e1[1]), "Min (0,28 | −20,43)", GR, dy=18, groesse=14, italic=False))
    return abb.speichern(ZIEL / "kurve.svg")


# ---------------------------------------------------------------- Federsystem
def _platte(x, y0, y1, breite=16):
    """Verschieblicher starrer Balken mit Führungen oben und unten (wie Tafelbild)."""
    t = [f'<rect x="{x}" y="{y0}" width="{breite}" height="{y1 - y0}" fill="#a6a6a6" stroke="#000" stroke-width="1.25"/>']
    for yy, s in ((y0 - 5, -1), (y1 + 5, 1)):
        t.append(f'<rect x="{x - 9}" y="{yy + (0 if s > 0 else -7)}" width="{breite + 18}" height="7" fill="{FARBE["lager"]}"/>')
        t.append(linie(x - 12, yy, x + breite + 12, yy, "#000000", 1.25))
    return "".join(t)


def _knoten_nr(x, y, n, dx=-10, dy=-12):
    return text(x + dx, y + dy, f"[{n}]", "#000000", 14, italic=False)


def federsystem():
    abb = Abbildung(720, 575, "Federsystem mit drei Federn")
    xw, xm, xr, b = 70, 330, 560, 16          # Wand, mittlerer Balken (p2), rechter Balken (p1)
    y3, y12 = 85, 225                          # Höhen der Federn
    ym0, ym1, yr0, yr1 = 150, 262, 50, 262     # Ausdehnung der Balken
    yf2, yf1, yp1 = 178, 130, 190
    dy = 280                                   # Versatz Freischnitt

    e = abb.ebene("system", "System")
    e.append(einspannung(xw, (yr0 + yr1) / 2, yr1 - yr0 + 10))
    e.append(_platte(xm, ym0, ym1))
    e.append(_platte(xr, yr0, yr1))
    e.append(feder(xw, y3, xr, y3, 5, 10, anteil=0.35, label="c_3", label_abstand=22))
    e.append(feder(xw, y12, xm, y12, 4, 10, label="c_1", label_abstand=22))
    e.append(feder(xm + b, y12, xr, y12, 4, 10, breite=3.0, label="c_2", label_abstand=22))
    for x, y in ((xw, y3), (xw, y12), (xm, y12), (xm + b, y12), (xr, y12), (xr, y3)):
        e.append(kreis(x, y, 4.2))
    e.append(_knoten_nr(xm, y12, 1))
    e.append(_knoten_nr(xr, y12, 2))
    e.append(_knoten_nr(xr, y3, 3))

    e = abb.ebene("last", "Lasten")
    e.append(kraft(xm + b, yf2, 0, "f_2", laenge=55, ziehend=True, label_seite=1))
    e.append(kraft(xr + b, yf1, 0, "f_1", laenge=60, ziehend=True, label_seite=1))

    e = abb.ebene("dof", "Freiheitsgrade")
    e.append(pfeil(xm + b, ym0 - 22, xm + b + 44, ym0 - 22, GR, 1.4, (9, 6)))
    e.append(text(xm + b + 50, ym0 - 22, "p_2", GR, anker="start"))
    e.append(pfeil(xr + b, yp1, xr + b + 50, yp1, GR, 1.4, (9, 6)))
    e.append(text(xr + b + 56, yp1, "p_1", GR, anker="start"))

    e = abb.ebene("dehnung", "Federverlängerungen")
    e.append(text((xw + xm) / 2, y12 + 34, "u_1 = p_2", GR, 17))
    e.append(text((xm + b + xr) / 2, y12 + 34, "u_2 = p_1 − p_2", GR, 17))
    e.append(text((xw + xr) / 2 - 60, y3 + 30, "u_3 = p_1", GR, 17))

    # Freischnitte der beiden Balken: Federkräfte als Zugkräfte (positiv), Kräfte rot
    e = abb.ebene("freischnitt", "Freischnitt")
    e.append(_platte(xm, ym0 + dy, ym1 + dy))
    e.append(_platte(xr, yr0 + dy, yr1 + dy))
    e.append(kraft(xm, y12 + dy, 180, "N_1", laenge=60, ziehend=True, label_seite=-1))
    e.append(kraft(xm + b, y12 + dy, 0, "N_2", laenge=60, ziehend=True, label_seite=1))
    e.append(kraft(xm + b, yf2 + dy, 0, "f_2", laenge=55, ziehend=True, label_seite=1))
    e.append(kraft(xr, y12 + dy, 180, "N_2", laenge=60, ziehend=True, label_seite=-1))
    e.append(kraft(xr, y3 + dy, 180, "N_3", laenge=60, ziehend=True, label_seite=-1))
    e.append(kraft(xr + b, yf1 + dy, 0, "f_1", laenge=60, ziehend=True, label_seite=1))
    e.append(linie(20, dy + 8, 700, dy + 8, "#c8c8c8", 0.8, "6 4"))
    e.append(text(30, dy + 30, "Freischnitt", "#555555", 15, anker="start", italic=False))
    return abb.speichern(ZIEL / "federsystem.svg")


def federsystem_3dof():
    """Übungsaufgabe: drei starre Balken, vier Federn (statisch, eine Ebene)."""
    abb = Abbildung(720, 400, "Federsystem mit drei Freiheitsgraden")
    xl, xm, xr, xw, b = 70, 330, 600, 470, 16
    y1, y3, y2, y4 = 70, 210, 280, 330
    e = abb.ebene("system", "System")
    e.append(_platte(xl, 30, 360))
    e.append(_platte(xm, 170, 360))
    e.append(_platte(xr, 30, 360))
    e.append(einspannung(xw + 8, y4, 50, seite="rechts"))
    e.append(feder(xl + b, y1, xr, y1, 4, 10, anteil=0.4, label="c_1", label_abstand=22))
    e.append(feder(xl + b, y2, xm, y2, 4, 10, label="c_2", label_abstand=22))
    e.append(feder(xm + b, y3, xr, y3, 4, 10, label="c_3", label_abstand=22))
    e.append(feder(xm + b, y4, xw + 8, y4, 4, 10, label="c_4", label_abstand=22))
    for x, y in ((xl + b, y1), (xr, y1), (xl + b, y2), (xm, y2), (xm + b, y3), (xr, y3), (xm + b, y4), (xw + 8, y4)):
        e.append(kreis(x, y, 4.2))
    e.append(_knoten_nr(xr, y1, 1))
    e.append(_knoten_nr(xm, y2, 2))
    e.append(_knoten_nr(xr, y3, 3))
    e.append(_knoten_nr(xw + 8, y4, 4))
    e.append(kraft(xl + b, 140, 0, "F", laenge=55, ziehend=True, label_seite=1))
    e.append(kraft(xr + b, 300, 0, "3F", laenge=55, ziehend=True, label_seite=1))
    for x, y, n in ((xl + b, 180, 1), (xm + b, 190, 2), (xr + b, 230, 3)):
        e.append(pfeil(x, y, x + 44, y, GR, 1.4, (9, 6)))
        e.append(text(x + 50, y, f"p_{n}", GR, anker="start"))
    return abb.speichern(ZIEL / "federsystem-3dof.svg")


# ---------------------------------------------------------------- Umformung zu K p = q
_FTOKEN = re.compile(r"\*\*(\w)\*\*|([A-Za-zα-ωΠ]+)(?:_(\{[^}]*\}|\w))?|(\s+)|([^A-Za-zα-ωΠ\s*]+|\*)")
_FFARBE = {"p": GR, "f": ROT}


def formel(x, y, s, farbe="#000000", groesse=20, anker="start", faerben=True):
    """Formel als SVG-Text: Buchstaben kursiv, Ziffern und Operatoren aufrecht, **K** fett aufrecht.
    p_i (Freiheitsgrade) grün, f_i (Lasten) rot, damit man sie beim Umformen verfolgen kann."""
    t = []
    for fett, name, index, leer, rest in _FTOKEN.findall(s):
        if fett:
            t.append(f'<tspan font-style="normal" font-weight="bold">{escape(fett)}</tspan>')
        elif name:
            fa = _FFARBE.get(name, farbe) if faerben and index else farbe
            t.append(f'<tspan font-style="italic" fill="{fa}">{escape(name)}</tspan>')
            if index:
                index = index.strip("{}")
                t.append(f'<tspan font-style="normal" fill="{fa}" font-size="70%" baseline-shift="sub">{escape(index)}</tspan>')
        elif leer:
            t.append(f"<tspan> </tspan>")
        else:
            t.append(f'<tspan font-style="normal">{escape(rest.replace("-", "−"))}</tspan>')
    return (f'<text x="{x}" y="{y + 0.34 * groesse:.1f}" fill="{farbe}" font-family="{SCHRIFT}" font-size="{groesse}" '
            f'text-anchor="{anker}" xml:space="preserve">{"".join(t)}</text>')


def _klammer(x, y0, y1, links=True, farbe="#000000"):
    """Runde Klammer für Matrizen und Vektoren."""
    w = 7 if links else -7
    return (f'<path d="M {x + w},{y0} Q {x - w * 0.6},{(y0 + y1) / 2} {x + w},{y1}" fill="none" '
            f'stroke="{farbe}" stroke-width="1.4"/>')


def _matrix(x, y, zeilen, spalten_x, dy=34, groesse=20):
    """Matrix/Vektor: zeilen = Listen von Formeln, spalten_x = Mitten der Spalten relativ zu x."""
    out = []
    for i, z in enumerate(zeilen):
        for j, e in enumerate(z):
            out.append(formel(x + spalten_x[j], y + i * dy, e, groesse=groesse, anker="middle"))
    y0, y1 = y - 20, y + (len(zeilen) - 1) * dy + 20
    out.append(_klammer(x, y0, y1, True))
    out.append(_klammer(x + spalten_x[-1] + spalten_x[0], y0, y1, False))
    return "".join(out)


def _unterklammer(x0, x1, y, label):
    """Geschweifte Klammer unter einem Ausdruck mit Bezeichnung (z. B. K, p, q)."""
    m = (x0 + x1) / 2
    d = (f"M {x0},{y} Q {x0},{y + 7} {x0 + 8},{y + 7} L {m - 8},{y + 7} Q {m},{y + 7} {m},{y + 14} "
         f"Q {m},{y + 7} {m + 8},{y + 7} L {x1 - 8},{y + 7} Q {x1},{y + 7} {x1},{y}")
    return (f'<path d="{d}" fill="none" stroke="#555555" stroke-width="1.1"/>'
            + formel(m, y + 30, label, groesse=20, anker="middle"))


def _rahmen(x, y, b, h, titel, farbe="#8a8f96"):
    return (f'<rect x="{x}" y="{y}" width="{b}" height="{h}" rx="6" fill="#f6f8fb" stroke="{farbe}" stroke-width="1"/>'
            + notiz(x + 10, y + 16, [titel], "#444444", 14))


def _schrittpfeil(x, y0, y1, label=""):
    t = [pfeil(x, y0, x, y1, "#555555", 1.3, (9, 6))]
    if label:
        t.append(notiz(x + 12, (y0 + y1) / 2, [label], "#555555", 14))
    return "".join(t)


def kpq():
    """Vom Gleichungssatz des Federsystems (Gleichgewicht, Federgesetz, Kinematik) zu K p = q.
    Schmal und hoch angelegt, damit die Formeln in der Bildspalte groß genug erscheinen."""
    abb = Abbildung(560, 1000, "Umformung zu K p = q")
    G = 19                                       # Schriftgröße der Formeln
    xg, xf, xk, y0 = 10, 214, 382, 18            # Spalten: Gleichgewicht, Federgesetz, Kinematik

    e = abb.ebene("gleichungen", "Unbekannte und Gleichungen")
    e.append(notiz(xg, y0, ["Unbekannte (8):"], "#444444", 15))
    e.append(formel(xg + 112, y0, "N_1, N_2, N_3,  u_1, u_2, u_3,  p_1, p_2", groesse=G))
    yb = y0 + 28
    e.append(_rahmen(xg, yb, 196, 124, "Gleichgewicht (2)"))
    e.append(formel(xg + 10, yb + 52, "−N_2 − N_3 + f_1 = 0", groesse=G))
    e.append(formel(xg + 10, yb + 92, "−N_1 + N_2 + f_2 = 0", groesse=G))
    e.append(_rahmen(xf, yb, 160, 124, "Federgesetz (3)"))
    for i, g in enumerate(("N_1 = c_1 u_1", "N_2 = c_2 u_2", "N_3 = c_3 u_3")):
        e.append(formel(xf + 12, yb + 46 + 30 * i, g, groesse=G))
    e.append(_rahmen(xk, yb, 168, 124, "Kinematik (3)"))
    for i, g in enumerate(("u_1 = p_2", "u_2 = p_1 − p_2", "u_3 = p_1")):
        e.append(formel(xk + 12, yb + 46 + 30 * i, g, groesse=G))

    # Kinematik in das Federgesetz
    y2 = yb + 196
    e = abb.ebene("schritt_federn", "Kinematik in Federgesetz")
    e.append(pfeil(xf + 80, yb + 128, xf + 110, y2 - 10, "#555555", 1.3, (9, 6)))
    e.append(pfeil(xk + 84, yb + 128, xf + 210, y2 - 10, "#555555", 1.3, (9, 6)))
    e.append(_rahmen(xf, y2 - 8, 336, 130, "Federkräfte in den Verschiebungen"))
    for i, g in enumerate(("N_1 = c_1 p_2", "N_2 = c_2 (p_1 − p_2)", "N_3 = c_3 p_1")):
        e.append(formel(xf + 12, y2 + 38 + 30 * i, g, groesse=G))

    # in das Gleichgewicht
    y3 = y2 + 186
    e = abb.ebene("schritt_glgw", "In das Gleichgewicht")
    e.append(pfeil(xg + 98, yb + 128, xg + 98, y3 - 10, "#555555", 1.3, (9, 6)))
    e.append(pfeil(xf + 150, y2 + 126, xg + 300, y3 - 10, "#555555", 1.3, (9, 6)))
    e.append(_rahmen(xg, y3 - 8, 540, 104, "Gleichgewicht in den Verschiebungen: 2 Gleichungen, 2 Unbekannte"))
    e.append(formel(xg + 14, y3 + 38, "−c_2 (p_1 − p_2) − c_3 p_1 + f_1 = 0", groesse=G))
    e.append(formel(xg + 14, y3 + 72, "−c_1 p_2 + c_2 (p_1 − p_2) + f_2 = 0", groesse=G))

    # sortieren
    y4 = y3 + 158
    e = abb.ebene("schritt_sortiert", "Nach den Freiheitsgraden sortiert")
    e.append(_schrittpfeil(xg + 98, y3 + 100, y4 - 10, "ausmultiplizieren, nach p_1, p_2 sortieren, f_i nach rechts"))
    e.append(_rahmen(xg, y4 - 8, 540, 104, "innere Kräfte = äußere Lasten"))
    # in Spalten gesetzt: p_1-Terme rechtsbündig, p_2-Terme rechtsbündig, dann = f_i
    for yy, a, b, c in ((y4 + 38, "(c_2 + c_3) p_1", "− c_2 p_2", "f_1"), (y4 + 72, "−c_2 p_1", "+ (c_1 + c_2) p_2", "f_2")):
        e.append(formel(xg + 150, yy, a, groesse=G, anker="end"))
        e.append(formel(xg + 290, yy, b, groesse=G, anker="end"))
        e.append(formel(xg + 300, yy, "= " + c, groesse=G))

    # Matrixform
    y5 = y4 + 160
    e = abb.ebene("schritt_matrix", "Matrixform")
    e.append(_schrittpfeil(xg + 98, y4 + 100, y5 - 30, "Koeffizienten von p_1, p_2 in eine Matrix"))
    e.append(_matrix(xg + 10, y5, [["c_2 + c_3", "−c_2"], ["−c_2", "c_1 + c_2"]], [52, 140], groesse=G))
    e.append(_matrix(xg + 210, y5, [["p_1"], ["p_2"]], [26], groesse=G))
    e.append(formel(xg + 278, y5 + 17, "=", groesse=22, anker="middle"))
    e.append(_matrix(xg + 300, y5, [["f_1"], ["f_2"]], [26], groesse=G))
    e.append(_unterklammer(xg + 12, xg + 200, y5 + 62, "**K**"))
    e.append(_unterklammer(xg + 212, xg + 258, y5 + 62, "**p**"))
    e.append(_unterklammer(xg + 302, xg + 348, y5 + 62, "**q**"))
    e.append(notiz(xg + 380, y5 + 6, ["Steifigkeitsmatrix", "mal Freiheitsgrade", "= Lasten"], "#444444", 15))

    # Zahlenwerte und Lösung
    y6 = y5 + 160
    e = abb.ebene("schritt_zahlen", "Zahlenwerte und Lösung")
    e.append(notiz(xg, y6 - 40, ["mit c_1 = 2k, c_2 = 4k, c_3 = k, f_1 = 3F, f_2 = −F:"], "#444444", 15))
    e.append(formel(xg + 4, y6 + 17, "k", groesse=G))
    e.append(_matrix(xg + 20, y6, [["5", "−4"], ["−4", "6"]], [26, 76], groesse=G))
    e.append(_matrix(xg + 128, y6, [["p_1"], ["p_2"]], [26], groesse=G))
    e.append(formel(xg + 196, y6 + 17, "=", groesse=22, anker="middle"))
    e.append(_matrix(xg + 218, y6, [["3F"], ["−F"]], [28], groesse=G))
    e.append(formel(xg + 300, y6 + 17, "⇒", groesse=22, anker="middle"))
    for i, (lhs, z, n) in enumerate((("p_1 =", "F", "k"), ("p_2 =", "F", "2k"))):
        xx, yy = xg + 326, y6 + i * 60 - 8
        e.append(formel(xx, yy + 17, lhs, groesse=G))
        e.append(formel(xx + 62, yy + 3, z, groesse=G, anker="middle", faerben=False))
        e.append(linie(xx + 49, yy + 17, xx + 75, yy + 17, "#000000", 1.0))
        e.append(formel(xx + 62, yy + 33, n, groesse=G, anker="middle", faerben=False))
    return abb.speichern(ZIEL / "kpq.svg")

# ---------------------------------------------------------------- TM-Aufgabe 7.1
def traeger71():
    """Träger mit Streckenlast q über 3a und schräger Kraft F am Kragende.
    F = 5 kN, q = 30 kN/m, a = 0,1 m, α = 45°; Ergebnisse aus Mathematica (Lösungsnotebook 7.1)."""
    abb = Abbildung(760, 620, "Schnittgrößen am Träger")
    F, q, a, c = 5.0, 30.0, 0.1, math.cos(math.radians(45))
    A = 3 * a * q * 1.5 * a / (3 * a) - F * c * a / (3 * a)
    Bv = 3 * a * q + F * c - A
    Bh = F * c
    px = 1300.0                                  # px je m
    x0, y = 110, 130
    xB, xE = x0 + 3 * a * px, x0 + 4 * a * px

    e = abb.ebene("traeger", "Träger")
    e.append(balken(x0, y, xE, y))
    e = abb.ebene("lager", "Lager")
    e.append(loslager(x0, y + 3.5, label="A", label_pos=(-20, 12)))
    e.append(festlager(xB, y + 3.5, label="B", label_pos=(-20, 12)))

    e = abb.ebene("lasten", "Lasten")
    e.append(streckenlast(x0, xB, y - 4, 34, label="q"))
    e.append(kraft(xE, y - 2, 225, "F", laenge=62, label_seite=1))
    e.append(linie(xE, y, xE + 60, y, GRAU, 0.8, "4 3"))
    e.append(winkelbogen(xE, y, 40, 0, 45, "α"))

    e = abb.ebene("mass", "Bemaßung")
    e.append(mass(x0, y + 26, xB, y + 26, "3a", abstand=-22))
    e.append(mass(xB, y + 26, xE, y + 26, "a", abstand=-22))

    e = abb.ebene("reaktionen", "Lagerreaktionen")
    e.append(kraft(x0, y + 4, 90, "A", laenge=48, label_seite=1))
    e.append(kraft(xB, y + 4, 90, "B_v", laenge=48, label_seite=1))
    e.append(kraft(xB - 4, y + 22, 0, "B_h", laenge=48, label_seite=1, label_pos=0.6))

    e = abb.ebene("bereiche", "Bereiche")
    for xa, n, rom in ((x0, 1, "I"), (xB, 2, "II")):
        e.append(pfeil(xa, y - 66, xa + 40, y - 66, GR, 1.25, (8, 5)))
        e.append(text(xa + 46, y - 66, f"x_{n}", GR, anker="start"))
    e.append(text((x0 + xB) / 2, y - 86, "[Bereich I]", "#444444", 15, italic=False))
    e.append(text((xB + xE) / 2, y - 86, "[Bereich II]", "#444444", 15, italic=False))

    xs = [i / 40 * 3 * a for i in range(41)]
    pN = [(0, 0), (3 * a * px, 0), (3 * a * px, -Bh), (4 * a * px, -Bh)]
    pQ = [(0, A), (3 * a * px, A - q * 3 * a), (3 * a * px, F * c), (4 * a * px, F * c)]
    pM = [(x * px, A * x - q * x * x / 2) for x in xs] + [(4 * a * px, 0.0)]
    xm = A / q
    e = abb.ebene("verlauf_n", "Normalkraft")
    e.append(verlauf(x0, pN, 8, 265, 4 * a * px, "N(x)", werte=[(4 * a * px - 40, -Bh, "−3,54", "middle")]))
    e = abb.ebene("verlauf_q", "Querkraft")
    e.append(verlauf(x0, pQ, 7, 380, 4 * a * px, "Q(x)",
                     werte=[(18, A, "3,32", "start"), (3 * a * px - 6, A - q * 3 * a, "−5,68", "end"),
                            (4 * a * px - 40, F * c, "3,54", "middle")]))
    e = abb.ebene("verlauf_m", "Biegemoment")
    e.append(verlauf(x0, pM, 140, 515, 4 * a * px, "M(x)",
                     werte=[(xm * px, A * xm - q * xm * xm / 2, "0,184", "middle"),
                            (3 * a * px + 8, -F * c * a, "−0,354", "start")]))
    e.append(notiz(x0, 600, ["N, Q in kN · M in kNm · positive Werte oberhalb der Achse"], "#555555", 13))
    return abb.speichern(ZIEL / "traeger71.svg")


# ---------------------------------------------------------------- Stab unter Eigengewicht
def _haengestab(xs, y0, y1, lager_oben=True, lager_unten=False, beschriften=True):
    t = [balken(xs, y0, xs, y1, 9)]
    if lager_oben:
        t.append(festlager(xs, y0, drehung=180))
    if lager_unten:
        t.append(festlager(xs, y1))
    for i in range(7):
        yy = y0 + 18 + i * (y1 - y0 - 36) / 6
        t.append(pfeil(xs + 16, yy - 14, xs + 16, yy + 8, ROT, 1.1, (7, 4.5)))
    if beschriften:
        t.append(text(xs + 28, (y0 + y1) / 2, "q_0", ROT, anker="start"))
    return "".join(t)


def eigengewicht():
    abb = Abbildung(780, 470, "Normalkraftstab unter Eigengewicht")
    y0, y1 = 70, 380
    BLAU, ROTK, GRAUK = EX, ROT, "#555555"

    e = abb.ebene("stab_a", "a) hängend")
    xa = 90
    e.append(_haengestab(xa, y0, y1))
    e.append(pfeil(xa - 26, y0 + 4, xa - 26, y0 + 50, GR, 1.25, (8, 5)))
    e.append(text(xa - 32, y0 + 44, "x", GR, anker="end"))
    e.append(mass(xa - 64, y0, xa - 64, y1, "L", abstand=0, hilfslinien=False))
    e.append(text(xa, y1 + 40, "[a)]", BLAU, 17, italic=False))

    e = abb.ebene("stab_b", "b) beidseitig gelagert")
    e.append(_haengestab(200, y0, y1, lager_unten=True, beschriften=False))
    e.append(text(200, y1 + 40, "[b)]", ROTK, 17, italic=False))
    e = abb.ebene("stab_c", "c) stehend")
    e.append(_haengestab(300, y0, y1, lager_oben=False, lager_unten=True, beschriften=False))
    e.append(text(300, y1 + 40, "[c)]", GRAUK, 17, italic=False))

    Du = Diagramm(430, 190, 280, 130, 1.0, 0.55)
    Dn = Diagramm(430, 380, 280, 130, 1.0, 1.0, ymin=-1.0)
    e = abb.ebene("achsen", "Achsen")
    e.append(Du.achsen("x", "u · EA/(q_0 L^2)", [(0.5, "L/2"), (1, "L")], [(0.25, "0,25"), (0.5, "0,5")], raster=True, groesse=16))
    e.append(Dn.achsen("x", "N/(q_0 L)", [(0.5, ""), (1, "")], [(-1, "−1"), (1, "1")], raster=True, groesse=16))

    faelle = (("a", BLAU, lambda x: (2 - x) * x / 2, lambda x: 1 - x),
              ("b", ROTK, lambda x: (1 - x) * x / 2, lambda x: 0.5 - x),
              ("c", GRAUK, lambda x: (1 - x * x) / 2, lambda x: -x))
    for n, farbe, u, N in faelle:
        e = abb.ebene(f"kurve_{n}", f"Verlauf {n})")
        e.append(Du.kurve(u, 0, 1, farbe=farbe))
        e.append(Dn.kurve(N, 0, 1, farbe=farbe))
    e = abb.ebene("marken_a", "Beschriftung a)")
    e.append(Du.text(1, 0.5, "a)", BLAU, dx=10, groesse=15, italic=False, anker="start"))
    e.append(Dn.text(0.12, 0.88, "a)", BLAU, dy=-14, groesse=15, italic=False, anker="start"))
    e = abb.ebene("marken_bc", "Beschriftung b), c)")
    e.append(Du.text(0.5, 0.125, "b)", ROTK, dy=-12, groesse=15, italic=False))
    e.append(Du.text(0.0, 0.5, "c)", GRAUK, dx=10, dy=-12, groesse=15, italic=False, anker="start"))
    e.append(Dn.text(0.12, 0.38, "b)", ROTK, dy=-14, groesse=15, italic=False, anker="start"))
    e.append(Dn.text(1.0, -1.0, "c)", GRAUK, dx=10, groesse=15, italic=False, anker="start"))
    return abb.speichern(ZIEL / "eigengewicht.svg")


# ---------------------------------------------------------------- Übungsaufgaben (statisch)
def aufgabe73():
    """Abgewinkelter Träger (TM, Aufgabe 7.3): Dreieckslast 0 … q0 über 3a, F oben am Arm."""
    abb = Abbildung(640, 300, "Abgewinkelter Träger")
    x0, y, s = 70, 220, 140                      # s = px je a
    xB, xE = x0 + 2 * s, x0 + 3 * s
    e = abb.ebene("system", "System")
    e.append(balkenzug([(x0, y), (xE, y), (xE, y - s)]))
    e.append(festlager(x0, y + 3.5, label="A", label_pos=(-20, 12)))
    e.append(loslager(xB, y + 3.5, label="B", label_pos=(-20, 12)))
    e.append(streckenlast(x0, xE - 4, y - 4, 0, 0.75 * s, label="", n=18))
    e.append(text(xE - 18, y - 0.75 * s / 2 - 4, "q_0", ROT, anker="end"))
    e.append(kraft(xE, y - s, 0, "F", laenge=60, label_seite=-1))
    e.append(mass(x0, y + 26, xB, y + 26, "2a", abstand=-22))
    e.append(mass(xB, y + 26, xE, y + 26, "a", abstand=-22))
    e.append(mass(xE + 4, y, xE + 4, y - s, "a", abstand=-30))
    return abb.speichern(ZIEL / "aufgabe73.svg")


def aufgabe_konisch():
    """Konischer Zugstab: links eingespannt, rechts Zugkraft F."""
    abb = Abbildung(640, 250, "Konischer Zugstab")
    x0, x1, y, h0, h1 = 80, 520, 110, 55, 11
    e = abb.ebene("system", "System")
    e.append(f'<polygon points="{x0},{y - h0} {x1},{y - h1} {x1},{y + h1} {x0},{y + h0}" fill="{FARBE["bauteil"]}" stroke="#000" stroke-width="1.25"/>')
    e.append(einspannung(x0, y, 2 * h0 + 16))
    e.append(linie(x0, y, x1, y, GRAU, 0.8, "8 3 2 3"))
    e.append(pfeil(x0 + 4, y, x0 + 64, y, GR, 1.6, (10, 6)))
    e.append(text(x0 + 58, y + 17, "x, u(x)", GR, anker="start"))
    e.append(kraft(x1 + 4, y, 0, "F", laenge=55, ziehend=True))
    e.append(text(x0 + 16, y - h0 - 16, "A_0", GR, anker="start"))
    e.append(text(x1 - 4, y - h1 - 16, "A_1", GR, anker="end"))
    e.append(text((x0 + x1) / 2, y - (h0 + h1) / 2 - 18, "E, A(x)", GR))
    e.append(mass(x0, y + h0, x1, y + h0, "L", abstand=-34))
    return abb.speichern(ZIEL / "aufgabe-konisch.svg")


def federsystem_beispiel():
    """Gesamtsystem (Lagerung, Kräfte, Freiheitsgrade) für das marimo-Beispiel: Ebenen aus federsystem.svg,
    Ausschnitt ohne Freischnitt. Liegt in beispiele/public/ und wird beim Export mitgenommen."""
    import re
    from ebenen_export import nur_ebenen
    svg = (ZIEL / "federsystem.svg").read_text(encoding="utf-8")
    svg = nur_ebenen(svg, ["system", "last", "dof"])
    svg = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"', 'width="680" height="265" viewBox="40 20 680 265"', svg, count=1)
    ziel = ZIEL.parent.parent / "beispiele" / "public" / "federsystem-system.svg"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(svg, encoding="utf-8")
    return ziel


if __name__ == "__main__":
    for fn in (kurve, traeger71, eigengewicht, federsystem, kpq, federsystem_3dof, aufgabe73, aufgabe_konisch,
               federsystem_beispiel):
        print(fn())

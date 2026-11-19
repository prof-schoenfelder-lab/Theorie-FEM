"""Grafiken zu Vorlesung 3: Normalkraftstab, von Ritz zur FEM.

Beispiel aus den Tafelbildern (1-Ritz2FEM, 1-FEM-Inzidenzmatrix): konischer Stab, links gelagert,
rechts Zugkraft F. E = 70000 MPa, L = 1000 mm, F = 5000 N, A0 = 100 mm², A1 = 20 mm²,
drei Elemente gleicher Länge mit der Querschnittsfläche in Elementmitte.
"""

import math
import re
from pathlib import Path

from fractions import Fraction

from grafiken_ritz import RITZ, _bruch, _stab, ritz
from nlzeichnen import Diagramm, feder, flaeche, notiz, wandgelenk
from tmzeichnen import (FARBE, SCHRIFT, Abbildung, _tspans, einspannung, f, kraft, kreis, linie, loslager, mass,
                        nummer, pfeil, polylinie, text)

ZIEL = Path(__file__).resolve().parent.parent / "grafiken" / "stab"
EX, FE, GR = FARBE["linear"], FARBE["nichtlinear"], FARBE["mass"]
GRAU = "#7a7a7a"

E, L, F, A0, A1 = 70000.0, 1000.0, 5000.0, 100.0, 20.0
N_EL = 3


def A(x):
    return A0 - (A0 - A1) / L * x


def u_exakt(x):
    return F / E * L / (A0 - A1) * math.log(A0 / A(x))


def fem(n):
    """Knotenverschiebungen und Elementspannungen für n gleich lange Elemente."""
    le = L / n
    k = [E * A((e + 0.5) * le) / le for e in range(n)]
    p = [0.0]
    for e in range(n):                       # statisch bestimmt: jede Feder trägt F
        p.append(p[-1] + F / k[e])
    sig = [F / A((e + 0.5) * le) for e in range(n)]
    return p, sig


def _fx(x, y, label, farbe, g=19, anker="middle"):
    """Formel in Latin Modern; *K* setzt Vektoren und Matrizen fett und aufrecht (wie \\mathbf)."""
    teile = []
    for i, stueck in enumerate(re.split(r"\*([^*]+)\*", label)):
        if not stueck:
            continue
        if i % 2:
            teile.append(f'<tspan font-weight="bold" font-style="normal">{_tspans(stueck, italic=False)}</tspan>')
        else:
            teile.append(_tspans(stueck))
    return (f'<text x="{f(x)}" y="{f(y + 0.34 * g)}" fill="{farbe}" stroke="#ffffff" stroke-width="4" '
            f'stroke-linejoin="round" paint-order="stroke" font-family="{SCHRIFT}" font-size="{f(g)}" '
            f'font-style="italic" text-anchor="{anker}" xml:space="preserve">{"".join(teile)}</text>')


def _klammer(x, y0, y1, links=True, b=8):
    """Eckige Klammer einer Matrix oder eines Vektors."""
    s = 1 if links else -1
    return polylinie([(x + s * b, y0), (x, y0), (x, y1), (x + s * b, y1)], "#000000", 1.3)


KO = FARBE["koord"]
LAST = FARBE["last"]


def _dof(x, y, label, ueber, laenge=46):
    """Freiheitsgrad kräftig auf der Mittellinie, beginnt immer am Knoten (nicht verschieblich);
    Label über dem Bauteil. Kräfte am selben Knoten werden längs ihrer Wirkungslinie verschoben."""
    return (pfeil(x, y, x + laenge, y, GR, 2.8, (14, 9))
            + text(x + laenge / 2, y - ueber - 20, label, GR, 21))


def _kraft(x_von, x_bis, y, label, ueber=0):
    """Kräftige Einzelkraft auf der Mittellinie von x_von nach x_bis; Label über dem Pfeil."""
    return (pfeil(x_von, y, x_bis, y, LAST, 3.0, (18, 11))
            + text((x_von + x_bis) / 2, y - max(24, ueber + 18), label, LAST, 23))


def _x_achse(x, y, label="x", laenge=58):
    """Koordinate im Ursprung auf der Mittellinie. Beginnt dort auch ein Freiheitsgrad, ist die Koordinate
    länger als der Freiheitsgrad, damit ihre Spitze und ihr Label daneben sichtbar bleiben."""
    return (pfeil(x, y, x + laenge, y, KO, 1.25, (9, 6))
            + text(x + laenge + 7, y, label, KO, 21, anker="start"))


def _element_kasten(x0, x1, y, h, gefuellt=True):
    teile = []
    if gefuellt:
        teile.append(f'<rect x="{x0}" y="{y - h}" width="{x1 - x0}" height="{2 * h}" fill="{FARBE["bauteil"]}" '
                     f'stroke="{GRAU}" stroke-width="1" stroke-dasharray="5 3"/>')
    teile.append(linie(x0, y, x1, y, "#555555", 2.2))
    return "".join(teile)


def system():
    abb = Abbildung(820, 470, "Konischer Stab: System, Elemente und Freiheitsgrade")
    x0, lp, y = 120, 540, 150
    x1 = x0 + lp
    s = 0.45                                   # px je mm² halbe Höhe
    X = lambda xm: x0 + xm / L * lp

    e = abb.ebene("stab", "Stab")
    e.append(polylinie([(x0, y - s * A0), (x1, y - s * A1), (x1, y + s * A1), (x0, y + s * A0)],
                       "#000000", 1.25, FARBE["bauteil"], schliessen=True))
    e.append(linie(x0, y, x1, y, GRAU, 0.8, "8 3 2 3"))
    e.append(wandgelenk(x0, y, 60))
    e.append(loslager(x1, y, 12))
    e.append(_x_achse(x0, y))

    e = abb.ebene("last", "Last")
    e.append(_kraft(x1 + 4, x1 + 84, y, "F", s * A1))
    e = abb.ebene("last2", "Last neben p_4")                 # verschoben, wenn p_4 am Knoten gezeigt wird
    e.append(_kraft(x1 + 56, x1 + 136, y, "F", s * A1))

    e = abb.ebene("mass", "Bemaßung")
    ym = y + s * A0 + 38                         # Maß L, Hilfslinien bis an beide Stabenden
    e.append(linie(x0, y + s * A0 + 4, x0, ym + 6, GR, 0.8))
    e.append(linie(x1, y + s * A1 + 4, x1, ym + 6, GR, 0.8))
    e.append(mass(x0, ym, x1, ym, "L", abstand=0, hilfslinien=False))
    e.append(text(x0 + 16, y + s * A0 - 16, "A_0", GR, anker="start"))
    e.append(text(x1 - 4, y - s * A1 - 16, "A_1", GR, anker="end"))
    e.append(text(X(500), y + s * A(500) + 18, "E, A(x)", GR))

    # Elemente: abgestufte Querschnitte (Fläche in Elementmitte)
    e = abb.ebene("elemente", "Elemente")
    le = lp / N_EL
    for i in range(N_EL):
        xa, xb = x0 + i * le, x0 + (i + 1) * le
        h = s * A((i + 0.5) * L / N_EL)
        e.append(f'<rect x="{xa}" y="{y - h}" width="{le}" height="{2 * h}" fill="none" '
                 f'stroke="{FE}" stroke-width="1.4" stroke-dasharray="6 4"/>')
        e.append(nummer((xa + xb) / 2, y - s * A0 - 52, i + 1, r=11))
    for i in range(N_EL + 1):
        e.append(kreis(x0 + i * le, y, 4.2))

    e = abb.ebene("sysdof", "Systemfreiheitsgrade")
    e.append(text(x0, y - s * A0 - 20, "p_1 = [0]", GR, 21))
    for i in range(1, N_EL + 1):
        e.append(_dof(x0 + i * le, y, f"p_{i + 1}", s * A((i + 0.5) * L / N_EL) if i < N_EL else s * A1 + 4))

    # Einzelne Elemente (auseinandergezogen) mit Elementfreiheitsgraden
    e = abb.ebene("einzeln", "Einzelne Elemente")
    ye, luecke, ba = 395, 70, 20
    for i in range(N_EL):
        xa = x0 - 40 + i * (le + luecke)
        xb = xa + le
        n = i + 1
        e.append(_element_kasten(xa, xb, ye, ba))
        e.append(kreis(xa, ye, 4.2))
        e.append(kreis(xb, ye, 4.2))
        e.append(nummer((xa + xb) / 2 - 10, ye - 50, n, r=11))
        e.append(_x_achse(xa, ye, f"x^{{({n})}}", laenge=96))
        e.append(_dof(xa, ye, f"p_2^{{({n})}}", ba, laenge=40))
        e.append(_dof(xb, ye, f"p_1^{{({n})}}", ba, laenge=40))
        e.append(mass(xa, ye + ba, xb, ye + ba, f"L^{{({n})}}", abstand=-30))

    e = abb.ebene("verbindung", "Verbindung Element – System")
    for i in range(N_EL):
        xa = x0 - 40 + i * (le + luecke)
        for xk, xs in ((xa, x0 + i * le), (xa + le, x0 + (i + 1) * le)):
            e.append(linie(xk, ye - 6, xs, y + s * A(i * L / N_EL) + 6, GRAU, 0.9, "4 3"))
    return abb.speichern(ZIEL / "system.svg")


def element():
    abb = Abbildung(800, 560, "Normalkraftstab als finites Element")
    xa, xb, y = 230, 560, 95

    e = abb.ebene("element", "Element")
    e.append(_element_kasten(xa, xb, y, 22))
    e.append(kreis(xa, y, 4.6))
    e.append(kreis(xb, y, 4.6))
    e.append(text((xa + xb) / 2 + 30, y - 46, "E^e, A^e", GR))
    e.append(linie((xa + xb) / 2 + 10, y - 34, (xa + xb) / 2 - 4, y - 16, GR, 0.9))
    e.append(mass(xa, y + 22, xb, y + 22, "L^e", abstand=-30))
    e.append(_x_achse(xa, y, "x^e", laenge=110))

    e = abb.ebene("dof", "Elementfreiheitsgrade")
    e.append(_dof(xa, y, "p_2^e", 22, laenge=50))
    e.append(_dof(xb, y, "p_1^e", 22, laenge=50))

    e = abb.ebene("kraefte", "Knotenkräfte")                # längs der Wirkungslinie neben die Freiheitsgrade geschoben
    e.append(_kraft(xa - 84, xa - 4, y, "q_2^e", 22))
    e.append(_kraft(xb + 62, xb + 142, y, "q_1^e", 22))

    # linkes Diagramm: Verschiebungsansatz
    D = Diagramm(90, 470, 260, 210, 1.0, 1.0)
    e = abb.ebene("ansatz_achsen", "Achsen Ansatz")
    e.append(D.achsen("x^e", "u^e", [(0, "0"), (1, "L^e")], [], groesse=19))
    e = abb.ebene("ansatz", "Linearer Ansatz")
    e.append(D.kurve(punkte=[(0, 0.32), (1, 0.82)], farbe=FE))
    e.append(D.linie(0, 0.82, 1, 0.82, GRAU, 0.9, "4 3"))
    e.append(D.linie(1, 0, 1, 1.0, GR, 0.9, "4 3"))
    e.append(D.text(0, 0.32, "u^e([0]) = p_2^e", FE, dx=-8, anker="end", groesse=16))
    e.append(D.text(0, 0.82, "u^e(L^e) = p_1^e", FE, dx=-8, anker="end", groesse=16))
    e.append(D.text(0.55, 0.57, "u^e(x^e)", FE, dx=10, dy=24, anker="start"))
    e.append(D.punkt(0, 0.32, FE, 3.6))
    e.append(D.punkt(1, 0.82, FE, 3.6))

    # rechtes Diagramm: Ansatzfunktionen
    D2 = Diagramm(470, 470, 240, 210, 1.0, 1.0)
    e = abb.ebene("form_achsen", "Achsen Ansatzfunktionen")
    e.append(D2.achsen("x^e", "N", [(0, "0"), (1, "L^e")], [(1, "1")], groesse=19))
    e = abb.ebene("formfkt", "Ansatzfunktionen")
    e.append(D2.kurve(punkte=[(0, 0), (1, 1)], farbe=FE))
    e.append(D2.kurve(punkte=[(0, 1), (1, 0)], farbe=FE, strich="9 5"))
    X, Y = D2.px(0.8, 0.8)
    e.append(_bruch(X + 34, Y + 14, "", "x^e", "L^e", "", FE, 19))
    X, Y = D2.px(0.2, 0.8)
    e.append(_bruch(X + 62, Y - 4, "[1] −", "x^e", "L^e", "", FE, 19))
    e.append(D2.linie(1, 0, 1, 1, GRAU, 0.9, "4 3"))
    e.append(D2.linie(0, 1, 1, 1, GRAU, 0.9, "4 3"))

    # linkes Diagramm (statt Ansatz): Ableitungen der Ansatzfunktionen, je Element konstant ±1/L^e
    D3 = Diagramm(90, 470, 260, 210, 1.0, 1.0, ymin=-1.0)
    e = abb.ebene("ableitung_achsen", "Achsen Ableitung")
    e.append(D3.achsen("x^e", "N′", [(1, "")], [], groesse=19))
    X, Y = D3.px(1, 0)
    e.append(text(X + 10, Y + 16, "L^e", "#000000", 15, anker="start"))
    e = abb.ebene("ableitung", "Ableitung der Ansatzfunktionen")
    e.append(D3.kurve(punkte=[(0, 0.6), (1, 0.6)], farbe=FE))
    e.append(D3.kurve(punkte=[(0, -0.6), (1, -0.6)], farbe=FE, strich="9 5"))
    e.append(D3.linie(1, -1.0, 1, 1.0, GRAU, 0.9, "4 3"))
    X, Y = D3.px(0.5, 0.6)
    e.append(_bruch(X, Y - 30, "", "[1]", "L^e", "", FE))
    X, Y = D3.px(0.5, -0.6)
    e.append(_bruch(X + 8, Y + 30, "−", "[1]", "L^e", "", FE))

    # Ersatzfeder unter dem Element: der Stab ist eine Feder
    yf = 240
    e = abb.ebene("feder", "Ersatzfeder")
    e.append(feder(xa, yf, xb, yf, 7, 11, anteil=0.6))
    e.append(kreis(xa, yf, 4.6))
    e.append(kreis(xb, yf, 4.6))
    e.append(_bruch((xa + xb) / 2 + 28, yf + 44, "c^e =", "E^e A^e", "L^e", "", GR, 21))
    e.append(_kraft(xa - 84, xa - 4, yf, "q_2^e"))
    e.append(_kraft(xb + 4, xb + 84, yf, "q_1^e"))
    return abb.speichern(ZIEL / "element.svg")


def ergebnis():
    abb = Abbildung(860, 400, "Konischer Stab: FEM-Lösung und exakte Lösung")
    p, sig = fem(N_EL)
    le = L / N_EL

    Du = Diagramm(110, 330, 280, 250, 1000, 1.6)
    e = abb.ebene("achsen", "Achsen")
    e.append(Du.achsen("x", "u [in mm]", [(0, "0"), (500, "500"), (1000, "1000")],
                       [(0.4, "0,4"), (0.8, "0,8"), (1.2, "1,2"), (1.6, "1,6")], raster=True))
    Ds = Diagramm(530, 330, 280, 250, 1000, 260)
    e.append(Ds.achsen("x", "σ [in MPa]", [(0, "0"), (500, "500"), (1000, "1000")],
                       [(50, "50"), (100, "100"), (150, "150"), (200, "200"), (250, "250")], raster=True))
    e.append(notiz(110 + 280, 362, ["x in mm"], "#444444", 13, anker="end"))
    e.append(notiz(530 + 280, 362, ["x in mm"], "#444444", 13, anker="end"))

    e = abb.ebene("exakt", "Exakte Lösung")
    e.append(Du.kurve(u_exakt, 0, L, farbe=EX))
    e.append(Ds.kurve(lambda x: F / A(x), 0, L, farbe=EX))
    e.append(Du.notiz(1000, u_exakt(L), ["exakt"], EX, dx=-8, dy=-10, anker="end"))
    e.append(Ds.notiz(1000, 250, ["exakt"], EX, dx=-8, dy=-6, anker="end"))

    e = abb.ebene("fem_u", "FEM Verschiebung")
    e.append(Du.kurve(punkte=[(i * le, p[i]) for i in range(N_EL + 1)], farbe=FE))
    for i in range(N_EL + 1):
        e.append(Du.punkt(i * le, p[i], FE, 3.8))
    e.append(Du.notiz(1000, p[-1], ["FEM, 3 Elemente"], FE, dx=-40, dy=34, anker="end"))

    e = abb.ebene("fem_s", "FEM Spannung")
    stufen = []
    for i in range(N_EL):
        stufen += [(i * le, sig[i]), ((i + 1) * le, sig[i])]
    e.append(Ds.flaeche([(0, 0)] + stufen + [(L, 0)], FARBE["bereich_nl"], 0.9))
    e.append(Ds.kurve(punkte=stufen, farbe=FE))
    e.append(Ds.kurve(lambda x: F / A(x), 0, L, farbe=EX))
    e.append(Ds.notiz(1000, sig[-1], ["FEM: konstant", "je Element"], FE, dx=-8, dy=24, anker="end"))
    return abb.speichern(ZIEL / "ergebnis.svg")


def zusammenbau():
    """Drei Stabelemente mit konstantem Querschnitt und das Besetzungsschema von K_sys
    (Beiträge der Elemente, Randbedingung)."""
    abb = Abbildung(820, 470, "Zusammenbau der Systemsteifigkeitsmatrix")
    p, _ = fem(N_EL)
    y = 85
    X = [100, 250, 400, 550]
    sq = 0.3                                     # px je mm² halbe Höhe
    hq = [sq * A((i + 0.5) * L / N_EL) for i in range(N_EL)]   # Fläche in Elementmitte
    ROTF = FARBE["nichtlinear"]

    e = abb.ebene("system", "Stabelemente")
    e.append(wandgelenk(X[0], y, 60))
    e.append(loslager(X[-1], y, 12))
    for i in range(N_EL):
        e.append(f'<rect x="{X[i]}" y="{f(y - hq[i])}" width="{X[i + 1] - X[i]}" height="{f(2 * hq[i])}" '
                 f'fill="{FARBE["bauteil"]}" stroke="#000" stroke-width="1.25"/>')
        e.append(text((X[i] + X[i + 1]) / 2 + 12, y - hq[i] - 18, f"c^{{({i + 1})}}", "#000000", 20))
    e.append(linie(X[0], y, X[-1], y, GRAU, 0.8, "8 3 2 3"))
    for xk in X:
        e.append(kreis(xk, y, 4.6))
    e.append(_x_achse(X[0], y, laenge=46))
    e.append(text(X[0], y - hq[0] - 20, "p_1 = [0]", GR, 19))
    for i in range(1, N_EL + 1):
        e.append(_dof(X[i], y, f"p_{i + 1}", hq[i] if i < N_EL else hq[-1] + 4))
    e.append(_kraft(X[-1] + 56, X[-1] + 136, y, "F", hq[-1]))

    # Besetzungsschema 4 × 4
    w, h = 88, 54
    MX, MY = 235, 185
    cx = lambda c: MX + c * w + w / 2
    cy = lambda r: MY + r * h + h / 2
    e = abb.ebene("raster", "Raster K_sys")
    for i in range(5):
        e.append(linie(MX, MY + i * h, MX + 4 * w, MY + i * h, "#d5d9de", 0.8))
        e.append(linie(MX + i * w, MY, MX + i * w, MY + 4 * h, "#d5d9de", 0.8))
    e.append(_klammer(MX - 4, MY - 4, MY + 4 * h + 4))
    e.append(_klammer(MX + 4 * w + 4, MY - 4, MY + 4 * h + 4, links=False))
    e.append(_fx(MX - 16, MY + 2 * h, "*K*_{sys} =", "#000000", 22, anker="end"))
    for c in range(4):
        e.append(text(cx(c), MY - 22, f"p_{c + 1}", GR, 18))

    for k in range(N_EL):                        # Element k+1 koppelt die Systemfreiheitsgrade k und k+1
        e = abb.ebene(f"block{k + 1}", f"Beitrag Element {k + 1}")
        e.append(f'<rect x="{f(MX + k * w + 4)}" y="{f(MY + k * h + 4)}" width="{f(2 * w - 8)}" '
                 f'height="{f(2 * h - 8)}" rx="6" fill="{ROTF}" fill-opacity="0.10" stroke="{ROTF}" '
                 f'stroke-width="1.4"/>')
        for r in (k, k + 1):
            for c in (k, k + 1):
                lab = f"c^{{({k + 1})}}" if r == c else f"−c^{{({k + 1})}}"
                dy = 0
                if r == c == k + 1 and k + 1 < N_EL:          # unten rechts, Nachbarelement folgt
                    dy = -13
                elif r == c == k and k > 0:                   # oben links, wird addiert
                    lab, dy = f"+ c^{{({k + 1})}}", 13
                e.append(_fx(cx(c), cy(r) + dy, lab, ROTF, 19))

    e = abb.ebene("nullen", "Nullen")
    for r in range(4):
        for c in range(4):
            if abs(r - c) > 1:
                e.append(_fx(cx(c), cy(r), "[0]", "#7a7a7a", 19))

    VX, QX = MX + 4 * w + 52, MX + 4 * w + 150
    e = abb.ebene("vektoren", "p_sys und q_sys")
    for x0 in (VX, QX):
        e.append(_klammer(x0 - 24, MY - 4, MY + 4 * h + 4))
        e.append(_klammer(x0 + 24, MY - 4, MY + 4 * h + 4, links=False))
    for r in range(4):
        e.append(_fx(VX, cy(r), f"p_{r + 1}", GR, 19))
    for r, (lab, farbe) in enumerate((("q_1", FARBE["last"]), ("[0]", "#000000"), ("[0]", "#000000"),
                                      ("F", FARBE["last"]))):
        e.append(_fx(QX, cy(r), lab, farbe, 19))
    e.append(_fx((VX + QX) / 2, MY + 2 * h, "=", "#000000", 22))

    e = abb.ebene("rb", "Randbedingung p_1 = 0")
    grau = 'fill="#7a7a7a" fill-opacity="0.18"'
    e.append(f'<rect x="{MX}" y="{MY}" width="{4 * w}" height="{h}" {grau}/>')
    e.append(f'<rect x="{MX}" y="{MY + h}" width="{w}" height="{3 * h}" {grau}/>')
    e.append(linie(MX - 2, cy(0), QX + 22, cy(0), "#444444", 1.6))
    e.append(linie(cx(0), MY - 2, cx(0), MY + 4 * h + 2, "#444444", 1.6))

    e = abb.ebene("loesung", "Lösung")
    for i in range(1, N_EL + 1):
        e.append(_fx(X[i], y + 52, f"p_{i + 1} = [{p[i]:.3f} mm]".replace(".", ","), ROTF, 17))
    e.append(_fx(X[0], y + 52, f"q_1 = [−{F:.0f} N]", FARBE["last"], 17))
    return abb.speichern(ZIEL / "zusammenbau.svg")


def zusammenfassung():
    """Ablauf der FEM (Pre, Solution, Post) und Vergleich Ritz – FEM."""
    abb = Abbildung(820, 480, "Zusammenfassung Vorlesung 3")
    spalten = [
        ("pre", "Preprocessor", EX, [("1a  Elementtyp wählen", "*K*^e, *p*^e, *N*^e"),
                                     ("1b  Vernetzen", "*p*_{sys}, *q*_{sys}"),
                                     ("2  Material und Geometrie", "*K*^e"),
                                     ("3  Konnektivität", "*Λ*^e")]),
        ("solution", "Solution", FE, [("4  Zusammenbau", "*K*_{sys} = [Σ] *Λ*^{eT}*K*^e*Λ*^e"),
                                      ("5  Gleichungssystem lösen", "*K*_{sys} *p*_{sys} = *q*_{sys}")]),
        ("post", "Postprocessor", GR, [("6  Elementverschiebungen", "*p*^e = *Λ*^e *p*_{sys}"),
                                       ("7  Verschiebungsverlauf", "u^e(x^e) = *N*^e*Λ*^e *p*_{sys}"),
                                       ("8  Dehnungen, Spannungen", ["ε^e = *N*^e′*Λ*^e *p*_{sys}", "σ^e = E^e ε^e"])]),
    ]
    bx, bw, bh, abst, y0 = [20, 290, 560], 240, 80, 16, 80
    for j, (id_, titel, farbe, kaesten) in enumerate(spalten):
        e = abb.ebene(id_, titel)
        e.append(text(bx[j] + bw / 2, 40, titel, farbe, 27))
        for i, (schritt, formel) in enumerate(kaesten):
            yt = y0 + i * (bh + abst)
            e.append(f'<rect x="{bx[j]}" y="{yt}" width="{bw}" height="{bh}" rx="8" fill="#ffffff" '
                     f'stroke="{farbe}" stroke-width="1.6"/>')
            e.append(text(bx[j] + 14, yt + 22, schritt, "#000000", 19, anker="start"))
            if isinstance(formel, list):                   # zwei Formeln untereinander
                for k, fo in enumerate(formel):
                    e.append(_fx(bx[j] + bw / 2, yt + 44 + k * 22, fo, "#000000", 17))
            else:
                e.append(_fx(bx[j] + bw / 2, yt + 55, formel, "#000000", 18))
        if j:
            e.append(pfeil(bx[j] - 26, y0 + bh / 2, bx[j] - 4, y0 + bh / 2, "#7a7a7a", 2.0, (10, 7)))

    # Vergleich: ein Polynom für den ganzen Stab (Ritz, Grad 2) – stückweise linear (FEM, 3 Elemente)
    p, _ = fem(N_EL)
    u2, _ = ritz(2)
    e = abb.ebene("vergleich", "Ritz und FEM")
    for x0, titel in ((80, "Ritz: ein Ansatz für den ganzen Stab"), (480, "FEM: einfacher Ansatz je Element")):
        D = Diagramm(x0, 420, 290, 300, L, 1.6)
        e.append(text(x0 + 145, 50, titel, "#000000", 22))
        e.append(D.achsen("x", "u", [(L, "L")], []))
        e.append(D.kurve(u_exakt, 0, L, farbe=EX))
        e.append(D.notiz(L, u_exakt(L), ["exakt"], EX, dx=-8, dy=-12, anker="end"))
        if x0 == 80:
            e.append(D.kurve(u2, 0, L, farbe=FE))
            e.append(D.notiz(0.62 * L, u2(0.62 * L), ["Polynom 2. Grades"], FE, dx=10, dy=22, anker="start"))
        else:
            for i in (1, 2):
                e.append(D.linie(i * L / N_EL, 0, i * L / N_EL, 1.6, GRAU, 0.9, "4 3"))
            e.append(D.kurve(punkte=[(i * L / N_EL, p[i]) for i in range(N_EL + 1)], farbe=FE))
            for i in range(N_EL + 1):
                e.append(D.punkt(i * L / N_EL, p[i], FE, 3.8))
            e.append(D.notiz(0.62 * L, 0.55, ["linear je Element"], FE, dx=10, dy=22, anker="start"))
    return abb.speichern(ZIEL / "zusammenfassung.svg")


# ---------------------------------------------------------------- Einstieg: abgesetzte Welle mit Ritz
WE, WF = 210000.0, 1500.0                        # Welle aus 02-welle-ritz: Stahl, F drückt (nach links)
WL, WD = [240, 160, 240], [11, 25, 11]


def _welle_ritz(n):
    """Ritz mit u = Σ b_i ξ^i (ξ = x/640) für die abgesetzte Welle, exakt mit Brüchen gerechnet."""
    gr = [Fraction(0), Fraction(240, 640), Fraction(400, 640), Fraction(1)]
    I = lambda m: sum(Fraction(WD[k] ** 2) * (gr[k + 1] ** (m + 1) - gr[k] ** (m + 1)) / (m + 1) for k in range(3))
    M = [[i * j * I(i + j - 2) for j in range(1, n + 1)] + [Fraction(-int(WF))] for i in range(1, n + 1)]
    for i in range(n):                            # Gauß-Elimination
        for j in range(i + 1, n):
            fa = M[j][i] / M[i][i]
            M[j] = [a - fa * b for a, b in zip(M[j], M[i])]
    b = [Fraction(0)] * n
    for i in reversed(range(n)):
        b[i] = (M[i][n] - sum(M[i][j] * b[j] for j in range(i + 1, n))) / M[i][i]
    fak = math.pi * WE / (4 * 640)
    b = [float(v) / fak for v in b]
    u = lambda x: sum(bi * (x / 640) ** (i + 1) for i, bi in enumerate(b))
    sig = lambda x: WE * sum(bi * (i + 1) * (x / 640) ** i / 640 for i, bi in enumerate(b))
    return u, sig


def _welle_exakt():
    A = [math.pi * d * d / 4 for d in WD]
    knoten = [0.0]
    for l, a in zip(WL, A):
        knoten.append(knoten[-1] - WF * l / (WE * a))
    sig = [-WF / a for a in A]
    return knoten, sig


def welle_ritz():
    """Die abgesetzte Welle: Ritz mit einem Polynom scheitert, Elemente (ein Abschnitt je Element) sind exakt."""
    abb = Abbildung(820, 600, "Abgesetzte Welle: Ritz und Elemente")
    s, sd = 0.9, 3.0
    x0, y = 110, 70
    xa = [x0, x0 + 240 * s, x0 + 400 * s, x0 + 640 * s]
    h = [d / 2 * sd for d in WD]
    knoten, sig = _welle_exakt()
    xs = [0, 240, 400, 640]

    e = abb.ebene("system", "Welle")
    e.append(einspannung(xa[0], y, 80))
    for i in range(3):
        e.append(_stab(xa[i], xa[i + 1], y, h[i]))
    e.append(_x_achse(xa[0], y, laenge=50))
    e.append(_kraft(xa[3] + 84, xa[3] + 4, y, "F", h[0]))
    for i, d in enumerate(WD):
        e.append(notiz((xa[i] + xa[i + 1]) / 2, y - h[1] - 14, [f"Ø {d}"], "#444444", 15, anker="middle"))

    Du = Diagramm(x0, 340, 640 * s, 180, 640, 0.0, ymin=-0.045)
    Ds = Diagramm(x0, 560, 640 * s, 170, 640, 0.0, ymin=-25.0)
    e = abb.ebene("exakt", "Exakte Lösung")
    e.append(Du.achsen("x", "u [in mm]", [(640, "L")], [(-0.02, "−0,02"), (-0.04, "−0,04")], achse_y0=0.0))
    e.append(Du.kurve(punkte=list(zip(xs, knoten)), farbe=EX))
    e.append(Du.notiz(640, knoten[-1], ["exakt"], EX, dx=8, dy=16, anker="start"))
    e.append(Ds.achsen("x", "σ [in MPa]", [(640, "L")], [(-10, "−10"), (-20, "−20")], achse_y0=0.0))
    stufen = []
    for i in range(3):
        stufen += [(xs[i], sig[i]), (xs[i + 1], sig[i])]
    e.append(Ds.kurve(punkte=stufen, farbe=EX))
    e.append(Ds.notiz(640, sig[-1], ["exakt"], EX, dx=8, anker="start"))

    for n, farbe, name in ((3, RITZ[1], "ritz3"), (8, RITZ[2], "ritz8")):
        u, sg = _welle_ritz(n)
        e = abb.ebene(name, f"Ritz Grad {n}")
        e.append(Du.kurve(u, 0, 640, farbe=farbe, breite=2.2))
        e.append(Ds.kurve(sg, 0, 640, farbe=farbe, breite=2.2, clip=False))
        e.append(Du.notiz(640, u(640), [f"Grad {n}"], farbe, dx=8, dy=-8, anker="start", groesse=14))

    e = abb.ebene("elemente", "Ein Element je Abschnitt")
    for i in (1, 2):
        e.append(linie(xa[i], y - h[1] - 8, xa[i], 560, GRAU, 0.9, "4 3"))
    for xk in xa:
        e.append(kreis(xk, y, 4.6))
    e.append(Du.kurve(punkte=list(zip(xs, knoten)), farbe=FE, breite=2.0, strich="7 4"))
    for xk, uk in zip(xs, knoten):
        e.append(Du.punkt(xk, uk, FE, 4.0))
    e.append(Ds.kurve(punkte=stufen, farbe=FE, breite=2.0, strich="7 4"))
    e.append(Du.notiz(320, knoten[2], ["3 Elemente = exakt"], FE, dx=-6, dy=26, anker="end"))
    return abb.speichern(ZIEL / "welle-ritz.svg")


# ---------------------------------------------------------------- Matrizenrechnung
def _klammer_rund(x, y0, y1, links=True):
    s = 1 if links else -1
    m = (y0 + y1) / 2
    return f'<path d="M {f(x + s * 7)},{f(y0)} Q {f(x - s * 5)},{f(m)} {f(x + s * 7)},{f(y1)}" fill="none" stroke="#000" stroke-width="1.4"/>'


def _matrix(x, y, zeilen, w=46, h=34, g=19, farbe="#000000", fuellung=None):
    """Matrix mit runden Klammern; (x, y) = linke obere Ecke des Inhalts. fuellung: {(r, c): Farbe}.
    Gibt (svg, Breite) zurück."""
    teile = []
    nz, ns = len(zeilen), max(len(r) for r in zeilen)
    for (r, c), fb in (fuellung or {}).items():
        teile.append(f'<rect x="{f(x + c * w + 2)}" y="{f(y + r * h + 2)}" width="{f(w - 4)}" height="{f(h - 4)}" '
                     f'rx="4" fill="{fb}"/>')
    for r, zeile in enumerate(zeilen):
        for c, t in enumerate(zeile):
            if isinstance(t, tuple):
                teile.append(_bruch(x + c * w + w / 2 + (6 if t[0] else 0), y + r * h + h / 2, t[0], t[1], t[2], "", farbe, g))
            elif t:
                teile.append(_fx(x + c * w + w / 2, y + r * h + h / 2, t, farbe, g))
    teile.append(_klammer_rund(x - 4, y - 2, y + nz * h + 2))
    teile.append(_klammer_rund(x + ns * w + 4, y - 2, y + nz * h + 2, links=False))
    return "".join(teile), ns * w


def _zeile(x, y, teile, g=22):
    """Reihe aus Formeln und Matrizen nebeneinander; teile: Text oder (zeilen, w, h, fuellung)."""
    out = []
    for t in teile:
        if isinstance(t, str):
            if t.startswith("^"):                        # Exponent direkt an die Klammer davor
                x -= 4
            breite = 11 * len(t.replace("*", "").replace("_", "").replace("^", "").replace("{", "").replace("}", "")) * g / 22 + 12
            out.append(_fx(x + 6, y, t, "#000000", g, anker="start"))
            x += breite
        else:
            zeilen, w, h, fuell = t
            svg, b = _matrix(x + 10, y - len(zeilen) * h / 2, zeilen, w, h, fuellung=fuell)
            out.append(svg)
            x += b + 22
    return "".join(out)


def _durchgestrichen(x0, y0, x1, y1):
    return linie(x0, y0, x1, y1, "#d40000", 2.0) + linie(x0, y1, x1, y0, "#d40000", 2.0)


def matrizen():
    abb = Abbildung(820, 680, "Matrizenrechnung")
    GE, BL, GN = "#fde9b8", "#d6e4f5", "#cfe8d2"         # Zeile, Spalte, Ergebnis (nur Markierung)
    A3 = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]

    e = abb.ebene("schreibweise", "Schreibweise")
    allg = [["A_{11}", "A_{12}", "…", "A_{1n}"], ["A_{21}", "A_{22}", "…", "A_{2n}"], ["⋮", "⋮", "", "⋮"],
            ["A_{m1}", "A_{m2}", "…", "A_{mn}"]]
    svg, b = _matrix(150, 120, allg, 62, 44, 21, fuellung={(1, c): GE for c in range(4)})
    e.append(_fx(130, 208, "*A* =", "#000000", 24, anker="end"))
    e.append(svg)
    e.append(text(150 + b + 20, 142, "Zeile 2", "#444444", 19, anker="start"))
    e.append(text(150 + 62 * 0 + 31, 92, "1. Index = Zeile", "#444444", 19, anker="start"))
    e.append(text(150 + 31, 335, "2. Index = Spalte", "#444444", 19, anker="start"))
    svg, b = _matrix(470, 360, [["a_1"], ["a_2"], ["⋮"], ["a_n"]], 50, 38, 21)
    e.append(_fx(450, 436, "*a* =", "#000000", 24, anker="end"))
    e.append(svg)
    e.append(_fx(470 + b + 22, 436, "= (a_1  a_2  …  a_n)^T", "#000000", 21, anker="start"))
    e.append(text(470, 530, "Vektor = Spaltenvektor", "#444444", 19, anker="start"))

    e = abb.ebene("addition", "Addition")
    G = lambda b_: [[f"{b_}_{{{r}{c}}}" for c in (1, 2, 3)] for r in (1, 2, 3)]
    S = [[f"A_{{{r}{c}}} + B_{{{r}{c}}}" for c in (1, 2, 3)] for r in (1, 2, 3)]
    e.append(_zeile(20, 260, ["*A* + *B* =", (S, 112, 46, None)], 22))
    e.append(_zeile(20, 110, ["*A* =", (G("A"), 52, 40, None), "  *B* =", (G("B"), 52, 40, None)], 22))
    e.append(text(30, 420, "komponentenweise, nur bei gleicher Größe", "#444444", 20, anker="start"))

    e = abb.ebene("multiplikation", "Multiplikation Zeile × Spalte")
    e.append(_zeile(20, 75, ["*A* =", (G("A"), 52, 36, None), "  *B* =", (G("B"), 52, 36, None)], 22))
    e.append(_zeile(20, 215, ["*A* *B* =", (G("A"), 52, 36, {(0, c): GE for c in range(3)}),
                              (G("B"), 52, 36, {(r, 0): BL for r in range(3)})], 22))
    w, hz = 52, 36                                          # Falk-Schema: A links unten, B rechts oben, AB rechts unten
    xa_, ya_ = 70, 470
    xb_, yb_ = 280, 330
    svg, _ = _matrix(xa_, ya_, G("A"), w, hz, fuellung={(0, c): GE for c in range(3)})
    e.append(svg)
    svg, _ = _matrix(xb_, yb_, G("B"), w, hz, fuellung={(r, 0): BL for r in range(3)})
    e.append(svg)
    erg = [["(*AB*)_{11}", "", ""], ["", "", ""], ["", "", ""]]
    svg, _ = _matrix(xb_, ya_, erg, w, hz, fuellung={(0, 0): GN})
    e.append(svg)
    e.append(_fx(xa_ + 1.5 * w, ya_ - 22, "*A*", "#000000", 22))
    e.append(_fx(xb_ + 3 * w + 26, yb_ + 1.5 * hz, "*B*", "#000000", 22, anker="start"))
    e.append(_fx(xb_ + 3 * w + 26, ya_ + 1.5 * hz, "*AB*", "#000000", 22, anker="start"))
    e.append(pfeil(xa_ + 3 * w + 8, ya_ + hz / 2, xb_ - 8, ya_ + hz / 2, "#7a7a7a", 1.6, (10, 7)))
    e.append(pfeil(xb_ + w / 2, yb_ + 3 * hz + 8, xb_ + w / 2, ya_ - 8, "#7a7a7a", 1.6, (10, 7)))
    e.append(text(500, 360, "Rechenschema:", "#444444", 19, anker="start"))
    e.append(text(500, 388, "B nach oben versetzt", "#444444", 19, anker="start"))
    e.append(_fx(40, 640, "(*AB*)_{11} = A_{11} B_{11} + A_{12} B_{21} + A_{13} B_{31}", "#000000", 22, anker="start"))

    e = abb.ebene("beispiele", "Beispiele")
    B33 = [["10", "20", "30"], ["40", "50", "60"], ["70", "80", "90"]]
    R33 = [["300", "360", "420"], ["660", "810", "960"], ["1020", "1260", "1500"]]
    B32 = [["10", "20"], ["40", "50"], ["70", "80"]]
    R32 = [["300", "360"], ["660", "810"], ["1020", "1260"]]
    B23 = [["10", "20", "30"], ["40", "50", "60"]]
    e.append(_zeile(20, 75, [(A3, 40, 30, None), (B33, 44, 30, None), "=", (R33, 56, 30, None)], 22))
    e.append(_zeile(20, 195, [(A3, 40, 30, None), (B32, 44, 30, None), "=", (R32, 56, 30, None)], 22))
    zeile3 = _zeile(20, 310, [(A3, 40, 30, None), (B23, 44, 30, None), "= ?"], 22)
    e.append(zeile3)
    e.append(_durchgestrichen(24, 262, 300, 358))
    e.append(_zeile(20, 445, [(A3, 40, 30, None), (B23, 44, 30, None), "^T =", (A3, 40, 30, None),
                              ([["10", "40"], ["20", "50"], ["30", "60"]], 44, 30, None), "=",
                              ([["140", "320"], ["320", "770"], ["500", "1220"]], 56, 30, None)], 22))

    e = abb.ebene("vektoren", "Vektoren")
    X = [["x_1"], ["x_2"], ["x_3"]]
    Y = [["y_1"], ["y_2"], ["y_3"]]
    for yy, wort in ((30, "Spaltenvektor · Spaltenvektor: geht nicht"), (180, "Zeilenvektor · Spaltenvektor = Zahl"),
                     (340, "Spaltenvektor · Zeilenvektor = Matrix"), (510, "Matrix · Spaltenvektor = Spaltenvektor")):
        e.append(text(30, yy, wort, "#444444", 19, anker="start"))
    e.append(_zeile(20, 95, ["*x* *y* =", (X, 40, 28, None), (Y, 40, 28, None), "= ?"], 22))
    e.append(_durchgestrichen(24, 51, 270, 139))
    e.append(_zeile(20, 250, ["*x*^T*y* =", ([["x_1", "x_2", "x_3"]], 40, 32, None), (Y, 40, 28, None),
                              "= x_1 y_1 + x_2 y_2 + x_3 y_3"], 22))
    e.append(_zeile(20, 415, ["*x* *y*^T =", (X, 40, 28, None), ([["y_1", "y_2", "y_3"]], 40, 32, None), "=",
                              ([[f"x_{r} y_{c}" for c in (1, 2, 3)] for r in (1, 2, 3)], 58, 28, None)], 22))
    e.append(_zeile(20, 590, ["*A* *x* =", (A3, 34, 28, None), (X, 40, 28, None), "=",
                              ([["x_1 + 2 x_2 + 3 x_3"], ["4 x_1 + 5 x_2 + 6 x_3"], ["7 x_1 + 8 x_2 + 9 x_3"]], 190, 28, None)], 22))

    e = abb.ebene("quadrat", "Quadrat eines Produkts")
    X = [["x_1"], ["x_2"], ["x_3"]]
    Y = [["y_1"], ["y_2"], ["y_3"]]
    e.append(text(30, 40, "Transponieren dreht die Reihenfolge um", "#444444", 19, anker="start"))
    e.append(_fx(40, 85, "(*A* *B*)^T = *B*^T *A*^T", "#000000", 24, anker="start"))
    e.append(text(30, 140, "Zeilenvektor · Spaltenvektor = Zahl; Transponieren ändert sie nicht", "#444444", 19, anker="start"))
    e.append(_fx(40, 185, "s = *x*^T*y*,    s^T = (*x*^T*y*)^T = *y*^T*x*", "#000000", 24, anker="start"))
    e.append(_fx(40, 250, "s^2 = s^T s = *y*^T*x* *x*^T*y* = *y*^T (*x* *x*^T) *y*", "#000000", 24, anker="start"))
    e.append(text(30, 310, "in der Mitte Spaltenvektor · Zeilenvektor = Matrix", "#444444", 19, anker="start"))
    e.append(_zeile(20, 400, ["*x* *x*^T =", (X, 40, 28, None), ([["x_1", "x_2", "x_3"]], 40, 32, None), "=",
                              ([[f"x_{r} x_{c}" for c in (1, 2, 3)] for r in (1, 2, 3)], 58, 28, None)], 22))
    e.append(_zeile(20, 570, ["s^2 =", ([["y_1", "y_2", "y_3"]], 40, 32, None),
                              ([[f"x_{r} x_{c}" for c in (1, 2, 3)] for r in (1, 2, 3)], 58, 28, None),
                              (Y, 40, 28, None)], 22))
    return abb.speichern(ZIEL / "matrizen.svg")


if __name__ == "__main__":
    for fn in (welle_ritz, matrizen, system, element, ergebnis, zusammenbau, zusammenfassung):
        print(fn())

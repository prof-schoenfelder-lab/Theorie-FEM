"""Grafiken zu Vorlesung 3: Normalkraftstab, von Ritz zur FEM.

Beispiel aus den Tafelbildern (1-Ritz2FEM, 1-FEM-Inzidenzmatrix): konischer Stab, links gelagert,
rechts Zugkraft F. E = 70000 MPa, L = 1000 mm, F = 5000 N, A0 = 100 mm², A1 = 20 mm²,
drei Elemente gleicher Länge mit der Querschnittsfläche in Elementmitte.
"""

import math
from pathlib import Path

from nlzeichnen import Diagramm, flaeche, notiz, wandgelenk
from tmzeichnen import FARBE, Abbildung, kraft, kreis, linie, loslager, mass, nummer, pfeil, polylinie, text

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


def _knoten_pfeil(e, x, y, label, laenge=34, dy=-22, farbe=GR, rechts_label=True):
    e.append(pfeil(x, y + dy, x + laenge, y + dy, farbe, 1.4, (9, 6)))
    if rechts_label:
        e.append(text(x + laenge + 5, y + dy, label, farbe, anker="start"))
    else:
        e.append(text(x + laenge / 2, y + dy - 15, label, farbe))


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

    e = abb.ebene("last", "Last")
    e.append(kraft(x1 + 4, y, 0, "F", laenge=55, ziehend=True, label_seite=1))

    e = abb.ebene("mass", "Bemaßung")
    e.append(mass(x0, y + s * A0, x1, y + s * A0, "L", abstand=-38))
    e.append(text(x0 + 16, y + s * A0 - 16, "A_0", GR, anker="start"))
    e.append(text(x1 - 4, y - s * A1 - 16, "A_1", GR, anker="end"))
    e.append(text(X(500), y + s * A(500) + 18, "E, A(x)", GR))
    e.append(pfeil(x0 + 4, y, x0 + 64, y, GR, 1.6, (10, 6)))
    e.append(text(x0 + 58, y + 17, "x", GR))

    # Elemente: abgestufte Querschnitte (Fläche in Elementmitte)
    e = abb.ebene("elemente", "Elemente")
    le = lp / N_EL
    for i in range(N_EL):
        xa, xb = x0 + i * le, x0 + (i + 1) * le
        h = s * A((i + 0.5) * L / N_EL)
        e.append(f'<rect x="{xa}" y="{y - h}" width="{le}" height="{2 * h}" fill="none" '
                 f'stroke="{FE}" stroke-width="1.4" stroke-dasharray="6 4"/>')
        e.append(nummer((xa + xb) / 2, y - s * A0 - 48, i + 1, r=11))
    for i in range(N_EL + 1):
        e.append(kreis(x0 + i * le, y, 4.2))

    e = abb.ebene("sysdof", "Systemfreiheitsgrade")
    for i in range(N_EL + 1):
        _knoten_pfeil(e, x0 + i * le, y, f"p_{i + 1}", dy=-s * A0 - 14)

    # Einzelne Elemente (auseinandergezogen) mit Elementfreiheitsgraden
    e = abb.ebene("einzeln", "Einzelne Elemente")
    ye, luecke = 395, 55
    for i in range(N_EL):
        xa = x0 - 40 + i * (le + luecke)
        xb = xa + le
        e.append(_element_kasten(xa, xb, ye, 20))
        e.append(kreis(xa, ye, 4.2))
        e.append(kreis(xb, ye, 4.2))
        e.append(nummer((xa + xb) / 2, ye - 45, i + 1, r=11))
        n = i + 1
        e.append(pfeil(xa + 6, ye - 13, xa + 40, ye - 13, GR, 1.25, (8, 5)))
        e.append(text(xa + 46, ye - 15, f"p_2^{n}", GR, anker="start"))
        e.append(pfeil(xb, ye - 34, xb + 34, ye - 34, GR, 1.4, (9, 6)))
        e.append(text(xb + 10, ye - 54, f"p_1^{n}", GR, anker="start"))
        e.append(pfeil(xa + 4, ye, xa + 44, ye, GR, 1.4, (9, 5)))
        e.append(text(xa + 40, ye + 15, f"x^{n}", GR))
        e.append(mass(xa, ye + 20, xb, ye + 20, f"L^{n}", abstand=-30))

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
    e.append(pfeil(xa + 4, y, xa + 50, y, GR, 1.4, (9, 5)))
    e.append(text(xa + 46, y + 15, "x^e", GR))

    e = abb.ebene("dof", "Elementfreiheitsgrade")
    e.append(pfeil(xa + 6, y - 14, xa + 44, y - 14, GR, 1.4, (9, 6)))
    e.append(text(xa + 50, y - 17, "p_2^e", GR, anker="start"))
    e.append(pfeil(xb + 6, y, xb + 50, y, GR, 1.4, (9, 6)))
    e.append(text(xb + 26, y - 20, "p_1^e", GR))

    e = abb.ebene("kraefte", "Knotenkräfte")
    e.append(kraft(xa - 6, y, 0, "q_2^e", laenge=60, label_seite=-1))
    e.append(kraft(xb + 62, y, 0, "q_1^e", laenge=50, ziehend=True, label_seite=-1, label_pos=1.2))

    # linkes Diagramm: Verschiebungsansatz
    D = Diagramm(90, 470, 260, 210, 1.0, 1.0)
    e = abb.ebene("ansatz_achsen", "Achsen Ansatz")
    e.append(D.achsen("x^e", "u^e", [(0, "0"), (1, "L^e")], [], groesse=19))
    e = abb.ebene("ansatz", "Linearer Ansatz")
    e.append(D.kurve(punkte=[(0, 0.32), (1, 0.82)], farbe=FE))
    e.append(D.linie(0, 0.82, 1, 0.82, GRAU, 0.9, "4 3"))
    e.append(D.linie(1, 0, 1, 1.0, GR, 0.9, "4 3"))
    e.append(D.text(0, 0.32, "u^e(0) = p_2^e", FE, dx=-8, anker="end", groesse=16))
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
    e.append(D2.kurve(punkte=[(0, 1), (1, 0)], farbe=EX))
    e.append(D2.text(0.8, 0.8, "x^e / L^e", FE, dx=12, dy=8, anker="start", groesse=17))
    e.append(D2.text(0.2, 0.8, "1 − x^e / L^e", EX, dx=6, dy=-6, anker="start", groesse=17))
    e.append(D2.linie(1, 0, 1, 1, GRAU, 0.9, "4 3"))
    e.append(D2.linie(0, 1, 1, 1, GRAU, 0.9, "4 3"))
    return abb.speichern(ZIEL / "element.svg")


def ergebnis():
    abb = Abbildung(860, 400, "Konischer Stab: FEM-Lösung und exakte Lösung")
    p, sig = fem(N_EL)
    le = L / N_EL

    Du = Diagramm(70, 330, 300, 250, 1000, 1.6)
    e = abb.ebene("achsen", "Achsen")
    e.append(Du.achsen("x", "u [in mm]", [(0, "0"), (500, "500"), (1000, "1000")],
                       [(0.4, "0,4"), (0.8, "0,8"), (1.2, "1,2"), (1.6, "1,6")], raster=True))
    Ds = Diagramm(500, 330, 300, 250, 1000, 260)
    e.append(Ds.achsen("x", "σ [in MPa]", [(0, "0"), (500, "500"), (1000, "1000")],
                       [(50, "50"), (100, "100"), (150, "150"), (200, "200"), (250, "250")], raster=True))
    e.append(notiz(70 + 300, 362, ["x in mm"], "#444444", 13, anker="end"))
    e.append(notiz(500 + 300, 362, ["x in mm"], "#444444", 13, anker="end"))

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


if __name__ == "__main__":
    for fn in (system, element, ergebnis):
        print(fn())

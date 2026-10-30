"""Grafiken zu Vorlesung 2: Rayleigh-Ritzsches Verfahren.

- Der Stab ist eine Feder (EA = konst., Einzelkraft): u(x) linear, c = EA/L
- Stabsystem aus 3-FEM-Stab/2a-Übung-2DOF über das Energieprinzip (Alu – Stahl – Alu, beidseitig fest,
  q = (−5F, 2F), F = 10 kN); Kernel: p1 = −0,1452 mm, p2 = −0,1325 mm, σ = −116,0 / −75,8 / 92,4 MPa
- Konischer Stab mit Ritz, Polynome Grad 1–3 (Koeffizienten hier berechnet, mit dem Kernel abgeglichen:
  u(L) = 1,1905 / 1,3975 / 1,4310 mm, exakt 1,4370 mm)
- Hängender Stab unter Eigengewicht: linearer Ansatz trifft u(L), N aber konstant q0 L/2
"""

import math
from pathlib import Path

from nlzeichnen import Diagramm, feder, notiz, wandgelenk
from tmzeichnen import (FARBE, Abbildung, einspannung, festlager, kraft, kreis, linie, loslager, mass, nummer,
                        pfeil, polylinie, text)

ZIEL = Path(__file__).resolve().parent.parent / "grafiken" / "ritz"
EX, ROT, GR = FARBE["linear"], FARBE["nichtlinear"], FARBE["mass"]
BLAU = EX                                        # wie die Kraft-Weg-Linie in V1
GRAU = "#7a7a7a"
RITZ = ["#f4a582", "#d6604d", "#b2182b"]          # Ansatzgrad 1, 2, 3 (heller → dunkler)


def _stab(x0, x1, y, h):
    """Prismatischer Stab als Rechteck mit Mittellinie."""
    return (f'<rect x="{x0}" y="{y - h}" width="{x1 - x0}" height="{2 * h}" fill="{FARBE["bauteil"]}" '
            f'stroke="#000" stroke-width="1.25"/>' + linie(x0, y, x1, y, GRAU, 0.8, "8 3 2 3"))


# ---------------------------------------------------------------- Der Stab ist eine Feder
def _halb(X, Y, links, rechts, farbe, g=19):
    """Formel „links ½ rechts“ mit ½ als echtem Bruch; (X, Y) = Mitte des Bruchstrichs (wie in V1)."""
    z, d = 0.79 * g, 0.58 * g
    return "".join([
        text(X - 9, Y, links, farbe, g, anker="end") if links else "",
        text(X, Y - d, "1", farbe, z, italic=False),
        linie(X - 0.32 * g, Y, X + 0.32 * g, Y, farbe, 1.1),
        text(X, Y + d, "2", farbe, z, italic=False),
        text(X + 0.53 * g, Y, rechts, farbe, g, anker="start"),
    ])


def stab_feder():
    abb = Abbildung(700, 500, "Der Stab ist eine Feder")
    x0, x1, y = 100, 480, 90

    e = abb.ebene("stab", "Stab")
    e.append(einspannung(x0, y, 64))
    e.append(_stab(x0, x1, y, 18))
    e.append(text((x0 + x1) / 2, y - 34, "EA = konst.", "#000000"))
    e.append(mass(x0, y + 20, x1, y + 20, "L", abstand=-24))

    e = abb.ebene("last", "Last")
    e.append(kraft(x1, y, 0, "F", laenge=60, ziehend=True, label_seite=1))

    # Kraft-Weg-Linie: Arbeit = Fläche des Dreiecks (wie bei der Feder in V1)
    K = Diagramm(505, 330, 130, 120, 1.25, 1.25)
    for name, titel, weg, kr, lab in (("kraftweg_f", "Kraft-Weg ganzer Stab", "u_L", "F", "F u_L"),
                                      ("kraftweg_n", "Kraft-Weg Stabstück", "du", "N", "N du")):
        e = abb.ebene(name, titel)
        e.append(K.flaeche([(0, 0), (1, 1), (1, 0)], "#dde7f5", 1.0))
        e.append(K.achsen("Weg", "Kraft", [(1, weg)], [(1, kr)], groesse=16))
        e.append(K.kurve(lambda v: v, 0, 1.12, farbe=BLAU))
        e.append(K.linie(1, 0, 1, 1, GRAU, 0.8, "4 3"))
        e.append(K.linie(0, 1, 1, 1, GRAU, 0.8, "4 3"))
        X, Y = K.px(0.66, 0.3)
        e.append(_halb(X - 14, Y, "", lab, BLAU, 15))

    # Herausgeschnittenes Stabstück dx: Normalkraft N an beiden Enden, Verlängerung du = ε dx
    xa, xb, ye, he = 200, 340, 245, 20
    e = abb.ebene("element", "Stabstück")
    xs = 395                                     # Lage des Stabstücks im Stab
    e.append(f'<rect x="{xs}" y="{y - 18}" width="22" height="36" fill="#9db8e0" stroke="#000" stroke-width="1"/>')
    e.append(text(xs + 11, y - 30, "dx", GR, 16))
    e.append(linie(xs, y + 18, xa, ye - he, GRAU, 0.8, "4 3"))
    e.append(linie(xs + 22, y + 18, xb, ye - he, GRAU, 0.8, "4 3"))
    e.append(f'<rect x="{xa}" y="{ye - he}" width="{xb - xa}" height="{2 * he}" fill="#9db8e0" stroke="#000" stroke-width="1.25"/>')
    e.append(polylinie([(xb, ye - he), (xb + 26, ye - he), (xb + 26, ye + he), (xb, ye + he)], GR, 1.1, strich="5 3"))
    e.append(kraft(xa, ye, 180, "N", laenge=56, ziehend=True, label_seite=-1))
    e.append(kraft(xb + 26, ye, 0, "N", laenge=56, ziehend=True, label_seite=1))
    e.append(mass(xa, ye + he, xb, ye + he, "dx", abstand=-22))
    e.append(mass(xb, ye + he, xb + 26, ye + he, "du", abstand=-22))
    e.append(notiz((xa + xb) / 2 + 13, ye + he + 62, ["N = σ A,   du = ε dx"], "#444444", 16, anker="middle"))

    D = Diagramm(x0, 300, x1 - x0, 120, 1.0, 1.0)
    e = abb.ebene("verlauf", "Verschiebungsverlauf")
    e.append(D.achsen("x", "u", [(1, "L")], [(1, "u_L")]))
    e.append(D.kurve(lambda s: s, 0, 1, farbe=GR))
    e.append(D.text(0.45, 0.62, "u(x) = u_L x/L", GR, dx=-8, anker="end"))
    e.append(D.text(0.55, 0.3, "u' = u_L/L = konst.", GR, dx=8, anker="start", groesse=17))

    e = abb.ebene("feder", "Ersatzfeder")
    yf = 430
    e.append(einspannung(x0, yf, 44))
    e.append(feder(x0, yf, x1, yf, 7, 10, label="c = EA/L", label_abstand=26))
    e.append(kreis(x1, yf, 4.2))
    e.append(kraft(x1, yf, 0, "F", laenge=60, ziehend=True, label_seite=1))
    return abb.speichern(ZIEL / "stab-feder.svg")


# ---------------------------------------------------------------- Stabsystem (2a-Übung-2DOF)
P1, P2 = -0.14516, -0.13252                      # mm, aus dem Kernel
SIG = (-115.96, -75.82, 92.38)                   # MPa


def stabsystem():
    abb = Abbildung(780, 600, "Stabsystem über das Energieprinzip")
    s = 2.4                                      # px je mm
    x0, y = 110, 120
    xa = [x0, x0 + 80 * s, x0 + 115 * s, x0 + 225 * s]
    h = [12 / 2 * s, 22 / 2 * s, 12 / 2 * s]

    e = abb.ebene("system", "System")
    e.append(einspannung(xa[0], y, 80))
    e.append(einspannung(xa[3], y, 80, seite="rechts"))
    for i in range(3):
        e.append(_stab(xa[i], xa[i + 1], y, h[i]))
    for i, name in enumerate(("Aluminium", "Stahl", "Aluminium")):
        xm = (xa[i] + xa[i + 1]) / 2
        e.append(notiz(xm, y + h[1] + 16, [f"{i + 1}: {name}"], "#444444", 14, anker="middle"))
    for i, l in enumerate((80, 35, 110)):
        e.append(mass(xa[i], y + 66, xa[i + 1], y + 66, f"[{l}]", abstand=-20))
    e.append(notiz(xa[3], y + 112, ["Maße in mm, Querschnitte quadratisch 12 × 12 bzw. 22 × 22"], "#666666", 13, anker="end"))

    # Kräfte greifen von außen am Stahlstück an, Wirkungslinie = Mittellinie
    e = abb.ebene("last", "Lasten")
    e.append(kraft(xa[1], y, 0, "2F", laenge=60, label_seite=-1, label_abstand=24))
    e.append(kraft(xa[2], y, 180, "5F", laenge=60, label_seite=1, label_abstand=24))

    # Mit den Freiheitsgraden: 5F längs der Wirkungslinie verschoben, damit p1 frei bleibt
    e = abb.ebene("last2", "Lasten verschoben")
    e.append(kraft(xa[1], y, 0, "2F", laenge=60, label_seite=-1, label_abstand=24))
    e.append(kraft(xa[2] + 76, y, 180, "5F", laenge=60, label_seite=1, label_abstand=24))

    e = abb.ebene("dof", "Freiheitsgrade")
    for x, n, hh in ((xa[1], 2, h[1]), (xa[2], 1, h[2])):
        e.append(kreis(x, y, 4.2))
        e.append(pfeil(x, y, x + 40, y, GR, 1.6, (9, 6)))
        e.append(text(x + 20, y - hh - 16, f"p_{n}", GR, 17))

    yf = 300
    e = abb.ebene("federn", "Ersatzfedern")
    e.append(einspannung(xa[0], yf, 44))
    e.append(einspannung(xa[3], yf, 44, seite="rechts"))
    for i, c in enumerate(("c_1", "c_2", "c_3")):
        e.append(feder(xa[i], yf, xa[i + 1], yf, 5 if i != 1 else 3, 9, label=c, label_abstand=22))
    for x, n in ((xa[1], 2), (xa[2], 1)):
        e.append(kreis(x, yf, 4.2))
        e.append(pfeil(x, yf + 18, x + 30, yf + 18, GR, 1.4, (8, 5)))
        e.append(text(x + 34, yf + 18, f"p_{n}", GR, 16, anker="start"))
    e.append(text((xa[0] + xa[3]) / 2, yf + 52, "c_e = E_e A_e / L_e", "#000000", 18))

    D = Diagramm(xa[0], 545, xa[3] - xa[0], 120, 225, 0.0, ymin=-0.16)
    e = abb.ebene("ergebnis", "Verschiebungsverlauf")
    e.append(D.achsen("x", "u in mm", [(80, ""), (115, ""), (225, "")], [(-0.1, "−0,1")], raster=True))
    e.append(D.kurve(punkte=[(0, 0), (80, P2), (115, P1), (225, 0)], farbe=ROT))
    for x, p in ((80, P2), (115, P1)):
        e.append(D.punkt(x, p, ROT, 4))
    e.append(D.text(80, P2, "p_2 = −0,133", ROT, dx=-8, dy=4, groesse=15, anker="end"))
    e.append(D.text(115, P1, "p_1 = −0,145", ROT, dx=10, dy=6, groesse=15, anker="start"))

    # Dehnungen und Spannungen: je Stab konstant, im Bereich der Ersatzfedern (dort ausgeblendet)
    grenzen = [(0, 80), (80, 115), (115, 225)]
    eps = (SIG[0] / 70000 * 1000, SIG[1] / 210000 * 1000, SIG[2] / 70000 * 1000)    # in ‰
    for name, titel, werte, ymax, ylabel, fmt, farbe, fuell in (
            ("dehnung", "Dehnungen", eps, 2.0, "ε in ‰", "{:.2f}", GR, "#d8eadb"),
            ("spannung", "Spannungen", SIG, 140, "σ in MPa", "{:.1f}", ROT, "#f6d5d5")):
        Ds = Diagramm(xa[0], 380, xa[3] - xa[0], 120, 225, ymax, ymin=-ymax)
        e = abb.ebene(name, titel)
        e.append(Ds.achsen("x", ylabel, [(80, ""), (115, ""), (225, "")], [], raster=True))
        for (a, b), w in zip(grenzen, werte):
            e.append(Ds.flaeche([(a, 0), (a, w), (b, w), (b, 0)], fuell, 1.0))
        e.append(Ds.kurve(punkte=[(0, 0), (0, werte[0]), (80, werte[0]), (80, werte[1]), (115, werte[1]),
                                  (115, werte[2]), (225, werte[2]), (225, 0)], farbe=farbe))
        for (a, b), w in zip(grenzen, werte):
            t = fmt.format(w).replace(".", ",").replace("-", "−")
            e.append(Ds.notiz((a + b) / 2, w, [t], farbe, dy=-14 if w > 0 else 14, groesse=15, anker="middle"))
    return abb.speichern(ZIEL / "stabsystem.svg")


# ---------------------------------------------------------------- Konischer Stab mit Ritz
E, L, F, A0, A1 = 70000.0, 1000.0, 5000.0, 100.0, 20.0


def A(x):
    return A0 - (A0 - A1) / L * x


def u_exakt(x):
    return F / E * L / (A0 - A1) * math.log(A0 / A(x))


def _loese(K, q):
    """Kleines lineares Gleichungssystem (Gauß ohne Pivotsuche, K symmetrisch positiv definit)."""
    n = len(q)
    M = [row[:] + [q[i]] for i, row in enumerate(K)]
    for i in range(n):
        for j in range(i + 1, n):
            f = M[j][i] / M[i][i]
            M[j] = [a - f * b for a, b in zip(M[j], M[i])]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def ritz(n):
    """Ritz mit u = Σ b_i ξ^i (ξ = x/L, i = 1…n). K_ij = E/L ∫ A(ξ) i j ξ^(i+j−2) dξ, q_i = F."""
    def I(m):                                    # ∫0^1 A(ξ) ξ^m dξ
        return A0 / (m + 1) - (A0 - A1) / (m + 2)
    K = [[E / L * i * j * I(i + j - 2) for j in range(1, n + 1)] for i in range(1, n + 1)]
    b = _loese(K, [F] * n)
    u = lambda x: sum(bi * (x / L) ** (i + 1) for i, bi in enumerate(b))
    sig = lambda x: E * sum(bi * (i + 1) * (x / L) ** i / L for i, bi in enumerate(b))
    return u, sig


def konisch_ritz():
    abb = Abbildung(780, 660, "Konischer Stab: Ritzsches Verfahren")
    x0, lp, y = 120, 540, 95
    x1 = x0 + lp
    hs = 0.42

    e = abb.ebene("system", "System")
    e.append(polylinie([(x0, y - hs * A0), (x1, y - hs * A1), (x1, y + hs * A1), (x0, y + hs * A0)],
                       "#000000", 1.25, FARBE["bauteil"], schliessen=True))
    e.append(linie(x0, y, x1, y, GRAU, 0.8, "8 3 2 3"))
    e.append(wandgelenk(x0, y, 60))
    e.append(loslager(x1, y, 12))
    e.append(kraft(x1 + 4, y, 0, "F", laenge=55, ziehend=True, label_seite=1))
    e.append(text(x0 + 20, y - hs * A0 - 16, "A_0", GR, anker="start"))
    e.append(text(x1 - 6, y - hs * A1 - 16, "A_1", GR, anker="end"))
    e.append(text((x0 + x1) / 2, y - (A0 + A1) / 2 * hs - 18, "E, A(x)", GR))

    Du = Diagramm(x0, 380, lp, 190, L, 1.6)
    Ds = Diagramm(x0, 630, lp, 190, L, 260)
    e = abb.ebene("achsen", "Achsen")
    e.append(Du.achsen("x", "u in mm", [(500, ""), (1000, "L")], [(0.5, "0,5"), (1.0, "1"), (1.5, "1,5")], raster=True))
    e.append(Ds.achsen("x", "σ in MPa", [(500, ""), (1000, "L")], [(100, "100"), (200, "200")], raster=True))

    e = abb.ebene("exakt", "Exakte Lösung")
    e.append(Du.kurve(u_exakt, 0, L, farbe=EX))
    e.append(Ds.kurve(lambda x: F / A(x), 0, L, farbe=EX))
    e.append(Du.notiz(L, u_exakt(L), ["exakt"], EX, dx=8, dy=-8, anker="start"))
    e.append(Ds.notiz(L, 250, ["exakt"], EX, dx=8, anker="start"))

    for n in (1, 2, 3):
        u, sig = ritz(n)
        f = RITZ[n - 1]
        e = abb.ebene(f"grad{n}", f"Ritz Grad {n}")
        e.append(Du.kurve(u, 0, L, farbe=f, breite=2.2))
        e.append(Ds.kurve(sig, 0, L, farbe=f, breite=2.2))
        if n == 1:                               # Grad 2 und 3 liegen am Ende zu dicht an der exakten Lösung
            e.append(Du.notiz(L, u(L), [f"Grad {n}"], f, dx=8, anker="start", groesse=13))
        e.append(Ds.notiz(L, sig(L), [f"Grad {n}"], f, dx=8, anker="start", groesse=13))
    return abb.speichern(ZIEL / "konisch-ritz.svg")


# ---------------------------------------------------------------- Hängender Stab unter Eigengewicht
def haengestab():
    abb = Abbildung(760, 470, "Hängender Stab: linearer und quadratischer Ansatz")
    xs, y0, y1 = 95, 70, 390

    e = abb.ebene("system", "System")
    e.append('<rect x="{}" y="{}" width="14" height="{}" fill="{}" stroke="#000" stroke-width="1.25"/>'
             .format(xs - 7, y0, y1 - y0, FARBE["bauteil"]))
    e.append(festlager(xs, y0, drehung=180))
    for i in range(7):
        yy = y0 + 18 + i * (y1 - y0 - 36) / 6
        e.append(pfeil(xs + 20, yy - 14, xs + 20, yy + 8, ROT, 1.1, (7, 4.5)))
    e.append(text(xs + 32, (y0 + y1) / 2, "q_0", ROT, anker="start"))
    e.append(pfeil(xs - 30, y0 + 4, xs - 30, y0 + 50, GR, 1.25, (8, 5)))
    e.append(text(xs - 36, y0 + 44, "x", GR, anker="end"))
    e.append(text(xs, y1 + 24, "EA = konst.", "#000000", 16))

    Du = Diagramm(250, 200, 440, 140, 1.0, 0.55)
    Dn = Diagramm(250, 430, 440, 160, 1.0, 1.05)
    e = abb.ebene("achsen", "Achsen")
    e.append(Du.achsen("x", "u · EA/(q_0 L^2)", [(0.5, "L/2"), (1, "L")], [(0.25, "0,25"), (0.5, "0,5")], raster=True, groesse=16))
    e.append(Dn.achsen("x", "N/(q_0 L)", [(0.5, "L/2"), (1, "L")], [(0.5, "0,5"), (1, "1")], raster=True, groesse=16))

    e = abb.ebene("exakt", "Exakt (= quadratischer Ansatz)")
    e.append(Du.kurve(lambda x: x * (2 - x) / 2, 0, 1, farbe=EX))
    e.append(Dn.kurve(lambda x: 1 - x, 0, 1, farbe=EX))
    e.append(Du.notiz(0.3, 0.5, ["exakt = quadratischer Ansatz"], EX, groesse=13))
    e.append(Dn.notiz(0.08, 0.92, ["exakt = quadratisch"], EX, dx=14, groesse=13, anker="start"))

    e = abb.ebene("linear", "Linearer Ansatz")
    e.append(Du.kurve(lambda x: x / 2, 0, 1, farbe=ROT, breite=2.2))
    e.append(Dn.kurve(lambda x: 0.5, 0, 1, farbe=ROT, breite=2.2))
    e.append(Du.notiz(0.55, 0.27, ["linear"], ROT, dx=10, dy=12, groesse=13, anker="start"))
    e.append(Dn.notiz(0.75, 0.5, ["linear: q_0 L/2"], ROT, dy=-14, groesse=13))
    e.append(Du.punkt(1, 0.5, "#000000", 4))
    e.append(Du.notiz(1, 0.5, ["u(L) gleich"], "#000000", dx=-8, dy=-16, groesse=13, anker="end"))
    e.append(Dn.punkt(0, 1, ROT, 4))
    e.append(Dn.punkt(0, 0.5, ROT, 4))
    e.append(Dn.notiz(0, 0.75, ["nur halb so groß"], ROT, dx=12, groesse=13, anker="start"))
    return abb.speichern(ZIEL / "haengestab.svg")


# ---------------------------------------------------------------- Rayleigh und Ritz
def portraets():
    """Gemeinfreie Fotos (Wikimedia Commons), eingebettet, damit die Grafik eigenständig bleibt."""
    import base64
    abb = Abbildung(810, 500, "Rayleigh und Ritz")
    for name, datei, x, b, zeilen in (
            ("rayleigh", "rayleigh.jpg", 40, 297, ["Lord Rayleigh", "1842–1919"]),
            ("ritz", "ritz.jpg", 383, 387, ["Walther Ritz", "1878–1909"])):
        daten = base64.b64encode((Path(__file__).parent / "fotos" / datei).read_bytes()).decode()
        e = abb.ebene(name, zeilen[0])
        e.append(f'<image x="{x}" y="20" width="{b}" height="400" preserveAspectRatio="xMidYMid meet" '
                 f'href="data:image/jpeg;base64,{daten}"/>')
        e.append(notiz(x + b / 2, 444, zeilen, "#000000", 19, anker="middle"))
    return abb.speichern(ZIEL / "portraets.svg")


# ---------------------------------------------------------------- Übung: abgesetzte Welle (3-FEM-Stab/2b)
def welle(mit_dof):
    """Abgesetzte Stahlwelle Ø11/Ø25/Ø11, L = 240/160/240 mm, links eingespannt, rechts F drückend."""
    titel = "Abgesetzte Welle: Freiheitsgrade" if mit_dof else "Abgesetzte Welle"
    abb = Abbildung(860, 300, titel)
    s, sd = 1.0, 3.6                             # px je mm in Längs- und Querrichtung
    x0, y = 70, 120
    xa = [x0, x0 + 240 * s, x0 + 400 * s, x0 + 640 * s]
    h = [11 / 2 * sd, 25 / 2 * sd, 11 / 2 * sd]
    e = abb.ebene("system", "System")
    e.append(einspannung(xa[0], y, 80))
    for i in range(3):
        e.append(_stab(xa[i], xa[i + 1], y, h[i]))
    for i, l in enumerate((240, 160, 240)):
        e.append(mass(xa[i], y + 66, xa[i + 1], y + 66, f"[{l}]", abstand=-20))
    if not mit_dof:
        e.append(kraft(xa[3], y, 180, "F", laenge=60, label_seite=1, label_abstand=24))
        for i, d in enumerate((11, 25, 11)):
            e.append(notiz((xa[i] + xa[i + 1]) / 2, y - h[1] - 16, [f"Ø {d}"], "#444444", 16, anker="middle"))
        e.append(notiz(xa[3], y + 112, ["Maße in mm, Stahl"], "#666666", 14, anker="end"))
    else:
        e.append(kraft(xa[3] + 80, y, 180, "F", laenge=60, label_seite=1, label_abstand=24))
        for i in range(3):
            e.append(nummer((xa[i] + xa[i + 1]) / 2, y + h[1] + 22, i + 1))
        for x, n, hh in ((xa[1], 2, h[1]), (xa[2], 3, h[1]), (xa[3], 1, h[2])):
            e.append(kreis(x, y, 4.2))
            e.append(pfeil(x, y, x + 40, y, GR, 1.6, (9, 6)))
            e.append(text(x + 20, y - hh - 16, f"p_{n}", GR, 18))
    return abb.speichern(ZIEL / ("welle-dof.svg" if mit_dof else "welle-system.svg"))


if __name__ == "__main__":
    for n in (1, 2, 3):
        u, sig = ritz(n)
        print(f"Grad {n}: u(L) = {u(L):.4f} mm, σ(L) = {sig(L):.1f} MPa")
    for fn in (stab_feder, stabsystem, konisch_ritz, haengestab, portraets):
        print(fn())
    print(welle(False), welle(True))

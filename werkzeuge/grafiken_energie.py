"""Grafiken zu Vorlesung 1: Energieprinzipien, Minimum der potentiellen Energie.

- Die Kugel rollt bergab (Tafelbild 1-Energieprinzipien-Feder): Lage, Höhe h, Minimum, bergauf unmöglich
- Eine Feder: System (Wand, Feder c, Kraft F, Verschiebung u) und Diagramm Π_i, Π_a, Π_ges über u
  (dimensionslos: u in F/c, Π in F²/c; Minimum bei u = F/c mit Π_ges = −F²/(2c), im Kernel geprüft)
Das Federsystem aus Vorlesung 0 wird direkt aus grafiken/einfuehrung/federsystem.svg verwendet.
"""

import math
from pathlib import Path

from nlzeichnen import Diagramm, feder, notiz
from tmzeichnen import FARBE, KRAEFTIG, Abbildung, bruch, einspannung, kraft, kreis, linie, mass, pfeil, polylinie, text

ZIEL = Path(__file__).resolve().parent.parent / "grafiken" / "energie"
BLAU, ROT, GR = FARBE["linear"], FARBE["nichtlinear"], FARBE["mass"]
GRAU = "#7a7a7a"


# ---------------------------------------------------------------- Die Kugel rollt bergab
_PROFIL = [(30, 150), (120, 112), (360, 300), (610, 160)]     # Hügel links, Tal, Anstieg rechts (px)


def _boden(X):
    """Höhe der Geländelinie an der Stelle X (glatter Übergang zwischen den Stützpunkten)."""
    for (x1, y1), (x2, y2) in zip(_PROFIL, _PROFIL[1:]):
        if x1 <= X <= x2:
            t = (X - x1) / (x2 - x1)
            return y1 + (y2 - y1) * (1 - math.cos(math.pi * t)) / 2
    return _PROFIL[-1][1]


def _kugel(X, r=17, farbe="#9a9a9a"):
    Y = _boden(X)
    h = 0.6
    # Tangente (1, y'), Normale nach oben (y', -1): SVG-y zeigt nach unten
    nx, ny = (_boden(X + h) - _boden(X - h)) / (2 * h), -1.0
    n = math.hypot(nx, ny)
    cx, cy = X + nx / n * r, Y + ny / n * r
    return cx, cy, f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{farbe}" stroke="#000" stroke-width="1.25"/>'


def kugel():
    abb = Abbildung(640, 380, "Die Kugel rollt bergab")
    xs = [30 + i * 2 for i in range(291)]
    gelaende = [(x, _boden(x)) for x in xs]
    yt = _PROFIL[2][1]

    e = abb.ebene("gelaende", "Gelände")
    e.append(polylinie(gelaende + [(610, 340), (30, 340)], None, fuellung="#ececec", schliessen=True))
    e.append(polylinie(gelaende, "#000000", 1.6))

    e = abb.ebene("kugel_oben", "Kugel oben")
    xs_ = _PROFIL[1][0]                                   # Bergspitze: dort liegt die Kugel in Ruhe
    ys_ = _boden(xs_)
    cx, cy, k = _kugel(xs_, farbe="#c9c9c9")
    e.append(k)
    e.append(linie(xs_, ys_, 470, ys_, GRAU, 0.8, "4 3"))   # h von Auflagepunkt zu Auflagepunkt
    e.append(linie(360, yt, 470, yt, GRAU, 0.8, "4 3"))
    e.append(mass(455, yt, 455, ys_, "h", abstand=0, hilfslinien=False))
    e.append(pfeil(cx - 76, cy - 34, cx - 76, cy + 16, FARBE["last"], KRAEFTIG["kraft"], KRAEFTIG["spitze"]))  # g wie eine Kraft
    e.append(text(cx - 66, cy - 22, "g", FARBE["last"], 22, anker="start"))
    e.append(text(cx, cy - 36, "Π = m g h", "#000000"))

    e = abb.ebene("rollen", "Kugel rollt ins Tal")
    pts = [(x, _boden(x) - 30) for x in range(148, 335, 4)]
    e.append(polylinie(pts, ROT, 1.4, strich="6 4"))
    e.append(pfeil(*pts[-2], *pts[-1], ROT, 1.4, (10, 7)))
    _cx, _cy, k = _kugel(360, farbe="#8a8a8a")
    e.append(k)
    e.append(notiz(360, yt + 26, ["Minimum der potentiellen Energie:", "Gleichgewichtslage"], "#444444", 15,
                   anker="middle"))

    # Waagerechte Tangenten: Bergspitze (Maximum, instabil) und Talsohle (Minimum, stabil)
    e = abb.ebene("tangenten", "Waagerechte Tangenten")
    xs_, ys_ = _PROFIL[1][0], _boden(_PROFIL[1][0])
    xt_, yt_ = _PROFIL[2][0], _boden(_PROFIL[2][0])
    for x, y in ((xs_, ys_), (xt_, yt_)):
        e.append(linie(x - 62, y, x + 62, y, BLAU, 2.0))
    e.append(text(xs_ + 66, ys_ - 26, "h′ = 0,  h″ < 0", BLAU, 17, anker="start"))
    e.append(notiz(xs_ + 66, ys_ - 4, ["Maximum: instabil"], BLAU, 15))
    e.append(text(xt_ - 70, yt_ - 30, "h′ = 0,  h″ > 0", BLAU, 17, anker="end"))
    e.append(notiz(xt_ - 70, yt_ - 8, ["Minimum: stabil"], BLAU, 15, anker="end"))

    e = abb.ebene("bergauf", "Bergauf unmöglich")
    cx2, cy2, k = _kugel(500, farbe="#e2e2e2")
    e.append(k)
    e.append(pfeil(cx2 + 6, cy2 - 26, cx2 + 52, cy2 - 64, GRAU, 1.4, (10, 7)))
    e.append(notiz(cx2 + 70, cy2 - 96, ["bergauf: Π würde wachsen"], ROT, 15, anker="end"))
    # der ganze Zustand (Kugel, Pfeil, Beschriftung) durchgestrichen
    x0, y0, x1, y1 = cx2 - 24, cy2 - 110, cx2 + 80, cy2 + 24
    e.append(linie(x0, y0, x1, y1, ROT, 3.0, kappe="round"))
    e.append(linie(x0, y1, x1, y0, ROT, 3.0, kappe="round"))
    return abb.speichern(ZIEL / "kugel.svg")


# ---------------------------------------------------------------- Eine Feder mit Energiediagramm
def _halb(X, Y, links, rechts, farbe, g=19):
    """Formel „links ½ rechts“ mit ½ als Bruch im displaystyle; (X, Y) = Mitte des Bruchstrichs."""
    return bruch(X, Y, "1", "2", farbe, g, links=links, rechts=rechts)


def feder_energie():
    abb = Abbildung(700, 700, "Die Feder: hängende Masse, innere, äußere und gesamte potentielle Energie")
    xf, yd, yr, ym, hm = 200, 24, 112, 152, 46       # Feder-x, Decke, Ende entspannt, Ende belastet, Höhe Masse

    e = abb.ebene("system", "System")
    e.append(linie(xf - 50, yd, xf + 50, yd, "#000000", 2.2))                 # Decke mit Schraffur
    for xx in range(int(xf - 46), int(xf + 50), 8):
        e.append(linie(xx, yd, xx + 8, yd - 8, "#000000", 0.8))
    e.append(feder(xf, yd, xf, ym, 7, 11, label="c", label_abstand=-26))
    e.append(kreis(xf, yd, 4.2))
    e.append(f'<rect x="{xf - 30}" y="{ym}" width="60" height="{hm}" fill="#d9d9d9" stroke="#000" stroke-width="1.25"/>')
    e.append(text(xf, ym + hm / 2, "m", "#000000", 19))

    e = abb.ebene("kraft", "Gewichtskraft")
    e.append(kraft(xf, ym + hm, -90, "F = m g", laenge=62, ziehend=True, label_seite=-1, kraeftig=True))

    e = abb.ebene("verschiebung", "Verschiebung")
    for yy in (yr, ym):
        e.append(linie(xf + 34, yy, xf + 96, yy, GRAU, 0.8, "4 3"))
    e.append(pfeil(xf + 80, yr, xf + 80, ym, GR, KRAEFTIG["dof"], KRAEFTIG["dof_spitze"]))
    e.append(text(xf + 88, (yr + ym) / 2, "u", GR, anker="start"))
    e.append(notiz(xf + 100, yr, ["entspannt"], "#666666", 13))

    # Kraft-Weg-Linie der Feder: Π_i ist die Fläche darunter (Arbeit beim Dehnen von 0 bis u)
    A = Diagramm(480, 230, 160, 140, 1.3, 1.3)
    e = abb.ebene("arbeit", "Kraft-Weg-Linie")
    e.append(A.flaeche([(0, 0), (1, 1), (1, 0)], "#dde7f5", 1.0))
    e.append(A.flaeche([(0.55, 0), (0.55, 0.55), (0.65, 0.65), (0.65, 0)], "#9db8e0", 1.0))
    e.append(A.achsen("s", "N", [(1, "u")], [(1, "c u")], groesse=17))
    e.append(A.kurve(lambda v: v, 0, 1.15, farbe=BLAU))
    e.append(A.linie(1, 0, 1, 1, GRAU, 0.8, "4 3"))
    e.append(A.text(0.72, 0.28, "Π_i", BLAU, groesse=17))
    e.append(A.text(0.6, 0.6, "N [d]s", BLAU, dx=-6, dy=-16, groesse=14, anker="end"))
    e.append(A.text(1.15, 1.15, "N = c s", BLAU, dx=4, dy=-4, groesse=15, anker="start"))

    # Wo ist die andere Hälfte? Die Last verliert F u (Rechteck), die Feder speichert nur das untere Dreieck
    e = abb.ebene("haelfte", "Andere Hälfte")
    e.append(A.flaeche([(0, 0), (1, 1), (1, 0)], "#dde7f5", 1.0))
    e.append(A.flaeche([(0, 0), (0, 1), (1, 1)], "#fbe3e3", 1.0))
    e.append(A.achsen("s", "N", [(1, "u")], [(1, "F")], groesse=17))
    e.append(A.linie(0, 1, 1, 1, ROT, 1.4))
    e.append(A.linie(1, 0, 1, 1, ROT, 1.4))
    e.append(A.kurve(lambda v: v, 0, 1.15, farbe=BLAU))
    X, Y = A.px(0.7, 0.27)
    e.append(_halb(X - 8, Y, "", "F u", BLAU, 15))
    X, Y = A.px(0.27, 0.74)
    e.append(_halb(X - 8, Y, "", "F u", ROT, 15))
    e.append(A.notiz(1.08, 0.55, ["Feder"], BLAU, anker="start", groesse=13))
    e.append(A.notiz(1.08, 0.95, ["Rest"], ROT, anker="start", groesse=13))

    # Diagramm: u in F/c, Π in F²/c
    D = Diagramm(120, 665, 470, 340, 2.4, 2.2, xmin=-0.3, ymin=-1.3)
    e = abb.ebene("achsen", "Achsen")
    e.append(D.achsen("u", "Π", [(1, ""), (2, "")], [(1, ""), (-1, "")], raster=True))
    for v, z in ((1, "F"), (2, "2F")):
        X, Y = D.px(v, 0)
        e.append(bruch(X + 16, Y + 24, z, "c", "#000000", 15))

    e = abb.ebene("pi_i", "Innere Energie")
    e.append(D.kurve(lambda u: u * u / 2, -0.3, 2.4, farbe=BLAU))
    X, Y = D.px(2.05, 2.05)
    e.append(_halb(X - 70, Y, "Π_i =", "c u^2", BLAU))

    e = abb.ebene("pi_a", "Äußere Energie")
    e.append(D.kurve(lambda u: -u, -0.3, 1.3, farbe=ROT))
    e.append(D.text(1.3, -1.3, "Π_a = −F u", ROT, dx=-16, dy=6, anker="end"))

    e = abb.ebene("pi_ges", "Gesamte Energie")
    e.append(D.kurve(lambda u: u * u / 2 - u, -0.3, 2.4, farbe="#000000", breite=2.6))
    e.append(D.text(2.4, 0.48, "Π_{ges} = Π_i + Π_a", "#000000", dx=-4, dy=-16, anker="end"))

    e = abb.ebene("minimum", "Minimum")
    e.append(D.hilfslinien(1, -0.5))
    e.append(D.punkt(1, -0.5, GR, 5))
    e.append(D.notiz(1, -0.5, ["Minimum"], GR, dx=14, dy=20))
    X, Y = D.px(1.5, -0.5)
    e.append(bruch(X, Y + 52, "[d]Π_{ges}", "[d]u", GR, 18, rechts="= 0", anker="start"))
    e.append(bruch(X + 74, Y + 52, "F", "c", GR, 18, links="⇒  u =", anker="start"))
    return abb.speichern(ZIEL / "feder.svg")


# ---------------------------------------------------------------- Höhenlinien von Π_ges(p1, p2), Federsystem aus V0
def hoehenlinien():
    """Π_ges = ½ pᵀKp − pᵀq mit K = k [[5, −4], [−4, 6]], q = (3F, −F); p in F/k, Π in F²/k.
    Minimum bei p = (1, 1/2), Π_min = −5/4 (im Kernel geprüft). Höhenlinien: Ellipsen um das Minimum,
    Halbachsen sqrt(2 ΔΠ / λ) entlang der Eigenvektoren von K."""
    K = ((5.0, -4.0), (-4.0, 6.0))
    pm, pi_min = (1.0, 0.5), -1.25
    sp, det = K[0][0] + K[1][1], K[0][0] * K[1][1] - K[0][1] ** 2
    lam = [sp / 2 + math.sqrt(sp * sp / 4 - det), sp / 2 - math.sqrt(sp * sp / 4 - det)]
    vek = []
    for l in lam:                                       # (K − λI) v = 0 → v = (K01, λ − K00)
        vx, vy = K[0][1], l - K[0][0]
        n = math.hypot(vx, vy)
        vek.append((vx / n, vy / n))

    abb = Abbildung(620, 560, "Höhenlinien der potentiellen Energie")
    D = Diagramm(90, 510, 450, 450, 2.5, 2.0, xmin=-0.5, ymin=-1.0)    # gleicher Maßstab in p1 und p2
    e = abb.ebene("achsen", "Achsen")
    e.append(D.achsen("p_1", "p_2", [(1, ""), (2, "")], [(1, ""), (-0.5, "")], raster=True))
    for v, z in ((1, "F"), (2, "2F")):
        X, Y = D.px(v, 0)
        e.append(bruch(X, Y + 26, z, "k", "#000000", 15))
    X, Y = D.px(0, 1)
    e.append(bruch(X - 20, Y, "F", "k", "#000000", 15))

    e = abb.ebene("konturen", "Höhenlinien")
    stufen = [-1.0, -0.5, 0.0, 1.0, 2.0, 3.0]
    for i, w in enumerate(stufen):
        d = w - pi_min
        a1, a2 = math.sqrt(2 * d / lam[0]), math.sqrt(2 * d / lam[1])
        farbe = ["#08306b", "#08519c", "#2171b5", "#4292c6", "#6baed6", "#9ecae1"][i]
        e.append(D.kurve(lambda t, a1=a1, a2=a2: (pm[0] + a1 * math.cos(t) * vek[0][0] + a2 * math.sin(t) * vek[1][0],
                                                   pm[1] + a1 * math.cos(t) * vek[0][1] + a2 * math.sin(t) * vek[1][1]),
                         0, 2 * math.pi, n=240, param=True, farbe=farbe, breite=1.6))
        if i < 4:                                         # Beschriftung an der Spitze der langen Achse, oben rechts
            r = 1 if vek[1][0] > 0 else -1
            x, y = pm[0] + r * a2 * vek[1][0], pm[1] + r * a2 * vek[1][1]
            wert = f"{w:g}".replace(".", ",").replace("-", "−")
            e.append(D.text(x, y, f"Π = {wert}", farbe, dx=8, dy=-4, groesse=15, anker="start"))
    e.append(D.notiz(-0.45, 1.88, ["Π_{ges} in F^2/k"], "#444444", groesse=14))

    e = abb.ebene("minimum", "Minimum")
    e.append(D.hilfslinien(pm[0], pm[1], GR))
    e.append(D.punkt(pm[0], pm[1], ROT, 5.5))
    X, Y = D.px(0, 0.5)
    e.append(bruch(X - 10, Y, "F", "2k", GR, 15, anker="end"))
    X, Y = D.px(pm[0], pm[1])
    e.append(bruch(X + 24, Y + 30, "5", "4", ROT, 17, links="Π_{min} = −", anker="start"))
    return abb.speichern(ZIEL / "hoehenlinien.svg")


# ---------------------------------------------------------------- Zusammenfassung: Gleichgewicht oder Energie?
def zusammenfassung():
    """Zwei Spalten: Weg aus Vorlesung 0 (Freischnitt, Gleichgewicht) und Weg aus Vorlesung 1 (Energie),
    beide führen auf dasselbe K p = q."""
    from grafiken_einfuehrung import _kasten, _platte, formel
    from tmzeichnen import freiheitsgrad
    abb = Abbildung(720, 640, "Gleichgewicht oder Energie?")
    xl, xr, b = 10, 370, 340                          # linke und rechte Spalte
    zeilen = (100, 250, 340, 430)                     # Ausgangspunkt, Werkstoff, Kinematik, Gleichungen

    def zeilentitel(x, y, t):
        return notiz(x + 12, y, [t], "#666666", 14)

    e = abb.ebene("gleichgewicht", "Weg über das Gleichgewicht")
    e.append(_kasten(xl, 10, b, 500, "Vorlesung 0: Gleichgewicht"))
    e.append(zeilentitel(xl, 50, "Freischnitt jedes Balkens"))
    xm, ym = xl + 160, 120
    e.append(_platte(xm, ym - 52, ym + 52))
    e.append(kraft(xm, ym + 20, 180, "N_1", laenge=60, ziehend=True, label_seite=-1, kraeftig=True))
    e.append(kraft(xm + 16, ym + 20, 0, "N_2", laenge=60, ziehend=True, label_seite=1, kraeftig=True))
    e.append(kraft(xm + 16, ym - 22, 0, "f_2", laenge=60, ziehend=True, label_seite=-1, kraeftig=True))
    e.append(zeilentitel(xl, zeilen[1] - 26, "Werkstoffgesetz"))
    e.append(formel(xl + b / 2, zeilen[1] + 6, "N = c u", groesse=21, anker="middle"))
    e.append(zeilentitel(xl, zeilen[2] - 26, "Kinematik"))
    e.append(formel(xl + b / 2, zeilen[2] + 6, "u_1 = p_2,  u_2 = p_1 − p_2", groesse=20, anker="middle"))
    e.append(zeilentitel(xl, zeilen[3] - 26, "Gleichungen: Gleichgewicht je Balken"))
    e.append(formel(xl + b / 2, zeilen[3] + 10, "−N_1 + N_2 + f_2 = 0", groesse=21, anker="middle"))

    e = abb.ebene("energie", "Weg über die Energie")
    e.append(_kasten(xr, 10, b, 500, "Vorlesung 1: Energie"))
    e.append(zeilentitel(xr, 50, "Energie jeder Feder, Arbeit jeder Kraft"))
    yf = 104
    e.append(einspannung(xr + 30, yf, 36))
    e.append(feder(xr + 30, yf, xr + 160, yf, 5, 9, label="c", label_abstand=-20))
    e.append(freiheitsgrad(xr + 160, yf, "p", laenge=46, label_seite=-1))
    e.append(kraft(xr + 250, yf, 0, "f", laenge=55, ziehend=True, label_seite=-1, kraeftig=True))
    e.append(bruch(xr + 40, yf + 62, "1", "2", BLAU, 20, links="Π_i =", rechts="c u^2", anker="start"))
    e.append(text(xr + 220, yf + 62, "Π_a = −f p", ROT, 20, anker="start"))
    e.append(zeilentitel(xr, zeilen[1] - 26, "Werkstoffgesetz"))
    e.append(notiz(xr + 50, zeilen[1] + 6, ["steckt in"], "#333333", 16))
    e.append(bruch(xr + 125, zeilen[1] + 6, "1", "2", "#000000", 20, links="Π_i =", rechts="c u^2", anker="start"))
    e.append(zeilentitel(xr, zeilen[2] - 26, "Kinematik"))
    e.append(formel(xr + b / 2, zeilen[2] + 6, "u_1 = p_2,  u_2 = p_1 − p_2", groesse=20, anker="middle"))
    e.append(zeilentitel(xr, zeilen[3] - 26, "Gleichungen: Minimum der Energie"))
    e.append(bruch(xr + 110, zeilen[3] + 10, "∂Π_{ges}", "∂p_i", "#000000", 21, rechts="= 0", anker="start"))

    e = abb.ebene("ergebnis", "Dasselbe Ergebnis")
    for x in (xl + b / 2, xr + b / 2):
        e.append(pfeil(x, 514, 360 + (x - 360) * 0.2, 566, "#555555", 1.4, (10, 7)))
    e.append(formel(360, 596, "**K** **p** = **q**", groesse=30, anker="middle"))
    return abb.speichern(ZIEL / "zusammenfassung.svg")


if __name__ == "__main__":
    for fn in (kugel, feder_energie, hoehenlinien, zusammenfassung):
        print(fn())

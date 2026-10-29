"""Grafiken zu Vorlesung 1: Energieprinzipien, Minimum der potentiellen Energie.

- Die Kugel rollt bergab (Tafelbild 1-Energieprinzipien-Feder): Lage, Höhe h, Minimum, bergauf unmöglich
- Eine Feder: System (Wand, Feder c, Kraft F, Verschiebung u) und Diagramm Π_i, Π_a, Π_ges über u
  (dimensionslos: u in F/c, Π in F²/c; Minimum bei u = F/c mit Π_ges = −F²/(2c), im Kernel geprüft)
Das Federsystem aus Vorlesung 0 wird direkt aus grafiken/einfuehrung/federsystem.svg verwendet.
"""

import math
from pathlib import Path

from nlzeichnen import Diagramm, feder, notiz
from tmzeichnen import FARBE, Abbildung, einspannung, kraft, kreis, linie, mass, pfeil, polylinie, text

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
    e.append(pfeil(cx - 34, cy - 18, cx - 34, cy + 26, GRAU, 1.4, (9, 6)))
    e.append(text(cx - 44, cy + 14, "g", GRAU, anker="end"))
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
    e.append(text(xs_ + 66, ys_ - 26, "h' = 0,  h'' < 0", BLAU, 17, anker="start"))
    e.append(notiz(xs_ + 66, ys_ - 4, ["Maximum: instabil"], BLAU, 15))
    e.append(text(xt_ - 70, yt_ - 30, "h' = 0,  h'' > 0", BLAU, 17, anker="end"))
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
    """Formel „links ½ rechts“ mit ½ als echtem Bruch; (X, Y) = Mitte des Bruchstrichs."""
    z, d = 0.79 * g, 0.58 * g                      # Größe und Abstand der Bruchziffern
    return "".join([
        text(X - 9, Y, links, farbe, g, anker="end") if links else "",
        text(X, Y - d, "1", farbe, z, italic=False),
        linie(X - 0.32 * g, Y, X + 0.32 * g, Y, farbe, 1.1),
        text(X, Y + d, "2", farbe, z, italic=False),
        text(X + 0.53 * g, Y, rechts, farbe, g, anker="start"),
    ])


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
    e.append(kraft(xf, ym + hm, -90, "F = m g", laenge=58, ziehend=True, label_seite=-1))

    e = abb.ebene("verschiebung", "Verschiebung")
    for yy in (yr, ym):
        e.append(linie(xf + 34, yy, xf + 96, yy, GRAU, 0.8, "4 3"))
    e.append(pfeil(xf + 80, yr, xf + 80, ym, GR, 1.4, (9, 6)))
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
    e.append(A.text(0.6, 0.6, "N ds", BLAU, dx=-6, dy=-16, groesse=14, anker="end"))
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
    e.append(D.achsen("u", "Π", [(1, "F/c"), (2, "2F/c")], [(1, ""), (-1, "")], raster=True))

    e = abb.ebene("pi_i", "Innere Energie")
    e.append(D.kurve(lambda u: u * u / 2, -0.3, 2.4, farbe=BLAU))
    X, Y = D.px(2.05, 2.05)
    e.append(_halb(X - 70, Y, "Π_i =", "c u^2", BLAU))

    e = abb.ebene("pi_a", "Äußere Energie")
    e.append(D.kurve(lambda u: -u, -0.3, 1.3, farbe=ROT))
    e.append(D.text(1.3, -1.3, "Π_a = −F u", ROT, dx=10, dy=-4, anker="start"))

    e = abb.ebene("pi_ges", "Gesamte Energie")
    e.append(D.kurve(lambda u: u * u / 2 - u, -0.3, 2.4, farbe="#000000", breite=2.6))
    e.append(D.text(2.4, 0.48, "Π_{ges} = Π_i + Π_a", "#000000", dx=-4, dy=-16, anker="end"))

    e = abb.ebene("minimum", "Minimum")
    e.append(D.hilfslinien(1, -0.5))
    e.append(D.punkt(1, -0.5, GR, 5))
    e.append(D.notiz(1, -0.5, ["Minimum"], GR, dx=14, dy=22))
    e.append(D.text(1, -0.5, "dΠ_{ges}/du = 0  ⇒  u = F/c", GR, dx=14, dy=48, anker="start"))
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
    e.append(D.achsen("p_1", "p_2", [(1, "F/k"), (2, "2F/k")], [(1, "F/k"), (-0.5, "")], raster=True))

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
    e.append(D.text(0, 0.5, "F/(2k)", GR, dx=-10, groesse=15, anker="end"))
    e.append(D.text(pm[0], pm[1], "Π_{min} = −5/4", ROT, dx=12, dy=14, groesse=16, anker="start"))
    return abb.speichern(ZIEL / "hoehenlinien.svg")


if __name__ == "__main__":
    for fn in (kugel, feder_energie, hoehenlinien):
        print(fn())

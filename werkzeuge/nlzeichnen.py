"""Ergänzungen zum TM-Zeichenbaukasten für die Nichtlinearitäten-Vorlesung.

- Federn (Wegfeder, Drehfeder), starre Stäbe
- Diagramme (Achsen, Kurven aus Funktionen, Punkte, Hilfslinien) im Stil der Tafelbilder

Farben in Diagrammen: linear blau, nichtlinear rot, Hilfslinien grau;
stabile Gleichgewichtslagen durchgezogen, instabile gestrichelt.
"""

from __future__ import annotations

import math

from tmzeichnen import (FARBE, GROESSE, STRICH, _tspans, balken, f, gruppe, kreis, linie, pfeil,
                        polylinie, text)

FARBE.update({
    "linear": "#0050b4",
    "nichtlinear": "#d40000",
    "gueltig": "#006414",
    "feder": "#000000",
    "bereich_lin": "#d8eedf",     # Fläche „linear gültig“ (hellgrün)
    "bereich_nl": "#fbe3e3",      # Fläche „nichtlinear“ (hellrot)
    "toleranz": "#f6c9c4",
})


# ---------------------------------------------------------------- Federn
def feder(x1, y1, x2, y2, windungen=5, amplitude=8, anteil=0.7, farbe=None, breite=STRICH["normal"],
          label="", label_seite=1, label_abstand=18, id_=None):
    """Zickzack-Feder von (x1,y1) nach (x2,y2); anteil = Länge des Zickzacks / Gesamtlänge."""
    farbe = farbe or FARBE["feder"]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    a = L * (1 - anteil) / 2
    pts = [(x1, y1), (x1 + ux * a, y1 + uy * a)]
    n = 2 * windungen
    for i in range(1, n):
        s = a + L * anteil * i / n
        sg = 1 if i % 2 else -1
        pts.append((x1 + ux * s + nx * amplitude * sg, y1 + uy * s + ny * amplitude * sg))
    pts += [(x2 - ux * a, y2 - uy * a), (x2, y2)]
    teile = [polylinie(pts, farbe, breite)]
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        teile.append(text(mx - nx * label_abstand * label_seite, my - ny * label_abstand * label_seite,
                          label, FARBE["mass"]))
    return gruppe(teile, id_)


def drehfeder(x, y, r=15, windungen=1.6, farbe=None, label="", label_pos=(14, -26), id_=None):
    """Drehfeder als Spirale um den Gelenkpunkt (x, y)."""
    farbe = farbe or FARBE["feder"]
    n = 80
    pts = []
    for i in range(n + 1):
        t = i / n
        w = math.radians(200) + t * windungen * 2 * math.pi
        rr = r * (0.25 + 0.75 * t)
        pts.append((x + rr * math.cos(w), y - rr * math.sin(w)))
    teile = [polylinie(pts, farbe, STRICH["normal"])]
    if label:
        teile.append(text(x + label_pos[0], y + label_pos[1], label, FARBE["mass"]))
    return gruppe(teile, id_)


def wandgelenk(x, y, hoehe=40, seite="links", id_=None):
    """Gelenk an einer schraffierten Wand (für Stab mit Drehfeder)."""
    s = -1 if seite == "links" else 1
    xw = x + s * 10
    teile = [linie(xw, y - hoehe / 2, xw, y + hoehe / 2, FARBE["linie"], STRICH["dick"])]
    yy = y - hoehe / 2
    while yy <= y + hoehe / 2 - 7.9:
        teile.append(linie(xw, yy, xw + s * 8, yy + 8, FARBE["linie"], STRICH["duenn"]))
        yy += 6
    teile.append(linie(xw, y, x, y, FARBE["linie"], STRICH["normal"]))
    teile.append(kreis(x, y, 3.6))
    return gruppe(teile, id_)


def starrer_stab(x0, y0, laenge, winkel_grad, dicke=11, id_=None):
    """Starrer Stab ab (x0, y0); winkel mathematisch (0 = rechts, negativ = nach unten gedreht)."""
    w = math.radians(winkel_grad)
    x1, y1 = x0 + laenge * math.cos(w), y0 - laenge * math.sin(w)
    return gruppe(balken(x0, y0, x1, y1, dicke), id_), (x1, y1)


def bogen(x, y, r, von, bis, farbe="#000000", breite=STRICH["duenn"], strich=None, pfeil_ende=False):
    """Kreisbogen (Grad, mathematisch), optional mit Pfeilspitze am Ende."""
    n = 30
    pts = [(x + r * math.cos(math.radians(von + (bis - von) * i / n)),
            y - r * math.sin(math.radians(von + (bis - von) * i / n))) for i in range(n + 1)]
    teile = [polylinie(pts, farbe, breite, strich=strich)]
    if pfeil_ende:
        (ax, ay), (bx, by) = pts[-3], pts[-1]
        teile.append(pfeil(ax, ay, bx, by, farbe, breite, (8, 6)))
    return gruppe(teile)


def haken(x, y, farbe=None, groesse=9):
    """Häkchen ✓ (gültig)."""
    farbe = farbe or FARBE["gueltig"]
    g = groesse
    return polylinie([(x - g, y), (x - g * 0.3, y + g * 0.7), (x + g, y - g * 0.9)], farbe, 2.4)


def kreuz(x, y, farbe=None, groesse=7):
    """Kreuz ✗ (nicht gültig)."""
    farbe = farbe or FARBE["nichtlinear"]
    g = groesse
    return gruppe([linie(x - g, y - g, x + g, y + g, farbe, 2.4), linie(x - g, y + g, x + g, y - g, farbe, 2.4)])


def notiz(x, y, zeilen, farbe="#444444", groesse=15, anker="start", zeilenabstand=1.3):
    """Mehrzeiliger aufrechter Hinweistext (Sans-Serif wie Handnotizen der Tafel)."""
    if isinstance(zeilen, str):
        zeilen = [zeilen]
    out = []
    for i, z in enumerate(zeilen):
        out.append(f'<text x="{f(x)}" y="{f(y + i * groesse * zeilenabstand + 0.34 * groesse)}" fill="{farbe}" '
                   f'stroke="#ffffff" stroke-width="4" stroke-linejoin="round" paint-order="stroke" '
                   f'font-family="\'Source Sans Pro\',\'Helvetica Neue\',Arial,sans-serif" font-size="{f(groesse)}" '
                   f'text-anchor="{anker}" xml:space="preserve">{_tspans(z, italic=False)}</text>')
    return "".join(out)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def flaeche(punkte, fuellung, deckkraft=1.0):
    d = "M " + " L ".join(f"{f(x)},{f(y)}" for x, y in punkte) + " Z"
    return f'<path d="{d}" fill="{fuellung}" fill-opacity="{deckkraft}" stroke="none"/>'


# ---------------------------------------------------------------- Diagramme
class Diagramm:
    """Koordinatensystem: Ursprung bei (X0, Y0) in px, Wertebereich [xmin, xmax] × [ymin, ymax]
    wird auf breite × hoehe px abgebildet (y nach oben)."""

    def __init__(self, X0, Y0, breite, hoehe, xmax, ymax, xmin=0.0, ymin=0.0):
        self.X0, self.Y0, self.b, self.h = X0, Y0, breite, hoehe
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax

    def px(self, x, y):
        X = self.X0 + (x - self.xmin) / (self.xmax - self.xmin) * self.b
        Y = self.Y0 - (y - self.ymin) / (self.ymax - self.ymin) * self.h
        return X, Y

    def achsen(self, xlabel="", ylabel="", xticks=(), yticks=(), achse_x0=0.0, achse_y0=0.0,
               raster=False, groesse=GROESSE):
        """Achsen durch (achse_y0 auf der x-Achse, achse_x0 …): x-Achse bei y = achse_y0,
        y-Achse bei x = achse_x0. ticks: [(wert, text)]."""
        teile = []
        xa0, ya = self.px(self.xmin, achse_y0)
        xa1, _ = self.px(self.xmax, achse_y0)
        xy, yb0 = self.px(achse_x0, self.ymin)
        _, yb1 = self.px(achse_x0, self.ymax)
        if raster:
            for v, _t in xticks:
                X, _ = self.px(v, 0)
                teile.append(linie(X, yb0, X, yb1, "#e3e6ea", 0.7))
            for v, _t in yticks:
                _, Y = self.px(0, v)
                teile.append(linie(xa0, Y, xa1, Y, "#e3e6ea", 0.7))
        teile.append(pfeil(xa0 - 4, ya, xa1 + 22, ya, "#000000", STRICH["normal"], (10, 7)))
        teile.append(pfeil(xy, yb0 + 4, xy, yb1 - 22, "#000000", STRICH["normal"], (10, 7)))
        if xlabel:
            teile.append(text(xa1 + 28, ya, xlabel, "#000000", groesse, anker="start"))
        if ylabel:
            teile.append(text(xy - 12, yb1 - 24, ylabel, "#000000", groesse, anker="end"))
        for v, t in xticks:
            X, _ = self.px(v, 0)
            teile.append(linie(X, ya - 4, X, ya + 4, "#000000", STRICH["normal"]))
            if t:
                teile.append(text(X, ya + 17, t, "#000000", 15, italic=_kursiv(t)))
        for v, t in yticks:
            _, Y = self.px(0, v)
            teile.append(linie(xy - 4, Y, xy + 4, Y, "#000000", STRICH["normal"]))
            if t:
                teile.append(text(xy - 9, Y, t, "#000000", 15, anker="end", italic=_kursiv(t)))
        return gruppe(teile)

    def kurve(self, fn=None, von=None, bis=None, n=200, punkte=None, farbe=None, breite=STRICH["dick"],
              strich=None, param=False, clip=True):
        """Kurve y = fn(x) für x in [von, bis] oder Parameterkurve fn(t) -> (x, y) (param=True),
        oder direkt aus Punkten (Wertekoordinaten)."""
        farbe = farbe or FARBE["nichtlinear"]
        if punkte is None:
            von = self.xmin if von is None else von
            bis = self.xmax if bis is None else bis
            punkte = []
            for i in range(n + 1):
                t = von + (bis - von) * i / n
                try:
                    p = fn(t) if param else (t, fn(t))
                except (ValueError, ZeroDivisionError):
                    continue
                punkte.append(p)
        stuecke, akt = [], []
        for x, y in punkte:
            innen = (self.xmin - 1e-9 <= x <= self.xmax + 1e-9 and self.ymin - 1e-9 <= y <= self.ymax + 1e-9)
            if innen or not clip:
                akt.append(self.px(x, y))
            elif akt:
                stuecke.append(akt)
                akt = []
        if akt:
            stuecke.append(akt)
        return gruppe([polylinie(s, farbe, breite, strich=strich) for s in stuecke if len(s) > 1])

    def punkt(self, x, y, farbe="#000000", r=4.2, hohl=False):
        X, Y = self.px(x, y)
        return kreis(X, Y, r, farbe, "#ffffff" if hohl else farbe, 1.4)

    def hilfslinien(self, x, y, farbe="#7a7a7a", nach_x=True, nach_y=True, strich="4 3"):
        X, Y = self.px(x, y)
        X0, Y0 = self.px(0 if self.xmin <= 0 <= self.xmax else self.xmin, 0 if self.ymin <= 0 <= self.ymax else self.ymin)
        teile = []
        if nach_x:
            teile.append(linie(X, Y, X, Y0, farbe, 0.9, strich))
        if nach_y:
            teile.append(linie(X, Y, X0, Y, farbe, 0.9, strich))
        return gruppe(teile)

    def text(self, x, y, label, farbe="#000000", dx=0, dy=0, **kw):
        X, Y = self.px(x, y)
        return text(X + dx, Y + dy, label, farbe, **kw)

    def notiz(self, x, y, zeilen, farbe="#444444", dx=0, dy=0, **kw):
        X, Y = self.px(x, y)
        return notiz(X + dx, Y + dy, zeilen, farbe, **kw)

    def linie(self, x1, y1, x2, y2, farbe="#000000", breite=STRICH["normal"], strich=None):
        return linie(*self.px(x1, y1), *self.px(x2, y2), farbe, breite, strich)

    def pfeil(self, x1, y1, x2, y2, farbe="#000000", breite=STRICH["normal"], spitze=(9, 6)):
        return pfeil(*self.px(x1, y1), *self.px(x2, y2), farbe, breite, spitze)

    def flaeche(self, punkte, fuellung, deckkraft=1.0):
        return flaeche([self.px(x, y) for x, y in punkte], fuellung, deckkraft)


def _kursiv(t):
    return not any(c.isdigit() for c in t) or any(c.isalpha() and c not in "e" for c in t)

"""TM-Zeichenbaukasten

Erzeugt Inkscape-kompatible SVG-Grafiken für die Technische Mechanik im Stil
der vorhandenen Skizzen (Lasten rot, Bemaßung/Koordinaten grün, Bauteile grau).

Jede Grafik besteht aus benannten Inkscape-Ebenen. Auf der Webseite entspricht
eine Ebene einem Scroll-Schritt; in Inkscape lassen sich die Ebenen ganz normal
ein-/ausblenden und bearbeiten.

Koordinaten sind SVG-Pixel (x nach rechts, y nach unten = z-Richtung).

Beschriftungen:  "A_H", "q_0", "M_{max}", "[I]" (eckige Klammern = aufrecht),
                 "F^2" (hochgestellt). Griechische Buchstaben direkt (α, φ, …).
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- Stil
FARBE = {
    "last": "#ff0000",          # eingeprägte Lasten F, q, M
    "reaktion": "#ff0000",      # Lager- und Gelenkreaktionen (wie Gross: alle Kräfte rot)
    "schnitt": "#ff0000",       # Schnittgrößen N, Q, M
    "mass": "#006414",          # Bemaßung, Lagerbezeichnungen, Winkel
    "koord": "#006414",         # Koordinatensysteme
    "linie": "#000000",
    "bauteil": "#e6e6e6",       # Balken/Stab-Füllung
    "lager": "#d9d9d9",         # Lagerkörper
    "verlauf": "#d40000",       # Schnittgrößenverlauf positiv: Kontur
    "verlauf_flaeche": "#fbe3e3",
    "verlauf_neg": "#0050b4",   # Schnittgrößenverlauf negativ: Kontur
    "verlauf_neg_flaeche": "#dde7f5",
    "hinweis": "#7a7a7a",       # Hilfslinien
}
SCHRIFT = "'Latin Modern Roman','LM Roman 10','CMU Serif',serif"
TEXTSCHRIFT = "'Source Sans Pro','Helvetica Neue',Arial,sans-serif"   # Wörter wie auf der Webseite
GROESSE = 19          # Schriftgröße Formelzeichen
STRICH = {"duenn": 0.8, "normal": 1.25, "dick": 1.9}


def f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


# ---------------------------------------------------------------- Text
_TOKEN = re.compile(r"\[([^\]]*)\]|([_^])(\{[^}]*\}|.)|([^\[_^]+)")


def _tspans(label: str, italic: bool = True) -> str:
    out = []
    for up, op, arg, plain in _TOKEN.findall(label):
        if up:
            out.append(f'<tspan font-style="normal">{escape(up)}</tspan>')
        elif op:
            arg = arg[1:-1] if arg.startswith("{") else arg
            shift = "sub" if op == "_" else "super"
            # Indizes aus Ziffern/Großbuchstaben aufrecht, sonst kursiv
            style = "normal" if re.fullmatch(r"[0-9A-ZIV,. ]+|max|min|ges|res", arg) else ("italic" if italic else "normal")
            out.append(f'<tspan baseline-shift="{shift}" font-size="70%" font-style="{style}">{escape(arg)}</tspan>')
        else:
            out.append(f"<tspan>{escape(plain)}</tspan>")
    return "".join(out)


_WORT = re.compile(r"[A-Za-zÄÖÜäöüß]*[a-zäöüß]{2}[A-Za-zÄÖÜäöüß]*")
_FUNKTION = {"sin", "cos", "tan", "exp", "log", "det"}


def ist_wort(label: str) -> bool:
    """True, wenn die Beschriftung geschriebenen Text enthält (ein Wort mit mindestens drei Buchstaben,
    davon zwei klein, z. B. „Bereich I“, „Freischnitt“, „Max (…)“). Indizes (M_{max}) und Einheiten (MPa)
    zählen nicht; reine Formelzeichen bleiben in der Formelschrift."""
    ohne_index = re.sub(r"[_^](\{[^}]*\}|.)", "", label)
    return any(len(w) >= 3 and w.lower() not in _FUNKTION for w in _WORT.findall(ohne_index))


def text(x, y, label, farbe="#000000", groesse=GROESSE, anker="middle", italic=True, id_=None, halo=True):
    """Text mit Referenzpunkt (x, y) = Mitte der Zeile (vertikal zentriert).
    halo: weißer Rand, damit Beschriftungen über Linien und Flächen lesbar bleiben.
    Geschriebene Wörter erscheinen automatisch aufrecht in der Textschrift der Webseite (Source Sans Pro),
    Formelzeichen in Latin Modern."""
    wort = ist_wort(label)
    if wort:
        italic, groesse = False, groesse * 0.85
    style = "italic" if italic else "normal"
    idattr = f' id="{id_}"' if id_ else ""
    h = ' stroke="#ffffff" stroke-width="4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text{idattr} x="{f(x)}" y="{f(y + 0.34 * groesse)}" fill="{farbe}"{h} '
            f'font-family="{TEXTSCHRIFT if wort else SCHRIFT}" font-size="{f(groesse)}" font-style="{style}" '
            f'text-anchor="{anker}" xml:space="preserve">{_tspans(label, italic)}</text>')


# ---------------------------------------------------------------- Grundformen
def linie(x1, y1, x2, y2, farbe="#000000", breite=STRICH["normal"], strich=None, kappe="butt"):
    dash = f' stroke-dasharray="{strich}"' if strich else ""
    return (f'<path d="M {f(x1)},{f(y1)} L {f(x2)},{f(y2)}" fill="none" stroke="{farbe}" '
            f'stroke-width="{f(breite)}" stroke-linecap="{kappe}"{dash}/>')


def polylinie(punkte, farbe="#000000", breite=STRICH["normal"], fuellung="none", strich=None, schliessen=False):
    d = "M " + " L ".join(f"{f(x)},{f(y)}" for x, y in punkte) + (" Z" if schliessen else "")
    dash = f' stroke-dasharray="{strich}"' if strich else ""
    stroke = f'stroke="{farbe}" stroke-width="{f(breite)}"' if farbe else 'stroke="none"'
    return f'<path d="{d}" fill="{fuellung}" {stroke} stroke-linejoin="round"{dash}/>'


def kreis(x, y, r, farbe="#000000", fuellung="#ffffff", breite=STRICH["normal"]):
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fuellung}" '
            f'stroke="{farbe}" stroke-width="{f(breite)}"/>')


def gruppe(inhalt, id_=None, transform=None, klasse=None):
    a = ""
    if id_:
        a += f' id="{id_}"'
    if transform:
        a += f' transform="{transform}"'
    if klasse:
        a += f' class="{klasse}"'
    return f"<g{a}>" + "".join(inhalt if isinstance(inhalt, (list, tuple)) else [inhalt]) + "</g>"


def _spitze(x, y, ux, uy, farbe, laenge, breite):
    bx, by = x - ux * laenge, y - uy * laenge
    nx, ny = -uy * breite / 2, ux * breite / 2
    return polylinie([(x, y), (bx + nx, by + ny), (bx - nx, by - ny)], farbe=None, fuellung=farbe, schliessen=True)


def pfeil(x1, y1, x2, y2, farbe="#000000", breite=STRICH["dick"], spitze=(12, 8), beidseitig=False):
    """Pfeil von (x1,y1) nach (x2,y2); Spitze bei (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    hl, hw = spitze
    sx1, sy1 = (x1 + ux * hl * 0.8, y1 + uy * hl * 0.8) if beidseitig else (x1, y1)
    teile = [linie(sx1, sy1, x2 - ux * hl * 0.8, y2 - uy * hl * 0.8, farbe, breite),
             _spitze(x2, y2, ux, uy, farbe, hl, hw)]
    if beidseitig:
        teile.append(_spitze(x1, y1, -ux, -uy, farbe, hl, hw))
    return gruppe(teile)


# ---------------------------------------------------------------- Lasten
def kraft(x, y, winkel, label="", farbe=None, laenge=55, ziehend=False, label_abstand=9,
          label_seite=1, label_pos=0.7, id_=None):
    """Einzelkraft mit Angriffspunkt (x, y).

    winkel: Richtung des Pfeils in Grad, mathematisch (0 = nach rechts, 90 = nach oben).
    ziehend=False: Spitze sitzt am Angriffspunkt (drückend), sonst beginnt der Pfeil dort.
    label_seite: +1 / -1 Seite des Labels neben dem Pfeil.
    label_pos: Lage des Labels längs des Pfeils (0 = Angriffspunkt, 1 = freies Pfeilende).
    """
    farbe = farbe or FARBE["last"]
    ux, uy = math.cos(math.radians(winkel)), -math.sin(math.radians(winkel))
    if ziehend:
        x1, y1, x2, y2 = x, y, x + ux * laenge, y + uy * laenge
        px, py = x + ux * laenge * label_pos, y + uy * laenge * label_pos
    else:
        x1, y1, x2, y2 = x - ux * laenge, y - uy * laenge, x, y
        px, py = x - ux * laenge * label_pos, y - uy * laenge * label_pos
    teile = [pfeil(x1, y1, x2, y2, farbe)]
    if label:
        nx, ny = -uy * label_seite, ux * label_seite
        # Text so ausrichten, dass er neben (nicht auf) dem Pfeil steht
        anker = "start" if nx > 0.3 else ("end" if nx < -0.3 else "middle")
        dy = ny * 9 if anker == "middle" else 0
        teile.append(text(px + nx * label_abstand, py + ny * label_abstand + dy, label, farbe, anker=anker))
    return gruppe(teile, id_)


def moment(x, y, label="", gegen_uhrzeiger=True, r=17, start=-60, bogen=250, farbe=None,
           label_pos=None, id_=None):
    """Momentenpfeil (Kreisbogen) um (x, y). start/bogen in Grad, mathematisch."""
    farbe = farbe or FARBE["last"]
    s = 1 if gegen_uhrzeiger else -1
    n = 40
    pts = []
    for i in range(n + 1):
        t = math.radians(start + s * bogen * i / n)
        pts.append((x + r * math.cos(t), y - r * math.sin(t)))
    te = math.radians(start + s * bogen)
    # Tangente am Ende
    ux, uy = -math.sin(te) * s, -math.cos(te) * s
    hl = 11
    # Bogen etwas kürzen, damit die Spitze sauber sitzt
    teile = [polylinie(pts[:-3], farbe, STRICH["dick"]),
             _spitze(pts[-1][0] + ux * 3, pts[-1][1] + uy * 3, ux, uy, farbe, hl, 8)]
    if label:
        lx, ly = label_pos if label_pos else (x + r + 12, y - r - 4)
        teile.append(text(lx, ly, label, farbe))
    return gruppe(teile, id_)


def streckenlast(x0, x1, y, h0, h1=None, label="", farbe=None, n=None, label_rechts=True,
                 oben=True, id_=None):
    """Streckenlast auf einer horizontalen Linie y (Balkenoberkante), Pfeile zum Balken.

    h0, h1: Pfeillänge (Lastordinate) am Anfang/Ende in px (linear dazwischen).
    """
    farbe = farbe or FARBE["last"]
    h1 = h0 if h1 is None else h1
    n = n or max(2, int(abs(x1 - x0) / 18))
    s = -1 if oben else 1
    teile = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * (x1 - x0)
        h = h0 + t * (h1 - h0)
        if abs(h) > 4:
            teile.append(pfeil(x, y + s * h, x, y, farbe, STRICH["normal"], (8, 5.5)))
    teile.append(linie(x0, y + s * h0, x1, y + s * h1, farbe, STRICH["normal"]))
    if label:
        if label_rechts:
            teile.append(text(x1 + 6, y + s * h1 - 4, label, farbe, anker="start"))
        else:
            teile.append(text(x0 - 6, y + s * h0 - 4, label, farbe, anker="end"))
    return gruppe(teile, id_)


# ---------------------------------------------------------------- Bauteile & Lager
def balken(x0, y0, x1, y1, dicke=7, id_=None):
    """Balken/Stab als graues Rechteck zwischen zwei Punkten (Achse)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * dicke / 2, dx / L * dicke / 2
    return gruppe(polylinie([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)],
                            FARBE["linie"], STRICH["normal"], FARBE["bauteil"], schliessen=True), id_)


def balkenzug(punkte, dicke=7, id_=None):
    """Abgewinkelter Balken/Rahmen als EINE durchgehende Fläche entlang der Achspunkte
    (Gehrung an den Ecken, keine Stückelung aus Einzelrechtecken)."""
    h = dicke / 2

    def normale(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        return -dy / L, dx / L

    links, rechts = [], []
    for i, p in enumerate(punkte):
        if i == 0:
            (nx, ny), m = normale(p, punkte[1]), 1.0
        elif i == len(punkte) - 1:
            (nx, ny), m = normale(punkte[i - 1], p), 1.0
        else:
            n1, n2 = normale(punkte[i - 1], p), normale(p, punkte[i + 1])
            sx, sy = n1[0] + n2[0], n1[1] + n2[1]
            Ls = math.hypot(sx, sy)
            nx, ny = sx / Ls, sy / Ls
            m = 1 / max(0.2, nx * n1[0] + ny * n1[1])      # Gehrungslänge
        links.append((p[0] + nx * h * m, p[1] + ny * h * m))
        rechts.append((p[0] - nx * h * m, p[1] - ny * h * m))
    return gruppe(polylinie(links + rechts[::-1], FARBE["linie"], STRICH["normal"], FARBE["bauteil"],
                            schliessen=True), id_)


def _schraffur(x0, x1, y, tiefe=7, abstand=6):
    teile = [linie(x0, y, x1, y, FARBE["linie"], STRICH["normal"])]
    x = x0 + 2
    while x <= x1 + 0.1:
        teile.append(linie(x, y, x - tiefe, y + tiefe, FARBE["linie"], STRICH["duenn"]))
        x += abstand
    return teile


def festlager(x, y, groesse=13, drehung=0, label="", label_pos=(-16, 10), id_=None):
    """Festlager (zweiwertig); Gelenkpunkt bei (x, y), Lager darunter."""
    s = groesse
    teile = [polylinie([(x, y), (x - 0.85 * s, y + 1.35 * s), (x + 0.85 * s, y + 1.35 * s)],
                       FARBE["linie"], STRICH["normal"], FARBE["lager"], schliessen=True)]
    teile += _schraffur(x - 1.35 * s, x + 1.35 * s, y + 1.35 * s)
    teile.append(kreis(x, y, 3.2))
    g = gruppe(teile, transform=f"rotate({f(drehung)} {f(x)} {f(y)})" if drehung else None)
    out = [g]
    if label:
        out.append(text(x + label_pos[0], y + label_pos[1], label, FARBE["mass"]))
    return gruppe(out, id_)


def loslager(x, y, groesse=13, drehung=0, label="", label_pos=(-16, 10), id_=None):
    """Loslager (einwertig): wie Festlager mit Spalt (verschieblich)."""
    s = groesse
    yb = y + 1.35 * s
    teile = [polylinie([(x, y), (x - 0.85 * s, yb), (x + 0.85 * s, yb)],
                       FARBE["linie"], STRICH["normal"], FARBE["lager"], schliessen=True),
             linie(x - 1.2 * s, yb, x + 1.2 * s, yb, FARBE["linie"], STRICH["normal"])]
    teile += _schraffur(x - 1.35 * s, x + 1.35 * s, yb + 4.5)
    teile.append(kreis(x, y, 3.2))
    g = gruppe(teile, transform=f"rotate({f(drehung)} {f(x)} {f(y)})" if drehung else None)
    out = [g]
    if label:
        out.append(text(x + label_pos[0], y + label_pos[1], label, FARBE["mass"]))
    return gruppe(out, id_)


def einspannung(x, y, hoehe=44, seite="links", label="", id_=None):
    """Feste Einspannung an der Stelle x: Wandlinie mit Schraffur (Wand links oder rechts vom Balken)."""
    s = -1 if seite == "links" else 1
    teile = [linie(x, y - hoehe / 2, x, y + hoehe / 2, FARBE["linie"], STRICH["dick"])]
    yy = y - hoehe / 2
    while yy <= y + hoehe / 2 - 7.9:
        teile.append(linie(x, yy, x + s * 8, yy + 8, FARBE["linie"], STRICH["duenn"]))
        yy += 6
    if label:
        teile.append(text(x + s * 16, y - hoehe / 2 - 8, label, FARBE["mass"]))
    return gruppe(teile, id_)


def gelenk(x, y, r=3.6, id_=None):
    return gruppe(kreis(x, y, r), id_)


# ---------------------------------------------------------------- Bemaßung, Koordinaten
def mass(x1, y1, x2, y2, label="", abstand=30, farbe=None, id_=None, hilfslinien=True):
    """Maßlinie zwischen (x1,y1) und (x2,y2), um 'abstand' senkrecht versetzt
    (positiv = links der Richtung 1→2, bei horizontaler Bemaßung also nach oben)."""
    farbe = farbe or FARBE["mass"]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = uy, -ux
    a = abstand
    p1 = (x1 + nx * a, y1 + ny * a)
    p2 = (x2 + nx * a, y2 + ny * a)
    teile = []
    if hilfslinien:
        sg = 1 if a >= 0 else -1
        for (px, py), (qx, qy) in (((x1, y1), p1), ((x2, y2), p2)):
            teile.append(linie(px + nx * sg * 4, py + ny * sg * 4, qx + nx * sg * 6, qy + ny * sg * 6,
                               farbe, STRICH["duenn"]))
    teile.append(pfeil(*p1, *p2, farbe=farbe, breite=STRICH["duenn"], spitze=(8, 5), beidseitig=True))
    if label:
        sg = 1 if a >= 0 else -1
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        teile.append(text(mx + nx * sg * 11, my + ny * sg * 11, label, farbe))
    return gruppe(teile, id_)


def koordinaten(x, y, laenge=38, xlabel="x", zlabel="z", farbe=None, id_=None, nur_x=False):
    farbe = farbe or FARBE["koord"]
    teile = [pfeil(x, y, x + laenge, y, farbe, STRICH["normal"], (8, 5)),
             text(x + laenge + 4, y + 11, xlabel, farbe, anker="start")]
    if not nur_x:
        teile += [pfeil(x, y, x, y + laenge, farbe, STRICH["normal"], (8, 5)),
                  text(x + 6, y + laenge + 2, zlabel, farbe, anker="start")]
    return gruppe(teile, id_)


def nummer(x, y, n, r=9.5, farbe="#000000", id_=None):
    """Eingekreiste Nummer (Bereiche, Stäbe)."""
    return gruppe([kreis(x, y, r, farbe, "#ffffff", STRICH["duenn"]),
                   text(x, y, f"[{n}]", farbe, 14, italic=False)], id_)


def winkelbogen(x, y, r, von, bis, label="", farbe=None, id_=None):
    farbe = farbe or FARBE["mass"]
    pts = [(x + r * math.cos(math.radians(von + (bis - von) * i / 20)),
            y - r * math.sin(math.radians(von + (bis - von) * i / 20))) for i in range(21)]
    teile = [polylinie(pts, farbe, STRICH["duenn"])]
    if label:
        m = math.radians((von + bis) / 2)
        teile.append(text(x + (r + 10) * math.cos(m), y - (r + 10) * math.sin(m), label, farbe, 15))
    return gruppe(teile, id_)


# ---------------------------------------------------------------- Schnittgrößen
def schnittufer(x, y, positiv=True, N="N", Q="Q", M="M", farbe=None, dicke=7, laenge=36,
                zeige=("N", "Q", "M"), id_=None):
    """Schnittgrößen am Schnittufer bei x (Balkenachse y), positive Richtungen.

    positiv=True: positives Schnittufer (Außennormale in +x, rechtes Ende eines
    linken Teils): N nach rechts, Q nach unten, M im Uhrzeigersinn.
    """
    farbe = farbe or FARBE["schnitt"]
    s = 1 if positiv else -1
    teile = []
    if "N" in zeige:
        teile.append(pfeil(x + s * 9, y, x + s * (laenge + 9), y, farbe))
        teile.append(text(x + s * (laenge + 16), y + 1, N, farbe, anker="start" if positiv else "end"))
    if "Q" in zeige:
        xq = x + s * 4
        y1, y2 = (y - laenge / 2, y + laenge / 2) if positiv else (y + laenge / 2, y - laenge / 2)
        teile.append(pfeil(xq, y1, xq, y2, farbe))
        # Label unter dem Balken auf der Seite des Teilsystems (dort ist Platz)
        teile.append(text(xq - s * 8, y + laenge / 2 - 2, Q, farbe,
                          anker="end" if positiv else "start"))
    if "M" in zeige:
        # untere Faser auf Zug: am positiven Ufer gegen den Uhrzeigersinn (bei z nach unten),
        # am negativen Ufer im Uhrzeigersinn
        if positiv:
            teile.append(moment(x, y, "", gegen_uhrzeiger=True, r=20, start=25, bogen=135, farbe=farbe))
            teile.append(text(x + 10, y - 31, M, farbe, anker="start"))
        else:
            teile.append(moment(x, y, "", gegen_uhrzeiger=False, r=20, start=155, bogen=135, farbe=farbe))
            teile.append(text(x - 10, y - 31, M, farbe, anker="end"))
    return gruppe(teile, id_)


def schnittlinie(x, y, hoehe=34, label="", farbe="#000000", id_=None):
    teile = [linie(x, y - hoehe / 2, x, y + hoehe / 2, farbe, STRICH["normal"], strich="5 3")]
    if label:
        teile.append(text(x, y - hoehe / 2 - 9, label, farbe, 15))
    return gruppe(teile, id_)


def vorzeichen_symbol(x, y, positiv, r=7.5, farbe="#000000"):
    """⊕ bzw. ⊖ als gezeichnetes Symbol (unabhängig von der Schrift)."""
    teile = [kreis(x, y, r, farbe, "#ffffff", 1.0), linie(x - r * 0.55, y, x + r * 0.55, y, farbe, 1.2)]
    if positiv:
        teile.append(linie(x, y - r * 0.55, x, y + r * 0.55, farbe, 1.2))
    return gruppe(teile)


def verlauf(x0, punkte, skala, y0, laenge, label="", positiv_unten=False, schraffur=8,
            farbe=None, fuellung=None, werte=(), achse_label=True, vorzeichen=True, id_=None,
            farbe_neg=None, fuellung_neg=None):
    """Schnittgrößenverlauf über der Balkenachse.

    punkte: Liste (xi, wert) mit xi in px relativ zu x0 (Sprünge: gleiche xi doppelt).
    skala:  px pro Werteinheit. positiv_unten=False: positive Werte oberhalb der Achse
            (Konvention der Vorlesung 2013); True: in z-Richtung nach unten.
    werte:  [(xi, wert, text, anker)] zusätzliche Beschriftungen an der Kurve.
    Positive Bereiche rot (farbe/fuellung), negative blau (farbe_neg/fuellung_neg).
    """
    stil = {1: (farbe or FARBE["verlauf"], fuellung or FARBE["verlauf_flaeche"]),
            -1: (farbe_neg or FARBE["verlauf_neg"], fuellung_neg or FARBE["verlauf_neg_flaeche"])}
    s = 1 if positiv_unten else -1
    teile = []
    for vz, abschnitt in _vorzeichen_abschnitte(punkte):
        kontur, flaeche = stil[vz]
        kurve = [(x0 + xi, y0 + s * v * skala) for xi, v in abschnitt]
        teile.append(polylinie([(kurve[0][0], y0)] + kurve + [(kurve[-1][0], y0)], None,
                               fuellung=flaeche, schliessen=True))
        if schraffur:
            xs = punkte[0][0] + schraffur / 2
            while xs < punkte[-1][0]:
                if abschnitt[0][0] <= xs <= abschnitt[-1][0]:
                    v = _interp(abschnitt, xs)
                    if abs(v * skala) > 1.5:
                        teile.append(linie(x0 + xs, y0, x0 + xs, y0 + s * v * skala, kontur, 0.6))
                xs += schraffur
        teile.append(polylinie(kurve, kontur, STRICH["dick"]))
    teile.append(linie(x0 - 8, y0, x0 + laenge + 14, y0, "#000000", STRICH["normal"]))
    if label:
        teile.append(text(x0 - 16, y0, label, "#000000", anker="end"))
    if vorzeichen:
        # ⊕/⊖ in der Mitte des jeweils größten positiven bzw. negativen Abschnitts
        for pos in (True, False):
            abschnitte, akt = [], []
            x_a, x_e = punkte[0][0], punkte[-1][0]
            proben = [(x_a + (x_e - x_a) * k / 200, _interp(punkte, x_a + (x_e - x_a) * k / 200)) for k in range(201)]
            for xi, v in proben:
                if (v > 1e-9) if pos else (v < -1e-9):
                    akt.append((xi, v))
                elif akt:
                    abschnitte.append(akt); akt = []
            if akt:
                abschnitte.append(akt)
            abschnitte = [a for a in abschnitte if a[-1][0] - a[0][0] > 20]
            if abschnitte:
                a = max(abschnitte, key=lambda a: (a[-1][0] - a[0][0]) * max(abs(v) for _, v in a))
                xm = (a[0][0] + a[-1][0]) / 2
                # Symbol dort, wo die Fläche am höchsten ist (innerhalb des Abschnitts)
                xm, vm = max(a[len(a) // 5: len(a) - len(a) // 5] or a, key=lambda p: abs(p[1]))
                if abs(vm * skala) > 18:
                    teile.append(vorzeichen_symbol(x0 + xm, y0 + s * vm * skala / 2, pos))
    for xi, v, t, anker in werte:
        dy = s * (14 if v >= 0 else -14)
        teile.append(text(x0 + xi, y0 + s * v * skala + dy, t, stil[1 if v >= 0 else -1][0], 15, anker=anker,
                          italic=not re.match(r"^[−-]?\d", t)))
    if achse_label:
        teile.append(text(x0 + laenge + 18, y0, "x", "#000000", 15, anker="start"))
    return gruppe(teile, id_)


def _vorzeichen_abschnitte(punkte):
    """Zerlegt den Verlauf in Abschnitte gleichen Vorzeichens, Nulldurchgänge eingefügt.

    Liefert [(vorzeichen, [(xi, wert), ...])]; Abschnitte mit Wert 0 entfallen.
    """
    sg = lambda v: (v > 1e-9) - (v < -1e-9)
    abschnitte, akt, akt_vz = [], [], 0
    for (xa, va), (xb, vb) in zip(punkte, punkte[1:]):
        if sg(va) * sg(vb) < 0:          # Vorzeichenwechsel: Nullstelle einfügen
            xn = xa + (xb - xa) * va / (va - vb)
            stuecke = [((xa, va), (xn, 0.0)), ((xn, 0.0), (xb, vb))]
        else:
            stuecke = [((xa, va), (xb, vb))]
        for (p, q) in stuecke:
            vz = sg(p[1]) or sg(q[1])
            if vz != akt_vz:
                if akt_vz:
                    abschnitte.append((akt_vz, akt))
                akt, akt_vz = [p], vz
            if vz:
                akt.append(q)
    if akt_vz:
        abschnitte.append((akt_vz, akt))
    return abschnitte


def _interp(punkte, x):
    for (xa, va), (xb, vb) in zip(punkte, punkte[1:]):
        if xa <= x <= xb and xb > xa:
            return va + (vb - va) * (x - xa) / (xb - xa)
    return 0.0


# ---------------------------------------------------------------- Abbildung mit Ebenen
class Abbildung:
    """SVG-Dokument mit benannten Inkscape-Ebenen."""

    def __init__(self, breite, hoehe, titel=""):
        self.breite, self.hoehe, self.titel = breite, hoehe, titel
        self.ebenen: list[tuple[str, str, list[str]]] = []

    def ebene(self, id_, label=None):
        teile: list[str] = []
        self.ebenen.append((id_, label or id_, teile))
        return teile

    def svg(self) -> str:
        kopf = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
                f'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" '
                f'width="{f(self.breite)}" height="{f(self.hoehe)}" '
                f'viewBox="0 0 {f(self.breite)} {f(self.hoehe)}" class="tm-grafik">')
        teile = [kopf]
        if self.titel:
            teile.append(f"<title>{escape(self.titel)}</title>")
        for i, (id_, label, inhalt) in enumerate(self.ebenen, 1):
            teile.append(f'<g inkscape:groupmode="layer" id="{id_}" '
                         f'inkscape:label="{i:02d} {escape(label)}" data-ebene="{id_}">')
            teile.extend(inhalt)
            teile.append("</g>")
        teile.append("</svg>")
        return "\n".join(teile)

    def speichern(self, pfad, ueberschreiben=False):
        """Schreibt die SVG-Datei. Eine in Inkscape gespeicherte (nachbearbeitete) Datei
        wird nicht überschrieben, außer mit ueberschreiben=True."""
        pfad = Path(pfad)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        if not ueberschreiben and pfad.exists() and any(m in pfad.read_text(encoding="utf-8")[:4000] for m in ("inkscape:version=", "sodipodi:docname=")):
            print(f"  übersprungen (in Inkscape bearbeitet): {pfad.name}")
            return pfad
        pfad.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + self.svg(), encoding="utf-8")
        return pfad

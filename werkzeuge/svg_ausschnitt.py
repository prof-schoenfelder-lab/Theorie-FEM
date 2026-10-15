"""Schneidet einen Bereich aus einer vorhandenen SVG-Tafelseite aus und speichert ihn als eigenständige SVG.

    python werkzeuge/svg_ausschnitt.py quelle.svg ziel.svg X0 Y0 X1 Y1 [--rand 4] [--ohne id1,id2]
    python werkzeuge/svg_ausschnitt.py quelle.svg --vorschau vorschau.png

Der Bereich wird in Anteilen der Seite angegeben (0 … 1, links oben = 0 0). Mit --vorschau entsteht ein
PNG mit 10-%-Raster, aus dem man den Bereich abliest.

Behalten wird jedes sichtbare Objekt, dessen Mittelpunkt im Bereich liegt (Größen von Inkscape
`--query-all`). Gruppen, Transformationen, <defs> (Marker, Verläufe, Symbole) bleiben erhalten; die
Ansicht (viewBox) wird eng um die behaltenen Objekte gelegt. Das Ergebnis ist mit Inkscape weiter
bearbeitbar; vor_render.py überschreibt es nicht, da es nicht von einem grafiken_*.py erzeugt wird.
"""

import argparse
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "http://www.w3.org/2000/svg"
INK = "http://www.inkscape.org/namespaces/inkscape"
NICHT_GRAFISCH = {"defs", "style", "metadata", "namedview", "title", "desc", "script"}


def _lokal(tag):
    return tag.rsplit("}", 1)[-1]


def _namensraeume(pfad):
    for _, (praefix, uri) in ET.iterparse(pfad, events=["start-ns"]):
        try:
            ET.register_namespace(praefix, uri)
        except ValueError:                            # z. B. "ns1" (TexText) ist in ElementTree reserviert
            ET.register_namespace(praefix + "_", uri)


def _laenge(s):
    """Länge mit Einheit → px (96 dpi)."""
    m = re.fullmatch(r"\s*([0-9.eE+-]+)\s*(mm|cm|in|pt|px)?\s*", s or "")
    if not m:
        return None
    v = float(m.group(1))
    return v * {"mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96, "pt": 96 / 72, "px": 1, None: 1}[m.group(2)]


def _abfrage(pfad):
    aus = subprocess.run(["inkscape", "--query-all", str(pfad)], capture_output=True, text=True, check=True).stdout
    boxen = {}
    for zeile in aus.splitlines():
        teile = zeile.split(",")
        if len(teile) == 5:
            boxen[teile[0]] = tuple(map(float, teile[1:]))
    return boxen


def vorschau(quelle, ziel):
    svg = Path(quelle).read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", svg, re.S)
    root = ET.fromstring(svg.encode())
    vb = list(map(float, root.get("viewBox").replace(",", " ").split()))
    linien = []
    for i in range(1, 10):
        x = vb[0] + vb[2] * i / 10
        y = vb[1] + vb[3] * i / 10
        w = vb[2] / 1500
        linien.append(f'<line x1="{x}" y1="{vb[1]}" x2="{x}" y2="{vb[1] + vb[3]}" stroke="#00a0ff" stroke-width="{w}"/>'
                      f'<text x="{x + w * 3}" y="{vb[1] + vb[2] / 60}" font-size="{vb[2] / 70}" fill="#00a0ff">{i / 10:.1f}</text>'
                      f'<line x1="{vb[0]}" y1="{y}" x2="{vb[0] + vb[2]}" y2="{y}" stroke="#00a0ff" stroke-width="{w}"/>'
                      f'<text x="{vb[0] + w * 3}" y="{y - w * 3}" font-size="{vb[2] / 70}" fill="#00a0ff">{i / 10:.1f}</text>')
    svg = svg[:svg.rfind("</svg>")] + "".join(linien) + "</svg>"
    subprocess.run(["rsvg-convert", "-w", "1200", "-b", "white", "-o", str(ziel)], input=svg.encode(), check=True)


def ausschneiden(quelle, ziel, bereich, rand=4.0, ohne=()):
    _namensraeume(quelle)
    baum = ET.parse(quelle)
    root = baum.getroot()
    # jedem Element eine id geben, damit Inkscape alle Größen liefert
    n = 0
    for el in root.iter():
        if el.get("id") is None:
            n += 1
            el.set("id", f"ausschnitt{n}")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_svg = Path(tmp) / "mit_ids.svg"
        baum.write(tmp_svg, encoding="utf-8", xml_declaration=True)
        boxen = _abfrage(tmp_svg)

    seite_b, seite_h = _laenge(root.get("width")), _laenge(root.get("height"))
    vb = list(map(float, root.get("viewBox").replace(",", " ").split()))
    if seite_b is None:
        seite_b, seite_h = vb[2], vb[3]
    s = vb[2] / seite_b                                   # Nutzereinheiten je px
    x0, y0, x1, y1 = bereich[0] * seite_b, bereich[1] * seite_h, bereich[2] * seite_b, bereich[3] * seite_h

    eltern = {k: v for v in root.iter() for k in v}

    def innen(el):
        b = boxen.get(el.get("id"))
        if not b or el.get("id") in ohne:
            return False
        mx, my = b[0] + b[2] / 2, b[1] + b[3] / 2
        return x0 <= mx <= x1 and y0 <= my <= y1 and b[2] <= (x1 - x0) * 1.05 and b[3] <= (y1 - y0) * 1.05

    # Blätter (grafische Objekte ohne grafische Kinder) bewerten, Gruppen über ihre Kinder
    behalten = set()
    for el in root.iter():
        if _lokal(el.tag) in NICHT_GRAFISCH or any(_lokal(a.tag) in NICHT_GRAFISCH for a in _vorfahren(el, eltern)):
            continue
        kinder = [k for k in el if _lokal(k.tag) not in NICHT_GRAFISCH]
        ist_text = _lokal(el.tag) == "text"
        if (not kinder or ist_text) and el is not root and innen(el):
            behalten.add(el)
            behalten.update(_vorfahren(el, eltern))
            if ist_text:
                behalten.update(el.iter())

    def aufraeumen(el):
        for k in list(el):
            if _lokal(k.tag) in NICHT_GRAFISCH:
                continue
            if k not in behalten:
                el.remove(k)
            elif _lokal(k.tag) != "text":
                aufraeumen(k)
    aufraeumen(root)

    blaetter = [boxen[e.get("id")] for e in behalten if e.get("id") in boxen and not [k for k in e if k in behalten]]
    if not blaetter:
        raise SystemExit("Im Bereich liegt kein Objekt.")
    bx0 = min(b[0] for b in blaetter) - rand
    by0 = min(b[1] for b in blaetter) - rand
    bx1 = max(b[0] + b[2] for b in blaetter) + rand
    by1 = max(b[1] + b[3] for b in blaetter) + rand
    neu_vb = (vb[0] + bx0 * s, vb[1] + by0 * s, (bx1 - bx0) * s, (by1 - by0) * s)
    root.set("viewBox", " ".join(f"{v:.3f}" for v in neu_vb))
    root.set("width", f"{bx1 - bx0:.1f}")
    root.set("height", f"{by1 - by0:.1f}")
    for k in list(root):
        if _lokal(k.tag) == "namedview":
            root.remove(k)
    baum.write(ziel, encoding="utf-8", xml_declaration=True)
    return len(blaetter), (bx1 - bx0, by1 - by0)


def _vorfahren(el, eltern):
    out = []
    while el in eltern:
        el = eltern[el]
        out.append(el)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle")
    ap.add_argument("ziel", nargs="?")
    ap.add_argument("bereich", nargs="*", type=float, help="X0 Y0 X1 Y1 als Anteile der Seite")
    ap.add_argument("--rand", type=float, default=4.0, help="Rand in px")
    ap.add_argument("--ohne", default="", help="ids, die weggelassen werden (Komma-getrennt)")
    ap.add_argument("--vorschau", help="PNG mit Raster zum Ablesen des Bereichs")
    a = ap.parse_args()
    if a.vorschau:
        vorschau(a.quelle, a.vorschau)
    else:
        anzahl, groesse = ausschneiden(a.quelle, a.ziel, a.bereich, a.rand, set(filter(None, a.ohne.split(","))))
        print(f"{a.ziel}: {anzahl} Objekte, {groesse[0]:.0f} × {groesse[1]:.0f} px")

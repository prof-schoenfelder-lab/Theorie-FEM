"""Lernblätter: Bildausschnitte aus den Kursgrafiken erzeugen und die Typst-Quellen zu PDF setzen.

python werkzeuge/lernblaetter.py            alle Blätter
python werkzeuge/lernblaetter.py 03-inzidenzmatrix

Bilder: BILDER legt fest, welche Ebenen einer Kursgrafik in welchem Ausschnitt (viewBox) auf ein Blatt kommen.
Die Typst-Quellen liegen in lernblaetter/, die Vorlage in lernblaetter/lernblatt.typ.
"""
import re
import subprocess
import sys
from pathlib import Path

from ebenen_export import nur_ebenen

HIER = Path(__file__).resolve().parent
KURS = HIER.parent
QUELLE = KURS / "lernblaetter"
ZIEL = QUELLE / "bilder"

# Name: (Kursgrafik, Ebenen, viewBox)
BILDER = {
    "stab-system": ("grafiken/stab/system.svg",
                    ["stab", "elemente", "sysdof", "einzeln", "verbindung"], "75 40 735 430"),
    "stab-zusammenbau": ("grafiken/stab/zusammenbau.svg",
                         ["raster", "block1", "block2", "block3", "nullen"], "155 150 440 260"),
    "stab-netz": ("grafiken/stab/system.svg", ["stab", "last2", "elemente", "sysdof"], "75 40 735 175"),
    "element": ("grafiken/stab/element.svg", ["element", "dof", "kraefte"], "130 30 600 150"),
    "element-ansatz": ("grafiken/stab/element.svg", ["ansatz_achsen", "ansatz"], "0 220 400 290"),
    "element-formfkt": ("grafiken/stab/element.svg", ["form_achsen", "formfkt"], "440 220 330 290"),
    "stab-ergebnis": ("grafiken/stab/ergebnis.svg", ["achsen", "exakt", "fem_u", "fem_s"], "20 40 840 340"),
    "stab-ablauf": ("grafiken/stab/zusammenfassung.svg", ["pre", "solution", "post"], "10 20 800 440"),
    # V0
    "federsystem": ("grafiken/einfuehrung/federsystem.svg", ["system", "last", "dof", "dehnung"], "40 20 680 265"),
    "freischnitt": ("grafiken/einfuehrung/federsystem.svg", ["freischnitt"], "260 310 390 250"),
    # V1
    "feder": ("grafiken/energie/feder.svg", ["system", "kraft", "verschiebung", "haelfte"], "140 5 560 260"),
    "feder-minimum": ("grafiken/energie/feder.svg", ["achsen", "pi_i", "pi_a", "pi_ges", "minimum"], "100 290 540 390"),
    # V2
    "stabstueck": ("grafiken/ritz/stab-feder.svg", ["stab", "element", "kraftweg_n"], "40 30 660 320"),
    "stab-ersatzfeder": ("grafiken/ritz/stab-feder.svg", ["stab", "last", "verlauf", "feder"], "40 30 660 430"),
    "stabsystem": ("grafiken/ritz/stabsystem.svg", ["system", "last2", "dof", "federn"], "90 60 600 330"),
    "stabsystem-u": ("grafiken/ritz/stabsystem.svg", ["ergebnis"], "20 390 680 170"),
    "konisch": ("grafiken/ritz/konisch-ritz.svg", ["system"], "90 20 650 120"),
    "konisch-ritz": ("grafiken/ritz/konisch-ritz.svg", ["achsen", "exakt", "grad1", "grad2", "grad3"], "30 150 690 510"),
}


def bilder():
    ZIEL.mkdir(exist_ok=True)
    for name, (datei, ebenen, vb) in BILDER.items():
        svg = nur_ebenen((KURS / datei).read_text(encoding="utf-8"), ebenen)
        b, h = vb.split()[2:]
        svg = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
                     f'width="{b}" height="{h}" viewBox="{vb}"', svg, count=1)
        (ZIEL / f"{name}.svg").write_text(svg, encoding="utf-8")


def setzen(blatt):
    subprocess.run(["quarto", "typst", "compile", "--root", str(KURS), "--font-path", str(KURS / "assets/fonts"),
                    str(QUELLE / f"{blatt}.typ"), str(QUELLE / f"{blatt}.pdf")], check=True)


if __name__ == "__main__":
    bilder()
    blaetter = sys.argv[1:] or sorted(p.stem for p in QUELLE.glob("[0-9]*.typ"))
    for b in blaetter:
        setzen(b)
        print("gesetzt:", b)

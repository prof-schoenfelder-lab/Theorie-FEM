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
    "matrix-schreibweise": ("grafiken/stab/matrizen.svg", ["schreibweise"], "80 70 430 275"),
    "matrix-produkt": ("grafiken/stab/matrizen.svg", ["multiplikation"], "20 310 640 350"),
    "matrix-vektoren": ("grafiken/stab/matrizen.svg", ["vektoren"], "20 10 520 630"),
    # V0
    "federsystem": ("grafiken/einfuehrung/federsystem.svg", ["system", "last", "dof", "dehnung"], "40 20 680 265"),
    "freischnitt": ("grafiken/einfuehrung/federsystem.svg", ["freischnitt"], "260 310 390 250"),
    # V1
    "feder": ("grafiken/energie/feder.svg", ["system", "kraft", "verschiebung", "haelfte"], "140 5 560 260"),
    "feder-minimum": ("grafiken/energie/feder.svg", ["achsen", "pi_i", "pi_a", "pi_ges", "minimum"], "100 290 540 402"),
    # V2
    "stabstueck": ("grafiken/ritz/stab-feder.svg", ["stab", "element", "kraftweg_n"], "40 30 660 332"),
    "stab-ersatzfeder": ("grafiken/ritz/stab-feder.svg", ["stab", "last", "verlauf", "feder"], "40 30 660 430"),
    "stabsystem": ("grafiken/ritz/stabsystem.svg", ["system", "last2", "dof", "federn"], "90 60 600 330"),
    "stabsystem-u": ("grafiken/ritz/stabsystem.svg", ["ergebnis"], "20 390 680 170"),
    "konisch": ("grafiken/ritz/konisch-ritz.svg", ["system"], "90 20 650 120"),
    "konisch-ritz": ("grafiken/ritz/konisch-ritz.svg", ["achsen", "exakt", "grad1", "grad2", "grad3"], "10 150 710 510"),
}


def bilder():
    ZIEL.mkdir(exist_ok=True)
    for name, (datei, ebenen, vb) in BILDER.items():
        svg = nur_ebenen((KURS / datei).read_text(encoding="utf-8"), ebenen)
        b, h = vb.split()[2:]
        svg = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
                     f'width="{b}" height="{h}" viewBox="{vb}"', svg, count=1)
        (ZIEL / f"{name}.svg").write_text(griechisch(svg), encoding="utf-8")


# Latin Modern Roman hat keine griechischen Buchstaben. Der Browser holt sie einzeln aus einer Ersatzschrift und
# neigt sie trotzdem; Typst setzt dann die ganze Zeile in der Ersatzschrift, aufrecht und ohne Fettdruck.
# Darum hier: Latin Modern Math als Ersatzschrift nennen und griechische Buchstaben je nach Schriftschnitt durch
# die mathematischen Zeichen ersetzen (kursiv 𝜀, fett 𝚲, fett kursiv 𝜺), die Latin Modern Math enthält.
_GR_KLEIN = range(0x3B1, 0x3CA)            # α … ω
_GR_GROSS = range(0x391, 0x3AA)            # Α … Ω
_MATHE = {                                  # (kursiv, fett): (Anfang Großbuchstaben, Anfang Kleinbuchstaben)
    (True, False): (0x1D6E2, 0x1D6FC),
    (False, True): (0x1D6A8, 0x1D6C2),
    (True, True): (0x1D71C, 0x1D736),
}


# Lateinische Buchstaben: Typst setzt eine Zeile mit einem fehlenden Zeichen ganz in der Ersatzschrift; dort gibt
# es keinen kursiven oder fetten Schnitt. In solchen Zeilen werden deshalb auch A–Z, a–z umgesetzt.
_LATEIN = {(True, False): (0x1D434, 0x1D44E), (False, True): (0x1D400, 0x1D41A), (True, True): (0x1D468, 0x1D482)}


def _zeichen(c, kursiv, fett):
    o = ord(c)
    if (kursiv, fett) not in _MATHE:
        return c
    gross, klein = _MATHE[(kursiv, fett)]
    if o in _GR_KLEIN:
        return chr(klein + o - 0x3B1)
    if o in _GR_GROSS and not kursiv:      # große griechische Buchstaben bleiben aufrecht (wie LaTeX)
        return chr(gross + o - 0x391)
    lg, lk = _LATEIN[(kursiv, fett)]
    if c == "h" and (kursiv, fett) == (True, False):
        return "ℎ"                    # ℎ: im Block der kursiven Buchstaben ausgespart
    if "A" <= c <= "Z":
        return chr(lg + o - 0x41)
    if "a" <= c <= "z":
        return chr(lk + o - 0x61)
    return c


def _braucht_ersatz(text):
    """Zeichen, die Latin Modern Roman nicht hat: griechische Buchstaben, Strich ′, Pfeile, Summen- und
    Vergleichszeichen."""
    return any(0x370 <= ord(c) <= 0x3FF or c in "′″∑Σ⇒⇔→←↑↓∞∂∫≈≠≤≥⋅" for c in text)


def _text_umsetzen(m):
    """Ein <text>-Element: Zustand (kursiv, fett) über die verschachtelten Tags verfolgen, Textknoten umsetzen."""
    teile = re.split(r"(<[^>]+>)", m.group(0))
    if not _braucht_ersatz("".join(t for t in teile if not t.startswith("<"))):
        return m.group(0)
    stapel, aus = [], []
    for t in teile:
        if t.startswith("</"):
            if stapel:
                stapel.pop()
        elif t.startswith("<"):
            alt = stapel[-1] if stapel else (False, False)
            stil = re.search(r'font-style="([^"]+)"', t)
            gew = re.search(r'font-weight="([^"]+)"', t)
            neu = (stil.group(1) == "italic" if stil else alt[0], gew.group(1) == "bold" if gew else alt[1])
            if not t.endswith("/>"):
                stapel.append(neu)
            if t.startswith("<text"):
                t = t.replace(",serif\"", ",'Latin Modern Math',serif\"")
        else:
            k, fe = stapel[-1] if stapel else (False, False)
            t = "".join(_zeichen(c, k, fe) for c in t)
        aus.append(t)
    return "".join(aus)


def griechisch(svg):
    return re.sub(r"<text\b.*?</text>", _text_umsetzen, svg, flags=re.S)


def setzen(blatt):
    subprocess.run(["quarto", "typst", "compile", "--root", str(KURS), "--font-path", str(KURS / "assets/fonts"),
                    str(QUELLE / f"{blatt}.typ"), str(QUELLE / f"{blatt}.pdf")], check=True)


if __name__ == "__main__":
    bilder()
    blaetter = sys.argv[1:] or sorted(p.stem for p in QUELLE.glob("[0-9]*.typ"))
    for b in blaetter:
        setzen(b)
        print("gesetzt:", b)

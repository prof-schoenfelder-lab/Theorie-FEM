"""Nur für die Veröffentlichung (GitHub Actions, vor `quarto render`):
entfernt die in entwuerfe.txt genannten Dateien samt Menüeinträgen und ersetzt Links darauf.
Lokal wird das Skript nicht ausgeführt, dort bleiben die Entwürfe sichtbar.

- Seiten (.qmd): Datei und Menüeintrag entfernen; Links → nur der Linktext (ohne Verweis)
- Beispiele (beispiele/<name>.py): Datei und Menüeintrag entfernen, Links in der Übersicht → „folgt“
- Mathematica-Aufgaben (.nb): Datei entfernen, Download in der Übersicht → „folgt“, Aufgabenkasten entfernen
"""
import os
import re
from pathlib import Path

projekt = Path(__file__).resolve().parent.parent
liste = projekt / "entwuerfe.txt"
entwuerfe = [z.strip() for z in liste.read_text(encoding="utf-8").splitlines()
             if z.strip() and not z.startswith("#")] if liste.exists() else []

seiten = [projekt / "index.qmd", projekt / "spickzettel.qmd", *sorted((projekt / "vorlesung").glob("*.qmd"))]


def ziel_im_netz(pfad):
    """Pfad, unter dem die Datei auf der Seite verlinkt ist."""
    p = Path(pfad)
    if p.parts[0] == "beispiele" and p.suffix == ".py":
        return f"beispiele/{p.stem}/index.html"
    return pfad


for pfad in entwuerfe:
    (projekt / pfad).unlink(missing_ok=True)
    print("Entwurf ausgeblendet:", pfad)
    href = ziel_im_netz(pfad)

    # Menüeintrag (href-Zeile und folgende text-Zeile) aus _quarto.yml entfernen
    q = projekt / "_quarto.yml"
    t = q.read_text(encoding="utf-8")
    t = re.sub(r"\n[ \t]*- href: " + re.escape(href) + r"\n[ \t]*text:[^\n]*", "", t)
    q.write_text(t, encoding="utf-8")

    # Links ersetzen (Pfad relativ zur jeweiligen Seite), inkl. Attributen wie {download="…"}
    for seite in seiten:
        if not seite.exists():
            continue
        t = seite.read_text(encoding="utf-8")
        rel = os.path.relpath(projekt / href, seite.parent)          # z. B. "03-stab.qmd" oder "../beispiele/…"
        muster = r"\[(\*\*)?([^\]]*?)(\*\*)?\]\(" + re.escape(rel) + r"\)(\{[^}]*\})?"
        if href.endswith(".nb") and seite.name != "index.qmd":
            # Download-Kasten der ausgeblendeten Aufgabe ganz entfernen
            t = re.sub(r"\n::: \{\.aufgabe\}\n(?:(?!\n:::\n).)*?" + re.escape(Path(href).name)
                       + r"(?:(?!\n:::\n).)*?\n:::\n", "\n", t, flags=re.S)
        if seite.name == "index.qmd" and not href.endswith(".qmd"):
            t = re.sub(muster, "*folgt*", t)
        else:
            t = re.sub(muster, lambda m: (m.group(1) or "") + m.group(2) + (m.group(3) or ""), t)
        seite.write_text(t, encoding="utf-8")

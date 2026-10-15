"""Exportiert ausgewählte Ebenen einer TM-Grafik als SVG/PNG/PDF.

python werkzeuge/ebenen_export.py grafik.svg ziel.png traeger lasten lager
(ohne Ebenen-Angabe: alle Ebenen). PNG/PDF über rsvg-convert.
"""
import re
import subprocess
import sys
from pathlib import Path


def nur_ebenen(svg: str, ebenen: list[str]) -> str:
    if not ebenen:
        return svg

    def ersetze(m):
        id_ = m.group(1)
        return m.group(0) if id_ in ebenen else m.group(0).replace("<g ", '<g style="display:none" ', 1)
    return re.sub(r'<g inkscape:groupmode="layer" id="([^"]+)"[^>]*>', ersetze, svg)


if __name__ == "__main__":
    quelle, ziel, *ebenen = sys.argv[1:]
    svg = nur_ebenen(Path(quelle).read_text(encoding="utf-8"), ebenen)
    ziel = Path(ziel)
    if ziel.suffix == ".svg":
        ziel.write_text(svg, encoding="utf-8")
    else:
        fmt = ziel.suffix[1:]
        subprocess.run(["rsvg-convert", "-f", fmt, "-z", "2" if fmt == "png" else "1", "-b", "white",
                        "-o", str(ziel)], input=svg.encode(), check=True)

#!/bin/bash
# Baut die Kursseite.
#   ./bauen.sh            alles bauen
#   ./bauen.sh vorschau   bauen und lokalen Server auf http://localhost:8768 starten
set -euo pipefail
cd "$(dirname "$0")"
# Python-Umgebung für marimo (wird mit dem TM-Kurs geteilt); einmalig anlegen
VENV="${HOME}/Library/Caches/tm-kurs-venv"
if [ ! -x "$VENV/bin/marimo" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q marimo numpy matplotlib uv
fi
ln -sfn "$VENV" .venv
quarto render
echo "Fertig: $(pwd)/_site"
if [ "${1:-}" = "vorschau" ]; then
  python3 -m http.server 8768 --directory _site
fi

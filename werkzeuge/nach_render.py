"""Wird von Quarto nach dem Rendern ausgeführt: exportiert die marimo-Beispiele
als WebAssembly-Seiten nach _site/beispiele/<name>/ (laufen ohne Server-Python im Browser)."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import offline

projekt = Path(__file__).resolve().parent.parent
venv_bin = projekt / ".venv" / "bin"
marimo = venv_bin / "marimo" if (venv_bin / "marimo").exists() else shutil.which("marimo")
env = dict(os.environ, PATH=f"{venv_bin}:{os.environ.get('PATH', '')}")

if not marimo:
    print("marimo nicht gefunden – Beispiele werden nicht exportiert")
else:
    for nb in sorted((projekt / "beispiele").glob("*.py")):
        ziel = projekt / "_site" / "beispiele" / nb.stem
        if not os.environ.get("QUARTO_PROJECT_RENDER_ALL") and (ziel / "index.html").exists():
            continue
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([str(marimo), "export", "html-wasm", str(nb), "-o", tmp,
                            "--mode", "run", "--no-show-code", "-f"], check=True, env=env,
                           stdout=subprocess.DEVNULL)
            ziel.mkdir(parents=True, exist_ok=True)
            subprocess.run(["rsync", "-a", "--delete", f"{tmp}/", f"{ziel}/"], check=True)
        print(f"marimo-Beispiel exportiert: {ziel.relative_to(projekt)}")

# Offline-Fassung (Service Worker, Manifest) – zuletzt, damit alle Dateien feststehen
offline.erzeugen(projekt / "_site")

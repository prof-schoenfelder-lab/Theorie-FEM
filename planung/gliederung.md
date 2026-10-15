# Theorie der FEM – Gliederung und Quellen

Struktur nach `../Übersicht-Theorie-FEM.pdf`. Rechensoftware in Übung/Praktikum: **Mathematica**
(task/solved-Notebooks). marimo-Notebooks nur in der Vorlesung, um Parametereinflüsse greifbar zu machen.

| Nr. | Vorlesung | Quellen | Stand |
|:-:|:--|:--|:--|
| 0 | Einführung in Mathematica an TM-Aufgaben; Federaufgabe (ohne Energie) als K p = q | `0-Mathematica`, `2-FEM-Federn/0-Matrizenrechnung*`, `1-Federbeispiel-Vorlesung-FEM` (3 Federn), `mathematica-lösungsmuster.nb` / `2-Federn-3DOF-*` (Übung) | Entwurf 2026-10-15 |
| 1 | Energieprinzipien, Minimum der potentiellen Energie | `1-Energieprinzipien` | offen |
| 2 | Rayleigh-Ritz | `1-Energieprinzipien/Ritzsches-Verfahren` | offen |
| 3 | Normalkraftstab: von Ritz zur FEM | `3-FEM-Stab/1-*`, `2-Ablauf-FEM.pdf`, `1-konischer-Stab-Ritz+FE.nb`, `3-Stab-konisch-FEM-*.nb` | Pilot 2026-10-15 |
| 4 | Stab: quadratisches Element, innere Lasten (Eigengewicht) | `3-FEM-Stab/4-*`, `5-*` | offen |
| 5 | Fachwerkstab 2D | `3-FEM-Stab/6-*` | offen |
| 6 | Balkenelement | `5-FEM-Balken` | offen |
| 7 | Rahmenelement | `6-Rahmenelement` | offen |
| 8 | 2D-Rechteckelement | `4-FEM-2D`, `Vorlesung/6-*` | offen |
| – | Abschluss, Probeklausur | `6-Abschlussübungen` | offen |

Entscheidungen 2026-10-15:
- Fahrrad-Vorbau-Beispiel entfällt in der Einführung.
- FEM an Federsystemen (früher eigene Einheit) entfällt; FEM-Prinzipien direkt am Normalkraftstab (nach Ritz).
- Notation wie Tafelbilder: Element-DOF p₂ᵉ links, p₁ᵉ rechts; Nᵉ = (xᵉ/Lᵉ, 1 − xᵉ/Lᵉ); Λᵉ, K_sys, p_sys, q_sys.

Werkzeuge:
- Grafiken: `werkzeuge/grafiken_<thema>.py` (Ebenen = Scroll-Schritte), werden vor jedem Rendern neu erzeugt.
- Mathematica-Übungen: `werkzeuge/mathematica_<thema>.wl` erzeugt task- und solved-Notebook aus einer Quelle;
  `echo 'pruefen = True; Get["werkzeuge/mathematica_stab.wl"]' | /Applications/Mathematica.app/Contents/MacOS/WolframKernel -noprompt`
  führt den Lösungscode zur Kontrolle aus. Nur `*-task.nb` wird veröffentlicht.

Ergänzung 2026-10-15 (Vorlesung 0):
- Beispiele in der Vorlesung: Kurvendiskussion → TM-Aufgabe 7.1 (Schnittgrößen, `0-Mathematica/2-Grundkenntnisse`) →
  Stab unter Eigengewicht a/b/c (`3-Infinitesimalrechnung/DGL-Stab-Eigengewicht`) → Federsystem K p = q.
- Übungen (je eine Datei, `werkzeuge/mathematica_uebungen0.wl`): `00-schnittgroessen-7-3`, `00-dgl-stab-konisch`;
  dazu `00-einfuehrung` (Kurvendiskussion + Federsystem 3 DOF).
- Startseite: eigene Kursübersicht `grafiken/uebersicht/kursweg.svg` (werkzeuge/grafiken_uebersicht.py), Tabelle mit Notebooks/Übungen.
- Spickzettel `spickzettel.qmd`: Auswertung aller 188 .nb (186 lesbar; `2-FEM-Federn/1-Federbeispiel-Vorlesung-FEM.nb` ist eine PostScript-Datei).

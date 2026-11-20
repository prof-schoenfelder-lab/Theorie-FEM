#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Der Ablauf der FEM],
  vorlesung: [Vorlesung 3 · Normalkraftstab],
)

*Worum geht es?* Jede FEM-Rechnung läuft in drei Phasen: Modell aufbauen, Gleichungssystem lösen, Ergebnisse
auswerten. Hier am konischen Stab mit drei linearen Elementen.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ Ks ps = qs $,
    $ sigma^e = E^e vN^(e prime) Lam^e ps $)
]

#(bild("bilder/stab-ablauf.svg", breite: 82%))

#schritt(1, [Preprocessor: Modell aufbauen], verhaeltnis: (1.2fr, 1fr),
  bild("bilder/stab-netz.svg", breite: 100%),
  [
    Elementtyp wählen (linearer Stab: $mK^e$, $vN^e$), vernetzen (3 Elemente), Material und Geometrie zuweisen:
    $A^((1)) = "86,7"$, $A^((2)) = 60$, $A^((3)) = "33,3" "mm"^2$. Die Inzidenzmatrizen $Lam^e$ entstehen dabei.
  ])

#schritt(2, [Solution: zusammenbauen, Lager einarbeiten, lösen],
  [
    $Ks = sum_e Lam^(e #T) mK^e Lam^e$. Das Lager hält $p_1 = 0$; die erste Gleichung enthält die unbekannte
    Lagerkraft $q_1$. Erste Zeile und Spalte streichen:
    $ mat("30 800", -"12 600", 0; -"12 600", "19 600", -7000; 0, -7000, 7000) mat(p_2; p_3; p_4) = mat(0; 0; 5000) $
  ],
  [
    Einträge in N/mm, Kräfte in N. Lösung:
    $ p_2 = "0,275", quad p_3 = "0,672", quad p_4 = "1,386" "mm" $
    Die gestrichene Gleichung liefert die Lagerkraft:
    $ q_1 = -c^((1)) p_2 = -5000 "N" $
  ])

#schritt(3, [Postprocessor: Verschiebungen, Dehnungen, Spannungen], verhaeltnis: (1.3fr, 1fr),
  bild("bilder/stab-ergebnis.svg", breite: 100%),
  [
    $ u^e &= vN^e Lam^e ps \
      epsilon^e &= vN^(e prime) Lam^e ps, quad sigma^e = E^e epsilon^e $
    $u$: am Ende −3,6 %. $sigma$: je Element konstant, $150$ statt $250$ MPa.
  ])

#v(1fr)
#merke[
  *Merke*
  - Ein Lager ist ein Freiheitsgrad mit vorgegebener Verschiebung.
  - Lagerkräfte folgen aus den gestrichenen Gleichungen.
  - Verschiebungen sind gut, Spannungen (Ableitungen) ungenauer.
  - Ritz: ein Ansatz für alles. FEM: einfacher Ansatz je Element, mehr Elemente = genauer.
]

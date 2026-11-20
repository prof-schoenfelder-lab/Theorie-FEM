#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Matrizenrechnung für die FEM],
  vorlesung: [Vorlesung 3 · Normalkraftstab],
)

#let mA = $bold(upright(A))$
#let mB = $bold(upright(B))$
#let vx = $bold(upright(x))$
#let vy = $bold(upright(y))$
#let va = $bold(upright(a))$

*Worum geht es?* Für die FEM braucht man nur wenige Regeln: Schreibweise, Addition, Produkt „Zeile mal Spalte“,
Transponieren und die drei Arten, Vektoren zu multiplizieren.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ (mA mB)_(i j) = sum_k A_(i k) B_(k j) $,
    $ (mA mB)^#T = mB^#T mA^#T $)
]

#schritt(1, [Matrizen und Vektoren], verhaeltnis: (1fr, 1fr),
  bild("bilder/matrix-schreibweise.svg", breite: 56%),
  [
    $mA$ hat $m$ Zeilen und $n$ Spalten. Im Eintrag $A_(i j)$ nennt der *erste Index die Zeile*, der *zweite die
    Spalte*.

    Vektoren sind immer *Spaltenvektoren*. Ein *Zeilenvektor* ist ein transponierter Spaltenvektor, $va^#T$.
    Vektoren und Matrizen sind fett gesetzt.

    *Addition:* nur bei gleicher Größe, Eintrag für Eintrag: $(mA + mB)_(i j) = A_(i j) + B_(i j)$.
  ])

#schritt(2, [Multiplikation: Zeile mal Spalte], verhaeltnis: (1fr, 1fr),
  bild("bilder/matrix-produkt.svg", breite: 80%),
  [
    Eintrag $(mA mB)_(i j)$: Zeile $i$ von $mA$ mal Spalte $j$ von $mB$, Einträge paarweise multiplizieren und
    addieren.
    $ (mA mB)_(11) = A_(11) B_(11) + A_(12) B_(21) + A_(13) B_(31) $
    *Größen:* $mA$ braucht so viele Spalten wie $mB$ Zeilen,
    $ (m times n) dot (n times r) = (m times r) $
    *Reihenfolge zählt:* im Allgemeinen $mA mB != mB mA$.
  ])

#schritt(3, [Vektoren multiplizieren], verhaeltnis: (1fr, 1fr),
  bild("bilder/matrix-vektoren.svg", breite: 50%),
  [
    - Spaltenvektor mal Spaltenvektor: *geht nicht*.
    - Zeilenvektor mal Spaltenvektor, $vx^#T vy$: eine *Zahl* (Skalarprodukt).
    - Spaltenvektor mal Zeilenvektor, $vx vy^#T$: eine *Matrix* (dyadisches Produkt).
    - Matrix mal Spaltenvektor, $mA vx$: wieder ein *Spaltenvektor*. So sieht $mK vp = vq$ aus.
  ])

#schritt(4, [Transponieren und das Quadrat eines Produkts], verhaeltnis: (1fr, 1.2fr),
  [Beim Transponieren eines Produkts dreht sich die Reihenfolge um. Eine Zahl ändert sich dabei nicht,
   $s = vx^#T vy = s^#T = vy^#T vx$. Damit wird ein Quadrat zum Produkt mit Spaltenvektor mal Zeilenvektor
   in der Mitte; so entsteht $mK^e$ aus der Energie.],
  $ s^2 = s^#T s = vy^#T vx vx^#T vy = vy^#T (vx vx^#T) vy $)

#schritt(5, [In Mathematica], verhaeltnis: (1fr, 1fr),
  [
    #set text(size: 9pt)
    #table(columns: 2, align: left, inset: (x: 5pt, y: 3pt),
      [Matrix als Liste von Zeilen], raw("A = {{1, 2}, {3, 4}}"),
      [Eintrag Zeile 2, Spalte 1], raw("A[[2, 1]]"),
      [Matrixprodukt (Punkt!)], raw("A . B"),
      [Transponieren], raw("Transpose[A]"),
      [Anzeige als Matrix], raw("A // MatrixForm"))
  ],
  [
    #set text(size: 9pt)
    #table(columns: 2, align: left, inset: (x: 5pt, y: 3pt),
      [Skalarprodukt], raw("xv . yv"),
      [Spaltenvektor · Zeilenvektor], raw("Transpose[{xv}] . {yv}"),
      [Matrix mal Vektor], raw("A . xv"),
      [Gleichungssystem lösen], raw("LinearSolve[K, q]"))
  ])

#v(1fr)
#merke[
  *Merke*
  - Vor dem Multiplizieren die Größen prüfen: innen gleich, außen bleibt übrig.
  - Die Reihenfolge zählt; beim Transponieren eines Produkts dreht sie sich um.
  - Zeile mal Spalte gibt eine Zahl, Spalte mal Zeile eine Matrix.
  - In Mathematica ist der Punkt das Matrixprodukt; `A B` mit Leerzeichen multipliziert nur Eintrag für Eintrag.
]

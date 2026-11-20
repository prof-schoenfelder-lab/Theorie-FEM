#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Inzidenzmatrix und Zusammenbau],
  vorlesung: [Vorlesung 3 · Normalkraftstab],
)

*Worum geht es?* Die Inzidenzmatrix $Lam^e$ sagt, welcher Elementfreiheitsgrad zu welchem
Systemfreiheitsgrad gehört. Damit setzt man die Elementmatrizen zur Systemsteifigkeitsmatrix $Ks$ zusammen.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ vp^e = Lam^e ps $,
    $ Ks = sum_(e=1)^n Lam^(e #T) mK^e Lam^e $)
]

#schritt(1, [System und Elemente], verhaeltnis: (1.6fr, 1fr),
  bild("bilder/stab-system.svg", breite: 100%),
  [
    *Systemfreiheitsgrade*, frei nummeriert:
    $ ps = mat(p_1; p_2; p_3; p_4) $
    *Elementfreiheitsgrade*, fest: rechts 1, links 2:
    $ vp^e = mat(p_1^e; p_2^e) $
    Oben das Element, in Klammern seine Nummer: $p_1^((2))$ ist der rechte Knoten von Element 2.
  ])

#schritt(2, [Kinematik ablesen und als Tabelle schreiben],
  table(columns: 2, align: (center, left),
    table.header([*System*], [*Element*]),
    $p_1$, $p_2^((1))$,
    $p_2$, $p_1^((1)) = p_2^((2))$,
    $p_3$, $p_1^((2)) = p_2^((3))$,
    $p_4$, $p_1^((3))$),
  [
    Welcher Elementknoten liegt auf welchem Systemknoten? Für Element 1 als Tabelle, eine Zeile je
    Elementfreiheitsgrad, eine Spalte je Systemfreiheitsgrad, $1$ wo sie zusammengehören:
    #align(center, table(columns: 5, align: center,
      [], $p_1$, $p_2$, $p_3$, $p_4$,
      $p_1^((1))$, [0], [*1*], [0], [0],
      $p_2^((1))$, [*1*], [0], [0], [0]))
  ])

#block(breakable: false, above: 0.9em, below: 0.4em, {
  block(below: 0.45em, [#nr(3) #h(3pt) #text(weight: "semibold", size: 11pt, fill: blau)[Die Tabelle ist die Inzidenzmatrix]])
  $ mat(p_1^((1)); p_2^((1))) = underbrace(mat(0, 1, 0, 0; 1, 0, 0, 0), Lam^((1))) mat(p_1; p_2; p_3; p_4)
    = mat(p_2; p_1) wide
    Lam^((2)) = mat(0, 0, 1, 0; 0, 1, 0, 0), quad Lam^((3)) = mat(0, 0, 0, 1; 0, 0, 1, 0) $
})

#schritt(4, [Zusammenbau über die Energie],
  bild("bilder/stab-zusammenbau.svg", breite: 72%),
  [
    Jedes Element ist eine Feder, $mK^e = c^e mat(1, -1; -1, 1)$ mit $c^e = (E^e A^e)\/L^e$.
    Die Energien der Elemente addieren sich; mit $vp^e = Lam^e ps$:
    $ Pi_i = sum_(e=1)^n 1/2 vp^(e #T) mK^e vp^e = 1/2 ps^#T underbrace((sum_(e=1)^n Lam^(e #T) mK^e Lam^e), Ks) ps $
    $Lam^(e #T) mK^e Lam^e$ setzt $mK^e$ in die Zeilen und Spalten seiner Knoten. An gemeinsamen Knoten
    werden die Steifigkeiten *addiert*.
  ])

#schritt(5, [Systemgleichung], verhaeltnis: (1fr, 1fr),
  kasten[$ Ks ps = qs, quad qs = mat(q_1, 0, 0, F)^#T $],
  [Minimum von $Pi_(g e s) = 1/2 ps^#T Ks ps - ps^#T qs$. $q_1$ ist die unbekannte Lagerkraft; sie folgt
   nach dem Einbau der Randbedingung $p_1 = 0$.])

#v(1fr)
#merke[
  *Merke*
  - $Lam^e$: nur Nullen und Einsen, Konnektivität statt Mechanik.
  - Größe: Elementfreiheitsgrade $times$ Systemfreiheitsgrade.
  - $Ks$: symmetrisch, Bandstruktur, ohne Lager singulär.
  - Ein FEM-Programm addiert $mK^e$ direkt an die richtigen Stellen.
]

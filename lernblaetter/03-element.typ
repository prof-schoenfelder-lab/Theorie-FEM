#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Normalkraftstab als finites Element],
  vorlesung: [Vorlesung 3 · Normalkraftstab],
)

*Worum geht es?* Für *ein* Stabelement wird alles einmal hergeleitet: Ansatz, Ansatzfunktionen und
Elementsteifigkeitsmatrix. Danach müssen die Elemente nur noch verbunden werden.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1.3fr), align: center + horizon,
    $ u^e (x^e) = vN^e vp^e $,
    $ mK^e = integral_(L^e) vN^(e prime #T) E^e A^e vN^(e prime) dif x^e = (E^e A^e) / L^e mat(1, -1; -1, 1) $)
]

#schritt(1, [Element und Energie], verhaeltnis: (1.2fr, 1fr),
  bild("bilder/element.svg", breite: 100%),
  [
    Freiheitsgrade $p_1^e$ rechts, $p_2^e$ links; Knotenkräfte $q_1^e$, $q_2^e$.
    $ Pi_i^e &= 1/2 integral_(L^e) E^e A^e u^(e prime) (x^e)^2 dif x^e \
      Pi_a^e &= -p_1^e q_1^e - p_2^e q_2^e $
  ])

#schritt(2, [Linearer Ansatz in Knotenverschiebungen], verhaeltnis: (1fr, 1.3fr),
  bild("bilder/element-ansatz.svg", breite: 85%),
  [
    $ u^e (x^e) = a_1 x^e + a_2 $
    Die *Konstante gehört dazu*: Das Element kann sich als Ganzes verschieben. Mit $u^e (0) = p_2^e$ und
    $u^e (L^e) = p_1^e$:
    $ u^e (x^e) = (p_1^e - p_2^e) / L^e x^e + p_2^e $
  ])

#schritt(3, [Ansatzfunktionen], verhaeltnis: (1fr, 1.3fr),
  bild("bilder/element-formfkt.svg", breite: 70%),
  [
    Nach den Freiheitsgraden sortiert: Zeilenvektor mal Spaltenvektor,
    $ u^e = x^e / L^e p_1^e + (1 - x^e / L^e) p_2^e
      = underbrace(mat(x^e / L^e, 1 - x^e / L^e), vN^e) underbrace(mat(p_1^e; p_2^e), vp^e) $
    Jede Ansatzfunktion ist an ihrem Knoten $1$, am anderen $0$.
  ])

#schritt(4, [Energie in Matrixform: die Elementsteifigkeitsmatrix],
  [
    Mit $u^(e prime) = vN^(e prime) vp^e$ und $(vN^(e prime) vp^e)^2 = vp^(e #T) vN^(e prime #T) vN^(e prime) vp^e$:
    $ Pi_i^e = 1/2 vp^(e #T) underbrace((integral_(L^e) vN^(e prime #T) E^e A^e vN^(e prime) dif x^e), mK^e) vp^e $
    $vp^e$ hängt nicht von $x^e$ ab und kommt aus dem Integral, $vp^(e #T)$ nach vorn.
  ],
  [
    $vN^(e prime) = mat(1/L^e, -1/L^e)$ ist konstant:
    $ mK^e = E^e A^e integral_0^(L^e) mat(1/L^e; -1/L^e) mat(1/L^e, -1/L^e) dif x^e
      = (E^e A^e) / L^e mat(1, -1; -1, 1) $
  ])

#schritt(5, [Minimum: die Elementgleichung],
  kasten[$ (E^e A^e) / L^e mat(1, -1; -1, 1) mat(p_1^e; p_2^e) = mat(q_1^e; q_2^e)
    quad "kurz" quad mK^e vp^e = vq^e $],
  [Aus $Pi^e = 1/2 vp^(e #T) mK^e vp^e - vp^(e #T) vq^e$ und $partial Pi^e \/ partial vp^e = bold(upright(0))$.
   Das ist eine Feder mit $c^e = E^e A^e \/ L^e$.])

#v(1fr)
#merke[
  *Merke*
  - Die Koeffizienten des Ansatzes sind die Knotenverschiebungen.
  - Im linearen Element sind Dehnung und Spannung konstant.
  - Material ($E^e$) und Geometrie ($A^e$, $L^e$) stecken nur in $mK^e$.
  - $u^e = vN^e vp^e$ gilt für jeden Elementtyp, nur $vN^e$ ändert sich.
]

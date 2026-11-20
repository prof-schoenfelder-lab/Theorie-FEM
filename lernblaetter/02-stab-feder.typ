#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Der Stab ist eine Feder],
  vorlesung: [Vorlesung 2 · Rayleigh-Ritz],
)

*Worum geht es?* Die Formänderungsenergie eines Stabes folgt aus Spannung und Dehnung. Bei konstantem $E A$
verhält sich der Stab wie eine Feder mit $c = E A \/ L$. Stabsysteme lassen sich dann über die Energie rechnen.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ Pi_i = 1/2 integral_0^L E A u'(x)^2 dif x $,
    $ c = (E A) / L quad (E A = "konst.") $)
]

#schritt(1, [Ein Stabstück ist eine kleine Feder], verhaeltnis: (1.1fr, 1fr),
  bild("bilder/stabstueck.svg", breite: 92%),
  [
    Ein Stück $dif x$ wird von $N$ gezogen und verlängert sich um $dif u$:
    $ dif Pi_i = 1/2 N dif u = 1/2 sigma A dot epsilon dif x = 1/2 sigma epsilon dif V $
    Über die Länge, mit $sigma = E epsilon$, $epsilon = u'$, $dif V = A dif x$:
    $ Pi_i = 1/2 integral_V sigma epsilon dif V = 1/2 integral_0^L E A u'(x)^2 dif x $
  ])

#schritt(2, [Konstantes $E A$: die Ersatzfeder], verhaeltnis: (1.1fr, 1fr),
  bild("bilder/stab-ersatzfeder.svg", breite: 80%),
  [
    Ohne Streckenlast ist $u(x) = u(L) x\/L$ linear, $u' = u(L)\/L$:
    $ Pi_i = 1/2 (E A) / L u(L)^2 quad => quad c = (E A) / L $
    Mit $Pi_a = -F u(L)$ und $dif Pi_(g e s) \/ dif u(L) = 0$:
    $ u(L) = (F L) / (E A) $
    Halb so lang heißt doppelt so steif.
  ])

#schritt(3, [Stabsystem: jeder Stab eine Feder], verhaeltnis: (1.1fr, 1fr),
  bild("bilder/stabsystem.svg", breite: 92%),
  [
    Knoten an Material- und Querschnittswechseln und an Kräften. Verlängerung = rechtes minus linkes Ende:
    $ Delta u_1 = p_2, quad Delta u_2 = p_1 - p_2, quad Delta u_3 = -p_1 $
    $ c_j = (E_j A_j) / L_j $
  ])

#schritt(4, [Energie, Minimum und Auswertung],
  [
    $ Pi_i &= sum_(j=1)^3 1/2 c_j Delta u_j^2 \
      Pi_a &= -(-5F) p_1 - 2F p_2 $
    $5F$ zeigt gegen $p_1$, daher das Vorzeichen. Aus $partial Pi_(g e s) \/ partial p_1 = partial Pi_(g e s) \/ partial p_2 = 0$:
    $ p_1 = -"0,145" "mm", quad p_2 = -"0,133" "mm" $
  ],
  [
    $u(x)$ ist in jedem Stab linear. Je Stab:
    $ epsilon_j = (Delta u_j) / L_j, quad sigma_j = E_j epsilon_j, quad N_j = c_j Delta u_j $
    #table(columns: 4, align: center, inset: (x: 5pt, y: 3pt),
      [Stab], [1 (Al)], [2 (St)], [3 (Al)],
      [$sigma$ in MPa], [−116,0], [−75,8], [92,4])
  ])

#v(1fr)
#merke[
  *Merke*
  - $1/2 sigma epsilon$ ist die Formänderungsenergie je Volumen.
  - Stab mit konstantem $E A$ = Feder $c = E A \/ L$.
  - Zwischen den Knoten ist $u(x)$ linear: Mehr Knoten bringen nichts.
  - Das Gleichgewicht ist im Minimum automatisch erfüllt.
]

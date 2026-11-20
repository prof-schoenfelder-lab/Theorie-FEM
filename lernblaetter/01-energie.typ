#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Minimum der potentiellen Energie],
  vorlesung: [Vorlesung 1 · Energieprinzipien],
)

*Worum geht es?* Ein elastisches System stellt sich so ein, dass seine potentielle Energie minimal wird. Ohne
Freischnitt kommt man zum selben Gleichungssystem wie über das Gleichgewicht. Das ist die Grundlage der FEM.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ Pi_(g e s) = Pi_i + Pi_a $,
    $ (partial Pi_(g e s)) / (partial p_i) = 0 quad "für alle" i $)
]

#schritt(1, [Eine Feder: innere und äußere Energie], verhaeltnis: (1.2fr, 1fr),
  bild("bilder/feder.svg", breite: 100%),
  [
    *Innere* Energie: in der Feder gespeichert, Fläche unter $N = c s$ (Dreieck):
    $ Pi_i = integral_0^u c s dif s = 1/2 c u^2 $
    *Äußere* Energie: Potential der Last, Kraft mal Weg mit Minus:
    $ Pi_a = -F u $
    Kein $1/2$: Die Last ist *konstant* (ganzes Rechteck).
  ])

#schritt(2, [Das Minimum ist das Gleichgewicht], verhaeltnis: (1fr, 1fr),
  bild("bilder/feder-minimum.svg", breite: 78%),
  [
    $ Pi_(g e s)(u) = 1/2 c u^2 - F u $
    $ (dif Pi_(g e s)) / (dif u) = c u - F = 0 quad => quad F = c u $
    Das Federgesetz, also das Gleichgewicht. Im Minimum gilt $Pi_i = -1/2 Pi_a$.
  ])

#schritt(3, [Federsystem: Energie aller Federn und Kräfte], verhaeltnis: (1fr, 1.2fr),
  bild("bilder/federsystem.svg", breite: 90%),
  [
    Kinematik wie in Vorlesung 0: $u_1 = p_2$, $u_2 = p_1 - p_2$, $u_3 = p_1$.
    $ Pi_i &= 1/2 c_1 p_2^2 + 1/2 c_2 (p_1 - p_2)^2 + 1/2 c_3 p_1^2 \
      Pi_a &= -f_1 p_1 - f_2 p_2 $
    Jede Kraft mit „ihrem“ Freiheitsgrad. *Kein Freischnitt nötig.*
  ])

#schritt(4, [Ableitungen gleich null],
  [
    $ (partial Pi_(g e s)) / (partial p_1) &= (c_2 + c_3) p_1 - c_2 p_2 - f_1 = 0 \
      (partial Pi_(g e s)) / (partial p_2) &= -c_2 p_1 + (c_1 + c_2) p_2 - f_2 = 0 $
  ],
  [Genau die Gleichungen aus Vorlesung 0. Das Gleichgewicht ist im Minimum automatisch erfüllt;
   Lösung wieder $p_1 = F/k$, $p_2 = F/(2k)$.])

#schritt(5, [$mK$ ist die zweite Ableitung],
  [
    $ mK = (partial^2 Pi_(g e s)) / (partial vp^2) = mat(c_2 + c_3, -c_2; -c_2, c_1 + c_2) $
  ],
  [Ein zweites Mal abgeleitet entsteht direkt die Steifigkeitsmatrix. Ist $mK$ symmetrisch und das System
   ausreichend gelagert, ist der stationäre Punkt ein *Minimum*.])

#v(1fr)
#merke[
  *Merke*
  - $Pi_i$: Formänderungsenergie, nie negativ, quadratisch in der Verformung.
  - $Pi_a$: $-$Kraft mal Weg, ohne $1/2$, weil die Last konstant ist.
  - Minimum von $Pi_(g e s)$ $<=>$ stabiles Gleichgewicht.
  - So arbeitet die FEM: Energie je Element addieren, dann ableiten.
]

#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Federsystem: die Struktur $mK vp = vq$],
  vorlesung: [Vorlesung 0 · Einführung],
)

*Worum geht es?* Aus Gleichgewicht, Federgesetz und Kinematik entsteht für jedes lineare System dieselbe Form:
Steifigkeitsmatrix mal Freiheitsgrade gleich Lasten. Genau diese Gleichung löst später jedes FE-Programm.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ mK vp = vq $,
    [Gleichgewicht + Federgesetz $N = c u$ + Kinematik])
]

#schritt(1, [System und Freiheitsgrade], verhaeltnis: (1.5fr, 1fr),
  bild("bilder/federsystem.svg", breite: 100%),
  [
    Zwei starre Balken, drei Federn, Kräfte $f_1$, $f_2$. Jeder Balken bewegt sich nur waagerecht: zwei
    *Freiheitsgrade*
    $ vp = mat(p_1; p_2) $
    Die Wand ist ein Freiheitsgrad mit vorgegebener Verschiebung $0$.
  ])

#schritt(2, [Freischnitt und Gleichgewicht], verhaeltnis: (1fr, 1.3fr),
  bild("bilder/freischnitt.svg", breite: 85%),
  [
    Zugkräfte ziehen den Balken in Richtung Feder:
    $ "rechts:" & quad -N_2 - N_3 + f_1 = 0 \
      "Mitte:" & quad -N_1 + N_2 + f_2 = 0 $
    Zwei Gleichungen, fünf Unbekannte: *statisch unbestimmt*. Wir brauchen die Verformung.
  ])

#schritt(3, [Kinematik und Federgesetz],
  [
    *Kinematik:* Verlängerung = rechtes minus linkes Federende
    $ u_1 = p_2, quad u_2 = p_1 - p_2, quad u_3 = p_1 $
  ],
  [
    *Federgesetz:* linear, Zug positiv
    $ N_1 = c_1 u_1, quad N_2 = c_2 u_2, quad N_3 = c_3 u_3 $
  ])

#schritt(4, [Einsetzen und nach den Freiheitsgraden sortieren],
  [
    Kinematik ins Federgesetz, beides ins Gleichgewicht, nach $p_1$, $p_2$ sortieren:
    $ (c_2 + c_3) p_1 - c_2 p_2 &= f_1 \
      -c_2 p_1 + (c_1 + c_2) p_2 &= f_2 $
  ],
  [
    Die Koeffizienten bilden die Steifigkeitsmatrix:
    $ underbrace(mat(c_2 + c_3, -c_2; -c_2, c_1 + c_2), mK) underbrace(mat(p_1; p_2), vp)
      = underbrace(mat(f_1; f_2), vq) $
  ])

#schritt(5, [Lösung und Rückrechnung],
  [
    Mit $c_1 = 2k$, $c_2 = 4k$, $c_3 = k$, $f_1 = 3F$, $f_2 = -F$:
    $ k mat(5, -4; -4, 6) mat(p_1; p_2) = mat(3F; -F) $
  ],
  [
    $ p_1 = F/k, quad p_2 = F/(2k) $
    Rückwärts über Kinematik und Federgesetz:
    $N_1 = F$, $N_2 = 2F$, $N_3 = F$.
  ])

#v(1fr)
#merke[
  *Merke*
  - Spalte $j$ von $mK$: Kräfte, die $p_j = 1$ erzwingen, alle anderen festgehalten.
  - Diagonale: Summe der Federn am Freiheitsgrad, immer positiv.
  - Nebendiagonale: $-c$ der Feder zwischen zwei Freiheitsgraden.
  - $mK$ ist symmetrisch; ohne Wand singulär.
]

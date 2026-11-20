#import "lernblatt.typ": *

#show: lernblatt.with(
  titel: [Das Verfahren nach Rayleigh-Ritz],
  vorlesung: [Vorlesung 2 · Rayleigh-Ritz],
)

*Worum geht es?* Ändert sich $E A$ längs des Stabes, hängt die Energie von einer ganzen Funktion $u(x)$ ab. Ritz
setzt eine Funktion mit wenigen unbekannten Koeffizienten an und sucht deren Minimum.

#kasten(farbe: blau)[
  #grid(columns: (1fr, 1fr), align: center + horizon,
    $ u(x) approx tilde(u)(x) = sum_(i=1)^n a_i phi_i (x) $,
    $ (partial Pi) / (partial a_i) = 0 quad => quad mK va = vq $)
]

#schritt(1, [Die Energie hängt von einer Funktion ab], verhaeltnis: (1.2fr, 1fr),
  bild("bilder/konisch.svg", breite: 100%),
  [
    $A(x)$ ändert sich, $u(x)$ ist nicht linear:
    $ Pi[u] = 1/2 integral_0^L E A(x) u'(x)^2 dif x - F u(L) $
    Eine „Funktion einer Funktion“: ein *Funktional*.
  ])

#schritt(2, [Ansatz: aus der Funktion werden Zahlen],
  [
    Der Ansatz muss die *geometrische* Randbedingung $u(0) = 0$ erfüllen: Polynome *ohne Konstante*.
    $ tilde(u) = a_1 x quad "oder" quad tilde(u) = a_1 x + a_2 x^2 $
    Mit $a_1 x + a_2$ könnte sich der Stab verschieben, ohne sich zu dehnen: kein Minimum.
  ],
  [
    Linearer Ansatz eingesetzt, $tilde(u)' = a_1$:
    $ Pi(a_1) = 1/2 a_1^2 E L (A_0 + A_1)/2 - F a_1 L $
    $ (dif Pi) / (dif a_1) = 0 quad => quad a_1 = (2F) / (E (A_0 + A_1)) $
  ])

#schritt(3, [Mehr Ansatzfunktionen], verhaeltnis: (1.2fr, 1fr),
  bild("bilder/konisch-ritz.svg", breite: 100%),
  [
    #table(columns: 3, align: center, inset: (x: 5pt, y: 3pt),
      [Grad], [$u(L)$], [$sigma(L)$],
      [1], [−17,2 %], [−66,7 %],
      [2], [−2,7 %], [−34,8 %],
      [3], [−0,4 %], [−16,2 %],
      [4], [−0,1 %], [−7,1 %])
    *Verschiebungen sind gut, Spannungen schwierig:* Spannungen sind Ableitungen und konvergieren langsamer.
  ])

#schritt(4, [Allgemein: ein lineares Gleichungssystem],
  [
    $ mat(K_(11), dots.c, K_(1n); dots.v, dots.down, dots.v; K_(n 1), dots.c, K_(n n))
      mat(a_1; dots.v; a_n) = mat(q_1; dots.v; q_n) $
    kurz $mK va = vq$, mit $va$, $vq$ als Spaltenvektoren.
  ],
  [
    Für den Stab mit Kraft $F$ am Ende:
    $ K_(i j) = integral_0^L E A phi_i' phi_j' dif x, quad q_i = F phi_i (L) $
    Dieselbe Struktur wie beim Federsystem; die Unbekannten sind Koeffizienten.
  ])

#v(1fr)
#merke[
  *Merke*
  - *Ein* Ansatz für das ganze Bauteil, erfüllt die geometrischen Randbedingungen.
  - Kraftrandbedingungen stecken in $Pi_a$, der Ansatz muss sie nicht erfüllen.
  - Mehr Ansatzfunktionen machen die Lösung nie schlechter; $Pi$ sinkt von oben auf das Minimum.
  - Ohne exakte Lösung: Grad erhöhen, bis sich das Ergebnis nicht mehr ändert.
]

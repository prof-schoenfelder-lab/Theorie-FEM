// Vorlage für die Lernblätter. Standard: A4 hoch, Kernformeln oben, nummerierte Schritte (Bild | Rechnung),
// unten Merke über die ganze Breite (Entscheidung 20.11.2026). Querformat/Spalten nur für Ausnahmen.
// Farben wie in den Kursgrafiken (Gestaltung und Konventionen: Farben).

#let gruen = rgb("#006414")     // Freiheitsgrade, Koordinaten
#let rot = rgb("#c00000")       // Hervorhebung, Elementmatrizen im Zusammenbau
#let blau = rgb("#0050b4")      // Kursfarbe
#let grau = rgb("#555555")

#let kasten(body, farbe: gruen) = block(
  width: 100%, inset: (x: 7pt, y: 6pt), radius: 3pt,
  fill: farbe.lighten(90%), stroke: (left: 2.5pt + farbe), body)

#let merke(body) = kasten(farbe: blau, body)

#let ueberschrift(text) = block(above: 0.9em, below: 0.45em,
  std.text(weight: "semibold", size: 11.5pt, fill: blau, text))

#let lernblatt(titel: "", vorlesung: "", quer: false, spalten: 1, body) = {
  set page(paper: "a4", flipped: quer, margin: (x: 12mm, top: 10mm, bottom: 10mm),
    footer: context [
      #set text(size: 7.5pt, fill: grau)
      Theorie der Finite-Elemente-Methode · #vorlesung · Prof. Dr.-Ing. Stephan Schönfelder
    ])
  set text(font: "Source Sans Pro", size: if quer { 10pt } else { 9.5pt }, lang: "de")
  show math.equation: set text(font: "Latin Modern Math")
  set par(leading: 0.55em, spacing: 0.75em, justify: false)
  set table(stroke: 0.5pt + luma(180), inset: (x: 6pt, y: 5pt))

  grid(columns: (1fr, auto), align: (left + horizon, right + horizon), column-gutter: 10mm,
    text(size: if quer { 22pt } else { 19pt }, weight: "light", titel),
    image("/assets/logos/htwk-schwarz.svg", height: 8.5mm))
  v(-1mm)
  line(length: 100%, stroke: 0.6pt + luma(170))
  v(1mm)
  if spalten > 1 { columns(spalten, gutter: 7mm, body) } else { body }
}

// Bild aus bilder/, mittig in seiner Spalte
#let bild(pfad, breite: 100%) = align(center, image(pfad, width: breite))

// Nummer eines Schritts im Kreis
#let nr(n) = box(baseline: 20%, circle(radius: 7pt, fill: blau, stroke: none,
  align(center + horizon, std.text(fill: white, weight: "bold", size: 9pt, str(n)))))

// Schritt: Nummer und Titel, darunter links Bild/Tabelle, rechts Rechnung
#let schritt(n, titel, links, rechts, verhaeltnis: (1fr, 1fr)) = block(breakable: false, above: 0.9em, below: 0.4em, {
  block(below: 0.45em, [#nr(n) #h(3pt) #std.text(weight: "semibold", size: 11pt, fill: blau, titel)])
  grid(columns: verhaeltnis, column-gutter: 6mm, align: left + horizon, links, rechts)
})

// Schreibweise wie auf der Kursseite: Vektoren/Matrizen aufrecht fett, sys kursiv, T aufrecht
#let sys = $s y s$
#let vp = $bold(upright(p))$
#let vq = $bold(upright(q))$
#let va = $bold(upright(a))$
#let vN = $bold(upright(N))$
#let mK = $bold(upright(K))$
#let ps = $bold(upright(p))_sys$
#let qs = $bold(upright(q))_sys$
#let Ks = $bold(upright(K))_sys$
#let Lam = $bold(upright(Lambda))$
#let T = $upright(sans(T))$

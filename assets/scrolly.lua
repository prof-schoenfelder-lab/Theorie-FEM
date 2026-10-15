--[[
Scrollytelling für Quarto (nur HTML).

Syntax in .qmd:

  :::: {.scrolly svg="../grafiken/schnittgroessen/beispiel.svg"}
  ::: {.schritt zeige="traeger lasten" dimmen="bereiche" zoom="30 30 620 200"}
  Text zum Schritt …
  :::
  ::::

- svg:    Grafik mit Inkscape-Ebenen (id der Ebene = Name in zeige/dimmen)
- zeige:  sichtbare Ebenen
- dimmen: blass dargestellte Ebenen (Kontext)
- zoom:   Bildausschnitt als viewBox "x y breite höhe" (wird animiert)

In anderen Formaten (PDF) wird die Grafik mit allen Ebenen statisch eingefügt.
]]

local function lies(pfad)
  local f = io.open(pfad, "r")
  if not f then return nil end
  local inhalt = f:read("*a")
  f:close()
  return inhalt
end

-- ::: {.vertiefung titel="…"} … :::  →  aufklappbarer Erklärtext (HTML),
-- in PDF als normaler Absatz mit Überschrift
local function vertiefung(el)
  local titel = el.attributes["titel"] or "Ausführlicher"
  if quarto.doc.is_format("html") then
    local out = { pandoc.RawBlock("html", '<details class="vertiefung"><summary>' .. titel .. '</summary>') }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    table.insert(out, pandoc.RawBlock("html", "</details>"))
    return out
  end
  local out = { pandoc.Para({ pandoc.Strong({ pandoc.Str(titel) }) }) }
  for _, b in ipairs(el.content) do table.insert(out, b) end
  return out
end

function Div(el)
  if el.classes:includes("vertiefung") then return vertiefung(el) end
  if not el.classes:includes("scrolly") then return nil end
  local src = el.attributes["svg"]
  local basis = pandoc.path.directory(quarto.doc.input_file)
  local pfad = pandoc.path.join({ basis, src })

  if not quarto.doc.is_format("html") then
    local out = { pandoc.Para({ pandoc.Image({}, src) }) }
    for _, b in ipairs(el.content) do table.insert(out, b) end
    return out
  end

  local svg = lies(pfad)
  if not svg then
    quarto.log.error("scrolly: Grafik nicht gefunden: " .. pfad)
    return nil
  end
  svg = svg:gsub("^%s*<%?xml.-%?>%s*", "")

  local id = el.identifier ~= "" and (' id="' .. el.identifier .. '"') or ""
  local out = {
    pandoc.RawBlock("html",
      '<div class="scrolly"' .. id .. '><div class="scrolly-grafik"><div class="scrolly-sticky">'
      .. svg .. '<div class="scrolly-zaehler"></div></div></div><div class="scrolly-schritte">')
  }
  for _, b in ipairs(el.content) do table.insert(out, b) end
  table.insert(out, pandoc.RawBlock("html", "</div></div>"))
  return out
end

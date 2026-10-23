"""Offline-Fassung der Kursseite (Progressive Web App), aufgerufen von nach_render.py.

Erzeugt in _site/
  - sw.js                 Service Worker: speichert die freigegebenen Seiten samt Schriften, Logos, Skripten
                          und MathJax im Browser, damit sie ohne Internet laufen
  - manifest.webmanifest  damit sich die Seite als App installieren lässt („Zum Home-Bildschirm“)
und ergänzt im <head> jeder HTML-Seite den Verweis auf Manifest und App-Symbol.

Die Versionskennung im Service Worker ist ein Hash über alle gespeicherten Dateien. Ändert sich etwas,
ändert sich sw.js, der Browser lädt beim nächsten Online-Besuch die neue Fassung, und die Seite zeigt
„Neue Fassung – neu laden“ (assets/scrolly.html).

Die marimo-Beispiele (WebAssembly, je ca. 27 MB) werden nicht gespeichert; offline erscheint dort ein Hinweis.
Die Mathematica-Aufgaben (*-task.nb) werden mitgespeichert, damit der Download auch offline klappt; Musterlösungen
(*-solved.nb) stehen nie in _site und sind zusätzlich ausgeschlossen.
Übernommen aus dem TM-Kurs (Commit d2de810), angepasst an die Ordner des FEM-Kurses."""
import hashlib
import json
from pathlib import Path

# Offline verfügbar: Startseite, Spickzettel und alle Vorlesungen, die in _site stehen, dazu die Mathematica-Aufgaben.
# Entwürfe (entwuerfe.txt) fehlen beim Veröffentlichen in _site und sind damit automatisch ausgenommen.
SEITEN_MUSTER = ["index.html", "spickzettel.html", "vorlesung/*.html"]
DATEI_MUSTER = ["mathematica/*-task.nb"]
# Ordner, die vollständig gespeichert werden (Skripte, Stile, Schriften, Logos, App-Symbol, Kursübersicht)
ORDNER = ["site_libs", "assets", "grafiken"]
EINZELN = ["search.json", "manifest.webmanifest"]

MANIFEST = {
    "name": "Theorie der Finite-Elemente-Methode",
    "short_name": "Theorie FEM",
    "description": "Vorlesung Theorie der Finite-Elemente-Methode, HTWK Leipzig",
    "lang": "de",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#0050b4",
    "icons": [
        {"src": "assets/app/symbol-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "assets/app/symbol-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "assets/app/symbol-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

KOPF = ('<link rel="manifest" href="{o}manifest.webmanifest">'
        '<meta name="theme-color" content="#0050b4">'
        '<link rel="apple-touch-icon" href="{o}assets/app/symbol-180.png">'
        '<meta name="apple-mobile-web-app-title" content="Theorie FEM">')

SW = r"""// Service Worker der Kursseite – erzeugt von werkzeuge/offline.py, nicht von Hand ändern.
const VERSION = "__VERSION__";
const CACHE = "fem-" + VERSION;         // Seiten und Dateien dieser Fassung
const CDN_CACHE = "fem-cdn";            // MathJax (bleibt über Fassungen hinweg erhalten)
// Eigenes Präfix: Der TM-Kurs liegt auf derselben Adresse (gleicher Browser-Speicher) und nutzt „tm-“.
const DATEIEN = __DATEIEN__;
const SEITEN = new Set(__SEITEN__.map(p => new URL(p, self.registration.scope).href));
const MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@4/";

const html = (titel, text) => new Response(
  `<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
   <title>${titel}</title><body style="font-family:'Source Sans Pro',system-ui,sans-serif;margin:2rem;color:#333;line-height:1.5">
   <h2 style="color:#0050b4">${titel}</h2><p>${text}</p></body></html>`,
  { headers: { "Content-Type": "text/html; charset=utf-8" } });

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(DATEIEN);
    try { await (await caches.open(CDN_CACHE)).add(MATHJAX + "tex-chtml.js"); } catch (_) {}
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("fem-") && k !== CACHE && k !== CDN_CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {
  if (e.data === "aktualisieren") self.skipWaiting();
  // Beim ersten Besuch lädt MathJax, bevor der Service Worker die Seite übernimmt: nachträglich speichern
  if (e.data && e.data.typ === "nachladen") {
    e.waitUntil(caches.open(CDN_CACHE).then(c => Promise.all(
      e.data.urls.filter(u => u.startsWith(MATHJAX)).map(u => c.match(u).then(m => m || c.add(u).catch(() => {})))
    )));
  }
});

// Seiten: zuerst aus dem Netz (immer die aktuelle Fassung), ohne Netz aus dem Speicher
async function seite(req) {
  const c = await caches.open(CACHE);
  const url = new URL(req.url); url.hash = ""; url.search = "";
  if (url.pathname.endsWith("/")) url.pathname += "index.html";
  try {
    const antwort = await fetch(req);
    if (antwort.ok && SEITEN.has(url.href)) c.put(url.href, antwort.clone());
    return antwort;
  } catch (_) {
    return (await c.match(url.href)) || html("Offline nicht verfügbar",
      'Diese Seite ist ohne Internet noch nicht verfügbar. <a href="' + self.registration.scope + 'index.html">Zur Übersicht</a>');
  }
}

// Übrige Dateien: sofort aus dem Speicher, im Hintergrund auffrischen
async function datei(req, cacheName) {
  const c = await caches.open(cacheName);
  const gespeichert = await c.match(req, { ignoreSearch: true });
  const netz = fetch(req).then(a => { if (a.ok) c.put(req, a.clone()); return a; });
  if (gespeichert) { netz.catch(() => {}); return gespeichert; }
  return netz;
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.href.startsWith(MATHJAX)) { e.respondWith(datei(req, CDN_CACHE)); return; }
  if (url.origin !== location.origin) {
    // übrige externe Skripte (z. B. Polyfill) offline still auslassen
    if (req.destination === "script") e.respondWith(fetch(req).catch(() => new Response("", { headers: { "Content-Type": "text/javascript" } })));
    return;
  }
  if (!url.href.startsWith(self.registration.scope)) return;
  if (url.pathname.includes("/beispiele/")) {
    e.respondWith(fetch(req).catch(() => req.mode === "navigate"
      ? html("Nur mit Internet", "Die Beispiele rechnen mit Python im Browser und sind nur online verfügbar.")
      : Response.error()));
    return;
  }
  if (req.mode === "navigate") { e.respondWith(seite(req)); return; }
  e.respondWith(datei(req, CACHE));
});
"""


def erzeugen(site: Path):
    (site / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")

    # Kopf jeder HTML-Seite ergänzen (nicht in den Beispielen); Pfad relativ zur Seite
    for h in site.rglob("*.html"):
        rel = h.relative_to(site)
        if rel.parts[0] == "beispiele":
            continue
        text = h.read_text(encoding="utf-8")
        if 'rel="manifest"' in text or "</head>" not in text:
            continue
        o = "../" * (len(rel.parts) - 1)
        h.write_text(text.replace("</head>", KOPF.format(o=o) + "</head>", 1), encoding="utf-8")

    def suche(muster):
        return [str(p.relative_to(site)) for m in muster for p in sorted(site.glob(m)) if "-solved" not in p.name and "-loesungen" not in p.name]

    seiten = suche(SEITEN_MUSTER)
    dateien = seiten + suche(DATEI_MUSTER) + [e for e in EINZELN if (site / e).exists()]
    for d in ORDNER:
        dateien += sorted(str(p.relative_to(site)) for p in (site / d).rglob("*")
                          if p.is_file() and p.name != ".DS_Store")

    h = hashlib.sha256(SW.encode())
    for d in dateien:
        h.update(d.encode())
        h.update((site / d).read_bytes())
    version = h.hexdigest()[:12]

    sw = (SW.replace("__VERSION__", version)
            .replace("__DATEIEN__", json.dumps(dateien, ensure_ascii=False))
            .replace("__SEITEN__", json.dumps(seiten, ensure_ascii=False)))
    (site / "sw.js").write_text(sw, encoding="utf-8")
    groesse = sum((site / d).stat().st_size for d in dateien) / 1e6
    print(f"Offline-Fassung: {len(seiten)} Seiten, {len(dateien)} Dateien, {groesse:.1f} MB, Version {version}")


if __name__ == "__main__":
    erzeugen(Path(__file__).resolve().parent.parent / "_site")

# Frontend: Server-Seiten mit Jinja und Bootstrap

Date: 2026-10-12

## Status

Accepted

## Context

Die Aufgabenstellung verlangt ein einfaches Frontend. Niemand im Team hat
Erfahrung mit JavaScript-Frameworks.

## Options Considered

 * Jinja-Templates mit Bootstrap über CDN: Flask erzeugt fertiges HTML,
   kein Build-Schritt. Nachteil: jede Aktion lädt die Seite neu.
 * HTMX oder Alpine.js zusätzlich: flüssigere Bedienung, aber ein weiteres
   Konzept zum Lernen.
 * React oder Vue mit JSON-API: modern, aber zwei Projekte statt einem und
   ein Build-Schritt.

## Decision

Jinja-Templates mit Bootstrap 5 über das CDN jsDelivr.

## Reasons

Am wenigsten bewegliche Teile. Formulare funktionieren auch ohne JavaScript.
Bootstrap sorgt ohne eigenes Design für eine brauchbare Darstellung auf
Handy und Laptop.

## Consequences

Jede Prüfung passiert im Backend; die Prüfungen im Browser (`required`,
`min`) sind nur Komfort. Wer später flüssigere Bedienung will, kann HTMX
ergänzen, ohne das Backend umzubauen.

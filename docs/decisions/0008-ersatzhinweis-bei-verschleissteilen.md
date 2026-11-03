# Ersatzhinweis bei Verschleissteilen

Date: 2026-11-03

## Status

Accepted

## Context

Bremsbeläge haben ein Intervall von 2000 km. Wer nach Ablauf «Wartung
erledigt» klickt, setzt den Zähler zurück, und die Beläge laufen weitere
2000 km, obwohl sie eigentlich ersetzt werden müssten. Bei Kette und Reifen ist
es dasselbe. Das Intervall vermischt «prüfen/pflegen» und «ersetzen»
(Issue #5).

## Options Considered

 * A: Verschleissteile haben nur ein Ersatzintervall und bieten bei
   Fälligkeit direkt «Tauschen» an. Einfach, aber Pflegeaufgaben wie «Kette
   ölen» fallen weg.
 * B: Zwei Intervalle pro Komponente (Wartung und Ersatz). Am vollständigsten,
   aber mehr Felder, doppelte Fälligkeitsrechnung und zwei Status pro
   Komponente.
 * C: Bei der Wartung das Ergebnis «gewartet» oder «ersetzt» wählen. Löst das
   Problem nicht, weil niemand zur Wahl «ersetzt» gezwungen wird.
 * D: Nur ein freies Infofeld «Ersatzhinweis» pro Komponente. Das
   Wartungsformular zeigt den Text und bietet einen Link zum Tausch. Die
   Fälligkeitslogik bleibt unverändert.

## Decision

Wir wählen Variante D (eine einfache Form von A). Entschieden vom
Projektteam.

 * Jede Komponente hat ein optionales Textfeld `ersatzhinweis`, das
   beschreibt, wann ein Tausch nötig ist (z.B. «Belag unter 1 mm»).
 * Der Hinweis erscheint nur im Wartungsformular, mit einem Link
   «Stattdessen tauschen». Der Nutzer entscheidet selbst: warten oder tauschen.
 * Die Standardkomponenten Kette, Bremsbeläge und Reifen bekommen einen
   Hinweistext in `vorlagen.py`.
 * Der Button in der Übersicht heisst neu «Warten» statt «Gewartet», damit alle
   Aktionen (Warten, Tauschen, Ausbauen) im gleichen Verb stehen.
 * Das Akzeptanzkriterium «Statusanzeige unterscheidet Wartung fällig von
   Ersatz fällig» entfällt.

## Reasons

Die Lösung ist klein und leicht zu verstehen: ein Feld, eine Info-Box, ein
Link. Sie braucht weder neue Fälligkeitslogik noch einen zweiten Status. Der
Nutzer sieht im richtigen Moment, nämlich beim Klick auf «Warten», dass ein
Tausch nötig sein könnte, und behält die Kontrolle.

## Consequences

 * Die App erinnert nicht an den Ersatz. Wer die Wartung nicht öffnet, sieht
   den Hinweis nie, und die Übersicht zeigt weiterhin nur «fällig».
 * Der Hinweis ist freier Text und wird nicht geprüft.
 * Bestehende Komponenten haben keinen Hinweis. Er lässt sich über «Bearbeiten»
   ergänzen.
 * Bestehende Datenbanken bekommen die Spalte beim Start automatisch
   (`init_db`).
 * Wollen wir später Erinnerungen oder eine Statusunterscheidung, ist
   Variante B der nächste Schritt.

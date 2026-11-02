# Nur den letzten Schritt rückgängig machen

Date: 2026-11-02

## Status

Accepted

## Context

Eine erfasste Wartung, ein Tausch oder ein Ausbau liess sich nicht
korrigieren. Ein Fehlklick verfälschte dauerhaft den Wartungsstatus und den
Verlauf (Issue #4). Ein Tausch war zudem nur ein Ausbau plus ein Einbau: Die
Datenbank wusste nicht, welche neue Komponente welche alte ersetzt hat.

## Options Considered

 * Beliebige Einträge im Verlauf ändern oder löschen: am flexibelsten.
   Nachteil: Danach müssen `letzte_wartung_*`, Ein- und Ausbaudaten aller
   späteren Einträge neu berechnet und geprüft werden.
 * Nur den jeweils letzten Schritt rückgängig machen: die letzte Wartung
   einer Komponente, den letzten Tausch, einen Ausbau ohne Ersatz. Der
   vorherige Zustand ist eindeutig bekannt.
 * Für den Tausch: die alte Komponente über gleiche Kategorie, Datum und
   Kilometer erraten, oder die Verknüpfung in einer neuen Spalte speichern.

## Decision

Nur der letzte Schritt lässt sich rückgängig machen. Entschieden vom
Projektteam.

 * Wartung löschen: nur die zuletzt erfasste Wartung einer aktiven
   Komponente. Danach gelten die Werte der vorherigen Wartung, ohne Wartung
   die des Einbaus.
 * Tausch rückgängig: nur solange die neue Komponente keine Wartung hat.
   Sonst zuerst diese Wartungen löschen.
 * Ausbau rückgängig: nur für Komponenten, die ohne Ersatz ausgebaut wurden.
   Wurde eine Komponente getauscht, geht es über «Tausch rückgängig».
 * Beim Tausch speichert die neue Komponente die alte in `vorgaenger_id`.
 * Vor jedem Rückgängigmachen fragt der Browser mit `confirm()` nach.

## Reasons

So bleibt der Verlauf immer in sich stimmig, ohne Neuberechnungen. Der
häufigste Fall, ein Fehlklick gerade eben, ist damit abgedeckt. Die Spalte
`vorgaenger_id` ist zuverlässiger als ein Erraten über gleiche Werte.

## Consequences

 * Ältere Einträge mitten im Verlauf lassen sich nicht korrigieren. Man muss
   bis zu ihnen alle späteren Schritte rückgängig machen.
 * Tausche, die vor dieser Änderung erfasst wurden, haben keine
   `vorgaenger_id`. Sie erscheinen als normaler Ausbau. «Wieder einbauen»
   holt dann nur die alte Komponente zurück, die neue muss man selbst
   ausbauen.
 * Bestehende Datenbanken bekommen die Spalte beim Start automatisch
   (`init_db`).
 * Die Sicherheitsabfrage läuft nur im Browser. Die Regeln (nur letzter
   Schritt) prüft das Backend.

# Datum und Quelle des Kilometerstands

Date: 2026-11-17

## Status

Accepted

## Context

Auf der Detailseite war unklar, wie man den Kilometerstand nachführt (Issue #2).
Man sah nicht, ob der Gesamtstand oder die gefahrenen km gemeint sind, wann der
Stand zuletzt geändert wurde und ob der Wert von Strava kommt. Die Tabelle
`velo` speicherte nur `km_stand`, aber weder Datum noch Herkunft. Der Stand
ändert sich an drei Stellen: von Hand auf der Detailseite, beim Bearbeiten des
Velos und beim Abgleich mit Strava.

## Options Considered

 * A: Kein Datum speichern, nur Beschriftung und Hilfetext verbessern. Am
   einfachsten, aber ein Akzeptanzkriterium bliebe offen.
 * B: Eine Spalte `km_stand_datum` in `velo`. Einfach, zeigt aber nicht, ob der
   Wert von Strava stammt.
 * C: Zwei Spalten `km_stand_datum` und `km_stand_quelle` (`manuell` /
   `strava`) in `velo`.
 * D: Eine neue Tabelle `km_eintrag` mit jeder Änderung (Datum, Stand, Quelle).
   Damit wäre ein Verlauf möglich, das braucht heute aber niemand, und es wären
   eine neue Tabelle und mehr Abfragen nötig.

Für «+ gefahrene km» standen zur Wahl: ein zweites Feld, ein Umschalter
«Gesamtstand / gefahrene km» im selben Feld oder gar keine solche Eingabe.

## Decision

Wir wählen Variante C. Entschieden vom Projektteam.

 * `velo` bekommt die Spalten `km_stand_datum` (ISO-Datum) und
   `km_stand_quelle` (`manuell` oder `strava`).
 * Alle Stellen, die den Stand ändern, gehen über die Funktion
   `setze_km_stand()` in `views.py`. Sie setzt Datum und Quelle immer mit.
 * Die Detailseite zeigt «Stand vom … · von Hand eingetragen / von Strava
   übernommen», eine sichtbare Beschriftung mit Hilfetext und bei verknüpften
   Velos einen Hinweis, wie der Abgleich mit Strava wirkt.
 * Ein zweites Formular «Oder gefahrene km dazuzählen» schickt `km_plus` an
   dieselbe Route. Den neuen Stand rechnet der Server aus, nicht JavaScript.

## Reasons

Zwei Spalten beantworten genau die Fragen aus dem Issue und bleiben leicht
verständlich. Weil eine einzige Funktion den Stand setzt, kann keine Stelle das
Datum vergessen. Die Rechnung «alt + gefahrene km» gehört ins Backend: Dort
gelten dieselben Prüfungen wie für den Gesamtstand, und die Seite braucht
kein JavaScript. Ein eigenes zweites Feld ist klarer als ein Umschalter, der
sich mit der Checkbox «Kilometerstand korrigieren» in die Quere käme.

## Consequences

 * Bestehende Datenbanken (z.B. auf Azure) bekommen die Spalten beim Start
   automatisch (`init_db`). Bei bestehenden Velos ist das Datum leer, die Seite
   zeigt dann «Datum der letzten Änderung unbekannt», bis der Stand das nächste
   Mal geändert wird.
 * Gespeichert ist nur die letzte Änderung, kein Verlauf. Braucht man später
   einen Verlauf der Kilometer, ist Variante D der nächste Schritt.
 * Gefahrene km können nur dazugezählt werden. Fürs Abziehen gibt es weiterhin
   «Kilometerstand korrigieren».

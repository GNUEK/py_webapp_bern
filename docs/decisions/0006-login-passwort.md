# Login mit einem gemeinsamen Passwort im Code

Date: 2026-10-19

## Status

Accepted (ergänzt [0005](0005-umfang-und-strava.md), wo Login noch
ausgeschlossen war)

## Context

Die App läuft öffentlich auf Azure. Ohne Login kann jeder, der die URL kennt,
Velos ansehen, ändern und löschen und die Strava-Verbindung benutzen
(Issue #11). Es gibt nur einen gemeinsamen Datenbestand und eine
Strava-Verbindung. Das Repository auf GitHub ist öffentlich.

## Options Considered

 * Nur ein Passwort, fest im Code: am einfachsten, keine Einstellungen nötig.
   Nachteil: Wer das öffentliche Repository liest, kennt das Passwort.
 * Passwort (oder Benutzer und Passwort-Hash) in Umgebungsvariablen: das
   Passwort steht nicht im Repository. Nachteil: `.env` lokal und
   App-Settings auf Azure müssen gepflegt werden.
 * Benutzerkonten in der Datenbank (z.B. mit Flask-Login): eigene Daten pro
   Person. Nachteil: jede Tabelle braucht einen Bezug zum Benutzer,
   Registrierung, Passwort-Reset; deutlich mehr Aufwand.

## Decision

Ein gemeinsames Passwort `Velo26`, fest in `src/app/auth.py`. Kein
Benutzername. Nach der Anmeldung speichert Flask `angemeldet = True` in der
Session. Die Prüfung läuft zentral in `before_request`, ausgenommen sind nur
`/login` und die statischen Dateien. Entschieden vom Projektteam
(Joel Schwarz), bewusst als einfachste Lösung.

## Reasons

Für den Prototyp und die Demo zählt, dass die Daten nicht ganz offen
herumliegen und der Login leicht zu erklären ist. Die zentrale Prüfung im
Backend kann bei neuen Seiten nicht vergessen werden.

## Consequences

 * Der Schutz ist schwach: das Passwort ist im öffentlichen Repository
   lesbar. Er hält zufällige Besucher ab, keine gezielten Angriffe.
 * Zum Ändern des Passworts braucht es einen Commit und ein Deployment.
 * Akzeptanzkriterien aus Issue #11, die damit wegfallen: Zugangsdaten in
   Umgebungsvariablen, Startprüfung fehlender Login-Variablen.
 * Nächste Schritte für einen echten Betrieb: Passwort in eine
   Umgebungsvariable verschieben, Schutz gegen viele Rateversuche,
   CSRF-Tokens in Formularen.

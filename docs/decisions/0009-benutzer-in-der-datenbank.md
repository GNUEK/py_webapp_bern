# Login mit Benutzern in der Datenbank

Date: 2026-11-04

## Status

Accepted (löst [0006](0006-login-passwort.md) ab)

## Context

Seit Entscheid 0006 schützt ein gemeinsames Passwort im Code die App. Das
Passwort ist im öffentlichen Repository lesbar und lässt sich nur mit einem
Commit ändern. Rückmeldung im Kurs: akzeptiert, aber nicht schön. Besser wäre
eine ganz einfache Benutzerverwaltung in der Datenbank, in der man Benutzer
über ein DB-Tool einrichtet.

## Options Considered

 * Passwort im Klartext in der Tabelle `benutzer`: am einfachsten
   einzutragen. Nachteil: Wer die DB-Datei sieht, kennt alle Passwörter.
 * Passwort als Hash in der Tabelle `benutzer`: übliche Praxis, die DB
   verrät die Passwörter nicht. Nachteil: Den Hash muss man mit einem kleinen
   Befehl erzeugen, bevor man ihn im DB-Tool einträgt.
 * Vollständige Benutzerverwaltung (Registrierung, eigene Velos pro Person,
   z.B. Flask-Login): deutlich grösserer Umbau aller Abfragen.

## Decision

Tabelle `benutzer` mit `name` und `passwort_hash` (Werkzeug-Hash). Keine
Registrierung in der App: Benutzer richtet man mit der VS-Code-Erweiterung
SQLite ein, den Hash erzeugt `uv run flask --app src/app passwort-hash`.
Alle Benutzer sehen dieselben Daten. Entschieden vom Projektteam
(Joel Schwarz) nach der Rückmeldung im Kurs.

## Reasons

Kein Passwort mehr im Repository, und Passwörter lassen sich ohne Deployment
ändern. Die Lösung bleibt klein: eine Tabelle, eine Abfrage beim Login und
ein Befehl. Der Hash ist Standard und mit einem Satz erklärbar: Die App
speichert nur einen "Fingerabdruck" des Passworts und vergleicht beim Login
den Fingerabdruck der Eingabe damit.

## Consequences

 * Ohne Eintrag in `benutzer` kann sich niemand anmelden. Nach dem ersten
   Start muss man lokal einen Benutzer einrichten (Anleitung im README).
 * Auf Azure liegt die Datenbank unter `/home/data/velo.db`. Die
   VS-Code-Erweiterung erreicht sie nicht direkt; dort braucht es einen
   anderen Weg (offen, eigenes Issue).
 * Für einen echten Betrieb fehlen weiterhin: Schutz gegen viele
   Rateversuche, CSRF-Tokens, Rollen.

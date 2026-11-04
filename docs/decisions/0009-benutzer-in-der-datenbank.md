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
Registrierung in der App: Den Hash erzeugt
`uv run flask --app src/app passwort-hash`, eingetragen wird er mit dem
Skript `tools/benutzer_setzen.py`, auf Azure über die SSH-Konsole.
Alle Benutzer sehen dieselben Daten. Für den Prototyp verwenden wir bewusst
nur einen gemeinsamen Benutzer. Entschieden vom Projektteam
(Joel Schwarz) nach der Rückmeldung im Kurs.

Zuerst war die VS-Code-Erweiterung SQLite als DB-Tool vorgesehen. Sie
erreicht aber nur die lokale Datenbank, nicht die auf Azure. Darum das
Skript: Es braucht nur die Python-Standardbibliothek und läuft deshalb auch
in der SSH-Konsole von Azure.

## Reasons

Kein Passwort mehr im Repository, und Passwörter lassen sich ohne Deployment
ändern. Die Lösung bleibt klein: eine Tabelle, eine Abfrage beim Login und
ein Befehl. Der Hash ist Standard und mit einem Satz erklärbar: Die App
speichert nur einen "Fingerabdruck" des Passworts und vergleicht beim Login
den Fingerabdruck der Eingabe damit.

## Consequences

 * Ohne Eintrag in `benutzer` kann sich niemand anmelden. Auf Azure und in
   jeder lokalen Datenbank muss man den Benutzer einmal einrichten
   (Anleitung im README).
 * Hash und Passwort gehören nicht ins Repository und nicht in Issues: Das
   Repository ist öffentlich, und ein kurzes Passwort lässt sich aus dem Hash
   durch Ausprobieren finden.
 * Für einen echten Betrieb fehlen weiterhin: Schutz gegen viele
   Rateversuche, CSRF-Tokens, Rollen.

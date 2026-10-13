# Datenbank: SQLite mit dem Python-Modul sqlite3

Date: 2026-10-12

## Status

Accepted

## Context

Die Aufgabenstellung verlangt mindestens eine Tabelle in einer Datenbank.
Die Projektskizze sah SQLite über SQLAlchemy vor. Wir haben drei fachliche
Tabellen (Velo, Komponente, Wartung) und wenige, einfache Abfragen.

## Options Considered

 * SQLite mit dem eingebauten Modul `sqlite3` und SQL von Hand: keine
   zusätzliche Bibliothek, jede Abfrage ist im Code direkt lesbar.
   Nachteil: SQL selbst schreiben, Schemaänderungen von Hand.
 * SQLite mit SQLAlchemy (ORM): Tabellen als Python-Klassen, Migrationen mit
   Alembic möglich. Nachteil: zusätzliche Abstraktion, die man erklären muss.
 * PostgreSQL auf Azure: robuster für mehrere Nutzer, aber kostet und braucht
   einen eigenen Dienst.

## Decision

SQLite mit `sqlite3`, Schema in `src/app/schema.sql`. Bewusste Abweichung
von der Skizze (SQLAlchemy).

## Reasons

Für vier Tabellen ist ein ORM mehr Aufwand als Nutzen. Das SQL zeigt direkt,
was in der Datenbank passiert, was in der Präsentation und in der Prüfung
leichter zu erklären ist. Abfragen nutzen immer Platzhalter (`?`), damit
keine SQL-Injection möglich ist.

## Consequences

 * Ändert sich das Schema, muss man die Datenbank lokal löschen oder eine
   `ALTER TABLE`-Anweisung schreiben. `CREATE TABLE IF NOT EXISTS` legt nur
   fehlende Tabellen an.
 * Auf Azure App Service bleibt nur der Ordner `/home` bei Neustarts und
   Deployments erhalten. Darum dort `DATABASE_PATH=/home/data/velo.db` setzen.
 * SQLite verträgt nur eine Instanz der App gleichzeitig (kein Hochskalieren).

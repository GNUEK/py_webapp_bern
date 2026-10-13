# Backend-Framework: Flask

Date: 2026-10-12

## Status

Accepted

## Context

Die Aufgabenstellung verlangt ein Python-Backend mit Flask, Django oder
FastAPI. Wir sind drei Personen ohne Informatik-Hintergrund mit wenig Zeit.
Die App braucht nur wenige Seiten mit Formularen und Listen.

## Options Considered

 * Flask: klein, wenig Magie, jede Route ist eine sichtbare Funktion.
   Nachteil: Formulare, Datenbank und Login muss man selbst zusammenstecken.
 * Django: bringt Admin, ORM, Formulare und Login mit. Nachteil: viele
   Konventionen und Dateien, die man verstehen muss, bevor man etwas sieht.
 * FastAPI: stark für JSON-APIs. Nachteil: für HTML-Seiten mit Formularen
   braucht es mehr Zusatzarbeit.

## Decision

Flask, gestartet mit Gunicorn (`app:app`). Umgesetzt gemäss Projektskizze.

## Reasons

Flask ist am einfachsten zu erklären, was für die Präsentation (Fragen zum
Code) wichtig ist. Das Template enthält bereits eine Anleitung für Flask auf
Azure App Service.

## Consequences

Eingabeprüfung (`formulare.py`) und Datenbankzugriff (`db.py`) schreiben wir
selbst. Ein Login fehlt; siehe Entscheid 0005.

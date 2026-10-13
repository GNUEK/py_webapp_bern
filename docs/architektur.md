# Architektur

## Komponenten

```mermaid
flowchart LR
    Browser["Browser<br/>HTML + Bootstrap (CDN)"]

    subgraph Azure["Azure App Service"]
        Gunicorn["Gunicorn<br/>(startup.sh)"]
        subgraph Flask["Flask-App src/app"]
            Views["views.py<br/>Velos, Komponenten, Wartung"]
            StravaMod["strava.py<br/>OAuth, Kilometerabgleich"]
            Formulare["formulare.py<br/>Eingaben prüfen"]
            Wartung["wartung.py<br/>Fälligkeitslogik"]
            Templates["templates/*.html<br/>Jinja"]
            DB["db.py"]
        end
        SQLite[("SQLite<br/>velo.db")]
    end

    Strava["Strava API<br/>(optional)"]
    GitHub["GitHub Actions<br/>Tests + Deployment"]

    Browser -- "HTTP GET/POST" --> Gunicorn --> Views
    Browser -- "/strava" --> StravaMod
    Views --> Formulare
    Views --> Wartung
    Views --> Templates
    Views --> DB
    StravaMod --> DB
    StravaMod -- "HTTPS, OAuth2" --> Strava
    DB --> SQLite
    GitHub -- "Deploy bei Push auf main" --> Azure
```

Die Seiten werden vollständig auf dem Server erzeugt (Jinja-Templates).
Es gibt kein separates JavaScript-Frontend und keinen Build-Schritt.

## Verantwortlichkeiten

| Ort | Was dort passiert |
| --- | --- |
| Browser | Formulare anzeigen, einfache Komfortprüfungen (`required`, `min`) |
| `views.py`, `strava.py` | Anfragen entgegennehmen, Daten lesen und schreiben, Seiten rendern |
| `formulare.py` | Jede Eingabe im Backend prüfen (der Browser lässt sich umgehen) |
| `wartung.py` | Fälligkeit berechnen; kennt weder Flask noch Datenbank, darum gut testbar |
| Datenbank | Daten speichern, Grundregeln absichern (`NOT NULL`, `CHECK`, Fremdschlüssel) |

## Datenmodell

```mermaid
erDiagram
    VELO ||--o{ KOMPONENTE : hat
    KOMPONENTE ||--o{ WARTUNG : hat

    VELO {
        int id PK
        text name
        text typ
        text rahmennummer
        text groesse
        real gewicht_kg
        real preis_chf
        int km_stand
        text strava_gear_id
    }
    KOMPONENTE {
        int id PK
        int velo_id FK
        text bezeichnung
        text kategorie
        text einbau_datum
        int einbau_km
        int intervall_km
        int intervall_tage
        text letzte_wartung_datum
        int letzte_wartung_km
        text anleitung_url
        text checkliste
        int aktiv
    }
    WARTUNG {
        int id PK
        int komponente_id FK
        text datum
        int km_stand
        text notiz
        text erledigt
    }
    STRAVA_TOKEN {
        int id PK
        text access_token
        text refresh_token
        int expires_at
    }
```

Eine getauschte Komponente wird nicht gelöscht, sondern auf `aktiv = 0`
gesetzt. So bleibt sichtbar, wie viele Kilometer sie gehalten hat.

## Fälligkeitsregel

Gezählt wird ab der letzten Wartung (beim Einbau ist das der Einbau):

* **fällig**: Intervall erreicht oder überschritten
* **bald fällig**: weniger als 10 % der Kilometer oder höchstens 14 Tage übrig
* Hat eine Komponente beide Intervalle, gilt das, was zuerst eintritt.
* Der Status eines Velos ist der dringendste Status seiner Komponenten.

## Ablauf Strava-Anmeldung (OAuth2)

```mermaid
sequenceDiagram
    actor N as Nutzer
    participant A as Flask-App
    participant S as Strava
    N->>A: /strava/verbinden
    A->>N: Weiterleitung zu Strava (mit state)
    N->>S: Anmelden und zustimmen
    S->>A: /strava/callback?code=…&state=…
    A->>S: Code gegen Tokens tauschen (mit Client-Secret)
    S-->>A: access_token, refresh_token, expires_at
    A->>S: GET /athlete (Velos mit Distanz in Metern)
    A->>A: Kilometerstand verknüpfter Velos erhöhen
```

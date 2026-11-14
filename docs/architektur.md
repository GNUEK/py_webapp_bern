# Architektur

## Komponenten

```mermaid
flowchart LR
    Browser["Browser<br/>HTML + Bootstrap (CDN)"]

    subgraph Azure["Azure App Service"]
        Gunicorn["Gunicorn<br/>(startup.sh)"]
        subgraph Flask["Flask-App src/app"]
            Auth["auth.py<br/>Login-Prüfung vor jeder Anfrage"]
            Views["views.py<br/>Velos, Komponenten, Wartung"]
            StravaMod["strava.py<br/>OAuth, Kilometerabgleich"]
            Formulare["formulare.py<br/>Eingaben prüfen"]
            Wartung["wartung.py<br/>Fälligkeitslogik"]
            Templates["templates/*.html<br/>Jinja"]
            DB["db.py"]
        end
        SQLite[("SQLite<br/>velo.db")]
        Skript["tools/benutzer_setzen.py<br/>Benutzer einrichten"]
    end

    Strava["Strava API<br/>(optional)"]
    GitHub["GitHub Actions<br/>Tests + Deployment"]
    Admin["Teammitglied<br/>Azure-Portal, SSH-Konsole"]

    Browser -- "HTTP GET/POST" --> Gunicorn --> Auth
    Auth -- "angemeldet" --> Views
    Auth -- "angemeldet, /strava" --> StravaMod
    Auth --> DB
    Views --> Formulare
    Views --> Wartung
    Views --> Templates
    Views --> DB
    StravaMod --> DB
    StravaMod -- "HTTPS, OAuth2" --> Strava
    DB --> SQLite
    Admin -- "SSH" --> Skript --> SQLite
    GitHub -- "Deploy bei Push auf master" --> Azure
```

Die Seiten werden vollständig auf dem Server erzeugt (Jinja-Templates).
Es gibt kein separates JavaScript-Frontend und keinen Build-Schritt.

## Verantwortlichkeiten

| Ort | Was dort passiert |
| --- | --- |
| Browser | Formulare anzeigen, einfache Komfortprüfungen (`required`, `min`) |
| `auth.py` | Vor jeder Anfrage prüfen, ob jemand angemeldet ist; Login und Logout |
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
    BENUTZER {
        int id PK
        text name UK
        text passwort_hash
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

`BENUTZER` und `STRAVA_TOKEN` stehen für sich allein: Alle angemeldeten
Benutzer sehen dieselben Velos, und es gibt nur eine Strava-Verbindung
([Entscheid 0009](decisions/0009-benutzer-in-der-datenbank.md)).

## Login und Benutzer einrichten

`auth.login_erzwingen` läuft vor jeder Anfrage. Ohne Anmeldung leitet es auf
`/login` weiter; nur `/login` und die statischen Dateien sind frei. In der
Datenbank steht nur der Hash des Passworts.

```mermaid
sequenceDiagram
    actor N as Nutzer
    participant A as Flask-App (auth.py)
    participant D as SQLite
    N->>A: GET /velos
    A->>N: nicht angemeldet: Weiterleitung zu /login?next=/velos
    N->>A: POST /login (Name, Passwort)
    A->>D: passwort_hash zum Namen lesen
    D-->>A: Hash
    A->>A: Hash der Eingabe vergleichen
    A->>N: Session setzen, Weiterleitung zu /velos
```

Eine Registrierung in der App gibt es nicht. Benutzer richtet ein
Teammitglied direkt auf dem Server ein:

```mermaid
sequenceDiagram
    actor T as Teammitglied
    participant L as Eigener Rechner
    participant S as Azure SSH-Konsole
    participant D as SQLite /home/data/velo.db
    T->>L: uv run flask --app src/app passwort-hash
    L-->>T: Hash (scrypt:…)
    T->>S: Azure-Portal → Entwicklungstools → SSH
    T->>S: python3 tools/benutzer_setzen.py NAME 'HASH'
    S->>D: Benutzer anlegen oder Hash ersetzen
```

Der Hash wird nur von Hand in die SSH-Konsole kopiert. Er gehört weder ins
Repository noch in Issues, weil beide öffentlich sind.

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

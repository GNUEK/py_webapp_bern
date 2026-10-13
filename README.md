# Velo-Wartungslogbuch

Eine Webapp, in der man seine Velos und deren Komponenten erfasst und sieht,
welche Wartung nach Kilometern oder nach Datum fällig ist: Kette, Bremsbeläge,
Reifen oder der Jahresservice. Die Kilometer trägt man von Hand nach oder holt
sie optional aus Strava.

Projekt im Modul Softwareentwicklung (Master Wirtschaftsinformatik), Gruppe
Montag+.

## Funktionen

| Nr. | Funktion | Wo |
| --- | --- | --- |
| M1 | Velo erfassen und speichern (Name, Typ, Rahmennummer, Grösse, Gewicht, Preis, Kilometerstand) | «Velo erfassen» |
| M2 | Übersicht aller Velos mit Wartungsstatus (ok, bald fällig, fällig) | Startseite |
| M3 | Automatisches Deployment über GitHub Actions auf Azure | `.github/workflows/ci-cd.yml` |
| M4 | Unittests, Architektur, Entscheide | `tests/`, `docs/` |
| K1 | Kilometerstand nachführen, Wartung als erledigt markieren | Velo-Detailseite |
| K2 | Komponenten mit eigenem Intervall nach Kilometern und/oder Tagen | Velo-Detailseite |
| K3 | Komponenten tauschen, ergänzen (z.B. Garmin, Flaschenhalter) und ausbauen | Velo-Detailseite |
| K4 | Strava: Gesamtkilometer pro Velo übernehmen (optional) | «Strava» |
| K5 | Wartungscheckliste und Link zur Montageanleitung pro Komponente | Wartungsformular |

## Get started

Voraussetzung: [uv](https://docs.astral.sh/uv/) ist installiert.

```bash
uv lock          # einmalig, falls uv.lock noch nicht zu pyproject.toml passt
uv sync --all-groups
uv run flask --app src/app run --debug
```

Danach http://localhost:5000 öffnen. Die Datenbank `instance/velo.db` wird
beim ersten Start automatisch angelegt.

Wie auf Azure mit Gunicorn starten (Linux/macOS):

```bash
uv run gunicorn --chdir src app:app
```

oder unter Windows:

```powershell
uv run waitress-serve --app-module=app:app --listen=127.0.0.1:8000
```

(dafür vorher im Ordner `src` stehen oder `$env:PYTHONPATH="src"` setzen)

### Tests

```bash
uv run pytest        # Tests mit Abdeckungsbericht
uv run ruff check .  # Code-Stil
```

### Einstellungen

Lokal liest die App eine Datei `.env` (Vorlage: `.env.example`).

| Variable | Zweck |
| --- | --- |
| `SECRET_KEY` | schützt die Session; auf Azure unbedingt setzen |
| `DATABASE_PATH` | Ort der SQLite-Datei; auf Azure `/home/data/velo.db` |
| `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` | nur für K4 Strava |

## Strava einrichten (optional)

1. Auf https://www.strava.com/settings/api eine App anlegen.
2. «Authorization Callback Domain» auf `localhost` setzen (lokal) bzw. auf
   den Hostnamen der Azure-App, z.B. `velo-logbuch.azurewebsites.net`.
3. Client-ID und Client-Secret als `STRAVA_CLIENT_ID` und
   `STRAVA_CLIENT_SECRET` in `.env` bzw. in den Azure-App-Settings eintragen.
4. In der App auf «Strava» → «Mit Strava verbinden», danach jedes Velo
   einem Strava-Velo zuordnen und «Kilometer übernehmen».

Die Velos müssen in Strava als Ausrüstung («Gear») erfasst sein.

## Deployment auf Azure App Service

Einmalig einrichten:

1. In Azure eine Web App mit Runtime **Python 3.13** (Linux) anlegen.
2. Unter *Konfiguration*:
   * Startup Command: `startup.sh`
   * App-Settings: `SCM_DO_BUILD_DURING_DEPLOYMENT=true`,
     `SECRET_KEY=<zufälliger Text>`, `DATABASE_PATH=/home/data/velo.db`,
     optional die beiden Strava-Variablen.
3. In der Web App unter *Übersicht* → «Veröffentlichungsprofil herunterladen».
4. In GitHub unter *Settings → Secrets and variables → Actions*:
   * Secret `AZURE_WEBAPP_PUBLISH_PROFILE` = Inhalt der heruntergeladenen Datei
   * Variable `AZURE_WEBAPP_NAME` = Name der Web App

Ab dann deployt jeder Push auf `main` automatisch, sofern alle Tests grün
sind. Ohne das Secret läuft nur der Testteil.

## Lokales Deployment mit Docker

```bash
docker build . -t velo-logbuch
docker run -p 8000:8000 -v velo-daten:/app/data velo-logbuch
```

Danach http://localhost:8000 öffnen. Das Volume `velo-daten` behält die
Datenbank, wenn der Container neu startet.

## Understanding the sources

```
src/app/
├── __init__.py   App erstellen und konfigurieren (create_app, app)
├── views.py      Seiten und Operationen: Velos, Komponenten, Wartung
├── strava.py     Strava-Anmeldung (OAuth2) und Kilometerabgleich
├── wartung.py    Fälligkeitslogik, ohne Flask und ohne Datenbank
├── formulare.py  Prüfung aller Eingaben im Backend
├── vorlagen.py   Standardkomponenten mit Richtwerten
├── db.py         Verbindung zur SQLite-Datenbank
├── schema.sql    Tabellen
├── templates/    HTML-Seiten (Jinja)
└── static/       CSS
tests/            pytest: Fälligkeitslogik, Seiten, Strava (ohne echten Aufruf)
docs/             Architektur und Entscheide
```

Die wichtigsten Ideen:

* **Fälligkeit wird berechnet, nicht gespeichert.** Gespeichert sind nur
  Kilometerstand und letzte Wartung; `wartung.py` rechnet bei jedem Aufruf
  aus, was fällig ist. Darum kann der Status nie veralten.
* **Getauschte Teile bleiben erhalten.** Eine ausgebaute Komponente wird
  archiviert, nicht gelöscht. So sieht man, wie lange sie gehalten hat.
* **Das Backend prüft alles.** Die Prüfungen im Browser sind nur Komfort.
* **Strava ist ein Zusatz.** Ohne Zugangsdaten läuft die App mit manuell
  nachgeführten Kilometern.

Details: [Architektur](docs/architektur.md) mit Komponentendiagramm,
Datenmodell und OAuth-Ablauf, sowie die Entscheide in
[docs/decisions](docs/decisions).

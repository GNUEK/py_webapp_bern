# Velo-Wartungslogbuch

Eine Webapp, in der man seine Velos und deren Komponenten erfasst und sieht,
welche Wartung nach Kilometern oder nach Datum fällig ist: Kette, Bremsbeläge,
Reifen oder der Jahresservice. Die Kilometer trägt man von Hand nach oder holt
sie optional aus Strava.

Projekt im Modul Softwareentwicklung (Master Wirtschaftsinformatik), Gruppe
Montag+.

**Live auf Azure:**
https://velo-logbuch-htdegwarhzgqbpb0.switzerlandnorth-01.azurewebsites.net/
(Anmeldung nötig)

## Funktionen

| Funktion | Wo |
| --- | --- |
| Anmelden mit Benutzername und Passwort | Login-Seite |
| Übersicht aller Velos mit Wartungsstatus (ok, bald fällig, fällig) | Startseite |
| Velo erfassen, bearbeiten und löschen (Name, Typ, Rahmennummer, Grösse, Gewicht, Preis, Kilometerstand), auf Wunsch mit Standardkomponenten | «Velo erfassen», Velo-Detailseite |
| Kilometerstand nachführen oder nach einem Tippfehler korrigieren | Velo-Detailseite |
| Komponenten mit Intervall nach Kilometern und/oder Tagen hinzufügen, bearbeiten, tauschen und ausbauen, auch Zubehör ohne Wartung (z.B. Garmin, Flaschenhalter) | Velo-Detailseite |
| Wartung erfassen mit Checkliste, Notiz, Link zur Anleitung und Hinweis, wann ein Tausch nötig ist | Wartungsformular |
| Wartungsverlauf und ausgebaute Komponenten mit ihrer Laufleistung | Velo-Detailseite |
| Letzten Schritt rückgängig machen: Wartung löschen, Tausch rückgängig, wieder einbauen | Velo-Detailseite |
| Gesamtkilometer pro Velo aus Strava übernehmen (optional) | «Strava», Startseite |
| Tests bei jedem Push, automatisches Deployment auf Azure bei Push auf `master` | GitHub Actions |

## Erste Schritte

Voraussetzung: [uv](https://docs.astral.sh/uv/) ist installiert.

1. Pakete installieren:

   ```bash
   uv sync --all-groups
   ```

2. App starten. Beim ersten Start legt sie die Datenbank `instance/velo.db`
   an. Das Terminal offen lassen:

   ```bash
   uv run flask --app src/app run --debug
   ```

3. In einem zweiten Terminal einen Passwort-Hash erzeugen (Passwort zweimal
   eingeben, die Zeile mit `scrypt:` kopieren):

   ```bash
   uv run flask --app src/app passwort-hash
   ```

4. Einen Benutzer mit diesem Hash eintragen. Den Hash in **einfache**
   Anführungszeichen setzen, weil er `$`-Zeichen enthält:

   ```bash
   uv run python tools/benutzer_setzen.py NAME 'HASH'
   ```

5. http://localhost:5000 öffnen und mit NAME und Passwort anmelden.

Schritte 3 und 4 braucht es nur einmal pro Datenbank. Mehr dazu unter
[Login](#login).

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

pytest schlägt fehl, wenn die Abdeckung unter 90 % fällt. Was wie getestet
wird, steht im [Testkonzept](docs/testkonzept.md), das Warum in
[Entscheid 0012](docs/decisions/0012-teststrategie.md).

### Einstellungen

Lokal liest die App eine Datei `.env` (Vorlage: `.env.example`).

| Variable | Zweck |
| --- | --- |
| `SECRET_KEY` | schützt die Session; auf Azure unbedingt setzen. Fehlt er, nimmt die App einen Zufallswert, und nach jedem Neustart sind alle abgemeldet ([Entscheid 0011](docs/decisions/0011-session-absichern.md)) |
| `DATABASE_PATH` | Ort der SQLite-Datei; auf Azure `/home/data/velo.db` |
| `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` | nur für K4 Strava |

### Login

Man meldet sich mit Benutzername und Passwort an. Die Benutzer stehen in der
Tabelle `benutzer`, alle sehen dieselben Daten
([Entscheid 0009](docs/decisions/0009-benutzer-in-der-datenbank.md)). Ohne
Anmeldung leitet jede Seite auf `/login` weiter. In der Tabelle steht nur ein
Hash des Passworts, nie das Passwort selbst.

#### Benutzer einrichten oder Passwort ändern

Es gibt keine Registrierung in der App. Benutzer legt man mit dem Skript
`tools/benutzer_setzen.py` an. Es braucht nur die Python-Standardbibliothek
und läuft deshalb auch in der SSH-Konsole von Azure. Gibt es den Namen schon,
ersetzt es nur das Passwort.

1. **Hash erzeugen (lokal):** `uv run flask --app src/app passwort-hash`,
   das Passwort zweimal eingeben und die ausgegebene Zeile (beginnt mit
   `scrypt:`) kopieren. Den Hash nirgends veröffentlichen.
2. **Auf Azure eintragen:** Azure-Portal → Web App → *Entwicklungstools →
   SSH → Los*, dann:

   ```bash
   cd /home/site/wwwroot
   DATABASE_PATH=/home/data/velo.db python3 tools/benutzer_setzen.py NAME 'HASH'
   ```

   Den Hash in **einfachen** Anführungszeichen übergeben, weil er `$`-Zeichen
   enthält. Ein Neustart der App ist nicht nötig.

Lokal funktioniert dasselbe mit
`uv run python tools/benutzer_setzen.py NAME 'HASH'`. Die App muss dafür
einmal gestartet worden sein, damit die Datenbank existiert.

## Strava einrichten (optional)

Eine Strava-App reicht für lokal und Azure
([Entscheid 0010](docs/decisions/0010-strava-app-und-verbindung.md)).

1. Auf https://www.strava.com/settings/api eine App anlegen.
2. «Authorization Callback Domain» auf den Hostnamen der Azure-App setzen,
   genau wie in der Adresszeile, ohne `https://` und ohne `/`, bei uns
   `velo-logbuch-htdegwarhzgqbpb0.switzerlandnorth-01.azurewebsites.net`. Lokal funktioniert `localhost`
   trotzdem, weil Strava es immer zulässt.
3. Client-ID und Client-Secret als `STRAVA_CLIENT_ID` und
   `STRAVA_CLIENT_SECRET` in `.env` bzw. in den Azure-App-Settings eintragen.
   Das Secret nie ins Repository, in Issues oder in den Chat stellen.
4. In der App auf «Strava» → «Mit Strava verbinden» und bei Strava **beide**
   Berechtigungen zulassen. Danach jedes Velo einem Strava-Velo zuordnen und
   «Kilometer übernehmen».

Die Velos müssen in Strava als Ausrüstung («Gear») erfasst sein. Eine neue
Strava-App lässt zuerst nur das Konto zu, das sie angelegt hat. Die App
kennt nur eine gemeinsame Strava-Verbindung.

## Deployment auf Azure App Service

Einmalig einrichten:

1. In Azure eine Web App mit Runtime **Python 3.13** (Linux) anlegen.
2. Unter *Konfiguration*:
   * Startup Command: `startup.sh`
   * App-Settings: `SCM_DO_BUILD_DURING_DEPLOYMENT=true`,
     `SECRET_KEY` (zufälliger Wert, siehe unten), `DATABASE_PATH=/home/data/velo.db`,
     optional die beiden Strava-Variablen.

   Einen zufälligen Wert für `SECRET_KEY` erzeugt:

   ```bash
   uv run python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. In der Web App unter *Übersicht* → «Veröffentlichungsprofil herunterladen».
4. In GitHub unter *Settings → Secrets and variables → Actions*:
   * Secret `AZURE_WEBAPP_PUBLISH_PROFILE` = Inhalt der heruntergeladenen Datei
   * Variable `AZURE_WEBAPP_NAME` = Name der Web App

Ab dann deployt jeder Push auf `master` automatisch, sofern alle Tests grün
sind. Ohne die Variable `AZURE_WEBAPP_NAME` läuft nur der Testteil (z.B. in
einem Fork). Ist die Variable gesetzt, aber das Secret fehlt, schlägt das
Deployment fehl.

## Lokales Deployment mit Docker

```bash
docker build . -t velo-logbuch
docker run -d --name velo-logbuch -p 8000:8000 \
    -e SECRET_KEY="$(uv run python -c 'import secrets; print(secrets.token_hex(32))')" \
    -v velo-daten:/app/data velo-logbuch
```

Das Volume `velo-daten` behält die Datenbank, wenn der Container neu
startet. `SECRET_KEY` wird beim `docker run` einmal zufällig erzeugt und
bleibt bei einem Neustart des Containers erhalten.

Beim ersten Mal einen Benutzer anlegen, wie unter
[Benutzer einrichten](#benutzer-einrichten-oder-passwort-ändern)
beschrieben. Nur der zweite Schritt läuft im Container:

```bash
uv run flask --app src/app passwort-hash    # lokal, Hash kopieren
docker exec velo-logbuch python tools/benutzer_setzen.py NAME 'HASH'
```

Danach http://localhost:8000 öffnen und anmelden.

## Bekannte Einschränkungen

Die App ist ein Prototyp für den Kurs. Bewusst nicht umgesetzt:

* **Gemeinsame Daten:** Alle angemeldeten Benutzer sehen und ändern
  dieselben Velos. Es gibt keine Rollen und keine Registrierung
  ([0009](docs/decisions/0009-benutzer-in-der-datenbank.md)).
* **Eine Strava-Verbindung** für alle. Eine neue Strava-App lässt zudem nur
  das Konto zu, das sie angelegt hat
  ([0010](docs/decisions/0010-strava-app-und-verbindung.md)).
* **Sicherheit:** Gegen CSRF schützt nur `SameSite=Lax` beim
  Session-Cookie, es gibt keine CSRF-Tokens
  ([0011](docs/decisions/0011-session-absichern.md)). Viele Login-Versuche
  hintereinander werden nicht gebremst.
* **SQLite** verträgt nur eine Instanz der App, ein Hochskalieren auf Azure
  ist nicht möglich ([0003](docs/decisions/0003-datenbank-sqlite.md)).
* **Rückgängig** geht nur für den letzten Schritt einer Komponente
  ([0007](docs/decisions/0007-nur-letzten-schritt-rueckgaengig.md)).

## Aufbau des Codes

```
src/app/
├── __init__.py   App erstellen und konfigurieren (create_app, app)
├── auth.py       Login mit Benutzern aus der DB, Prüfung vor jeder Anfrage
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
tools/            benutzer_setzen.py: Benutzer anlegen (lokal und Azure)
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

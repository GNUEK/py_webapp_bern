# Testkonzept

Dieses Dokument beschreibt, wie das Velo-Wartungslogbuch getestet wird und
was die Tests abdecken. Warum wir so testen, steht im
[Entscheid 0012](decisions/0012-teststrategie.md).

Stand: 17.11.2026, 159 Tests, Abdeckung 99.9 % (Zeilen und Zweige)

## Ziel

Die Tests sollen zeigen, dass

 * **Logik:** die Fälligkeit richtig berechnet wird (km, Tage, das
   dringendere Intervall zählt),
 * **Eingaben:** ungültige oder unplausible Eingaben abgelehnt werden und
   dabei nichts gespeichert wird (z.B. Kilometer sinken nur mit Bestätigung),
 * **Abläufe:** Erfassen, Bearbeiten, Tauschen, Wartung und Rückgängig die
   Datenbank richtig verändern und die Seiten den richtigen Stand anzeigen,
 * **Sicherheit:** ohne Login alles gesperrt ist, nach dem Login nicht auf
   fremde Seiten weitergeleitet wird, der Session-Cookie abgesichert ist und
   die Strava-Anmeldung gegen gefälschte Rückleitungen geschützt ist,
 * **Daten:** bestehende Datenbanken bei einem Update die neuen Spalten
   erhalten,
 * **Strava:** Kilometer korrekt übernommen werden (nur erhöhen, Tokens
   erneuern) und die App bei Fehlern von Strava eine Meldung zeigt statt
   abzustürzen.

Was die Tests bewusst nicht abdecken, steht unter
[Nicht automatisiert getestet](#nicht-automatisiert-getestet).

## Werkzeuge und Ausführung

| Werkzeug | Zweck |
| --- | --- |
| pytest | Tests ausführen |
| pytest-cov | Abdeckung messen, inkl. Zweigen (`if`/`else`) |
| ruff, black | Code-Stil |

```bash
uv run pytest        # alle Tests mit Abdeckungsbericht
uv run ruff check .  # Code-Stil
```

Die gleichen Befehle laufen in GitHub Actions bei jedem Push und Pull Request.
Deployt wird nur, wenn alle Tests grün sind
([Entscheid 0004](decisions/0004-deployment-github-actions-azure.md)).
Liegt die Abdeckung unter **90 %**, schlägt pytest fehl
(`fail_under` in `pyproject.toml`).

## Testebenen

| Ebene | Was | Dateien |
| --- | --- | --- |
| Unit-Tests | Reine Logik ohne Flask und Datenbank | `test_wartung.py`, `test_formulare.py`, Teile von `test_strava.py` |
| Integrationstests | HTTP-Anfragen über den Flask-Testclient, mit echter SQLite-Datei | `test_seiten.py`, `test_velo_bearbeiten.py`, `test_login.py`, `test_strava.py` |
| Skript-Test | `tools/benutzer_setzen.py` als eigener Prozess, so wie auf Azure | `test_benutzer_skript.py` |

Die Integrationstests machen den grössten Teil aus. Sie prüfen eine Funktion
so, wie ein Benutzer sie braucht: Formular abschicken, dann kontrollieren, was
in der Datenbank steht und was die Seite anzeigt.

## Testumgebung

Alle gemeinsamen Hilfen stehen in [`tests/conftest.py`](../tests/conftest.py):

 * **Eigene Datenbank pro Test:** Jeder Test bekommt eine leere SQLite-Datei
   in einem temporären Ordner. Tests beeinflussen sich darum nicht.
 * **Festes Datum:** `HEUTE` ist der 12.10.2026. Tests mit Datumsberechnungen
   laufen so an jedem Tag gleich.
 * **Testbenutzer** mit schnellem Passwort-Hash (echte Hashes sind absichtlich
   langsam).
 * **Clients:** `client` ist angemeldet, `anonym` nicht.
 * **Helfer:** `melde_an`, `erfasse_velo`, `erfasse_komponente`.

## Externe Dienste (Strava)

Strava wird in den Tests **nie** aufgerufen. `requests.post` und
`requests.get` werden mit `monkeypatch` durch Funktionen ersetzt, die eine
vorbereitete Antwort (`FakeAntwort`) liefern oder einen Verbindungsfehler
auslösen. So lassen sich auch Fehlerfälle testen, die mit dem echten Dienst
kaum herbeizuführen sind. Die echte Verbindung wurde von Hand lokal getestet
([Entscheid 0010](decisions/0010-strava-app-und-verbindung.md)).

## Welche Funktion wird wo getestet

| Funktion | Datei | Geprüft wird u.a. |
| --- | --- | --- |
| Fälligkeit berechnen | `test_wartung.py` | Intervall in km und Tagen, das dringendere zählt, Zählung ab letzter Wartung |
| Eingaben prüfen | `test_formulare.py` | Pflichtfelder, Zahlen, Datum nicht in der Zukunft, nur Weblinks (kein `javascript:`) |
| Velos erfassen und Übersicht | `test_seiten.py` | leere Übersicht, Standardkomponenten, fällige Wartung sichtbar, 404 |
| Velo bearbeiten | `test_velo_bearbeiten.py` | Formular vorausgefüllt, km dürfen nicht sinken |
| Kilometer eintragen und korrigieren | `test_seiten.py` | km sinken nur mit Bestätigung und nie unter eine Komponente |
| Wartung erfassen | `test_seiten.py` | Zähler zurückgesetzt, Checkliste, Datum und km gegen Einbau, letzte Wartung und Velo geprüft |
| Komponenten ergänzen, bearbeiten, tauschen | `test_seiten.py` | Kategorie, Zubehör ohne Intervall, Tausch übernimmt Werte, ausgebaute nicht änderbar |
| Rückgängig machen | `test_seiten.py` | nur der letzte Schritt, Tausch erst nach Löschen der Wartungen, Sicherheitsabfrage |
| Ersatzhinweis | `test_seiten.py` | Hinweis im Wartungsformular, beim Tausch übernommen |
| Datenbank-Migration | `test_seiten.py` | alte Datenbanken erhalten neue Spalten |
| Login und Session | `test_login.py` | alle Seiten gesperrt, keine Weiterleitung auf fremde Seiten, ungültige Hashes, Cookie-Einstellungen |
| Benutzer anlegen | `test_benutzer_skript.py` | Benutzer anlegen, Passwort ändern, Klartext statt Hash abgelehnt |
| Strava | `test_strava.py` | OAuth mit `state`, Tokens speichern und erneuern, km nur erhöhen, Fehler von Strava |

## Abdeckung

Die Abdeckung zeigt, welche Zeilen und Zweige kein Test ausführt. Sie zeigt
nicht, ob ein Test das Richtige prüft. Darum ist das Ziel nicht 100 %, sondern:
**Jedes Verhalten, das ein Benutzer sieht, und jede Sicherheitsprüfung hat
einen Test.** Der Mindestwert von 90 % verhindert, dass neuer Code unbemerkt
ohne Tests dazukommt.

## Nicht automatisiert getestet

| Bereich | Warum | Wie geprüft |
| --- | --- | --- |
| Darstellung im Browser (Bootstrap, CSS, Mobile) | keine Browser-Tests, siehe Entscheid 0012 | von Hand |
| Bestätigungsdialoge (`confirm()` vor Löschen und Rückgängig) | die Tests prüfen nur, dass der Dialog im HTML steht | von Hand |
| Eingabeprüfung im Browser (`required`, `type="number"` usw.) | nur Komfort, der Server prüft nochmals (getestet) | nicht nötig |
| Echte Strava-Verbindung | braucht ein Strava-Konto und Internet | von Hand lokal (Entscheid 0010) |
| Deployment auf Azure | läuft nur in GitHub Actions | nach dem Deployment von Hand |
| `startup.sh`, Gunicorn | nur auf Azure relevant | über das Deployment |

**Checkliste von Hand vor einer Abgabe oder nach einem Deployment:**

 1. Anmelden, falsches Passwort zeigt eine Meldung.
 2. Velo mit Standardkomponenten erfassen, die Übersicht zeigt es.
 3. Kilometer erhöhen, bis eine Komponente «bald fällig» bzw. «fällig» ist.
 4. Wartung erfassen, der Status ist wieder «ok»; Wartung rückgängig machen.
 5. Komponente tauschen und den Tausch rückgängig machen.
 6. Bei einem Löschen oder Rückgängig im Bestätigungsdialog «Abbrechen»
    wählen: Es ändert sich nichts. Mit «OK» wird die Aktion ausgeführt.
 7. Seite auf dem Handy ansehen.
 8. (Falls konfiguriert) Mit Strava verbinden und Kilometer abgleichen.
 9. Abmelden; die Übersicht ist danach gesperrt.

## Neue Tests schreiben

 * Pro neuer Funktion mindestens einen Test für den Normalfall und einen für
   eine ungültige Eingabe.
 * Ein Test prüft ein Verhalten. Nach einer abgelehnten Eingabe auch prüfen,
   dass sich in der Datenbank nichts geändert hat.
 * Gemeinsame Hilfen kommen in `conftest.py`, nur in einer Datei gebrauchte
   Hilfen in diese Datei.
 * Externe Dienste immer mit `monkeypatch` ersetzen.

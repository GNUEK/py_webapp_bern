# Teststrategie: Unit- und Integrationstests, Strava gemockt

Date: 2026-11-17

## Status

Accepted

## Context

Vor der Abgabe wollten wir prüfen, ob unsere Tests vollständig sind, und das
Testkonzept festhalten. Die App rendert alle Seiten auf dem Server mit Jinja
und Bootstrap ([0002](0002-frontend-jinja-bootstrap.md)). Es gibt keine
eigenen JavaScript-Dateien, nur fünf Bestätigungsdialoge
(`onsubmit="return confirm(…)"`) vor Löschen und Rückgängig. Die Daten liegen in SQLite
([0003](0003-datenbank-sqlite.md)), Strava ist der einzige externe Dienst
([0010](0010-strava-app-und-verbindung.md)). Die Tests laufen in GitHub
Actions vor jedem Deployment ([0004](0004-deployment-github-actions-azure.md)).

Die Abdeckung lag bei 93 %. Einige Fehlerfälle (v.a. bei Strava) waren
ungetestet, und ein Test prüfte nicht, was sein Name versprach.

## Options Considered

 * **Nur Unit-Tests** der reinen Logik (Fälligkeit, Eingabeprüfung): schnell
   und einfach, prüft aber weder Datenbank, Login noch Abläufe über mehrere
   Seiten.
 * **Unit- und Integrationstests** mit dem Flask-Testclient und einer echten
   SQLite-Datei pro Test, Strava mit `monkeypatch` ersetzt: prüft die Abläufe
   so, wie ein Benutzer sie braucht, bleibt schnell (wenige Sekunden) und
   braucht keine zusätzlichen Werkzeuge.
 * **Zusätzlich Browser-Tests (E2E)** mit Playwright oder Selenium: würde auch
   Darstellung und Klicks prüfen, braucht aber einen Browser in der CI, ist
   langsamer und anfälliger. Bei fünf Bestätigungsdialogen als einziger
   Logik im Browser wäre der Gewinn klein.

## Decision

Wir verwenden Unit- und Integrationstests, Strava wird gemockt. pytest
schlägt fehl, wenn die Abdeckung (Zeilen und Zweige) unter 90 % fällt.
Entschieden vom Projektteam am 17.11.2026.

## Reasons

 * Der Flask-Testclient deckt das Wichtigste ab: Formulare, Datenbank, Login
   und Weiterleitungen. Ausser den Bestätigungsdialogen gibt es im Browser
   keine Logik, die nur ein E2E-Test finden würde. Dass die Dialoge im HTML
   stehen, prüfen die Tests; dass sie erscheinen, prüfen wir von Hand.
 * Die Eingabeprüfung im Browser (`required`, `type="number"` usw.) ist nur
   Komfort. Der Server prüft dieselben Eingaben nochmals, und das ist
   getestet.
 * Eine echte SQLite-Datei statt eines Mocks prüft auch die SQL-Abfragen und
   die Migration alter Datenbanken.
 * Mit gemocktem Strava laufen die Tests ohne Internet und Konto, und auch
   Fehlerfälle wie Timeouts lassen sich gezielt testen.
 * 90 % statt 100 %: Die Abdeckung soll verhindern, dass Code ohne Tests
   dazukommt. Tests nur für die Zahl haben wenig Aussagekraft.

## Consequences

 * Die Darstellung im Browser, die echte Strava-Verbindung und das Deployment
   werden nur von Hand geprüft. Dafür gibt es eine Checkliste im
   [Testkonzept](../testkonzept.md).
 * Neuer Code braucht Tests, sonst kann die CI wegen der Abdeckung rot werden.
 * Sollte später mehr JavaScript dazukommen (z.B. HTMX), sind Browser-Tests neu zu
   prüfen.

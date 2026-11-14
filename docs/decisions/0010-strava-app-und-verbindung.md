# Eine Strava-App und eine gemeinsame Strava-Verbindung

Date: 2026-11-14

## Status

Proposed (wird nach dem End-to-End-Test lokal und auf Azure auf Accepted
gesetzt, Issue #10)

## Context

Der Code für K4 (Strava) gibt es seit [0005](0005-umfang-und-strava.md). Er
wurde aber nie mit einem echten Strava-Konto getestet, und auf Azure fehlt die
Konfiguration. Beim Einrichten waren drei Fragen offen:

 1. Strava erlaubt pro API-App nur **eine** «Authorization Callback Domain».
    Die App läuft aber lokal (`localhost`) und auf Azure
    (`<name>.azurewebsites.net`).
 2. Die Tabelle `strava_token` speichert genau eine Verbindung für alle.
    Seit [0009](0009-benutzer-in-der-datenbank.md) gibt es Benutzer in der
    Datenbank. Braucht jede Person eine eigene Verbindung?
 3. Laut Issue gehören Client-Secret und Tokens nicht in Logs. Gunicorn
    schreibt aber jede angefragte URL ins Access-Log, auch
    `/strava/callback?code=…`.

## Options Considered

Callback-Domain:

 * Zwei Strava-Apps (lokal und Azure): klar getrennt. Dafür doppelte
   Verwaltung und zwei Paare aus ID und Secret.
 * Eine App, Domain je nach Test von Hand umstellen: Man vergisst es leicht,
   und dann bricht der Login auf der anderen Umgebung ab.
 * Eine App mit der Azure-Domain: `localhost` und `127.0.0.1` stehen bei
   Strava immer auf der Whitelist, also funktioniert lokal trotzdem alles.

Verbindung:

 * Eine gemeinsame Verbindung: kein Umbau.
 * Eine Verbindung pro Benutzer: `strava_token` bräuchte eine `benutzer_id`,
   und alle Strava-Abfragen müssten angepasst werden.

OAuth-Code im Access-Log:

 * Akzeptieren und dokumentieren.
 * Gunicorn so einstellen, dass der Query-String nicht im Log landet. Das
   betrifft das Log aller Seiten.

## Decision

 * Eine Strava-App, Callback-Domain = Hostname der Azure-App. Lokal wird
   `localhost` verwendet.
 * Es bleibt eine gemeinsame Strava-Verbindung.
 * Der OAuth-Code im Access-Log wird akzeptiert.

Entschieden vom Projektteam bei der Arbeit an Issue #10.

## Reasons

 * Eine App heisst ein Satz Zugangsdaten in `.env` und in den
   Azure-App-Settings. Es gibt nichts umzustellen.
 * Für den Prototyp verwenden wir bewusst nur einen gemeinsamen Benutzer
   (0009). Mehrere Verbindungen bringen deshalb nichts. Dazu kommt: Eine neue
   Strava-App lässt anfangs ohnehin nur einen Athleten zu, nämlich das Konto
   der Person, die sie angelegt hat.
 * Der Code im Log ist weder Secret noch Token. Er gilt nur einmal, läuft nach
   kurzer Zeit ab und ist nach dem Tausch gegen die Tokens wertlos. Ohne das
   Client-Secret lässt er sich ausserdem gar nicht eintauschen. Access- und
   Refresh-Token tauschen Server und Strava direkt aus, sie erscheinen in
   keiner URL.

## Consequences

 * Nur das Strava-Konto, das die App angelegt hat, kann sich verbinden. Für
   weitere Konten müsste Strava die Athleten-Kapazität erhöhen.
 * Ändert sich der Name der Azure-App, muss man die Callback-Domain in Strava
   anpassen.
 * Will das Team später eine Verbindung pro Benutzer, braucht es
   `strava_token.benutzer_id` und angepasste Abfragen in `strava.py`.
 * Test vom 2026-11-14 bestätigt: Lokal (`localhost`) klappt der ganze
   Ablauf, obwohl in Strava die Azure-Domain eingetragen ist. Getestet:
   verbinden, Velo zuordnen, Kilometer übernehmen. Der Test auf Azure steht
   noch aus.

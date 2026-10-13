# Umfang des Prototyps und Strava als optionale Anbindung

Date: 2026-10-12

## Status

Accepted

## Context

Die Projektskizze definiert die Muss-Kriterien M1–M4 und die Kann-Kriterien
K1–K5. Ob ein externer Web Service Pflicht ist, war bei der Skizze noch
offen. Die Strava-Anmeldung (OAuth2) ist der aufwendigste Teil.

## Options Considered

 * Nur M1–M4 bauen, Kann später: kleinstes Risiko, aber wenig zu zeigen.
 * Alles inklusive Strava als Pflicht: die App wäre ohne Strava-Konto nicht
   nutzbar und hinge von einem fremden Dienst ab.
 * Alles bauen, Strava optional: die App läuft immer mit manuell
   eingetragenen Kilometern; Strava kommt dazu, sobald Zugangsdaten gesetzt
   sind.

## Decision

Prototyp mit M1–M4 und K1–K5. Strava (K4) ist nur aktiv, wenn
`STRAVA_CLIENT_ID` und `STRAVA_CLIENT_SECRET` gesetzt sind.

Nicht umgesetzt (wie in der Skizze): Push-Benachrichtigungen,
Komponentenübernahme per KI, Garmin, Login.

## Reasons

So erfüllt die App die Vorgaben auch dann, wenn Strava nicht klappt, und
zeigt bei der Demo trotzdem einen externen Dienst. Kilometer von Strava
werden nur übernommen, wenn sie höher sind als der lokale Stand; manuell
nachgeführte Kilometer gehen so nicht verloren.

## Consequences

 * Ohne Login gibt es nur einen gemeinsamen Datenbestand und höchstens eine
   Strava-Verbindung. Wer die URL kennt, kann Daten ändern. Für eine
   Kursdemo akzeptiert, für echten Betrieb nicht.
 * Strava-Tokens liegen in der Datenbank, Client-ID und Secret nur in
   Umgebungsvariablen, nie im Repository.
 * Neue Strava-Apps sind zunächst auf das eigene Konto beschränkt; für die
   Demo genügt das.

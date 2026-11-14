# Session-Cookie absichern

Date: 2026-11-14

## Status

Accepted

## Context

Nach dem Login merkt sich Flask den Benutzernamen in einem Session-Cookie,
das mit `SECRET_KEY` signiert ist. Fehlte die Variable, setzte die App bisher
den festen Wert `nur-fuer-lokale-entwicklung` ein. Dieser Wert steht im
öffentlichen Repository: Wer ihn kennt, kann selbst ein Cookie mit
`benutzer=...` signieren und ist ohne Passwort angemeldet. Vergisst man auf
Azure, `SECRET_KEY` zu setzen, merkt man davon nichts.

Ausserdem hat die App keine CSRF-Tokens. Eine fremde Webseite könnte also
versuchen, im Browser einer angemeldeten Person ein Formular an die App zu
schicken (z.B. «Velo löschen»).

## Options Considered

 * Fehlender `SECRET_KEY`:
   * Fester Ersatzwert (bisher): bequem, aber unsicher.
   * Start verweigern: am strengsten, lokal braucht dann jede Person eine
     `.env`.
   * Zufallswert beim Start mit Warnung im Log: sicher und lokal ohne `.env`
     nutzbar. Nach jedem Neustart sind alle abgemeldet.
 * CSRF:
   * `SESSION_COOKIE_SAMESITE="Lax"`: Der Browser schickt das Cookie bei
     POST-Anfragen von fremden Seiten nicht mit. Eine Zeile.
   * CSRF-Tokens mit Flask-WTF: vollständiger Schutz, aber neues Paket und
     Änderungen an allen Formularen und Tests.
 * `SESSION_COOKIE_SECURE` (Cookie nur über https): immer, nie, oder nur auf
   Azure.

## Decision

Fehlt `SECRET_KEY`, erzeugt die App einen Zufallswert und schreibt eine
Warnung ins Log. Das Cookie ist immer `SameSite=Lax`. `Secure` ist es nur auf
Azure, erkannt an der Variable `WEBSITE_HOSTNAME`, die Azure App Service
immer setzt. Entschieden vom Projektteam beim Review vor der Abgabe.

## Reasons

Die Lücke wird mit wenigen Zeilen ohne neues Paket geschlossen. `Secure`
hängt bewusst nicht vom Debug-Modus ab: Lokal läuft die App über http, und
manche Browser (z.B. Safari) nehmen dann kein Secure-Cookie an. Der Login
würde ohne Fehlermeldung scheitern.

## Consequences

 * Ist `SECRET_KEY` auf Azure nicht gesetzt, ist man nach jedem Neustart
   abgemeldet. Das fällt auf und erinnert daran, den Wert zu setzen.
 * `SameSite=Lax` ersetzt keine CSRF-Tokens vollständig. Für einen echten
   Betrieb wären sie weiterhin sinnvoll.

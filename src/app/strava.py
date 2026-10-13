"""K4: Kilometer aus Strava übernehmen (externer Web Service).

Ablauf (OAuth2):
 1. /strava/verbinden leitet zur Strava-Anmeldeseite weiter.
 2. Strava leitet nach der Zustimmung auf /strava/callback zurück und
    schickt einen einmaligen Code mit.
 3. Das Backend tauscht diesen Code gegen ein Access- und ein Refresh-Token.
 4. Mit dem Access-Token liest /strava die Velos ("Gear") des Athleten.
    Das Access-Token läuft nach etwa 6 Stunden ab und wird dann mit dem
    Refresh-Token erneuert.

Client-ID und Client-Secret stehen nie im Code, sondern in
Umgebungsvariablen (lokal in der Datei .env, auf Azure in den App-Settings).
"""

import secrets
import time

import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .db import get_db

bp = Blueprint("strava", __name__, url_prefix="/strava")

AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
TIMEOUT_S = 10


class StravaFehler(Exception):
    """Strava war nicht erreichbar oder hat einen Fehler gemeldet."""


def ist_konfiguriert() -> bool:
    return bool(
        current_app.config.get("STRAVA_CLIENT_ID")
        and current_app.config.get("STRAVA_CLIENT_SECRET")
    )


# --------------------------------------------------------------------------
# Kommunikation mit Strava
# --------------------------------------------------------------------------


def _post_token(daten: dict) -> dict:
    daten = {
        "client_id": current_app.config["STRAVA_CLIENT_ID"],
        "client_secret": current_app.config["STRAVA_CLIENT_SECRET"],
        **daten,
    }
    try:
        antwort = requests.post(TOKEN_URL, data=daten, timeout=TIMEOUT_S)
        antwort.raise_for_status()
    except requests.RequestException as fehler:
        raise StravaFehler(f"Anmeldung bei Strava fehlgeschlagen: {fehler}") from None
    return antwort.json()


def _speichere_token(token: dict, athlet: str | None = None) -> None:
    db = get_db()
    db.execute(
        """INSERT INTO strava_token
               (id, access_token, refresh_token, expires_at, athlet)
           VALUES (1, ?, ?, ?, ?)
           ON CONFLICT (id) DO UPDATE SET
               access_token = excluded.access_token,
               refresh_token = excluded.refresh_token,
               expires_at = excluded.expires_at,
               athlet = COALESCE(excluded.athlet, strava_token.athlet)""",
        (token["access_token"], token["refresh_token"], token["expires_at"], athlet),
    )
    db.commit()


def gueltiges_access_token() -> str | None:
    """Gibt ein gültiges Access-Token zurück und erneuert es bei Bedarf."""
    zeile = get_db().execute("SELECT * FROM strava_token WHERE id = 1").fetchone()
    if zeile is None:
        return None
    # 60 Sekunden Reserve, damit das Token nicht während der Anfrage abläuft
    if zeile["expires_at"] - 60 < time.time():
        token = _post_token(
            {"grant_type": "refresh_token", "refresh_token": zeile["refresh_token"]}
        )
        _speichere_token(token)
        return token["access_token"]
    return zeile["access_token"]


def lade_strava_velos(access_token: str) -> list[dict]:
    """Liest die Velos des Athleten. Strava liefert Distanzen in Metern."""
    try:
        antwort = requests.get(
            ATHLETE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=TIMEOUT_S,
        )
        antwort.raise_for_status()
    except requests.RequestException as fehler:
        raise StravaFehler(f"Strava-Daten nicht lesbar: {fehler}") from None
    return [
        {
            "id": velo["id"],
            "name": velo.get("name") or velo["id"],
            "km": meter_zu_km(velo.get("distance") or 0),
        }
        for velo in antwort.json().get("bikes", [])
    ]


def meter_zu_km(meter: float) -> int:
    return int(meter // 1000)


def kilometer_uebernehmen(strava_velos: list[dict]) -> list[str]:
    """Setzt den Kilometerstand verknüpfter Velos auf den Strava-Wert.

    Der Stand wird nur erhöht, nie verkleinert: Wer zusätzlich Kilometer
    von Hand einträgt, verliert sie so nicht.
    Gibt eine Liste der geänderten Velos zurück (für die Meldung).
    """
    db = get_db()
    geaendert = []
    for strava_velo in strava_velos:
        velo = db.execute(
            "SELECT * FROM velo WHERE strava_gear_id = ?", (strava_velo["id"],)
        ).fetchone()
        if velo is not None and strava_velo["km"] > velo["km_stand"]:
            db.execute(
                "UPDATE velo SET km_stand = ? WHERE id = ?",
                (strava_velo["km"], velo["id"]),
            )
            geaendert.append(f"{velo['name']}: {strava_velo['km']} km")
    db.commit()
    return geaendert


# --------------------------------------------------------------------------
# Seiten
# --------------------------------------------------------------------------


@bp.get("")
def strava_seite():
    db = get_db()
    velos = db.execute("SELECT * FROM velo ORDER BY name").fetchall()
    verbindung = db.execute("SELECT athlet FROM strava_token WHERE id = 1").fetchone()
    strava_velos = []
    if ist_konfiguriert() and verbindung is not None:
        try:
            strava_velos = lade_strava_velos(gueltiges_access_token())
        except StravaFehler as fehler:
            flash(str(fehler), "danger")
    return render_template(
        "strava.html",
        konfiguriert=ist_konfiguriert(),
        verbindung=verbindung,
        velos=velos,
        strava_velos=strava_velos,
    )


@bp.get("/verbinden")
def verbinden():
    if not ist_konfiguriert():
        flash("Strava ist nicht konfiguriert.", "warning")
        return redirect(url_for("strava.strava_seite"))
    # Zufallswert gegen gefälschte Rückleitungen (CSRF-Schutz bei OAuth)
    session["strava_state"] = secrets.token_urlsafe(16)
    parameter = {
        "client_id": current_app.config["STRAVA_CLIENT_ID"],
        "redirect_uri": url_for("strava.callback", _external=True),
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "read,profile:read_all",
        "state": session["strava_state"],
    }
    ziel = requests.Request("GET", AUTHORIZE_URL, params=parameter).prepare().url
    return redirect(ziel)


@bp.get("/callback")
def callback():
    erwartet = session.pop("strava_state", None)
    if not erwartet or request.args.get("state") != erwartet:
        flash("Ungültige Rückmeldung von Strava. Bitte erneut verbinden.", "danger")
        return redirect(url_for("strava.strava_seite"))
    if "error" in request.args or "code" not in request.args:
        flash("Strava-Verbindung wurde abgebrochen.", "warning")
        return redirect(url_for("strava.strava_seite"))
    if "profile:read_all" not in request.args.get("scope", ""):
        flash("Ohne «Profil lesen» sieht die App keine Strava-Velos.", "warning")
    try:
        token = _post_token(
            {"grant_type": "authorization_code", "code": request.args["code"]}
        )
    except StravaFehler as fehler:
        flash(str(fehler), "danger")
        return redirect(url_for("strava.strava_seite"))
    athlet = token.get("athlete") or {}
    name = f"{athlet.get('firstname', '')} {athlet.get('lastname', '')}".strip()
    _speichere_token(token, athlet=name or None)
    flash("Mit Strava verbunden.", "success")
    return redirect(url_for("strava.strava_seite"))


@bp.post("/verknuepfen")
def verknuepfen():
    """Ordnet einem lokalen Velo ein Strava-Velo zu (oder hebt es auf)."""
    db = get_db()
    velo_id = request.form.get("velo_id", type=int)
    gear_id = (request.form.get("strava_gear_id") or "").strip() or None
    if db.execute("SELECT 1 FROM velo WHERE id = ?", (velo_id,)).fetchone() is None:
        flash("Unbekanntes Velo.", "danger")
        return redirect(url_for("strava.strava_seite"))
    # Ein Strava-Velo darf nur mit einem lokalen Velo verknüpft sein
    db.execute(
        "UPDATE velo SET strava_gear_id = NULL WHERE strava_gear_id = ?", (gear_id,)
    )
    db.execute("UPDATE velo SET strava_gear_id = ? WHERE id = ?", (gear_id, velo_id))
    db.commit()
    flash("Verknüpfung gespeichert.", "success")
    return redirect(url_for("strava.strava_seite"))


@bp.post("/abgleichen")
def abgleichen():
    if not ist_konfiguriert():
        flash("Strava ist nicht konfiguriert.", "warning")
        return redirect(url_for("strava.strava_seite"))
    try:
        token = gueltiges_access_token()
        if token is None:
            flash("Zuerst mit Strava verbinden.", "warning")
            return redirect(url_for("strava.strava_seite"))
        geaendert = kilometer_uebernehmen(lade_strava_velos(token))
    except StravaFehler as fehler:
        flash(str(fehler), "danger")
        return redirect(url_for("strava.strava_seite"))
    if geaendert:
        flash("Kilometer übernommen: " + ", ".join(geaendert), "success")
    else:
        flash("Keine neuen Kilometer auf Strava.", "info")
    return redirect(url_for("velos.uebersicht"))


@bp.post("/trennen")
def trennen():
    db = get_db()
    db.execute("DELETE FROM strava_token")
    db.commit()
    flash("Strava-Verbindung getrennt.", "success")
    return redirect(url_for("strava.strava_seite"))

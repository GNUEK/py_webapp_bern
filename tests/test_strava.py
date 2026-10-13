"""Tests der Strava-Anbindung. Strava selbst wird dabei nie aufgerufen."""

from app import strava
from app.db import get_db
from conftest import erfasse_velo


def test_meter_werden_zu_ganzen_km():
    assert strava.meter_zu_km(12345.6) == 12
    assert strava.meter_zu_km(999) == 0


def test_seite_ohne_konfiguration(client):
    antwort = client.get("/strava")
    assert antwort.status_code == 200
    assert "nicht eingerichtet" in antwort.text


def test_verbinden_ohne_konfiguration_leitet_zurueck(client):
    antwort = client.get("/strava/verbinden")
    assert antwort.status_code == 302
    assert antwort.headers["Location"].endswith("/strava")


def test_callback_mit_falschem_state_wird_abgelehnt(client):
    antwort = client.get(
        "/strava/callback?code=abc&state=falsch", follow_redirects=True
    )
    assert "Ungültige Rückmeldung" in antwort.text


def test_kilometer_werden_nur_erhoeht(client, app):
    erfasse_velo(client, name="A", km_stand=1000)
    erfasse_velo(client, name="B", km_stand=5000)
    erfasse_velo(client, name="C", km_stand=10)
    with app.app_context():
        db = get_db()
        db.execute("UPDATE velo SET strava_gear_id = 'b1' WHERE name = 'A'")
        db.execute("UPDATE velo SET strava_gear_id = 'b2' WHERE name = 'B'")
        db.commit()

        geaendert = strava.kilometer_uebernehmen(
            [
                {"id": "b1", "name": "A", "km": 1500},  # mehr als lokal
                {"id": "b2", "name": "B", "km": 4000},  # weniger als lokal
                {"id": "b9", "name": "?", "km": 999},  # nicht verknüpft
            ]
        )
        stand = dict(db.execute("SELECT name, km_stand FROM velo").fetchall())

    assert geaendert == ["A: 1500 km"]
    assert stand == {"A": 1500, "B": 5000, "C": 10}


def test_abgleich_mit_verbindung(client, app, monkeypatch):
    app.config.update(STRAVA_CLIENT_ID="1", STRAVA_CLIENT_SECRET="geheim")
    erfasse_velo(client, name="A", km_stand=100)
    with app.app_context():
        db = get_db()
        db.execute("UPDATE velo SET strava_gear_id = 'b1'")
        db.commit()

    monkeypatch.setattr(strava, "gueltiges_access_token", lambda: "token")
    strava_velos = [{"id": "b1", "name": "A", "km": 250}]
    monkeypatch.setattr(strava, "lade_strava_velos", lambda token: strava_velos)
    antwort = client.post("/strava/abgleichen", follow_redirects=True)
    assert "A: 250 km" in antwort.text

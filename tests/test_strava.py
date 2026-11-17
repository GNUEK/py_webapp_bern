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


# --- Ablauf mit nachgebildeten Antworten von Strava --------------------------


class FakeAntwort:
    """Ersetzt die Antwort von requests, damit Strava nie aufgerufen wird."""

    def __init__(self, daten):
        self.daten = daten

    def raise_for_status(self):
        pass

    def json(self):
        return self.daten


def konfiguriere_strava(app):
    app.config.update(STRAVA_CLIENT_ID="1", STRAVA_CLIENT_SECRET="geheim")


def speichere_token(app, expires_at):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO strava_token (id, access_token, refresh_token, expires_at)"
            " VALUES (1, 'alt', 'refresh-alt', ?)",
            (expires_at,),
        )
        db.commit()


def token_zeile(app):
    with app.app_context():
        return get_db().execute("SELECT * FROM strava_token").fetchone()


def test_callback_speichert_tokens(client, app, monkeypatch):
    konfiguriere_strava(app)
    with client.session_transaction() as session:
        session["strava_state"] = "zufall"
    gesendet = {}

    def fake_post(url, data, timeout):
        gesendet.update(data)
        return FakeAntwort(
            {
                "access_token": "neu",
                "refresh_token": "refresh-neu",
                "expires_at": 2_000_000_000,
                "athlete": {"firstname": "Eva", "lastname": "Muster"},
            }
        )

    monkeypatch.setattr(strava.requests, "post", fake_post)
    antwort = client.get(
        "/strava/callback?code=c1&state=zufall&scope=read,profile:read_all"
    )

    assert antwort.status_code == 302
    # Der Code wird zusammen mit dem Client-Secret eingetauscht
    assert gesendet["code"] == "c1"
    assert gesendet["client_secret"] == "geheim"
    zeile = token_zeile(app)
    assert zeile["access_token"] == "neu"
    assert zeile["athlet"] == "Eva Muster"


def test_abgelaufenes_token_wird_erneuert(app, monkeypatch):
    konfiguriere_strava(app)
    speichere_token(app, expires_at=0)  # längst abgelaufen
    gesendet = {}

    def fake_post(url, data, timeout):
        gesendet.update(data)
        return FakeAntwort(
            {"access_token": "frisch", "refresh_token": "r2", "expires_at": 9e9}
        )

    monkeypatch.setattr(strava.requests, "post", fake_post)
    with app.app_context():
        assert strava.gueltiges_access_token() == "frisch"

    assert gesendet["grant_type"] == "refresh_token"
    assert gesendet["refresh_token"] == "refresh-alt"
    assert token_zeile(app)["access_token"] == "frisch"


def test_gueltiges_token_wird_nicht_erneuert(app, monkeypatch):
    konfiguriere_strava(app)
    speichere_token(app, expires_at=2_000_000_000)

    def darf_nicht_aufgerufen_werden(*args, **kwargs):
        raise AssertionError("Strava darf nicht aufgerufen werden")

    monkeypatch.setattr(strava.requests, "post", darf_nicht_aufgerufen_werden)
    with app.app_context():
        assert strava.gueltiges_access_token() == "alt"


def test_strava_velo_nur_mit_einem_velo_verknuepft(client, app):
    erfasse_velo(client, name="A")
    erfasse_velo(client, name="B")

    def verknuepfungen():
        with app.app_context():
            zeilen = get_db().execute("SELECT name, strava_gear_id FROM velo")
            return dict(zeilen.fetchall())

    client.post("/strava/verknuepfen", data={"velo_id": 1, "strava_gear_id": "b1"})
    assert verknuepfungen() == {"A": "b1", "B": None}

    # Dasselbe Strava-Velo bei B: A verliert die Verknüpfung
    client.post("/strava/verknuepfen", data={"velo_id": 2, "strava_gear_id": "b1"})
    assert verknuepfungen() == {"A": None, "B": "b1"}

    # Leere Auswahl hebt die Verknüpfung auf
    client.post("/strava/verknuepfen", data={"velo_id": 2, "strava_gear_id": ""})
    assert verknuepfungen() == {"A": None, "B": None}


def test_trennen_loescht_tokens(client, app):
    speichere_token(app, expires_at=2_000_000_000)
    antwort = client.post("/strava/trennen", follow_redirects=True)
    assert "getrennt" in antwort.text
    assert token_zeile(app) is None


def test_strava_nicht_erreichbar_zeigt_meldung(client, app, monkeypatch):
    konfiguriere_strava(app)
    speichere_token(app, expires_at=2_000_000_000)

    def fake_get(*args, **kwargs):
        raise strava.requests.ConnectionError("keine Verbindung")

    monkeypatch.setattr(strava.requests, "get", fake_get)
    antwort = client.get("/strava")
    assert antwort.status_code == 200
    assert "Strava-Daten nicht lesbar" in antwort.text


# --- Verbinden und Rückmeldung von Strava (OAuth) ----------------------------


def setze_state(client, state="zufall"):
    with client.session_transaction() as session:
        session["strava_state"] = state


def test_verbinden_leitet_mit_zufaelligem_state_zu_strava(client, app):
    konfiguriere_strava(app)
    antwort = client.get("/strava/verbinden")

    assert antwort.status_code == 302
    ziel = antwort.headers["Location"]
    assert ziel.startswith(strava.AUTHORIZE_URL)
    assert "client_id=1" in ziel
    assert "profile%3Aread_all" in ziel
    # Der state in der Adresse muss derselbe sein wie in der Session
    with client.session_transaction() as session:
        state = session["strava_state"]
    assert f"state={state}" in ziel
    assert "geheim" not in ziel  # Das Client-Secret verlässt den Server nie


def test_callback_bei_abbruch_speichert_nichts(client, app):
    konfiguriere_strava(app)
    setze_state(client)
    antwort = client.get(
        "/strava/callback?error=access_denied&state=zufall", follow_redirects=True
    )
    assert "abgebrochen" in antwort.text
    assert token_zeile(app) is None


def test_callback_ohne_profil_berechtigung_warnt(client, app, monkeypatch):
    konfiguriere_strava(app)
    setze_state(client)
    monkeypatch.setattr(
        strava.requests,
        "post",
        lambda url, data, timeout: FakeAntwort(
            {"access_token": "neu", "refresh_token": "r", "expires_at": 9e9}
        ),
    )
    antwort = client.get(
        "/strava/callback?code=c1&state=zufall&scope=read", follow_redirects=True
    )
    assert "Ohne «Profil lesen»" in antwort.text
    assert token_zeile(app)["access_token"] == "neu"  # trotzdem verbunden


def test_callback_wenn_strava_nicht_antwortet(client, app, monkeypatch):
    konfiguriere_strava(app)
    setze_state(client)

    def fake_post(*args, **kwargs):
        raise strava.requests.ConnectionError("keine Verbindung")

    monkeypatch.setattr(strava.requests, "post", fake_post)
    antwort = client.get(
        "/strava/callback?code=c1&state=zufall&scope=read,profile:read_all",
        follow_redirects=True,
    )
    assert "Anmeldung bei Strava fehlgeschlagen" in antwort.text
    assert token_zeile(app) is None


def test_verknuepfen_mit_unbekanntem_velo(client):
    antwort = client.post(
        "/strava/verknuepfen",
        data={"velo_id": 99, "strava_gear_id": "b1"},
        follow_redirects=True,
    )
    assert "Unbekanntes Velo." in antwort.text


# --- Kilometer abgleichen: Fehlerfälle ----------------------------------------


def test_abgleich_ohne_konfiguration(client):
    antwort = client.post("/strava/abgleichen", follow_redirects=True)
    assert "nicht konfiguriert" in antwort.text


def test_abgleich_ohne_verbindung(client, app):
    konfiguriere_strava(app)
    antwort = client.post("/strava/abgleichen", follow_redirects=True)
    assert "Zuerst mit Strava verbinden" in antwort.text


def test_abgleich_wenn_strava_nicht_antwortet(client, app, monkeypatch):
    konfiguriere_strava(app)
    speichere_token(app, expires_at=0)  # muss erneuert werden

    def fake_post(*args, **kwargs):
        raise strava.requests.Timeout("zu langsam")

    monkeypatch.setattr(strava.requests, "post", fake_post)
    antwort = client.post("/strava/abgleichen", follow_redirects=True)
    assert "Anmeldung bei Strava fehlgeschlagen" in antwort.text


def test_abgleich_ohne_neue_kilometer(client, app, monkeypatch):
    konfiguriere_strava(app)
    erfasse_velo(client, name="A", km_stand=500)
    speichere_token(app, expires_at=2_000_000_000)
    with app.app_context():
        db = get_db()
        db.execute("UPDATE velo SET strava_gear_id = 'b1'")
        db.commit()

    monkeypatch.setattr(
        strava.requests,
        "get",
        lambda *args, **kwargs: FakeAntwort(
            {"bikes": [{"id": "b1", "name": "A", "distance": 400_000}]}
        ),
    )
    antwort = client.post("/strava/abgleichen", follow_redirects=True)
    assert "Keine neuen Kilometer" in antwort.text

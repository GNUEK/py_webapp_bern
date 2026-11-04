"""Tests für den Login (Issue #11)."""

import pytest

from app.db import get_db
from conftest import melde_an

# Ohne Anmeldung --------------------------------------------------------------


@pytest.mark.parametrize(
    "url", ["/", "/velos/neu", "/velos/1", "/strava", "/strava/callback?code=x"]
)
def test_ohne_login_weiterleitung_zum_login(anonym, url):
    antwort = anonym.get(url)
    assert antwort.status_code == 302
    assert antwort.location.startswith("/login?next=")


def test_ohne_login_werden_keine_daten_geaendert(anonym, app):
    antwort = anonym.post("/velos/neu", data={"name": "Fremd", "km_stand": "1"})
    assert antwort.status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM velo").fetchone()[0] == 0


def test_login_seite_und_css_ohne_login_erreichbar(anonym):
    assert anonym.get("/login").status_code == 200
    assert anonym.get("/static/style.css").status_code == 200


def test_navigation_ist_ohne_login_versteckt(anonym):
    seite = anonym.get("/login").text
    assert "Velo erfassen" not in seite
    assert "Abmelden" not in seite


# Anmelden ---------------------------------------------------------------------


def test_login_fuehrt_zur_gewuenschten_seite(anonym):
    assert anonym.get("/velos/neu").location == "/login?next=/velos/neu"

    antwort = melde_an(anonym, next="/velos/neu")
    assert antwort.status_code == 302
    assert antwort.location == "/velos/neu"
    assert anonym.get("/velos/neu").status_code == 200


def test_login_ohne_ziel_fuehrt_zur_uebersicht(anonym):
    antwort = melde_an(anonym)
    assert antwort.location == "/"
    assert "Abmelden" in anonym.get("/").text


@pytest.mark.parametrize(
    "ziel", ["https://boese.example", "//boese.example", "/\\boese.example"]
)
def test_login_leitet_nicht_auf_fremde_seiten(anonym, ziel):
    antwort = melde_an(anonym, next=ziel)
    assert antwort.location == "/"


@pytest.mark.parametrize(
    "name, passwort",
    [("test", "falsch"), ("test", ""), ("unbekannt", "test-passwort")],
)
def test_falsche_zugangsdaten_werden_abgelehnt(anonym, name, passwort):
    antwort = melde_an(anonym, name=name, passwort=passwort)
    assert antwort.status_code == 401
    # Gleiche Meldung, egal ob Benutzer oder Passwort falsch ist
    assert "Benutzername oder Passwort ist falsch." in antwort.text
    assert anonym.get("/").status_code == 302


def test_ungueltiger_hash_in_der_datenbank(anonym, app):
    # z.B. Passwort statt Hash im DB-Tool eingetragen
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO benutzer (name, passwort_hash) VALUES ('x', 'abc')")
        db.commit()
    assert melde_an(anonym, name="x", passwort="abc").status_code == 401


def test_navigation_zeigt_benutzer(client):
    assert "Abmelden (test)" in client.get("/").text


def test_befehl_passwort_hash(app):
    from werkzeug.security import check_password_hash

    ergebnis = app.test_cli_runner().invoke(
        args=["passwort-hash"], input="geheim\ngeheim\n"
    )
    assert ergebnis.exit_code == 0
    assert check_password_hash(ergebnis.output.strip().splitlines()[-1], "geheim")


def test_abmelden(client):
    assert client.get("/").status_code == 200
    antwort = client.post("/logout", follow_redirects=True)
    assert "Du bist abgemeldet." in antwort.text
    assert client.get("/").status_code == 302


def test_strava_callback_erreicht_mit_login_die_app(client):
    # Mit Login wird der Callback verarbeitet (und hier wegen state abgelehnt)
    antwort = client.get("/strava/callback?code=x&state=falsch")
    assert antwort.location == "/strava"

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


@pytest.mark.parametrize("passwort", ["falsch", "velo26", ""])
def test_falsches_passwort_wird_abgelehnt(anonym, passwort):
    antwort = melde_an(anonym, passwort=passwort)
    assert antwort.status_code == 401
    assert "Falsches Passwort." in antwort.text
    assert anonym.get("/").status_code == 302


def test_abmelden(client):
    assert client.get("/").status_code == 200
    antwort = client.post("/logout", follow_redirects=True)
    assert "Du bist abgemeldet." in antwort.text
    assert client.get("/").status_code == 302


def test_strava_callback_erreicht_mit_login_die_app(client):
    # Mit Login wird der Callback verarbeitet (und hier wegen state abgelehnt)
    antwort = client.get("/strava/callback?code=x&state=falsch")
    assert antwort.location == "/strava"

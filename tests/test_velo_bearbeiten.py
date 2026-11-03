"""Tests für das Bearbeiten eines Velos (Route /velos/<id>/bearbeiten)."""

from app.db import get_db
from conftest import erfasse_velo


def velo(app, velo_id=1):
    with app.app_context():
        return (
            get_db().execute("SELECT * FROM velo WHERE id = ?", (velo_id,)).fetchone()
        )


def test_formular_zeigt_aktuelle_werte(client):
    erfasse_velo(client, name="Gravel", km_stand=1000)
    antwort = client.get("/velos/1/bearbeiten")
    assert antwort.status_code == 200
    assert "Gravel" in antwort.text


def test_aenderungen_werden_gespeichert(client, app):
    erfasse_velo(client, name="Gravel", km_stand=1000)
    antwort = client.post(
        "/velos/1/bearbeiten",
        data={
            "name": "Rennvelo",
            "typ": "Rennrad",
            "groesse": "56",
            "gewicht_kg": "8,5",  # Komma wie in der Schweiz üblich
            "preis_chf": "2500",
            "km_stand": "1200",
        },
    )
    assert antwort.status_code == 302
    assert antwort.location == "/velos/1"

    gespeichert = velo(app)
    assert gespeichert["name"] == "Rennvelo"
    assert gespeichert["typ"] == "Rennrad"
    assert gespeichert["gewicht_kg"] == 8.5
    assert gespeichert["km_stand"] == 1200


def test_kilometerstand_darf_gleich_bleiben(client, app):
    erfasse_velo(client, km_stand=1000)
    antwort = client.post("/velos/1/bearbeiten", data={"name": "X", "km_stand": "1000"})
    assert antwort.status_code == 302
    assert velo(app)["km_stand"] == 1000


def test_kleinerer_kilometerstand_wird_abgelehnt(client, app):
    erfasse_velo(client, name="Gravel", km_stand=1000)
    antwort = client.post(
        "/velos/1/bearbeiten", data={"name": "Neu", "km_stand": "900"}
    )
    assert antwort.status_code == 400
    assert "nicht kleiner werden" in antwort.text
    # Nichts wurde verändert, auch der Name nicht
    assert velo(app)["km_stand"] == 1000
    assert velo(app)["name"] == "Gravel"


def test_leerer_name_wird_abgelehnt(client, app):
    erfasse_velo(client, name="Gravel", km_stand=1000)
    antwort = client.post("/velos/1/bearbeiten", data={"name": " ", "km_stand": "1000"})
    assert antwort.status_code == 400
    assert "darf nicht leer sein" in antwort.text
    assert velo(app)["name"] == "Gravel"


def test_unbekanntes_velo_gibt_404(client):
    assert client.get("/velos/99/bearbeiten").status_code == 404
    antwort = client.post("/velos/99/bearbeiten", data={"name": "X", "km_stand": "1"})
    assert antwort.status_code == 404


def test_bearbeiten_ohne_login_leitet_zum_login(anonym):
    antwort = anonym.post("/velos/1/bearbeiten", data={"name": "X", "km_stand": "1"})
    assert antwort.status_code == 302
    assert antwort.location.startswith("/login")

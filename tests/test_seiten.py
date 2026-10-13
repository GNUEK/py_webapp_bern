"""Tests der Seiten über den Flask-Testclient (mit echter Test-Datenbank)."""

from app.db import get_db
from conftest import erfasse_komponente, erfasse_velo


def velo(app, velo_id=1):
    with app.app_context():
        db = get_db()
        return db.execute("SELECT * FROM velo WHERE id = ?", (velo_id,)).fetchone()


def komponenten(app, aktiv=1):
    with app.app_context():
        return (
            get_db()
            .execute("SELECT * FROM komponente WHERE aktiv = ? ORDER BY id", (aktiv,))
            .fetchall()
        )


# M1 / M2 -----------------------------------------------------------------


def test_leere_uebersicht(client):
    antwort = client.get("/")
    assert antwort.status_code == 200
    assert "Noch keine Velos erfasst" in antwort.text


def test_velo_erfassen_und_in_uebersicht_sehen(client, app):
    antwort = erfasse_velo(client, name="Rennvelo", km_stand=5400)
    assert antwort.status_code == 302  # Weiterleitung auf die Detailseite

    assert velo(app)["km_stand"] == 5400
    uebersicht = client.get("/").text
    assert "Rennvelo" in uebersicht
    assert "5’400 km" in uebersicht


def test_velo_ohne_name_wird_abgelehnt(client, app):
    antwort = client.post("/velos/neu", data={"name": " ", "km_stand": "10"})
    assert antwort.status_code == 400
    assert "darf nicht leer sein" in antwort.text
    assert velo(app) is None


def test_negativer_kilometerstand_wird_abgelehnt(client, app):
    antwort = client.post("/velos/neu", data={"name": "X", "km_stand": "-5"})
    assert antwort.status_code == 400
    assert velo(app) is None


def test_standardkomponenten_werden_angelegt(client, app):
    erfasse_velo(client, km_stand=800, standardkomponenten=True)
    angelegt = komponenten(app)
    assert {k["kategorie"] for k in angelegt} >= {"Kette", "Bremsbeläge", "Service"}
    assert all(k["einbau_km"] == 800 for k in angelegt)


def test_uebersicht_zeigt_faellige_wartung(client):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, einbau_km="1000", intervall_km="3000")
    assert "fällig" not in client.get("/").text

    client.post("/velos/1/kilometer", data={"km_stand": "4100"})
    assert "1 fällig" in client.get("/").text


def test_unbekanntes_velo_gibt_404(client):
    assert client.get("/velos/99").status_code == 404


# K1: Kilometer und Wartung ------------------------------------------------


def test_kilometer_koennen_nicht_sinken(client, app):
    erfasse_velo(client, km_stand=1000)
    client.post("/velos/1/kilometer", data={"km_stand": "900"})
    assert velo(app)["km_stand"] == 1000


def test_wartung_setzt_zaehler_zurueck(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(
        client, einbau_km="1000", intervall_km="3000", checkliste="Reinigen\nÖlen"
    )
    client.post("/velos/1/kilometer", data={"km_stand": "4500"})

    antwort = client.post(
        "/komponenten/1/wartung",
        data={
            "datum": "2026-10-12",
            "km_stand": "4500",
            "erledigt": ["Ölen", "Erfunden"],
        },
    )
    assert antwort.status_code == 302

    komponente = komponenten(app)[0]
    assert komponente["letzte_wartung_km"] == 4500
    assert komponente["letzte_wartung_datum"] == "2026-10-12"
    with app.app_context():
        wartung = get_db().execute("SELECT * FROM wartung").fetchone()
    assert wartung["erledigt"] == "Ölen"  # Unbekannte Punkte werden ignoriert
    assert "1 fällig" not in client.get("/").text


def test_wartung_in_der_zukunft_wird_abgelehnt(client):
    erfasse_velo(client)
    erfasse_komponente(client)
    antwort = client.post(
        "/komponenten/1/wartung", data={"datum": "2030-01-01", "km_stand": "1000"}
    )
    assert antwort.status_code == 400


# K2 / K3: Komponenten -----------------------------------------------------


def test_zubehoer_ohne_intervall(client, app):
    erfasse_velo(client)
    erfasse_komponente(
        client,
        bezeichnung="Garmin Edge",
        kategorie="Zubehör",
        intervall_km="",
        intervall_tage="",
    )
    assert komponenten(app)[0]["intervall_km"] is None
    assert "kein Intervall" in client.get("/velos/1").text


def test_komponente_mit_ungueltiger_kategorie(client, app):
    erfasse_velo(client)
    antwort = erfasse_komponente(client, kategorie="Raketenantrieb")
    assert antwort.status_code == 400
    assert komponenten(app) == []


def test_anleitung_muss_weblink_sein(client, app):
    erfasse_velo(client)
    antwort = erfasse_komponente(client, anleitung_url="javascript:alert(1)")
    assert antwort.status_code == 400
    assert komponenten(app) == []


def test_komponente_tauschen(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, bezeichnung="Alte Kette", einbau_km="0")
    client.post("/velos/1/kilometer", data={"km_stand": "3200"})

    antwort = client.post(
        "/komponenten/1/tauschen",
        data={
            "bezeichnung": "Neue Kette",
            "kategorie": "Kette",
            "einbau_datum": "2026-10-12",
            "einbau_km": "3200",
            "intervall_km": "3000",
        },
    )
    assert antwort.status_code == 302

    alt = komponenten(app, aktiv=0)
    neu = komponenten(app, aktiv=1)
    assert [k["bezeichnung"] for k in alt] == ["Alte Kette"]
    assert alt[0]["ausbau_km"] == 3200
    assert [k["bezeichnung"] for k in neu] == ["Neue Kette"]
    assert neu[0]["letzte_wartung_km"] == 3200


def test_velo_loeschen_entfernt_komponenten(client, app):
    erfasse_velo(client)
    erfasse_komponente(client)
    client.post("/velos/1/loeschen")
    assert velo(app) is None
    assert komponenten(app) == []

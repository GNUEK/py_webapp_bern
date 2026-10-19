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


def bearbeite_komponente(client, komponente_id=1, **werte):
    daten = {
        "bezeichnung": "Kette",
        "kategorie": "Kette",
        "einbau_datum": "2026-01-01",
        "einbau_km": "1000",
        "intervall_km": "3000",
        "intervall_tage": "",
        **werte,
    }
    return client.post(f"/komponenten/{komponente_id}/bearbeiten", data=daten)


def test_komponente_bearbeiten(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, bezeichnung="Ketet", intervall_km="300")
    formular = client.get("/komponenten/1/bearbeiten").text
    assert 'value="Ketet"' in formular  # Formular ist vorausgefüllt

    antwort = bearbeite_komponente(
        client, bezeichnung="Kette", kategorie="Kassette", intervall_km="3000"
    )
    assert antwort.status_code == 302

    komponente = komponenten(app)[0]
    assert komponente["bezeichnung"] == "Kette"
    assert komponente["kategorie"] == "Kassette"
    assert komponente["intervall_km"] == 3000


def test_einbau_aendern_ohne_wartung_verschiebt_zaehlung(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, einbau_km="1000", einbau_datum="2026-05-01")

    bearbeite_komponente(client, einbau_km="200", einbau_datum="2026-02-01")

    komponente = komponenten(app)[0]
    assert komponente["einbau_km"] == 200
    assert komponente["letzte_wartung_km"] == 200
    assert komponente["letzte_wartung_datum"] == "2026-02-01"


def test_einbau_aendern_mit_wartung_behaelt_letzte_wartung(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, einbau_km="0")
    client.post(
        "/komponenten/1/wartung", data={"datum": "2026-06-01", "km_stand": "500"}
    )
    client.post(
        "/komponenten/1/wartung", data={"datum": "2026-10-01", "km_stand": "800"}
    )

    bearbeite_komponente(client, einbau_km="100")
    komponente = komponenten(app)[0]
    assert komponente["einbau_km"] == 100
    assert komponente["letzte_wartung_km"] == 800
    assert komponente["letzte_wartung_datum"] == "2026-10-01"

    # Einbau nach der ersten Wartung ist nicht möglich
    antwort = bearbeite_komponente(client, einbau_km="700")
    assert antwort.status_code == 400
    antwort = bearbeite_komponente(client, einbau_datum="2026-07-01")
    assert antwort.status_code == 400
    assert komponenten(app)[0]["einbau_km"] == 100


def test_ungueltige_bearbeitung_aendert_nichts(client, app):
    erfasse_velo(client, km_stand=1000)
    erfasse_komponente(client, bezeichnung="Kette")
    antwort = bearbeite_komponente(client, bezeichnung=" ", einbau_km="5000")
    assert antwort.status_code == 400
    assert komponenten(app)[0]["bezeichnung"] == "Kette"


def test_ausgebaute_komponente_nicht_bearbeitbar(client, app):
    erfasse_velo(client)
    erfasse_komponente(client, bezeichnung="Kette")
    client.post("/komponenten/1/ausbauen")

    antwort = bearbeite_komponente(client, bezeichnung="Neu")
    assert antwort.status_code == 302
    assert komponenten(app, aktiv=0)[0]["bezeichnung"] == "Kette"


def test_velo_loeschen_entfernt_komponenten(client, app):
    erfasse_velo(client)
    erfasse_komponente(client)
    client.post("/velos/1/loeschen")
    assert velo(app) is None
    assert komponenten(app) == []


# Issue #6: Modellnr. ---------------------------------------------------------


def test_modellnr_erfassen_anzeigen_und_beim_tauschen_vorschlagen(client):
    erfasse_velo(client)
    erfasse_komponente(client, modell="Shimano CN-HG701-11")
    assert "Modellnr. Shimano CN-HG701-11" in client.get("/velos/1").text
    assert "Shimano CN-HG701-11" in client.get("/komponenten/1/tauschen").text


def test_alte_datenbank_bekommt_spalte_modell(tmp_path):
    import sqlite3

    from app.db import init_db

    pfad = str(tmp_path / "alt.db")
    with sqlite3.connect(pfad) as alt:
        alt.execute("CREATE TABLE komponente (id INTEGER PRIMARY KEY)")
    init_db(pfad)
    with sqlite3.connect(pfad) as neu:
        spalten = [s[1] for s in neu.execute("PRAGMA table_info(komponente)")]
    assert "modell" in spalten

"""Gemeinsame Test-Hilfen (pytest "Fixtures").

Jeder Test bekommt eine eigene, leere Datenbank in einem temporären Ordner.
Das heutige Datum ist fest auf den 12.10.2026 gesetzt, damit Tests mit
Datumsberechnungen jeden Tag gleich laufen.

Der Fixture ``client`` ist bereits angemeldet, ``anonym`` nicht.
"""

from datetime import date

import pytest

from app import create_app
from app.auth import PASSWORT

HEUTE = date(2026, 10, 12)


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "HEUTE": HEUTE,
            "STRAVA_CLIENT_ID": None,
            "STRAVA_CLIENT_SECRET": None,
        }
    )


@pytest.fixture
def anonym(app):
    """Testclient ohne Anmeldung."""
    return app.test_client()


@pytest.fixture
def client(app):
    """Testclient, der bereits angemeldet ist."""
    angemeldet = app.test_client()
    melde_an(angemeldet)
    return angemeldet


def melde_an(client, passwort=PASSWORT, next=None):
    daten = {"passwort": passwort}
    if next:
        daten["next"] = next
    return client.post("/login", data=daten)


def erfasse_velo(client, name="Gravel", km_stand=1000, standardkomponenten=False):
    daten = {"name": name, "km_stand": str(km_stand)}
    if standardkomponenten:
        daten["standardkomponenten"] = "1"
    return client.post("/velos/neu", data=daten)


def erfasse_komponente(client, velo_id=1, **werte):
    daten = {
        "bezeichnung": "Kette",
        "kategorie": "Kette",
        "einbau_datum": "2026-01-01",
        "einbau_km": "1000",
        "intervall_km": "3000",
        "intervall_tage": "",
        **werte,
    }
    return client.post(f"/velos/{velo_id}/komponenten/neu", data=daten)

"""Gemeinsame Test-Hilfen (pytest "Fixtures").

Jeder Test bekommt eine eigene, leere Datenbank in einem temporären Ordner.
Das heutige Datum ist fest auf den 12.10.2026 gesetzt, damit Tests mit
Datumsberechnungen jeden Tag gleich laufen.

Der Fixture ``client`` ist bereits angemeldet, ``anonym`` nicht.
"""

from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db

HEUTE = date(2026, 10, 12)

BENUTZER = "test"
PASSWORT = "test-passwort"
# Echte Hashes sind absichtlich langsam. Für Tests genügt ein schneller,
# einmal berechneter Hash (nur in Tests so verwenden!).
PASSWORT_HASH = generate_password_hash(PASSWORT, method="pbkdf2:sha256:1000")


@pytest.fixture
def app(tmp_path):
    test_app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "HEUTE": HEUTE,
            "STRAVA_CLIENT_ID": None,
            "STRAVA_CLIENT_SECRET": None,
        }
    )
    # Ein Testbenutzer, so wie man ihn sonst per DB-Tool einträgt
    with test_app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO benutzer (name, passwort_hash) VALUES (?, ?)",
            (BENUTZER, PASSWORT_HASH),
        )
        db.commit()
    return test_app


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


def melde_an(client, name=BENUTZER, passwort=PASSWORT, next=None):
    daten = {"name": name, "passwort": passwort}
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

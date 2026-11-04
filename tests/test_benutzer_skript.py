"""Tests für tools/benutzer_setzen.py (so aufgerufen wie auf Azure)."""

import os
import subprocess
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

from conftest import melde_an

SKRIPT = Path(__file__).resolve().parents[1] / "tools" / "benutzer_setzen.py"


def starte_skript(app, *argumente):
    umgebung = {**os.environ, "DATABASE_PATH": app.config["DATABASE"]}
    return subprocess.run(
        [sys.executable, str(SKRIPT), *argumente],
        env=umgebung,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def schneller_hash(passwort):
    return generate_password_hash(passwort, method="pbkdf2:sha256:1000")


def test_benutzer_anlegen_und_anmelden(app, anonym):
    ergebnis = starte_skript(app, "neu", schneller_hash("geheim"))
    assert ergebnis.returncode == 0
    assert melde_an(anonym, name="neu", passwort="geheim").status_code == 302


def test_passwort_aendern(app, anonym):
    # Der Testbenutzer "test" existiert schon und bekommt ein neues Passwort
    assert starte_skript(app, "test", schneller_hash("neues-pw")).returncode == 0
    assert melde_an(anonym, name="test", passwort="neues-pw").status_code == 302


def test_passwort_statt_hash_wird_abgelehnt(app):
    ergebnis = starte_skript(app, "neu", "geheim")
    assert ergebnis.returncode == 1
    assert "kein Hash" in ergebnis.stdout

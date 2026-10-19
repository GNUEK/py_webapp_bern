"""Zugriff auf die SQLite-Datenbank.

Pro Anfrage wird eine Verbindung geöffnet und am Ende wieder geschlossen.
Flask merkt sich die Verbindung im Objekt ``g`` (gilt nur für eine Anfrage).
"""

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    """Gibt die Datenbankverbindung der aktuellen Anfrage zurück."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Zeilen verhalten sich wie Dictionaries: zeile["name"]
        g.db.row_factory = sqlite3.Row
        # SQLite prüft Fremdschlüssel nur, wenn man es einschaltet.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exception=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(database_path: str) -> None:
    """Legt die Datenbankdatei und alle Tabellen an, falls sie fehlen."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        # Ältere Datenbanken haben die Spalte "modell" noch nicht (Issue #6).
        # CREATE TABLE IF NOT EXISTS ergänzt keine Spalten, darum von Hand.
        spalten = [s[1] for s in connection.execute("PRAGMA table_info(komponente)")]
        if "modell" not in spalten:
            connection.execute("ALTER TABLE komponente ADD COLUMN modell TEXT")

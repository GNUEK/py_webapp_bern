"""Legt einen Benutzer an oder ändert sein Passwort (lokal und auf Azure).

Aufruf:
    python3 tools/benutzer_setzen.py NAME 'HASH'

Den HASH erzeugt man vorher lokal mit
``uv run flask --app src/app passwort-hash``. In einfachen Anführungszeichen
übergeben, weil der Hash $-Zeichen enthält.

Das Skript braucht nur die Python-Standardbibliothek. Darum läuft es auch in
der SSH-Konsole von Azure, wo die Pakete der App nicht direkt verfügbar sind.
Welche Datenbank es verwendet, bestimmt wie bei der App ``DATABASE_PATH``.
"""

import os
import sqlite3
import sys
from pathlib import Path

STANDARD_DB = Path(__file__).resolve().parents[1] / "instance" / "velo.db"


def benutzer_setzen(pfad: str, name: str, passwort_hash: str) -> None:
    with sqlite3.connect(pfad) as db:
        # Neuer Name: anlegen. Bestehender Name: nur den Hash ersetzen.
        db.execute(
            """INSERT INTO benutzer (name, passwort_hash) VALUES (?, ?)
               ON CONFLICT (name) DO UPDATE
               SET passwort_hash = excluded.passwort_hash""",
            (name, passwort_hash),
        )
    db.close()


def main(argumente: list[str]) -> int:
    if len(argumente) != 2:
        print("Aufruf: python3 tools/benutzer_setzen.py NAME 'HASH'")
        return 1
    name, passwort_hash = argumente
    # Schützt davor, aus Versehen das Passwort statt des Hashs einzutragen
    if not passwort_hash.startswith(("scrypt:", "pbkdf2:")):
        print("Das ist kein Hash. Zuerst 'flask passwort-hash' ausführen.")
        return 1

    pfad = os.environ.get("DATABASE_PATH", str(STANDARD_DB))
    print("Datenbank:", pfad)
    if not Path(pfad).exists():
        print("Datei nicht gefunden. Die App einmal starten oder DATABASE_PATH prüfen.")
        return 1

    benutzer_setzen(pfad, name, passwort_hash)
    print(f"Benutzer «{name}» gespeichert.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

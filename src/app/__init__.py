"""Velo-Wartungslogbuch: Einstiegspunkt der Flask-Applikation.

Gunicorn startet die App mit ``app:app``: Modul ``app`` (dieser Ordner),
Objekt ``app`` (unten in dieser Datei).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from . import auth, db, strava, views

PROJEKT_ORDNER = Path(__file__).resolve().parents[2]


def create_app(test_config: dict | None = None) -> Flask:
    """Erstellt und konfiguriert die Flask-App.

    Tests übergeben ``test_config``, um z.B. eine eigene Datenbank zu nutzen.
    """
    load_dotenv()  # liest eine lokale .env-Datei, falls vorhanden

    flask_app = Flask(__name__)
    flask_app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "nur-fuer-lokale-entwicklung"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(PROJEKT_ORDNER / "instance" / "velo.db")
        ),
        STRAVA_CLIENT_ID=os.environ.get("STRAVA_CLIENT_ID"),
        STRAVA_CLIENT_SECRET=os.environ.get("STRAVA_CLIENT_SECRET"),
    )
    if test_config:
        flask_app.config.update(test_config)

    # Azure leitet Anfragen über einen Proxy weiter. Ohne ProxyFix würde
    # Flask glauben, die Seite laufe über http statt https.
    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_proto=1, x_host=1)

    db.init_db(flask_app.config["DATABASE"])
    flask_app.teardown_appcontext(db.close_db)

    # Zentrale Login-Prüfung vor jeder Anfrage, für alle Seiten
    flask_app.before_request(auth.login_erzwingen)

    flask_app.register_blueprint(auth.bp)
    flask_app.register_blueprint(views.bp)
    flask_app.register_blueprint(strava.bp)

    @flask_app.template_filter("km")
    def km_format(wert) -> str:
        """Schweizer Schreibweise mit Apostroph: 12345 -> 12’345"""
        return f"{int(wert):,}".replace(",", "’")

    @flask_app.context_processor
    def strava_konfiguriert():
        return {"strava_aktiv": strava.ist_konfiguriert()}

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

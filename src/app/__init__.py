"""Velo-Wartungslogbuch: Einstiegspunkt der Flask-Applikation.

Gunicorn startet die App mit ``app:app``: Modul ``app`` (dieser Ordner),
Objekt ``app`` (unten in dieser Datei).
"""

import os
import secrets
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
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(PROJEKT_ORDNER / "instance" / "velo.db")
        ),
        STRAVA_CLIENT_ID=os.environ.get("STRAVA_CLIENT_ID"),
        STRAVA_CLIENT_SECRET=os.environ.get("STRAVA_CLIENT_SECRET"),
        # Session-Cookie absichern (Entscheid 0011):
        # Lax: Eine fremde Seite kann keine POST-Anfrage mit unserem Cookie
        # abschicken (einfacher Schutz gegen CSRF).
        SESSION_COOKIE_SAMESITE="Lax",
        # Secure: Cookie nur über https senden. Nur auf Azure, das die
        # Variable WEBSITE_HOSTNAME immer setzt. Lokal läuft die App über http.
        SESSION_COOKIE_SECURE="WEBSITE_HOSTNAME" in os.environ,
    )
    if test_config:
        flask_app.config.update(test_config)

    if not flask_app.config["SECRET_KEY"]:
        # Ein fester Ersatzwert stünde öffentlich im Repository. Damit könnte
        # jeder ein gültiges Session-Cookie fälschen und wäre "angemeldet".
        # Ein Zufallswert ist sicher, gilt aber nur bis zum nächsten Neustart:
        # Danach sind alle abgemeldet.
        flask_app.config["SECRET_KEY"] = secrets.token_hex(32)
        flask_app.logger.warning(
            "SECRET_KEY ist nicht gesetzt: Zufallswert verwendet. "
            "Nach jedem Neustart sind alle abgemeldet."
        )

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


# Das Objekt, das Gunicorn mit "app:app" startet. Die Zeile läuft bei jedem
# Import dieses Moduls, also auch in den Tests: Dabei wird die normale
# Datenbank (instance/velo.db) angelegt, falls sie fehlt. Die Tests selbst
# arbeiten mit create_app() und einer eigenen, leeren Datenbank.
app = create_app()

"""Login mit Benutzername und Passwort aus der Tabelle ``benutzer``.

Neue Benutzer legt man mit ``tools/benutzer_setzen.py`` an (siehe README).
In der Tabelle steht nur der Hash des Passworts. Den Hash erzeugt der Befehl
``uv run flask --app src/app passwort-hash``.

Alle angemeldeten Benutzer sehen dieselben Daten. Nach der Anmeldung merkt
sich Flask in der Session den Namen des Benutzers.

Die Prüfung läuft im Backend vor jeder Anfrage (``login_erzwingen``), nicht
in den einzelnen Seiten. So kann eine neue Seite nicht vergessen werden.
"""

import click
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

# cli_group=None: der Befehl heisst "flask passwort-hash", nicht "flask auth ..."
bp = Blueprint("auth", __name__, cli_group=None)

# Endpunkte, die man ohne Anmeldung aufrufen darf
OHNE_LOGIN = {"auth.login", "static"}


def login_erzwingen():
    """Läuft vor jeder Anfrage. Leitet nicht angemeldete Besucher zum Login."""
    if request.endpoint in OHNE_LOGIN or session.get("benutzer"):
        return None  # Anfrage normal weiterverarbeiten
    # Nach dem Login zurück auf die ursprünglich gewünschte Seite
    ziel = request.full_path if request.query_string else request.path
    return redirect(url_for("auth.login", next=ziel))


def sicheres_ziel(ziel: str | None) -> str:
    """Erlaubt nur Weiterleitungen innerhalb der App.

    Sonst könnte ein präparierter Link wie ``/login?next=https://boese.example``
    nach dem Login auf eine fremde Seite führen ("Open Redirect").
    """
    # Nur Pfade wie "/velos/1". "//..." und "/\..." lesen Browser als fremde Seite.
    if ziel and ziel.startswith("/") and not ziel.startswith(("//", "/\\")):
        return ziel
    return url_for("velos.uebersicht")


def passwort_stimmt(name: str, passwort: str) -> bool:
    benutzer = (
        get_db()
        .execute("SELECT passwort_hash FROM benutzer WHERE name = ?", (name,))
        .fetchone()
    )
    if benutzer is None:
        return False
    try:
        return check_password_hash(benutzer["passwort_hash"], passwort)
    except ValueError:
        # Kein gültiger Hash, z.B. von Hand in die Datenbank eingetragen
        return False


@bp.route("/login", methods=["GET", "POST"])
def login():
    ziel = sicheres_ziel(request.values.get("next"))
    if request.method == "GET":
        if session.get("benutzer"):
            return redirect(ziel)
        return render_template("login.html", ziel=ziel)

    name = request.form.get("name", "").strip()
    if not passwort_stimmt(name, request.form.get("passwort", "")):
        # Bewusst eine Meldung für beide Fälle: kein Hinweis, was falsch war
        flash("Benutzername oder Passwort ist falsch.", "danger")
        return render_template("login.html", ziel=ziel, name=name), 401

    session.clear()  # alte Session-Daten verwerfen, neu beginnen
    session["benutzer"] = name
    return redirect(ziel)


@bp.post("/logout")
def logout():
    session.clear()
    flash("Du bist abgemeldet.", "success")
    return redirect(url_for("auth.login"))


@bp.cli.command("passwort-hash")
def passwort_hash():
    """Fragt ein Passwort ab und gibt den Hash für die Tabelle benutzer aus."""
    passwort = click.prompt("Passwort", hide_input=True, confirmation_prompt=True)
    click.echo(generate_password_hash(passwort))

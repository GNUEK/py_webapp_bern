"""Login: Wer das Passwort kennt, darf die App benutzen.

Es gibt keine Benutzerkonten, nur ein gemeinsames Passwort. Nach der
Anmeldung merkt sich Flask in der Session ``angemeldet = True``.

Die Prüfung läuft im Backend vor jeder Anfrage (``login_erzwingen``), nicht
in den einzelnen Seiten. So kann eine neue Seite nicht vergessen werden.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

bp = Blueprint("auth", __name__)

# Bewusst einfach gehalten und öffentlich im Repository (siehe Entscheid 0006)
PASSWORT = "Velo26"

# Endpunkte, die man ohne Anmeldung aufrufen darf
OHNE_LOGIN = {"auth.login", "static"}


def login_erzwingen():
    """Läuft vor jeder Anfrage. Leitet nicht angemeldete Besucher zum Login."""
    if request.endpoint in OHNE_LOGIN or session.get("angemeldet"):
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


@bp.route("/login", methods=["GET", "POST"])
def login():
    ziel = sicheres_ziel(request.values.get("next"))
    if request.method == "GET":
        if session.get("angemeldet"):
            return redirect(ziel)
        return render_template("login.html", ziel=ziel)

    if request.form.get("passwort") != PASSWORT:
        flash("Falsches Passwort.", "danger")
        return render_template("login.html", ziel=ziel), 401

    session.clear()  # alte Session-Daten verwerfen, neu beginnen
    session["angemeldet"] = True
    return redirect(ziel)


@bp.post("/logout")
def logout():
    session.clear()
    flash("Du bist abgemeldet.", "success")
    return redirect(url_for("auth.login"))

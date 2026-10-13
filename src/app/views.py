"""Seiten und Operationen der Applikation.

Jede Funktion mit ``@bp.route`` beantwortet eine URL. GET-Anfragen zeigen
eine Seite an, POST-Anfragen verändern Daten und leiten danach weiter
(Muster "Post/Redirect/Get", damit ein Neuladen nichts doppelt speichert).
"""

from datetime import date

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import formulare as f
from .db import get_db
from .vorlagen import STANDARDKOMPONENTEN
from .wartung import berechne_faelligkeit, schlimmster_status

bp = Blueprint("velos", __name__)


def heute() -> date:
    """Heutiges Datum. Tests können es über die Konfiguration festlegen."""
    return current_app.config.get("HEUTE") or date.today()


# --------------------------------------------------------------------------
# Hilfsfunktionen für die Datenbank
# --------------------------------------------------------------------------


def lade_velo(velo_id: int):
    velo = get_db().execute("SELECT * FROM velo WHERE id = ?", (velo_id,)).fetchone()
    if velo is None:
        abort(404)
    return velo


def lade_komponente(komponente_id: int):
    komponente = (
        get_db()
        .execute("SELECT * FROM komponente WHERE id = ?", (komponente_id,))
        .fetchone()
    )
    if komponente is None:
        abort(404)
    return komponente


def faelligkeit_von(komponente, km_stand: int):
    return berechne_faelligkeit(
        km_stand=km_stand,
        letzte_wartung_km=komponente["letzte_wartung_km"],
        letzte_wartung_datum=date.fromisoformat(komponente["letzte_wartung_datum"]),
        intervall_km=komponente["intervall_km"],
        intervall_tage=komponente["intervall_tage"],
        heute=heute(),
    )


def aktive_komponenten_mit_status(velo):
    zeilen = (
        get_db()
        .execute(
            "SELECT * FROM komponente WHERE velo_id = ? AND aktiv = 1"
            " ORDER BY kategorie, bezeichnung",
            (velo["id"],),
        )
        .fetchall()
    )
    return [(k, faelligkeit_von(k, velo["km_stand"])) for k in zeilen]


def speichere_komponente(velo_id: int, daten: dict) -> int:
    cursor = get_db().execute(
        """INSERT INTO komponente (
               velo_id, bezeichnung, kategorie, einbau_datum, einbau_km,
               intervall_km, intervall_tage, letzte_wartung_datum,
               letzte_wartung_km, anleitung_url, checkliste)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            velo_id,
            daten["bezeichnung"],
            daten["kategorie"],
            daten["einbau_datum"],
            daten["einbau_km"],
            daten["intervall_km"],
            daten["intervall_tage"],
            daten["einbau_datum"],  # Zählung beginnt beim Einbau
            daten["einbau_km"],
            daten["anleitung_url"],
            daten["checkliste"],
        ),
    )
    return cursor.lastrowid


# --------------------------------------------------------------------------
# Velos
# --------------------------------------------------------------------------


@bp.get("/")
def uebersicht():
    """M2: Übersicht aller Velos mit Wartungsstatus."""
    velos = get_db().execute("SELECT * FROM velo ORDER BY name").fetchall()
    eintraege = []
    for velo in velos:
        komponenten = aktive_komponenten_mit_status(velo)
        status = [faelligkeit.status for _, faelligkeit in komponenten]
        eintraege.append(
            {
                "velo": velo,
                "status": schlimmster_status(status),
                "anzahl_faellig": status.count("faellig"),
                "anzahl_bald": status.count("bald"),
                "anzahl_komponenten": len(komponenten),
            }
        )
    return render_template("uebersicht.html", eintraege=eintraege)


def velo_aus_formular(fehler: f.Fehlerliste) -> dict:
    form = request.form
    return {
        "name": f.text(form, "name", fehler, pflicht=True),
        "typ": f.text(form, "typ", fehler),
        "rahmennummer": f.text(form, "rahmennummer", fehler),
        "groesse": f.text(form, "groesse", fehler, max_laenge=20),
        "gewicht_kg": f.dezimalzahl(form, "gewicht_kg", fehler),
        "preis_chf": f.dezimalzahl(form, "preis_chf", fehler),
        "km_stand": f.ganzzahl(form, "km_stand", fehler, pflicht=True),
    }


@bp.route("/velos/neu", methods=["GET", "POST"])
def velo_neu():
    """M1: Velo erfassen und speichern."""
    if request.method == "GET":
        return render_template("velo_formular.html", velo={"km_stand": 0}, neu=True)

    fehler = f.Fehlerliste()
    daten = velo_aus_formular(fehler)
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return render_template("velo_formular.html", velo=request.form, neu=True), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO velo (name, typ, rahmennummer, groesse, gewicht_kg,
                             preis_chf, km_stand)
           VALUES (:name, :typ, :rahmennummer, :groesse, :gewicht_kg,
                   :preis_chf, :km_stand)""",
        daten,
    )
    velo_id = cursor.lastrowid

    if request.form.get("standardkomponenten"):
        for vorlage in STANDARDKOMPONENTEN:
            speichere_komponente(
                velo_id,
                {
                    **vorlage,
                    "einbau_datum": heute().isoformat(),
                    "einbau_km": daten["km_stand"],
                },
            )
    db.commit()
    flash(f"Velo «{daten['name']}» gespeichert.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo_id))


@bp.get("/velos/<int:velo_id>")
def velo_detail(velo_id: int):
    velo = lade_velo(velo_id)
    db = get_db()
    ausgebaut = db.execute(
        "SELECT * FROM komponente WHERE velo_id = ? AND aktiv = 0"
        " ORDER BY ausbau_datum DESC",
        (velo_id,),
    ).fetchall()
    wartungen = db.execute(
        """SELECT wartung.*, komponente.bezeichnung
           FROM wartung JOIN komponente ON komponente.id = wartung.komponente_id
           WHERE komponente.velo_id = ?
           ORDER BY wartung.datum DESC, wartung.id DESC""",
        (velo_id,),
    ).fetchall()
    return render_template(
        "velo_detail.html",
        velo=velo,
        komponenten=aktive_komponenten_mit_status(velo),
        ausgebaut=ausgebaut,
        wartungen=wartungen,
    )


@bp.route("/velos/<int:velo_id>/bearbeiten", methods=["GET", "POST"])
def velo_bearbeiten(velo_id: int):
    velo = lade_velo(velo_id)
    if request.method == "GET":
        return render_template("velo_formular.html", velo=velo, neu=False)

    fehler = f.Fehlerliste()
    daten = velo_aus_formular(fehler)
    if daten["km_stand"] is not None and daten["km_stand"] < velo["km_stand"]:
        fehler.append("Der Kilometerstand kann nicht kleiner werden.")
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return (
            render_template(
                "velo_formular.html", velo={**request.form, "id": velo_id}, neu=False
            ),
            400,
        )

    db = get_db()
    db.execute(
        """UPDATE velo SET name = :name, typ = :typ, rahmennummer = :rahmennummer,
                  groesse = :groesse, gewicht_kg = :gewicht_kg,
                  preis_chf = :preis_chf, km_stand = :km_stand
           WHERE id = :id""",
        {**daten, "id": velo_id},
    )
    db.commit()
    flash("Änderungen gespeichert.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo_id))


@bp.post("/velos/<int:velo_id>/loeschen")
def velo_loeschen(velo_id: int):
    velo = lade_velo(velo_id)
    db = get_db()
    db.execute("DELETE FROM velo WHERE id = ?", (velo_id,))
    db.commit()
    flash(f"Velo «{velo['name']}» gelöscht.", "success")
    return redirect(url_for("velos.uebersicht"))


@bp.post("/velos/<int:velo_id>/kilometer")
def kilometer_nachfuehren(velo_id: int):
    """K1: Neuen Kilometerstand eintragen."""
    velo = lade_velo(velo_id)
    fehler = f.Fehlerliste()
    neu = f.ganzzahl(request.form, "km_stand", fehler, pflicht=True)
    if neu is not None and neu < velo["km_stand"]:
        fehler.append(
            f"Der neue Kilometerstand ({neu}) ist kleiner als der bisherige "
            f"({velo['km_stand']})."
        )
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
    else:
        db = get_db()
        db.execute("UPDATE velo SET km_stand = ? WHERE id = ?", (neu, velo_id))
        db.commit()
        flash(f"Kilometerstand auf {neu} km gesetzt.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo_id))


# --------------------------------------------------------------------------
# Komponenten
# --------------------------------------------------------------------------


def komponente_aus_formular(fehler: f.Fehlerliste, velo) -> dict:
    form = request.form
    daten = {
        "bezeichnung": f.text(form, "bezeichnung", fehler, pflicht=True),
        "kategorie": f.kategorie(form, fehler),
        "einbau_datum": f.datum(form, "einbau_datum", fehler, heute()),
        "einbau_km": f.ganzzahl(form, "einbau_km", fehler, pflicht=True),
        "intervall_km": f.ganzzahl(form, "intervall_km", fehler, minimum=1),
        "intervall_tage": f.ganzzahl(form, "intervall_tage", fehler, minimum=1),
        "anleitung_url": f.url(form, "anleitung_url", fehler),
        "checkliste": f.text(form, "checkliste", fehler, max_laenge=1000),
    }
    if daten["einbau_km"] is not None and daten["einbau_km"] > velo["km_stand"]:
        fehler.append("Der Kilometerstand beim Einbau ist grösser als der aktuelle.")
    if daten["einbau_datum"]:
        daten["einbau_datum"] = daten["einbau_datum"].isoformat()
    return daten


def komponente_formular_anzeigen(velo, komponente, modus, alt=None, status=200):
    return (
        render_template(
            "komponente_formular.html",
            velo=velo,
            komponente=komponente,
            kategorien=f.KATEGORIEN,
            modus=modus,
            alt=alt,
        ),
        status,
    )


@bp.route("/velos/<int:velo_id>/komponenten/neu", methods=["GET", "POST"])
def komponente_neu(velo_id: int):
    """K2/K3: Komponente ergänzen (z.B. Kette, Flaschenhalter, Garmin)."""
    velo = lade_velo(velo_id)
    if request.method == "GET":
        vorschlag = {
            "einbau_datum": heute().isoformat(),
            "einbau_km": velo["km_stand"],
        }
        return komponente_formular_anzeigen(velo, vorschlag, "neu")

    fehler = f.Fehlerliste()
    daten = komponente_aus_formular(fehler, velo)
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return komponente_formular_anzeigen(velo, request.form, "neu", status=400)

    speichere_komponente(velo_id, daten)
    get_db().commit()
    flash(f"Komponente «{daten['bezeichnung']}» hinzugefügt.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo_id))


@bp.route("/komponenten/<int:komponente_id>/tauschen", methods=["GET", "POST"])
def komponente_tauschen(komponente_id: int):
    """K3: Alte Komponente ausbauen und eine neue an ihrer Stelle einbauen."""
    alt = lade_komponente(komponente_id)
    velo = lade_velo(alt["velo_id"])
    if not alt["aktiv"]:
        flash("Diese Komponente ist bereits ausgebaut.", "warning")
        return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))

    if request.method == "GET":
        # Neue Komponente übernimmt Kategorie, Intervalle und Anleitung
        vorschlag = {
            **dict(alt),
            "einbau_datum": heute().isoformat(),
            "einbau_km": velo["km_stand"],
        }
        return komponente_formular_anzeigen(velo, vorschlag, "tauschen", alt=alt)

    fehler = f.Fehlerliste()
    daten = komponente_aus_formular(fehler, velo)
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return komponente_formular_anzeigen(
            velo, request.form, "tauschen", alt=alt, status=400
        )

    db = get_db()
    db.execute(
        "UPDATE komponente SET aktiv = 0, ausbau_datum = ?, ausbau_km = ?"
        " WHERE id = ?",
        (daten["einbau_datum"], daten["einbau_km"], komponente_id),
    )
    speichere_komponente(velo["id"], daten)
    db.commit()
    flash(f"«{alt['bezeichnung']}» ersetzt durch «{daten['bezeichnung']}».", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))


@bp.route("/komponenten/<int:komponente_id>/bearbeiten", methods=["GET", "POST"])
def komponente_bearbeiten(komponente_id: int):
    """Angaben einer aktiven Komponente korrigieren, z.B. nach einem Tippfehler."""
    komponente = lade_komponente(komponente_id)
    velo = lade_velo(komponente["velo_id"])
    if not komponente["aktiv"]:
        flash("Ausgebaute Komponenten können nicht bearbeitet werden.", "warning")
        return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))

    if request.method == "GET":
        return komponente_formular_anzeigen(velo, komponente, "bearbeiten")

    db = get_db()
    erste_wartung = db.execute(
        "SELECT MIN(km_stand) AS km, MIN(datum) AS datum FROM wartung"
        " WHERE komponente_id = ?",
        (komponente_id,),
    ).fetchone()
    hat_wartungen = erste_wartung["km"] is not None

    fehler = f.Fehlerliste()
    daten = komponente_aus_formular(fehler, velo)
    # Der Einbau muss vor der ersten erfassten Wartung liegen
    if hat_wartungen:
        if daten["einbau_km"] is not None and daten["einbau_km"] > erste_wartung["km"]:
            fehler.append(
                "Der Kilometerstand beim Einbau ist grösser als bei der "
                "ersten Wartung."
            )
        if daten["einbau_datum"] and daten["einbau_datum"] > erste_wartung["datum"]:
            fehler.append("Das Einbaudatum liegt nach der ersten Wartung.")
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return komponente_formular_anzeigen(
            velo, request.form, "bearbeiten", status=400
        )

    # Ohne Wartung beginnt die Zählung beim Einbau und wandert mit ihm mit
    if hat_wartungen:
        letzte_wartung_datum = komponente["letzte_wartung_datum"]
        letzte_wartung_km = komponente["letzte_wartung_km"]
    else:
        letzte_wartung_datum = daten["einbau_datum"]
        letzte_wartung_km = daten["einbau_km"]

    db.execute(
        """UPDATE komponente SET
               bezeichnung = ?, kategorie = ?, einbau_datum = ?, einbau_km = ?,
               intervall_km = ?, intervall_tage = ?, letzte_wartung_datum = ?,
               letzte_wartung_km = ?, anleitung_url = ?, checkliste = ?
           WHERE id = ?""",
        (
            daten["bezeichnung"],
            daten["kategorie"],
            daten["einbau_datum"],
            daten["einbau_km"],
            daten["intervall_km"],
            daten["intervall_tage"],
            letzte_wartung_datum,
            letzte_wartung_km,
            daten["anleitung_url"],
            daten["checkliste"],
            komponente_id,
        ),
    )
    db.commit()
    flash(f"Komponente «{daten['bezeichnung']}» gespeichert.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))


@bp.post("/komponenten/<int:komponente_id>/ausbauen")
def komponente_ausbauen(komponente_id: int):
    """Komponente ohne Ersatz entfernen. Sie bleibt im Verlauf sichtbar."""
    komponente = lade_komponente(komponente_id)
    velo = lade_velo(komponente["velo_id"])
    db = get_db()
    db.execute(
        "UPDATE komponente SET aktiv = 0, ausbau_datum = ?, ausbau_km = ?"
        " WHERE id = ?",
        (heute().isoformat(), velo["km_stand"], komponente_id),
    )
    db.commit()
    flash(f"«{komponente['bezeichnung']}» ausgebaut.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))


# --------------------------------------------------------------------------
# Wartung
# --------------------------------------------------------------------------


@bp.route("/komponenten/<int:komponente_id>/wartung", methods=["GET", "POST"])
def wartung_erfassen(komponente_id: int):
    """K1/K5: Wartung als erledigt markieren, mit Checkliste."""
    komponente = lade_komponente(komponente_id)
    velo = lade_velo(komponente["velo_id"])
    checkliste = [
        punkt.strip()
        for punkt in (komponente["checkliste"] or "").splitlines()
        if punkt.strip()
    ]

    def formular(werte, status=200):
        return (
            render_template(
                "wartung_formular.html",
                velo=velo,
                komponente=komponente,
                checkliste=checkliste,
                werte=werte,
            ),
            status,
        )

    if request.method == "GET":
        return formular({"datum": heute().isoformat(), "km_stand": velo["km_stand"]})

    fehler = f.Fehlerliste()
    datum = f.datum(request.form, "datum", fehler, heute())
    km = f.ganzzahl(request.form, "km_stand", fehler, pflicht=True)
    notiz = f.text(request.form, "notiz", fehler, max_laenge=500)
    if km is not None and km > velo["km_stand"]:
        fehler.append("Der Kilometerstand ist grösser als der des Velos.")
    if km is not None and km < komponente["letzte_wartung_km"]:
        fehler.append("Der Kilometerstand liegt vor der letzten Wartung.")
    if fehler:
        for meldung in fehler:
            flash(meldung, "danger")
        return formular(request.form, status=400)

    # Nur Punkte übernehmen, die wirklich auf der Checkliste stehen
    erledigt = [p for p in request.form.getlist("erledigt") if p in checkliste]

    db = get_db()
    db.execute(
        "INSERT INTO wartung (komponente_id, datum, km_stand, notiz, erledigt)"
        " VALUES (?, ?, ?, ?, ?)",
        (komponente_id, datum.isoformat(), km, notiz, "\n".join(erledigt) or None),
    )
    db.execute(
        "UPDATE komponente SET letzte_wartung_datum = ?, letzte_wartung_km = ?"
        " WHERE id = ?",
        (datum.isoformat(), km, komponente_id),
    )
    db.commit()
    flash(f"Wartung von «{komponente['bezeichnung']}» erfasst.", "success")
    return redirect(url_for("velos.velo_detail", velo_id=velo["id"]))

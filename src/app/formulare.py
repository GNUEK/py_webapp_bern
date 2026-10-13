"""Prüfen von Formulareingaben im Backend.

Das HTML-Formular prüft einige Felder bereits im Browser (z.B. ``required``).
Das ist nur Komfort: Jede Eingabe wird hier noch einmal geprüft, weil man
den Browser umgehen kann.
"""

from datetime import date
from urllib.parse import urlparse

KATEGORIEN = [
    "Kette",
    "Kassette",
    "Kettenblatt",
    "Bremsbeläge",
    "Bremsscheibe",
    "Reifen vorne",
    "Reifen hinten",
    "Schlauch / Dichtmilch",
    "Federgabel",
    "Dämpfer",
    "Lager",
    "Schaltzug / Bremszug",
    "Service",
    "Zubehör",
    "Andere",
]


# Lesbare Namen der Formularfelder für Fehlermeldungen
BESCHRIFTUNG = {
    "name": "Name",
    "rahmennummer": "Rahmennummer",
    "typ": "Typ",
    "groesse": "Grösse",
    "gewicht_kg": "Gewicht",
    "preis_chf": "Preis",
    "km_stand": "Kilometerstand",
    "bezeichnung": "Bezeichnung",
    "einbau_datum": "Einbaudatum",
    "einbau_km": "Kilometerstand beim Einbau",
    "intervall_km": "Intervall in km",
    "intervall_tage": "Intervall in Tagen",
    "anleitung_url": "Link zur Anleitung",
    "checkliste": "Checkliste",
    "datum": "Datum",
    "notiz": "Notiz",
}


class Fehlerliste(list):
    """Sammelt Fehlermeldungen, damit alle auf einmal angezeigt werden."""


def _b(feld: str) -> str:
    return BESCHRIFTUNG.get(feld, feld)


def text(form, feld: str, fehler: Fehlerliste, pflicht=False, max_laenge=100):
    wert = (form.get(feld) or "").strip()
    if pflicht and not wert:
        fehler.append(f"«{_b(feld)}» darf nicht leer sein.")
    if len(wert) > max_laenge:
        fehler.append(f"«{_b(feld)}» darf höchstens {max_laenge} Zeichen haben.")
    return wert or None


def ganzzahl(form, feld: str, fehler: Fehlerliste, pflicht=False, minimum=0):
    roh = (form.get(feld) or "").strip().replace("'", "")
    if not roh:
        if pflicht:
            fehler.append(f"«{_b(feld)}» darf nicht leer sein.")
        return None
    try:
        wert = int(roh)
    except ValueError:
        fehler.append(f"«{_b(feld)}» muss eine ganze Zahl sein.")
        return None
    if wert < minimum:
        fehler.append(f"«{_b(feld)}» muss mindestens {minimum} sein.")
        return None
    return wert


def dezimalzahl(form, feld: str, fehler: Fehlerliste):
    roh = (form.get(feld) or "").strip().replace(",", ".")
    if not roh:
        return None
    try:
        wert = float(roh)
    except ValueError:
        fehler.append(f"«{_b(feld)}» muss eine Zahl sein.")
        return None
    if wert < 0:
        fehler.append(f"«{_b(feld)}» darf nicht negativ sein.")
        return None
    return wert


def datum(form, feld: str, fehler: Fehlerliste, heute: date):
    roh = (form.get(feld) or "").strip()
    if not roh:
        fehler.append(f"«{_b(feld)}» darf nicht leer sein.")
        return None
    try:
        wert = date.fromisoformat(roh)
    except ValueError:
        fehler.append(f"«{_b(feld)}» ist kein gültiges Datum.")
        return None
    if wert > heute:
        fehler.append(f"«{_b(feld)}» darf nicht in der Zukunft liegen.")
        return None
    return wert


def url(form, feld: str, fehler: Fehlerliste):
    wert = (form.get(feld) or "").strip()
    if not wert:
        return None
    teile = urlparse(wert)
    # Nur echte Weblinks zulassen, keine "javascript:"-Links.
    if teile.scheme not in ("http", "https") or not teile.netloc:
        fehler.append(f"«{_b(feld)}» muss mit http:// oder https:// beginnen.")
        return None
    return wert


def kategorie(form, fehler: Fehlerliste):
    wert = (form.get("kategorie") or "").strip()
    if wert not in KATEGORIEN:
        fehler.append("Bitte eine Kategorie aus der Liste wählen.")
        return None
    return wert

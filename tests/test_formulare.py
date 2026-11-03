"""Tests der Eingabeprüfung in formulare.py.

Die Funktionen sind klein und brauchen keine App: Wir geben ein Dictionary als
"Formular" hinein und prüfen Rückgabewert und Fehlermeldungen.
"""

from datetime import date

import pytest

from app import formulare as f

HEUTE = date(2026, 10, 12)


# Text ------------------------------------------------------------------------


def test_text_wird_getrimmt():
    fehler = f.Fehlerliste()
    assert f.text({"name": "  Gravel "}, "name", fehler) == "Gravel"
    assert not fehler


def test_leerer_text_ist_none():
    fehler = f.Fehlerliste()
    assert f.text({"typ": "  "}, "typ", fehler) is None
    assert not fehler


def test_pflichtfeld_darf_nicht_leer_sein():
    fehler = f.Fehlerliste()
    f.text({"name": ""}, "name", fehler, pflicht=True)
    assert fehler == ["«Name» darf nicht leer sein."]


def test_text_zu_lang():
    fehler = f.Fehlerliste()
    f.text({"groesse": "x" * 21}, "groesse", fehler, max_laenge=20)
    assert fehler == ["«Grösse» darf höchstens 20 Zeichen haben."]


# Ganzzahl --------------------------------------------------------------------


@pytest.mark.parametrize(
    "eingabe, erwartet",
    [("1000", 1000), ("1'000", 1000), (" 42 ", 42), ("0", 0)],
)
def test_ganzzahl_gueltig(eingabe, erwartet):
    fehler = f.Fehlerliste()
    assert f.ganzzahl({"km_stand": eingabe}, "km_stand", fehler) == erwartet
    assert not fehler


@pytest.mark.parametrize("eingabe", ["abc", "12.5", "1,5"])
def test_ganzzahl_ungueltig(eingabe):
    fehler = f.Fehlerliste()
    assert f.ganzzahl({"km_stand": eingabe}, "km_stand", fehler) is None
    assert fehler == ["«Kilometerstand» muss eine ganze Zahl sein."]


def test_ganzzahl_unter_minimum():
    fehler = f.Fehlerliste()
    assert f.ganzzahl({"km_stand": "-5"}, "km_stand", fehler) is None
    assert fehler == ["«Kilometerstand» muss mindestens 0 sein."]


def test_ganzzahl_leer_ohne_pflicht_ist_ok():
    fehler = f.Fehlerliste()
    assert f.ganzzahl({}, "intervall_km", fehler) is None
    assert not fehler


def test_ganzzahl_leer_mit_pflicht_ist_fehler():
    fehler = f.Fehlerliste()
    assert f.ganzzahl({"km_stand": ""}, "km_stand", fehler, pflicht=True) is None
    assert fehler == ["«Kilometerstand» darf nicht leer sein."]


# Dezimalzahl -----------------------------------------------------------------


@pytest.mark.parametrize(
    "eingabe, erwartet", [("12.5", 12.5), ("12,5", 12.5), ("0", 0)]
)
def test_dezimalzahl_gueltig(eingabe, erwartet):
    fehler = f.Fehlerliste()
    assert f.dezimalzahl({"gewicht_kg": eingabe}, "gewicht_kg", fehler) == erwartet
    assert not fehler


def test_dezimalzahl_leer_ist_none():
    fehler = f.Fehlerliste()
    assert f.dezimalzahl({"gewicht_kg": ""}, "gewicht_kg", fehler) is None
    assert not fehler


def test_dezimalzahl_kein_zahlenwert():
    fehler = f.Fehlerliste()
    assert f.dezimalzahl({"gewicht_kg": "schwer"}, "gewicht_kg", fehler) is None
    assert fehler == ["«Gewicht» muss eine Zahl sein."]


def test_dezimalzahl_negativ():
    fehler = f.Fehlerliste()
    assert f.dezimalzahl({"preis_chf": "-1"}, "preis_chf", fehler) is None
    assert fehler == ["«Preis» darf nicht negativ sein."]


# Datum -----------------------------------------------------------------------


def test_datum_gueltig():
    fehler = f.Fehlerliste()
    erg = f.datum({"datum": "2026-01-31"}, "datum", fehler, HEUTE)
    assert erg == date(2026, 1, 31)
    assert not fehler


def test_datum_heute_ist_erlaubt():
    fehler = f.Fehlerliste()
    assert f.datum({"datum": "2026-10-12"}, "datum", fehler, HEUTE) == HEUTE
    assert not fehler


def test_datum_leer():
    fehler = f.Fehlerliste()
    assert f.datum({"datum": ""}, "datum", fehler, HEUTE) is None
    assert fehler == ["«Datum» darf nicht leer sein."]


@pytest.mark.parametrize("eingabe", ["31.01.2026", "2026-13-01", "morgen"])
def test_datum_ungueltiges_format(eingabe):
    fehler = f.Fehlerliste()
    assert f.datum({"datum": eingabe}, "datum", fehler, HEUTE) is None
    assert fehler == ["«Datum» ist kein gültiges Datum."]


def test_datum_in_der_zukunft():
    fehler = f.Fehlerliste()
    assert f.datum({"datum": "2026-10-13"}, "datum", fehler, HEUTE) is None
    assert fehler == ["«Datum» darf nicht in der Zukunft liegen."]


# URL -------------------------------------------------------------------------


@pytest.mark.parametrize("eingabe", ["https://example.com/a", "http://example.com"])
def test_url_gueltig(eingabe):
    fehler = f.Fehlerliste()
    assert f.url({"anleitung_url": eingabe}, "anleitung_url", fehler) == eingabe
    assert not fehler


def test_url_leer_ist_ok():
    fehler = f.Fehlerliste()
    assert f.url({"anleitung_url": ""}, "anleitung_url", fehler) is None
    assert not fehler


@pytest.mark.parametrize("eingabe", ["javascript:alert(1)", "example.com", "https://"])
def test_url_ungueltig(eingabe):
    fehler = f.Fehlerliste()
    assert f.url({"anleitung_url": eingabe}, "anleitung_url", fehler) is None
    assert len(fehler) == 1

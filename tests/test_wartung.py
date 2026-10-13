"""Unittests der Fälligkeitslogik (ohne Datenbank und ohne Flask)."""

from datetime import date, timedelta

import pytest

from app.wartung import (
    BALD,
    FAELLIG,
    KEIN_INTERVALL,
    OK,
    berechne_faelligkeit,
    schlimmster_status,
)

HEUTE = date(2026, 10, 12)


def faelligkeit(km_stand=1000, letzte_km=0, vor_tagen=0, km=None, tage=None):
    return berechne_faelligkeit(
        km_stand=km_stand,
        letzte_wartung_km=letzte_km,
        letzte_wartung_datum=HEUTE - timedelta(days=vor_tagen),
        intervall_km=km,
        intervall_tage=tage,
        heute=HEUTE,
    )


def test_ohne_intervall_gibt_es_keinen_status():
    assert faelligkeit().status == KEIN_INTERVALL


@pytest.mark.parametrize(
    ("km_stand", "erwartet", "rest"),
    [
        (1000, OK, 2000),  # 1000 von 3000 km gefahren
        (2700, BALD, 300),  # genau 10 % übrig
        (2699, OK, 301),
        (3000, FAELLIG, 0),  # Intervall genau erreicht
        (3500, FAELLIG, -500),  # überfällig
    ],
)
def test_intervall_in_km(km_stand, erwartet, rest):
    ergebnis = faelligkeit(km_stand=km_stand, km=3000)
    assert ergebnis.status == erwartet
    assert ergebnis.rest_km == rest
    assert ergebnis.rest_tage is None


@pytest.mark.parametrize(
    ("vor_tagen", "erwartet"),
    [(100, OK), (351, BALD), (350, OK), (365, FAELLIG), (400, FAELLIG)],
)
def test_intervall_in_tagen(vor_tagen, erwartet):
    ergebnis = faelligkeit(vor_tagen=vor_tagen, tage=365)
    assert ergebnis.status == erwartet
    assert ergebnis.rest_tage == 365 - vor_tagen


def test_km_zaehlen_ab_letzter_wartung():
    # 3500 km Stand, aber bei 2000 km gewartet: erst 1500 km gefahren
    assert faelligkeit(km_stand=3500, letzte_km=2000, km=3000).status == OK


def test_bei_zwei_intervallen_gilt_das_dringendere():
    # Kilometer fast unberührt, aber Zeit abgelaufen
    ergebnis = faelligkeit(km_stand=100, vor_tagen=400, km=3000, tage=365)
    assert ergebnis.status == FAELLIG
    assert ergebnis.rest_km == 2900


def test_schlimmster_status():
    assert schlimmster_status([OK, BALD, KEIN_INTERVALL]) == BALD
    assert schlimmster_status([OK, FAELLIG, BALD]) == FAELLIG
    assert schlimmster_status([]) == KEIN_INTERVALL

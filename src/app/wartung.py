"""Fälligkeitslogik: Wann muss eine Komponente gewartet werden?

Dieses Modul kennt weder Flask noch die Datenbank. Es rechnet nur mit
Zahlen und Daten. Darum lässt es sich einfach mit Unittests prüfen.

Regeln:
 * Eine Komponente hat ein Intervall in Kilometern, in Tagen oder beides.
 * Gezählt wird ab der letzten Wartung (beim Einbau ist das der Einbau).
 * "fällig": das Intervall ist erreicht oder überschritten.
 * "bald":   weniger als 10 % der Kilometer oder höchstens 14 Tage übrig.
 * Gilt beides (km und Tage), zählt das, was zuerst eintritt.
"""

from dataclasses import dataclass
from datetime import date

OK = "ok"
BALD = "bald"
FAELLIG = "faellig"
KEIN_INTERVALL = "kein_intervall"

BALD_ANTEIL_KM = 0.10
BALD_TAGE = 14

# Reihenfolge von "harmlos" bis "dringend", für den Vergleich mehrerer Status
_RANG = {KEIN_INTERVALL: 0, OK: 1, BALD: 2, FAELLIG: 3}


@dataclass
class Faelligkeit:
    status: str
    rest_km: int | None = None
    rest_tage: int | None = None


def berechne_faelligkeit(
    *,
    km_stand: int,
    letzte_wartung_km: int,
    letzte_wartung_datum: date,
    intervall_km: int | None,
    intervall_tage: int | None,
    heute: date,
) -> Faelligkeit:
    """Berechnet Status und Restlaufzeit einer Komponente."""
    if not intervall_km and not intervall_tage:
        return Faelligkeit(KEIN_INTERVALL)

    status_liste = []
    rest_km = None
    rest_tage = None

    if intervall_km:
        gefahren = km_stand - letzte_wartung_km
        rest_km = intervall_km - gefahren
        if rest_km <= 0:
            status_liste.append(FAELLIG)
        elif rest_km <= intervall_km * BALD_ANTEIL_KM:
            status_liste.append(BALD)
        else:
            status_liste.append(OK)

    if intervall_tage:
        vergangen = (heute - letzte_wartung_datum).days
        rest_tage = intervall_tage - vergangen
        if rest_tage <= 0:
            status_liste.append(FAELLIG)
        elif rest_tage <= BALD_TAGE:
            status_liste.append(BALD)
        else:
            status_liste.append(OK)

    return Faelligkeit(schlimmster_status(status_liste), rest_km, rest_tage)


def schlimmster_status(status_liste) -> str:
    """Gibt den dringendsten Status zurück, z.B. für ein ganzes Velo."""
    status_liste = list(status_liste)
    if not status_liste:
        return KEIN_INTERVALL
    return max(status_liste, key=lambda status: _RANG[status])

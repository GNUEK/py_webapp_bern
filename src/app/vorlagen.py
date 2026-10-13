"""Standardkomponenten, die beim Erfassen eines Velos angelegt werden können.

Die Intervalle sind grobe Richtwerte und lassen sich pro Komponente ändern.
Die Links führen auf eine YouTube-Suche (z.B. nach GCN-Anleitungen).
"""

from urllib.parse import quote_plus


def youtube_suche(begriff: str) -> str:
    return "https://www.youtube.com/results?search_query=" + quote_plus(begriff)


STANDARDKOMPONENTEN = [
    {
        "bezeichnung": "Kette",
        "kategorie": "Kette",
        "intervall_km": 3000,
        "intervall_tage": None,
        "anleitung_url": youtube_suche("GCN how to replace bike chain"),
        "checkliste": "Kettenverschleiss messen\nKette reinigen\nKette ölen",
    },
    {
        "bezeichnung": "Bremsbeläge",
        "kategorie": "Bremsbeläge",
        "intervall_km": 2000,
        "intervall_tage": None,
        "anleitung_url": youtube_suche("GCN how to replace disc brake pads"),
        "checkliste": "Belagstärke prüfen\nBremsscheibe reinigen\nBremse testen",
    },
    {
        "bezeichnung": "Reifen hinten",
        "kategorie": "Reifen hinten",
        "intervall_km": 4000,
        "intervall_tage": None,
        "anleitung_url": youtube_suche("GCN how to change a tyre"),
        "checkliste": "Profil und Schnitte prüfen\nLuftdruck prüfen",
    },
    {
        "bezeichnung": "Jahresservice",
        "kategorie": "Service",
        "intervall_km": None,
        "intervall_tage": 365,
        "anleitung_url": youtube_suche("GCN bike service at home"),
        "checkliste": (
            "Schrauben nachziehen\nSchaltung einstellen\n"
            "Lager auf Spiel prüfen\nZüge prüfen"
        ),
    },
]

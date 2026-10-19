-- Datenbankschema des Velo-Wartungslogbuchs.
-- Wird beim ersten Start automatisch angelegt (siehe db.py).

CREATE TABLE IF NOT EXISTS velo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    typ             TEXT,
    rahmennummer    TEXT,
    groesse         TEXT,
    gewicht_kg      REAL,
    preis_chf       REAL,
    km_stand        INTEGER NOT NULL DEFAULT 0 CHECK (km_stand >= 0),
    strava_gear_id  TEXT UNIQUE,
    erstellt_am     TEXT    NOT NULL DEFAULT (date('now'))
);

-- Eine Komponente gehört zu genau einem Velo.
-- Das Intervall gilt ab der letzten Wartung (bzw. ab dem Einbau).
CREATE TABLE IF NOT EXISTS komponente (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    velo_id               INTEGER NOT NULL REFERENCES velo(id) ON DELETE CASCADE,
    bezeichnung           TEXT    NOT NULL,
    modell                TEXT,
    kategorie             TEXT    NOT NULL,
    einbau_datum          TEXT    NOT NULL,
    einbau_km             INTEGER NOT NULL CHECK (einbau_km >= 0),
    intervall_km          INTEGER CHECK (intervall_km IS NULL OR intervall_km > 0),
    intervall_tage        INTEGER CHECK (intervall_tage IS NULL OR intervall_tage > 0),
    letzte_wartung_datum  TEXT    NOT NULL,
    letzte_wartung_km     INTEGER NOT NULL,
    anleitung_url         TEXT,
    checkliste            TEXT,
    aktiv                 INTEGER NOT NULL DEFAULT 1,
    ausbau_datum          TEXT,
    ausbau_km             INTEGER
);

CREATE TABLE IF NOT EXISTS wartung (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    komponente_id  INTEGER NOT NULL REFERENCES komponente(id) ON DELETE CASCADE,
    datum          TEXT    NOT NULL,
    km_stand       INTEGER NOT NULL,
    notiz          TEXT,
    erledigt       TEXT
);

-- Zugangsdaten zu Strava. Es gibt höchstens eine Zeile (id = 1),
-- weil der Prototyp keine Benutzerkonten kennt.
CREATE TABLE IF NOT EXISTS strava_token (
    id             INTEGER PRIMARY KEY CHECK (id = 1),
    access_token   TEXT    NOT NULL,
    refresh_token  TEXT    NOT NULL,
    expires_at     INTEGER NOT NULL,
    athlet         TEXT
);

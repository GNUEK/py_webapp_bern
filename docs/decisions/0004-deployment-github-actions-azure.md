# Deployment: GitHub Actions auf Azure App Service

Date: 2026-10-12

## Status

Accepted

## Context

Die Aufgabenstellung verlangt eine öffentliche URL und automatisches
Deployment. Das Template enthält eine Anleitung für Flask auf Azure App
Service mit dem eingebauten Python-Runtime.

## Options Considered

 * Azure App Service (Python-Runtime) mit GitHub Actions und Publish Profile:
   vom Template vorgesehen, keine Container-Kenntnisse nötig.
 * Azure App Service mit Docker-Container: das Dockerfile existiert, braucht
   aber zusätzlich eine Container Registry.
 * Andere Anbieter (Render, Railway): einfach, aber im Modul nicht vorgesehen.

## Decision

Workflow `.github/workflows/ci-cd.yml`:

 1. Bei jedem Push und Pull Request: `ruff check` und `pytest`.
 2. Bei Push auf `main` und grünen Tests: `requirements.txt` aus `uv`
    erzeugen und mit `azure/webapps-deploy` auf App Service laden.
    Azure installiert die Pakete und startet `startup.sh`.

## Reasons

Fehler fallen vor dem Deployment auf, weil ein roter Test das Deployment
stoppt. Das Publish Profile ist der einfachste Weg, GitHub Zugriff auf Azure
zu geben.

## Consequences

 * In GitHub müssen das Secret `AZURE_WEBAPP_PUBLISH_PROFILE` und die
   Variable `AZURE_WEBAPP_NAME` angelegt werden (siehe README). Fehlen sie,
   läuft nur der Testteil.
 * In Azure: Startup Command `startup.sh`, App-Setting
   `SCM_DO_BUILD_DURING_DEPLOYMENT=true`, dazu `SECRET_KEY` und
   `DATABASE_PATH`.

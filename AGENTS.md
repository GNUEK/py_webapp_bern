## Technology stack

This project represents a web application with a backend and a frontend part.
The backend is to be kept completely in Python. The frontend stack can be chosen
freely.

 * We use `uv` for any Python related tasks

## Files and directories

 * Check `docs/directories.md` for the recommended directory structure.
 * In case Django is used, the entire `src/` directory maybe adapted for Djangos
   directory conventions and the `app/` directory may be removed or ignored.
 * The project currently contains a very simple vanilla Python-based WSGI
   application that can be run with gunicorn/waitress. Once the developers have
   decided on the way to go, remove any of this basic code from
   `src/app/__init__.py` and `src/app/static/index.html`.
 * If the developers choose Flask and deployment to Azure App Service with the
   built-in Python runtime, follow
   `docs/deployment-azure-app-service-flask.md`. In particular, create a
   root-level `startup.sh` for Gunicorn and make sure `src/app/__init__.py`
   exposes a Flask application object named `app` so `app:app` can be imported.
   Keep these steps conditional; do not add Flask-specific Azure files when the
   team chooses Django, FastAPI, Starlette or a container-based deployment.

## Design guidelines

This is a project that is to be developed in the course of a master degree in
business informatics. The focus is on exploring and learning about all the parts
involved in running a full web application rather than building a fully
productive, scalable and long-term maintainable application. The created
elements should be easy to understand.

 * When discussing design options, start with the simpler options; for example
   suggest to start with Flask or Starlette rather than Django, suggest vanilla
   JavaScript, HTMX or Alpine.js rather than going straight for full fledged
   solutions like Angular or React. Accept more complex solutions once the
   developers made it clear that they are needed and they understand the
   implications.
 * Prefer frontend technologies that can be used through CDN and don't need any
   frontend build steps.
 * For WSGI/ASGI start with either Gunicorn or Uvicorn depending on the web
   framework used.
 * Document architectural design decisions that were discussed with the
   developers in the folder `docs/decisions`. Use a new file for every decision
   and use a continuous numbering scheme in the form
   `0001-framework-choice.md`.

## Educational collaboration

This template is used for learning software development, not only for producing
code. When students ask an agent to add a feature, choose a technology, or make
an architectural change, the agent should first help them reason about the
decision before implementing it.

Reusable guidance for this behavior is stored as the generic agent skill
`.agents/skills/challenge-development-decisions`. Agents that support skills
should use that skill for feature requests, technology choices, architecture
placement questions, and decision records in this project.

Decision records for this project belong in `docs/decisions` and should be
based on `docs/decision-template.md`.

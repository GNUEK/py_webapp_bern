# Azure App Service deployment with Flask

Use this document when the project team has chosen Flask and wants to deploy the
application to Azure App Service with the built-in Python runtime.

These steps apply both to an initial manual deployment and to a later automated
deployment through GitHub Actions. The important part is the runtime shape of
the deployed application: Azure App Service must know how to start the Flask app
after the code has arrived on the service.

Some help can be found in the GitHub example project https://github.com/Azure-Samples/msdocs-python-flask-webapp-quickstart/tree/main

More detailed help can be found in
* https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Cazure-cli-deploy%2Cdeploy-instructions-azportal%2Cterminal-bash%2Cdeploy-instructions-zip-azcli
* https://learn.microsoft.com/en-us/azure/app-service/configure-language-python
* This particular blog post about uv-based Python Flask App Service applications: https://techcommunity.microsoft.com/blog/appsonazureblog/what%E2%80%99s-new-for-python-on-app-service-for-linux-pyproject-toml-uv-and-more/4468903

Azure App Service with the built-in Python runtime needs a clear startup command
for a Python web application. For Flask projects in this template, create a
`startup.sh` file in the project root:

```sh
#!/bin/sh
set -eu

exec gunicorn \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 600 \
    --access-logfile "-" \
    --error-logfile "-" \
    app:app
```

The final `app:app` means:

* the first `app` is the Python module/package `src/app`
* the second `app` is the Flask application object inside `src/app/__init__.py`

In the Azure App Service configuration, set the startup command to:

```sh
startup.sh
```

## Flask application shape

The file `src/app/__init__.py` must expose a Flask application object named
`app`, because this is what Gunicorn imports through `app:app`.

A minimal version looks like this:

```python
from flask import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return "Hello from Flask"


if __name__ == "__main__":
    app.run()
```

The `if __name__ == "__main__":` block is useful for local development with:

```sh
uv run python -m app
```

Gunicorn does not execute that block. It imports the `app` object directly.

## Dependencies

Make sure Flask and Gunicorn are project dependencies:

```sh
uv add flask gunicorn
```

This template already includes gunicorn. If the team removed them while choosing
another framework, add them again before using this deployment path.

## Local check before deployment

Before deploying to Azure, check that Gunicorn can load the application in the
same way Azure will:

```sh
uv run gunicorn --bind "0.0.0.0:8000" --chdir src app:app
```

Open `http://localhost:8000` and verify that the application starts correctly.

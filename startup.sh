#!/bin/sh
# Startbefehl für Azure App Service (in Azure als Startup Command: startup.sh)
set -eu

exec gunicorn \
    --bind "0.0.0.0:${PORT:-8000}" \
    --chdir src \
    --timeout 600 \
    --access-logfile "-" \
    --error-logfile "-" \
    app:app

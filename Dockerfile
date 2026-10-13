FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
# Datenbank in einem eigenen Ordner, damit man ihn als Volume einbinden kann
ENV DATABASE_PATH="/app/data/velo.db"

EXPOSE 8000

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "app:app" ]

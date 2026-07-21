FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8000

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "app:app" ]

# Base: minimal Linux with Python 3.14 already inside (we build on top of this)
FROM python:3.14-slim

# Live logs (don't buffer) + no junk .pyc cache files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Bootstrap Poetry with pip (pip ships in the base image); --no-cache-dir keeps the image lean
RUN pip install --no-cache-dir poetry

# "cd" into /app inside the container — where our files will live
WORKDIR /app

# Copy ONLY the dep files first → if deps don't change, Docker reuses the cached install (faster rebuilds)
COPY pyproject.toml poetry.lock ./

# No inner venv (container is already isolated) + runtime deps only (skip dev: no pytest/ruff) → leaner image
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root

# Carry the backend code in (only app/)
COPY app ./app

# Note: the app listens on 8000 (this doesn't OPEN it — that's -p at run time)
EXPOSE 8000

# Run-time startup: serve FastAPI. 0.0.0.0 = reachable from outside the container
CMD ["uvicorn", "app.fast_api_endpoints:app", "--host", "0.0.0.0", "--port", "8000"]

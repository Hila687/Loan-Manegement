# Production image: builds the Vue app, then runs Django + gunicorn,
# which serves both the API (/api/...) and the site from one address.

# ---- 1. Frontend build ------------------------------------------------
FROM node:22-alpine AS frontend
WORKDIR /app/frontend/client
COPY frontend/client/package.json frontend/client/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/client/ ./
RUN npm run build

# ---- 2. Backend runtime ----------------------------------------------
FROM python:3.12-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FRONTEND_DIST=/app/frontend/client/dist \
    MEDIA_ROOT=/data/media \
    BACKUP_DIR=/data/backups \
    DJANGO_DEBUG=false \
    TZ=Asia/Jerusalem

# pg_dump / psql for backups and restores
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ ./
COPY deploy/docker-entrypoint.sh deploy/backup.sh /usr/local/bin/
COPY --from=frontend /app/frontend/client/dist /app/frontend/client/dist

# Static files are collected at build time (no secrets needed for that).
RUN DJANGO_SECRET_KEY=build-only DB_ENGINE=sqlite \
    python manage.py collectstatic --noinput \
    && chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/backup.sh \
    && useradd --create-home --uid 1000 gemach \
    && mkdir -p /data/media /data/backups \
    && chown -R gemach:gemach /data

USER gemach
VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:%s/api/health/' % os.getenv('PORT','8000'), timeout=4)" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["web"]

# Analog Atlas · Dockerfile · v1.0 · 2026-11-15 · Isabelita (equipo Ctrl Z)
# Un solo contenedor: compila la página React y la sirve con la API (FastAPI) en el puerto 8000.
# Uso: docker compose up -d --build   (ver docker-compose.yml y .env.example)

# ---------- 1. Página React ----------
FROM node:22.11.0-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---------- 2. Servidor ----------
FROM python:3.13.1-slim AS servidor
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib
WORKDIR /app

COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

# Solo lo que la API necesita: código y datos ya procesados (la tabla de la Tierra y las referencias)
COPY api/ api/
COPY services/ services/
COPY models/ models/
COPY config/ config/
COPY backend/ backend/
COPY science/ science/
COPY datos/__init__.py datos/celdas.parquet datos/
COPY datos/geo/ datos/geo/
COPY --from=frontend /app/frontend/dist frontend/dist

# Sin privilegios de administrador dentro del contenedor
RUN useradd --create-home --uid 10001 atlas && chown -R atlas /app
USER atlas

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

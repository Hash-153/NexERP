# ==============================================================================
# NexERP Enterprise - Multi-Stage Production Dockerfile
# Stage 1: Build Python dependencies with pip in a clean base
# Stage 2: Lean runtime image with non-root system user for security hardening
# ==============================================================================

# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

WORKDIR /build

# System libraries required for cryptography, psycopg2 builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (cache layer)
COPY backend/requirements.txt requirements.txt

# Install Python packages into /install prefix for copy into slim stage
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---- Stage 2: Runtime ----
FROM python:3.12-slim AS runtime

# Security: install runtime shared libs (libpq for Postgres, libssl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Run as non-root application user
RUN groupadd --system nexerp && useradd --system --gid nexerp --home /app nexerp

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY backend/ ./backend/
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Set correct file ownership
RUN chown -R nexerp:nexerp /app

USER nexerp

# Environment defaults (can be overridden by docker-compose or K8s ConfigMaps)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    NEXERP_ENV=production \
    LOG_LEVEL=info

# Health check: ping the FastAPI readiness endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

EXPOSE 8000

# Entrypoint: run database migrations then start Gunicorn with Uvicorn workers
CMD ["sh", "-c", "alembic upgrade head && gunicorn backend.src.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile -"]

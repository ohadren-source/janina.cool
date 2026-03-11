# Dockerfile — Janina on Railway
# ================================
# Multi-stage build: slim runtime with no build artifacts.
# Runs both release and web phases from Procfile via custom entrypoint.

FROM python:3.11-slim

# Install system dependencies
# libpq5 is required by psycopg2 (even with -binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY janina_api.py .
COPY janina_banks.py .
COPY load_responses.py .
COPY responses.json .

# Create entrypoint script that runs release phase, then web phase
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Release phase: load responses into database\n\
echo "[release] Loading 108 responses..."\n\
python load_responses.py --file responses.json\n\
echo "[release] Responses loaded successfully"\n\
\n\
# Web phase: start the API\n\
echo "[web] Starting Janina API..."\n\
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} janina_api:app\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Expose port (Railway will override with $PORT env var)
EXPOSE 5000

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Stage 1: Build Python wheels
FROM python:3.14-slim AS builder

# Install build dependencies only here
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
# Build wheels instead of direct install
RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# Stage 2: Final runtime image
FROM python:3.14-slim

# Install only runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home/appuser

# Install Python packages from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY --chown=appuser:appgroup govuk-frontend-flask.py config.py ./ 
COPY --chown=appuser:appgroup app app
COPY --chown=appuser:appgroup migrations migrations

# Copy entrypoint script into PATH
COPY --chown=appuser:appgroup docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER appuser

ENTRYPOINT ["docker-entrypoint.sh"]

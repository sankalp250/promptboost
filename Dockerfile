# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY server/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy server application code
COPY server/ /app/

# Copy ML models (if they exist)
COPY server/app/ml_models/ /app/app/ml_models/

# Copy alembic configuration
# Since server/ is copied to /app/, alembic migrations are at /app/alembic/
# We need to adjust the script_location path in alembic.ini
COPY alembic.ini /tmp/alembic.ini.orig
RUN sed 's|script_location = %(here)s/server/alembic|script_location = alembic|' /tmp/alembic.ini.orig > /app/alembic.ini && rm /tmp/alembic.ini.orig

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

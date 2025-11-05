#!/bin/bash
set -e

echo "Starting PromptBoost server on Render..."

# On Render, the database is already available via DATABASE_URL
# No need to wait for it

# Run migrations
echo "Running database migrations..."
cd /app
alembic -c alembic.ini upgrade head

# Start the server
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

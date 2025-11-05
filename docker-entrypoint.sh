#!/bin/bash
set -e

# Check if we're on Render (Render provides PORT environment variable)
if [ -n "$PORT" ]; then
    echo "Detected Render environment..."
    # On Render, database is already available via DATABASE_URL
    # No need to wait for it
    echo "Running database migrations..."
    cd /app
    alembic -c alembic.ini upgrade head
    echo "Starting FastAPI server on port $PORT..."
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
else
    echo "Detected local Docker environment..."
    echo "Waiting for database to be ready..."
    # Wait for PostgreSQL to be ready (local Docker Compose)
    until pg_isready -h db -p 5432 -U ${POSTGRES_USER:-promptboost}; do
        echo "Database is unavailable - sleeping"
        sleep 1
    done
    
    echo "Database is ready!"
    
    # Run migrations
    echo "Running database migrations..."
    cd /app
    alembic -c alembic.ini upgrade head
    
    # Start the server
    echo "Starting FastAPI server..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
fi

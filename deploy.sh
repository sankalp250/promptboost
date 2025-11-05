#!/bin/bash

# PromptBoost Deployment Script
# This script helps set up and deploy the application

set -e

echo "=========================================="
echo "  PromptBoost Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://www.docker.com/get-started"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker and docker-compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# Database Configuration
POSTGRES_USER=promptboost
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
POSTGRES_DB=promptboost
POSTGRES_PORT=5432

# Server Configuration
SERVER_PORT=8000
PROJECT_NAME=PromptBoost
PROJECT_DESCRIPTION=Prompt Enhancement Service

# API Keys (REQUIRED - Replace with your actual keys)
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
EOF
    echo "✅ Created .env file with random database password"
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys!"
    echo ""
    read -p "Press Enter after you've added your API keys to .env, or Ctrl+C to exit..."
fi

# Check if ML models exist
if [ ! -f "server/app/ml_models/preference_model.joblib" ] || [ ! -f "server/app/ml_models/tfidf_vectorizer.joblib" ]; then
    echo "⚠️  ML models not found!"
    echo "   Would you like to train them now? (requires Python and dependencies)"
    read -p "Train models now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "venv" ]; then
            echo "Activating virtual environment..."
            source venv/bin/activate || source venv/Scripts/activate
        fi
        echo "Training ML models..."
        python scripts/train_preference_model.py
        echo "✅ Models trained"
    else
        echo "⚠️  Continuing without models. Some features may not work."
    fi
    echo ""
fi

# Build and start services
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "✅ Server should be running at: http://localhost:8000"
echo "✅ API Documentation: http://localhost:8000/docs"
echo "✅ Health Check: http://localhost:8000/"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services with: docker-compose down"
echo ""

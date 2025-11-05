# PromptBoost Deployment Script for Windows
# This script helps set up and deploy the application on Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PromptBoost Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ docker-compose is available: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose is not available." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    
    # Generate a random password
    $randomPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 25 | ForEach-Object {[char]$_})
    
    $envContent = @"
# Database Configuration
POSTGRES_USER=promptboost
POSTGRES_PASSWORD=$randomPassword
POSTGRES_DB=promptboost
POSTGRES_PORT=5432

# Server Configuration
SERVER_PORT=8000
PROJECT_NAME=PromptBoost
PROJECT_DESCRIPTION=Prompt Enhancement Service

# API Keys (REQUIRED - Replace with your actual keys)
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
"@
    
    $envContent | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ Created .env file with random database password" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Please edit .env and add your API keys!" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after you've added your API keys to .env, or Ctrl+C to exit"
}

# Check if ML models exist
$modelPath = "server\app\ml_models\preference_model.joblib"
$vectorizerPath = "server\app\ml_models\tfidf_vectorizer.joblib"

if (-not (Test-Path $modelPath) -or -not (Test-Path $vectorizerPath)) {
    Write-Host "⚠️  ML models not found!" -ForegroundColor Yellow
    Write-Host "   Would you like to train them now? (requires Python and dependencies)"
    $response = Read-Host "Train models now? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        if (Test-Path "venv\Scripts\activate.ps1") {
            Write-Host "Activating virtual environment..."
            & "venv\Scripts\activate.ps1"
        }
        Write-Host "Training ML models..."
        python scripts\train_preference_model.py
        Write-Host "✅ Models trained" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Continuing without models. Some features may not work." -ForegroundColor Yellow
    }
    Write-Host ""
}

# Build and start services
Write-Host "Building Docker images..." -ForegroundColor Cyan
docker-compose build

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Server should be running at: http://localhost:8000" -ForegroundColor Green
Write-Host "✅ API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "✅ Health Check: http://localhost:8000/" -ForegroundColor Green
Write-Host ""
Write-Host "View logs with: docker-compose logs -f" -ForegroundColor Cyan
Write-Host "Stop services with: docker-compose down" -ForegroundColor Cyan
Write-Host ""

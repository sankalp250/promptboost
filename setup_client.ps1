# PromptBoost Client Setup Script
# This script creates the .env file with the correct API URL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PromptBoost Client Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$envPath = "enhancer_client\.env"

# Check if .env already exists
if (Test-Path $envPath) {
    Write-Host "[INFO] .env file already exists at: $envPath" -ForegroundColor Yellow
    Write-Host ""
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "[INFO] Keeping existing .env file" -ForegroundColor Green
        exit 0
    }
}

# Get API URL from user
Write-Host "Enter your backend API URL:" -ForegroundColor Yellow
Write-Host "  Example: https://promptboost-server.onrender.com" -ForegroundColor Gray
Write-Host ""
$apiUrl = Read-Host "Backend URL (without /api/v1)"

# Remove trailing slash if present
$apiUrl = $apiUrl.TrimEnd('/')

# Add /api/v1 if not already present
if (-not $apiUrl.EndsWith("/api/v1")) {
    $apiUrl = "$apiUrl/api/v1"
}

# Create .env content
$envContent = "API_BASE_URL=$apiUrl`n"

# Write to file
try {
    Set-Content -Path $envPath -Value $envContent -Force
    Write-Host ""
    Write-Host "[SUCCESS] Created .env file at: $envPath" -ForegroundColor Green
    Write-Host "[INFO] API_BASE_URL = $apiUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the client with:" -ForegroundColor Cyan
    Write-Host "  cd enhancer_client" -ForegroundColor White
    Write-Host "  python main.py" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "[ERROR] Failed to create .env file: $_" -ForegroundColor Red
    exit 1
}


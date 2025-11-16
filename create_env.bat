@echo off
REM Create .env file for PromptBoost client

echo ========================================
echo   PromptBoost - Create .env File
echo ========================================
echo.

set ENV_FILE=enhancer_client\.env

if exist %ENV_FILE% (
    echo [WARNING] .env file already exists!
    echo.
    set /p OVERWRITE="Do you want to overwrite it? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Keeping existing .env file.
        pause
        exit /b 0
    )
)

echo.
echo Enter your backend URL (e.g., https://promptboost-server.onrender.com)
echo The script will automatically add /api/v1 to the end.
echo.
set /p BACKEND_URL="Backend URL: "

REM Remove trailing slash if present
set BACKEND_URL=%BACKEND_URL:/=%

REM Create the .env file with correct format
echo API_BASE_URL=%BACKEND_URL%/api/v1 > %ENV_FILE%

echo.
echo [SUCCESS] Created .env file at: %ENV_FILE%
echo [INFO] API_BASE_URL = %BACKEND_URL%/api/v1
echo.
echo You can now run the client with:
echo   cd enhancer_client
echo   python main.py
echo.
pause


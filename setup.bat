@echo off
REM Initial setup script for Windows

echo.
echo ================================
echo Polymarket BTC Bot Setup (Windows)
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ and add to PATH
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo Creating .env file...
if exist .env (
    echo .env already exists
) else (
    copy .env.example .env
    echo Created .env - edit with your PRIVATE_KEY
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env with your PRIVATE_KEY (use Notepad or VS Code)
echo 2. Run: run_dev.bat (for testing)
echo 3. Run: run_live.bat (for live trading - CAREFUL!)
echo.
echo To activate venv manually:
echo   .venv\Scripts\activate
echo.
pause
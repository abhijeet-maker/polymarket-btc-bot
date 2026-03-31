@echo off
REM Testing mode - DRY_RUN will be set to true

echo.
echo ================================
echo Running in DEV/SIMULATION mode
echo No real trades will be executed
echo ================================
echo.

cd /d %~dp0

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

set DRY_RUN=true
.\.venv\Scripts\python.exe -m src.bot

pause

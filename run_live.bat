@echo off
REM WARNING: This will trade with real USDC!

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║         WARNING: LIVE TRADING MODE                 ║
echo ║     This will use real USDC from your wallet       ║
echo ║     Ensure .env has correct PRIVATE_KEY            ║
echo ╚════════════════════════════════════════════════════╝
echo.

pause

cd /d %~dp0

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

set DRY_RUN=false
python -m src.bot

pause
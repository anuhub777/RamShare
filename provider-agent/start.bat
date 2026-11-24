@echo off
echo ==========================================
echo     RAMShare Provider Agent Launcher      
echo ==========================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python 3 is required. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

if not exist venv (
    echo Setting up Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Ensuring dependencies are installed...
pip install -r requirements.txt --quiet

set API_URL=%1
if "%API_URL%"=="" set API_URL=http://localhost:8000

echo Connecting to RAMShare backend at: %API_URL%
python -m agent.main start --api-url %API_URL%

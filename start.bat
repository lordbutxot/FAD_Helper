@echo off
REM Quick start script for Windows

echo ==========================================
echo F.A.D. List Builder - Quick Start
echo ==========================================
echo.

echo [1/3] Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using global Python
)
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt
echo.

echo [3/3] Starting application...
echo.
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

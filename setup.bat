@echo off
echo.
echo ==================================================
echo   TruthSense Fake News Detector Setup
echo ==================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+ and try again.
    pause
    exit /b
)

:: Create virtual environment
echo [1/3] Creating virtual environment...
python -m venv venv

:: Activate and install dependencies
echo [2/3] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

:: Train initial model
echo [3/3] Training initial model...
python -c "from app.ml_model import classifier; print(classifier.train('data/train.csv'))"

echo.
echo ==================================================
echo   Setup Complete!
echo   To start the app: python run.py
echo   URL: http://localhost:5000
echo ==================================================
echo.
pause

@echo off
REM ====================================================
REM  CSV Chatbot Pro - Clean Installation Script
REM  Run this AFTER removing McAfee
REM ====================================================

echo.
echo ========================================
echo  CSV Chatbot Pro - Fresh Setup
echo ========================================
echo.

REM Step 1: Check if we're in the right directory
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please run this script from the csv_chatbot folder
    pause
    exit /b 1
)

REM Step 2: Delete old virtual environment if it exists
echo [1/5] Cleaning old virtual environment...
if exist "venv" (
    rmdir /s /q venv
    echo    - Old venv deleted
) else (
    echo    - No old venv found
)

REM Step 3: Create fresh virtual environment
echo.
echo [2/5] Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.9+ is installed
    pause
    exit /b 1
)
echo    - Virtual environment created

REM Step 4: Activate and upgrade pip
echo.
echo [3/5] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
echo    - Pip upgraded

REM Step 5: Install all dependencies
echo.
echo [4/5] Installing dependencies (this may take 2-3 minutes)...
pip install streamlit pandas groq python-dotenv plotly numpy openpyxl
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    - All dependencies installed

REM Step 6: Verify .env exists
echo.
echo [5/5] Checking configuration...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating template .env file...
    echo GROQ_API_KEY=your_groq_api_key_here > .env
    echo    - Please edit .env and add your Groq API key
) else (
    echo    - .env file exists
)

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure your .env file has: GROQ_API_KEY=your_actual_key
echo 2. Run: start_app.bat
echo.
pause

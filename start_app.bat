@echo off
REM ====================================================
REM  CSV Chatbot Pro - Startup Script
REM ====================================================

echo Starting CSV Chatbot Pro...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists and has API key
findstr /C:"GROQ_API_KEY=your_groq_api_key_here" .env >nul 2>&1
if %errorlevel%==0 (
    echo.
    echo ========================================
    echo  WARNING: API Key Not Configured!
    echo ========================================
    echo.
    echo Please edit .env and add your Groq API key
    echo Get one free at: https://console.groq.com/keys
    echo.
    pause
    exit /b 1
)

REM Start Streamlit
streamlit run app.py

pause

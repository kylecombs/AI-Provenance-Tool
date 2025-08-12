@echo off
REM AI Provenance Tool - Windows Development Server Script

echo 🚀 Starting AI Provenance Tool Development Server...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment and start server
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

echo ✅ Starting server...
echo 📚 API Documentation: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo 🛑 Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
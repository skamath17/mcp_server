@echo off
title Stock Analysis HTTP API Server

echo ========================================
echo  Stock Analysis HTTP API Server
echo ========================================
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to the project directory
cd /d "%SCRIPT_DIR%"

echo 📁 Project Directory: %CD%
echo.

REM Check if virtual environment exists
if not exist "stock-mcp-env\Scripts\python.exe" (
    echo ❌ Error: Virtual environment not found!
    echo Please run the following commands first:
    echo.
    echo   python -m venv stock-mcp-env
    echo   stock-mcp-env\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo 🔧 Activating virtual environment...
call stock-mcp-env\Scripts\activate.bat

echo 🚀 Starting Stock Analysis HTTP API...
echo 📡 Server will be available at: http://localhost:8001
echo 📚 API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the HTTP proxy server
python http_mcp_proxy.py

echo.
echo 🛑 Server stopped.
pause 
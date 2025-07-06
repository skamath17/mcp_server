# Stock Analysis HTTP API Server Launcher
# PowerShell script to start the HTTP proxy server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Stock Analysis HTTP API Server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📁 Project Directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "stock-mcp-env\Scripts\python.exe")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the following commands first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   python -m venv stock-mcp-env" -ForegroundColor White
    Write-Host "   stock-mcp-env\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "🔧 Checking dependencies..." -ForegroundColor Blue
& "stock-mcp-env\Scripts\python.exe" -c "import fastapi, mcp" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies missing. Installing..." -ForegroundColor Yellow
    & "stock-mcp-env\Scripts\pip.exe" install -r requirements.txt
}

Write-Host "🚀 Starting Stock Analysis HTTP API..." -ForegroundColor Green
Write-Host "📡 Server will be available at: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Start the server
    & "stock-mcp-env\Scripts\python.exe" "http_mcp_proxy.py"
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "🛑 Server stopped." -ForegroundColor Red
    Read-Host "Press Enter to exit"
} 
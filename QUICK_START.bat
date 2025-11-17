@echo off
REM QUICK_START.bat - One-click setup and maintenance

echo ====================================
echo PDF Structure Quick Start
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not found. Please install Git
    echo Download from: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing dev tools (optional)...
pip install black isort ruff 2>nul
echo Dev tools installed (or skipped if already present)

echo.
echo [3/4] Checking wkhtmltopdf...
where wkhtmltopdf >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: wkhtmltopdf is installed
) else (
    echo.
    echo WARNING: wkhtmltopdf not found!
    echo This is required for HTML to PDF conversion.
    echo.
    echo Please download and install from:
    echo https://wkhtmltopdf.org/downloads.html
    echo.
    echo After installation, add to PATH:
    echo C:\Program Files\wkhtmltopdf\bin
    echo.
)

echo.
echo [4/4] Creating required directories...
if not exist "INPUT_DATA" mkdir INPUT_DATA
if not exist "OUTPUT_PDF" mkdir OUTPUT_PDF
if not exist "LOGS" mkdir LOGS

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo You can now:
echo   1. Run maintenance: maintain-pdf-structure.bat
echo   2. Start Flask app: python app.py
echo   3. Convert files: python -m html2pdf.cli --help
echo.
echo For detailed instructions, see MAINTENANCE_GUIDE.md
echo.
pause

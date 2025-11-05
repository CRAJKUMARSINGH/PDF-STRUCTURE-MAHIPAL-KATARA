@echo off
REM ============================================================================
REM PDF Conversion Tools - Test Runner
REM ============================================================================

echo.
echo ========================================================================
echo  PDF CONVERSION TOOLS - TEST RUNNER
echo ========================================================================
echo.

REM Generate timestamp for output folders
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

REM Create timestamped output directories
set HTML_OUTPUT=output_html_%TIMESTAMP%
set DXF_OUTPUT=output_dxf_%TIMESTAMP%

echo Creating output directories:
echo   - %HTML_OUTPUT%
echo   - %DXF_OUTPUT%
echo.

if not exist "%HTML_OUTPUT%" mkdir "%HTML_OUTPUT%"
if not exist "%DXF_OUTPUT%" mkdir "%DXF_OUTPUT%"

echo [1/3] Testing HTML to PDF Converter...
echo ------------------------------------------------------------------------
echo Converting all HTML files to combined PDF...
python -m html2pdf.cli --source-dir . --output "%HTML_OUTPUT%\combined_reports.pdf"
if %errorlevel% neq 0 (
    echo ERROR: HTML to PDF conversion failed!
    pause
    exit /b 1
)
echo.

echo [2/3] Testing DXF to PDF Printer (SMART SPLIT MODE)...
echo ------------------------------------------------------------------------
echo Detecting segments and legend, printing each on separate A4 page...
python -m dxf2pdf.cli . --output-dir "%DXF_OUTPUT%" --split
if %errorlevel% neq 0 (
    echo ERROR: DXF to PDF conversion failed!
    pause
    exit /b 1
)
echo.

echo [3/3] Displaying final results...
echo ------------------------------------------------------------------------
echo.
echo HTML CONVERSION RESULTS:
echo ------------------------
dir "%HTML_OUTPUT%\*.pdf" 2>nul
echo.
echo DXF CONVERSION RESULTS:
echo -----------------------
dir "%DXF_OUTPUT%\*.pdf" 2>nul
echo.

echo ========================================================================
echo  TEST COMPLETE - ALL CONVERSIONS SUCCESSFUL!
echo ========================================================================
echo.
echo Output locations:
echo   - HTML PDFs: %HTML_OUTPUT%\
echo   - DXF PDFs:  %DXF_OUTPUT%\
echo.
echo Usage:
echo   1. HTML to PDF: python -m html2pdf.cli --source-dir [dir] --output [file]
echo   2. DXF to PDF:  python -m dxf2pdf.cli [input] --output-dir [dir] --pages [1-5]
echo.
echo See README.md for detailed documentation.
echo.

pause

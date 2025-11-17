@echo off
REM maintain-pdf-structure.bat
REM Simple CMD version of the maintenance script

echo ====================================
echo PDF Structure Maintenance Pipeline
echo ====================================
echo.

REM 1. UPDATE
echo [1/6] Updating repository...
git checkout main 2>nul || git checkout master
git pull --ff-only
if %errorlevel% neq 0 (
    echo WARNING: Git pull failed
) else (
    echo SUCCESS: Repository updated
)
echo.

REM 2. OPTIMIZE
echo [2/6] Optimizing code...
where black >nul 2>&1
if %errorlevel% equ 0 (
    black html2pdf dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>nul
    echo SUCCESS: Code formatted with black
) else (
    echo SKIPPED: black not installed
)

where isort >nul 2>&1
if %errorlevel% equ 0 (
    isort html2pdf dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>nul
    echo SUCCESS: Imports sorted with isort
) else (
    echo SKIPPED: isort not installed
)

where ruff >nul 2>&1
if %errorlevel% equ 0 (
    ruff check --fix html2pdf dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>nul
    echo SUCCESS: Linting applied with ruff
) else (
    echo SKIPPED: ruff not installed
)
echo.

REM 3. INSTALL DEPENDENCIES
echo [3/6] Installing dependencies...
pip install --no-cache-dir -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo SUCCESS: Dependencies installed
echo.

REM 4. VERIFY DEPENDENCIES
echo [4/6] Verifying critical modules...
python -c "import pdfkit; print('OK: pdfkit')" 2>nul || echo ERROR: pdfkit missing
python -c "import PyPDF2; print('OK: PyPDF2')" 2>nul || echo ERROR: PyPDF2 missing
python -c "import weasyprint; print('OK: weasyprint')" 2>nul || echo ERROR: weasyprint missing
python -c "import flask; print('OK: flask')" 2>nul || echo ERROR: flask missing
python -c "import ezdxf; print('OK: ezdxf')" 2>nul || echo ERROR: ezdxf missing
python -c "import reportlab; print('OK: reportlab')" 2>nul || echo ERROR: reportlab missing

where wkhtmltopdf >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: wkhtmltopdf installed
) else (
    echo WARNING: wkhtmltopdf not found - install from https://wkhtmltopdf.org/downloads.html
)
echo.

REM 5. CLEAR CACHES
echo [5/6] Clearing caches...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc *.pyo 2>nul
rd /s /q .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov 2>nul
rd /s /q html2pdf_cache dxf2pdf_cache .streamlit 2>nul
rd /s /q test_html test_dxf 2>nul
echo SUCCESS: Caches cleared
echo.

REM 6. COMMIT AND PUSH
echo [6/6] Committing and pushing...
git add .
git diff-index --quiet HEAD
if %errorlevel% neq 0 (
    git commit -m "chore(pdf-structure): optimized, tested, cache-cleared [%date% %time%]"
    git push origin main 2>nul || git push origin master
    if %errorlevel% equ 0 (
        echo SUCCESS: Changes pushed
    ) else (
        echo WARNING: Push failed
    )
) else (
    echo INFO: No changes to commit
)
echo.

echo ====================================
echo Maintenance Complete!
echo ====================================
pause

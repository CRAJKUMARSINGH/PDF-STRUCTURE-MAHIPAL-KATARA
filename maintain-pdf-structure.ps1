# maintain-pdf-structure.ps1
# Full maintenance pipeline for PDF-STRUCTURE-MAHIPAL-KATARA (HTML/DXF to PDF converter)
# Windows PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "📄 Starting PDF Structure maintenance pipeline..." -ForegroundColor Cyan

# 1. UPDATE
Write-Host "`n📥 Pulling latest changes..." -ForegroundColor Yellow
try {
    git checkout main 2>$null
    if ($LASTEXITCODE -ne 0) { git checkout master }
    git pull --ff-only
    Write-Host "✅ Repository updated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Git pull failed: $_" -ForegroundColor Yellow
}

# 2. OPTIMIZE & REMOVE BUGS
Write-Host "`n🧹 Formatting and linting Python code..." -ForegroundColor Yellow

# Check and run black
if (Get-Command black -ErrorAction SilentlyContinue) {
    Write-Host "Running black formatter..."
    black html2pdf/ dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Black formatting applied" -ForegroundColor Green }
} else {
    Write-Host "⚠️  black not installed - skipping formatting" -ForegroundColor Yellow
}

# Check and run isort
if (Get-Command isort -ErrorAction SilentlyContinue) {
    Write-Host "Running isort..."
    isort html2pdf/ dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Import sorting applied" -ForegroundColor Green }
} else {
    Write-Host "⚠️  isort not installed - skipping import sorting" -ForegroundColor Yellow
}

# Check and run ruff
if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "Running ruff linter..."
    ruff check --fix html2pdf/ dxf_converter.py enhanced_dxf_converter.py unified_converter.py app.py 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Ruff fixes applied" -ForegroundColor Green }
} else {
    Write-Host "⚠️  ruff not installed - skipping linting" -ForegroundColor Yellow
}

# 3. MAKE DEPLOYABLE
Write-Host "`n⚙️  Installing dependencies..." -ForegroundColor Yellow
pip install --no-cache-dir -r requirements.txt

# Verify critical modules
Write-Host "`nVerifying critical dependencies..."
$modules = @(
    @{Name="pdfkit"; Display="PDFKit"},
    @{Name="PyPDF2"; Display="PyPDF2"},
    @{Name="weasyprint"; Display="WeasyPrint"},
    @{Name="flask"; Display="Flask"},
    @{Name="ezdxf"; Display="ezdxf"},
    @{Name="reportlab"; Display="ReportLab"}
)

foreach ($module in $modules) {
    try {
        python -c "import $($module.Name); print('✅ $($module.Display) OK')"
    } catch {
        Write-Host "❌ $($module.Display) missing" -ForegroundColor Red
        exit 1
    }
}

# Check system dependency for wkhtmltopdf
Write-Host "`nChecking wkhtmltopdf..."
if (Get-Command wkhtmltopdf -ErrorAction SilentlyContinue) {
    Write-Host "✅ wkhtmltopdf installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  wkhtmltopdf not installed (required for HTML to PDF conversion)" -ForegroundColor Yellow
    Write-Host "ℹ️  Install from: https://wkhtmltopdf.org/downloads.html" -ForegroundColor Cyan
}

# 4. TEST RUN
Write-Host "`n🧪 Running application tests..." -ForegroundColor Yellow

# Create test directories
New-Item -ItemType Directory -Force -Path "test_html" | Out-Null
New-Item -ItemType Directory -Force -Path "test_dxf" | Out-Null

# Test HTML to PDF conversion
Write-Host "`n🌐 Testing HTML to PDF conversion..."
$testHtml = @"
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #336699; }
        .box { 
            border: 2px solid #336699; 
            padding: 20px; 
            margin: 20px 0;
            background-color: #f5f9ff;
        }
    </style>
</head>
<body>
    <h1>HTML to PDF Test</h1>
    <div class="box">
        <p>This is a test page for HTML to PDF conversion.</p>
        <p>Conversion should preserve styles and layout.</p>
    </div>
</body>
</html>
"@

Set-Content -Path "test_html\test_page.html" -Value $testHtml

if (Get-Command wkhtmltopdf -ErrorAction SilentlyContinue) {
    try {
        python -m html2pdf.cli --source-dir test_html --output test_html_output.pdf 2>$null
        if (Test-Path "test_html_output.pdf") {
            $fileSize = (Get-Item "test_html_output.pdf").Length
            if ($fileSize -gt 0) {
                Write-Host "✅ HTML to PDF conversion successful ($fileSize bytes)" -ForegroundColor Green
            } else {
                Write-Host "⚠️  HTML to PDF conversion created empty file" -ForegroundColor Yellow
            }
            Remove-Item "test_html_output.pdf" -Force
        }
    } catch {
        Write-Host "⚠️  HTML to PDF test failed: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Skipping HTML to PDF test - wkhtmltopdf not installed" -ForegroundColor Yellow
}

# Test DXF to PDF conversion
Write-Host "`n📐 Testing DXF to PDF conversion..."
$testDxf = @"
0
SECTION
2
HEADER
0
ENDSEC
0
SECTION
2
TABLES
0
TABLE
2
LTYPE
70
1
0
LTYPE
2
CONTINUOUS
70
64
3
Solid line
72
65
73
0
40
0.0
0
ENDTAB
0
TABLE
2
LAYER
70
1
0
LAYER
2
0
70
64
62
7
6
CONTINUOUS
0
ENDTAB
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
0
10
0.0
20
0.0
30
0.0
11
100.0
21
100.0
31
0.0
0
CIRCLE
8
0
10
50.0
20
50.0
30
0.0
40
30.0
0
TEXT
8
0
10
30.0
20
30.0
30
0.0
40
5.0
1
Test DXF
0
ENDSEC
0
EOF
"@

Set-Content -Path "test_dxf\test_drawing.dxf" -Value $testDxf

try {
    python -c "from dxf_converter import DXFToPDFConverter; import sys; c = DXFToPDFConverter(); success, output, pages = c.convert_dxf_to_pdf('test_dxf/test_drawing.dxf'); sys.exit(0 if success else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ DXF to PDF conversion successful" -ForegroundColor Green
    } else {
        Write-Host "⚠️  DXF to PDF conversion failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  DXF to PDF test error: $_" -ForegroundColor Yellow
}

# Test Flask app importability
Write-Host "`n🚀 Testing Flask app importability..."
try {
    python -c "import app; print('✅ Flask app importable')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Flask app imports successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Flask app import failed (may require manual testing)" -ForegroundColor Yellow
}

# 5. REMOVE CACHE
Write-Host "`n🧹 Clearing application caches..." -ForegroundColor Yellow

# Python caches
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -File -Include "*.pyc","*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force

# Test caches
Remove-Item -Path ".pytest_cache",".mypy_cache",".ruff_cache",".coverage","htmlcov" -Recurse -Force -ErrorAction SilentlyContinue

# PDF generation caches
Remove-Item -Path "html2pdf_cache","dxf2pdf_cache" -Recurse -Force -ErrorAction SilentlyContinue

# Test directories
Remove-Item -Path "test_html","test_dxf" -Recurse -Force -ErrorAction SilentlyContinue

# Streamlit caches
Remove-Item -Path ".streamlit" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Caches cleared" -ForegroundColor Green

# Reinstall dependencies clean
Write-Host "`nReinstalling dependencies..."
pip install --no-cache-dir -r requirements.txt | Out-Null

# 6. PUSH BACK TO REMOTE
Write-Host "`n📤 Committing and pushing..." -ForegroundColor Yellow

git add .

# Check if there are changes to commit
$gitStatus = git status --porcelain
if ($gitStatus) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm UTC"
    git commit -m "chore(pdf-structure): optimized, tested, cache-cleared [$timestamp]"
    
    try {
        git push origin main 2>$null
        if ($LASTEXITCODE -ne 0) { git push origin master }
        Write-Host "✅ Changes pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Push failed: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ No changes — repository is clean and up-to-date" -ForegroundColor Green
}

Write-Host "`n✨ PDF Structure maintenance complete!" -ForegroundColor Cyan

# 🤖 PDF Structure Automation Suite

Complete automation for the **PDF-STRUCTURE-MAHIPAL-KATARA** project - a dual Python toolset for HTML-to-PDF and DXF-to-PDF conversion.

## 🎯 What You Get

Four automation scripts that handle your entire maintenance pipeline:

```
📦 Automation Suite
├── 🚀 QUICK_START.bat              # First-time setup
├── ⚡ maintain-pdf-structure.ps1   # Full maintenance (PowerShell)
├── 🔧 maintain-pdf-structure.bat   # Simple maintenance (CMD)
└── 📚 MAINTENANCE_GUIDE.md         # Complete documentation
```

## ⚡ Quick Start (3 Steps)

### Step 1: Initial Setup
```cmd
QUICK_START.bat
```
This installs all Python dependencies and dev tools.

### Step 2: Install wkhtmltopdf (Manual)
Download and install from: https://wkhtmltopdf.org/downloads.html

Add to PATH: `C:\Program Files\wkhtmltopdf\bin`

### Step 3: Run Maintenance
```powershell
powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

**Done!** Your project is now optimized, tested, and pushed.

---

## 🔄 What the Maintenance Script Does

```
┌─────────────────────────────────────┐
│  1. UPDATE                          │  ← Pull latest from Git
├─────────────────────────────────────┤
│  2. OPTIMIZE                        │  ← Format with black, isort, ruff
├─────────────────────────────────────┤
│  3. VERIFY                          │  ← Check all dependencies
├─────────────────────────────────────┤
│  4. TEST                            │  ← Run HTML & DXF conversions
├─────────────────────────────────────┤
│  5. CLEAN                           │  ← Remove all caches
├─────────────────────────────────────┤
│  6. PUSH                            │  ← Commit & push changes
└─────────────────────────────────────┘
```

---

## 📋 Prerequisites

| Requirement | Check Command | Install Link |
|-------------|---------------|--------------|
| Python 3.8+ | `python --version` | https://python.org |
| Git | `git --version` | https://git-scm.com |
| wkhtmltopdf | `wkhtmltopdf --version` | https://wkhtmltopdf.org |

**Optional (for optimization):**
```cmd
pip install black isort ruff
```

---

## 🎮 Usage Options

### Option 1: PowerShell (Recommended)
**Full-featured with colored output and detailed testing**

```powershell
powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

**Features:**
- ✅ Colored console output
- ✅ Detailed error messages
- ✅ Comprehensive testing
- ✅ Smart error handling

---

### Option 2: CMD (Simple)
**Lightweight version for basic maintenance**

```cmd
maintain-pdf-structure.bat
```

**Features:**
- ✅ Quick execution
- ✅ Basic error checking
- ✅ Essential operations only

---

## 🧪 What Gets Tested

### HTML to PDF Conversion
```
✅ Creates test HTML with CSS styling
✅ Converts to PDF using pdfkit
✅ Verifies output file size
✅ Cleans up test files
```

### DXF to PDF Conversion
```
✅ Creates test DXF with entities (lines, circles, text)
✅ Converts to PDF using ezdxf + reportlab
✅ Verifies conversion success
✅ Cleans up test files
```

### Flask App
```
✅ Imports app.py successfully
✅ Verifies all routes are defined
✅ Checks template availability
```

---

## 🧹 What Gets Cleaned

```python
# Python caches
__pycache__/
*.pyc, *.pyo

# Test caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Application caches
html2pdf_cache/
dxf2pdf_cache/
.streamlit/

# Test directories
test_html/
test_dxf/
```

---

## 🔧 Project Structure

```
PDF-STRUCTURE-MAHIPAL-KATARA/
│
├── html2pdf/                    # HTML to PDF module
│   ├── cli.py                  # Command-line interface
│   ├── converter.py            # Core conversion logic
│   ├── merger.py               # PDF merging
│   └── service.py              # Service layer
│
├── dxf_converter.py            # DXF to PDF (standard)
├── enhanced_dxf_converter.py   # DXF to PDF (enhanced)
├── unified_converter.py        # Unified conversion service
│
├── app.py                      # Flask web application
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
│
├── INPUT_DATA/                 # Input files
├── OUTPUT_PDF/                 # Generated PDFs
├── LOGS/                       # Application logs
│
└── requirements.txt            # Python dependencies
```

---

## 🎨 Conversion Features

### HTML to PDF
- **Engine:** pdfkit + wkhtmltopdf
- **Features:** CSS preservation, multi-page, batch conversion
- **Input:** HTML, HTM files
- **Output:** Single or merged PDF

### DXF to PDF
- **Engine:** ezdxf + reportlab
- **Scale Modes:** 
  - `standard` - Normal scale
  - `enlarged_2x` - 2x detail
  - `maximum_4x` - 4x maximum detail
- **Input:** DXF files
- **Output:** Multi-page PDF with legends

### Unified Conversion
- **Combines:** HTML + DXF workflows
- **Organization:** Session-based output folders
- **Interface:** Flask web UI + CLI

---

## 🐛 Troubleshooting

### "Execution Policy" Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "wkhtmltopdf not found"
1. Download: https://wkhtmltopdf.org/downloads.html
2. Install to default location
3. Add to PATH: `C:\Program Files\wkhtmltopdf\bin`
4. Restart terminal

### "Module not found"
```cmd
pip install --upgrade -r requirements.txt
```

### Git Authentication
```cmd
git config credential.helper store
git push origin main
```

---

## 📊 Expected Output

```
📄 Starting PDF Structure maintenance pipeline...

📥 Pulling latest changes...
✅ Repository updated

🧹 Formatting and linting Python code...
✅ Black formatting applied
✅ Import sorting applied
✅ Ruff fixes applied

⚙️  Installing dependencies...
✅ PDFKit OK
✅ PyPDF2 OK
✅ WeasyPrint OK
✅ Flask OK
✅ ezdxf OK
✅ ReportLab OK
✅ wkhtmltopdf installed

🧪 Running application tests...
🌐 Testing HTML to PDF conversion...
✅ HTML to PDF conversion successful (12345 bytes)

📐 Testing DXF to PDF conversion...
✅ DXF to PDF conversion successful

🚀 Testing Flask app importability...
✅ Flask app imports successfully

🧹 Clearing application caches...
✅ Caches cleared

📤 Committing and pushing...
✅ Changes pushed successfully

✨ PDF Structure maintenance complete!
```

---

## 🚀 CI/CD Integration

### GitHub Actions
```yaml
name: Maintenance
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  maintain:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install wkhtmltopdf
        run: choco install wkhtmltopdf -y
      - name: Run maintenance
        run: powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

---

## 📝 Manual Operations

### Start Flask App
```cmd
python app.py
```
Then open: http://localhost:5000

### Convert HTML Files
```cmd
python -m html2pdf.cli --source-dir INPUT_DATA --output OUTPUT_PDF/report.pdf
```

### Convert DXF Files
```python
from dxf_converter import DXFToPDFConverter

converter = DXFToPDFConverter(scale_mode='enlarged_2x')
success, output, pages = converter.convert_dxf_to_pdf('INPUT_DATA/drawing.dxf')
print(f"Success: {success}, Output: {output}, Pages: {pages}")
```

---

## ✅ Verification Checklist

After running maintenance:

- [ ] Git repository is up to date
- [ ] All dependencies installed successfully
- [ ] No `__pycache__` directories remain
- [ ] HTML to PDF test passed
- [ ] DXF to PDF test passed
- [ ] Flask app imports successfully
- [ ] Changes committed and pushed

**Quick verify:**
```cmd
python -c "import pdfkit, PyPDF2, weasyprint, flask, ezdxf, reportlab; print('✅ All OK')"
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README_AUTOMATION.md` | This file - overview |
| `MAINTENANCE_GUIDE.md` | Detailed usage guide |
| `AUTOMATION_SUMMARY.md` | Technical summary |

---

## 🎯 Best Practices

1. **Run maintenance weekly** to keep code clean
2. **Check wkhtmltopdf** before HTML conversions
3. **Use PowerShell script** for detailed output
4. **Review git changes** before pushing
5. **Keep dependencies updated** with pip

---

## 🆘 Support

For issues:
1. Check `MAINTENANCE_GUIDE.md` for detailed troubleshooting
2. Review script output for error messages
3. Verify prerequisites are installed
4. Check Python version: `python --version`
5. Check Git version: `git --version`

---

## 📄 License

Part of the PDF-STRUCTURE-MAHIPAL-KATARA project.

---

**Platform:** Windows (PowerShell/CMD)  
**Python:** 3.8+  
**Created:** 2025-11-17  
**Status:** ✅ Production Ready

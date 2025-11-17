# PDF Structure Maintenance Guide

Complete automation script for the **PDF-STRUCTURE-MAHIPAL-KATARA** project.

## 🎯 What This Script Does

The `maintain-pdf-structure.ps1` script automates your entire maintenance pipeline:

1. **Update** - Pulls latest changes from Git
2. **Optimize** - Formats code with black, isort, and ruff
3. **Remove Bugs** - Validates all critical dependencies
4. **Make Deployable** - Installs requirements and checks system dependencies
5. **Test Run** - Creates and runs test conversions for HTML and DXF
6. **Remove Cache** - Clears all Python and application caches
7. **Push** - Commits and pushes changes back to repository

## 📋 Prerequisites

### Required Software

1. **Python 3.8+**
   ```powershell
   python --version
   ```

2. **Git**
   ```powershell
   git --version
   ```

3. **wkhtmltopdf** (for HTML to PDF conversion)
   - Download from: https://wkhtmltopdf.org/downloads.html
   - Install and add to PATH

### Optional Dev Tools (for optimization)

```powershell
pip install black isort ruff
```

## 🚀 Quick Start

### 1. Open PowerShell in Project Directory

```powershell
cd path\to\PDF-STRUCTURE-MAHIPAL-KATARA
```

### 2. Run the Maintenance Script

```powershell
powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

Or if execution policy allows:

```powershell
.\maintain-pdf-structure.ps1
```

## 📦 Project Structure

```
PDF-STRUCTURE-MAHIPAL-KATARA/
├── html2pdf/              # HTML to PDF conversion module
│   ├── cli.py            # Command-line interface
│   ├── converter.py      # Core conversion logic
│   ├── merger.py         # PDF merging utilities
│   └── service.py        # Service layer
├── dxf_converter.py       # DXF to PDF converter (standard)
├── enhanced_dxf_converter.py  # Enhanced DXF converter
├── unified_converter.py   # Unified conversion service
├── app.py                # Flask web application
├── INPUT_DATA/           # Input files directory
├── OUTPUT_PDF/           # Generated PDFs directory
├── templates/            # Flask HTML templates
├── static/               # Static web assets
└── requirements.txt      # Python dependencies
```

## 🔧 Manual Steps (If Needed)

### Install Dependencies Only

```powershell
pip install -r requirements.txt
```

### Run Flask App

```powershell
python app.py
```

Then open: http://localhost:5000

### Convert HTML Files

```powershell
python -m html2pdf.cli --source-dir INPUT_DATA --output OUTPUT_PDF/report.pdf
```

### Convert DXF Files

```python
from dxf_converter import DXFToPDFConverter

converter = DXFToPDFConverter(scale_mode='standard')
success, output, pages = converter.convert_dxf_to_pdf('INPUT_DATA/drawing.dxf')
```

## 🧪 Testing

The maintenance script automatically runs tests, but you can run them manually:

### Test HTML Conversion

```powershell
python test_html_conversion.py
```

### Test DXF Conversion

```powershell
python test_3_scale_options.py
```

### Test Unified System

```powershell
python demo_unified_system.py
```

## 🐛 Troubleshooting

### wkhtmltopdf Not Found

**Error:** `wkhtmltopdf not installed`

**Solution:**
1. Download from https://wkhtmltopdf.org/downloads.html
2. Install to default location
3. Add to PATH: `C:\Program Files\wkhtmltopdf\bin`
4. Restart PowerShell

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'pdfkit'`

**Solution:**
```powershell
pip install --upgrade -r requirements.txt
```

### Git Push Fails

**Error:** `Push failed: authentication required`

**Solution:**
```powershell
git config credential.helper store
git push origin main
```

### Execution Policy Error

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Scale Options

The DXF converter supports 3 scale modes:

- **standard** - Standard scale (default)
- **enlarged_2x** - 2x enlarged scale for better detail
- **maximum_4x** - 4x maximum detail for complex drawings

## 🔄 CI/CD Integration

To run this in a CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
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
      - name: Run maintenance
        run: powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

## 📝 Notes

- The script creates temporary test files in `test_html/` and `test_dxf/` directories
- All caches are cleared including `__pycache__`, `.pytest_cache`, and Streamlit caches
- Git commits are timestamped with UTC time
- The script exits with error code 1 if critical dependencies are missing

## 🆘 Support

For issues specific to:
- **HTML conversion**: Check `html2pdf/` module
- **DXF conversion**: Check `dxf_converter.py`
- **Web interface**: Check `app.py` and `templates/`
- **Dependencies**: Check `requirements.txt`

## 📄 License

This maintenance script is part of the PDF-STRUCTURE-MAHIPAL-KATARA project.

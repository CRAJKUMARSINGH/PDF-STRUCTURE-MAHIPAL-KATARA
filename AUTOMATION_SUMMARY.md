# Automation Scripts Summary

## 📦 Created Files

### 1. `maintain-pdf-structure.ps1` (PowerShell - Recommended)
**Full-featured maintenance script with colored output and detailed error handling**

**Features:**
- ✅ Git update with fallback to master branch
- ✅ Code formatting (black, isort, ruff)
- ✅ Dependency installation and verification
- ✅ Automated testing (HTML & DXF conversion)
- ✅ Cache clearing (Python, pytest, Streamlit)
- ✅ Smart git commit with UTC timestamp
- ✅ Colored console output
- ✅ Comprehensive error handling

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
```

---

### 2. `maintain-pdf-structure.bat` (CMD - Simple Alternative)
**Lightweight CMD version for basic maintenance**

**Features:**
- ✅ Git update
- ✅ Code optimization (if tools installed)
- ✅ Dependency installation
- ✅ Module verification
- ✅ Cache clearing
- ✅ Git commit and push

**Usage:**
```cmd
maintain-pdf-structure.bat
```

---

### 3. `QUICK_START.bat` (Initial Setup)
**One-time setup script for new installations**

**Features:**
- ✅ Python version check
- ✅ Git installation check
- ✅ Dependency installation
- ✅ Dev tools installation (black, isort, ruff)
- ✅ wkhtmltopdf verification
- ✅ Directory creation

**Usage:**
```cmd
QUICK_START.bat
```

---

### 4. `MAINTENANCE_GUIDE.md` (Documentation)
**Complete guide for using the automation scripts**

**Contents:**
- Project structure overview
- Prerequisites and installation
- Usage instructions
- Manual operation steps
- Troubleshooting guide
- CI/CD integration examples

---

## 🚀 Quick Start Workflow

### First Time Setup
```cmd
1. QUICK_START.bat          # Install everything
2. Install wkhtmltopdf      # Manual step (see guide)
3. Restart terminal         # Refresh PATH
```

### Daily Maintenance
```powershell
maintain-pdf-structure.ps1  # Run full pipeline
```

### Simple Maintenance (CMD)
```cmd
maintain-pdf-structure.bat  # Lighter version
```

---

## 🎯 Pipeline Steps

Each maintenance script executes these steps:

| Step | Action | Tools Used |
|------|--------|------------|
| 1. Update | Pull latest from Git | `git pull` |
| 2. Optimize | Format and lint code | `black`, `isort`, `ruff` |
| 3. Verify | Check dependencies | `pip`, `python -c` |
| 4. Test | Run conversion tests | Custom test code |
| 5. Clean | Remove caches | File system operations |
| 6. Push | Commit and push | `git commit`, `git push` |

---

## 📊 Project-Specific Features

### HTML to PDF Conversion
- Uses `pdfkit` and `weasyprint`
- Requires `wkhtmltopdf` system binary
- Supports batch conversion
- Preserves CSS styling

### DXF to PDF Conversion
- Uses `ezdxf` and `reportlab`
- Three scale modes: standard, 2x, 4x
- Multi-page support
- CAD entity preservation

### Unified Conversion
- Combines HTML and DXF workflows
- Session-based output organization
- Flask web interface
- Batch processing support

---

## 🔧 Customization

### Add Custom Tests
Edit the test section in `maintain-pdf-structure.ps1`:

```powershell
# Add your custom test
Write-Host "Running custom test..."
python your_test_script.py
```

### Change Git Branch
Modify the update section:

```powershell
git checkout your-branch-name
git pull --ff-only
```

### Skip Optimization
Comment out the formatting section:

```powershell
# Write-Host "🧹 Formatting..." -ForegroundColor Yellow
# black html2pdf/ ...
```

---

## 🐛 Common Issues

### Issue: "Execution Policy" Error
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "wkhtmltopdf not found"
**Solution:**
1. Download: https://wkhtmltopdf.org/downloads.html
2. Install to: `C:\Program Files\wkhtmltopdf`
3. Add to PATH: `C:\Program Files\wkhtmltopdf\bin`
4. Restart terminal

### Issue: "Module not found"
**Solution:**
```cmd
pip install --upgrade -r requirements.txt
```

### Issue: Git push authentication
**Solution:**
```cmd
git config credential.helper store
git push origin main
```

---

## 📈 CI/CD Integration

### GitHub Actions Example
```yaml
name: Maintenance
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
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

### Azure DevOps Example
```yaml
trigger:
  - main

pool:
  vmImage: 'windows-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
- script: powershell -ExecutionPolicy Bypass -File maintain-pdf-structure.ps1
  displayName: 'Run Maintenance'
```

---

## 📝 Notes

- All scripts are Windows-compatible (PowerShell/CMD)
- PowerShell script has better error handling and output
- CMD script is simpler but less feature-rich
- Both scripts are safe to run multiple times
- No data loss - only clears caches and temporary files
- Git commits are timestamped automatically

---

## 🆘 Support

For issues:
1. Check `MAINTENANCE_GUIDE.md` for detailed troubleshooting
2. Review script output for specific error messages
3. Verify all prerequisites are installed
4. Check Python and Git versions

---

## ✅ Verification

After running maintenance, verify:
- [ ] Git repository is up to date
- [ ] All dependencies are installed
- [ ] No Python cache files remain
- [ ] Tests pass successfully
- [ ] Changes are committed and pushed

Run verification:
```powershell
python -c "import pdfkit, PyPDF2, weasyprint, flask, ezdxf, reportlab; print('All modules OK')"
```

---

**Created for:** PDF-STRUCTURE-MAHIPAL-KATARA  
**Platform:** Windows (PowerShell/CMD)  
**Python:** 3.8+  
**Last Updated:** 2025-11-17

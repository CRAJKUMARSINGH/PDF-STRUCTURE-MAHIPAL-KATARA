#!/usr/bin/env python3
"""
Project Status Checker
Comprehensive health check for the DXF to PDF conversion project.
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'ezdxf',
        'reportlab',
        'requests'
    ]
    
    print("📦 Checking Dependencies:")
    missing = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"   ❌ {package} - Not installed")
                missing.append(package)
            else:
                print(f"   ✅ {package} - Available")
        except ImportError:
            print(f"   ❌ {package} - Import error")
            missing.append(package)
    
    return missing

def check_project_structure():
    """Check if project files are in place."""
    print("\n📁 Checking Project Structure:")
    
    required_files = [
        'dxf2pdf/__init__.py',
        'dxf2pdf/cli.py',
        'dxf2pdf/renderer.py',
        'dxf2pdf/parser.py',
        'dxf2pdf/geometry.py',
        'dxf2pdf/scale.py',
        'dxf2pdf/scanner.py',
        'dxf2pdf/reporter.py',
        'convert_dxf.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return missing_files

def check_dxf_files():
    """Check for available DXF test files."""
    print("\n📐 Checking DXF Test Files:")
    
    dxf_files = [
        'LIBRBeamSections011.DXF',
        'LIBRColumnCenterLineSht.DXF', 
        'LIBRdoubleLinesht011.DXF',
        'LIBRFootingCenterLineSht.DXF',
        'LIBRFootingSections.DXF',
        'LIBRslablongsection011.DXF',
        'LIBRslablongsectionbothrf011.DXF',
        'LIBRslabsht011.DXF'
    ]
    
    available = []
    
    for dxf_file in dxf_files:
        path = Path(dxf_file)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"   ✅ {dxf_file} ({size_kb:.1f} KB)")
            available.append(dxf_file)
        else:
            print(f"   ❌ {dxf_file} - Not found")
    
    return available

def test_conversion():
    """Test DXF to PDF conversion."""
    print("\n🔄 Testing DXF Conversion:")
    
    # Check if we can import the module
    try:
        from dxf2pdf.cli import convert_dxf_file
        print("   ✅ DXF2PDF module imports successfully")
    except ImportError as e:
        print(f"   ❌ Cannot import DXF2PDF module: {e}")
        return False
    
    # Find a test DXF file
    test_files = ['LIBRBeamSections011.DXF', 'LIBRslabsht011.DXF']
    test_file = None
    
    for file in test_files:
        if Path(file).exists():
            test_file = file
            break
    
    if not test_file:
        print("   ⚠️  No test DXF files available")
        return False
    
    try:
        # Test conversion
        dxf_path = Path(test_file)
        pdf_path = Path(f"test_output_{dxf_path.stem}.pdf")
        
        success = convert_dxf_file(dxf_path, pdf_path, num_pages=1, use_split=False)
        
        if success and pdf_path.exists():
            size_kb = pdf_path.stat().st_size / 1024
            print(f"   ✅ Conversion successful: {pdf_path} ({size_kb:.1f} KB)")
            return True
        else:
            print("   ❌ Conversion failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Conversion error: {e}")
        return False

def check_git_status():
    """Check git repository status."""
    print("\n📋 Git Repository Status:")
    
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("   ⚠️  Uncommitted changes detected")
                print("   📝 Run 'git status' for details")
            else:
                print("   ✅ Working directory clean")
            
            # Check remote
            remote_result = subprocess.run(['git', 'remote', '-v'], 
                                         capture_output=True, text=True, timeout=10)
            if remote_result.returncode == 0 and remote_result.stdout:
                print("   ✅ Git remote configured")
            else:
                print("   ⚠️  No git remote configured")
                
        else:
            print("   ❌ Not a git repository")
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Git not available")

def main():
    """Main status check function."""
    print("="*60)
    print("🔍 DXF TO PDF PROJECT - STATUS CHECK")
    print("="*60)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    # Check project structure
    missing_files = check_project_structure()
    
    # Check DXF files
    available_dxf = check_dxf_files()
    
    # Test conversion
    conversion_works = test_conversion()
    
    # Check git status
    check_git_status()
    
    # Summary
    print("\n" + "="*60)
    print("📊 PROJECT STATUS SUMMARY")
    print("="*60)
    
    if not missing_deps:
        print("✅ All dependencies installed")
    else:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
    
    if not missing_files:
        print("✅ All project files present")
    else:
        print(f"❌ Missing files: {len(missing_files)}")
    
    print(f"📐 DXF test files available: {len(available_dxf)}")
    
    if conversion_works:
        print("✅ DXF to PDF conversion working")
    else:
        print("❌ DXF to PDF conversion issues")
    
    # Overall status
    overall_ok = (not missing_deps and not missing_files and 
                  len(available_dxf) > 0 and conversion_works)
    
    print("\n" + "="*60)
    if overall_ok:
        print("🎉 PROJECT STATUS: HEALTHY ✅")
        print("Ready for deployment and use!")
    else:
        print("⚠️  PROJECT STATUS: NEEDS ATTENTION ❌")
        print("Please address the issues above.")
    print("="*60)
    
    return overall_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
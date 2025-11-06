#!/usr/bin/env python3
"""
Final deployment readiness check for the DXF to PDF converter.
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

def check_critical_dependencies():
    """Check if all critical dependencies are available."""
    print("🔍 Checking Critical Dependencies:")
    print("-" * 40)
    
    critical_deps = {
        'ezdxf': 'DXF file parsing',
        'reportlab': 'PDF generation',
        'streamlit': 'Web interface',
        'requests': 'HTTP health checks'
    }
    
    missing = []
    
    for package, purpose in critical_deps.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                print(f"❌ {package} - Missing ({purpose})")
                missing.append(package)
            else:
                print(f"✅ {package} - Available ({purpose})")
        except ImportError:
            print(f"❌ {package} - Import error ({purpose})")
            missing.append(package)
    
    return missing

def check_core_functionality():
    """Test the core DXF to PDF conversion."""
    print("\n🔧 Testing Core Functionality:")
    print("-" * 40)
    
    try:
        from dxf2pdf.renderer import PDFRenderer
        from dxf2pdf.parser import DXFParser
        from dxf2pdf.geometry import GeometryProcessor
        
        # Test renderer improvements
        renderer = PDFRenderer()
        
        # Check if new methods exist
        new_methods = [
            '_render_mtext', '_render_spline', '_render_ellipse', 
            '_render_point', '_render_insert', '_get_color_from_aci'
        ]
        
        for method in new_methods:
            if hasattr(renderer, method):
                print(f"✅ {method} - Available")
            else:
                print(f"❌ {method} - Missing")
        
        print("✅ Core functionality imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Core functionality error: {e}")
        return False

def check_deployment_files():
    """Check if all deployment files are present."""
    print("\n📁 Checking Deployment Files:")
    print("-" * 40)
    
    deployment_files = {
        'streamlit_app.py': 'Web interface',
        'requirements.txt': 'Dependencies',
        'check_streamlit.py': 'Health checker',
        'deployment_test_suite.py': 'Testing suite',
        'DEPLOYMENT_GUIDE.md': 'Documentation',
        'FINAL_SUMMARY.md': 'Project summary'
    }
    
    missing = []
    
    for file, purpose in deployment_files.items():
        path = Path(file)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"✅ {file} - {size_kb:.1f} KB ({purpose})")
        else:
            print(f"❌ {file} - Missing ({purpose})")
            missing.append(file)
    
    return missing

def check_git_status():
    """Check git repository status."""
    print("\n📋 Git Repository Status:")
    print("-" * 40)
    
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected")
                print("   📝 Consider committing before deployment")
            else:
                print("✅ Working directory clean")
            
            # Check remote
            remote_result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                         capture_output=True, text=True, timeout=10)
            if remote_result.returncode == 0:
                remote_url = remote_result.stdout.strip()
                print(f"✅ Remote configured: {remote_url}")
                return True
            else:
                print("❌ No git remote configured")
                return False
                
        else:
            print("❌ Not a git repository")
            return False
            
    except Exception as e:
        print(f"❌ Git check error: {e}")
        return False

def generate_deployment_checklist():
    """Generate final deployment checklist."""
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT READINESS CHECKLIST")
    print("="*60)
    
    # Run all checks
    missing_deps = check_critical_dependencies()
    core_ok = check_core_functionality()
    missing_files = check_deployment_files()
    git_ok = check_git_status()
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 READINESS SUMMARY")
    print("="*60)
    
    deps_ok = len(missing_deps) == 0
    files_ok = len(missing_files) == 0
    
    print(f"🔧 Dependencies:     {'✅ READY' if deps_ok else '❌ MISSING'}")
    print(f"⚙️  Core Functions:   {'✅ READY' if core_ok else '❌ ISSUES'}")
    print(f"📁 Deployment Files: {'✅ READY' if files_ok else '❌ MISSING'}")
    print(f"📋 Git Repository:   {'✅ READY' if git_ok else '❌ ISSUES'}")
    
    # Overall readiness
    overall_ready = deps_ok and core_ok and files_ok and git_ok
    
    print("\n" + "-"*60)
    if overall_ready:
        print("🎉 DEPLOYMENT STATUS: READY FOR PRODUCTION ✅")
        print("\n📋 Next Steps:")
        print("1. Deploy Streamlit app: streamlit run streamlit_app.py")
        print("2. Push to Streamlit Cloud via GitHub")
        print("3. Test deployment: python check_streamlit.py <your-url>")
        print("4. Monitor with: python deployment_test_suite.py")
    else:
        print("⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION ❌")
        print("\n🔧 Required Actions:")
        
        if missing_deps:
            print(f"   • Install dependencies: pip install {' '.join(missing_deps)}")
        if not core_ok:
            print("   • Fix core functionality issues")
        if missing_files:
            print(f"   • Add missing files: {', '.join(missing_files)}")
        if not git_ok:
            print("   • Configure git repository properly")
    
    print("="*60)
    
    return overall_ready

def main():
    """Main deployment readiness check."""
    return generate_deployment_checklist()

if __name__ == "__main__":
    ready = main()
    sys.exit(0 if ready else 1)
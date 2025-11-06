#!/usr/bin/env python3
"""Demonstration of the unified conversion system."""

from pathlib import Path
from unified_converter import UnifiedConverter
import time

def demo_unified_system():
    """Demonstrate the unified conversion system."""
    print("🎬 UNIFIED CONVERSION SYSTEM DEMONSTRATION")
    print("="*70)
    
    # Show current input files
    input_folder = Path("INPUT_DATA")
    html_files = list(input_folder.glob("*.html")) + list(input_folder.glob("*.htm"))
    dxf_files = list(input_folder.glob("*.dxf")) + list(input_folder.glob("*.DXF"))
    
    print(f"📁 INPUT FILES AVAILABLE:")
    print(f"   📄 HTML files: {len(html_files)}")
    for f in html_files[:5]:  # Show first 5
        print(f"      • {f.name}")
    if len(html_files) > 5:
        print(f"      ... and {len(html_files) - 5} more")
    
    print(f"   🏗️  DXF files: {len(dxf_files)}")
    for f in dxf_files[:5]:  # Show first 5
        print(f"      • {f.name}")
    if len(dxf_files) > 5:
        print(f"      ... and {len(dxf_files) - 5} more")
    
    if not html_files and not dxf_files:
        print("\n⚠️  No files found for demonstration.")
        print("   Please add some HTML or DXF files to the INPUT_DATA folder.")
        return
    
    print(f"\n🚀 STARTING UNIFIED CONVERSION...")
    print("   This will create organized output folders with date stamps:")
    print("   📂 OUTPUT_PDF/")
    print("      ├── HTML_REPORTS/session_YYYY-MM-DD_HH-MM-SS/")
    print("      ├── DXF_DRAWINGS/session_YYYY-MM-DD_HH-MM-SS/")
    print("      └── CONVERSION_LOGS/session_YYYY-MM-DD_HH-MM-SS/")
    
    # Initialize and run converter
    converter = UnifiedConverter()
    results = converter.convert_all_files()
    
    # Show results
    if results['summary']['overall_success']:
        print(f"\n🎉 DEMONSTRATION SUCCESSFUL!")
        print(f"   Session ID: {results['session_id']}")
        print(f"   Check the organized folders in OUTPUT_PDF/")
        
        # Show what was created
        session_folders = results['output_folders']
        for folder_type, folder_path in session_folders.items():
            folder = Path(folder_path)
            if folder.exists():
                files = list(folder.glob('*'))
                print(f"   📁 {folder_type.upper()}: {len(files)} files created")
    else:
        print(f"\n❌ DEMONSTRATION FAILED")
        print(f"   Check the logs for details")

if __name__ == "__main__":
    demo_unified_system()
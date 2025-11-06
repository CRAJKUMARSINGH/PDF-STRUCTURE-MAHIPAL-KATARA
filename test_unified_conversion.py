#!/usr/bin/env python3
"""Test the unified conversion system."""

from pathlib import Path
from unified_converter import UnifiedConverter
import json

def test_unified_conversion():
    """Test the unified conversion system."""
    print("="*70)
    print("🧪 TESTING UNIFIED CONVERSION SYSTEM")
    print("="*70)
    
    # Initialize converter
    converter = UnifiedConverter()
    
    # Get session info
    session_info = converter.get_session_info()
    print(f"📅 Session: {session_info['session_id']}")
    print(f"📁 Input folder: {session_info['input_folder']}")
    print(f"📂 Output folders:")
    for folder_type, path in session_info['output_folders'].items():
        print(f"   {folder_type.upper()}: {path}")
    
    # Scan input files
    input_files = converter.scan_input_files()
    print(f"\n📊 INPUT FILES FOUND:")
    print(f"   HTML files: {len(input_files['html'])}")
    for html_file in input_files['html']:
        print(f"     📄 {html_file}")
    
    print(f"   DXF files: {len(input_files['dxf'])}")
    for dxf_file in input_files['dxf']:
        print(f"     🏗️  {dxf_file}")
    
    if not input_files['html'] and not input_files['dxf']:
        print("\n⚠️  No files to convert. Please add HTML or DXF files to INPUT_DATA folder.")
        return False
    
    # Perform conversion
    print(f"\n🚀 STARTING UNIFIED CONVERSION...")
    results = converter.convert_all_files()
    
    # Verify results
    print(f"\n🔍 VERIFYING RESULTS...")
    
    # Check HTML output
    if results['html_results']:
        html_folder = Path(session_info['output_folders']['html'])
        html_files = list(html_folder.glob('*.pdf'))
        print(f"   HTML PDFs created: {len(html_files)}")
        for pdf_file in html_files:
            size_kb = pdf_file.stat().st_size / 1024
            print(f"     ✅ {pdf_file.name} ({size_kb:.1f} KB)")
    
    # Check DXF output
    if results['dxf_results']:
        dxf_folder = Path(session_info['output_folders']['dxf'])
        dxf_files = list(dxf_folder.glob('*.pdf'))
        print(f"   DXF PDFs created: {len(dxf_files)}")
        for pdf_file in dxf_files:
            size_kb = pdf_file.stat().st_size / 1024
            print(f"     ✅ {pdf_file.name} ({size_kb:.1f} KB)")
    
    # Check logs
    logs_folder = Path(session_info['output_folders']['logs'])
    log_files = list(logs_folder.glob('*.json'))
    print(f"   Log files created: {len(log_files)}")
    for log_file in log_files:
        print(f"     📝 {log_file.name}")
    
    # Display final summary
    summary = results['summary']
    print(f"\n📈 FINAL SUMMARY:")
    print(f"   Overall success: {'✅ YES' if summary['overall_success'] else '❌ NO'}")
    print(f"   Duration: {summary['duration_seconds']:.1f} seconds")
    print(f"   Total PDFs created: {summary['total_pdf_files_created']}")
    print(f"   Total pages generated: {summary['total_pages_generated']}")
    
    return summary['overall_success']

if __name__ == "__main__":
    success = test_unified_conversion()
    print(f"\n{'='*70}")
    print(f"🎯 TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*70}")
    exit(0 if success else 1)
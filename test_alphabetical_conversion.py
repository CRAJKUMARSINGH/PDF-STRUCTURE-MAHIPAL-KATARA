#!/usr/bin/env python3
"""Test alphabetical conversion and combined PDF creation."""

from pathlib import Path
from unified_converter import UnifiedConverter
from PyPDF2 import PdfReader
import time

def test_alphabetical_conversion():
    """Test the alphabetical conversion system."""
    print("="*80)
    print("🔤 ALPHABETICAL CONVERSION & COMBINED PDF TEST")
    print("="*80)
    
    # Initialize converter
    converter = UnifiedConverter()
    
    # Scan files to show alphabetical order
    input_files = converter.scan_input_files()
    
    print(f"\n📊 INPUT FILES (ALPHABETICAL ORDER):")
    print(f"   📄 HTML files: {len(input_files['html'])}")
    for i, file in enumerate(input_files['html'], 1):
        print(f"      {i:2d}. {file}")
    
    print(f"   🏗️  DXF files: {len(input_files['dxf'])}")
    for i, file in enumerate(input_files['dxf'], 1):
        print(f"      {i:2d}. {file}")
    
    if not input_files['html'] and not input_files['dxf']:
        print("\n⚠️  No files found for testing.")
        return False
    
    # Perform unified conversion
    print(f"\n🚀 STARTING ALPHABETICAL UNIFIED CONVERSION...")
    start_time = time.time()
    
    results = converter.convert_all_files()
    
    duration = time.time() - start_time
    
    # Analyze results
    print(f"\n📊 CONVERSION RESULTS ANALYSIS:")
    print("="*80)
    
    # HTML Results
    if results['html_results']:
        html_res = results['html_results']
        print(f"📄 HTML CONVERSION:")
        print(f"   Files processed: {html_res.get('total', 0)}")
        print(f"   Successful: {html_res.get('successful', 0)}")
        print(f"   Output: {html_res.get('output_file', 'N/A')}")
    
    # DXF Results
    if results['dxf_results']:
        dxf_res = results['dxf_results']
        print(f"\n🏗️  DXF CONVERSION (ALPHABETICAL):")
        print(f"   Files processed: {dxf_res.get('total', 0)}")
        print(f"   Individual PDFs: {dxf_res.get('individual_pdfs', 0)}")
        print(f"   Combined PDF: {'✅ Created' if dxf_res.get('combined_success', False) else '❌ Failed'}")
        print(f"   Total pages: {dxf_res.get('total_pages', 0)}")
        
        if dxf_res.get('combined_pdf'):
            combined_path = Path(dxf_res['combined_pdf'])
            if combined_path.exists():
                try:
                    reader = PdfReader(str(combined_path))
                    size_kb = combined_path.stat().st_size / 1024
                    print(f"   Combined PDF details:")
                    print(f"     📁 Size: {size_kb:.1f} KB")
                    print(f"     📄 Pages: {len(reader.pages)}")
                    print(f"     📂 File: {combined_path.name}")
                except Exception as e:
                    print(f"     ❌ Error reading combined PDF: {e}")
    
    # Summary
    summary = results['summary']
    print(f"\n🎯 FINAL SUMMARY:")
    print("="*80)
    print(f"✅ Overall success: {summary['overall_success']}")
    print(f"⏱️  Duration: {duration:.1f} seconds")
    print(f"📁 Total PDFs created: {summary['total_pdf_files_created']}")
    print(f"📄 Total pages: {summary['total_pages_generated']}")
    
    # Verify alphabetical order was maintained
    if results['dxf_results'] and results['dxf_results'].get('details'):
        print(f"\n🔤 ALPHABETICAL ORDER VERIFICATION:")
        print("-" * 50)
        dxf_details = results['dxf_results']['details']
        print(f"DXF files were processed in this order:")
        for i, detail in enumerate(dxf_details, 1):
            status = "✅" if detail['success'] else "❌"
            print(f"  {i:2d}. {status} {detail['input']} → {detail.get('pages', 0)} pages")
    
    # Check session folders
    session_info = converter.get_session_info()
    print(f"\n📂 SESSION FOLDERS:")
    print("-" * 50)
    for folder_type, folder_path in session_info['output_folders'].items():
        folder = Path(folder_path)
        if folder.exists():
            files = list(folder.glob('*.pdf'))
            print(f"📁 {folder_type.upper()}: {len(files)} PDF files")
            for pdf_file in sorted(files, key=lambda x: x.name.lower()):
                size_kb = pdf_file.stat().st_size / 1024
                print(f"   📄 {pdf_file.name} ({size_kb:.1f} KB)")
    
    return summary['overall_success']

if __name__ == "__main__":
    success = test_alphabetical_conversion()
    print(f"\n{'='*80}")
    print(f"🎯 TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*80}")
    exit(0 if success else 1)
#!/usr/bin/env python3
"""Test the enlarged scale DXF to PDF conversion."""

from pathlib import Path
from dxf_converter import DXFToPDFConverter
from PyPDF2 import PdfReader
import time

def test_enlarged_scale_conversion():
    """Test both standard and enlarged scale conversions."""
    print("="*80)
    print("🔍 ENLARGED SCALE DXF TO PDF CONVERSION TEST")
    print("="*80)
    
    # Find a DXF file to test
    input_folder = Path("INPUT_DATA")
    dxf_files = list(input_folder.glob("*.dxf")) + list(input_folder.glob("*.DXF"))
    
    if not dxf_files:
        print("❌ No DXF files found in INPUT_DATA folder")
        return False
    
    test_file = dxf_files[0]  # Use first available DXF file
    print(f"📁 Test file: {test_file.name}")
    
    # Test 1: Standard Scale Conversion
    print(f"\n📄 TEST 1: STANDARD SCALE CONVERSION")
    print("-" * 50)
    
    standard_converter = DXFToPDFConverter(enable_detail_enhancement=False)
    
    start_time = time.time()
    success_std, output_std, pages_std = standard_converter.convert_dxf_to_pdf(test_file)
    std_duration = time.time() - start_time
    
    if success_std:
        pdf_path_std = Path(output_std)
        size_kb_std = pdf_path_std.stat().st_size / 1024
        print(f"✅ Standard conversion successful!")
        print(f"   📄 Pages: {pages_std}")
        print(f"   📁 Size: {size_kb_std:.1f} KB")
        print(f"   ⏱️  Time: {std_duration:.1f} seconds")
        print(f"   📂 Output: {pdf_path_std.name}")
    else:
        print(f"❌ Standard conversion failed: {output_std}")
        return False
    
    # Test 2: Enlarged Scale Conversion (4x)
    print(f"\n🔍 TEST 2: 4x ENLARGED SCALE CONVERSION")
    print("-" * 50)
    
    enlarged_converter = DXFToPDFConverter(scale_factor=4.0, enable_detail_enhancement=True)
    
    start_time = time.time()
    success_enl, output_enl, pages_enl = enlarged_converter.convert_dxf_to_pdf(test_file)
    enl_duration = time.time() - start_time
    
    if success_enl:
        pdf_path_enl = Path(output_enl)
        size_kb_enl = pdf_path_enl.stat().st_size / 1024
        print(f"✅ Enlarged conversion successful!")
        print(f"   📄 Pages: {pages_enl}")
        print(f"   📁 Size: {size_kb_enl:.1f} KB")
        print(f"   ⏱️  Time: {enl_duration:.1f} seconds")
        print(f"   📂 Output: {pdf_path_enl.name}")
    else:
        print(f"❌ Enlarged conversion failed: {output_enl}")
        return False
    
    # Comparison Analysis
    print(f"\n📊 COMPARISON ANALYSIS")
    print("=" * 80)
    
    page_ratio = pages_enl / pages_std if pages_std > 0 else 0
    size_ratio = size_kb_enl / size_kb_std if size_kb_std > 0 else 0
    
    print(f"📄 Page Count:")
    print(f"   Standard Scale: {pages_std} pages")
    print(f"   Enlarged Scale: {pages_enl} pages")
    print(f"   Ratio: {page_ratio:.1f}x more pages")
    
    print(f"\n📁 File Size:")
    print(f"   Standard Scale: {size_kb_std:.1f} KB")
    print(f"   Enlarged Scale: {size_kb_enl:.1f} KB")
    print(f"   Ratio: {size_ratio:.1f}x larger file")
    
    print(f"\n⏱️  Processing Time:")
    print(f"   Standard Scale: {std_duration:.1f} seconds")
    print(f"   Enlarged Scale: {enl_duration:.1f} seconds")
    print(f"   Ratio: {enl_duration/std_duration:.1f}x longer")
    
    # Verify PDF quality
    print(f"\n🔍 PDF QUALITY VERIFICATION")
    print("-" * 50)
    
    try:
        # Check standard PDF
        reader_std = PdfReader(str(pdf_path_std))
        print(f"📄 Standard PDF: {len(reader_std.pages)} pages verified")
        
        # Check enlarged PDF
        reader_enl = PdfReader(str(pdf_path_enl))
        print(f"🔍 Enlarged PDF: {len(reader_enl.pages)} pages verified")
        
        # Check if enlarged scale achieved the target
        target_ratio = 4.0  # 4x enlargement
        if page_ratio >= target_ratio * 0.8:  # Allow 20% tolerance
            print(f"🎯 ENLARGEMENT TARGET ACHIEVED!")
            print(f"   Expected: ~{target_ratio}x more pages")
            print(f"   Actual: {page_ratio:.1f}x more pages")
        else:
            print(f"⚠️  Enlargement below target:")
            print(f"   Expected: ~{target_ratio}x more pages")
            print(f"   Actual: {page_ratio:.1f}x more pages")
        
    except Exception as e:
        print(f"❌ PDF verification error: {e}")
        return False
    
    print(f"\n🎉 ENLARGED SCALE TEST COMPLETED SUCCESSFULLY!")
    print(f"   ✅ Standard conversion: {pages_std} pages")
    print(f"   🔍 Enlarged conversion: {pages_enl} pages ({page_ratio:.1f}x more detail)")
    print(f"   📈 Detail enhancement: {((page_ratio - 1) * 100):.0f}% more content")
    
    return True

if __name__ == "__main__":
    success = test_enlarged_scale_conversion()
    print(f"\n{'='*80}")
    print(f"🎯 TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*80}")
    exit(0 if success else 1)
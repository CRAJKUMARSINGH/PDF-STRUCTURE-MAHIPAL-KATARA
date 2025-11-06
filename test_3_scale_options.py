#!/usr/bin/env python3
"""Test the 3 scale options for DXF to PDF conversion."""

from pathlib import Path
from dxf_converter import DXFToPDFConverter
from PyPDF2 import PdfReader
import time

def test_3_scale_options():
    """Test all 3 scale options: Standard, 2x Enlarged, 4x Maximum."""
    print("="*80)
    print("🎯 3 SCALE OPTIONS TEST - DXF TO PDF CONVERSION")
    print("="*80)
    
    # Find a DXF file to test
    input_folder = Path("INPUT_DATA")
    dxf_files = list(input_folder.glob("*.dxf")) + list(input_folder.glob("*.DXF"))
    
    if not dxf_files:
        print("❌ No DXF files found in INPUT_DATA folder")
        return False
    
    test_file = dxf_files[0]  # Use first available DXF file
    print(f"📁 Test file: {test_file.name}")
    print(f"📐 Testing all 3 scale options...")
    
    results = {}
    
    # Test all 3 scale options
    scale_modes = ['standard', 'enlarged_2x', 'maximum_4x']
    
    for scale_mode in scale_modes:
        print(f"\n{'='*60}")
        print(f"🎯 TESTING: {scale_mode.upper().replace('_', ' ')}")
        print(f"{'='*60}")
        
        # Initialize converter for this scale mode
        converter = DXFToPDFConverter(scale_mode=scale_mode)
        
        # Show scale configuration
        config = converter.scale_config
        print(f"📊 Scale Configuration:")
        print(f"   Name: {config['name']}")
        print(f"   Factor: {config['factor']}x")
        print(f"   Description: {config['description']}")
        print(f"   Max pages: {config['max_pages']}")
        print(f"   DPI multiplier: {config['dpi_multiplier']}x")
        
        # Perform conversion
        start_time = time.time()
        success, output_path, pages = converter.convert_dxf_to_pdf(test_file)
        duration = time.time() - start_time
        
        if success:
            pdf_path = Path(output_path)
            size_kb = pdf_path.stat().st_size / 1024
            
            # Verify PDF
            try:
                reader = PdfReader(str(pdf_path))
                verified_pages = len(reader.pages)
                
                results[scale_mode] = {
                    'success': True,
                    'pages': pages,
                    'verified_pages': verified_pages,
                    'size_kb': size_kb,
                    'duration': duration,
                    'output_file': pdf_path.name,
                    'scale_factor': config['factor']
                }
                
                print(f"✅ Conversion successful!")
                print(f"   📄 Pages: {pages} (verified: {verified_pages})")
                print(f"   📁 Size: {size_kb:.1f} KB")
                print(f"   ⏱️  Time: {duration:.1f} seconds")
                print(f"   📂 Output: {pdf_path.name}")
                
            except Exception as e:
                print(f"❌ PDF verification failed: {e}")
                results[scale_mode] = {'success': False, 'error': str(e)}
        else:
            print(f"❌ Conversion failed: {output_path}")
            results[scale_mode] = {'success': False, 'error': output_path}
    
    # Comparison Analysis
    print(f"\n{'='*80}")
    print(f"📊 SCALE COMPARISON ANALYSIS")
    print(f"{'='*80}")
    
    successful_results = {k: v for k, v in results.items() if v.get('success', False)}
    
    if len(successful_results) >= 2:
        print(f"📄 PAGE COUNT COMPARISON:")
        for scale_mode, result in successful_results.items():
            config = DXFToPDFConverter.SCALE_OPTIONS[scale_mode]
            print(f"   {config['name']}: {result['pages']} pages ({config['factor']}x scale)")
        
        print(f"\n📁 FILE SIZE COMPARISON:")
        for scale_mode, result in successful_results.items():
            config = DXFToPDFConverter.SCALE_OPTIONS[scale_mode]
            print(f"   {config['name']}: {result['size_kb']:.1f} KB")
        
        print(f"\n⏱️  PROCESSING TIME COMPARISON:")
        for scale_mode, result in successful_results.items():
            config = DXFToPDFConverter.SCALE_OPTIONS[scale_mode]
            print(f"   {config['name']}: {result['duration']:.1f} seconds")
        
        # Calculate ratios if we have standard as baseline
        if 'standard' in successful_results:
            standard = successful_results['standard']
            print(f"\n📈 IMPROVEMENT RATIOS (vs Standard):")
            
            for scale_mode, result in successful_results.items():
                if scale_mode != 'standard':
                    config = DXFToPDFConverter.SCALE_OPTIONS[scale_mode]
                    page_ratio = result['pages'] / standard['pages']
                    size_ratio = result['size_kb'] / standard['size_kb']
                    time_ratio = result['duration'] / standard['duration']
                    
                    print(f"   {config['name']}:")
                    print(f"     📄 Pages: {page_ratio:.1f}x more")
                    print(f"     📁 Size: {size_ratio:.1f}x larger")
                    print(f"     ⏱️  Time: {time_ratio:.1f}x longer")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"🎯 SCALE OPTIONS SUMMARY")
    print(f"{'='*80}")
    
    successful_count = len(successful_results)
    total_count = len(scale_modes)
    
    print(f"✅ Successful conversions: {successful_count}/{total_count}")
    
    if successful_count == total_count:
        print(f"🎉 ALL 3 SCALE OPTIONS WORKING PERFECTLY!")
        print(f"\nRecommendations:")
        print(f"   📄 Standard: Use for quick previews and fast processing")
        print(f"   🔍 2x Enlarged: Use for moderate detail with reasonable processing time")
        print(f"   🎯 4x Maximum: Use for maximum precision and detailed analysis")
    else:
        print(f"⚠️  Some scale options failed - check logs for details")
    
    return successful_count == total_count

if __name__ == "__main__":
    success = test_3_scale_options()
    print(f"\n{'='*80}")
    print(f"🎯 TEST RESULT: {'✅ ALL SCALES PASSED' if success else '❌ SOME SCALES FAILED'}")
    print(f"{'='*80}")
    exit(0 if success else 1)
#!/usr/bin/env python3
"""Verify the created PDF files."""

from pathlib import Path
from PyPDF2 import PdfReader

def verify_pdfs():
    """Verify both standard and enlarged PDFs."""
    print("🔍 VERIFYING CREATED PDF FILES")
    print("="*50)
    
    # Check standard PDF
    std_pdf = Path('OUTPUT_PDF/G.F.dwg-Model_1762410547272_A4_landscape.pdf')
    print(f"\n📄 STANDARD PDF:")
    if std_pdf.exists():
        try:
            reader = PdfReader(str(std_pdf))
            size_kb = std_pdf.stat().st_size / 1024
            print(f"  ✅ File exists: {std_pdf.name}")
            print(f"  📁 Size: {size_kb:.1f} KB")
            print(f"  📄 Pages: {len(reader.pages)}")
        except Exception as e:
            print(f"  ❌ Error reading: {e}")
    else:
        print(f"  ❌ File not found")
    
    # Check enlarged PDF
    enl_pdf = Path('OUTPUT_PDF/G.F.dwg-Model_1762410547272_ENLARGED_4.0x_A4_landscape.pdf')
    print(f"\n🔍 ENLARGED PDF:")
    if enl_pdf.exists():
        try:
            reader = PdfReader(str(enl_pdf))
            size_kb = enl_pdf.stat().st_size / 1024
            print(f"  ✅ File exists: {enl_pdf.name}")
            print(f"  📁 Size: {size_kb:.1f} KB")
            print(f"  📄 Pages: {len(reader.pages)}")
            
            # Calculate improvement
            if std_pdf.exists():
                std_reader = PdfReader(str(std_pdf))
                page_ratio = len(reader.pages) / len(std_reader.pages)
                print(f"  📈 Page ratio: {page_ratio:.1f}x more pages than standard")
                
        except Exception as e:
            print(f"  ❌ Error reading: {e}")
    else:
        print(f"  ❌ File not found")
    
    print(f"\n{'='*50}")
    
    # Summary
    std_exists = std_pdf.exists()
    enl_exists = enl_pdf.exists()
    
    if std_exists and enl_exists:
        print("🎉 SUCCESS: Both PDFs created successfully!")
        print("   The enlarged scale conversion worked despite PowerShell timeout")
    elif std_exists:
        print("⚠️  PARTIAL: Standard PDF created, enlarged PDF incomplete")
    else:
        print("❌ FAILURE: No PDFs created")

if __name__ == "__main__":
    verify_pdfs()
from pathlib import Path
from PyPDF2 import PdfReader

# Quick check of both PDFs
std_pdf = Path('OUTPUT_PDF/G.F.dwg-Model_1762410547272_A4_landscape.pdf')
enl_pdf = Path('OUTPUT_PDF/G.F.dwg-Model_1762410547272_ENLARGED_4.0x_A4_landscape.pdf')

print("PDF STATUS CHECK:")
print("="*40)

if std_pdf.exists():
    reader = PdfReader(str(std_pdf))
    size_kb = std_pdf.stat().st_size / 1024
    print(f"✅ Standard: {len(reader.pages)} pages, {size_kb:.0f} KB")
else:
    print("❌ Standard PDF not found")

if enl_pdf.exists():
    reader = PdfReader(str(enl_pdf))
    size_kb = enl_pdf.stat().st_size / 1024
    print(f"✅ Enlarged: {len(reader.pages)} pages, {size_kb:.0f} KB")
else:
    print("❌ Enlarged PDF not found")

print("="*40)
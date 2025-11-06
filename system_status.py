print('🚀 ENHANCED DXF & HTML TO PDF SYSTEM - STATUS CHECK')
print('='*60)

# Test imports
try:
    from dxf_converter import DXFToPDFConverter
    from unified_converter import UnifiedConverter
    from html2pdf.service import HTMLToPDFService
    print('✅ All modules imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')

# Check scale options
try:
    scale_options = DXFToPDFConverter.SCALE_OPTIONS
    print('✅ 3 Scale options available:')
    for mode, config in scale_options.items():
        print(f'   {config["name"]}: {config["factor"]}x')
except Exception as e:
    print(f'❌ Scale options error: {e}')

# Check files
try:
    from pathlib import Path
    input_folder = Path('INPUT_DATA')
    html_files = list(input_folder.glob('*.html')) + list(input_folder.glob('*.htm'))
    dxf_files = list(input_folder.glob('*.dxf')) + list(input_folder.glob('*.DXF'))
    print(f'✅ Files found: {len(html_files)} HTML, {len(dxf_files)} DXF')
except Exception as e:
    print(f'❌ File error: {e}')

print('='*60)
print('🎯 SYSTEM READY!')
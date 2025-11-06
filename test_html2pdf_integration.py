"""Test script for HTML to PDF integration."""
from pathlib import Path
from html2pdf.service import HTMLToPDFService
import tempfile
import os

def create_test_html_files():
    """Create some test HTML files for testing."""
    input_dir = Path("INPUT_DATA")
    input_dir.mkdir(exist_ok=True)
    
    # Test HTML 1
    html1_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report 1</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Structural Analysis Report</h1>
        <p>This is a test HTML report for PDF conversion.</p>
        <table>
            <tr><th>Element</th><th>Load (kN)</th><th>Stress (MPa)</th></tr>
            <tr><td>Beam B1</td><td>150</td><td>25.5</td></tr>
            <tr><td>Column C1</td><td>300</td><td>18.2</td></tr>
        </table>
    </body>
    </html>
    """
    
    # Test HTML 2
    html2_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report 2</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #666; }
            .summary { background: #f9f9f9; padding: 15px; border-left: 4px solid #007cba; }
        </style>
    </head>
    <body>
        <h1>Foundation Design Summary</h1>
        <div class="summary">
            <h3>Design Parameters</h3>
            <ul>
                <li>Concrete Grade: M25</li>
                <li>Steel Grade: Fe415</li>
                <li>Soil Bearing Capacity: 200 kN/m²</li>
            </ul>
        </div>
        <p>All foundations meet the design requirements as per IS 456:2000.</p>
    </body>
    </html>
    """
    
    with open(input_dir / "test_report_1.html", "w") as f:
        f.write(html1_content)
    
    with open(input_dir / "test_report_2.html", "w") as f:
        f.write(html2_content)
    
    print("✓ Created test HTML files")

def test_html_to_pdf_service():
    """Test the HTML to PDF service."""
    print("\n" + "="*50)
    print("Testing HTML to PDF Service")
    print("="*50)
    
    # Create test files
    create_test_html_files()
    
    # Initialize service
    service = HTMLToPDFService()
    
    # Test scanning HTML files
    html_files = service.get_html_files()
    print(f"Found HTML files: {html_files}")
    
    # Test conversion
    result = service.convert_html_to_pdf()
    
    print(f"\nConversion Result:")
    print(f"Success: {result['success']}")
    print(f"Total files: {result['total']}")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")
    
    if result['success']:
        print(f"Output file: {result['output_file']}")
        output_path = Path(result['output_path'])
        if output_path.exists():
            print(f"✓ PDF created successfully: {output_path}")
            print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
        else:
            print("✗ PDF file not found")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if result.get('failures'):
            for failure in result['failures']:
                print(f"  - {failure['file']}: {failure['error']}")

if __name__ == "__main__":
    test_html_to_pdf_service()
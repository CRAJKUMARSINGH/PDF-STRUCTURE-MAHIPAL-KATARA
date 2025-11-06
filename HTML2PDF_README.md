# HTML to PDF Converter Integration

This document describes the HTML to PDF conversion functionality that has been integrated into the root application.

## Features

- **Enhanced PDF Generation**: Maximum page usage with elegant 10mm margins only
- **High-Quality Output**: 300 DPI rendering for crisp text and images
- **Optimized Typography**: Professional font rendering with proper spacing
- **Smart Layout**: Print-optimized CSS for better appearance
- **Batch HTML to PDF Conversion**: Convert multiple HTML files into a single combined PDF
- **Web Interface**: Upload and convert HTML files through the Flask web interface
- **Command Line Interface**: Use the CLI for batch processing with page size options
- **Automatic File Detection**: Scans for .html and .htm files in the input directory
- **Error Handling**: Comprehensive error reporting for failed conversions
- **Temporary File Management**: Automatic cleanup of intermediate files
- **Multiple Page Sizes**: Support for A4, A3, A5, Letter, and Legal formats
- **Orientation Control**: Portrait and Landscape orientation options

## Dependencies

The following packages have been added to support HTML to PDF conversion:

- `pdfkit>=1.0.0` - Python wrapper for wkhtmltopdf
- `pypdf2>=3.0.0` - PDF manipulation library

**Note**: You'll also need to install `wkhtmltopdf` on your system:
- Windows: Download from https://wkhtmltopdf.org/downloads.html
- Linux: `sudo apt-get install wkhtmltopdf` (Ubuntu/Debian) or `sudo yum install wkhtmltopdf` (CentOS/RHEL)
- macOS: `brew install wkhtmltopdf`

## Usage

### Web Interface

1. **Upload HTML Files**: Use the web interface to upload .html or .htm files
2. **Convert Individual Files**: Click "Convert to PDF" next to any HTML file
3. **Convert All Files**: Click "Convert All HTML to Combined PDF" to merge all HTML files into one PDF
4. **Download Results**: Download the generated PDF files from the output section

### Command Line Interface

```bash
# Convert all HTML files in current directory with enhanced styling
python convert_html_cli.py

# Convert HTML files from specific directory
python convert_html_cli.py --source-dir /path/to/html/files

# Specify output file with custom page size
python convert_html_cli.py --output combined_report.pdf --page-size A4 --orientation Portrait

# Use A3 landscape for larger content
python convert_html_cli.py --page-size A3 --orientation Landscape

# Available page sizes: A4, A3, A5, Letter, Legal
# Available orientations: Portrait, Landscape
```

### Programmatic Usage

```python
from html2pdf.service import HTMLToPDFService

# Initialize service
service = HTMLToPDFService(input_folder="INPUT_DATA", output_folder="OUTPUT_PDF")

# Convert all HTML files
result = service.convert_html_to_pdf()

# Convert specific files
result = service.convert_html_to_pdf(html_files=["report1.html", "report2.html"])

# Check results
if result['success']:
    print(f"PDF created: {result['output_file']}")
else:
    print(f"Error: {result['error']}")
```

## File Structure

```
html2pdf/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── converter.py        # HTML to PDF conversion logic
├── merger.py           # PDF merging functionality
├── models.py           # Data models and configuration
├── reporter.py         # Result reporting
├── scanner.py          # HTML file discovery
└── service.py          # Flask integration service
```

## API Endpoints

### POST /convert_html
Convert HTML files to PDF.

**Request Body:**
```json
{
    "files": ["file1.html", "file2.html"],  // Optional: specific files to convert
    "output_filename": "custom_name.pdf"    // Optional: custom output filename
}
```

**Response:**
```json
{
    "success": true,
    "output_file": "combined_html_20231106_123456.pdf",
    "total": 2,
    "successful": 2,
    "failed": 0,
    "failures": []
}
```

### GET /html_files
Get list of available HTML files.

**Response:**
```json
{
    "success": true,
    "files": ["report1.html", "report2.html"]
}
```

## Configuration

The HTML to PDF converter uses the following default settings:

- **Input Directory**: `INPUT_DATA/` (same as DXF files)
- **Output Directory**: `OUTPUT_PDF/` (same as DXF files)
- **Temporary Directory**: `temp_html2pdf/`
- **wkhtmltopdf Options**:
  - `enable-local-file-access`: Allows access to local files and images
  - `encoding`: UTF-8
  - `quiet`: Suppress wkhtmltopdf output

## Error Handling

The converter handles various error scenarios:

- **Missing wkhtmltopdf**: Clear error message if wkhtmltopdf is not installed
- **Invalid HTML**: Continues processing other files if one fails
- **File Access Issues**: Reports permission and file access errors
- **Memory Issues**: Handles large files gracefully

## Testing

Run the integration test to verify functionality:

```bash
python test_html2pdf_integration.py
```

This will:
1. Create sample HTML files
2. Test the conversion process
3. Verify the output PDF is created
4. Report results and file sizes

## Troubleshooting

### Common Issues

1. **"wkhtmltopdf not found"**
   - Install wkhtmltopdf on your system
   - Ensure it's in your system PATH

2. **"Permission denied"**
   - Check file permissions in input/output directories
   - Ensure the application has write access to output directory

3. **"No HTML files found"**
   - Verify HTML files are in the INPUT_DATA directory
   - Check file extensions (.html, .htm)

4. **"Conversion failed"**
   - Check HTML file validity
   - Verify all referenced resources (images, CSS) are accessible

### Logs

The converter logs detailed information about the conversion process. Check the application logs for:
- File discovery results
- Individual conversion status
- Error details and stack traces
- Performance metrics

## Integration Notes

The HTML to PDF converter has been seamlessly integrated with the existing DXF to PDF application:

- **Shared Infrastructure**: Uses the same input/output directories and Flask app
- **Unified Interface**: Both DXF and HTML conversion available in the same web interface
- **Consistent Error Handling**: Same error reporting patterns as DXF converter
- **File Management**: Same upload, download, and delete functionality
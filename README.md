# PDF Conversion Tools

Two Python tools for converting files to PDF format:
1. **HTML to PDF Converter** - Combines multiple HTML files into a single PDF
2. **DXF to PDF Printer** - Converts CAD DXF files to A4 landscape PDF

## Installation

### Prerequisites

**For HTML to PDF Converter:**
- Python 3.8+
- wkhtmltopdf (system dependency)

**For DXF to PDF Printer:**
- Python 3.8+

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Install wkhtmltopdf (for HTML to PDF only)

**Windows:**
Download and install from: https://wkhtmltopdf.org/downloads.html

**Linux:**
```bash
sudo apt-get install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

## Usage

### HTML to PDF Converter

Convert all HTML files in current directory to a single combined PDF:

```bash
python -m html2pdf.cli
```

Specify source directory and output file:

```bash
python -m html2pdf.cli --source-dir ./reports --output combined.pdf
```

**Options:**
- `--source-dir`, `-s`: Source directory containing HTML files (default: current directory)
- `--output`, `-o`: Output PDF filename (default: combined_YYYYMMDD_HHMMSS.pdf)

**Features:**
- Scans directory for .html and .htm files
- Converts each HTML to PDF preserving formatting
- Combines all PDFs in alphabetical order
- Handles conversion errors gracefully
- Displays detailed conversion report

### DXF to PDF Printer

Convert DXF files to A4 landscape PDF:

**Single file:**
```bash
python -m dxf2pdf.cli drawing.dxf
```

**Batch conversion (all DXF files in directory):**
```bash
python -m dxf2pdf.cli . --output-dir ./pdf_output
```

**Custom output filename (single file):**
```bash
python -m dxf2pdf.cli drawing.dxf --output my_drawing.pdf
```

**Options:**
- `input`: Input DXF file or directory (required)
- `--output-dir`, `-d`: Output directory for PDFs (default: same as input)
- `--output`, `-o`: Custom output filename (single file only)
- `--pages`, `-p`: Number of pages to split each drawing into (1-5, default: 1)

**Features:**
- A4 landscape page size (297mm x 210mm)
- **Multi-page output**: Split large drawings into 1-5 sections with legends
- Automatic scaling to fit drawing on page
- Maintains aspect ratio
- Centers drawing on page
- **Legend on each page**: Shows drawing name, page number, scale, and section coordinates
- Supports multiple entity types (LINE, CIRCLE, ARC, POLYLINE, TEXT, etc.)
- Batch processing support
- Error handling for corrupted files

## Examples

### HTML to PDF

```bash
# Convert all HTML files in current directory
python -m html2pdf.cli

# Convert HTML files from specific directory
python -m html2pdf.cli --source-dir ./engineering_reports

# Specify custom output name
python -m html2pdf.cli --output project_reports.pdf
```

### DXF to PDF

```bash
# Convert single DXF file (1 page)
python -m dxf2pdf.cli LIBRBeamSections011.DXF

# Convert to multi-page PDF (3 sections with legends)
python -m dxf2pdf.cli LIBRBeamSections011.DXF --pages 3

# Convert all DXF files in current directory to 5-page PDFs
python -m dxf2pdf.cli . --pages 5

# Convert all DXF files to specific output directory with 2 pages each
python -m dxf2pdf.cli . --output-dir ./pdf_drawings --pages 2

# Convert single file with custom name and 4 pages
python -m dxf2pdf.cli drawing.dxf --output final_design.pdf --pages 4
```

**Multi-Page Options:**
- `--pages 1`: Single page with full drawing (default)
- `--pages 2`: Split horizontally into 2 sections
- `--pages 3`: Split horizontally into 3 sections
- `--pages 4`: 2x2 grid (4 detailed sections)
- `--pages 5`: Full overview + 2x2 grid (5 pages total)

## Project Structure

```
.
├── html2pdf/              # HTML to PDF converter package
│   ├── __init__.py
│   ├── cli.py            # Command-line interface
│   ├── converter.py      # HTML to PDF conversion
│   ├── merger.py         # PDF merging
│   ├── models.py         # Data models
│   ├── reporter.py       # Results reporting
│   └── scanner.py        # File scanning
│
├── dxf2pdf/              # DXF to PDF printer package
│   ├── __init__.py
│   ├── cli.py            # Command-line interface
│   ├── geometry.py       # Geometry processing
│   ├── models.py         # Data models
│   ├── parser.py         # DXF parsing
│   ├── renderer.py       # PDF rendering
│   ├── reporter.py       # Results reporting
│   ├── scale.py          # Scale calculation
│   └── scanner.py        # File scanning
│
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Dependencies

- **pdfkit**: HTML to PDF conversion (wrapper for wkhtmltopdf)
- **PyPDF2**: PDF manipulation and merging
- **ezdxf**: DXF file parsing and processing
- **reportlab**: PDF generation and rendering

## Troubleshooting

### HTML to PDF Issues

**Error: "wkhtmltopdf not found"**
- Install wkhtmltopdf system dependency (see Installation section)
- Ensure wkhtmltopdf is in your system PATH

**Error: "No module named 'pdfkit'"**
- Run: `pip install pdfkit PyPDF2`

### DXF to PDF Issues

**Error: "No entities found"**
- DXF file may be empty or contain only non-drawable entities
- Check that the DXF file opens correctly in a CAD viewer

**Error: "Parse error"**
- DXF file may be corrupted
- Try opening and re-saving the file in a CAD application

**Drawing appears too small/large**
- The tool automatically scales drawings to fit A4 landscape
- Check the original drawing units and scale

## License

MIT License

## Author

Created for engineering document processing and CAD drawing conversion.

```
# DXF to PDF Converter

This is a Streamlit web application that converts DXF (AutoCAD Drawing Exchange Format) files to PDF format.

## Features

- Upload DXF files through a web interface
- Convert DXF files to PDF format
- Support for multiple entity types (lines, circles, arcs, polylines, text, etc.)
- Multi-page output options
- Smart drawing segmentation
- Entity analysis and statistics

## Requirements

- Python 3.7+
- Streamlit
- ezdxf
- reportlab

## Installation

```bash
pip install -r requirements.txt
```

## Usage

To run the app locally:

```bash
streamlit run streamlit_app.py
```

Then open your browser to the URL provided (typically http://localhost:8501).

## Deployment

This app can be deployed to Streamlit Cloud:

1. Push this code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Deploy the app

## File Structure

- `streamlit_app.py`: Main Streamlit application
- `dxf2pdf/`: Python modules for DXF to PDF conversion
- `requirements.txt`: Python dependencies
- `DEPLOYMENT_GUIDE.md`: Detailed deployment instructions

## Supported Entities

- Lines and Polylines
- Circles and Arcs
- Text and Multi-text
- Splines and Ellipses
- Points and Blocks

## Technical Info

- Output: A4 Landscape PDF
- Scale: Auto-calculated
- Colors: Preserved from DXF
- Max File Size: 200MB

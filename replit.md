# DXF to PDF Converter - A4 Landscape Multi-Page

## Overview
Professional DXF to PDF conversion application designed for architectural and structural footing drawings. Automatically converts DXF files to A4 landscape PDFs with intelligent multi-page splitting.

## Features
- **Batch Processing**: Convert multiple DXF files in one operation
- **A4 Landscape Output**: Professional 297mm × 210mm landscape orientation
- **Intelligent Page Splitting**: Automatically detects and separates footing sections, plans, and elevations
- **Smart Section Detection**: Identifies gaps and natural boundaries in drawings
- **Web Interface**: Simple drag-and-drop upload with real-time conversion
- **Entity Support**: Handles lines, polylines, arcs, circles, dimensions, text, hatches, blocks, and more

## Project Structure
```
├── INPUT_DATA/          # DXF source files (upload here)
├── OUTPUT_PDF/          # Generated PDF files (A4 landscape)
├── LOGS/                # Conversion logs and reports
├── templates/           # Flask HTML templates
├── dxf_converter.py     # Core conversion engine
├── app.py               # Flask web application
└── replit.md            # This file
```

## How It Works

### Core Technology
- **ezdxf 1.4.3**: Industry-standard Python library for DXF file parsing
- **matplotlib**: High-quality rendering backend for PDF generation
- **reportlab**: PDF layout control and multi-page management
- **Flask**: Web interface for file upload and conversion

### Intelligent Page Splitting
The converter analyzes DXF drawings to:
1. Detect natural gaps and boundaries between sections
2. Identify separate footing plans, elevations, and details
3. Calculate optimal page breaks based on content density
4. Fit each section within A4 landscape dimensions

### Conversion Process
1. Upload DXF files via web interface or place in INPUT_DATA folder
2. Click "Convert All" or convert individual files
3. Converter analyzes drawing structure and entities
4. Automatically splits into multiple A4 landscape pages
5. Download PDFs from OUTPUT_PDF folder

## Usage

### Web Interface
1. Open the web application (runs on port 5000)
2. Upload DXF files by dragging/dropping or clicking upload area
3. Click "Convert All to PDF" for batch processing
4. Download generated PDFs

### Command Line (Batch)
```python
from dxf_converter import DXFToPDFConverter

converter = DXFToPDFConverter()
results = converter.batch_convert()
```

### Single File Conversion
```python
from dxf_converter import DXFToPDFConverter

converter = DXFToPDFConverter()
success, output_path, num_pages = converter.convert_dxf_to_pdf('INPUT_DATA/footing.dxf')
```

## Configuration

### Page Settings
- **Page Size**: A4 (297mm × 210mm)
- **Orientation**: Landscape
- **Margins**: 10mm
- **DPI**: 300 (high quality)
- **Max Pages**: 50 per file (configurable)

### Supported DXF Entities
- LINE, LWPOLYLINE, POLYLINE
- CIRCLE, ARC, ELLIPSE
- TEXT, MTEXT
- DIMENSION (all types)
- HATCH, SOLID
- INSERT (blocks)
- SPLINE

## Sample Files
The INPUT_DATA folder contains sample architectural/structural DXF files:
- Footing sections and center lines
- Column layouts and details
- Beam sections and reinforcement
- Slab plans and long sections
- Double line sheets

## Recent Changes
- **2025-11-06**: Initial implementation
  - Core DXF to PDF converter with A4 landscape support
  - Intelligent multi-page section detection
  - Flask web interface with batch processing
  - Smart gap detection for footing drawings
  - Support for all major DXF entity types

## Dependencies
- Python 3.11+
- ezdxf 1.4.3 (DXF parsing)
- matplotlib 3.10+ (rendering)
- reportlab 4.4+ (PDF generation)
- Flask 3.1+ (web interface)
- werkzeug, Pillow, numpy

## Architecture
The application uses a three-tier architecture:
1. **Conversion Engine** (`dxf_converter.py`): Core DXF parsing and PDF generation
2. **Web Application** (`app.py`): Flask server with file management
3. **User Interface** (`templates/index.html`): Modern drag-and-drop web UI

## Logging
All conversions are logged in the LOGS folder with:
- Conversion status (success/failure)
- Number of pages generated
- Error messages and warnings
- Timestamp information

## User Preferences
- Prefers A4 landscape orientation for all structural drawings
- Requires each footing section/plan on separate page
- Batch processing essential for multiple files
- High-quality output for professional use

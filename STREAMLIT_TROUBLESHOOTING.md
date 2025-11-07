# Streamlit DXF to PDF Converter - Troubleshooting Guide

## Common Issues and Solutions

### ❌ "Conversion Failed" Error

If you're seeing the "Unable to convert the DXF file" error, here are the most common causes and solutions:

#### 1. Invalid or Corrupted DXF File

**Symptoms:**
- Conversion fails immediately
- Error message about DXF structure

**Solutions:**
- Open the DXF file in AutoCAD or another DXF viewer to verify it's valid
- Try re-saving the file from AutoCAD
- Use "Save As" and select a different DXF version (R2018 or R2013 recommended)

#### 2. Empty DXF File

**Symptoms:**
- File uploads successfully but conversion fails
- No entities found in the file

**Solutions:**
- Verify the DXF file contains actual drawing entities (lines, circles, polylines, etc.)
- Check that the drawing is in the modelspace (not just in layouts)
- Ensure the drawing is not just metadata or empty layers

#### 3. Unsupported DXF Version

**Symptoms:**
- Error about DXF version
- File is very old or very new

**Solutions:**
- Convert the file to DXF R2018 or R2013 format
- Use AutoCAD's "Save As" feature to convert to a compatible version

#### 4. Large or Complex Files

**Symptoms:**
- Conversion times out
- App becomes unresponsive

**Solutions:**
- Simplify the drawing by removing unnecessary layers
- Split large drawings into smaller sections
- Reduce the number of entities in the drawing

## Diagnostic Tool

Use the diagnostic tool to check your DXF file before uploading:

```bash
cd "New folder"
python diagnose_dxf.py path/to/your/file.dxf
```

This will provide detailed information about:
- File size and validity
- DXF version
- Number and types of entities
- Drawing bounds
- Any structural issues

## Testing Locally

Before deploying to Streamlit Cloud, test the conversion locally:

```bash
cd "New folder"
streamlit run streamlit_app.py
```

## Supported Entity Types

The converter supports these DXF entity types:
- ✅ LINE
- ✅ CIRCLE
- ✅ ARC
- ✅ POLYLINE
- ✅ LWPOLYLINE
- ✅ TEXT
- ✅ MTEXT
- ✅ SPLINE
- ✅ ELLIPSE
- ✅ POINT
- ✅ INSERT (blocks)

## File Requirements

- **Format:** DXF (AutoCAD Drawing Exchange Format)
- **Version:** R2013 or newer recommended
- **Size:** Up to 200MB
- **Content:** Must contain drawable entities in modelspace

## Getting Help

If you're still experiencing issues:

1. Run the diagnostic tool on your DXF file
2. Check the Streamlit app logs for detailed error messages
3. Verify your DXF file opens correctly in AutoCAD or another viewer
4. Try converting a simple test DXF file first

## Example Test Files

The `INPUT_DATA` folder contains sample DXF files you can use for testing:
- `nurseBeamSections011.DXF`
- `nurseFootingSections.DXF`
- `nurseslabsht011.DXF`

These files are known to work correctly with the converter.

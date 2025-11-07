# Batch Processing Guide

## New Features Added ✨

Your Streamlit app now has **THREE powerful batch processing buttons**:

### 1. 📂 Upload Files/Folder
- Upload multiple DXF and HTML files at once
- Supports drag-and-drop
- Automatically separates files by type
- Shows count of DXF vs HTML files

### 2. 📄 Convert All HTML to PDF
**What it does:**
- Converts all uploaded HTML files to individual PDFs
- Creates a combined PDF with all HTML content
- Provides two download options:
  - **Combined PDF** - All HTML files merged into one PDF
  - **Individual PDFs (ZIP)** - Each HTML as separate PDF in a ZIP file

**How to use:**
1. Upload multiple HTML files using the file uploader
2. Click "🔄 Convert All HTML" button
3. Wait for conversion to complete
4. Download either:
   - Combined PDF (single file with all content)
   - ZIP file with individual PDFs

### 3. 📐 Convert All DXF to PDF
**What it does:**
- Converts all uploaded DXF files to PDF format
- Each DXF becomes a separate PDF
- All PDFs packaged in a ZIP file for easy download

**How to use:**
1. Upload multiple DXF files using the file uploader
2. Click "🔄 Convert All DXF" button
3. Wait for conversion to complete
4. Download ZIP file containing all converted PDFs

## Features

### Multi-File Upload
- Upload any combination of DXF and HTML files
- No limit on number of files (within Streamlit's 200MB limit)
- Automatic file type detection

### Smart Processing
- Files are processed in parallel where possible
- Progress indicators show conversion status
- Detailed error messages for failed conversions

### Flexible Downloads
- **HTML conversions:** Get combined PDF + individual PDFs
- **DXF conversions:** Get all PDFs in one ZIP file
- Timestamped filenames prevent overwrites

### Error Handling
- Shows which files succeeded and which failed
- Detailed error messages for troubleshooting
- Continues processing even if some files fail

## Usage Examples

### Example 1: Convert Multiple HTML Reports
```
1. Upload: report1.html, report2.html, report3.html
2. Click: "Convert All HTML"
3. Get:
   - combined_html_20241107_143022.pdf (all reports in one)
   - html_pdfs.zip (3 individual PDFs)
```

### Example 2: Convert Multiple DXF Drawings
```
1. Upload: drawing1.dxf, drawing2.dxf, drawing3.dxf
2. Click: "Convert All DXF"
3. Get:
   - dxf_pdfs_20241107_143022.zip (3 PDFs inside)
```

### Example 3: Mixed Batch Processing
```
1. Upload: 5 HTML files + 3 DXF files
2. Click: "Convert All HTML" → Get HTML PDFs
3. Click: "Convert All DXF" → Get DXF PDFs
4. Result: All files converted in two batches
```

## Single File Conversion

The original single-file conversion is still available below the batch processing section:
- Upload one DXF file
- Configure options (pages, smart splitting)
- View entity statistics
- Download individual PDF

## Tips for Best Results

### For HTML Files:
- Ensure HTML files are well-formed
- Include all referenced CSS/images
- Test with small files first

### For DXF Files:
- Use DXF R2018 or R2013 format
- Verify files open in AutoCAD
- Check files with `diagnose_dxf.py` first
- Simplify complex drawings if needed

### For Large Batches:
- Upload in smaller groups (10-20 files)
- Monitor conversion progress
- Check error messages for failed files
- Re-upload failed files individually

## Troubleshooting

### "No files found" warning
- Make sure you uploaded files first
- Check file extensions (.dxf, .html, .htm)

### Some files fail to convert
- Check error messages for specific issues
- Try converting failed files individually
- Use diagnostic tool for DXF files

### Download button doesn't appear
- Wait for conversion to complete
- Check if any files converted successfully
- Look for error messages

### ZIP file is empty
- All conversions may have failed
- Check error messages
- Try files individually

## Technical Details

### File Processing
- **HTML:** Uses pdfkit + wkhtmltopdf
- **DXF:** Uses ezdxf + matplotlib + reportlab
- **Merging:** Uses PyPDF2 for combining PDFs
- **Packaging:** Uses Python zipfile for ZIP creation

### Temporary Files
- All processing uses temporary directories
- Files are automatically cleaned up
- No files stored on server permanently

### Limitations
- Maximum upload size: 200MB total
- Processing time depends on file complexity
- Some DXF entities may not be supported
- HTML must be valid and well-formed

## Deployment

After updating the code:

```bash
cd "New folder"
git add streamlit_app.py
git commit -m "Add batch processing with 3 buttons"
git push origin main
```

Streamlit Cloud will automatically redeploy with the new features.

## Testing Locally

```bash
cd "New folder"
streamlit run streamlit_app.py
```

Then test:
1. Upload multiple files
2. Try each batch button
3. Verify downloads work
4. Check error handling

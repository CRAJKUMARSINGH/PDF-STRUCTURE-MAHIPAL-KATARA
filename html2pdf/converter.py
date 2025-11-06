"""HTML to PDF converter module."""
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import pdfkit

logger = logging.getLogger(__name__)


class HTMLConverter:
    """Converts HTML files to PDF format with enhanced elegance and maximum page usage."""
    
    def __init__(self, temp_dir: Path, page_size: str = 'A4', orientation: str = 'Portrait'):
        """
        Initialize converter with temporary directory for intermediate PDFs.
        
        Args:
            temp_dir: Path to temporary directory for storing intermediate PDFs
            page_size: PDF page size (A4, A3, Letter, etc.)
            orientation: Page orientation (Portrait or Landscape)
        """
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure wkhtmltopdf options for MAXIMUM page usage with ONLY 10mm margins
        self.options = {
            # Basic settings
            'enable-local-file-access': None,
            'encoding': 'UTF-8',
            'quiet': '',
            
            # Page layout - MAXIMUM content area with ONLY 10mm margins
            'page-size': page_size,
            'orientation': orientation,
            'margin-top': '10mm',
            'margin-right': '10mm', 
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            
            # Content optimization for MAXIMUM elegance
            'disable-smart-shrinking': '',  # Prevent automatic shrinking
            'print-media-type': '',         # Use print CSS styles
            'no-background': False,         # Keep background colors/images
            'enable-javascript': '',        # Enable JS for dynamic content
            'javascript-delay': 1500,       # Wait longer for JS to complete
            
            # ULTRA HIGH quality and rendering
            'dpi': 600,                     # ULTRA HIGH DPI for maximum crispness
            'image-dpi': 600,               # ULTRA HIGH DPI for images
            'image-quality': 100,           # Maximum image quality
            
            # Error handling
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore',
            
            # Advanced options for MAXIMUM rendering quality
            'minimum-font-size': 6,         # Allow smaller fonts for more content
            'zoom': 1.0,                    # No zoom scaling
            'viewport-size': '1920x1080',   # Large viewport for maximum content
            
            # Additional elegance options
            'lowquality': False,            # High quality rendering
            'grayscale': False,             # Full color
            'disable-plugins': '',          # Disable plugins for faster rendering
            'no-pdf-compression': ''        # No compression for maximum quality
        }
    
    def enhance_html_for_pdf(self, html_path: Path) -> Path:
        """
        Enhance HTML file with PDF-optimized CSS for better appearance.
        
        Args:
            html_path: Path to original HTML file
            
        Returns:
            Path to enhanced HTML file
        """
        enhanced_path = self.temp_dir / f"enhanced_{html_path.name}"
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ULTRA ELEGANT CSS for PDF rendering with MAXIMUM page usage and ONLY 10mm margins
            pdf_css = """
            <style type="text/css" media="print,screen">
                /* MAXIMUM ELEGANCE - Reset and base styles for PDF */
                * {
                    box-sizing: border-box !important;
                    -webkit-print-color-adjust: exact !important;
                    color-adjust: exact !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                
                body {
                    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
                    font-size: 10pt !important;
                    line-height: 1.3 !important;
                    color: #2c3e50 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    background: white !important;
                    font-weight: 400 !important;
                    text-rendering: optimizeLegibility !important;
                    -webkit-font-smoothing: antialiased !important;
                }
                
                /* MAXIMIZE content area - remove ALL unnecessary spacing */
                .container, .content, .main, .wrapper, .page, .document {
                    width: 100% !important;
                    max-width: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border: none !important;
                }
                
                /* ELEGANT Typography optimization for maximum space usage */
                h1, h2, h3, h4, h5, h6 {
                    font-weight: 600 !important;
                    margin: 6pt 0 3pt 0 !important;
                    padding: 0 !important;
                    page-break-after: avoid !important;
                    line-height: 1.2 !important;
                }
                
                h1 { 
                    font-size: 14pt !important; 
                    color: #1a252f !important;
                    border-bottom: 1pt solid #3498db !important;
                    padding-bottom: 2pt !important;
                }
                h2 { 
                    font-size: 12pt !important; 
                    color: #2c3e50 !important;
                    margin-top: 8pt !important;
                }
                h3 { 
                    font-size: 11pt !important; 
                    color: #34495e !important;
                }
                h4, h5, h6 { 
                    font-size: 10pt !important; 
                    color: #34495e !important;
                }
                
                p {
                    margin: 2pt 0 !important;
                    padding: 0 !important;
                    text-align: justify !important;
                    orphans: 3 !important;
                    widows: 3 !important;
                    line-height: 1.3 !important;
                }
                
                /* ULTRA COMPACT table optimization for MAXIMUM space usage */
                table {
                    width: 100% !important;
                    border-collapse: collapse !important;
                    margin: 4pt 0 !important;
                    font-size: 9pt !important;
                    page-break-inside: auto !important;
                    border-spacing: 0 !important;
                }
                
                th, td {
                    border: 0.25pt solid #bdc3c7 !important;
                    padding: 2pt 3pt !important;
                    text-align: left !important;
                    vertical-align: top !important;
                    line-height: 1.2 !important;
                }
                
                th {
                    background-color: #ecf0f1 !important;
                    font-weight: 600 !important;
                    color: #2c3e50 !important;
                    font-size: 9pt !important;
                }
                
                /* COMPACT list optimization */
                ul, ol {
                    margin: 2pt 0 !important;
                    padding-left: 12pt !important;
                }
                
                li {
                    margin: 1pt 0 !important;
                    line-height: 1.2 !important;
                }
                
                /* SMART page break control */
                .page-break {
                    page-break-before: always !important;
                }
                
                .no-break {
                    page-break-inside: avoid !important;
                }
                
                /* Remove ALL unnecessary elements for maximum content */
                .navbar, .sidebar, .footer, .header, .nav, .menu, .breadcrumb {
                    display: none !important;
                }
                
                /* OPTIMIZED images for maximum space */
                img {
                    max-width: 100% !important;
                    height: auto !important;
                    page-break-inside: avoid !important;
                    margin: 2pt 0 !important;
                }
                
                /* ELEGANT code blocks */
                pre, code {
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
                    font-size: 8pt !important;
                    background-color: #f8f9fa !important;
                    border: 0.25pt solid #dee2e6 !important;
                    padding: 1pt 2pt !important;
                    page-break-inside: avoid !important;
                    line-height: 1.1 !important;
                }
                
                /* MAXIMUM content density adjustments */
                @media print {
                    body { 
                        font-size: 9pt !important; 
                        line-height: 1.25 !important;
                    }
                    h1 { font-size: 13pt !important; }
                    h2 { font-size: 11pt !important; }
                    h3 { font-size: 10pt !important; }
                    table { font-size: 8pt !important; }
                    th, td { padding: 1pt 2pt !important; }
                }
                
                /* ELEGANT form elements */
                input, textarea, select {
                    border: 0.5pt solid #bdc3c7 !important;
                    padding: 1pt !important;
                    font-size: 9pt !important;
                }
                
                /* PROFESSIONAL dividers */
                hr {
                    border: none !important;
                    border-top: 0.5pt solid #bdc3c7 !important;
                    margin: 4pt 0 !important;
                }
                
                /* COMPACT blockquotes */
                blockquote {
                    margin: 3pt 0 !important;
                    padding: 2pt 6pt !important;
                    border-left: 2pt solid #3498db !important;
                    background-color: #f8f9fa !important;
                    font-style: italic !important;
                }
            </style>
            """
            
            # Insert CSS before closing head tag or at the beginning if no head
            if '</head>' in content:
                content = content.replace('</head>', f'{pdf_css}</head>')
            elif '<head>' in content:
                content = content.replace('<head>', f'<head>{pdf_css}')
            else:
                # Add head section if it doesn't exist
                if '<html>' in content:
                    content = content.replace('<html>', f'<html><head>{pdf_css}</head>')
                else:
                    content = f'<html><head>{pdf_css}</head><body>{content}</body></html>'
            
            with open(enhanced_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return enhanced_path
            
        except Exception as e:
            logger.warning(f"Failed to enhance HTML {html_path.name}: {e}")
            return html_path  # Return original if enhancement fails

    def convert_file(self, html_path: Path) -> Optional[Path]:
        """
        Convert single HTML file to PDF with enhanced styling.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Path to generated PDF, or None if conversion failed
        """
        try:
            # Generate output PDF path in temp directory
            pdf_filename = html_path.stem + '.pdf'
            pdf_path = self.temp_dir / pdf_filename
            
            logger.info(f"Converting {html_path.name} to PDF with enhanced styling...")
            
            # Enhance HTML for better PDF rendering
            enhanced_html = self.enhance_html_for_pdf(html_path)
            
            # Convert enhanced HTML to PDF
            pdfkit.from_file(str(enhanced_html), str(pdf_path), options=self.options)
            
            # Clean up enhanced HTML file
            if enhanced_html != html_path and enhanced_html.exists():
                enhanced_html.unlink()
            
            logger.info(f"Successfully converted {html_path.name}")
            return pdf_path
            
        except Exception as e:
            logger.warning(f"Failed to convert {html_path.name}: {e}")
            return None
    
    def convert_batch(self, html_files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Convert multiple HTML files to PDFs.
        
        Args:
            html_files: List of HTML file paths
            
        Returns:
            Tuple of (successful_pdfs, failed_conversions)
            failed_conversions is list of (file_path, error_message) tuples
        """
        successful_pdfs = []
        failed_conversions = []
        
        for html_file in html_files:
            try:
                pdf_path = self.convert_file(html_file)
                if pdf_path and pdf_path.exists():
                    successful_pdfs.append(pdf_path)
                else:
                    failed_conversions.append((html_file, "Conversion failed - no output generated"))
            except Exception as e:
                error_msg = str(e)
                failed_conversions.append((html_file, error_msg))
                logger.error(f"Error converting {html_file}: {error_msg}")
        
        return successful_pdfs, failed_conversions
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.glob('*.pdf'):
                    file.unlink()
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")
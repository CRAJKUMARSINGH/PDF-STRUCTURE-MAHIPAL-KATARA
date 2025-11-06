"""HTML to PDF service for Flask integration."""
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .models import ConversionResult, ConverterConfig
from .scanner import scan_html_files
from .converter import HTMLConverter
from .merger import merge_pdfs

logger = logging.getLogger(__name__)


class HTMLToPDFService:
    """Service class for HTML to PDF conversion in Flask app."""
    
    def __init__(self, input_folder: str = "INPUT_DATA", output_folder: str = "OUTPUT_PDF", 
                 page_size: str = "A4", orientation: str = "Portrait"):
        """
        Initialize the HTML to PDF service with enhanced styling.
        
        Args:
            input_folder: Directory containing HTML files
            output_folder: Directory for output PDF files
            page_size: PDF page size (A4, A3, Letter, etc.)
            orientation: Page orientation (Portrait or Landscape)
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.temp_dir = Path("temp_html2pdf")
        self.page_size = page_size
        self.orientation = orientation
        
        # Ensure directories exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
    
    def scan_html_files(self) -> List[Path]:
        """
        Scan input folder for HTML files.
        
        Returns:
            List of HTML file paths
        """
        try:
            return scan_html_files(self.input_folder)
        except Exception as e:
            logger.error(f"Error scanning HTML files: {e}")
            return []
    
    def convert_html_to_pdf(self, html_files: Optional[List[str]] = None, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert HTML files to a single combined PDF.
        
        Args:
            html_files: List of HTML filenames to convert (if None, converts all)
            output_filename: Name for output PDF file (if None, generates timestamp-based name)
            
        Returns:
            Dictionary with conversion results
        """
        try:
            # Get HTML files to convert
            if html_files:
                files_to_convert = [self.input_folder / filename for filename in html_files 
                                  if (self.input_folder / filename).exists()]
            else:
                files_to_convert = self.scan_html_files()
            
            if not files_to_convert:
                return {
                    'success': False,
                    'error': 'No HTML files found to convert',
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            # Generate output filename
            if not output_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f'combined_html_{timestamp}.pdf'
            
            output_path = self.output_folder / output_filename
            
            # Initialize converter with enhanced settings
            converter = HTMLConverter(self.temp_dir, self.page_size, self.orientation)
            
            # Convert HTML files to PDFs
            successful_pdfs, failed_conversions = converter.convert_batch(files_to_convert)
            
            if not successful_pdfs:
                converter.cleanup()
                return {
                    'success': False,
                    'error': 'No HTML files were successfully converted',
                    'total': len(files_to_convert),
                    'successful': 0,
                    'failed': len(failed_conversions),
                    'failures': [{'file': str(f[0].name), 'error': f[1]} for f in failed_conversions]
                }
            
            # Merge PDFs
            merge_success = merge_pdfs(successful_pdfs, output_path)
            
            # Clean up temporary files
            converter.cleanup()
            
            if not merge_success:
                return {
                    'success': False,
                    'error': 'Failed to merge PDFs',
                    'total': len(files_to_convert),
                    'successful': len(successful_pdfs),
                    'failed': len(failed_conversions)
                }
            
            return {
                'success': True,
                'output_file': output_filename,
                'output_path': str(output_path),
                'total': len(files_to_convert),
                'successful': len(successful_pdfs),
                'failed': len(failed_conversions),
                'failures': [{'file': str(f[0].name), 'error': f[1]} for f in failed_conversions] if failed_conversions else []
            }
            
        except Exception as e:
            logger.error(f"Error in HTML to PDF conversion: {e}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'successful': 0,
                'failed': 0
            }
    
    def get_html_files(self) -> List[str]:
        """
        Get list of HTML files in input directory.
        
        Returns:
            List of HTML filenames
        """
        html_files = self.scan_html_files()
        return [f.name for f in html_files]
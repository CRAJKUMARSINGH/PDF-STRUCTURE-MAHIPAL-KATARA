"""HTML to PDF converter module."""
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import pdfkit

logger = logging.getLogger(__name__)


class HTMLConverter:
    """Converts HTML files to PDF format."""
    
    def __init__(self, temp_dir: Path):
        """
        Initialize converter with temporary directory for intermediate PDFs.
        
        Args:
            temp_dir: Path to temporary directory for storing intermediate PDFs
        """
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure wkhtmltopdf options
        self.options = {
            'enable-local-file-access': None,
            'encoding': 'UTF-8',
            'quiet': ''
        }
    
    def convert_file(self, html_path: Path) -> Optional[Path]:
        """
        Convert single HTML file to PDF.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Path to generated PDF, or None if conversion failed
        """
        try:
            # Generate output PDF path in temp directory
            pdf_filename = html_path.stem + '.pdf'
            pdf_path = self.temp_dir / pdf_filename
            
            logger.info(f"Converting {html_path.name} to PDF...")
            
            # Convert HTML to PDF
            pdfkit.from_file(str(html_path), str(pdf_path), options=self.options)
            
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

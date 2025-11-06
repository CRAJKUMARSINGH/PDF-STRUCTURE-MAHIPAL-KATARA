"""PDF merger module."""
from pathlib import Path
from typing import List
import logging
from PyPDF2 import PdfMerger

logger = logging.getLogger(__name__)


def merge_pdfs(pdf_files: List[Path], output_path: Path) -> bool:
    """
    Merge multiple PDF files into single output file.
    
    Args:
        pdf_files: List of PDF file paths in desired order
        output_path: Path for output merged PDF
        
    Returns:
        True if merge successful, False otherwise
    """
    if not pdf_files:
        logger.error("No PDF files to merge")
        return False
    
    try:
        logger.info(f"Merging {len(pdf_files)} PDF files...")
        
        merger = PdfMerger()
        
        for pdf_file in pdf_files:
            if not pdf_file.exists():
                logger.warning(f"PDF file not found: {pdf_file}")
                continue
            
            try:
                merger.append(str(pdf_file))
                logger.debug(f"Added {pdf_file.name} to merger")
            except Exception as e:
                logger.warning(f"Failed to add {pdf_file.name}: {e}")
        
        # Write merged PDF
        merger.write(str(output_path))
        merger.close()
        
        logger.info(f"Successfully merged PDFs to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to merge PDFs: {e}")
        return False
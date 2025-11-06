"""File scanner module for discovering HTML files."""
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def scan_html_files(source_dir: Path) -> List[Path]:
    """
    Scan directory for HTML files and return sorted list.
    
    Args:
        source_dir: Path to directory to scan
        
    Returns:
        List of Path objects for .html and .htm files, sorted alphabetically
        
    Raises:
        FileNotFoundError: If source directory doesn't exist
        PermissionError: If directory cannot be accessed
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {source_dir}")
    
    try:
        # Find all .html and .htm files
        html_files = []
        for pattern in ['*.html', '*.htm']:
            html_files.extend(source_dir.glob(pattern))
        
        # Sort alphabetically by filename
        html_files.sort(key=lambda p: p.name.lower())
        
        logger.info(f"Found {len(html_files)} HTML files in {source_dir}")
        return html_files
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory: {source_dir}")
        raise
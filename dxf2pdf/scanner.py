"""File scanner module for discovering DXF files."""
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def scan_dxf_files(input_path: Path) -> List[Path]:
    """
    Scan for DXF files from file or directory path.
    
    Args:
        input_path: Path to DXF file or directory
        
    Returns:
        List of Path objects for .dxf files
        
    Raises:
        FileNotFoundError: If input path doesn't exist
        PermissionError: If path cannot be accessed
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")
    
    dxf_files = []
    
    try:
        if input_path.is_file():
            # Single file
            if input_path.suffix.lower() == '.dxf':
                dxf_files.append(input_path)
            else:
                logger.warning(f"File is not a DXF file: {input_path}")
        elif input_path.is_dir():
            # Directory - find all DXF files
            dxf_files = list(input_path.glob('*.dxf')) + list(input_path.glob('*.DXF'))
            dxf_files.sort(key=lambda p: p.name.lower())
        
        logger.info(f"Found {len(dxf_files)} DXF files")
        return dxf_files
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing path: {input_path}")
        raise

"""DXF parser module."""
from pathlib import Path
import logging
import ezdxf

logger = logging.getLogger(__name__)


class DXFParseError(Exception):
    """Exception raised when DXF file cannot be parsed."""
    pass


class DXFParser:
    """Parses DXF files and extracts drawing data."""
    
    def parse_file(self, dxf_path: Path):
        """
        Parse DXF file and return drawing document.
        
        Args:
            dxf_path: Path to DXF file
            
        Returns:
            ezdxf Drawing object
            
        Raises:
            DXFParseError: If file cannot be parsed
        """
        try:
            logger.info(f"Parsing DXF file: {dxf_path.name}")
            doc = ezdxf.readfile(str(dxf_path))
            logger.debug(f"Successfully parsed {dxf_path.name}")
            return doc
        except IOError as e:
            raise DXFParseError(f"Cannot read file: {e}")
        except ezdxf.DXFStructureError as e:
            raise DXFParseError(f"Invalid DXF structure: {e}")
        except Exception as e:
            raise DXFParseError(f"Parse error: {e}")

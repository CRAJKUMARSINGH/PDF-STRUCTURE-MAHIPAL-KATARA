"""DXF parser module."""
from pathlib import Path
import logging
import ezdxf
from ezdxf import recover

logger = logging.getLogger(__name__)


class DXFParseError(Exception):
    """Exception raised when DXF file cannot be parsed."""
    pass


class DXFParser:
    """Parses DXF files and extracts drawing data."""
    
    def parse_file(self, dxf_path: Path):
        """
        Parse DXF file and return drawing document.
        Uses recovery mode if normal parsing fails.
        
        Args:
            dxf_path: Path to DXF file
            
        Returns:
            ezdxf Drawing object
            
        Raises:
            DXFParseError: If file cannot be parsed
        """
        try:
            logger.info(f"Parsing DXF file: {dxf_path.name}")
            
            # Try to read the file normally
            doc = ezdxf.readfile(str(dxf_path))
            
            # Verify the document has a modelspace
            msp = doc.modelspace()
            if msp is None:
                raise DXFParseError("DXF file has no modelspace")
            
            # Count entities
            entity_count = len(list(msp))
            logger.info(f"Successfully parsed {dxf_path.name} - Found {entity_count} entities")
            
            if entity_count == 0:
                logger.warning(f"DXF file {dxf_path.name} contains no entities")
            
            return doc
            
        except ezdxf.DXFStructureError as e:
            # Try recovery mode
            logger.warning(f"Normal parsing failed, attempting recovery mode: {e}")
            try:
                doc, auditor = recover.readfile(str(dxf_path))
                
                if auditor.has_errors:
                    logger.warning(f"DXF file has {len(auditor.errors)} errors (recovered)")
                    for error in auditor.errors[:3]:
                        logger.warning(f"  - {error}")
                
                # Verify modelspace
                msp = doc.modelspace()
                if msp is None:
                    raise DXFParseError("DXF file has no modelspace (even after recovery)")
                
                entity_count = len(list(msp))
                logger.info(f"Successfully recovered {dxf_path.name} - Found {entity_count} entities")
                
                return doc
                
            except Exception as recover_error:
                error_msg = f"Recovery mode failed: {recover_error}"
                logger.error(error_msg)
                raise DXFParseError(error_msg)
            
        except IOError as e:
            error_msg = f"Cannot read file: {e}"
            logger.error(error_msg)
            raise DXFParseError(error_msg)
        except ezdxf.DXFVersionError as e:
            error_msg = f"Unsupported DXF version: {e}"
            logger.error(error_msg)
            raise DXFParseError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected parse error: {type(e).__name__} - {e}"
            logger.error(error_msg)
            raise DXFParseError(error_msg)

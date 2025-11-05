"""Scale calculator module."""
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class ScaleCalculator:
    """Calculates scale factor and positioning for A4 landscape."""
    
    # A4 landscape dimensions in mm
    A4_WIDTH_MM = 297
    A4_HEIGHT_MM = 210
    MARGIN_MM = 10
    
    def __init__(self):
        """Initialize scale calculator."""
        self.drawable_width = self.A4_WIDTH_MM - (2 * self.MARGIN_MM)
        self.drawable_height = self.A4_HEIGHT_MM - (2 * self.MARGIN_MM)
    
    def calculate_scale(self, bbox: Tuple[float, float, float, float]) -> float:
        """
        Calculate scale factor to fit drawing on A4 landscape.
        
        Args:
            bbox: Bounding box (min_x, min_y, max_x, max_y)
            
        Returns:
            Scale factor to apply to drawing
        """
        min_x, min_y, max_x, max_y = bbox
        
        # Calculate drawing dimensions
        drawing_width = max_x - min_x
        drawing_height = max_y - min_y
        
        if drawing_width <= 0 or drawing_height <= 0:
            logger.warning("Invalid drawing dimensions, using scale 1.0")
            return 1.0
        
        # Calculate scale factors for width and height
        scale_x = self.drawable_width / drawing_width
        scale_y = self.drawable_height / drawing_height
        
        # Use the smaller scale to ensure drawing fits
        scale = min(scale_x, scale_y)
        
        logger.info(f"Drawing size: {drawing_width:.2f} x {drawing_height:.2f}")
        logger.info(f"Calculated scale: {scale:.4f}")
        
        return scale
    
    def calculate_offset(self, bbox: Tuple[float, float, float, float], scale: float) -> Tuple[float, float]:
        """
        Calculate offset to center drawing on page.
        
        Args:
            bbox: Bounding box (min_x, min_y, max_x, max_y)
            scale: Scale factor
            
        Returns:
            Tuple of (offset_x, offset_y) in mm
        """
        min_x, min_y, max_x, max_y = bbox
        
        # Calculate scaled drawing dimensions
        scaled_width = (max_x - min_x) * scale
        scaled_height = (max_y - min_y) * scale
        
        # Calculate centering offset
        offset_x = self.MARGIN_MM + (self.drawable_width - scaled_width) / 2
        offset_y = self.MARGIN_MM + (self.drawable_height - scaled_height) / 2
        
        logger.info(f"Centering offset: ({offset_x:.2f}, {offset_y:.2f}) mm")
        
        return (offset_x, offset_y)

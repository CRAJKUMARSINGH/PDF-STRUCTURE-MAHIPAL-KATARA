"""Geometry processor module."""
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class GeometryProcessor:
    """Extracts entities and calculates bounding box from DXF drawings."""
    
    def extract_entities(self, drawing) -> List[Any]:
        """
        Extract all drawable entities from DXF drawing.
        
        Args:
            drawing: ezdxf Drawing object
            
        Returns:
            List of DXF entities
        """
        entities = []
        
        try:
            msp = drawing.modelspace()
            
            # Get all entities from modelspace
            for entity in msp:
                # Filter supported entity types
                if entity.dxftype() in ['LINE', 'CIRCLE', 'ARC', 'POLYLINE', 
                                       'LWPOLYLINE', 'TEXT', 'MTEXT', 'POINT',
                                       'ELLIPSE', 'SPLINE', 'INSERT']:
                    entities.append(entity)
            
            logger.info(f"Extracted {len(entities)} entities")
            
        except Exception as e:
            logger.warning(f"Error extracting entities: {e}")
        
        return entities
    
    def calculate_bounding_box(self, entities: List[Any]) -> Tuple[float, float, float, float]:
        """
        Calculate bounding box of all entities.
        
        Args:
            entities: List of DXF entities
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
            
        Raises:
            ValueError: If no entities or cannot calculate bounds
        """
        if not entities:
            raise ValueError("No entities to calculate bounding box")
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in entities:
            try:
                # Try to get bounding box from entity
                if hasattr(entity, 'bounding_box'):
                    bbox = entity.bounding_box
                    if bbox.has_data:
                        min_x = min(min_x, bbox.extmin.x)
                        min_y = min(min_y, bbox.extmin.y)
                        max_x = max(max_x, bbox.extmax.x)
                        max_y = max(max_y, bbox.extmax.y)
                
                # Fallback: get start/end points for lines
                elif entity.dxftype() == 'LINE':
                    min_x = min(min_x, entity.dxf.start.x, entity.dxf.end.x)
                    min_y = min(min_y, entity.dxf.start.y, entity.dxf.end.y)
                    max_x = max(max_x, entity.dxf.start.x, entity.dxf.end.x)
                    max_y = max(max_y, entity.dxf.start.y, entity.dxf.end.y)
                
                # Circle
                elif entity.dxftype() == 'CIRCLE':
                    cx, cy = entity.dxf.center.x, entity.dxf.center.y
                    r = entity.dxf.radius
                    min_x = min(min_x, cx - r)
                    min_y = min(min_y, cy - r)
                    max_x = max(max_x, cx + r)
                    max_y = max(max_y, cy + r)
                    
            except Exception as e:
                logger.debug(f"Could not process entity {entity.dxftype()}: {e}")
                continue
        
        if min_x == float('inf'):
            raise ValueError("Could not calculate bounding box from entities")
        
        logger.info(f"Bounding box: ({min_x:.2f}, {min_y:.2f}) to ({max_x:.2f}, {max_y:.2f})")
        
        return (min_x, min_y, max_x, max_y)

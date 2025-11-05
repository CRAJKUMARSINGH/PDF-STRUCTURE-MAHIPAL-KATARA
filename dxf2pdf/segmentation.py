"""Intelligent segmentation of DXF drawings."""
from typing import List, Tuple, Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class DrawingSegmenter:
    """Intelligently segments DXF drawings into logical sections."""
    
    def __init__(self, entities: List[Any], bbox: Tuple[float, float, float, float]):
        """
        Initialize segmenter.
        
        Args:
            entities: List of DXF entities
            bbox: Overall bounding box (min_x, min_y, max_x, max_y)
        """
        self.entities = entities
        self.bbox = bbox
        self.min_x, self.min_y, self.max_x, self.max_y = bbox
        self.width = self.max_x - self.min_x
        self.height = self.max_y - self.min_y
    
    def segment_by_layer(self) -> Dict[str, List[Any]]:
        """
        Segment entities by layer.
        
        Returns:
            Dictionary mapping layer names to entity lists
        """
        layers = defaultdict(list)
        
        for entity in self.entities:
            try:
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0'
                layers[layer].append(entity)
            except:
                layers['0'].append(entity)
        
        logger.info(f"Found {len(layers)} layers: {list(layers.keys())}")
        return dict(layers)
    
    def segment_by_spatial_clustering(self, num_segments: int = 3) -> List[Tuple[Tuple[float, float, float, float], List[Any]]]:
        """
        Segment entities by spatial clustering.
        
        Args:
            num_segments: Number of segments to create
            
        Returns:
            List of (bbox, entities) tuples for each segment
        """
        if num_segments <= 1:
            return [(self.bbox, self.entities)]
        
        # Determine split direction based on aspect ratio
        aspect = self.width / self.height if self.height > 0 else 1
        
        if aspect > 1.5:
            # Wide drawing - split horizontally
            return self._split_horizontal(num_segments)
        elif aspect < 0.67:
            # Tall drawing - split vertically
            return self._split_vertical(num_segments)
        else:
            # Balanced - use grid
            return self._split_grid(num_segments)
    
    def _split_horizontal(self, num_segments: int) -> List[Tuple[Tuple[float, float, float, float], List[Any]]]:
        """Split drawing horizontally into segments."""
        segments = []
        segment_width = self.width / num_segments
        
        for i in range(num_segments):
            seg_min_x = self.min_x + (i * segment_width)
            seg_max_x = self.min_x + ((i + 1) * segment_width)
            seg_bbox = (seg_min_x, self.min_y, seg_max_x, self.max_y)
            
            # Find entities in this segment
            seg_entities = []
            for entity in self.entities:
                if self._entity_in_bbox(entity, seg_bbox):
                    seg_entities.append(entity)
            
            if seg_entities:
                segments.append((seg_bbox, seg_entities))
                logger.info(f"Segment {i+1}: {len(seg_entities)} entities")
        
        return segments
    
    def _split_vertical(self, num_segments: int) -> List[Tuple[Tuple[float, float, float, float], List[Any]]]:
        """Split drawing vertically into segments."""
        segments = []
        segment_height = self.height / num_segments
        
        for i in range(num_segments):
            seg_min_y = self.min_y + (i * segment_height)
            seg_max_y = self.min_y + ((i + 1) * segment_height)
            seg_bbox = (self.min_x, seg_min_y, self.max_x, seg_max_y)
            
            # Find entities in this segment
            seg_entities = []
            for entity in self.entities:
                if self._entity_in_bbox(entity, seg_bbox):
                    seg_entities.append(entity)
            
            if seg_entities:
                segments.append((seg_bbox, seg_entities))
                logger.info(f"Segment {i+1}: {len(seg_entities)} entities")
        
        return segments
    
    def _split_grid(self, num_segments: int) -> List[Tuple[Tuple[float, float, float, float], List[Any]]]:
        """Split drawing into grid segments."""
        segments = []
        
        if num_segments <= 2:
            # 1x2 or 2x1
            return self._split_horizontal(num_segments)
        elif num_segments <= 4:
            # 2x2 grid
            rows = 2
            cols = 2
        else:
            # 2x3 or 3x2 grid
            rows = 2
            cols = 3
        
        segment_width = self.width / cols
        segment_height = self.height / rows
        
        for row in range(rows):
            for col in range(cols):
                if len(segments) >= num_segments:
                    break
                
                seg_min_x = self.min_x + (col * segment_width)
                seg_max_x = self.min_x + ((col + 1) * segment_width)
                seg_min_y = self.min_y + (row * segment_height)
                seg_max_y = self.min_y + ((row + 1) * segment_height)
                
                seg_bbox = (seg_min_x, seg_min_y, seg_max_x, seg_max_y)
                
                # Find entities in this segment
                seg_entities = []
                for entity in self.entities:
                    if self._entity_in_bbox(entity, seg_bbox):
                        seg_entities.append(entity)
                
                if seg_entities:
                    segments.append((seg_bbox, seg_entities))
                    logger.info(f"Segment {len(segments)}: {len(seg_entities)} entities")
        
        return segments
    
    def segment_by_layer_and_spatial(self, num_segments: int = 3) -> List[Tuple[str, Tuple[float, float, float, float], List[Any]]]:
        """
        Segment by combining layer and spatial information.
        
        Returns:
            List of (layer_name, bbox, entities) tuples
        """
        layers = self.segment_by_layer()
        
        # If we have multiple meaningful layers, use them
        if len(layers) > 1 and len(layers) <= num_segments:
            segments = []
            for layer_name, layer_entities in sorted(layers.items()):
                if len(layer_entities) > 0:
                    # Calculate bbox for this layer
                    layer_bbox = self._calculate_entities_bbox(layer_entities)
                    segments.append((layer_name, layer_bbox, layer_entities))
            
            logger.info(f"Using {len(segments)} layer-based segments")
            return segments
        
        # Otherwise use spatial clustering
        spatial_segments = self.segment_by_spatial_clustering(num_segments)
        return [('Section ' + str(i+1), bbox, entities) 
                for i, (bbox, entities) in enumerate(spatial_segments)]
    
    def _entity_in_bbox(self, entity, bbox: Tuple[float, float, float, float]) -> bool:
        """Check if entity intersects with bounding box."""
        min_x, min_y, max_x, max_y = bbox
        
        try:
            if hasattr(entity, 'bounding_box'):
                ebbox = entity.bounding_box
                if ebbox.has_data:
                    # Check intersection
                    return not (ebbox.extmax.x < min_x or ebbox.extmin.x > max_x or
                              ebbox.extmax.y < min_y or ebbox.extmin.y > max_y)
            
            # Fallback for specific entity types
            if entity.dxftype() == 'LINE':
                sx, sy = entity.dxf.start.x, entity.dxf.start.y
                ex, ey = entity.dxf.end.x, entity.dxf.end.y
                return ((min_x <= sx <= max_x or min_x <= ex <= max_x) and
                       (min_y <= sy <= max_y or min_y <= ey <= max_y))
            elif entity.dxftype() == 'CIRCLE':
                cx, cy = entity.dxf.center.x, entity.dxf.center.y
                return (min_x <= cx <= max_x and min_y <= cy <= max_y)
            elif entity.dxftype() in ['TEXT', 'MTEXT']:
                if hasattr(entity.dxf, 'insert'):
                    tx, ty = entity.dxf.insert.x, entity.dxf.insert.y
                    return (min_x <= tx <= max_x and min_y <= ty <= max_y)
        except:
            pass
        
        return True  # Include by default
    
    def _calculate_entities_bbox(self, entities: List[Any]) -> Tuple[float, float, float, float]:
        """Calculate bounding box for a list of entities."""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in entities:
            try:
                if hasattr(entity, 'bounding_box'):
                    bbox = entity.bounding_box
                    if bbox.has_data:
                        min_x = min(min_x, bbox.extmin.x)
                        min_y = min(min_y, bbox.extmin.y)
                        max_x = max(max_x, bbox.extmax.x)
                        max_y = max(max_y, bbox.extmax.y)
            except:
                pass
        
        if min_x == float('inf'):
            return self.bbox
        
        return (min_x, min_y, max_x, max_y)

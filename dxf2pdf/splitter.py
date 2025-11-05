"""Smart DXF splitter - detects segments and legend automatically."""
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Island:
    """Represents an independent segment or legend in the drawing."""
    bbox: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    entities: List
    label: str  # 'Segment 1', 'Segment 2', 'Legend', etc.
    area: float
    
    @property
    def width(self):
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self):
        return self.bbox[3] - self.bbox[1]
    
    @property
    def center(self):
        return ((self.bbox[0] + self.bbox[2]) / 2, 
                (self.bbox[1] + self.bbox[3]) / 2)
    
    def best_a4_scale(self, margin_mm: float = 10) -> Tuple[float, Tuple[float, float], str]:
        """
        Calculate best scale and orientation for A4.
        
        Returns:
            (scale, page_size, orientation)
        """
        A4_PORTRAIT = (210, 297)
        A4_LANDSCAPE = (297, 210)
        
        usable_portrait = (A4_PORTRAIT[0] - 2 * margin_mm, A4_PORTRAIT[1] - 2 * margin_mm)
        usable_landscape = (A4_LANDSCAPE[0] - 2 * margin_mm, A4_LANDSCAPE[1] - 2 * margin_mm)
        
        # Calculate scale for each orientation
        scale_portrait = min(usable_portrait[0] / self.width, usable_portrait[1] / self.height)
        scale_landscape = min(usable_landscape[0] / self.width, usable_landscape[1] / self.height)
        
        # Choose orientation with larger scale
        if scale_landscape > scale_portrait:
            return scale_landscape, A4_LANDSCAPE, 'landscape'
        else:
            return scale_portrait, A4_PORTRAIT, 'portrait'


class DXFSplitter:
    """Intelligently splits DXF into segments and legend."""
    
    def __init__(self, doc, entities: List):
        """
        Initialize splitter.
        
        Args:
            doc: ezdxf document
            entities: List of all entities
        """
        self.doc = doc
        self.entities = entities
        self.islands = []
    
    def detect_islands(self) -> List[Island]:
        """
        Detect all independent segments and legend.
        
        Returns:
            List of Island objects
        """
        logger.info("Detecting islands (segments and legend)...")
        
        # Step 1: Find closed polylines and hatches (segment candidates)
        segment_candidates = self._find_segment_candidates()
        
        # Step 2: Find text clusters (legend candidates)
        legend_candidates = self._find_legend_candidates()
        
        # Step 3: Merge overlapping bboxes
        all_candidates = segment_candidates + legend_candidates
        islands = self._merge_overlapping(all_candidates)
        
        # Step 4: Filter out tiny artifacts
        islands = self._filter_tiny_artifacts(islands)
        
        # Step 5: Label islands
        islands = self._label_islands(islands)
        
        logger.info(f"Detected {len(islands)} islands")
        for island in islands:
            logger.info(f"  {island.label}: {island.width:.1f} x {island.height:.1f} mm, area={island.area:.1f}")
        
        self.islands = islands
        return islands
    
    def _find_segment_candidates(self) -> List[Island]:
        """Find closed polylines and hatches as segment candidates."""
        candidates = []
        
        for entity in self.entities:
            try:
                # Skip frozen/off layers
                if hasattr(entity.dxf, 'layer'):
                    layer = entity.dxf.layer
                    if layer in ['DEFPOINTS', '0'] or layer.startswith('_'):
                        continue
                
                # Look for closed polylines
                if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    if hasattr(entity.dxf, 'flags') and (entity.dxf.flags & 1):  # Closed
                        bbox = self._get_entity_bbox(entity)
                        if bbox:
                            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                            candidates.append(Island(bbox, [entity], 'segment', area))
                
                # Look for hatches
                elif entity.dxftype() == 'HATCH':
                    bbox = self._get_entity_bbox(entity)
                    if bbox:
                        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        candidates.append(Island(bbox, [entity], 'segment', area))
                
            except Exception as e:
                logger.debug(f"Error processing entity: {e}")
        
        logger.info(f"Found {len(candidates)} segment candidates")
        return candidates
    
    def _find_legend_candidates(self) -> List[Island]:
        """Find text clusters as legend candidates."""
        text_entities = []
        
        for entity in self.entities:
            if entity.dxftype() in ['TEXT', 'MTEXT']:
                try:
                    if hasattr(entity.dxf, 'insert'):
                        pos = (entity.dxf.insert.x, entity.dxf.insert.y)
                        text_entities.append((pos, entity))
                except:
                    pass
        
        if len(text_entities) < 10:
            return []
        
        # Cluster text entities within 50mm of each other
        clusters = self._cluster_text_entities(text_entities, threshold=50)
        
        candidates = []
        for cluster in clusters:
            if len(cluster) >= 10:  # At least 10 text entities
                entities = [e for _, e in cluster]
                bbox = self._calculate_bbox_for_entities(entities)
                if bbox:
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    candidates.append(Island(bbox, entities, 'legend', area))
        
        logger.info(f"Found {len(candidates)} legend candidates")
        return candidates
    
    def _cluster_text_entities(self, text_entities: List[Tuple[Tuple[float, float], any]], 
                               threshold: float) -> List[List]:
        """Cluster text entities by proximity."""
        if not text_entities:
            return []
        
        clusters = []
        used = set()
        
        for i, (pos1, entity1) in enumerate(text_entities):
            if i in used:
                continue
            
            cluster = [(pos1, entity1)]
            used.add(i)
            
            for j, (pos2, entity2) in enumerate(text_entities):
                if j in used:
                    continue
                
                # Check distance to any point in cluster
                for cluster_pos, _ in cluster:
                    dist = ((pos2[0] - cluster_pos[0])**2 + (pos2[1] - cluster_pos[1])**2)**0.5
                    if dist < threshold:
                        cluster.append((pos2, entity2))
                        used.add(j)
                        break
            
            if len(cluster) >= 5:
                clusters.append(cluster)
        
        return clusters
    
    def _merge_overlapping(self, candidates: List[Island]) -> List[Island]:
        """Merge overlapping or touching bounding boxes."""
        if not candidates:
            return []
        
        # Sort by area (largest first)
        candidates = sorted(candidates, key=lambda x: x.area, reverse=True)
        
        merged = []
        used = set()
        
        for i, island1 in enumerate(candidates):
            if i in used:
                continue
            
            # Start with this island
            merged_bbox = island1.bbox
            merged_entities = island1.entities.copy()
            merged_label = island1.label
            used.add(i)
            
            # Check for overlaps
            changed = True
            while changed:
                changed = False
                for j, island2 in enumerate(candidates):
                    if j in used:
                        continue
                    
                    if self._bboxes_overlap(merged_bbox, island2.bbox, tolerance=20):
                        # Merge
                        merged_bbox = self._merge_bboxes(merged_bbox, island2.bbox)
                        merged_entities.extend(island2.entities)
                        used.add(j)
                        changed = True
            
            area = (merged_bbox[2] - merged_bbox[0]) * (merged_bbox[3] - merged_bbox[1])
            merged.append(Island(merged_bbox, merged_entities, merged_label, area))
        
        return merged
    
    def _filter_tiny_artifacts(self, islands: List[Island]) -> List[Island]:
        """Remove tiny artifacts (< 5% of largest area)."""
        if not islands:
            return []
        
        max_area = max(island.area for island in islands)
        threshold = max_area * 0.05
        
        filtered = [island for island in islands if island.area >= threshold]
        
        logger.info(f"Filtered {len(islands) - len(filtered)} tiny artifacts")
        return filtered
    
    def _label_islands(self, islands: List[Island]) -> List[Island]:
        """Assign proper labels to islands."""
        # Sort by area
        islands = sorted(islands, key=lambda x: x.area, reverse=True)
        
        segment_count = 0
        legend_count = 0
        
        for island in islands:
            if island.label == 'legend':
                legend_count += 1
                island.label = f'Legend {legend_count}' if legend_count > 1 else 'Legend'
            else:
                segment_count += 1
                island.label = f'Segment {segment_count}'
        
        return islands
    
    def _get_entity_bbox(self, entity) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding box for an entity."""
        try:
            if hasattr(entity, 'bounding_box'):
                bbox = entity.bounding_box
                if bbox.has_data:
                    return (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
            
            # Fallback for specific types
            if entity.dxftype() == 'LINE':
                x1, y1 = entity.dxf.start.x, entity.dxf.start.y
                x2, y2 = entity.dxf.end.x, entity.dxf.end.y
                return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            
            elif entity.dxftype() == 'CIRCLE':
                cx, cy = entity.dxf.center.x, entity.dxf.center.y
                r = entity.dxf.radius
                return (cx - r, cy - r, cx + r, cy + r)
        except:
            pass
        
        return None
    
    def _calculate_bbox_for_entities(self, entities: List) -> Optional[Tuple[float, float, float, float]]:
        """Calculate combined bounding box for entities."""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in entities:
            bbox = self._get_entity_bbox(entity)
            if bbox:
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                max_x = max(max_x, bbox[2])
                max_y = max(max_y, bbox[3])
        
        if min_x == float('inf'):
            return None
        
        return (min_x, min_y, max_x, max_y)
    
    def _bboxes_overlap(self, bbox1: Tuple[float, float, float, float], 
                       bbox2: Tuple[float, float, float, float], 
                       tolerance: float = 0) -> bool:
        """Check if two bounding boxes overlap (with tolerance)."""
        return not (bbox1[2] + tolerance < bbox2[0] or 
                   bbox1[0] - tolerance > bbox2[2] or
                   bbox1[3] + tolerance < bbox2[1] or 
                   bbox1[1] - tolerance > bbox2[3])
    
    def _merge_bboxes(self, bbox1: Tuple[float, float, float, float], 
                     bbox2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """Merge two bounding boxes."""
        return (min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3]))

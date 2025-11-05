"""Smart multi-page PDF renderer with intelligent segmentation."""
from pathlib import Path
from typing import List, Tuple, Any
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import black, gray

from .segmentation import DrawingSegmenter

logger = logging.getLogger(__name__)


class SmartRenderer:
    """Renders DXF with intelligent segment detection."""
    
    def __init__(self, page_size: Tuple[float, float] = (297, 210)):
        """Initialize renderer with A4 landscape page size in mm."""
        self.page_width = page_size[0] * mm
        self.page_height = page_size[1] * mm
        self.margin = 10 * mm
        self.legend_height = 20 * mm
        self.drawable_width = self.page_width - (2 * self.margin)
        self.drawable_height = self.page_height - (2 * self.margin) - self.legend_height
    
    def render_to_pdf(
        self,
        entities: List[Any],
        output_path: Path,
        bbox: Tuple[float, float, float, float],
        drawing_name: str = "",
        num_pages: int = 3
    ) -> bool:
        """
        Render DXF with intelligent segmentation.
        
        Args:
            entities: List of DXF entities
            output_path: Output PDF path
            bbox: Overall bounding box
            drawing_name: Drawing name for legend
            num_pages: Target number of pages
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Smart rendering to PDF: {output_path.name}")
            
            # Create segmenter
            segmenter = DrawingSegmenter(entities, bbox)
            
            # Get intelligent segments
            segments = segmenter.segment_by_layer_and_spatial(num_pages)
            
            if not segments:
                logger.error("No segments created")
                return False
            
            logger.info(f"Created {len(segments)} intelligent segments")
            
            # Create PDF
            c = canvas.Canvas(str(output_path), pagesize=(self.page_width, self.page_height))
            
            # Render each segment
            for page_num, (segment_name, seg_bbox, seg_entities) in enumerate(segments, 1):
                logger.info(f"Rendering page {page_num}: {segment_name} ({len(seg_entities)} entities)")
                
                # Calculate scale and offset for this segment
                scale = self._calculate_scale(seg_bbox)
                offset = self._calculate_offset(seg_bbox, scale)
                
                # Render page
                self._render_page(c, seg_entities, seg_bbox, scale, offset, 
                                page_num, len(segments), drawing_name, segment_name)
                
                # Add new page if not last
                if page_num < len(segments):
                    c.showPage()
            
            c.save()
            logger.info(f"Successfully rendered {len(segments)}-page PDF")
            return True
            
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _calculate_scale(self, bbox: Tuple[float, float, float, float]) -> float:
        """Calculate scale factor for bbox."""
        min_x, min_y, max_x, max_y = bbox
        width = max_x - min_x
        height = max_y - min_y
        
        if width <= 0 or height <= 0:
            return 1.0
        
        scale_x = (self.drawable_width / mm) / width
        scale_y = (self.drawable_height / mm) / height
        
        return min(scale_x, scale_y)
    
    def _calculate_offset(self, bbox: Tuple[float, float, float, float], scale: float) -> Tuple[float, float]:
        """Calculate centering offset."""
        min_x, min_y, max_x, max_y = bbox
        
        scaled_width = (max_x - min_x) * scale * mm
        scaled_height = (max_y - min_y) * scale * mm
        
        offset_x = self.margin + (self.drawable_width - scaled_width) / 2
        offset_y = self.margin + (self.drawable_height - scaled_height) / 2
        
        return (offset_x, offset_y)
    
    def _render_page(self, c, entities: List[Any], bbox: Tuple[float, float, float, float],
                    scale: float, offset: Tuple[float, float], page_num: int, total_pages: int,
                    drawing_name: str, segment_name: str):
        """Render a single page."""
        c.setLineWidth(0.5)
        
        min_x, min_y, max_x, max_y = bbox
        offset_x, offset_y = offset
        
        # Render entities
        for entity in entities:
            try:
                self._render_entity(c, entity, scale, offset_x, offset_y, min_x, min_y)
            except Exception as e:
                logger.debug(f"Could not render entity {entity.dxftype()}: {e}")
        
        # Draw border
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(self.margin, self.margin, self.drawable_width, 
               self.drawable_height + self.legend_height)
        
        # Draw legend
        self._draw_legend(c, page_num, total_pages, drawing_name, segment_name, bbox, scale)
    
    def _draw_legend(self, c, page_num: int, total_pages: int, drawing_name: str,
                    segment_name: str, bbox: Tuple[float, float, float, float], scale: float):
        """Draw legend at bottom of page."""
        legend_y = self.page_height - self.margin - self.legend_height
        
        # Background
        c.setFillColor(gray, 0.9)
        c.rect(self.margin, legend_y, self.drawable_width, self.legend_height, fill=1, stroke=0)
        
        # Text
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 11)
        
        text_y = legend_y + (self.legend_height / 2)
        
        # Drawing name and segment
        c.drawString(self.margin + 5, text_y + 8, f"{drawing_name}")
        c.setFont("Helvetica-Bold", 9)
        c.drawString(self.margin + 5, text_y - 2, f"Section: {segment_name}")
        
        # Page number
        c.setFont("Helvetica", 8)
        c.drawString(self.margin + 5, text_y - 12, f"Page {page_num} of {total_pages}")
        
        # Scale info
        c.setFont("Helvetica", 9)
        scale_text = f"Scale: 1:{1/scale:.0f}" if scale < 1 else f"Scale: {scale:.2f}:1"
        c.drawRightString(self.page_width - self.margin - 5, text_y + 5, scale_text)
        
        # Coordinates
        min_x, min_y, max_x, max_y = bbox
        coord_text = f"X: {min_x:.1f} to {max_x:.1f}, Y: {min_y:.1f} to {max_y:.1f}"
        c.setFont("Helvetica", 7)
        c.drawRightString(self.page_width - self.margin - 5, text_y - 8, coord_text)
    
    def _transform_point(self, x: float, y: float, scale: float, 
                        offset_x: float, offset_y: float, 
                        min_x: float, min_y: float) -> Tuple[float, float]:
        """Transform DXF coordinates to PDF coordinates."""
        pdf_x = ((x - min_x) * scale * mm) + offset_x
        pdf_y = ((y - min_y) * scale * mm) + offset_y
        return (pdf_x, pdf_y)
    
    def _render_entity(self, c, entity, scale: float, offset_x: float, 
                      offset_y: float, min_x: float, min_y: float):
        """Render a single DXF entity."""
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            self._render_line(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'CIRCLE':
            self._render_circle(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'ARC':
            self._render_arc(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type in ['POLYLINE', 'LWPOLYLINE']:
            self._render_polyline(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type in ['TEXT', 'MTEXT']:
            self._render_text(c, entity, scale, offset_x, offset_y, min_x, min_y)
    
    def _render_line(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a LINE entity."""
        x1, y1 = self._transform_point(entity.dxf.start.x, entity.dxf.start.y, 
                                       scale, offset_x, offset_y, min_x, min_y)
        x2, y2 = self._transform_point(entity.dxf.end.x, entity.dxf.end.y, 
                                       scale, offset_x, offset_y, min_x, min_y)
        c.line(x1, y1, x2, y2)
    
    def _render_circle(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a CIRCLE entity."""
        cx, cy = self._transform_point(entity.dxf.center.x, entity.dxf.center.y, 
                                       scale, offset_x, offset_y, min_x, min_y)
        radius = entity.dxf.radius * scale * mm
        c.circle(cx, cy, radius, stroke=1, fill=0)
    
    def _render_arc(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render an ARC entity."""
        cx, cy = self._transform_point(entity.dxf.center.x, entity.dxf.center.y, 
                                       scale, offset_x, offset_y, min_x, min_y)
        radius = entity.dxf.radius * scale * mm
        c.circle(cx, cy, radius, stroke=1, fill=0)  # Simplified
    
    def _render_polyline(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a POLYLINE or LWPOLYLINE entity."""
        try:
            points = list(entity.points())
            if len(points) < 2:
                return
            
            x, y = self._transform_point(points[0][0], points[0][1], 
                                        scale, offset_x, offset_y, min_x, min_y)
            p = c.beginPath()
            p.moveTo(x, y)
            
            for point in points[1:]:
                x, y = self._transform_point(point[0], point[1], 
                                            scale, offset_x, offset_y, min_x, min_y)
                p.lineTo(x, y)
            
            if hasattr(entity.dxf, 'flags') and entity.dxf.flags & 1:
                p.close()
            
            c.drawPath(p, stroke=1, fill=0)
        except Exception as e:
            logger.debug(f"Error rendering polyline: {e}")
    
    def _render_text(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a TEXT entity."""
        try:
            if hasattr(entity.dxf, 'insert'):
                x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y, 
                                            scale, offset_x, offset_y, min_x, min_y)
            else:
                return
            
            text = entity.dxf.text if hasattr(entity.dxf, 'text') else str(entity.text)
            height = entity.dxf.height * scale * mm if hasattr(entity.dxf, 'height') else 8
            
            c.setFont("Helvetica", max(6, min(height, 12)))
            c.drawString(x, y, text)
        except Exception as e:
            logger.debug(f"Error rendering text: {e}")

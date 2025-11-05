"""PDF renderer module."""
from pathlib import Path
from typing import List, Tuple, Any
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import ezdxf

logger = logging.getLogger(__name__)


class PDFRenderer:
    """Renders DXF geometry to PDF."""
    
    def __init__(self, page_size: Tuple[float, float] = (297, 210)):
        """
        Initialize renderer with A4 landscape page size in mm.
        
        Args:
            page_size: Tuple of (width, height) in mm
        """
        self.page_width = page_size[0] * mm
        self.page_height = page_size[1] * mm
    
    def render_to_pdf(
        self,
        entities: List[Any],
        output_path: Path,
        scale: float,
        offset: Tuple[float, float],
        bbox: Tuple[float, float, float, float]
    ) -> bool:
        """
        Render DXF entities to PDF file.
        
        Args:
            entities: List of DXF entities to render
            output_path: Path for output PDF
            scale: Scale factor to apply
            offset: Offset for centering (x, y) in mm
            bbox: Bounding box (min_x, min_y, max_x, max_y)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Rendering to PDF: {output_path.name}")
            
            # Create PDF canvas
            c = canvas.Canvas(str(output_path), pagesize=(self.page_width, self.page_height))
            
            # Set line width
            c.setLineWidth(0.5)
            
            min_x, min_y, max_x, max_y = bbox
            offset_x, offset_y = offset
            
            # Convert offset to points
            offset_x_pt = offset_x * mm
            offset_y_pt = offset_y * mm
            
            # Render each entity
            for entity in entities:
                try:
                    self._render_entity(c, entity, scale, offset_x_pt, offset_y_pt, min_x, min_y)
                except Exception as e:
                    logger.debug(f"Could not render entity {entity.dxftype()}: {e}")
            
            # Save PDF
            c.save()
            logger.info(f"Successfully rendered PDF: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            return False
    
    def _transform_point(self, x: float, y: float, scale: float, 
                        offset_x: float, offset_y: float, 
                        min_x: float, min_y: float) -> Tuple[float, float]:
        """Transform DXF coordinates to PDF coordinates."""
        # Translate to origin, scale, then offset
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
        elif entity_type == 'TEXT':
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
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        
        # Draw arc using path
        p = c.beginPath()
        # Note: reportlab uses different angle convention
        extent = end_angle - start_angle
        c.drawPath(p)
    
    def _render_polyline(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a POLYLINE or LWPOLYLINE entity."""
        try:
            points = list(entity.points())
            if len(points) < 2:
                return
            
            # Start path
            x, y = self._transform_point(points[0][0], points[0][1], 
                                        scale, offset_x, offset_y, min_x, min_y)
            p = c.beginPath()
            p.moveTo(x, y)
            
            # Add lines to remaining points
            for point in points[1:]:
                x, y = self._transform_point(point[0], point[1], 
                                            scale, offset_x, offset_y, min_x, min_y)
                p.lineTo(x, y)
            
            # Close if closed polyline
            if hasattr(entity.dxf, 'flags') and entity.dxf.flags & 1:
                p.close()
            
            c.drawPath(p, stroke=1, fill=0)
            
        except Exception as e:
            logger.debug(f"Error rendering polyline: {e}")
    
    def _render_text(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a TEXT entity."""
        try:
            x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            text = entity.dxf.text
            height = entity.dxf.height * scale * mm
            
            c.setFont("Helvetica", max(6, min(height, 12)))
            c.drawString(x, y, text)
        except Exception as e:
            logger.debug(f"Error rendering text: {e}")

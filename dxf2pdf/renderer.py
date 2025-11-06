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
    
    def _get_color_from_aci(self, aci_color: int) -> Tuple[float, float, float]:
        """Convert AutoCAD Color Index (ACI) to RGB values (0-1 range)."""
        # Basic ACI color mapping (simplified)
        aci_colors = {
            1: (1.0, 0.0, 0.0),    # Red
            2: (1.0, 1.0, 0.0),    # Yellow
            3: (0.0, 1.0, 0.0),    # Green
            4: (0.0, 1.0, 1.0),    # Cyan
            5: (0.0, 0.0, 1.0),    # Blue
            6: (1.0, 0.0, 1.0),    # Magenta
            7: (1.0, 1.0, 1.0),    # White
            8: (0.5, 0.5, 0.5),    # Gray
            9: (0.75, 0.75, 0.75), # Light Gray
        }
        return aci_colors.get(aci_color, (0.0, 0.0, 0.0))  # Default to black
    
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
        elif entity_type == 'MTEXT':
            self._render_mtext(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'SPLINE':
            self._render_spline(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'ELLIPSE':
            self._render_ellipse(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'DIMENSION':
            self._render_dimension(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'HATCH':
            self._render_hatch(c, entity, scale, offset_x, offset_y, min_x, min_y)
        elif entity_type == 'INSERT':
            self._render_insert(c, entity, scale, offset_x, offset_y, min_x, min_y)
        else:
            logger.debug(f"Unsupported entity type: {entity_type}")
    
    def _render_line(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a LINE entity."""
        try:
            x1, y1 = self._transform_point(entity.dxf.start.x, entity.dxf.start.y, 
                                           scale, offset_x, offset_y, min_x, min_y)
            x2, y2 = self._transform_point(entity.dxf.end.x, entity.dxf.end.y, 
                                           scale, offset_x, offset_y, min_x, min_y)
            
            # Set line color if available
            if hasattr(entity.dxf, 'color') and entity.dxf.color != 256:  # 256 = BYLAYER
                color = self._get_color_from_aci(entity.dxf.color)
                c.setStrokeColor(color[0], color[1], color[2])
            
            c.line(x1, y1, x2, y2)
            
            # Reset to default color
            c.setStrokeColor(0, 0, 0)  # Black
            
        except Exception as e:
            logger.debug(f"Error rendering line: {e}")
    
    def _render_circle(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a CIRCLE entity."""
        try:
            cx, cy = self._transform_point(entity.dxf.center.x, entity.dxf.center.y, 
                                           scale, offset_x, offset_y, min_x, min_y)
            radius = entity.dxf.radius * scale * mm
            
            # Set line color if available
            if hasattr(entity.dxf, 'color') and entity.dxf.color != 256:  # 256 = BYLAYER
                color = self._get_color_from_aci(entity.dxf.color)
                c.setStrokeColor(color[0], color[1], color[2])
            
            c.circle(cx, cy, radius)
            
            # Reset to default color
            c.setStrokeColor(0, 0, 0)  # Black
            
        except Exception as e:
            logger.debug(f"Error rendering circle: {e}")
    
    def _render_polyline(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a POLYLINE or LWPOLYLINE entity."""
        try:
            points = list(entity.points())
            if len(points) < 2:
                return
            
            # Set line color if available
            if hasattr(entity.dxf, 'color') and entity.dxf.color != 256:  # 256 = BYLAYER
                color = self._get_color_from_aci(entity.dxf.color)
                c.setStrokeColor(color[0], color[1], color[2])
            
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
            
            c.drawPath(p)
            
            # Reset to default color
            c.setStrokeColor(0, 0, 0)  # Black
            
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
    
    def _render_mtext(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render an MTEXT entity."""
        try:
            x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            text = entity.plain_text()
            height = entity.dxf.char_height * scale * mm
            
            c.setFont("Helvetica", max(6, min(height, 12)))
            
            # Split multi-line text
            lines = text.split('\n')
            line_height = height * 1.2
            
            for i, line in enumerate(lines):
                c.drawString(x, y - (i * line_height), line)
        except Exception as e:
            logger.debug(f"Error rendering mtext: {e}")
    
    def _render_spline(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a SPLINE entity as approximated polyline."""
        try:
            # Get spline points (approximation)
            points = list(entity.control_points)
            if len(points) < 2:
                return
            
            # Start path
            x, y = self._transform_point(points[0].x, points[0].y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            p = c.beginPath()
            p.moveTo(x, y)
            
            # Add lines to remaining points (simple approximation)
            for point in points[1:]:
                x, y = self._transform_point(point.x, point.y, 
                                            scale, offset_x, offset_y, min_x, min_y)
                p.lineTo(x, y)
            
            c.drawPath(p)
            
        except Exception as e:
            logger.debug(f"Error rendering spline: {e}")
    
    def _render_ellipse(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render an ELLIPSE entity as approximated circle."""
        try:
            cx, cy = self._transform_point(entity.dxf.center.x, entity.dxf.center.y, 
                                           scale, offset_x, offset_y, min_x, min_y)
            
            # Use major axis length as radius (approximation)
            major_axis = entity.dxf.major_axis
            radius = (major_axis.x**2 + major_axis.y**2)**0.5 * scale * mm
            
            c.circle(cx, cy, radius)
            
        except Exception as e:
            logger.debug(f"Error rendering ellipse: {e}")
    
    def _render_dimension(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a DIMENSION entity."""
        try:
            # For now, just render the definition point as a small circle
            # A full implementation would render the dimension line, arrows, and text
            if hasattr(entity.dxf, 'defpoint'):
                x, y = self._transform_point(entity.dxf.defpoint.x, entity.dxf.defpoint.y,
                                            scale, offset_x, offset_y, min_x, min_y)
                c.circle(x, y, 1 * mm)
            logger.debug("Dimension rendering is simplified - only showing definition point")
        except Exception as e:
            logger.debug(f"Error rendering dimension: {e}")
    
    def _render_hatch(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a HATCH entity."""
        try:
            # For now, just render the boundary of the hatch
            # A full implementation would fill the area with the hatch pattern
            boundary_paths = entity.paths
            for path in boundary_paths:
                if path.path_type_flags & 2:  # Polyline path
                    points = path.vertices
                    if len(points) < 2:
                        continue
                    
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
                    
                    # Close path
                    p.close()
                    c.drawPath(p)
            logger.debug("Hatch rendering is simplified - only showing boundaries")
        except Exception as e:
            logger.debug(f"Error rendering hatch: {e}")
    
    def _render_insert(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render an INSERT entity (block reference)."""
        try:
            # For now, just render the insertion point as a small cross
            # A full implementation would render the entire block content
            x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y,
                                        scale, offset_x, offset_y, min_x, min_y)
            
            # Draw a small cross at the insertion point
            cross_size = 2 * mm
            c.line(x - cross_size, y, x + cross_size, y)  # Horizontal line
            c.line(x, y - cross_size, x, y + cross_size)  # Vertical line
            
            logger.debug("Insert rendering is simplified - only showing insertion point")
        except Exception as e:
            logger.debug(f"Error rendering insert: {e}")
    def _render_point(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a POINT entity."""
        try:
            x, y = self._transform_point(entity.dxf.location.x, entity.dxf.location.y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            
            # Set point color if available
            if hasattr(entity.dxf, 'color') and entity.dxf.color != 256:
                color = self._get_color_from_aci(entity.dxf.color)
                c.setFillColor(color[0], color[1], color[2])
            
            # Draw point as small circle
            point_radius = 0.5 * mm
            c.circle(x, y, point_radius, stroke=1, fill=1)
            
            # Reset color
            c.setFillColor(0, 0, 0)
            
        except Exception as e:
            logger.debug(f"Error rendering point: {e}")
    
    def _render_insert(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render an INSERT entity (block reference)."""
        try:
            # For now, just render the insertion point
            x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            
            # Draw a small square to indicate block insertion point
            size = 2 * mm
            c.rect(x - size/2, y - size/2, size, size, stroke=1, fill=0)
            
            # Add block name if available
            if hasattr(entity.dxf, 'name'):
                c.setFont("Helvetica", 6)
                c.drawString(x + size, y, f"[{entity.dxf.name}]")
            
        except Exception as e:
            logger.debug(f"Error rendering insert: {e}")
    
    def get_rendering_stats(self, entities: List[Any]) -> dict:
        """Get statistics about entity types that can be rendered."""
        stats = {
            'total': len(entities),
            'supported': 0,
            'unsupported': 0,
            'by_type': {}
        }
        
        supported_types = {
            'LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE', 
            'TEXT', 'MTEXT', 'SPLINE', 'ELLIPSE', 'POINT', 'INSERT'
        }
        
        for entity in entities:
            entity_type = entity.dxftype()
            stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1
            
            if entity_type in supported_types:
                stats['supported'] += 1
            else:
                stats['unsupported'] += 1
        
        return stats
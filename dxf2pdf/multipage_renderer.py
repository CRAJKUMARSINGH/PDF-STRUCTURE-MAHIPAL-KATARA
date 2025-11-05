"""Multi-page PDF renderer for DXF files."""
from pathlib import Path
from typing import List, Tuple, Any
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import black, gray
import math

logger = logging.getLogger(__name__)


class MultiPageRenderer:
    """Renders DXF geometry to multi-page PDF with automatic sectioning."""
    
    def __init__(self, page_size: Tuple[float, float] = (297, 210), pages: int = 1):
        """
        Initialize renderer with A4 landscape page size in mm.
        
        Args:
            page_size: Tuple of (width, height) in mm
            pages: Number of pages to split drawing into (1-5)
        """
        self.page_width = page_size[0] * mm
        self.page_height = page_size[1] * mm
        self.num_pages = max(1, min(5, pages))  # Limit to 1-5 pages
        self.margin = 10 * mm
        self.legend_height = 15 * mm
        self.drawable_width = self.page_width - (2 * self.margin)
        self.drawable_height = self.page_height - (2 * self.margin) - self.legend_height
    
    def render_to_pdf(
        self,
        entities: List[Any],
        output_path: Path,
        bbox: Tuple[float, float, float, float],
        drawing_name: str = ""
    ) -> bool:
        """
        Render DXF entities to multi-page PDF file.
        
        Args:
            entities: List of DXF entities to render
            output_path: Path for output PDF
            bbox: Bounding box (min_x, min_y, max_x, max_y)
            drawing_name: Name of the drawing for legend
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Rendering to {self.num_pages}-page PDF: {output_path.name}")
            
            # Create PDF canvas
            c = canvas.Canvas(str(output_path), pagesize=(self.page_width, self.page_height))
            
            min_x, min_y, max_x, max_y = bbox
            drawing_width = max_x - min_x
            drawing_height = max_y - min_y
            
            # Calculate sections based on number of pages
            sections = self._calculate_sections(drawing_width, drawing_height)
            
            # Render each section on a separate page
            for page_num, section in enumerate(sections[:self.num_pages], 1):
                logger.info(f"Rendering page {page_num}/{len(sections)}")
                
                section_bbox = self._get_section_bbox(bbox, section, drawing_width, drawing_height)
                
                # Calculate scale for this section
                scale = self._calculate_section_scale(section_bbox)
                
                # Calculate offset to center section on page
                offset = self._calculate_section_offset(section_bbox, scale)
                
                # Render entities in this section
                self._render_page(c, entities, section_bbox, scale, offset, page_num, drawing_name)
                
                # Add new page if not last
                if page_num < len(sections):
                    c.showPage()
            
            # Save PDF
            c.save()
            logger.info(f"Successfully rendered {self.num_pages}-page PDF: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            return False
    
    def _calculate_sections(self, width: float, height: float) -> List[Tuple[float, float, float, float]]:
        """
        Calculate section divisions based on number of pages.
        
        Returns:
            List of (x_start, y_start, x_end, y_end) tuples as fractions (0-1)
        """
        if self.num_pages == 1:
            return [(0, 0, 1, 1)]
        elif self.num_pages == 2:
            # Split horizontally
            return [(0, 0, 0.5, 1), (0.5, 0, 1, 1)]
        elif self.num_pages == 3:
            # Split into 3 horizontal sections
            return [(0, 0, 0.33, 1), (0.33, 0, 0.67, 1), (0.67, 0, 1, 1)]
        elif self.num_pages == 4:
            # 2x2 grid
            return [(0, 0, 0.5, 0.5), (0.5, 0, 1, 0.5), 
                    (0, 0.5, 0.5, 1), (0.5, 0.5, 1, 1)]
        else:  # 5 pages
            # 2x2 grid + 1 full overview
            return [(0, 0, 1, 1),  # Full overview
                    (0, 0, 0.5, 0.5), (0.5, 0, 1, 0.5),
                    (0, 0.5, 0.5, 1), (0.5, 0.5, 1, 1)]
    
    def _get_section_bbox(self, bbox: Tuple[float, float, float, float], 
                         section: Tuple[float, float, float, float],
                         width: float, height: float) -> Tuple[float, float, float, float]:
        """Calculate actual bounding box for a section."""
        min_x, min_y, max_x, max_y = bbox
        x_start, y_start, x_end, y_end = section
        
        section_min_x = min_x + (x_start * width)
        section_min_y = min_y + (y_start * height)
        section_max_x = min_x + (x_end * width)
        section_max_y = min_y + (y_end * height)
        
        return (section_min_x, section_min_y, section_max_x, section_max_y)
    
    def _calculate_section_scale(self, section_bbox: Tuple[float, float, float, float]) -> float:
        """Calculate scale factor for a section."""
        min_x, min_y, max_x, max_y = section_bbox
        section_width = max_x - min_x
        section_height = max_y - min_y
        
        if section_width <= 0 or section_height <= 0:
            return 1.0
        
        # Calculate scale to fit in drawable area
        scale_x = (self.drawable_width / mm) / section_width
        scale_y = (self.drawable_height / mm) / section_height
        
        return min(scale_x, scale_y)
    
    def _calculate_section_offset(self, section_bbox: Tuple[float, float, float, float], 
                                  scale: float) -> Tuple[float, float]:
        """Calculate offset to center section on page."""
        min_x, min_y, max_x, max_y = section_bbox
        
        scaled_width = (max_x - min_x) * scale * mm
        scaled_height = (max_y - min_y) * scale * mm
        
        offset_x = self.margin + (self.drawable_width - scaled_width) / 2
        offset_y = self.margin + (self.drawable_height - scaled_height) / 2
        
        return (offset_x, offset_y)
    
    def _render_page(self, c, entities: List[Any], section_bbox: Tuple[float, float, float, float],
                    scale: float, offset: Tuple[float, float], page_num: int, drawing_name: str):
        """Render a single page with entities and legend."""
        c.setLineWidth(0.5)
        
        min_x, min_y, max_x, max_y = section_bbox
        offset_x, offset_y = offset
        
        # Render entities
        for entity in entities:
            try:
                if self._entity_in_section(entity, section_bbox):
                    self._render_entity(c, entity, scale, offset_x, offset_y, min_x, min_y)
            except Exception as e:
                logger.debug(f"Could not render entity {entity.dxftype()}: {e}")
        
        # Draw border
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(self.margin, self.margin, self.drawable_width, self.drawable_height + self.legend_height)
        
        # Draw legend
        self._draw_legend(c, page_num, drawing_name, section_bbox, scale)
    
    def _entity_in_section(self, entity, section_bbox: Tuple[float, float, float, float]) -> bool:
        """Check if entity is within section bounds."""
        min_x, min_y, max_x, max_y = section_bbox
        
        try:
            if hasattr(entity, 'bounding_box'):
                bbox = entity.bounding_box
                if bbox.has_data:
                    # Check if entity bbox intersects with section
                    return not (bbox.extmax.x < min_x or bbox.extmin.x > max_x or
                              bbox.extmax.y < min_y or bbox.extmin.y > max_y)
            
            # Fallback checks for specific entity types
            if entity.dxftype() == 'LINE':
                return ((min_x <= entity.dxf.start.x <= max_x or min_x <= entity.dxf.end.x <= max_x) and
                       (min_y <= entity.dxf.start.y <= max_y or min_y <= entity.dxf.end.y <= max_y))
            elif entity.dxftype() == 'CIRCLE':
                cx, cy = entity.dxf.center.x, entity.dxf.center.y
                return (min_x <= cx <= max_x and min_y <= cy <= max_y)
        except:
            pass
        
        return True  # Include by default if can't determine
    
    def _draw_legend(self, c, page_num: int, drawing_name: str, 
                    section_bbox: Tuple[float, float, float, float], scale: float):
        """Draw legend at bottom of page."""
        legend_y = self.page_height - self.margin - self.legend_height
        
        # Background
        c.setFillColor(gray, 0.9)
        c.rect(self.margin, legend_y, self.drawable_width, self.legend_height, fill=1, stroke=0)
        
        # Text
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        
        text_y = legend_y + (self.legend_height / 2) - 3
        
        # Drawing name
        c.drawString(self.margin + 5, text_y + 5, f"Drawing: {drawing_name}")
        
        # Page number
        c.drawString(self.margin + 5, text_y - 8, f"Page {page_num} of {self.num_pages}")
        
        # Scale info
        c.setFont("Helvetica", 8)
        scale_text = f"Scale: 1:{1/scale:.0f}" if scale < 1 else f"Scale: {scale:.2f}:1"
        c.drawRightString(self.page_width - self.margin - 5, text_y, scale_text)
        
        # Section info
        min_x, min_y, max_x, max_y = section_bbox
        section_text = f"Section: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})"
        c.drawRightString(self.page_width - self.margin - 5, text_y - 10, section_text)
    
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
        
        # Draw arc
        p = c.beginPath()
        extent = end_angle - start_angle
        c.drawPath(p)
    
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
            x, y = self._transform_point(entity.dxf.insert.x, entity.dxf.insert.y, 
                                        scale, offset_x, offset_y, min_x, min_y)
            text = entity.dxf.text
            height = entity.dxf.height * scale * mm
            
            c.setFont("Helvetica", max(6, min(height, 12)))
            c.drawString(x, y, text)
        except Exception as e:
            logger.debug(f"Error rendering text: {e}")

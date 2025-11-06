"""Renderer for split DXF islands - one island per A4 page."""
from pathlib import Path
from typing import List, Tuple
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import black, gray

from .splitter import Island

logger = logging.getLogger(__name__)


class SplitRenderer:
    """Renders each island on its own optimally-scaled A4 page."""
    
    def __init__(self):
        """Initialize renderer."""
        self.margin = 10 * mm
        self.legend_height = 15 * mm
    
    def render_islands_to_pdf(
        self,
        islands: List[Island],
        all_entities: List,
        output_path: Path,
        drawing_name: str = ""
    ) -> bool:
        """
        Render each island on its own A4 page.
        
        Args:
            islands: List of Island objects
            all_entities: All entities (for reference)
            output_path: Output PDF path
            drawing_name: Drawing name for legend
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Rendering {len(islands)} islands to PDF: {output_path.name}")
            
            # Start with first island's optimal page size
            if islands:
                _, first_page_size, _ = islands[0].best_a4_scale()
                c = canvas.Canvas(str(output_path), 
                                pagesize=(first_page_size[0] * mm, first_page_size[1] * mm))
            else:
                c = canvas.Canvas(str(output_path), pagesize=(297 * mm, 210 * mm))
            
            # Render each island
            for page_num, island in enumerate(islands, 1):
                logger.info(f"Rendering page {page_num}: {island.label}")
                
                # Get optimal scale and orientation for this island
                scale, page_size, orientation = island.best_a4_scale()
                
                # Set page size
                c.setPageSize((page_size[0] * mm, page_size[1] * mm))
                
                # Calculate offset to center island
                offset = self._calculate_offset(island, scale, page_size)
                
                # Render the island
                self._render_island(c, island, scale, offset, page_num, len(islands), 
                                  drawing_name, orientation)
                
                # Add new page if not last
                if page_num < len(islands):
                    c.showPage()
            
            c.save()
            logger.info(f"Successfully rendered {len(islands)}-page PDF")
            return True
            
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _calculate_offset(self, island: Island, scale: float, 
                         page_size: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate offset to center island on page."""
        min_x, min_y, max_x, max_y = island.bbox
        
        # Scaled dimensions
        scaled_width = (max_x - min_x) * scale * mm
        scaled_height = (max_y - min_y) * scale * mm
        
        # Page dimensions
        page_width = page_size[0] * mm
        page_height = page_size[1] * mm
        
        # Available space (minus margins and legend)
        available_width = page_width - (2 * self.margin)
        available_height = page_height - (2 * self.margin) - self.legend_height
        
        # Center in available space
        offset_x = self.margin + (available_width - scaled_width) / 2
        offset_y = self.margin + (available_height - scaled_height) / 2
        
        return (offset_x, offset_y)
    
    def _render_island(self, c, island: Island, scale: float, 
                      offset: Tuple[float, float], page_num: int, total_pages: int,
                      drawing_name: str, orientation: str):
        """Render a single island on the page."""
        c.setLineWidth(0.5)
        
        min_x, min_y, max_x, max_y = island.bbox
        offset_x, offset_y = offset
        
        # Render all entities in this island
        for entity in island.entities:
            try:
                self._render_entity(c, entity, scale, offset_x, offset_y, min_x, min_y)
            except Exception as e:
                logger.debug(f"Could not render entity {entity.dxftype()}: {e}")
        
        # Draw border around drawing area
        page_width = c._pagesize[0]
        page_height = c._pagesize[1]
        
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(self.margin, self.margin, 
               page_width - 2 * self.margin, 
               page_height - 2 * self.margin)
        
        # Draw legend
        self._draw_legend(c, page_num, total_pages, drawing_name, island, scale, orientation)
    
    def _draw_legend(self, c, page_num: int, total_pages: int, drawing_name: str,
                    island: Island, scale: float, orientation: str):
        """Draw legend at bottom of page."""
        page_width = c._pagesize[0]
        page_height = c._pagesize[1]
        
        legend_y = page_height - self.margin - self.legend_height
        
        # Background
        c.setFillColor(gray, 0.9)
        c.rect(self.margin, legend_y, page_width - 2 * self.margin, 
               self.legend_height, fill=1, stroke=0)
        
        # Text
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 11)
        
        text_y = legend_y + (self.legend_height / 2)
        
        # Drawing name and island label
        c.drawString(self.margin + 5, text_y + 5, f"{drawing_name}")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin + 5, text_y - 7, f"{island.label}")
        
        # Page info
        c.setFont("Helvetica", 8)
        page_text = f"Page {page_num} of {total_pages} | {orientation.upper()}"
        c.drawRightString(page_width - self.margin - 5, text_y + 5, page_text)
        
        # Scale info
        c.setFont("Helvetica-Bold", 9)
        if scale < 1:
            scale_text = f"Scale 1:{1/scale:.0f}"
        else:
            scale_text = f"Scale {scale:.2f}:1"
        c.drawRightString(page_width - self.margin - 5, text_y - 7, scale_text)
        
        # Dimensions
        c.setFont("Helvetica", 7)
        dim_text = f"{island.width:.1f} × {island.height:.1f} mm"
        c.drawString(self.margin + 5, legend_y + 2, dim_text)
    
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
        elif entity_type == 'HATCH':
            self._render_hatch(c, entity, scale, offset_x, offset_y, min_x, min_y)
    
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
        c.circle(cx, cy, radius, stroke=1, fill=0)
    
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
    
    def _render_hatch(self, c, entity, scale, offset_x, offset_y, min_x, min_y):
        """Render a HATCH entity (simplified - just boundary)."""
        try:
            # Draw hatch boundary
            for path in entity.paths:
                if hasattr(path, 'edges'):
                    for edge in path.edges:
                        if edge.EDGE_TYPE == 'LineEdge':
                            x1, y1 = self._transform_point(edge.start[0], edge.start[1],
                                                          scale, offset_x, offset_y, min_x, min_y)
                            x2, y2 = self._transform_point(edge.end[0], edge.end[1],
                                                          scale, offset_x, offset_y, min_x, min_y)
                            c.line(x1, y1, x2, y2)
        except Exception as e:
            logger.debug(f"Error rendering hatch: {e}")
    
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
            
            c.setFont("Helvetica", max(4, min(height, 10)))
            c.drawString(x, y, text)
        except Exception as e:
            logger.debug(f"Error rendering text: {e}")

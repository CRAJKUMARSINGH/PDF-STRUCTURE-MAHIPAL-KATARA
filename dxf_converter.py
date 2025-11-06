import ezdxf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ezdxf.addons.drawing.properties import RenderContext
from ezdxf.addons.drawing.frontend import Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DXFToPDFConverter:
    A4_WIDTH_MM = 297
    A4_HEIGHT_MM = 210
    MARGIN_MM = 10
    DPI = 300
    
    def __init__(self, input_folder="INPUT_DATA", output_folder="OUTPUT_PDF", log_folder="LOGS"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.log_folder = Path(log_folder)
        
        self.output_folder.mkdir(exist_ok=True)
        self.log_folder.mkdir(exist_ok=True)
    
    def get_entity_bounds(self, entity):
        try:
            if hasattr(entity, 'dxf') and hasattr(entity.dxf, 'insert'):
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
                return (x, y, x, y)
            
            if entity.dxftype() == 'LINE':
                return (
                    min(entity.dxf.start.x, entity.dxf.end.x),
                    min(entity.dxf.start.y, entity.dxf.end.y),
                    max(entity.dxf.start.x, entity.dxf.end.x),
                    max(entity.dxf.start.y, entity.dxf.end.y)
                )
            elif entity.dxftype() == 'CIRCLE':
                cx, cy, r = entity.dxf.center.x, entity.dxf.center.y, entity.dxf.radius
                return (cx - r, cy - r, cx + r, cy + r)
            elif entity.dxftype() == 'ARC':
                cx, cy, r = entity.dxf.center.x, entity.dxf.center.y, entity.dxf.radius
                return (cx - r, cy - r, cx + r, cy + r)
            elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = list(entity.get_points())
                if points:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    return (min(xs), min(ys), max(xs), max(ys))
            elif entity.dxftype() == 'TEXT':
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
                return (x, y, x + 10, y + 5)
            elif entity.dxftype() == 'MTEXT':
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
                return (x, y, x + 20, y + 10)
        except Exception as e:
            logger.debug(f"Could not get bounds for {entity.dxftype()}: {e}")
        
        return None
    
    def analyze_drawing_sections(self, msp):
        entities = list(msp)
        if not entities:
            return [entities]
        
        entity_bounds = []
        for entity in entities:
            bounds = self.get_entity_bounds(entity)
            if bounds:
                entity_bounds.append((entity, bounds))
        
        if not entity_bounds:
            return [entities]
        
        all_bounds = [b[1] for b in entity_bounds]
        min_x = min(b[0] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        if total_width == 0 or total_height == 0:
            return [entities]
        
        aspect_ratio = total_width / total_height
        a4_aspect = self.A4_WIDTH_MM / self.A4_HEIGHT_MM
        
        if aspect_ratio < a4_aspect * 1.5 and total_height < total_width * 2:
            return [entities]
        
        y_positions = sorted(set(b[1] for b in all_bounds) | set(b[3] for b in all_bounds))
        
        gaps = []
        for i in range(len(y_positions) - 1):
            gap_size = y_positions[i + 1] - y_positions[i]
            entities_in_gap = sum(1 for b in all_bounds if b[1] <= y_positions[i] and b[3] >= y_positions[i + 1])
            if entities_in_gap == 0 and gap_size > total_height * 0.05:
                gaps.append((y_positions[i], y_positions[i + 1], gap_size))
        
        if not gaps:
            num_sections = max(2, int(total_height / (total_width * a4_aspect)) + 1)
            section_height = total_height / num_sections
            split_points = [min_y + i * section_height for i in range(1, num_sections)]
        else:
            gaps.sort(key=lambda x: x[2], reverse=True)
            num_splits = min(len(gaps), max(1, int(total_height / (total_width * a4_aspect))))
            split_points = [g[0] + (g[1] - g[0]) / 2 for g in gaps[:num_splits]]
            split_points.sort()
        
        sections = [[] for _ in range(len(split_points) + 1)]
        
        for entity, bounds in entity_bounds:
            entity_center_y = (bounds[1] + bounds[3]) / 2
            
            section_idx = 0
            for i, split_y in enumerate(split_points):
                if entity_center_y > split_y:
                    section_idx = i + 1
                else:
                    break
            
            sections[section_idx].append(entity)
        
        sections = [s for s in sections if s]
        
        if len(sections) <= 1:
            return [entities]
        
        return sections
    
    def convert_dxf_to_pdf(self, dxf_path, pdf_path=None, max_pages=50):
        if pdf_path is None:
            pdf_path = self.output_folder / f"{Path(dxf_path).stem}_A4_landscape.pdf"
        
        logger.info(f"Converting {dxf_path} to {pdf_path}")
        
        try:
            doc = ezdxf.readfile(dxf_path)
            
            auditor = doc.audit()
            if auditor.has_errors:
                logger.warning(f"DXF file has {len(auditor.errors)} errors, attempting to fix...")
                for error in auditor.errors[:5]:
                    logger.warning(f"  - {error}")
            
            msp = doc.modelspace()
            
            sections = self.analyze_drawing_sections(msp)
            logger.info(f"Split drawing into {len(sections)} sections")
            
            fig_width_inch = self.A4_WIDTH_MM / 25.4
            fig_height_inch = self.A4_HEIGHT_MM / 25.4
            
            with PdfPages(pdf_path) as pdf:
                for idx, section_entities in enumerate(sections[:max_pages]):
                    if not section_entities:
                        continue
                    
                    logger.info(f"Rendering page {idx + 1}/{len(sections)} with {len(section_entities)} entities")
                    
                    fig = plt.figure(figsize=(fig_width_inch, fig_height_inch), dpi=self.DPI)
                    ax = fig.add_axes((0, 0, 1, 1))
                    ax.set_aspect('equal')
                    
                    ctx = RenderContext(doc)
                    out = MatplotlibBackend(ax)
                    
                    frontend = Frontend(ctx, out)
                    for entity in section_entities:
                        try:
                            frontend.draw_entity(entity)
                        except Exception as e:
                            logger.debug(f"Could not render entity {entity.dxftype()}: {e}")
                    
                    out.finalize()
                    
                    ax.autoscale()
                    ax.margins(0.02)
                    ax.axis('off')
                    
                    pdf.savefig(fig, dpi=self.DPI, bbox_inches='tight', pad_inches=0.1)
                    plt.close(fig)
                
                d = pdf.infodict()
                d['Title'] = f'{Path(dxf_path).stem} - A4 Landscape'
                d['Author'] = 'DXF to PDF Converter'
                d['Subject'] = 'Architectural/Structural Drawing'
                d['Keywords'] = 'DXF, PDF, A4, Landscape, Footing, Structural'
                d['CreationDate'] = datetime.now()
            
            logger.info(f"Successfully created PDF with {len(sections)} pages: {pdf_path}")
            return True, str(pdf_path), len(sections)
        
        except Exception as e:
            logger.error(f"Error converting {dxf_path}: {str(e)}")
            return False, str(e), 0
    
    def batch_convert(self, pattern="*.dxf"):
        dxf_files = list(self.input_folder.glob(pattern))
        dxf_files.extend(self.input_folder.glob(pattern.replace('dxf', 'DXF')))
        dxf_files = list(set(dxf_files))
        
        if not dxf_files:
            logger.warning(f"No DXF files found in {self.input_folder}")
            return []
        
        logger.info(f"Found {len(dxf_files)} DXF files to convert")
        
        results = []
        for dxf_file in dxf_files:
            success, output, pages = self.convert_dxf_to_pdf(dxf_file)
            results.append({
                'input': str(dxf_file),
                'output': output,
                'success': success,
                'pages': pages,
                'timestamp': datetime.now().isoformat()
            })
        
        log_file = self.log_folder / f"conversion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write(f"DXF to PDF Batch Conversion Log\n")
            f.write(f"{'='*80}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total files: {len(results)}\n")
            f.write(f"Successful: {sum(1 for r in results if r['success'])}\n")
            f.write(f"Failed: {sum(1 for r in results if not r['success'])}\n")
            f.write(f"{'='*80}\n\n")
            
            for result in results:
                status = "SUCCESS" if result['success'] else "FAILED"
                f.write(f"{status}: {result['input']}\n")
                if result['success']:
                    f.write(f"  Output: {result['output']}\n")
                    f.write(f"  Pages: {result['pages']}\n")
                else:
                    f.write(f"  Error: {result['output']}\n")
                f.write(f"\n")
        
        logger.info(f"Batch conversion complete. Log saved to {log_file}")
        return results


if __name__ == "__main__":
    converter = DXFToPDFConverter()
    results = converter.batch_convert()
    
    print(f"\n{'='*80}")
    print(f"Batch Conversion Summary")
    print(f"{'='*80}")
    print(f"Total files: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"{'='*80}\n")
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {Path(result['input']).name}")
        if result['success']:
            print(f"  → {result['pages']} pages → {Path(result['output']).name}")

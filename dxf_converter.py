import ezdxf
from ezdxf import recover
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ezdxf.addons.drawing import RenderContext, Frontend
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
    
    def get_drawing_bounds(self, msp):
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in msp:
            try:
                if hasattr(entity, 'dxf'):
                    if entity.dxftype() == 'LINE':
                        min_x = min(min_x, entity.dxf.start.x, entity.dxf.end.x)
                        max_x = max(max_x, entity.dxf.start.x, entity.dxf.end.x)
                        min_y = min(min_y, entity.dxf.start.y, entity.dxf.end.y)
                        max_y = max(max_y, entity.dxf.start.y, entity.dxf.end.y)
                    elif entity.dxftype() in ['CIRCLE', 'ARC']:
                        cx, cy, r = entity.dxf.center.x, entity.dxf.center.y, entity.dxf.radius
                        min_x = min(min_x, cx - r)
                        max_x = max(max_x, cx + r)
                        min_y = min(min_y, cy - r)
                        max_y = max(max_y, cy + r)
                    elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                        for point in entity.get_points():
                            min_x = min(min_x, point[0])
                            max_x = max(max_x, point[0])
                            min_y = min(min_y, point[1])
                            max_y = max(max_y, point[1])
                    elif entity.dxftype() in ['TEXT', 'MTEXT']:
                        x, y = entity.dxf.insert.x, entity.dxf.insert.y
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)
            except Exception as e:
                logger.debug(f"Could not get bounds for {entity.dxftype()}: {e}")
        
        if min_x == float('inf'):
            return 0, 0, 100, 100
        
        return min_x, min_y, max_x, max_y
    
    def calculate_page_regions(self, min_x, min_y, max_x, max_y):
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        if total_width <= 0 or total_height <= 0:
            return [(min_x, min_y, max_x, max_y)]
        
        a4_aspect = self.A4_WIDTH_MM / self.A4_HEIGHT_MM
        page_height = total_width / a4_aspect
        
        if total_height <= page_height * 1.3:
            return [(min_x, min_y, max_x, max_y)]
        
        num_pages = int(np.ceil(total_height / page_height))
        num_pages = min(num_pages, 50)
        
        logger.info(f"Drawing size: {total_width:.1f} x {total_height:.1f}, splitting into {num_pages} page(s)")
        
        regions = []
        section_height = total_height / num_pages
        overlap = section_height * 0.05
        
        for i in range(num_pages):
            y_start = min_y + i * section_height - (overlap if i > 0 else 0)
            y_end = min_y + (i + 1) * section_height + (overlap if i < num_pages - 1 else 0)
            y_end = min(y_end, max_y)
            
            if y_start < max_y:
                regions.append((min_x, y_start, max_x, y_end))
        
        return regions
    
    def convert_dxf_to_pdf(self, dxf_path, pdf_path=None, max_pages=50):
        if pdf_path is None:
            pdf_path = self.output_folder / f"{Path(dxf_path).stem}_A4_landscape.pdf"
        
        logger.info(f"Converting {dxf_path} to {pdf_path}")
        
        try:
            try:
                doc, auditor = recover.readfile(str(dxf_path))
            except IOError:
                logger.error(f"Not a DXF file or I/O error: {dxf_path}")
                return False, "Not a valid DXF file", 0
            except ezdxf.DXFStructureError:
                logger.error(f"Invalid or corrupted DXF file: {dxf_path}")
                return False, "Corrupted DXF file", 0
            
            if auditor.has_errors:
                logger.warning(f"DXF file has {len(auditor.errors)} errors")
                for error in auditor.errors[:3]:
                    logger.warning(f"  - {error}")
            
            msp = doc.modelspace()
            
            min_x, min_y, max_x, max_y = self.get_drawing_bounds(msp)
            regions = self.calculate_page_regions(min_x, min_y, max_x, max_y)
            
            logger.info(f"Drawing bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
            logger.info(f"Creating {len(regions)} page(s)")
            
            fig_width_inch = self.A4_WIDTH_MM / 25.4
            fig_height_inch = self.A4_HEIGHT_MM / 25.4
            
            with PdfPages(pdf_path) as pdf:
                for idx, (rx_min, ry_min, rx_max, ry_max) in enumerate(regions[:max_pages]):
                    logger.info(f"Rendering page {idx + 1}/{len(regions)}")
                    
                    fig = plt.figure(figsize=(fig_width_inch, fig_height_inch), dpi=self.DPI)
                    ax = fig.add_subplot(111)
                    ax.set_aspect('equal')
                    
                    ctx = RenderContext(doc)
                    out = MatplotlibBackend(ax)
                    
                    Frontend(ctx, out).draw_layout(msp, finalize=True)
                    
                    region_width = rx_max - rx_min
                    region_height = ry_max - ry_min
                    
                    if region_width > 0 and region_height > 0:
                        margin_x = region_width * 0.05
                        margin_y = region_height * 0.05
                        
                        ax.set_xlim(rx_min - margin_x, rx_max + margin_x)
                        ax.set_ylim(ry_min - margin_y, ry_max + margin_y)
                    
                    ax.axis('off')
                    
                    pdf.savefig(fig, dpi=self.DPI, bbox_inches='tight', pad_inches=0.1)
                    plt.close(fig)
                
                d = pdf.infodict()
                d['Title'] = f'{Path(dxf_path).stem} - A4 Landscape'
                d['Author'] = 'DXF to PDF Converter'
                d['Subject'] = 'Architectural/Structural Drawing'
                d['Keywords'] = 'DXF, PDF, A4, Landscape, Footing, Structural'
                d['CreationDate'] = datetime.now()
            
            logger.info(f"Successfully created PDF with {len(regions)} page(s): {pdf_path}")
            return True, str(pdf_path), len(regions)
        
        except Exception as e:
            logger.error(f"Error converting {dxf_path}: {str(e)}", exc_info=True)
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

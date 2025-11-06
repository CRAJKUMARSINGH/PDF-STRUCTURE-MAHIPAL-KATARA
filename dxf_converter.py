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
    
    # 3 SCALE OPTIONS CONFIGURATION
    SCALE_OPTIONS = {
        'standard': {
            'factor': 1.0,
            'name': 'Standard Scale',
            'description': 'Normal page count - fast processing',
            'max_pages': 50,
            'dpi_multiplier': 1.0,
            'suffix': ''
        },
        'enlarged_2x': {
            'factor': 2.0,
            'name': '2x Enlarged Scale',
            'description': 'Double detail - moderate processing',
            'max_pages': 100,
            'dpi_multiplier': 1.2,
            'suffix': '_ENLARGED_2x'
        },
        'maximum_4x': {
            'factor': 4.0,
            'name': '4x Maximum Detail',
            'description': 'Maximum precision - detailed processing',
            'max_pages': 200,
            'dpi_multiplier': 1.5,
            'suffix': '_MAXIMUM_4x'
        }
    }
    
    def __init__(self, input_folder="INPUT_DATA", output_folder="OUTPUT_PDF", log_folder="LOGS", 
                 scale_mode='standard'):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.log_folder = Path(log_folder)
        
        # SCALE MODE CONFIGURATION
        if scale_mode not in self.SCALE_OPTIONS:
            scale_mode = 'standard'
            
        self.scale_mode = scale_mode
        self.scale_config = self.SCALE_OPTIONS[scale_mode]
        self.scale_factor = self.scale_config['factor']
        self.detail_enhancement = scale_mode != 'standard'
        self.max_pages = self.scale_config['max_pages']
        
        self.output_folder.mkdir(exist_ok=True)
        self.log_folder.mkdir(exist_ok=True)
        
        logger.info(f"🎯 DXF Converter initialized:")
        logger.info(f"   Scale mode: {self.scale_config['name']} ({self.scale_factor}x)")
        logger.info(f"   Description: {self.scale_config['description']}")
        logger.info(f"   Maximum pages: {self.max_pages}")
        logger.info(f"   Detail enhancement: {'ENABLED' if self.detail_enhancement else 'DISABLED'}")
    
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
        
        # ENLARGED SCALE CALCULATION - 4x more detailed pages
        a4_aspect = self.A4_WIDTH_MM / self.A4_HEIGHT_MM
        
        if self.detail_enhancement:
            # CALCULATE ENLARGED SCALE REGIONS
            # Reduce the effective page size by scale factor for more detailed view
            effective_page_width = total_width / self.scale_factor
            effective_page_height = effective_page_width / a4_aspect
            
            # Calculate number of pages in both dimensions for grid-based splitting
            pages_horizontal = max(1, int(np.ceil(total_width / effective_page_width)))
            pages_vertical = max(1, int(np.ceil(total_height / effective_page_height)))
            
            total_pages = pages_horizontal * pages_vertical
            total_pages = min(total_pages, self.max_pages)
            
            logger.info(f"🔍 ENLARGED SCALE CONVERSION:")
            logger.info(f"   Drawing size: {total_width:.1f} x {total_height:.1f}")
            logger.info(f"   Scale factor: {self.scale_factor}x")
            logger.info(f"   Grid layout: {pages_horizontal} x {pages_vertical}")
            logger.info(f"   Total pages: {total_pages} (vs ~{total_pages//4} standard)")
            logger.info(f"   Detail level: MAXIMUM PRECISION")
            
            regions = []
            
            # Create grid-based regions for maximum detail
            for row in range(pages_vertical):
                for col in range(pages_horizontal):
                    if len(regions) >= self.max_pages:
                        break
                    
                    # Calculate region boundaries with overlap for continuity
                    overlap_x = effective_page_width * 0.05
                    overlap_y = effective_page_height * 0.05
                    
                    x_start = min_x + col * effective_page_width - (overlap_x if col > 0 else 0)
                    x_end = min_x + (col + 1) * effective_page_width + (overlap_x if col < pages_horizontal - 1 else 0)
                    x_end = min(x_end, max_x)
                    
                    y_start = min_y + row * effective_page_height - (overlap_y if row > 0 else 0)
                    y_end = min_y + (row + 1) * effective_page_height + (overlap_y if row < pages_vertical - 1 else 0)
                    y_end = min(y_end, max_y)
                    
                    if x_start < max_x and y_start < max_y:
                        regions.append((x_start, y_start, x_end, y_end))
                
                if len(regions) >= self.max_pages:
                    break
            
        else:
            # STANDARD SCALE CALCULATION (original method)
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
    
    def convert_dxf_to_pdf(self, dxf_path, pdf_path=None, max_pages=None):
        if max_pages is None:
            max_pages = self.max_pages
            
        if pdf_path is None:
            scale_suffix = self.scale_config['suffix']
            pdf_path = self.output_folder / f"{Path(dxf_path).stem}{scale_suffix}_A4_landscape.pdf"
        
        logger.info(f"🏗️  Converting {dxf_path} to {pdf_path}")
        logger.info(f"🎯 Scale Mode: {self.scale_config['name']} ({self.scale_factor}x)")
        if self.detail_enhancement:
            logger.info(f"🔍 Detail Enhancement: {self.scale_config['description']}")
        
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
            
            logger.info(f"📐 Drawing bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
            logger.info(f"📄 Creating {len(regions)} page(s) with {self.scale_factor}x enlargement")
            
            # ENHANCED DPI based on scale mode
            enhanced_dpi = int(self.DPI * self.scale_config['dpi_multiplier'])
            
            fig_width_inch = self.A4_WIDTH_MM / 25.4
            fig_height_inch = self.A4_HEIGHT_MM / 25.4
            
            with PdfPages(pdf_path) as pdf:
                for idx, (rx_min, ry_min, rx_max, ry_max) in enumerate(regions[:max_pages]):
                    progress = f"{idx + 1}/{len(regions)}"
                    
                    # OPTIMIZED progress reporting for large page counts
                    if self.detail_enhancement and len(regions) > 10:
                        # Report every 5th page for large conversions to reduce log spam
                        if idx % 5 == 0 or idx == len(regions) - 1:
                            logger.info(f"🖨️  Rendering pages {idx + 1}-{min(idx + 5, len(regions))}/{len(regions)} - Progress: {((idx + 1) / len(regions) * 100):.0f}%")
                    else:
                        logger.info(f"🖨️  Rendering page {progress} - Region: ({rx_min:.1f}, {ry_min:.1f}) to ({rx_max:.1f}, {ry_max:.1f})")
                    
                    fig = plt.figure(figsize=(fig_width_inch, fig_height_inch), dpi=enhanced_dpi)
                    ax = fig.add_subplot(111)
                    ax.set_aspect('equal')
                    
                    ctx = RenderContext(doc)
                    out = MatplotlibBackend(ax)
                    
                    Frontend(ctx, out).draw_layout(msp, finalize=True)
                    
                    region_width = rx_max - rx_min
                    region_height = ry_max - ry_min
                    
                    if region_width > 0 and region_height > 0:
                        # REDUCED margins for enlarged scale to show maximum detail
                        margin_factor = 0.02 if self.detail_enhancement else 0.05
                        margin_x = region_width * margin_factor
                        margin_y = region_height * margin_factor
                        
                        ax.set_xlim(rx_min - margin_x, rx_max + margin_x)
                        ax.set_ylim(ry_min - margin_y, ry_max + margin_y)
                    
                    ax.axis('off')
                    
                    # ENHANCED quality settings for enlarged scale
                    pdf.savefig(fig, dpi=enhanced_dpi, bbox_inches='tight', 
                              pad_inches=0.05 if self.detail_enhancement else 0.1,
                              facecolor='white', edgecolor='none')
                    plt.close(fig)
                    
                    # MEMORY cleanup for large conversions
                    if self.detail_enhancement and idx % 10 == 0:
                        import gc
                        gc.collect()  # Force garbage collection every 10 pages
                
                d = pdf.infodict()
                scale_info = f" - {self.scale_config['name']}" if self.detail_enhancement else ""
                d['Title'] = f'{Path(dxf_path).stem}{scale_info} - A4 Landscape'
                d['Author'] = 'Multi-Scale DXF to PDF Converter'
                d['Subject'] = f'Architectural/Structural Drawing - {self.scale_config["name"]}'
                d['Keywords'] = f'DXF, PDF, A4, Landscape, Footing, Structural, Scale, {self.scale_mode}, {self.scale_factor}x'
                d['CreationDate'] = datetime.now()
            
            success_msg = f"✅ Successfully created {self.scale_config['name']} PDF with {len(regions)} page(s): {pdf_path}"
            if self.detail_enhancement:
                estimated_standard = max(1, len(regions) // int(self.scale_factor))
                success_msg += f"\n   🎯 Scale: {self.scale_factor}x ({self.scale_config['description']})"
                success_msg += f"\n   📄 Pages: {len(regions)} (vs ~{estimated_standard} standard scale)"
            
            logger.info(success_msg)
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
        
        # ALPHABETICAL SORTING - case insensitive
        dxf_files.sort(key=lambda f: f.name.lower())
        
        logger.info(f"Found {len(dxf_files)} DXF files to convert (ALPHABETICAL ORDER):")
        for i, dxf_file in enumerate(dxf_files, 1):
            logger.info(f"  {i:2d}. {dxf_file.name}")
        
        results = []
        for i, dxf_file in enumerate(dxf_files, 1):
            logger.info(f"\n🔄 Processing DXF {i}/{len(dxf_files)}: {dxf_file.name}")
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

"""CLI module for DXF to PDF printer."""
import argparse
import logging
import sys
from pathlib import Path

from .models import ConversionResult, DrawingInfo
from .scanner import scan_dxf_files
from .parser import DXFParser, DXFParseError
from .geometry import GeometryProcessor
from .scale import ScaleCalculator
from .renderer import PDFRenderer
from .multipage_renderer import MultiPageRenderer
from .smart_renderer import SmartRenderer
from .splitter import DXFSplitter
from .split_renderer import SplitRenderer
from .reporter import report_results


def setup_logging(verbose=False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    
    Returns:
        Namespace with input_path, output_dir, output_file
    """
    parser = argparse.ArgumentParser(
        description='Convert DXF files to A4 landscape PDF'
    )
    
    parser.add_argument(
        'input',
        type=Path,
        help='Input DXF file or directory containing DXF files'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        type=Path,
        help='Output directory for PDF files (default: same as input)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output PDF filename (only for single file conversion)'
    )
    
    parser.add_argument(
        '--pages', '-p',
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help='Number of pages to split each drawing into (1-5, default: 1)'
    )
    
    parser.add_argument(
        '--split',
        action='store_true',
        help='Smart split: detect segments and legend, print each on separate A4 page with maximum scale'
    )
    
    args = parser.parse_args()
    
    # Validate input path
    if not args.input.exists():
        parser.error(f"Input path does not exist: {args.input}")
    
    # Set default output directory
    if args.output_dir is None:
        if args.input.is_file():
            args.output_dir = args.input.parent
        else:
            args.output_dir = args.input
    
    # Create output directory if it doesn't exist
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    return args


def convert_dxf_file(dxf_path: Path, output_path: Path, num_pages: int = 1, use_split: bool = False) -> bool:
    """
    Convert a single DXF file to PDF.
    
    Args:
        dxf_path: Path to DXF file
        output_path: Path for output PDF
        num_pages: Number of pages to split drawing into (1-5)
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Parse DXF file
        parser = DXFParser()
        drawing = parser.parse_file(dxf_path)
        
        # Extract geometry
        geo_processor = GeometryProcessor()
        entities = geo_processor.extract_entities(drawing)
        
        if not entities:
            logger.warning(f"No entities found in {dxf_path.name}")
            return False
        
        bbox = geo_processor.calculate_bounding_box(entities)
        
        # Choose renderer based on options
        if use_split:
            # Use smart splitter - detects segments and legend automatically
            splitter = DXFSplitter(drawing, entities)
            islands = splitter.detect_islands()
            
            if not islands:
                logger.warning(f"No islands detected in {dxf_path.name}")
                return False
            
            renderer = SplitRenderer()
            success = renderer.render_islands_to_pdf(islands, entities, output_path, dxf_path.stem)
        elif num_pages > 1:
            # Use smart renderer with intelligent segmentation
            renderer = SmartRenderer()
            success = renderer.render_to_pdf(entities, output_path, bbox, dxf_path.stem, num_pages)
        else:
            # Use single-page renderer
            scale_calc = ScaleCalculator()
            scale = scale_calc.calculate_scale(bbox)
            offset = scale_calc.calculate_offset(bbox, scale)
            
            renderer = PDFRenderer()
            success = renderer.render_to_pdf(entities, output_path, scale, offset, bbox)
        
        return success
        
    except DXFParseError as e:
        logger.error(f"Parse error for {dxf_path.name}: {e}")
        return False
    except ValueError as e:
        logger.error(f"Geometry error for {dxf_path.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error for {dxf_path.name}: {e}")
        return False


def main():
    """Entry point for the CLI application."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        logger.info(f"Starting DXF to PDF conversion")
        logger.info(f"Input: {args.input}")
        logger.info(f"Output directory: {args.output_dir}")
        logger.info(f"Pages per drawing: {args.pages}")
        
        # Scan for DXF files
        dxf_files = scan_dxf_files(args.input)
        
        if not dxf_files:
            logger.error("No DXF files found")
            print(f"\n✗ No DXF files found in {args.input}")
            sys.exit(1)
        
        print(f"\nFound {len(dxf_files)} DXF file(s):")
        for dxf_file in dxf_files:
            print(f"  - {dxf_file.name}")
        print()
        
        # Convert each DXF file
        output_files = []
        failed_conversions = []
        
        for dxf_file in dxf_files:
            # Determine output filename
            if args.output and len(dxf_files) == 1:
                output_path = args.output
            else:
                output_filename = dxf_file.stem + '.pdf'
                output_path = args.output_dir / output_filename
            
            logger.info(f"Converting {dxf_file.name}...")
            mode = "SPLIT" if args.split else f"{args.pages} page(s)"
            print(f"Converting {dxf_file.name} ({mode})...", end=' ')
            
            success = convert_dxf_file(dxf_file, output_path, args.pages, args.split)
            
            if success:
                output_files.append(output_path)
                print("✓")
            else:
                failed_conversions.append((dxf_file, "Conversion failed"))
                print("✗")
        
        # Report results
        result = ConversionResult(
            total_files=len(dxf_files),
            successful=len(output_files),
            failed=failed_conversions,
            output_files=output_files
        )
        report_results(result)
        
        if output_files:
            logger.info("Conversion completed successfully")
            sys.exit(0)
        else:
            logger.error("All conversions failed")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Conversion cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

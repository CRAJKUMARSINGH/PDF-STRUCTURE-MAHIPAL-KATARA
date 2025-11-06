"""CLI module for HTML to PDF converter."""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

from .models import ConversionResult, ConverterConfig
from .scanner import scan_html_files
from .converter import HTMLConverter
from .merger import merge_pdfs
from .reporter import report_results


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    
    Returns:
        Namespace with source_dir and output_file
    """
    parser = argparse.ArgumentParser(
        description='Convert multiple HTML files to a single combined PDF'
    )
    
    parser.add_argument(
        '--source-dir', '-s',
        type=Path,
        default=Path.cwd(),
        help='Source directory containing HTML files (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output PDF file path (default: combined_YYYYMMDD_HHMMSS.pdf in source directory)'
    )
    
    parser.add_argument(
        '--page-size',
        type=str,
        default='A4',
        choices=['A4', 'A3', 'A5', 'Letter', 'Legal'],
        help='PDF page size (default: A4)'
    )
    
    parser.add_argument(
        '--orientation',
        type=str,
        default='Portrait',
        choices=['Portrait', 'Landscape'],
        help='Page orientation (default: Portrait)'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    if not args.source_dir.exists():
        parser.error(f"Source directory does not exist: {args.source_dir}")
    
    if not args.source_dir.is_dir():
        parser.error(f"Source path is not a directory: {args.source_dir}")
    
    # Generate default output filename if not specified
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = args.source_dir / f'combined_{timestamp}.pdf'
    
    return args


def main():
    """Entry point for the CLI application."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        logger.info(f"Starting HTML to PDF conversion")
        logger.info(f"Source directory: {args.source_dir}")
        logger.info(f"Output file: {args.output}")
        
        # Scan for HTML files
        html_files = scan_html_files(args.source_dir)
        
        if not html_files:
            logger.error("No HTML files found in source directory")
            print(f"\n✗ No HTML files found in {args.source_dir}")
            sys.exit(1)
        
        # Display processing order
        print(f"\nFound {len(html_files)} HTML files:")
        processing_order = [f.name for f in html_files]
        for i, filename in enumerate(processing_order, 1):
            print(f"  {i}. {filename}")
        print()
        
        # Initialize converter with enhanced settings
        config = ConverterConfig(
            source_dir=args.source_dir,
            output_file=args.output
        )
        converter = HTMLConverter(config.temp_dir, args.page_size, args.orientation)
        
        # Convert HTML files to PDFs
        successful_pdfs, failed_conversions = converter.convert_batch(html_files)
        
        # Check if any conversions succeeded
        if not successful_pdfs:
            logger.error("No HTML files were successfully converted")
            result = ConversionResult(
                total_files=len(html_files),
                successful=0,
                failed=failed_conversions,
                output_path=None,
                processing_order=processing_order
            )
            report_results(result)
            converter.cleanup()
            sys.exit(1)
        
        # Merge PDFs
        merge_success = merge_pdfs(successful_pdfs, args.output)
        
        if not merge_success:
            logger.error("Failed to merge PDFs")
            result = ConversionResult(
                total_files=len(html_files),
                successful=len(successful_pdfs),
                failed=failed_conversions,
                output_path=None,
                processing_order=processing_order
            )
            report_results(result)
            converter.cleanup()
            sys.exit(1)
        
        # Clean up temporary files
        converter.cleanup()
        
        # Report results
        result = ConversionResult(
            total_files=len(html_files),
            successful=len(successful_pdfs),
            failed=failed_conversions,
            output_path=args.output,
            processing_order=processing_order
        )
        report_results(result)
        
        logger.info("Conversion completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Conversion cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
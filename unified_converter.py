#!/usr/bin/env python3
"""
Unified Converter - Process both HTML and DXF files in one click
Generates outputs in separate date-stamped subfolders
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import json

from dxf_converter import DXFToPDFConverter
from html2pdf.service import HTMLToPDFService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedConverter:
    """Unified converter for both HTML and DXF files with organized output structure."""
    
    def __init__(self, input_folder: str = "INPUT_DATA", base_output_folder: str = "OUTPUT_PDF"):
        """
        Initialize unified converter.
        
        Args:
            input_folder: Directory containing both HTML and DXF files
            base_output_folder: Base directory for organized outputs
        """
        self.input_folder = Path(input_folder)
        self.base_output_folder = Path(base_output_folder)
        
        # Create timestamp for this conversion session
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Create organized output structure
        self.html_output_folder = self.base_output_folder / "HTML_REPORTS" / f"session_{self.timestamp}"
        self.dxf_output_folder = self.base_output_folder / "DXF_DRAWINGS" / f"session_{self.timestamp}"
        self.logs_folder = self.base_output_folder / "CONVERSION_LOGS" / f"session_{self.timestamp}"
        
        # Ensure all directories exist
        self.input_folder.mkdir(exist_ok=True)
        self.html_output_folder.mkdir(parents=True, exist_ok=True)
        self.dxf_output_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize converters
        self.dxf_converter = DXFToPDFConverter(
            input_folder=str(self.input_folder),
            output_folder=str(self.dxf_output_folder),
            log_folder=str(self.logs_folder)
        )
        
        self.html_converter = HTMLToPDFService(
            input_folder=str(self.input_folder),
            output_folder=str(self.html_output_folder)
        )
        
        logger.info(f"Unified Converter initialized for session: {self.timestamp}")
        logger.info(f"HTML outputs: {self.html_output_folder}")
        logger.info(f"DXF outputs: {self.dxf_output_folder}")
        logger.info(f"Logs: {self.logs_folder}")
    
    def scan_input_files(self) -> Dict[str, List[str]]:
        """
        Scan input folder for HTML and DXF files ALPHABETICALLY.
        
        Returns:
            Dictionary with 'html' and 'dxf' file lists sorted alphabetically
        """
        html_files = []
        dxf_files = []
        
        # Scan for HTML files
        for pattern in ['*.html', '*.htm', '*.HTML', '*.HTM']:
            html_files.extend([f.name for f in self.input_folder.glob(pattern)])
        
        # Scan for DXF files
        for pattern in ['*.dxf', '*.DXF']:
            dxf_files.extend([f.name for f in self.input_folder.glob(pattern)])
        
        # ALPHABETICAL SORTING - case insensitive
        html_files = sorted(list(set(html_files)), key=str.lower)
        dxf_files = sorted(list(set(dxf_files)), key=str.lower)
        
        logger.info(f"📁 Files found (ALPHABETICAL ORDER):")
        logger.info(f"   📄 HTML files: {len(html_files)}")
        for i, file in enumerate(html_files, 1):
            logger.info(f"      {i:2d}. {file}")
        
        logger.info(f"   🏗️  DXF files: {len(dxf_files)}")
        for i, file in enumerate(dxf_files, 1):
            logger.info(f"      {i:2d}. {file}")
        
        return {
            'html': html_files,
            'dxf': dxf_files
        }
    
    def convert_all_files(self) -> Dict[str, Any]:
        """
        Convert all HTML and DXF files in one operation.
        
        Returns:
            Comprehensive conversion results
        """
        logger.info("="*70)
        logger.info("🚀 STARTING UNIFIED CONVERSION SESSION")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # Scan input files
        input_files = self.scan_input_files()
        
        logger.info(f"📁 Found {len(input_files['html'])} HTML files")
        logger.info(f"📁 Found {len(input_files['dxf'])} DXF files")
        
        if not input_files['html'] and not input_files['dxf']:
            return {
                'success': False,
                'error': 'No HTML or DXF files found in input directory',
                'timestamp': self.timestamp,
                'html_results': {},
                'dxf_results': {},
                'summary': {}
            }
        
        # Initialize results
        results = {
            'success': True,
            'timestamp': self.timestamp,
            'session_id': f"session_{self.timestamp}",
            'input_files': input_files,
            'html_results': {},
            'dxf_results': {},
            'summary': {},
            'output_folders': {
                'html': str(self.html_output_folder),
                'dxf': str(self.dxf_output_folder),
                'logs': str(self.logs_folder)
            }
        }
        
        # Convert HTML files
        if input_files['html']:
            logger.info("\n📄 CONVERTING HTML FILES...")
            logger.info("-" * 50)
            
            try:
                html_result = self.html_converter.convert_html_to_pdf(
                    output_filename=f"combined_html_reports_{self.timestamp}.pdf"
                )
                results['html_results'] = html_result
                
                if html_result['success']:
                    logger.info(f"✅ HTML conversion successful: {html_result['output_file']}")
                else:
                    logger.error(f"❌ HTML conversion failed: {html_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ HTML conversion error: {e}")
                results['html_results'] = {
                    'success': False,
                    'error': str(e),
                    'total': len(input_files['html']),
                    'successful': 0,
                    'failed': len(input_files['html'])
                }
        
        # Convert DXF files INDIVIDUALLY + COMBINED
        if input_files['dxf']:
            logger.info("\n🏗️  CONVERTING DXF FILES (ALPHABETICAL ORDER)...")
            logger.info("-" * 50)
            
            try:
                # STEP 1: Convert each DXF file individually (alphabetical order)
                individual_results = []
                individual_pdfs = []
                
                for i, dxf_filename in enumerate(input_files['dxf'], 1):
                    logger.info(f"🔄 Converting DXF {i}/{len(input_files['dxf'])}: {dxf_filename}")
                    
                    dxf_path = self.input_folder / dxf_filename
                    if dxf_path.exists():
                        success, output_path, pages = self.dxf_converter.convert_dxf_to_pdf(dxf_path)
                        
                        result = {
                            'input': dxf_filename,
                            'output': Path(output_path).name if success else output_path,
                            'success': success,
                            'pages': pages,
                            'timestamp': datetime.now().isoformat()
                        }
                        individual_results.append(result)
                        
                        if success:
                            individual_pdfs.append(Path(output_path))
                            logger.info(f"   ✅ {dxf_filename} → {pages} pages")
                        else:
                            logger.error(f"   ❌ {dxf_filename} → {output_path}")
                
                # STEP 2: Combine all successful DXF PDFs into one master PDF
                combined_pdf_path = None
                if individual_pdfs:
                    logger.info(f"\n📚 COMBINING {len(individual_pdfs)} DXF PDFs...")
                    
                    from html2pdf.merger import merge_pdfs
                    combined_pdf_path = self.dxf_output_folder / f"COMBINED_ALL_DXF_{self.timestamp}.pdf"
                    
                    # Sort PDFs alphabetically by filename for consistent order
                    individual_pdfs.sort(key=lambda p: p.name.lower())
                    
                    logger.info(f"📄 Combining PDFs in alphabetical order:")
                    for i, pdf_path in enumerate(individual_pdfs, 1):
                        logger.info(f"   {i:2d}. {pdf_path.name}")
                    
                    combine_success = merge_pdfs(individual_pdfs, combined_pdf_path)
                    
                    if combine_success:
                        logger.info(f"✅ Combined PDF created: {combined_pdf_path.name}")
                    else:
                        logger.error(f"❌ Failed to create combined PDF")
                        combined_pdf_path = None
                
                # Process DXF results
                successful_dxf = sum(1 for r in individual_results if r['success'])
                failed_dxf = len(individual_results) - successful_dxf
                total_pages = sum(r.get('pages', 0) for r in individual_results if r['success'])
                
                results['dxf_results'] = {
                    'success': successful_dxf > 0,
                    'total': len(individual_results),
                    'successful': successful_dxf,
                    'failed': failed_dxf,
                    'total_pages': total_pages,
                    'details': individual_results,
                    'individual_pdfs': len(individual_pdfs),
                    'combined_pdf': str(combined_pdf_path) if combined_pdf_path else None,
                    'combined_success': combined_pdf_path is not None
                }
                
                logger.info(f"✅ DXF conversion complete:")
                logger.info(f"   📄 Individual PDFs: {successful_dxf}/{len(individual_results)} successful")
                logger.info(f"   📚 Combined PDF: {'✅ Created' if combined_pdf_path else '❌ Failed'}")
                logger.info(f"   📄 Total pages: {total_pages}")
                
            except Exception as e:
                logger.error(f"❌ DXF conversion error: {e}")
                results['dxf_results'] = {
                    'success': False,
                    'error': str(e),
                    'total': len(input_files['dxf']),
                    'successful': 0,
                    'failed': len(input_files['dxf']),
                    'total_pages': 0,
                    'individual_pdfs': 0,
                    'combined_pdf': None,
                    'combined_success': False
                }
        
        # Calculate summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        html_success = results['html_results'].get('success', False)
        dxf_success = results['dxf_results'].get('success', False)
        
        results['summary'] = {
            'overall_success': html_success or dxf_success,
            'duration_seconds': duration,
            'total_input_files': len(input_files['html']) + len(input_files['dxf']),
            'html_files_processed': len(input_files['html']),
            'dxf_files_processed': len(input_files['dxf']),
            'html_successful': results['html_results'].get('successful', 0),
            'dxf_successful': results['dxf_results'].get('successful', 0),
            'dxf_individual_pdfs': results['dxf_results'].get('individual_pdfs', 0),
            'dxf_combined_pdf': results['dxf_results'].get('combined_success', False),
            'total_pdf_files_created': (
                (1 if html_success else 0) + 
                results['dxf_results'].get('individual_pdfs', 0) +
                (1 if results['dxf_results'].get('combined_success', False) else 0)
            ),
            'total_pages_generated': results['dxf_results'].get('total_pages', 0)
        }
        
        # Save conversion log
        self.save_conversion_log(results)
        
        # Print summary
        self.print_conversion_summary(results)
        
        return results
    
    def save_conversion_log(self, results: Dict[str, Any]) -> None:
        """Save detailed conversion log to JSON file."""
        log_file = self.logs_folder / f"conversion_log_{self.timestamp}.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"📝 Conversion log saved: {log_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save conversion log: {e}")
    
    def print_conversion_summary(self, results: Dict[str, Any]) -> None:
        """Print formatted conversion summary."""
        logger.info("\n" + "="*70)
        logger.info("📊 UNIFIED CONVERSION SUMMARY")
        logger.info("="*70)
        
        summary = results['summary']
        
        logger.info(f"🕒 Session: {results['timestamp']}")
        logger.info(f"⏱️  Duration: {summary['duration_seconds']:.1f} seconds")
        logger.info(f"📁 Total input files: {summary['total_input_files']}")
        
        logger.info(f"\n📄 HTML CONVERSION:")
        if results['html_results']:
            html_res = results['html_results']
            logger.info(f"   Files processed: {html_res.get('total', 0)}")
            logger.info(f"   Successful: {html_res.get('successful', 0)}")
            logger.info(f"   Failed: {html_res.get('failed', 0)}")
            if html_res.get('success'):
                logger.info(f"   Output: {html_res.get('output_file', 'N/A')}")
        else:
            logger.info("   No HTML files to process")
        
        logger.info(f"\n🏗️  DXF CONVERSION (ALPHABETICAL ORDER):")
        if results['dxf_results']:
            dxf_res = results['dxf_results']
            logger.info(f"   Files processed: {dxf_res.get('total', 0)}")
            logger.info(f"   Individual PDFs: {dxf_res.get('successful', 0)} successful")
            logger.info(f"   Combined PDF: {'✅ Created' if dxf_res.get('combined_success', False) else '❌ Failed'}")
            logger.info(f"   Failed conversions: {dxf_res.get('failed', 0)}")
            logger.info(f"   Total pages: {dxf_res.get('total_pages', 0)}")
            if dxf_res.get('combined_pdf'):
                logger.info(f"   Combined file: {Path(dxf_res['combined_pdf']).name}")
        else:
            logger.info("   No DXF files to process")
        
        logger.info(f"\n📂 OUTPUT LOCATIONS:")
        logger.info(f"   HTML Reports: {results['output_folders']['html']}")
        logger.info(f"   DXF Drawings: {results['output_folders']['dxf']}")
        logger.info(f"   Logs: {results['output_folders']['logs']}")
        
        status = "✅ SUCCESS" if summary['overall_success'] else "❌ FAILED"
        logger.info(f"\n🎯 OVERALL STATUS: {status}")
        logger.info("="*70)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        return {
            'timestamp': self.timestamp,
            'session_id': f"session_{self.timestamp}",
            'input_folder': str(self.input_folder),
            'output_folders': {
                'html': str(self.html_output_folder),
                'dxf': str(self.dxf_output_folder),
                'logs': str(self.logs_folder)
            }
        }


def main():
    """Main function for command-line usage."""
    print("🚀 UNIFIED HTML & DXF TO PDF CONVERTER")
    print("="*70)
    
    converter = UnifiedConverter()
    results = converter.convert_all_files()
    
    return 0 if results['summary']['overall_success'] else 1


if __name__ == "__main__":
    exit(main())
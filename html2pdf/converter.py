"""HTML to PDF converter module using reportlab."""
from pathlib import Path
from typing import List, Tuple, Optional
import logging
from html.parser import HTMLParser
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import re

logger = logging.getLogger(__name__)


class HTMLToReportLabParser(HTMLParser):
    """Parse HTML and convert to ReportLab flowables."""
    
    def __init__(self):
        super().__init__()
        self.flowables = []
        self.styles = getSampleStyleSheet()
        self.current_text = []
        self.current_style = self.styles['Normal']
        self.in_table = False
        self.table_data = []
        self.current_row = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_style = self.styles['Heading1']
        elif tag == 'h2':
            self.current_style = self.styles['Heading2']
        elif tag == 'h3':
            self.current_style = self.styles['Heading3']
        elif tag == 'p':
            self.current_style = self.styles['Normal']
        elif tag == 'table':
            self.in_table = True
            self.table_data = []
        elif tag == 'tr':
            self.current_row = []
        elif tag == 'br':
            self.current_text.append('<br/>')
    
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'p']:
            if self.current_text:
                text = ''.join(self.current_text).strip()
                if text:
                    try:
                        para = Paragraph(text, self.current_style)
                        self.flowables.append(para)
                        self.flowables.append(Spacer(1, 0.2*inch))
                    except:
                        pass
                self.current_text = []
            self.current_style = self.styles['Normal']
        elif tag == 'table':
            if self.table_data:
                try:
                    table = Table(self.table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    self.flowables.append(table)
                    self.flowables.append(Spacer(1, 0.3*inch))
                except:
                    pass
            self.in_table = False
            self.table_data = []
        elif tag == 'tr':
            if self.current_row:
                self.table_data.append(self.current_row)
            self.current_row = []
    
    def handle_data(self, data):
        text = data.strip()
        if text:
            if self.in_table:
                self.current_row.append(text)
            else:
                # Clean up text for reportlab
                text = re.sub(r'\s+', ' ', text)
                self.current_text.append(text)


class HTMLConverter:
    """Converts HTML files to PDF format using reportlab."""
    
    def __init__(self, temp_dir: Path):
        """
        Initialize converter with temporary directory for intermediate PDFs.
        
        Args:
            temp_dir: Path to temporary directory for storing intermediate PDFs
        """
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Using ReportLab for HTML to PDF conversion")
    
    def convert_file(self, html_path: Path) -> Optional[Path]:
        """
        Convert single HTML file to PDF.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Path to generated PDF, or None if conversion failed
        """
        try:
            # Generate output PDF path in temp directory
            pdf_filename = html_path.stem + '.pdf'
            pdf_path = self.temp_dir / pdf_filename
            
            logger.info(f"Converting {html_path.name} to PDF using ReportLab...")
            
            # Read HTML content
            html_content = html_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse HTML
            parser = HTMLToReportLabParser()
            parser.feed(html_content)
            
            if not parser.flowables:
                # If no flowables, create a simple text document
                logger.warning(f"No structured content found in {html_path.name}, creating text document")
                # Remove HTML tags for plain text
                plain_text = re.sub(r'<[^>]+>', ' ', html_content)
                plain_text = re.sub(r'\s+', ' ', plain_text).strip()
                
                if plain_text:
                    styles = getSampleStyleSheet()
                    para = Paragraph(plain_text[:5000], styles['Normal'])  # Limit length
                    parser.flowables = [para]
            
            if not parser.flowables:
                logger.error(f"No content to convert in {html_path.name}")
                return None
            
            # Create PDF
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            doc.build(parser.flowables)
            
            if pdf_path.exists():
                logger.info(f"Successfully converted {html_path.name}")
                return pdf_path
            else:
                logger.warning(f"PDF not created for {html_path.name}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to convert {html_path.name}: {e}", exc_info=True)
            return None
    
    def convert_batch(self, html_files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Convert multiple HTML files to PDFs.
        
        Args:
            html_files: List of HTML file paths
            
        Returns:
            Tuple of (successful_pdfs, failed_conversions)
            failed_conversions is list of (file_path, error_message) tuples
        """
        successful_pdfs = []
        failed_conversions = []
        
        for html_file in html_files:
            try:
                pdf_path = self.convert_file(html_file)
                if pdf_path and pdf_path.exists():
                    successful_pdfs.append(pdf_path)
                else:
                    failed_conversions.append((html_file, "Conversion failed - no output generated"))
            except Exception as e:
                error_msg = str(e)
                failed_conversions.append((html_file, error_msg))
                logger.error(f"Error converting {html_file}: {error_msg}")
        
        return successful_pdfs, failed_conversions
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.glob('*.pdf'):
                    file.unlink()
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")

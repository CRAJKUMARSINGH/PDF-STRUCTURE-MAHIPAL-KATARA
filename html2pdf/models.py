"""Data models for HTML to PDF converter."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import tempfile


@dataclass
class ConversionResult:
    """Results of HTML to PDF conversion operation."""
    total_files: int
    successful: int
    failed: List[Tuple[Path, str]]
    output_path: Optional[Path]
    processing_order: List[str]


@dataclass
class ConverterConfig:
    """Configuration for HTML to PDF converter."""
    source_dir: Path
    output_file: Path
    temp_dir: Path = field(default_factory=lambda: Path(tempfile.gettempdir()) / "html2pdf_temp")
    wkhtmltopdf_options: Dict[str, Any] = field(default_factory=lambda: {
        'enable-local-file-access': None,
        'encoding': 'UTF-8',
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'disable-smart-shrinking': '',
        'print-media-type': '',
        'no-background': False,
        'enable-javascript': '',
        'javascript-delay': 1000,
        'load-error-handling': 'ignore',
        'load-media-error-handling': 'ignore'
    })
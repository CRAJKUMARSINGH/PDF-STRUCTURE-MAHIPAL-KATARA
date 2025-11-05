"""Data models for DXF to PDF printer."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Any


@dataclass
class ConversionResult:
    """Results of DXF to PDF conversion operation."""
    total_files: int
    successful: int
    failed: List[Tuple[Path, str]]
    output_files: List[Path]


@dataclass
class DrawingInfo:
    """Information about a DXF drawing."""
    entities: List[Any]
    bounding_box: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    scale: float
    offset: Tuple[float, float]  # x, y offset in mm

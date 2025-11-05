"""Result reporter module."""
from .models import ConversionResult


def report_results(result: ConversionResult) -> None:
    """
    Display formatted conversion results to console.
    
    Args:
        result: ConversionResult object with conversion statistics
    """
    print("\n" + "="*60)
    print("DXF to PDF Conversion Results")
    print("="*60)
    
    print(f"\nTotal DXF files found: {result.total_files}")
    print(f"Successfully converted: {result.successful}")
    print(f"Failed conversions: {len(result.failed)}")
    
    if result.output_files:
        print(f"\nGenerated PDF files:")
        for output_file in result.output_files:
            print(f"  ✓ {output_file}")
    
    if result.failed:
        print(f"\nFailed conversions:")
        for file_path, error_msg in result.failed:
            print(f"  ✗ {file_path.name}: {error_msg}")
    
    print("="*60 + "\n")

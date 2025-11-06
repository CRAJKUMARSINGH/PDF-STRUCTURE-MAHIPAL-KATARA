"""Result reporter module."""
from .models import ConversionResult


def report_results(result: ConversionResult) -> None:
    """
    Display formatted conversion results to console.
    
    Args:
        result: ConversionResult object with conversion statistics
    """
    print("\n" + "="*60)
    print("HTML to PDF Conversion Results")
    print("="*60)
    
    print(f"\nTotal HTML files found: {result.total_files}")
    print(f"Successfully converted: {result.successful}")
    print(f"Failed conversions: {len(result.failed)}")
    
    if result.processing_order:
        print(f"\nProcessing order:")
        for i, filename in enumerate(result.processing_order, 1):
            print(f"  {i}. {filename}")
    
    if result.failed:
        print(f"\nFailed conversions:")
        for file_path, error_msg in result.failed:
            print(f"  ✗ {file_path.name}: {error_msg}")
    
    if result.output_path:
        print(f"\n✓ Combined PDF saved to: {result.output_path}")
    else:
        print(f"\n✗ No output PDF generated")
    
    print("="*60 + "\n")
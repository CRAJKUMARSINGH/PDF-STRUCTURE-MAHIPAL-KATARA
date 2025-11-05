#!/usr/bin/env python3
"""Simple DXF to PDF converter using the dxf2pdf package."""

import sys
from pathlib import Path
from dxf2pdf.cli import main as cli_main

def main():
    """Run DXF to PDF conversion."""
    if len(sys.argv) < 2:
        print("Usage: python convert_dxf.py <dxf_file>")
        print("Example: python convert_dxf.py LIBRBeamSections011.DXF")
        sys.exit(1)
    
    # Override sys.argv to pass to CLI
    dxf_file = sys.argv[1]
    if not Path(dxf_file).exists():
        print(f"Error: DXF file '{dxf_file}' not found")
        sys.exit(1)
    
    # Set up arguments for CLI
    sys.argv = ['convert_dxf.py', dxf_file]
    
    # Run the CLI
    cli_main()

if __name__ == "__main__":
    main()
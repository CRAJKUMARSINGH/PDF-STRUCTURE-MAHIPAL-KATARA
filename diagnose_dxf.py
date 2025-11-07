#!/usr/bin/env python3
"""
DXF File Diagnostic Tool
Helps identify issues with DXF files before conversion.
"""

import sys
from pathlib import Path
import ezdxf
from ezdxf import recover


def diagnose_dxf(dxf_path: Path):
    """
    Diagnose a DXF file and report any issues.
    
    Args:
        dxf_path: Path to DXF file
    """
    print(f"\n{'='*60}")
    print(f"DXF File Diagnostic Report")
    print(f"{'='*60}")
    print(f"File: {dxf_path.name}")
    print(f"Path: {dxf_path}")
    
    # Check file exists
    if not dxf_path.exists():
        print(f"❌ ERROR: File does not exist")
        return False
    
    # Check file size
    file_size = dxf_path.stat().st_size
    print(f"Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    
    if file_size == 0:
        print(f"❌ ERROR: File is empty")
        return False
    
    print(f"\n{'='*60}")
    print(f"Attempting to parse DXF file...")
    print(f"{'='*60}")
    
    # Try normal parsing first
    try:
        doc = ezdxf.readfile(str(dxf_path))
        print(f"✅ Successfully parsed with ezdxf.readfile()")
        
        # Get DXF version
        print(f"DXF Version: {doc.dxfversion}")
        
        # Check modelspace
        msp = doc.modelspace()
        if msp is None:
            print(f"❌ ERROR: No modelspace found")
            return False
        
        print(f"✅ Modelspace found")
        
        # Count entities
        entities = list(msp)
        entity_count = len(entities)
        print(f"Total entities: {entity_count}")
        
        if entity_count == 0:
            print(f"⚠️  WARNING: No entities found in modelspace")
            return False
        
        # Count by type
        entity_types = {}
        for entity in entities:
            entity_type = entity.dxftype()
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print(f"\nEntity breakdown:")
        for entity_type, count in sorted(entity_types.items()):
            print(f"  {entity_type}: {count}")
        
        # Check for drawable entities
        drawable_types = {'LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE', 
                         'SPLINE', 'ELLIPSE', 'TEXT', 'MTEXT', 'INSERT', 'POINT'}
        
        drawable_count = sum(count for etype, count in entity_types.items() 
                           if etype in drawable_types)
        
        print(f"\nDrawable entities: {drawable_count}")
        
        if drawable_count == 0:
            print(f"⚠️  WARNING: No drawable entities found")
            print(f"   The file may contain only metadata or unsupported entity types")
        
        # Try to get bounds
        print(f"\n{'='*60}")
        print(f"Calculating drawing bounds...")
        print(f"{'='*60}")
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in entities:
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
            except Exception as e:
                pass
        
        if min_x != float('inf'):
            width = max_x - min_x
            height = max_y - min_y
            print(f"Bounds: ({min_x:.2f}, {min_y:.2f}) to ({max_x:.2f}, {max_y:.2f})")
            print(f"Size: {width:.2f} x {height:.2f}")
            
            if width <= 0 or height <= 0:
                print(f"⚠️  WARNING: Invalid drawing dimensions")
        else:
            print(f"⚠️  WARNING: Could not calculate bounds")
        
        print(f"\n{'='*60}")
        print(f"✅ DIAGNOSIS COMPLETE - File appears valid")
        print(f"{'='*60}")
        return True
        
    except ezdxf.DXFStructureError as e:
        print(f"❌ DXF Structure Error: {e}")
        print(f"\nAttempting recovery mode...")
        
        try:
            doc, auditor = recover.readfile(str(dxf_path))
            print(f"✅ File recovered with errors")
            
            if auditor.has_errors:
                print(f"\nRecovery errors found ({len(auditor.errors)}):")
                for i, error in enumerate(auditor.errors[:5], 1):
                    print(f"  {i}. {error}")
                if len(auditor.errors) > 5:
                    print(f"  ... and {len(auditor.errors) - 5} more")
            
            if auditor.has_fixes:
                print(f"\nRecovery fixes applied ({len(auditor.fixes)}):")
                for i, fix in enumerate(auditor.fixes[:5], 1):
                    print(f"  {i}. {fix}")
                if len(auditor.fixes) > 5:
                    print(f"  ... and {len(auditor.fixes) - 5} more")
            
            return True
            
        except Exception as recover_error:
            print(f"❌ Recovery failed: {recover_error}")
            return False
    
    except ezdxf.DXFVersionError as e:
        print(f"❌ DXF Version Error: {e}")
        print(f"   The DXF version may not be supported")
        return False
    
    except IOError as e:
        print(f"❌ I/O Error: {e}")
        print(f"   Cannot read the file")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__} - {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python diagnose_dxf.py <dxf_file>")
        print("\nExample:")
        print("  python diagnose_dxf.py INPUT_DATA/drawing.dxf")
        sys.exit(1)
    
    dxf_path = Path(sys.argv[1])
    success = diagnose_dxf(dxf_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

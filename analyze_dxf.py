"""Analyze DXF file structure to understand layers and segments."""
import ezdxf
from pathlib import Path
from collections import defaultdict

dxf_file = Path('LIBRBeamSections011.DXF')

print("\n" + "="*70)
print(f"Analyzing: {dxf_file.name}")
print("="*70)

try:
    doc = ezdxf.readfile(str(dxf_file))
    msp = doc.modelspace()
    
    # Analyze layers
    print("\nLAYERS:")
    print("-" * 70)
    layers = defaultdict(int)
    for entity in msp:
        layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'UNKNOWN'
        layers[layer] += 1
    
    for layer, count in sorted(layers.items()):
        print(f"  {layer}: {count} entities")
    
    # Analyze entity types
    print("\nENTITY TYPES:")
    print("-" * 70)
    entity_types = defaultdict(int)
    for entity in msp:
        entity_types[entity.dxftype()] += 1
    
    for etype, count in sorted(entity_types.items()):
        print(f"  {etype}: {count}")
    
    # Analyze spatial distribution
    print("\nSPATIAL ANALYSIS:")
    print("-" * 70)
    
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    entity_positions = []
    
    for entity in msp:
        try:
            if hasattr(entity, 'bounding_box'):
                bbox = entity.bounding_box
                if bbox.has_data:
                    min_x = min(min_x, bbox.extmin.x)
                    min_y = min(min_y, bbox.extmin.y)
                    max_x = max(max_x, bbox.extmax.x)
                    max_y = max(max_y, bbox.extmax.y)
                    
                    # Store center point
                    cx = (bbox.extmin.x + bbox.extmax.x) / 2
                    cy = (bbox.extmin.y + bbox.extmax.y) / 2
                    entity_positions.append((cx, cy, entity.dxftype(), entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'UNKNOWN'))
        except:
            pass
    
    print(f"  Overall bounding box:")
    print(f"    X: {min_x:.2f} to {max_x:.2f} (width: {max_x - min_x:.2f})")
    print(f"    Y: {min_y:.2f} to {max_y:.2f} (height: {max_y - min_y:.2f})")
    
    # Check for text entities (potential labels/legends)
    print("\nTEXT ENTITIES (potential labels/legends):")
    print("-" * 70)
    text_count = 0
    for entity in msp:
        if entity.dxftype() in ['TEXT', 'MTEXT']:
            text_count += 1
            try:
                text = entity.dxf.text if hasattr(entity.dxf, 'text') else entity.text
                pos = entity.dxf.insert if hasattr(entity.dxf, 'insert') else None
                layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else 'UNKNOWN'
                if text_count <= 20:  # Show first 20
                    print(f"  [{layer}] {text[:50]}")
            except:
                pass
    
    if text_count > 20:
        print(f"  ... and {text_count - 20} more text entities")
    
    print("\n" + "="*70)
    print("\nRECOMMENDATIONS:")
    print("-" * 70)
    
    if len(layers) > 1:
        print(f"✓ Drawing has {len(layers)} layers - can separate by layer")
    else:
        print("  Drawing has only 1 layer - will use spatial clustering")
    
    width = max_x - min_x
    height = max_y - min_y
    aspect = width / height if height > 0 else 1
    
    if aspect > 2:
        print(f"✓ Wide drawing (aspect {aspect:.1f}:1) - recommend horizontal split")
    elif aspect < 0.5:
        print(f"✓ Tall drawing (aspect {aspect:.1f}:1) - recommend vertical split")
    else:
        print(f"  Balanced drawing (aspect {aspect:.1f}:1) - recommend grid split")
    
    print("\n" + "="*70)
    
except Exception as e:
    print(f"Error analyzing DXF: {e}")
    import traceback
    traceback.print_exc()

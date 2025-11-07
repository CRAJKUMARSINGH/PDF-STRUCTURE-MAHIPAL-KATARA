#!/usr/bin/env python3
"""
Streamlit Web App for DXF to PDF Conversion
Deploy this to Streamlit Cloud for online access.
"""

import streamlit as st
import tempfile
import io
from pathlib import Path
import sys
import os
import zipfile
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dxf2pdf.cli import convert_dxf_file
    from dxf2pdf.parser import DXFParser
    from dxf2pdf.geometry import GeometryProcessor
    from dxf2pdf.renderer import PDFRenderer
    from html2pdf.converter import HTMLConverter
    from html2pdf.merger import merge_pdfs
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure all required modules are available.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="DXF to PDF Converter",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🔧 DXF to PDF Converter</h1>
    <p>Convert your AutoCAD DXF files to PDF format instantly</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Upload** your DXF file
    2. **Configure** conversion options
    3. **Download** the generated PDF
    
    **Supported formats:**
    - DXF (AutoCAD Drawing Exchange Format)
    
    **Output format:**
    - PDF (A4 Landscape)
    """)
    
    st.header("⚙️ Conversion Options")
    
    # Conversion options
    num_pages = st.selectbox(
        "Pages per drawing",
        options=[1, 2, 3, 4, 5],
        index=0,
        help="Split drawing into multiple pages"
    )
    
    use_split = st.checkbox(
        "Smart splitting",
        value=False,
        help="Automatically detect and split drawing segments"
    )
    
    show_stats = st.checkbox(
        "Show entity statistics",
        value=True,
        help="Display analysis of DXF entities"
    )

# Batch Processing Section
st.header("🚀 Batch Processing")
st.markdown("Upload multiple files or folders for batch conversion")

batch_col1, batch_col2, batch_col3 = st.columns(3)

with batch_col1:
    st.subheader("📂 Upload Files/Folder")
    uploaded_files = st.file_uploader(
        "Upload multiple DXF or HTML files",
        type=['dxf', 'DXF', 'html', 'htm', 'HTML', 'HTM'],
        accept_multiple_files=True,
        key="batch_upload"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Separate by type
        dxf_files = [f for f in uploaded_files if f.name.lower().endswith(('.dxf'))]
        html_files = [f for f in uploaded_files if f.name.lower().endswith(('.html', '.htm'))]
        
        st.info(f"📐 DXF files: {len(dxf_files)} | 📄 HTML files: {len(html_files)}")

with batch_col2:
    st.subheader("📄 Convert HTML to PDF")
    st.markdown("Convert all HTML files individually and create combined PDF")
    
    if st.button("🔄 Convert All HTML", type="primary", use_container_width=True, key="convert_html"):
        if not uploaded_files:
            st.warning("⚠️ Please upload files first")
        else:
            html_files = [f for f in uploaded_files if f.name.lower().endswith(('.html', '.htm'))]
            
            if not html_files:
                st.warning("⚠️ No HTML files found")
            else:
                with st.spinner(f'Converting {len(html_files)} HTML file(s)...'):
                    try:
                        # Create temp directory
                        temp_dir = Path(tempfile.mkdtemp())
                        converter = HTMLConverter(temp_dir)
                        
                        # Save uploaded HTML files
                        html_paths = []
                        for html_file in html_files:
                            html_path = temp_dir / html_file.name
                            html_path.write_bytes(html_file.getvalue())
                            html_paths.append(html_path)
                        
                        # Convert to PDFs
                        pdf_paths, failed = converter.convert_batch(html_paths)
                        
                        if pdf_paths:
                            st.success(f"✅ Converted {len(pdf_paths)} HTML file(s)")
                            
                            # Create combined PDF
                            combined_path = temp_dir / f"combined_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            if merge_pdfs(pdf_paths, combined_path):
                                st.success("✅ Created combined PDF")
                                
                                # Download combined PDF
                                with open(combined_path, 'rb') as f:
                                    st.download_button(
                                        "📥 Download Combined PDF",
                                        f.read(),
                                        file_name=combined_path.name,
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                
                                # Download individual PDFs as ZIP
                                zip_path = temp_dir / "individual_pdfs.zip"
                                with zipfile.ZipFile(zip_path, 'w') as zipf:
                                    for pdf_path in pdf_paths:
                                        zipf.write(pdf_path, pdf_path.name)
                                
                                with open(zip_path, 'rb') as f:
                                    st.download_button(
                                        "📦 Download Individual PDFs (ZIP)",
                                        f.read(),
                                        file_name="html_pdfs.zip",
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                        
                        if failed:
                            st.warning(f"⚠️ Failed to convert {len(failed)} file(s)")
                            for file, error in failed:
                                st.error(f"❌ {file.name}: {error}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

with batch_col3:
    st.subheader("📐 Convert DXF to PDF")
    st.markdown("Convert all DXF files to PDF format")
    
    if st.button("🔄 Convert All DXF", type="primary", use_container_width=True, key="convert_dxf"):
        if not uploaded_files:
            st.warning("⚠️ Please upload files first")
        else:
            dxf_files = [f for f in uploaded_files if f.name.lower().endswith('.dxf')]
            
            if not dxf_files:
                st.warning("⚠️ No DXF files found")
            else:
                with st.spinner(f'Converting {len(dxf_files)} DXF file(s)...'):
                    try:
                        temp_dir = Path(tempfile.mkdtemp())
                        pdf_paths = []
                        failed = []
                        
                        for dxf_file in dxf_files:
                            # Save DXF file
                            dxf_path = temp_dir / dxf_file.name
                            dxf_path.write_bytes(dxf_file.getvalue())
                            
                            # Convert to PDF
                            pdf_path = dxf_path.with_suffix('.pdf')
                            
                            try:
                                success = convert_dxf_file(dxf_path, pdf_path, num_pages=1, use_split=False)
                                if success and pdf_path.exists():
                                    pdf_paths.append(pdf_path)
                                else:
                                    failed.append((dxf_file.name, "Conversion failed"))
                            except Exception as e:
                                failed.append((dxf_file.name, str(e)))
                        
                        if pdf_paths:
                            st.success(f"✅ Converted {len(pdf_paths)} DXF file(s)")
                            
                            # Download all PDFs as ZIP
                            zip_path = temp_dir / "dxf_pdfs.zip"
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for pdf_path in pdf_paths:
                                    zipf.write(pdf_path, pdf_path.name)
                            
                            with open(zip_path, 'rb') as f:
                                st.download_button(
                                    "📦 Download All PDFs (ZIP)",
                                    f.read(),
                                    file_name=f"dxf_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                        
                        if failed:
                            st.warning(f"⚠️ Failed to convert {len(failed)} file(s)")
                            for filename, error in failed:
                                st.error(f"❌ {filename}: {error}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

st.markdown("---")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Single File Conversion")
    
    uploaded_file = st.file_uploader(
        "Choose a DXF file",
        type=['dxf', 'DXF'],
        help="Select your AutoCAD DXF file to convert"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.info(f"📄 **File:** {uploaded_file.name} ({file_size:.1f} KB)")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = Path(tmp_file.name)
        
        try:
            # Analyze DXF file if requested
            if show_stats:
                with st.spinner("🔍 Analyzing DXF file..."):
                    parser = DXFParser()
                    drawing = parser.parse_file(tmp_path)
                    
                    geo_processor = GeometryProcessor()
                    entities = geo_processor.extract_entities(drawing)
                    
                    renderer = PDFRenderer()
                    stats = renderer.get_rendering_stats(entities)
                
                # Display statistics
                st.subheader("📊 DXF Analysis")
                
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    st.metric("Total Entities", stats['total'])
                
                with col_stats2:
                    st.metric("Supported", stats['supported'])
                
                with col_stats3:
                    success_rate = (stats['supported'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Entity breakdown
                if stats['by_type']:
                    st.subheader("🔍 Entity Types Found")
                    
                    supported_types = {
                        'LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE', 
                        'TEXT', 'MTEXT', 'SPLINE', 'ELLIPSE', 'POINT', 'INSERT'
                    }
                    
                    for entity_type, count in sorted(stats['by_type'].items()):
                        status = "✅" if entity_type in supported_types else "❌"
                        st.write(f"{status} **{entity_type}**: {count}")
            
            # Convert button
            if st.button("🔄 Convert to PDF", type="primary", use_container_width=True):
                pdf_path = tmp_path.with_suffix('.pdf')
                
                with st.spinner('Converting DXF to PDF...'):
                    try:
                        success = convert_dxf_file(
                            tmp_path, 
                            pdf_path, 
                            num_pages=num_pages, 
                            use_split=use_split
                        )
                    except Exception as conv_error:
                        st.error(f"❌ Conversion error: {str(conv_error)}")
                        success = False
                
                if success and pdf_path.exists():
                    # Success message
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ Conversion Successful!</h4>
                        <p>Your DXF file has been converted to PDF format.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # File info
                    pdf_size = pdf_path.stat().st_size / 1024  # KB
                    st.info(f"📄 **Generated PDF:** {pdf_size:.1f} KB")
                    
                    # Download button
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                        
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=uploaded_file.name.replace('.dxf', '.pdf').replace('.DXF', '.pdf'),
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    
                    # Clean up
                    try:
                        pdf_path.unlink()
                    except:
                        pass
                        
                else:
                    st.markdown("""
                    <div class="error-box">
                        <h4>❌ Conversion Failed</h4>
                        <p>Unable to convert the DXF file. Possible reasons:</p>
                        <ul>
                            <li>The DXF file may be corrupted or invalid</li>
                            <li>The file may be empty or contain no drawable entities</li>
                            <li>The DXF version may not be supported</li>
                        </ul>
                        <p><strong>Troubleshooting:</strong></p>
                        <ul>
                            <li>Try opening the file in AutoCAD or another DXF viewer to verify it's valid</li>
                            <li>Ensure the file contains actual drawing entities (lines, circles, etc.)</li>
                            <li>Try saving the file in a different DXF version (R2018 or R2013 recommended)</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show file details for debugging
                    st.info(f"📋 File details: {uploaded_file.name} ({file_size:.1f} KB)")
            
        except Exception as e:
            st.error(f"❌ Error processing DXF file: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                tmp_path.unlink()
            except:
                pass

with col2:
    st.header("ℹ️ About")
    
    st.markdown("""
    <div class="feature-box">
        <h4>🚀 Features</h4>
        <ul>
            <li>Fast DXF to PDF conversion</li>
            <li>Support for multiple entity types</li>
            <li>Multi-page output options</li>
            <li>Smart drawing segmentation</li>
            <li>Entity analysis and statistics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>📐 Supported Entities</h4>
        <ul>
            <li>✅ Lines and Polylines</li>
            <li>✅ Circles and Arcs</li>
            <li>✅ Text and Multi-text</li>
            <li>✅ Splines and Ellipses</li>
            <li>✅ Points and Blocks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h4>🔧 Technical Info</h4>
        <p><strong>Output:</strong> A4 Landscape PDF<br>
        <strong>Scale:</strong> Auto-calculated<br>
        <strong>Colors:</strong> Preserved from DXF<br>
        <strong>Max File Size:</strong> 200MB</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🔧 DXF to PDF Converter | Built with Streamlit | 
    <a href="https://github.com/CRAJKUMARSINGH/PDF-STRUCTURE-MAHIPAL-KATARA" target="_blank">View Source</a></p>
</div>
""", unsafe_allow_html=True)
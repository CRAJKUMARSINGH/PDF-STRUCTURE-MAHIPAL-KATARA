from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dxf_converter import DXFToPDFConverter
from html2pdf.service import HTMLToPDFService
from unified_converter import UnifiedConverter
from pathlib import Path
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'INPUT_DATA'
app.config['OUTPUT_FOLDER'] = 'OUTPUT_PDF'

# Initialize converters with 3 scale options
standard_converter = DXFToPDFConverter(scale_mode='standard')      # Standard scale
enlarged_2x_converter = DXFToPDFConverter(scale_mode='enlarged_2x') # 2x enlarged scale
maximum_4x_converter = DXFToPDFConverter(scale_mode='maximum_4x')   # 4x maximum detail

# Default converter (for backward compatibility)
converter = standard_converter
html_converter = HTMLToPDFService(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], 
                                      page_size='A4', orientation='Portrait')
unified_converter = UnifiedConverter(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])

ALLOWED_EXTENSIONS = {'dxf', 'DXF', 'html', 'htm', 'HTML', 'HTM'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get DXF files
    dxf_files = list(Path(app.config['UPLOAD_FOLDER']).glob('*.dxf'))
    dxf_files.extend(Path(app.config['UPLOAD_FOLDER']).glob('*.DXF'))
    dxf_files = sorted(set(dxf_files), key=lambda x: x.name)
    
    # Get HTML files
    html_files = list(Path(app.config['UPLOAD_FOLDER']).glob('*.html'))
    html_files.extend(Path(app.config['UPLOAD_FOLDER']).glob('*.htm'))
    html_files.extend(Path(app.config['UPLOAD_FOLDER']).glob('*.HTML'))
    html_files.extend(Path(app.config['UPLOAD_FOLDER']).glob('*.HTM'))
    html_files = sorted(set(html_files), key=lambda x: x.name)
    
    # Get output PDF files
    output_files = sorted(Path(app.config['OUTPUT_FOLDER']).glob('*.pdf'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    return render_template('index.html', 
                         dxf_files=[f.name for f in dxf_files],
                         html_files=[f.name for f in html_files],
                         output_files=[f.name for f in output_files])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'success': False, 'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    uploaded = []
    errors = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(filepath)
            uploaded.append(filename)
            logger.info(f"Uploaded: {filename}")
        elif file and file.filename:
            errors.append(f"{file.filename} - Invalid file type")
    
    return jsonify({
        'success': True,
        'uploaded': uploaded,
        'errors': errors,
        'count': len(uploaded)
    })

@app.route('/convert', methods=['POST'])
def convert_files():
    try:
        data = request.get_json() or {}
        files_to_convert = data.get('files', [])
        scale_mode = data.get('scale_mode', 'standard')  # 'standard' or 'enlarged'
        
        # Choose converter based on scale mode
        converter_map = {
            'standard': standard_converter,
            'enlarged_2x': enlarged_2x_converter,
            'maximum_4x': maximum_4x_converter
        }
        active_converter = converter_map.get(scale_mode, standard_converter)
        
        if not files_to_convert:
            results = active_converter.batch_convert()
        else:
            results = []
            for filename in files_to_convert:
                dxf_path = Path(app.config['UPLOAD_FOLDER']) / filename
                if dxf_path.exists():
                    success, output, pages = active_converter.convert_dxf_to_pdf(dxf_path)
                    results.append({
                        'input': filename,
                        'output': Path(output).name if success else output,
                        'success': success,
                        'pages': pages,
                        'scale_mode': scale_mode
                    })
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        return jsonify({
            'success': True,
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results,
            'scale_mode': scale_mode
        })
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_scale_options')
def get_scale_options():
    """Get available DXF scale options."""
    try:
        return jsonify({
            'success': True,
            'scale_options': DXFToPDFConverter.SCALE_OPTIONS
        })
    except Exception as e:
        logger.error(f"Error getting scale options: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = Path(app.config['OUTPUT_FOLDER']) / secure_filename(filename)
        if filepath.exists():
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_input/<filename>', methods=['POST'])
def delete_input(filename):
    try:
        filepath = Path(app.config['UPLOAD_FOLDER']) / secure_filename(filename)
        if filepath.exists():
            filepath.unlink()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_output/<filename>', methods=['POST'])
def delete_output(filename):
    try:
        filepath = Path(app.config['OUTPUT_FOLDER']) / secure_filename(filename)
        if filepath.exists():
            filepath.unlink()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/convert_html', methods=['POST'])
def convert_html_files():
    """Convert HTML files to PDF."""
    try:
        data = request.get_json() or {}
        files_to_convert = data.get('files', [])
        output_filename = data.get('output_filename')
        
        # Convert HTML files
        result = html_converter.convert_html_to_pdf(files_to_convert, output_filename)
        
        if result['success']:
            logger.info(f"HTML to PDF conversion successful: {result['output_file']}")
        else:
            logger.error(f"HTML to PDF conversion failed: {result.get('error', 'Unknown error')}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"HTML conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/html_files')
def get_html_files():
    """Get list of available HTML files."""
    try:
        html_files = html_converter.get_html_files()
        return jsonify({'success': True, 'files': html_files})
    except Exception as e:
        logger.error(f"Error getting HTML files: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/convert_all', methods=['POST'])
def convert_all_files():
    """Convert all HTML and DXF files in one operation with organized output."""
    try:
        logger.info("Starting unified conversion of all files")
        
        # Create new unified converter instance for this session
        session_converter = UnifiedConverter(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])
        
        # Perform unified conversion
        results = session_converter.convert_all_files()
        
        if results['summary']['overall_success']:
            logger.info(f"Unified conversion successful - Session: {results['timestamp']}")
        else:
            logger.error(f"Unified conversion failed - Session: {results['timestamp']}")
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Unified conversion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'summary': {'overall_success': False}
        }), 500

@app.route('/get_session_folders')
def get_session_folders():
    """Get list of available session folders."""
    try:
        base_output = Path(app.config['OUTPUT_FOLDER'])
        
        # Get HTML session folders
        html_sessions = []
        html_base = base_output / "HTML_REPORTS"
        if html_base.exists():
            html_sessions = [f.name for f in html_base.iterdir() if f.is_dir() and f.name.startswith('session_')]
        
        # Get DXF session folders
        dxf_sessions = []
        dxf_base = base_output / "DXF_DRAWINGS"
        if dxf_base.exists():
            dxf_sessions = [f.name for f in dxf_base.iterdir() if f.is_dir() and f.name.startswith('session_')]
        
        # Get all unique sessions
        all_sessions = sorted(list(set(html_sessions + dxf_sessions)), reverse=True)
        
        return jsonify({
            'success': True,
            'sessions': all_sessions,
            'html_sessions': html_sessions,
            'dxf_sessions': dxf_sessions
        })
    
    except Exception as e:
        logger.error(f"Error getting session folders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_session/<session_id>/<file_type>/<filename>')
def download_session_file(session_id, file_type, filename):
    """Download file from specific session folder."""
    try:
        base_output = Path(app.config['OUTPUT_FOLDER'])
        
        if file_type == 'html':
            file_path = base_output / "HTML_REPORTS" / session_id / secure_filename(filename)
        elif file_type == 'dxf':
            file_path = base_output / "DXF_DRAWINGS" / session_id / secure_filename(filename)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Unified DXF and HTML to PDF Converter'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

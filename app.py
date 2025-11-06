from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dxf_converter import DXFToPDFConverter
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

converter = DXFToPDFConverter()

ALLOWED_EXTENSIONS = {'dxf', 'DXF'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    input_files = list(Path(app.config['UPLOAD_FOLDER']).glob('*.dxf'))
    input_files.extend(Path(app.config['UPLOAD_FOLDER']).glob('*.DXF'))
    input_files = sorted(set(input_files), key=lambda x: x.name)
    
    output_files = sorted(Path(app.config['OUTPUT_FOLDER']).glob('*.pdf'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    return render_template('index.html', 
                         input_files=[f.name for f in input_files],
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
        
        if not files_to_convert:
            results = converter.batch_convert()
        else:
            results = []
            for filename in files_to_convert:
                dxf_path = Path(app.config['UPLOAD_FOLDER']) / filename
                if dxf_path.exists():
                    success, output, pages = converter.convert_dxf_to_pdf(dxf_path)
                    results.append({
                        'input': filename,
                        'output': Path(output).name if success else output,
                        'success': success,
                        'pages': pages
                    })
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        return jsonify({
            'success': True,
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
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

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'DXF to PDF Converter'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

import logging
import os
from flask import Flask, render_template, jsonify

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def index():
    logger.info("Root route accessed")
    return "Mashaaer server is running - Test OK"

@app.route('/diagnostic')
def diagnostic():
    logger.info("Diagnostic route accessed")
    try:
        return app.send_static_file('diagnostic.html')
    except Exception as e:
        logger.error(f"Error sending static file: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/cosmic')
def cosmic():
    logger.info("Cosmic route accessed")
    try:
        return render_template('cosmic_onboarding.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return f"Error rendering cosmic_onboarding.html: {str(e)}", 500

@app.route('/status')
def status():
    logger.info("Status route accessed")
    file_info = {}
    
    # Check static files
    if os.path.exists('static'):
        static_files = os.listdir('static')
        file_info['static_files'] = static_files
        file_info['static_count'] = len(static_files)
    else:
        file_info['static_files'] = 'Directory not found'
    
    # Check template files
    if os.path.exists('templates'):
        template_files = os.listdir('templates')
        file_info['template_files'] = template_files
        file_info['template_count'] = len(template_files)
    else:
        file_info['template_files'] = 'Directory not found'
    
    return jsonify({
        'status': 'online',
        'file_info': file_info,
        'app_root': app.root_path,
        'static_folder': app.static_folder,
        'template_folder': app.template_folder
    })

if __name__ == '__main__':
    logger.info(f"Starting test server on port 5000")
    logger.info(f"App root: {app.root_path}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Template folder: {app.template_folder}")
    app.run(host='0.0.0.0', port=5000, debug=True)
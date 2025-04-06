from flask import Blueprint, send_from_directory
import os

direct_test_bp = Blueprint('direct_test', __name__)

@direct_test_bp.route('/direct-test')
def direct_test():
    """Serve the direct test HTML file"""
    return send_from_directory(os.getcwd(), 'direct_test.html')

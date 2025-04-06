from flask import Blueprint, send_from_directory
import os

direct_report_bp = Blueprint('direct_report', __name__)

@direct_report_bp.route('/test-report')
def direct_report():
    """Serve the test report HTML file"""
    return send_from_directory(os.getcwd(), 'direct_report.html')

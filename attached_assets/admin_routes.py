from flask import Blueprint, render_template
import json, csv

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin():
    with open('rules_config.json') as f:
        rules = json.load(f)
    with open('logs/interaction_log.csv') as f:
        logs = list(csv.reader(f))
    return render_template('admin.html', rules=rules, logs=logs)
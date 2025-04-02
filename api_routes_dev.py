"""
API Routes for Developer Mode in Robin AI
Provides access to system logs, database management, and performance metrics
"""

import os
import json
import logging
import datetime
import time
import shutil
import sqlite3
import subprocess
from flask import Blueprint, request, jsonify, session

# Set up logger
logger = logging.getLogger(__name__)

def init_developer_api(app):
    """Initialize the developer API endpoints"""
    dev_api = Blueprint('dev_api', __name__)
    
    @dev_api.route('/logs', methods=['GET'])
    def get_logs():
        """Get system logs for developer mode"""
        try:
            log_type = request.args.get('type', 'all')
            max_entries = int(request.args.get('max', 1000))
            
            # Define log directories
            log_dirs = {
                'system': './logs',
                'voice': './voice_logs',
                'errors': './logs/errors'
            }
            
            logs = []
            
            # Determine which directories to scan based on log_type
            dirs_to_scan = []
            if log_type == 'all':
                dirs_to_scan = log_dirs.values()
            elif log_type in log_dirs:
                dirs_to_scan = [log_dirs[log_type]]
            
            # Scan log directories
            for log_dir in dirs_to_scan:
                if os.path.exists(log_dir):
                    for filename in os.listdir(log_dir):
                        if filename.endswith('.log'):
                            log_path = os.path.join(log_dir, filename)
                            try:
                                with open(log_path, 'r') as file:
                                    for line in file:
                                        # Parse log entry
                                        try:
                                            parts = line.strip().split(' ', 3)
                                            if len(parts) >= 3:
                                                date_str = parts[0]
                                                time_str = parts[1]
                                                level = parts[2].strip('[]')
                                                message = parts[3] if len(parts) > 3 else ""
                                                
                                                logs.append({
                                                    'timestamp': f"{date_str} {time_str}",
                                                    'level': level,
                                                    'message': message,
                                                    'type': os.path.basename(log_dir),
                                                    'source': filename
                                                })
                                        except Exception:
                                            # If parse fails, just add the raw line
                                            logs.append({
                                                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'level': 'INFO',
                                                'message': line.strip(),
                                                'type': os.path.basename(log_dir),
                                                'source': filename
                                            })
                            except Exception as e:
                                logger.error(f"Error reading log file {log_path}: {str(e)}")
            
            # Sort logs by timestamp (most recent first)
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit to max_entries
            logs = logs[:max_entries]
            
            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs)
            })
        except Exception as e:
            logger.error(f"Error retrieving logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error retrieving logs: {str(e)}"
            }), 500
    
    @dev_api.route('/logs/clear', methods=['POST'])
    def clear_logs():
        """Clear system logs (developer mode only)"""
        try:
            # Make sure this is a developer with the right permissions
            if request.headers.get('X-Developer-Key') != os.environ.get('DEVELOPER_KEY', 'robin_dev_key'):
                # Check if user has developer mode enabled in session
                if not session.get('developer_mode', False):
                    return jsonify({
                        'success': False,
                        'error': 'Developer permission required'
                    }), 403
            
            # Define log directories
            log_dirs = ['./logs', './voice_logs']
            
            cleared_files = []
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    for filename in os.listdir(log_dir):
                        if filename.endswith('.log'):
                            log_path = os.path.join(log_dir, filename)
                            try:
                                # Clear content but keep file
                                with open(log_path, 'w') as file:
                                    file.write(f"Log cleared on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                cleared_files.append(log_path)
                            except Exception as e:
                                logger.error(f"Error clearing log file {log_path}: {str(e)}")
            
            logger.info(f"Cleared {len(cleared_files)} log files through developer interface")
            
            return jsonify({
                'success': True,
                'message': f"Cleared {len(cleared_files)} log files",
                'cleared_files': cleared_files
            })
        except Exception as e:
            logger.error(f"Error clearing logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error clearing logs: {str(e)}"
            }), 500
    
    @dev_api.route('/db/status', methods=['GET'])
    def get_db_status():
        """Get database status information for developer mode"""
        try:
            # Database file paths
            db_files = []
            
            # Check main database
            if os.path.exists('robin_memory.db'):
                db_files.append('robin_memory.db')
            
            # Look for other SQLite databases
            for file in os.listdir('.'):
                if file.endswith('.db') and file != 'robin_memory.db':
                    db_files.append(file)
            
            total_size = 0
            all_tables = []
            total_records = 0
            
            for db_file in db_files:
                try:
                    # Get file size
                    size_bytes = os.path.getsize(db_file)
                    total_size += size_bytes
                    
                    # Connect to database
                    conn = sqlite3.connect(db_file)
                    c = conn.cursor()
                    
                    # Get list of tables
                    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = c.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        
                        # Skip SQLite internal tables
                        if table_name.startswith('sqlite_'):
                            continue
                        
                        # Get row count
                        try:
                            c.execute(f"SELECT COUNT(*) FROM '{table_name}';")
                            row_count = c.fetchone()[0]
                            total_records += row_count
                            
                            # Calculate table size (approximate)
                            c.execute(f"PRAGMA table_info('{table_name}');")
                            columns = c.fetchall()
                            
                            all_tables.append({
                                'name': table_name,
                                'rows': row_count,
                                'columns': len(columns),
                                'database': db_file,
                                'size': f"{(size_bytes / len(tables)) / 1024:.1f} KB" if len(tables) > 0 else "0 KB"
                            })
                        except Exception as e:
                            logger.error(f"Error analyzing table {table_name}: {str(e)}")
                            all_tables.append({
                                'name': table_name,
                                'rows': 0,
                                'columns': 0,
                                'database': db_file,
                                'size': "Unknown",
                                'error': str(e)
                            })
                    
                    conn.close()
                except Exception as e:
                    logger.error(f"Error analyzing database {db_file}: {str(e)}")
            
            # Get backup information
            last_backup = None
            backup_dir = './database/backups'
            if os.path.exists(backup_dir):
                backups = [f for f in os.listdir(backup_dir) if f.endswith('.backup') or f.endswith('.sql')]
                if backups:
                    # Get most recent backup
                    backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
                    last_backup_time = os.path.getmtime(os.path.join(backup_dir, backups[0]))
                    last_backup = datetime.datetime.fromtimestamp(last_backup_time).strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({
                'success': True,
                'size': f"{total_size / 1024 / 1024:.2f} MB",
                'size_bytes': total_size,
                'tables': all_tables,
                'total_records': total_records,
                'databases': db_files,
                'last_backup': last_backup
            })
        except Exception as e:
            logger.error(f"Error retrieving database status: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error retrieving database status: {str(e)}"
            }), 500
    
    @dev_api.route('/db/backup', methods=['POST'])
    def backup_database():
        """Create a database backup (developer mode only)"""
        try:
            # Make sure this is a developer with the right permissions
            if request.headers.get('X-Developer-Key') != os.environ.get('DEVELOPER_KEY', 'robin_dev_key'):
                # Check if user has developer mode enabled in session
                if not session.get('developer_mode', False):
                    return jsonify({
                        'success': False,
                        'error': 'Developer permission required'
                    }), 403
            
            # Ensure backup directory exists
            backup_dir = './database/backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamp for backup filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"robin_db_backup_{timestamp}.sql"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Database file path
            db_path = 'robin_memory.db'
            
            if not os.path.exists(db_path):
                return jsonify({
                    'success': False,
                    'error': 'Database file not found'
                }), 404
            
            # Create backup
            # Option 1: Simple file copy (if SQLite)
            simple_backup_path = os.path.join(backup_dir, f"robin_db_backup_{timestamp}.backup")
            shutil.copy2(db_path, simple_backup_path)
            
            try:
                # Option 2: Use sqlite3 command to dump SQL (better for restoration)
                dump_cmd = f"sqlite3 {db_path} .dump > {backup_path}"
                subprocess.run(dump_cmd, shell=True, check=True)
                
                logger.info(f"Created database backup: {backup_path}")
                
                # Generate download URL
                download_url = f"/database/backups/{backup_filename}"
                
                return jsonify({
                    'success': True,
                    'message': f"Database backup created successfully",
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'backup_path': backup_path,
                    'file_size': os.path.getsize(backup_path),
                    'download_url': download_url,
                    'filename': backup_filename
                })
            except Exception as e:
                logger.error(f"Error creating SQL dump backup: {str(e)}")
                # If SQL dump fails, at least we have the file copy
                return jsonify({
                    'success': True,
                    'message': f"Database backup created (file copy only, SQL dump failed)",
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'backup_path': simple_backup_path,
                    'file_size': os.path.getsize(simple_backup_path),
                    'error_details': str(e)
                })
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error backing up database: {str(e)}"
            }), 500
    
    @dev_api.route('/db/optimize', methods=['POST'])
    def optimize_database():
        """Optimize database performance (developer mode only)"""
        try:
            # Make sure this is a developer with the right permissions
            if request.headers.get('X-Developer-Key') != os.environ.get('DEVELOPER_KEY', 'robin_dev_key'):
                # Check if user has developer mode enabled in session
                if not session.get('developer_mode', False):
                    return jsonify({
                        'success': False,
                        'error': 'Developer permission required'
                    }), 403
            
            # Database file path
            db_path = 'robin_memory.db'
            
            if not os.path.exists(db_path):
                return jsonify({
                    'success': False,
                    'error': 'Database file not found'
                }), 404
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Perform optimization operations
            operations = [
                "PRAGMA optimize;",
                "VACUUM;",
                "ANALYZE;",
                "PRAGMA integrity_check;"
            ]
            
            results = {}
            
            for op in operations:
                try:
                    cursor.execute(op)
                    if op == "PRAGMA integrity_check;":
                        results[op] = cursor.fetchone()[0]
                    else:
                        results[op] = "Success"
                except Exception as e:
                    results[op] = f"Error: {str(e)}"
            
            conn.close()
            
            logger.info("Database optimization completed through developer interface")
            
            return jsonify({
                'success': True,
                'message': "Database optimization completed",
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'operations': results
            })
        except Exception as e:
            logger.error(f"Error optimizing database: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error optimizing database: {str(e)}"
            }), 500
    
    @dev_api.route('/system/performance', methods=['GET'])
    def get_system_performance():
        """Get system performance metrics for developer mode"""
        try:
            # Measure API response time (include this in the response)
            start_time = time.time()
            
            # Get CPU usage
            try:
                # Try importing psutil
                import psutil
                cpu_usage = psutil.cpu_percent(interval=0.1)
                
                # Get memory usage
                memory = psutil.virtual_memory()
                memory_usage = {
                    'total': f"{memory.total / (1024 * 1024 * 1024):.2f} GB",
                    'available': f"{memory.available / (1024 * 1024 * 1024):.2f} GB",
                    'used': f"{memory.used / (1024 * 1024 * 1024):.2f} GB",
                    'percent': memory.percent
                }
                
                # Get disk usage
                disk = psutil.disk_usage('/')
                disk_usage = {
                    'total': f"{disk.total / (1024 * 1024 * 1024):.2f} GB",
                    'used': f"{disk.used / (1024 * 1024 * 1024):.2f} GB",
                    'free': f"{disk.free / (1024 * 1024 * 1024):.2f} GB",
                    'percent': disk.percent
                }
                
                # Get system uptime
                boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
                uptime = datetime.datetime.now() - boot_time
                uptime_str = str(uptime).split('.')[0]  # Format as HH:MM:SS
                uptime_seconds = uptime.total_seconds()
                boot_time_str = boot_time.strftime('%Y-%m-%d %H:%M:%S')
            except ImportError:
                # Fallback if psutil isn't available
                cpu_usage = -1
                memory_usage = {
                    'total': 'N/A',
                    'available': 'N/A',
                    'used': 'N/A',
                    'percent': -1
                }
                disk_usage = {
                    'total': 'N/A',
                    'used': 'N/A',
                    'free': 'N/A',
                    'percent': -1
                }
                uptime_str = 'N/A'
                uptime_seconds = -1
                boot_time_str = 'N/A'
            
            # Get active sessions (estimate from Flask session)
            active_sessions = len(os.listdir('./flask_session')) if os.path.exists('./flask_session') else 0
            
            # Get API response time
            api_response_time = int((time.time() - start_time) * 1000)  # in milliseconds
            
            return jsonify({
                'success': True,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cpu': cpu_usage,
                'memory': f"{memory_usage['used']} / {memory_usage['total']} ({memory_usage['percent']}%)" if cpu_usage != -1 else 'N/A',
                'memory_percent': memory_usage['percent'] if cpu_usage != -1 else -1,
                'disk': f"{disk_usage['used']} / {disk_usage['total']} ({disk_usage['percent']}%)" if cpu_usage != -1 else 'N/A',
                'disk_percent': disk_usage['percent'] if cpu_usage != -1 else -1,
                'uptime': uptime_str,
                'uptime_seconds': uptime_seconds,
                'boot_time': boot_time_str,
                'active_sessions': active_sessions,
                'api_response_time': api_response_time
            })
        except Exception as e:
            logger.error(f"Error retrieving system performance: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"Error retrieving system performance: {str(e)}"
            }), 500
    
    # Register the blueprint
    app.register_blueprint(dev_api, url_prefix='/api')
    return dev_api
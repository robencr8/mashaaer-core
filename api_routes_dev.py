"""
API Routes for Developer Mode in Robin AI
Provides access to system logs, database management, and performance metrics
"""

import os
import json
import time
import logging
import psutil
import sqlite3
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)

# Import Flask dependencies here to avoid circular imports
from flask import Blueprint, jsonify, request, current_app

# Initialize the developer API blueprint
def init_developer_api(app):
    """Initialize the developer API endpoints"""
    
    dev_api = Blueprint('dev_api', __name__)
    
    @dev_api.route('/api/dev/logs', methods=['GET'])
    def get_logs():
        """Get system logs for developer mode"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Determine log paths
            log_paths = _get_log_paths()
            
            # Get filter parameters
            log_type = request.args.get('type', 'all')
            level = request.args.get('level', 'all')
            limit = int(request.args.get('limit', 100))
            search = request.args.get('search', '')
            
            # Read and filter logs
            logs = _read_logs(log_paths, log_type, level, limit, search)
            
            return jsonify({
                'success': True,
                'logs': logs,
                'log_paths': log_paths
            })
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @dev_api.route('/api/dev/logs/clear', methods=['POST'])
    def clear_logs():
        """Clear system logs (developer mode only)"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Determine log paths
            log_paths = _get_log_paths()
            
            # Get specific log type to clear, or 'all'
            log_type = request.json.get('type', 'all')
            
            # Clear specified logs
            cleared = _clear_logs(log_paths, log_type)
            
            return jsonify({
                'success': True,
                'cleared': cleared
            })
        except Exception as e:
            logger.error(f"Error clearing logs: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @dev_api.route('/api/dev/db/status', methods=['GET'])
    def get_db_status():
        """Get database status information for developer mode"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Get DB Manager from app context
            db_manager = current_app.config.get('db_manager')
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database manager not available'}), 500
            
            # Get database information
            db_status = _get_db_info(db_manager)
            
            return jsonify({
                'success': True,
                'status': db_status
            })
        except Exception as e:
            logger.error(f"Error getting database status: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @dev_api.route('/api/dev/db/backup', methods=['POST'])
    def backup_database():
        """Create a database backup (developer mode only)"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Get DB Manager from app context
            db_manager = current_app.config.get('db_manager')
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database manager not available'}), 500
            
            # Create backup
            backup_path = _backup_database(db_manager)
            
            return jsonify({
                'success': True,
                'backup_path': backup_path,
                'message': f'Database backup created at {backup_path}'
            })
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @dev_api.route('/api/dev/db/optimize', methods=['POST'])
    def optimize_database():
        """Optimize database performance (developer mode only)"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Get DB Manager from app context
            db_manager = current_app.config.get('db_manager')
            if not db_manager:
                return jsonify({'success': False, 'error': 'Database manager not available'}), 500
            
            # Optimize database
            optimization_result = _optimize_database(db_manager)
            
            return jsonify({
                'success': True,
                'optimization_result': optimization_result
            })
        except Exception as e:
            logger.error(f"Error optimizing database: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @dev_api.route('/api/dev/system/performance', methods=['GET'])
    def get_system_performance():
        """Get system performance metrics for developer mode"""
        try:
            # Check if request has developer authorization
            if not _is_developer_authorized():
                return jsonify({'success': False, 'error': 'Developer authorization required'}), 403
            
            # Get system performance metrics
            performance = _get_system_performance()
            
            return jsonify({
                'success': True,
                'performance': performance
            })
        except Exception as e:
            logger.error(f"Error getting system performance: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Helper methods
    def _is_developer_authorized():
        """Check if the request is authorized for developer operations"""
        # First check for developer mode in app config
        from main import is_developer_mode
        
        if not is_developer_mode():
            # If not in dev mode, check for developer API key
            dev_key = request.headers.get('X-Developer-Key')
            expected_key = os.environ.get('DEVELOPER_KEY', 'robin_dev_key')
            
            if not dev_key or dev_key != expected_key:
                return False
        
        return True
    
    def _get_log_paths():
        """Get paths to log files"""
        log_dir = 'logs'
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Define log paths
        log_paths = {
            'system': os.path.join(log_dir, 'robin.log'),
            'errors': os.path.join(log_dir, 'errors.log'),
            'api': os.path.join(log_dir, 'api.log'),
            'voice': os.path.join('voice_logs', 'recognition.log')
        }
        
        return log_paths
    
    def _read_logs(log_paths, log_type='all', level='all', limit=100, search=''):
        """Read and filter logs"""
        logs = []
        
        # Determine which log files to read
        files_to_read = []
        if log_type == 'all':
            files_to_read = log_paths.values()
        elif log_type in log_paths:
            files_to_read = [log_paths[log_type]]
        
        # Read each log file
        for log_file in files_to_read:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        file_logs = f.readlines()
                        
                        # Filter by level if specified
                        if level != 'all':
                            file_logs = [log for log in file_logs if f":{level.upper()}:" in log]
                            
                        # Filter by search term if specified
                        if search:
                            file_logs = [log for log in file_logs if search.lower() in log.lower()]
                            
                        # Add log source and parse timestamp if possible
                        parsed_logs = []
                        for log in file_logs:
                            log_entry = {
                                'text': log.strip(),
                                'source': os.path.basename(log_file),
                                'timestamp': _extract_timestamp(log)
                            }
                            parsed_logs.append(log_entry)
                        
                        logs.extend(parsed_logs)
                except Exception as e:
                    logs.append({
                        'text': f"Error reading log file {log_file}: {str(e)}",
                        'source': 'error',
                        'timestamp': time.time()
                    })
        
        # Sort logs by timestamp (newest first)
        logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Limit number of logs
        return logs[:limit]
    
    def _extract_timestamp(log_line):
        """Extract timestamp from log line"""
        try:
            # Try to extract ISO format timestamp
            iso_formats = [
                '%Y-%m-%d %H:%M:%S,%f',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in iso_formats:
                try:
                    date_str = log_line.split(' ')[0] + ' ' + log_line.split(' ')[1]
                    dt = datetime.strptime(date_str, fmt)
                    return dt.timestamp()
                except:
                    continue
            
            # If no timestamp found, use current time
            return time.time()
        except:
            return time.time()
    
    def _clear_logs(log_paths, log_type='all'):
        """Clear specified log files"""
        cleared = []
        
        # Determine which log files to clear
        files_to_clear = []
        if log_type == 'all':
            files_to_clear = log_paths.values()
        elif log_type in log_paths:
            files_to_clear = [log_paths[log_type]]
        
        # Clear each log file
        for log_file in files_to_clear:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'w') as f:
                        f.write(f"Log cleared at {datetime.now().isoformat()}\n")
                    cleared.append(os.path.basename(log_file))
                except Exception as e:
                    logger.error(f"Error clearing log file {log_file}: {str(e)}")
        
        return cleared
    
    def _get_db_info(db_manager):
        """Get database information"""
        info = {
            'type': 'unknown',
            'tables': [],
            'size': 0,
            'rows_per_table': {},
            'last_backup': None
        }
        
        try:
            # Determine database type
            if hasattr(db_manager, 'use_postgres') and db_manager.use_postgres:
                info['type'] = 'postgresql'
                info['connection'] = {
                    'host': os.environ.get('PGHOST', 'unknown'),
                    'port': os.environ.get('PGPORT', 'unknown'),
                    'database': os.environ.get('PGDATABASE', 'unknown'),
                    'user': os.environ.get('PGUSER', 'unknown')
                }
                
                # Get tables
                tables_query = """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                tables_result = db_manager.execute_query(tables_query)
                
                if tables_result:
                    tables = [row[0] for row in tables_result]
                    info['tables'] = tables
                    
                    # Get row count for each table
                    for table in tables:
                        try:
                            count_query = f"SELECT COUNT(*) FROM {table}"
                            count_result = db_manager.execute_query(count_query)
                            if count_result:
                                info['rows_per_table'][table] = count_result[0][0]
                        except:
                            info['rows_per_table'][table] = -1
                
                # Get database size
                size_query = """
                    SELECT pg_database_size(current_database())
                """
                size_result = db_manager.execute_query(size_query)
                if size_result:
                    info['size'] = size_result[0][0]
                    info['size_human'] = _format_size(size_result[0][0])
                
            else:
                info['type'] = 'sqlite'
                info['path'] = db_manager.db_path
                
                # Get file size
                if os.path.exists(db_manager.db_path):
                    info['size'] = os.path.getsize(db_manager.db_path)
                    info['size_human'] = _format_size(info['size'])
                
                # Get tables
                try:
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    info['tables'] = tables
                    
                    # Get row count for each table
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            info['rows_per_table'][table] = count
                        except:
                            info['rows_per_table'][table] = -1
                    
                    conn.close()
                except Exception as e:
                    logger.error(f"Error getting SQLite database info: {str(e)}")
            
            # Check for last backup
            backup_dir = 'database/backups'
            if os.path.exists(backup_dir):
                backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.sql') or f.endswith('.dump')]
                if backups:
                    # Get the most recent backup
                    newest_backup = max(backups, key=os.path.getmtime)
                    info['last_backup'] = {
                        'path': newest_backup,
                        'size': os.path.getsize(newest_backup),
                        'size_human': _format_size(os.path.getsize(newest_backup)),
                        'date': datetime.fromtimestamp(os.path.getmtime(newest_backup)).isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error getting database info: {str(e)}")
            info['error'] = str(e)
        
        return info
    
    def _backup_database(db_manager):
        """Create a database backup"""
        # Create backup directory if it doesn't exist
        backup_dir = 'database/backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate backup file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = None
        
        try:
            # Different backup procedures for PostgreSQL and SQLite
            if hasattr(db_manager, 'use_postgres') and db_manager.use_postgres:
                # PostgreSQL backup using pg_dump
                backup_file = os.path.join(backup_dir, f"postgres_backup_{timestamp}.sql")
                
                # Build pg_dump command
                pg_host = os.environ.get('PGHOST')
                pg_port = os.environ.get('PGPORT')
                pg_user = os.environ.get('PGUSER')
                pg_db = os.environ.get('PGDATABASE')
                pg_password = os.environ.get('PGPASSWORD')
                
                # Set PGPASSWORD environment for pg_dump
                current_env = os.environ.copy()
                current_env['PGPASSWORD'] = pg_password
                
                # Run pg_dump
                import subprocess
                pg_dump_cmd = [
                    'pg_dump',
                    '-h', pg_host,
                    '-p', pg_port,
                    '-U', pg_user,
                    '-d', pg_db,
                    '-f', backup_file,
                    '--format=plain'
                ]
                
                try:
                    subprocess.run(pg_dump_cmd, env=current_env, check=True)
                    backup_path = backup_file
                except subprocess.CalledProcessError:
                    # Try alternative method - use db_manager to export data
                    backup_file = os.path.join(backup_dir, f"postgres_data_export_{timestamp}.json")
                    _export_data_to_json(db_manager, backup_file)
                    backup_path = backup_file
            else:
                # SQLite backup using Python
                backup_file = os.path.join(backup_dir, f"sqlite_backup_{timestamp}.db")
                
                # Copy the database file
                import shutil
                shutil.copy2(db_manager.db_path, backup_file)
                backup_path = backup_file
        
        except Exception as e:
            logger.error(f"Error creating database backup: {str(e)}")
            # Try JSON export as fallback
            try:
                backup_file = os.path.join(backup_dir, f"data_export_fallback_{timestamp}.json")
                _export_data_to_json(db_manager, backup_file)
                backup_path = backup_file
            except Exception as json_err:
                logger.error(f"JSON export fallback failed: {str(json_err)}")
                raise
        
        return backup_path
    
    def _export_data_to_json(db_manager, output_file):
        """Export database data to JSON file"""
        data = {}
        
        # Get tables
        if hasattr(db_manager, 'use_postgres') and db_manager.use_postgres:
            tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        else:
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        
        tables_result = db_manager.execute_query(tables_query)
        if tables_result:
            tables = [row[0] for row in tables_result]
            
            # Export data from each table
            for table in tables:
                try:
                    query = f"SELECT * FROM {table}"
                    rows = db_manager.execute_query(query)
                    
                    # Get column names
                    if hasattr(db_manager, 'use_postgres') and db_manager.use_postgres:
                        col_query = f"""
                            SELECT column_name FROM information_schema.columns
                            WHERE table_schema = 'public' AND table_name = '{table}'
                            ORDER BY ordinal_position
                        """
                        col_result = db_manager.execute_query(col_query)
                        columns = [row[0] for row in col_result]
                    else:
                        cursor = db_manager.get_cursor()
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall()]
                    
                    # Convert rows to dictionaries
                    table_data = []
                    for row in rows:
                        row_dict = {columns[i]: row[i] for i in range(len(columns))}
                        table_data.append(row_dict)
                    
                    data[table] = table_data
                except Exception as e:
                    logger.error(f"Error exporting data from table {table}: {str(e)}")
        
        # Write data to JSON file
        with open(output_file, 'w') as f:
            json.dump(data, f, default=str)
    
    def _optimize_database(db_manager):
        """Optimize database performance"""
        result = {
            'vacuum': False,
            'analyze': False,
            'indices': [],
            'errors': []
        }
        
        try:
            # Different optimizations for PostgreSQL and SQLite
            if hasattr(db_manager, 'use_postgres') and db_manager.use_postgres:
                # PostgreSQL optimizations
                try:
                    db_manager.execute_query("VACUUM ANALYZE")
                    result['vacuum'] = True
                    result['analyze'] = True
                except Exception as e:
                    result['errors'].append(f"VACUUM ANALYZE failed: {str(e)}")
                
                # Update table statistics
                try:
                    # Get tables
                    tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                    tables_result = db_manager.execute_query(tables_query)
                    
                    if tables_result:
                        tables = [row[0] for row in tables_result]
                        
                        # Analyze each table
                        for table in tables:
                            try:
                                db_manager.execute_query(f"ANALYZE {table}")
                                result['indices'].append(f"Analyzed {table}")
                            except Exception as e:
                                result['errors'].append(f"ANALYZE {table} failed: {str(e)}")
                except Exception as e:
                    result['errors'].append(f"Error updating table statistics: {str(e)}")
                
            else:
                # SQLite optimizations
                try:
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    
                    # VACUUM
                    cursor.execute("VACUUM")
                    result['vacuum'] = True
                    
                    # ANALYZE
                    cursor.execute("ANALYZE")
                    result['analyze'] = True
                    
                    # Get indices
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                    indices = [row[0] for row in cursor.fetchall()]
                    result['indices'] = indices
                    
                    conn.close()
                except Exception as e:
                    result['errors'].append(f"SQLite optimization failed: {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Database optimization failed: {str(e)}")
        
        return result
    
    def _get_system_performance():
        """Get system performance metrics"""
        performance = {
            'cpu': {},
            'memory': {},
            'disk': {},
            'uptime': {},
            'process': {}
        }
        
        try:
            # CPU metrics
            performance['cpu']['percent'] = psutil.cpu_percent(interval=1)
            performance['cpu']['count'] = psutil.cpu_count()
            performance['cpu']['per_cpu'] = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            performance['memory']['total'] = memory.total
            performance['memory']['total_human'] = _format_size(memory.total)
            performance['memory']['used'] = memory.used
            performance['memory']['used_human'] = _format_size(memory.used)
            performance['memory']['percent'] = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            performance['disk']['total'] = disk.total
            performance['disk']['total_human'] = _format_size(disk.total)
            performance['disk']['used'] = disk.used
            performance['disk']['used_human'] = _format_size(disk.used)
            performance['disk']['percent'] = disk.percent
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            performance['uptime']['seconds'] = uptime.total_seconds()
            performance['uptime']['formatted'] = _format_timedelta(uptime)
            
            # Process information
            process = psutil.Process()
            performance['process']['pid'] = process.pid
            performance['process']['cpu_percent'] = process.cpu_percent(interval=1)
            performance['process']['memory_percent'] = process.memory_percent()
            performance['process']['memory_info'] = {
                'rss': process.memory_info().rss,
                'rss_human': _format_size(process.memory_info().rss),
                'vms': process.memory_info().vms,
                'vms_human': _format_size(process.memory_info().vms)
            }
            
            # Process start time
            start_time = datetime.fromtimestamp(process.create_time())
            process_uptime = datetime.now() - start_time
            performance['process']['uptime'] = {
                'seconds': process_uptime.total_seconds(),
                'formatted': _format_timedelta(process_uptime)
            }
            
            # Get open files
            try:
                open_files = process.open_files()
                performance['process']['open_files'] = len(open_files)
            except:
                performance['process']['open_files'] = -1
            
            # Get connections
            try:
                connections = process.connections()
                performance['process']['connections'] = len(connections)
            except:
                performance['process']['connections'] = -1
            
            # Resource trends (last 1 hour)
            performance['trends'] = _get_resource_trends()
            
        except Exception as e:
            logger.error(f"Error getting system performance: {str(e)}")
            performance['error'] = str(e)
        
        return performance
    
    def _get_resource_trends():
        """Get resource usage trends over time"""
        trends = {
            'cpu': [],
            'memory': [],
            'timestamp': []
        }
        
        try:
            # Try to load previous resource data if available
            trend_file = 'logs/resource_trends.json'
            current_time = time.time()
            
            if os.path.exists(trend_file):
                try:
                    with open(trend_file, 'r') as f:
                        saved_trends = json.load(f)
                        
                        # Filter to last hour
                        one_hour_ago = current_time - 3600
                        indices = []
                        
                        for i, ts in enumerate(saved_trends.get('timestamp', [])):
                            if ts >= one_hour_ago:
                                indices.append(i)
                        
                        # Get relevant data points
                        if indices:
                            trends['timestamp'] = [saved_trends['timestamp'][i] for i in indices]
                            trends['cpu'] = [saved_trends['cpu'][i] for i in indices]
                            trends['memory'] = [saved_trends['memory'][i] for i in indices]
                except Exception as e:
                    logger.warning(f"Error loading resource trends: {str(e)}")
            
            # Add current data point
            trends['timestamp'].append(current_time)
            trends['cpu'].append(psutil.cpu_percent())
            trends['memory'].append(psutil.virtual_memory().percent)
            
            # Save updated trends
            with open(trend_file, 'w') as f:
                json.dump(trends, f)
            
        except Exception as e:
            logger.error(f"Error getting resource trends: {str(e)}")
        
        return trends
    
    def _format_size(size_bytes):
        """Format bytes to human-readable size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        
        size_kb = size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        
        size_mb = size_kb / 1024
        if size_mb < 1024:
            return f"{size_mb:.2f} MB"
        
        size_gb = size_mb / 1024
        return f"{size_gb:.2f} GB"
    
    def _format_timedelta(delta):
        """Format timedelta to human-readable string"""
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    # Register blueprint with app
    app.register_blueprint(dev_api)
    
    # Store DB Manager in app config for access by API endpoints
    app.config['db_manager'] = app.config.get('db_manager', None)
    
    logger.info("Developer API routes initialized")
    
    return dev_api
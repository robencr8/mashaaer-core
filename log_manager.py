"""
Log Manager for Mashaaer Feelings Application
Handles logging of user interactions for analysis and improvement

Enhanced for Phase 2 with additional features:
- Advanced analytics and trend detection
- User session tracking
- Custom event logging
- Performance monitoring 
- Structured logging with JSON support
"""
import csv
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Constants
LOG_DIR = 'logs'
INTERACTION_LOG_FILE = os.path.join(LOG_DIR, 'interaction_log.csv')
SESSION_LOG_FILE = os.path.join(LOG_DIR, 'session_log.csv')
PERFORMANCE_LOG_FILE = os.path.join(LOG_DIR, 'performance_log.csv')
EVENT_LOG_FILE = os.path.join(LOG_DIR, 'event_log.json')
USER_JOURNEY_LOG_FILE = os.path.join(LOG_DIR, 'user_journey_log.csv')

def init_logs():
    """
    Initialize the enhanced logging system for Phase 2
    Creates the logs directory and all log files if they don't exist
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Create interaction log file with headers if it doesn't exist
        if not os.path.exists(INTERACTION_LOG_FILE):
            with open(INTERACTION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 
                    'user_input', 
                    'emotion', 
                    'action', 
                    'params',
                    'language'
                ])
        
        # Create session log file with headers if it doesn't exist
        if not os.path.exists(SESSION_LOG_FILE):
            with open(SESSION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_id',
                    'user_id',
                    'start_time',
                    'end_time',
                    'duration_seconds',
                    'interaction_count',
                    'platform',
                    'browser',
                    'language'
                ])
        
        # Create performance log file with headers if it doesn't exist
        if not os.path.exists(PERFORMANCE_LOG_FILE):
            with open(PERFORMANCE_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'operation',
                    'duration_ms',
                    'status',
                    'error_message',
                    'memory_usage_mb',
                    'cpu_usage_percent'
                ])
        
        # Create event log file with empty array if it doesn't exist
        if not os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # Create user journey log file with headers if it doesn't exist
        if not os.path.exists(USER_JOURNEY_LOG_FILE):
            with open(USER_JOURNEY_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'user_id',
                    'session_id',
                    'journey_step',
                    'previous_step',
                    'next_step',
                    'step_duration_ms',
                    'user_feedback'
                ])
        
        logger.info("Enhanced logging system (Phase 2) initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing logging system: {str(e)}")
        return False

def log_interaction(user_input: str, emotion: str, action: str, params: Dict[str, Any], language: str = 'en'):
    """
    Log a user interaction
    
    Args:
        user_input: The text input from the user
        emotion: The detected emotion
        action: The action taken by the system
        params: Additional parameters for the action
        language: The language of the interaction ('en' or 'ar')
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Convert params to JSON string
        params_str = json.dumps(params) if isinstance(params, dict) else str(params)
        
        # Write to CSV log
        with open(INTERACTION_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                user_input,
                emotion,
                action,
                params_str,
                language
            ])
        
        logger.debug(f"Logged interaction: emotion={emotion}, action={action}, lang={language}")
        return True
    except Exception as e:
        logger.error(f"Error logging interaction: {str(e)}")
        return False

def get_recent_interactions(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get recent interactions from the log
    
    Args:
        limit: Maximum number of interactions to retrieve
        
    Returns:
        List of interaction records as dictionaries
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return []
        
        interactions = []
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            
            # Read rows and convert to dictionaries
            for row in reader:
                if len(row) >= 5:  # Ensure row has minimum expected columns
                    interaction = {
                        'timestamp': row[0],
                        'user_input': row[1],
                        'emotion': row[2],
                        'action': row[3],
                        'params': row[4],
                        'language': row[5] if len(row) >= 6 else 'en'  # Default to 'en' if language not present
                    }
                    interactions.append(interaction)
        
        # Return the most recent interactions first, up to the limit
        return interactions[-limit:][::-1] if interactions else []
    except Exception as e:
        logger.error(f"Error getting recent interactions: {str(e)}")
        return []

def get_emotion_statistics() -> Dict[str, int]:
    """
    Get statistics on emotions from the interaction log
    
    Returns:
        Dictionary with emotion counts
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return {}
        
        emotion_counts = {}
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 3:  # Ensure row has emotion column
                    emotion = row[2]
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return emotion_counts
    except Exception as e:
        logger.error(f"Error getting emotion statistics: {str(e)}")
        return {}

def get_action_statistics() -> Dict[str, int]:
    """
    Get statistics on actions from the interaction log
    
    Returns:
        Dictionary with action counts
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return {}
        
        action_counts = {}
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 4:  # Ensure row has action column
                    action = row[3]
                    action_counts[action] = action_counts.get(action, 0) + 1
        
        return action_counts
    except Exception as e:
        logger.error(f"Error getting action statistics: {str(e)}")
        return {}

def log_session(session_id: str, user_id: str, start_time: datetime, end_time: Optional[datetime] = None, 
              interaction_count: int = 0, platform: str = "unknown", browser: str = "unknown", 
              language: str = "en") -> bool:
    """
    Log a user session (Phase 2)
    
    Args:
        session_id: Unique identifier for this session
        user_id: Identifier for the user
        start_time: When the session started
        end_time: When the session ended (None if still active)
        interaction_count: Number of interactions in the session
        platform: User's platform (e.g., "web", "mobile", "desktop")
        browser: User's browser (e.g., "chrome", "firefox", "safari")
        language: Session language preference
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Calculate duration if end_time is provided
        duration_seconds = None
        if end_time:
            duration_seconds = (end_time - start_time).total_seconds()
        
        # Write to CSV log
        with open(SESSION_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                session_id,
                user_id,
                start_time.isoformat(),
                end_time.isoformat() if end_time else "",
                duration_seconds if duration_seconds is not None else "",
                interaction_count,
                platform,
                browser,
                language
            ])
        
        logger.debug(f"Logged session: id={session_id}, user={user_id}, interactions={interaction_count}")
        return True
    except Exception as e:
        logger.error(f"Error logging session: {str(e)}")
        return False

def log_performance(operation: str, duration_ms: float, status: str = "success", 
                   error_message: str = "", memory_usage_mb: float = None, 
                   cpu_usage_percent: float = None) -> bool:
    """
    Log a performance measurement (Phase 2)
    
    Args:
        operation: The operation being measured
        duration_ms: Duration of the operation in milliseconds
        status: Status of the operation ("success" or "error")
        error_message: Error message if status is "error"
        memory_usage_mb: Memory usage in MB (if available)
        cpu_usage_percent: CPU usage percentage (if available)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Get memory and CPU usage if not provided
        if memory_usage_mb is None or cpu_usage_percent is None:
            try:
                import psutil
                process = psutil.Process()
                if memory_usage_mb is None:
                    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
                if cpu_usage_percent is None:
                    cpu_usage_percent = process.cpu_percent(interval=0.1)
            except ImportError:
                # psutil not available, use defaults
                if memory_usage_mb is None:
                    memory_usage_mb = ""
                if cpu_usage_percent is None:
                    cpu_usage_percent = ""
        
        # Write to CSV log
        with open(PERFORMANCE_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                operation,
                duration_ms,
                status,
                error_message,
                memory_usage_mb,
                cpu_usage_percent
            ])
        
        logger.debug(f"Logged performance: operation={operation}, duration={duration_ms}ms, status={status}")
        return True
    except Exception as e:
        logger.error(f"Error logging performance: {str(e)}")
        return False

def log_event(event_type: str, data: Dict[str, Any], user_id: Optional[str] = None, 
              session_id: Optional[str] = None) -> bool:
    """
    Log a custom event (Phase 2)
    
    Args:
        event_type: Type of event (e.g., "button_click", "page_view", "error")
        data: Event data as a dictionary
        user_id: Optional user identifier
        session_id: Optional session identifier
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Read existing events
        events = []
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, 'r', encoding='utf-8') as f:
                try:
                    events = json.load(f)
                except json.JSONDecodeError:
                    # File is empty or invalid, start with empty list
                    events = []
        
        # Create new event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        if user_id:
            event["user_id"] = user_id
        if session_id:
            event["session_id"] = session_id
        
        # Add to events list
        events.append(event)
        
        # Write back to file
        with open(EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2)
        
        logger.debug(f"Logged event: type={event_type}, user={user_id}, session={session_id}")
        return True
    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        return False

def log_user_journey(user_id: str, session_id: str, journey_step: str, 
                    previous_step: Optional[str] = None, next_step: Optional[str] = None,
                    step_duration_ms: Optional[float] = None, 
                    user_feedback: Optional[str] = None) -> bool:
    """
    Log a user journey step (Phase 2)
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        journey_step: Current step in the user journey
        previous_step: Previous step (if known)
        next_step: Next step (if known)
        step_duration_ms: Duration spent on this step (if known)
        user_feedback: Optional user feedback for this step
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Write to CSV log
        with open(USER_JOURNEY_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                user_id,
                session_id,
                journey_step,
                previous_step or "",
                next_step or "",
                step_duration_ms or "",
                user_feedback or ""
            ])
        
        logger.debug(f"Logged user journey: user={user_id}, step={journey_step}")
        return True
    except Exception as e:
        logger.error(f"Error logging user journey: {str(e)}")
        return False

def get_performance_statistics(start_time: Optional[datetime] = None, 
                          end_time: Optional[datetime] = None,
                          operation_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance statistics from the log (Phase 2)
    
    Args:
        start_time: Optional start time filter
        end_time: Optional end time filter
        operation_filter: Optional operation name filter
        
    Returns:
        Dictionary with performance statistics
    """
    try:
        if not os.path.exists(PERFORMANCE_LOG_FILE):
            return {}
        
        stats = {
            "operations": {},
            "overall": {
                "avg_duration_ms": 0,
                "min_duration_ms": float('inf'),
                "max_duration_ms": 0,
                "total_operations": 0,
                "success_rate": 0,
                "error_rate": 0
            }
        }
        
        total_duration = 0
        success_count = 0
        error_count = 0
        
        with open(PERFORMANCE_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            
            for row in reader:
                if len(row) < 7:  # Ensure row has all columns
                    continue
                
                timestamp_str = row[0]
                operation = row[1]
                duration_ms = float(row[2]) if row[2] else 0
                status = row[3]
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Apply filters
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                if operation_filter and operation != operation_filter:
                    continue
                
                # Update overall stats
                total_duration += duration_ms
                stats["overall"]["total_operations"] += 1
                stats["overall"]["min_duration_ms"] = min(stats["overall"]["min_duration_ms"], duration_ms)
                stats["overall"]["max_duration_ms"] = max(stats["overall"]["max_duration_ms"], duration_ms)
                
                if status == "success":
                    success_count += 1
                else:
                    error_count += 1
                
                # Update operation-specific stats
                if operation not in stats["operations"]:
                    stats["operations"][operation] = {
                        "count": 0,
                        "avg_duration_ms": 0,
                        "min_duration_ms": float('inf'),
                        "max_duration_ms": 0,
                        "success_count": 0,
                        "error_count": 0
                    }
                
                op_stats = stats["operations"][operation]
                op_stats["count"] += 1
                op_stats["total_duration_ms"] = op_stats.get("total_duration_ms", 0) + duration_ms
                op_stats["min_duration_ms"] = min(op_stats["min_duration_ms"], duration_ms)
                op_stats["max_duration_ms"] = max(op_stats["max_duration_ms"], duration_ms)
                
                if status == "success":
                    op_stats["success_count"] += 1
                else:
                    op_stats["error_count"] += 1
        
        # Calculate averages and rates
        total_operations = stats["overall"]["total_operations"]
        if total_operations > 0:
            stats["overall"]["avg_duration_ms"] = total_duration / total_operations
            stats["overall"]["success_rate"] = success_count / total_operations
            stats["overall"]["error_rate"] = error_count / total_operations
            
            # Handle edge case for min duration
            if stats["overall"]["min_duration_ms"] == float('inf'):
                stats["overall"]["min_duration_ms"] = 0
        
        # Calculate operation-specific averages
        for op, op_stats in stats["operations"].items():
            if op_stats["count"] > 0:
                op_stats["avg_duration_ms"] = op_stats["total_duration_ms"] / op_stats["count"]
                
                # Handle edge case for min duration
                if op_stats["min_duration_ms"] == float('inf'):
                    op_stats["min_duration_ms"] = 0
                    
                # Remove temporary total_duration_ms field
                if "total_duration_ms" in op_stats:
                    del op_stats["total_duration_ms"]
        
        return stats
    except Exception as e:
        logger.error(f"Error getting performance statistics: {str(e)}")
        return {"error": str(e)}

def get_user_journey_analytics(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get user journey analytics from the log (Phase 2)
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        Dictionary with user journey analytics
    """
    try:
        if not os.path.exists(USER_JOURNEY_LOG_FILE):
            return {}
        
        analytics = {
            "common_paths": [],
            "step_durations": {},
            "funnel_progression": {},
            "drop_off_points": {},
            "session_counts": {}
        }
        
        # Collect all journey steps and paths
        all_steps = set()
        step_durations = {}
        user_paths = {}
        
        with open(USER_JOURNEY_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            
            for row in reader:
                if len(row) < 7:  # Ensure row has minimum columns
                    continue
                
                current_user_id = row[1]
                session_id = row[2]
                journey_step = row[3]
                previous_step = row[4] if row[4] else None
                step_duration = float(row[6]) if row[6] else None
                
                # Apply user filter if needed
                if user_id and current_user_id != user_id:
                    continue
                
                # Track unique steps
                all_steps.add(journey_step)
                if previous_step:
                    all_steps.add(previous_step)
                
                # Track step durations
                if journey_step not in step_durations:
                    step_durations[journey_step] = {
                        "total_duration": 0,
                        "count": 0,
                        "min_duration": float('inf'),
                        "max_duration": 0
                    }
                
                if step_duration is not None and step_duration > 0:
                    step_durations[journey_step]["total_duration"] += step_duration
                    step_durations[journey_step]["count"] += 1
                    step_durations[journey_step]["min_duration"] = min(
                        step_durations[journey_step]["min_duration"], 
                        step_duration
                    )
                    step_durations[journey_step]["max_duration"] = max(
                        step_durations[journey_step]["max_duration"], 
                        step_duration
                    )
                
                # Track paths
                if previous_step:
                    path_key = f"{previous_step} -> {journey_step}"
                    if path_key not in analytics["funnel_progression"]:
                        analytics["funnel_progression"][path_key] = 0
                    analytics["funnel_progression"][path_key] += 1
                
                # Track user paths
                user_session_key = f"{current_user_id}:{session_id}"
                if user_session_key not in user_paths:
                    user_paths[user_session_key] = []
                user_paths[user_session_key].append(journey_step)
                
                # Track session counts
                if session_id not in analytics["session_counts"]:
                    analytics["session_counts"][session_id] = 0
                analytics["session_counts"][session_id] += 1
        
        # Calculate common paths
        path_counts = {}
        for path_list in user_paths.values():
            for i in range(len(path_list) - 1):
                path = f"{path_list[i]} -> {path_list[i+1]}"
                if path not in path_counts:
                    path_counts[path] = 0
                path_counts[path] += 1
        
        # Sort paths by frequency
        sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)
        analytics["common_paths"] = [{"path": path, "count": count} for path, count in sorted_paths[:10]]
        
        # Calculate step durations averages
        for step, stats in step_durations.items():
            if stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]
                
                # Handle edge case for min duration
                if stats["min_duration"] == float('inf'):
                    stats["min_duration"] = 0
                    
                # Remove temporary total_duration field
                if "total_duration" in stats:
                    del stats["total_duration"]
                    
        analytics["step_durations"] = step_durations
        
        # Calculate drop-off points
        step_entry_counts = {step: 0 for step in all_steps}
        step_exit_counts = {step: 0 for step in all_steps}
        
        for path_list in user_paths.values():
            if path_list:
                step_entry_counts[path_list[0]] += 1
                step_exit_counts[path_list[-1]] += 1
        
        for step in all_steps:
            entry_count = step_entry_counts.get(step, 0)
            exit_count = step_exit_counts.get(step, 0)
            if entry_count > 0 and exit_count > 0:
                drop_off_rate = exit_count / (exit_count + entry_count)
                analytics["drop_off_points"][step] = {
                    "entry_count": entry_count,
                    "exit_count": exit_count,
                    "drop_off_rate": drop_off_rate
                }
        
        return analytics
    except Exception as e:
        logger.error(f"Error getting user journey analytics: {str(e)}")
        return {"error": str(e)}

def get_session_statistics(start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get session statistics from the log (Phase 2)
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Dictionary with session statistics
    """
    try:
        if not os.path.exists(SESSION_LOG_FILE):
            return {}
        
        stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "avg_duration_seconds": 0,
            "avg_interactions": 0,
            "platform_breakdown": {},
            "browser_breakdown": {},
            "language_breakdown": {},
            "session_trend": []
        }
        
        sessions = []
        total_duration = 0
        total_interactions = 0
        
        # Read all sessions
        with open(SESSION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            
            for row in reader:
                if len(row) < 9:  # Ensure row has all expected columns
                    continue
                
                session_id = row[0]
                user_id = row[1]
                start_time_str = row[2]
                end_time_str = row[3]
                duration_seconds = float(row[4]) if row[4] else None
                interaction_count = int(row[5]) if row[5] else 0
                platform = row[6]
                browser = row[7]
                language = row[8]
                
                # Parse timestamps
                start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
                end_time = datetime.fromisoformat(end_time_str) if end_time_str else None
                
                # Apply date filters
                if start_date and start_time and start_time < start_date:
                    continue
                if end_date and start_time and start_time > end_date:
                    continue
                
                # Create session object
                session = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_seconds": duration_seconds,
                    "interaction_count": interaction_count,
                    "platform": platform,
                    "browser": browser,
                    "language": language,
                    "is_active": end_time is None
                }
                
                sessions.append(session)
        
        # Calculate statistics
        stats["total_sessions"] = len(sessions)
        stats["active_sessions"] = sum(1 for s in sessions if s["is_active"])
        stats["completed_sessions"] = sum(1 for s in sessions if not s["is_active"])
        
        # Duration and interaction stats
        completed_sessions = [s for s in sessions if not s["is_active"] and s["duration_seconds"] is not None]
        if completed_sessions:
            total_duration = sum(s["duration_seconds"] for s in completed_sessions)
            stats["avg_duration_seconds"] = total_duration / len(completed_sessions)
        
        sessions_with_interactions = [s for s in sessions if s["interaction_count"] > 0]
        if sessions_with_interactions:
            total_interactions = sum(s["interaction_count"] for s in sessions_with_interactions)
            stats["avg_interactions"] = total_interactions / len(sessions_with_interactions)
        
        # Platform breakdown
        platform_counts = {}
        for session in sessions:
            platform = session["platform"]
            if platform not in platform_counts:
                platform_counts[platform] = 0
            platform_counts[platform] += 1
        stats["platform_breakdown"] = platform_counts
        
        # Browser breakdown
        browser_counts = {}
        for session in sessions:
            browser = session["browser"]
            if browser not in browser_counts:
                browser_counts[browser] = 0
            browser_counts[browser] += 1
        stats["browser_breakdown"] = browser_counts
        
        # Language breakdown
        language_counts = {}
        for session in sessions:
            language = session["language"]
            if language not in language_counts:
                language_counts[language] = 0
            language_counts[language] += 1
        stats["language_breakdown"] = language_counts
        
        # Session trend (group by day)
        sessions_by_day = {}
        for session in sessions:
            if session["start_time"]:
                day_key = session["start_time"].strftime("%Y-%m-%d")
                if day_key not in sessions_by_day:
                    sessions_by_day[day_key] = 0
                sessions_by_day[day_key] += 1
        
        stats["session_trend"] = [
            {"date": day, "count": count} 
            for day, count in sorted(sessions_by_day.items())
        ]
        
        return stats
    except Exception as e:
        logger.error(f"Error getting session statistics: {str(e)}")
        return {"error": str(e)}

def clear_logs() -> bool:
    """
    Clear all logs
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Reset interaction log
        if os.path.exists(INTERACTION_LOG_FILE):
            with open(INTERACTION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 
                    'user_input', 
                    'emotion', 
                    'action', 
                    'params',
                    'language'
                ])
        
        # Reset session log
        if os.path.exists(SESSION_LOG_FILE):
            with open(SESSION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_id',
                    'user_id',
                    'start_time',
                    'end_time',
                    'duration_seconds',
                    'interaction_count',
                    'platform',
                    'browser',
                    'language'
                ])
        
        # Reset performance log
        if os.path.exists(PERFORMANCE_LOG_FILE):
            with open(PERFORMANCE_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'operation',
                    'duration_ms',
                    'status',
                    'error_message',
                    'memory_usage_mb',
                    'cpu_usage_percent'
                ])
        
        # Reset event log
        if os.path.exists(EVENT_LOG_FILE):
            with open(EVENT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # Reset user journey log
        if os.path.exists(USER_JOURNEY_LOG_FILE):
            with open(USER_JOURNEY_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'user_id',
                    'session_id',
                    'journey_step',
                    'previous_step',
                    'next_step',
                    'step_duration_ms',
                    'user_feedback'
                ])
            
        logger.info("All logs cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return False
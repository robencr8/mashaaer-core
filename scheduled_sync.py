import os
import sys
import logging
import subprocess
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduled_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScheduledSync")

def check_rclone():
    """Check if rclone is available"""
    rclone_path = "./rclone"
    
    if not os.path.exists(rclone_path):
        logger.error(f"rclone not found at {rclone_path}")
        return False
        
    try:
        result = subprocess.run([rclone_path, "version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"rclone found: {result.stdout.splitlines()[0]}")
            return True
        else:
            logger.error(f"rclone execution failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error checking rclone: {e}")
        return False

def check_config():
    """Check if rclone config exists"""
    config_path = "rclone.conf"
    
    if os.path.exists(config_path):
        logger.info(f"rclone config found at {config_path}")
        return True
    else:
        logger.error(f"rclone config not found at {config_path}")
        return False

def run_sync():
    """Run the sync script"""
    sync_script = "rclone_sync.py"
    
    if not os.path.exists(sync_script):
        logger.error(f"Sync script not found at {sync_script}")
        return False
        
    try:
        logger.info(f"Running sync script: {sync_script}")
        result = subprocess.run([sys.executable, sync_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Sync completed successfully")
            return True
        else:
            logger.error(f"Sync failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running sync script: {e}")
        return False

def send_notification(success, log_file=None):
    """Send a notification about the sync result"""
    # This function can be expanded to send email, SMS, or other notifications
    status = "SUCCESS" if success else "FAILURE"
    message = f"Mashaaer Sync {status}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    logger.info(f"Notification: {message}")
    
    # Example: Write to a notification file
    with open("sync_notification.txt", "a") as f:
        f.write(f"{message}\n")
        if log_file:
            f.write(f"Log file: {log_file}\n")

def main():
    """Main function for scheduled sync"""
    parser = argparse.ArgumentParser(description="Scheduled sync to Google Drive")
    parser.add_argument("--notify", action="store_true", help="Send notification about sync result")
    args = parser.parse_args()
    
    logger.info("Starting scheduled sync")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"scheduled_sync_{timestamp}.log"
    
    # Redirect log to a timestamped file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Check prerequisites
    if not check_rclone():
        logger.error("rclone check failed, aborting sync")
        if args.notify:
            send_notification(False, log_file)
        return 1
        
    if not check_config():
        logger.error("config check failed, aborting sync")
        if args.notify:
            send_notification(False, log_file)
        return 1
    
    # Run sync
    success = run_sync()
    
    # Send notification if requested
    if args.notify:
        send_notification(success, log_file)
    
    logger.info(f"Scheduled sync completed with {'success' if success else 'failure'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
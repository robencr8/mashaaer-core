import os
import subprocess
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rclone_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Mashaaer-Sync")

# Configuration
GOOGLE_DRIVE_FOLDER_ID = "1wUodMcwES79gB18uul2xACChciO-X2Um"  # Roben's Google Drive folder ID
PROJECT_NAME = "مشاعر | Mashaaer"
RCLONE_CONFIG_PATH = "rclone.conf"
SOURCE_DIR = "."  # Current directory
EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__/**",
    ".git/**",
    "*.log",
    "*.db",
    "venv/**",
    ".env",
    "rclone.conf",
    "rclone_sync.log",
    "android/.buildozer/**",
    "android/bin/**",
    "voice_logs/**",
    "logs/**",
    "temp/**"
]

def create_rclone_config():
    """Create a basic rclone config for Google Drive"""
    if os.path.exists(RCLONE_CONFIG_PATH):
        logger.info(f"Config file {RCLONE_CONFIG_PATH} already exists")
        return
    
    config_content = """
[googledrive]
type = drive
scope = drive
root_folder_id = {folder_id}
""".format(folder_id=GOOGLE_DRIVE_FOLDER_ID)
    
    with open(RCLONE_CONFIG_PATH, "w") as f:
        f.write(config_content.strip())
    
    logger.info(f"Created rclone config at {RCLONE_CONFIG_PATH}")

def create_exclude_file():
    """Create a file with patterns to exclude from sync"""
    exclude_file = "exclude.txt"
    with open(exclude_file, "w") as f:
        for pattern in EXCLUDE_PATTERNS:
            f.write(f"{pattern}\n")
    
    logger.info(f"Created exclude file with {len(EXCLUDE_PATTERNS)} patterns")
    return exclude_file

def check_remote_folder():
    """Check if the destination folder exists on Google Drive"""
    try:
        cmd = [
            "./rclone", 
            "--config", RCLONE_CONFIG_PATH,
            "lsf", 
            "googledrive:",
            "--format", "json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to list remote folders: {result.stderr}")
            return False
        
        folders = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    item = json.loads(line)
                    if item.get("IsDir", False):
                        folders.append(item.get("Name"))
                except json.JSONDecodeError:
                    pass
        
        logger.info(f"Found {len(folders)} folders on Google Drive: {folders}")
        
        if PROJECT_NAME in folders:
            logger.info(f"Found existing project folder: {PROJECT_NAME}")
            return True
        else:
            logger.info(f"Project folder not found, will create: {PROJECT_NAME}")
            return False
    
    except Exception as e:
        logger.error(f"Error checking remote folder: {e}")
        return False

def create_remote_folder():
    """Create the project folder on Google Drive if it doesn't exist"""
    try:
        cmd = [
            "./rclone", 
            "--config", RCLONE_CONFIG_PATH,
            "mkdir", 
            f"googledrive:{PROJECT_NAME}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Created folder: {PROJECT_NAME}")
            return True
        else:
            logger.error(f"Failed to create folder: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error creating remote folder: {e}")
        return False

def sync_to_google_drive():
    """Sync the project to Google Drive"""
    exclude_file = create_exclude_file()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"rclone_sync_{timestamp}.log"
    
    try:
        cmd = [
            "./rclone",
            "--config", RCLONE_CONFIG_PATH,
            "sync",
            SOURCE_DIR,  
            f"googledrive:{PROJECT_NAME}",
            "--exclude-from", exclude_file,
            "--progress",
            "-v"
        ]
        
        logger.info(f"Starting sync with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        with open(log_file, "w") as f:
            f.write(result.stdout)
            f.write("\n\nERRORS:\n")
            f.write(result.stderr)
        
        if result.returncode == 0:
            logger.info(f"Sync completed successfully. Log saved to {log_file}")
            return True
        else:
            logger.error(f"Sync failed with code {result.returncode}. Check {log_file} for details")
            logger.error(f"Error: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error during sync: {e}")
        return False

def main():
    """Main function to run the sync process"""
    logger.info(f"Starting sync to Google Drive folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
    
    # Create rclone config file
    create_rclone_config()
    
    # Check if folder exists on Google Drive
    if not check_remote_folder():
        # Create folder if it doesn't exist
        if not create_remote_folder():
            logger.error("Failed to create remote folder, aborting sync")
            return
    
    # Run the sync
    if sync_to_google_drive():
        logger.info("Sync completed successfully")
    else:
        logger.error("Sync failed")

if __name__ == "__main__":
    main()
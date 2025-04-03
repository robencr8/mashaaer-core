import os
import json
import logging
import argparse
from datetime import datetime
from rclone_sync import (
    logger, 
    GOOGLE_DRIVE_FOLDER_ID,
    PROJECT_NAME,
    RCLONE_CONFIG_PATH,
    create_rclone_config, 
    check_remote_folder, 
    create_remote_folder,
    create_exclude_file
)

# Configure specific version sync logging
version_logger = logging.getLogger("Mashaaer-Version-Sync")

def get_version_info():
    """Get the current version information or create it if it doesn't exist"""
    version_file = "version.json"
    
    if os.path.exists(version_file):
        try:
            with open(version_file, "r") as f:
                version_data = json.load(f)
                version_logger.info(f"Loaded version info: {version_data}")
                return version_data
        except json.JSONDecodeError:
            version_logger.warning(f"Version file {version_file} exists but is not valid JSON")
    
    # Create a default version file if it doesn't exist or is invalid
    version_data = {
        "major": 1,
        "minor": 0,
        "patch": 0,
        "last_updated": datetime.now().isoformat(),
        "update_history": []
    }
    
    with open(version_file, "w") as f:
        json.dump(version_data, f, indent=2)
    
    version_logger.info(f"Created new version file with data: {version_data}")
    return version_data

def update_version(increment_type="patch", version_note=""):
    """Update the version according to semantic versioning"""
    version_data = get_version_info()
    
    # Record the previous version
    previous_version = f"{version_data['major']}.{version_data['minor']}.{version_data['patch']}"
    
    # Increment the appropriate version component
    if increment_type == "major":
        version_data["major"] += 1
        version_data["minor"] = 0
        version_data["patch"] = 0
    elif increment_type == "minor":
        version_data["minor"] += 1
        version_data["patch"] = 0
    else:  # patch by default
        version_data["patch"] += 1
    
    # Update timestamp
    version_data["last_updated"] = datetime.now().isoformat()
    
    # Add to update history
    version_data["update_history"].append({
        "version": f"{version_data['major']}.{version_data['minor']}.{version_data['patch']}",
        "date": version_data["last_updated"],
        "type": increment_type,
        "note": version_note
    })
    
    # Save the updated version info
    with open("version.json", "w") as f:
        json.dump(version_data, f, indent=2)
    
    new_version = f"{version_data['major']}.{version_data['minor']}.{version_data['patch']}"
    version_logger.info(f"Updated version from {previous_version} to {new_version}")
    return new_version

def sync_versioned_project(version, note=""):
    """Sync the project to Google Drive with version information"""
    # Format the folder name with version number
    versioned_folder = f"{PROJECT_NAME} v{version}"
    
    # Create a timestamped folder name for this specific sync
    timestamp = datetime.now().strftime("%Y%m%d")
    sync_folder = f"{versioned_folder} - {timestamp}"
    
    exclude_file = create_exclude_file()
    log_file = f"rclone_sync_v{version}_{timestamp}.log"
    
    version_logger.info(f"Syncing project to versioned folder: {sync_folder}")
    
    try:
        import subprocess
        
        # First create the folder if it doesn't exist
        mkdir_cmd = [
            "./rclone",
            "--config", RCLONE_CONFIG_PATH,
            "mkdir",
            f"googledrive:{sync_folder}"
        ]
        
        subprocess.run(mkdir_cmd, check=True)
        version_logger.info(f"Created destination folder: {sync_folder}")
        
        # Then sync the files
        cmd = [
            "./rclone",
            "--config", RCLONE_CONFIG_PATH,
            "sync",
            ".",  # Current directory
            f"googledrive:{sync_folder}",
            "--exclude-from", exclude_file,
            "--progress",
            "-v"
        ]
        
        version_logger.info(f"Starting sync with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        with open(log_file, "w") as f:
            f.write(result.stdout)
            f.write("\n\nERRORS:\n")
            f.write(result.stderr)
        
        if result.returncode == 0:
            version_logger.info(f"Sync completed successfully. Log saved to {log_file}")
            
            # Create a README file with sync information
            readme_content = f"""# Mashaaer | Feelings v{version}

Synced on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Version: {version}

## Sync Notes
{note}

## Contents
This is a versioned backup of the Mashaaer | Feelings project.
"""
            
            with open("VERSION_README.md", "w") as f:
                f.write(readme_content)
            
            # Upload the README file
            readme_cmd = [
                "./rclone",
                "--config", RCLONE_CONFIG_PATH,
                "copy",
                "VERSION_README.md",
                f"googledrive:{sync_folder}/VERSION_README.md"
            ]
            
            subprocess.run(readme_cmd, check=True)
            version_logger.info("Uploaded VERSION_README.md with sync information")
            
            return True
        else:
            version_logger.error(f"Sync failed with code {result.returncode}. Check {log_file} for details")
            version_logger.error(f"Error: {result.stderr}")
            return False
    
    except Exception as e:
        version_logger.error(f"Error during versioned sync: {e}")
        return False

def main():
    """Main function to handle versioned sync"""
    parser = argparse.ArgumentParser(description="Sync Mashaaer | Feelings to Google Drive with version control")
    parser.add_argument(
        "--increment", 
        choices=["major", "minor", "patch"],
        default="patch",
        help="Version increment type (default: patch)"
    )
    parser.add_argument(
        "--note",
        default="",
        help="Note about this version update"
    )
    
    args = parser.parse_args()
    
    version_logger.info(f"Starting versioned sync with increment: {args.increment}")
    
    # Create rclone config file
    create_rclone_config()
    
    # Check if base folder exists on Google Drive
    if not check_remote_folder():
        # Create folder if it doesn't exist
        if not create_remote_folder():
            version_logger.error("Failed to create remote folder, aborting sync")
            return
    
    # Update version
    new_version = update_version(args.increment, args.note)
    print(f"\n=== Updated to version {new_version} ===")
    
    # Sync with version information
    if sync_versioned_project(new_version, args.note):
        print(f"\n=== Successfully synced version {new_version} to Google Drive ===")
        print(f"Sync notes: {args.note}")
    else:
        print(f"\n=== Failed to sync version {new_version} to Google Drive ===")

if __name__ == "__main__":
    main()
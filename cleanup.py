#!/usr/bin/env python
"""
Mashaaer Feelings Project Cleanup Script

This script performs final cleanup tasks before deployment:
1. Removes test/diagnostic routes from main.py 
2. Removes test HTML/template files
3. Cleans up logs and temporary files
4. Verifies essential components are present

Usage:
  python cleanup.py          # Execute all cleanup tasks
  python cleanup.py --dry-run # Show what would be done without making changes
  python cleanup.py --help   # Show help message
"""

import os
import sys
import glob
import shutil
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cleanup.log')
    ]
)

logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Mashaaer Feelings Project Cleanup')
parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
parser.add_argument('--verify-only', action='store_true', help='Only verify essential files without making changes')
args = parser.parse_args()

# Global flags
DRY_RUN = args.dry_run
VERIFY_ONLY = args.verify_only

if DRY_RUN:
    print("DRY RUN MODE: No changes will be made")
    logger.info("DRY RUN MODE: No changes will be made")

# Files to remove (test/diagnostic files)
TEST_FILES = [
    # Test HTML files
    'static/test.html',
    'static/feedback_test.html',
    'static/cors_test.html',
    'static/minimal_test.html',
    'static/test_*.html',
    'static/feedback_*.html',
    'static/cors_*.html',
    
    # Test template files
    'templates/test.html',
    'templates/feedback_test.html',
    'templates/cors_test.html',
    'templates/minimal_test.html',
    'templates/test_*.html',
    'templates/feedback_*.html',
    'templates/cors_*.html',
    
    # Test scripts
    'test_server_connectivity.py',
    'test_feedback_tool_connectivity.py',
    'standalone_minimal_server.py',
    'ultra_minimal_server.py',
    'truly_minimal_server.py',
    'minimal_flask_server.py',
    'minimal_test_server.py',
    'minimal_server.py',
    
    # Temporary log files
    '*.log.1',
    '*.log.2',
    'minimal_*.log',
    'test_*.log'
]

# Directories to clean up
CLEANUP_DIRS = [
    # Temp directories
    'temp',
    # Test cache directories
    'test_cache'
]

# Essential files to verify
ESSENTIAL_FILES = [
    'main.py',
    'config.py', 
    'emotion_tracker.py',
    'tts/tts_manager.py',
    'tts/elevenlabs.py',
    'tts/gtts_fallback.py',
    'templates/index.html',
    'templates/cosmic_onboarding.html'
]

# Files to be copied during cleanup (source -> destination)
FILES_TO_COPY = {
    'static/archive/js/app.js': 'static/js/app.js',
    'static/archive/css/style.css': 'static/css/style.css'
}

def backup_main_py():
    """Create a backup of main.py before replacing it"""
    if os.path.exists('main.py'):
        backup_file = 'main.py.pre_deployment_backup'
        try:
            shutil.copy2('main.py', backup_file)
            logger.info(f"Created backup of main.py as {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup of main.py: {str(e)}")
            return False
    else:
        logger.error("main.py not found, cannot create backup")
        return False

def replace_main_py():
    """Replace main.py with the clean version"""
    if os.path.exists('main.py.clean'):
        try:
            # Create backup first
            if backup_main_py():
                # Replace the file
                shutil.copy2('main.py.clean', 'main.py')
                logger.info("Successfully replaced main.py with clean version")
                return True
            else:
                logger.error("Skipping replacement due to backup failure")
                return False
        except Exception as e:
            logger.error(f"Failed to replace main.py: {str(e)}")
            return False
    else:
        logger.error("main.py.clean not found, cannot replace main.py")
        return False

def remove_test_files():
    """Remove test and diagnostic files"""
    removed_count = 0
    
    for pattern in TEST_FILES:
        try:
            # Expand the glob pattern
            matching_files = glob.glob(pattern)
            
            for file_path in matching_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed: {file_path}")
                    removed_count += 1
        except Exception as e:
            logger.error(f"Error removing {pattern}: {str(e)}")
    
    logger.info(f"Removed {removed_count} test files")
    return removed_count

def clean_directories():
    """Clean up temporary directories"""
    cleaned_count = 0
    
    for dir_path in CLEANUP_DIRS:
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                # Remove all files in the directory but keep the directory itself
                for file_path in glob.glob(os.path.join(dir_path, '*')):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                logger.info(f"Cleaned directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error cleaning directory {dir_path}: {str(e)}")
    
    logger.info(f"Cleaned {cleaned_count} files from directories")
    return cleaned_count

def copy_necessary_files():
    """Copy necessary files to their expected locations"""
    copied_count = 0
    
    for source, dest in FILES_TO_COPY.items():
        try:
            if os.path.exists(source):
                # Create destination directory if it doesn't exist
                dest_dir = os.path.dirname(dest)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                    logger.info(f"Created directory: {dest_dir}")
                
                # Copy the file
                shutil.copy2(source, dest)
                logger.info(f"Copied: {source} -> {dest}")
                copied_count += 1
            else:
                logger.error(f"Source file not found: {source}")
        except Exception as e:
            logger.error(f"Error copying {source} to {dest}: {str(e)}")
    
    logger.info(f"Copied {copied_count} files")
    return copied_count

def verify_essential_files():
    """Verify that essential files are present"""
    missing_files = []
    
    for file_path in ESSENTIAL_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            logger.warning(f"Missing essential file: {file_path}")
    
    if missing_files:
        logger.error(f"Missing {len(missing_files)} essential files")
        for file in missing_files:
            print(f"  - {file}")
    else:
        logger.info("All essential files are present")
    
    return missing_files

def backup_main_py_dry_run():
    """Simulate creating a backup of main.py in dry-run mode"""
    if os.path.exists('main.py'):
        backup_file = 'main.py.pre_deployment_backup'
        logger.info(f"[DRY RUN] Would create backup of main.py as {backup_file}")
        return True
    else:
        logger.error("[DRY RUN] main.py not found, cannot create backup")
        return False

def replace_main_py_dry_run():
    """Simulate replacing main.py with the clean version in dry-run mode"""
    if os.path.exists('main.py.clean'):
        if backup_main_py_dry_run():
            logger.info("[DRY RUN] Would replace main.py with clean version")
            return True
        else:
            logger.error("[DRY RUN] Skipping replacement due to backup failure")
            return False
    else:
        logger.error("[DRY RUN] main.py.clean not found, cannot replace main.py")
        return False

def remove_test_files_dry_run():
    """Simulate removing test and diagnostic files in dry-run mode"""
    would_remove_count = 0
    
    for pattern in TEST_FILES:
        try:
            matching_files = glob.glob(pattern)
            
            for file_path in matching_files:
                if os.path.exists(file_path):
                    logger.info(f"[DRY RUN] Would remove: {file_path}")
                    would_remove_count += 1
        except Exception as e:
            logger.error(f"[DRY RUN] Error checking {pattern}: {str(e)}")
    
    logger.info(f"[DRY RUN] Would remove {would_remove_count} test files")
    return would_remove_count

def clean_directories_dry_run():
    """Simulate cleaning up temporary directories in dry-run mode"""
    would_clean_count = 0
    
    for dir_path in CLEANUP_DIRS:
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                files_in_dir = glob.glob(os.path.join(dir_path, '*'))
                for file_path in files_in_dir:
                    if os.path.isfile(file_path):
                        logger.info(f"[DRY RUN] Would remove: {file_path}")
                        would_clean_count += 1
                logger.info(f"[DRY RUN] Would clean directory: {dir_path}")
        except Exception as e:
            logger.error(f"[DRY RUN] Error checking directory {dir_path}: {str(e)}")
    
    logger.info(f"[DRY RUN] Would clean {would_clean_count} files from directories")
    return would_clean_count

def copy_necessary_files_dry_run():
    """Simulate copying necessary files to their expected locations in dry-run mode"""
    would_copy_count = 0
    
    for source, dest in FILES_TO_COPY.items():
        try:
            if os.path.exists(source):
                dest_dir = os.path.dirname(dest)
                if not os.path.exists(dest_dir):
                    logger.info(f"[DRY RUN] Would create directory: {dest_dir}")
                logger.info(f"[DRY RUN] Would copy: {source} -> {dest}")
                would_copy_count += 1
            else:
                logger.error(f"[DRY RUN] Source file not found: {source}")
        except Exception as e:
            logger.error(f"[DRY RUN] Error checking {source}: {str(e)}")
    
    logger.info(f"[DRY RUN] Would copy {would_copy_count} files")
    return would_copy_count

def main():
    """Main cleanup function"""
    if VERIFY_ONLY:
        print("VERIFY ONLY MODE: Only verifying essential files without making changes")
        logger.info("VERIFY ONLY MODE: Only verifying essential files without making changes")
        
        # Just run verification
        print("\nVerifying essential files")
        missing_files = verify_essential_files()
        if missing_files:
            print(f"❌ Missing {len(missing_files)} essential files")
        else:
            print("✅ All essential files are present")
        
        print("\nVerification completed!")
        logger.info("Verification completed")
        return
    
    print("Starting Mashaaer Feelings project cleanup...")
    logger.info("Starting cleanup process")
    
    # Step 1: Replace main.py with clean version
    print("\nStep 1: Replacing main.py with clean version")
    if DRY_RUN:
        if replace_main_py_dry_run():
            print("[DRY RUN] ✓ Would replace main.py with clean version")
        else:
            print("[DRY RUN] ✗ Would not be able to replace main.py")
    else:
        if replace_main_py():
            print("✅ Successfully replaced main.py")
        else:
            print("❌ Failed to replace main.py")
    
    # Step 2: Remove test files
    print("\nStep 2: Removing test and diagnostic files")
    if DRY_RUN:
        would_remove_count = remove_test_files_dry_run()
        print(f"[DRY RUN] ✓ Would remove {would_remove_count} test files")
    else:
        removed_count = remove_test_files()
        print(f"✅ Removed {removed_count} test files")
    
    # Step 3: Clean directories
    print("\nStep 3: Cleaning temporary directories")
    if DRY_RUN:
        would_clean_count = clean_directories_dry_run()
        print(f"[DRY RUN] ✓ Would clean {would_clean_count} files from temporary directories")
    else:
        cleaned_count = clean_directories()
        print(f"✅ Cleaned {cleaned_count} files from temporary directories")
    
    # Step 4: Copy necessary files
    print("\nStep 4: Copying necessary files")
    if DRY_RUN:
        would_copy_count = copy_necessary_files_dry_run()
        print(f"[DRY RUN] ✓ Would copy {would_copy_count} files to their expected locations")
    else:
        copied_count = copy_necessary_files()
        print(f"✅ Copied {copied_count} files to their expected locations")
    
    # Step 5: Verify essential files
    print("\nStep 5: Verifying essential files")
    missing_files = verify_essential_files()
    if missing_files:
        print(f"❌ Missing {len(missing_files)} essential files (see log for details)")
    else:
        print("✅ All essential files are present")
    
    if DRY_RUN:
        print("\n[DRY RUN] Cleanup simulation completed! No actual changes were made.")
        logger.info("[DRY RUN] Cleanup simulation completed")
    else:
        print("\nCleanup process completed!")
        logger.info("Cleanup process completed")

if __name__ == "__main__":
    main()
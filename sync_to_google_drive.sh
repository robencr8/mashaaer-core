#!/bin/bash

# Sync "Mashaaer | Feelings" to Roben's Google Drive
echo "====== Syncing Mashaaer | Feelings to Google Drive ======"
echo "Starting sync process at $(date)"

# Check if rclone config exists
if [ ! -f rclone.conf ]; then
    echo "Rclone config not found. Setting up Google Drive authentication..."
    python setup_google_drive.py
    
    # Check if setup was successful
    if [ ! -f rclone.conf ]; then
        echo "Failed to set up Google Drive. Exiting."
        exit 1
    fi
fi

# Run the sync script
echo "Starting sync to Google Drive..."
python rclone_sync.py

echo "Sync process completed at $(date)"
echo "======================================================"
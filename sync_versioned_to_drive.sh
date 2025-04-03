#!/bin/bash

# Sync "Mashaaer | Feelings" to Roben's Google Drive with version control
echo "====== Versioned Sync of Mashaaer | Feelings to Google Drive ======"
echo "Starting versioned sync process at $(date)"

# Check if rclone exists and is executable
if [ ! -f "./rclone" ] || [ ! -x "./rclone" ]; then
    echo "Rclone not found or not executable. Extracting from archive..."
    
    # Check if we have the rclone archive
    if [ -f "./rclone-v1.69.1-linux-amd64.zip" ]; then
        unzip -o ./rclone-v1.69.1-linux-amd64.zip
        chmod +x ./rclone-v1.69.1-linux-amd64/rclone
        cp ./rclone-v1.69.1-linux-amd64/rclone ./rclone
        chmod +x ./rclone
    elif [ -d "./rclone-v1.69.1-linux-amd64" ]; then
        cp ./rclone-v1.69.1-linux-amd64/rclone ./rclone
        chmod +x ./rclone
    else
        echo "Rclone archive not found. Please download it first."
        exit 1
    fi
fi

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

# Get version increment type and note from arguments
INCREMENT="patch"  # Default to patch
NOTE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --major)
            INCREMENT="major"
            shift
            ;;
        --minor)
            INCREMENT="minor"
            shift
            ;;
        --patch)
            INCREMENT="patch"
            shift
            ;;
        --note)
            NOTE="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            shift
            ;;
    esac
done

# If no note was provided, prompt for one
if [ -z "$NOTE" ]; then
    echo "Please enter a brief note about this version update:"
    read -r NOTE
fi

# Run the versioned sync script
echo "Starting versioned sync to Google Drive..."
python sync_version.py --increment $INCREMENT --note "$NOTE"

echo "Versioned sync process completed at $(date)"
echo "======================================================"
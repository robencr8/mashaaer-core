# Google Drive Sync for Mashaaer | Feelings

This document outlines the process for syncing the "مشاعر | Mashaaer" project to Roben Edwan's Google Drive.

## Version-Based Sync (New Feature)

For version-controlled sync with automatic versioning:

1. Run the versioned sync script: `./sync_versioned_to_drive.sh`
2. Specify the version increment:
   - `./sync_versioned_to_drive.sh --major` (for major version changes)
   - `./sync_versioned_to_drive.sh --minor` (for feature additions)
   - `./sync_versioned_to_drive.sh --patch` (for bug fixes, default)
3. Add a note about the update: `./sync_versioned_to_drive.sh --note "Added voice features"`
4. Follow authentication instructions if needed

This creates a new folder with the version number and date (e.g., "مشاعر | Mashaaer v1.2.3 - 20250403")

## Prerequisites

- An internet connection
- Google account access (for authentication)
- The project files ready to be synced

## Setup and Sync Process

### One-Time Setup

The first time you sync, you'll need to authenticate with Google Drive:

1. Run the sync script: `./sync_to_google_drive.sh`
2. Follow the on-screen instructions for authentication
3. When prompted, log in to the appropriate Google account
4. Grant permission for rclone to access your Google Drive
5. The authentication will be saved for future use

### Regular Syncing

After the initial setup, syncing is straightforward:

1. Simply run: `./sync_to_google_drive.sh`
2. The script will automatically:
   - Check for an existing configuration
   - Verify the destination folder exists
   - Sync all project files while excluding unnecessary files (logs, cache, etc.)
   - Log the sync operations

## What Gets Synced

The sync process includes most project files while excluding:

- Python cache files (`*.pyc`, `__pycache__/*`)
- Git repository files (`.git/*`)
- Log files (`*.log`)
- Database files (`*.db`)
- Virtual environment (`venv/*`)
- Environment configuration (`.env`)
- Android build artifacts (`android/.buildozer/*`, `android/bin/*`)
- Temporary files and logs (`voice_logs/*`, `logs/*`, `temp/*`)

## Destination

Files are synced to a folder named "Mashaaer | Feelings" in Roben's Google Drive folder (ID: 1wUodMcwES79gB18uul2xACChciO-X2Um).

## Troubleshooting

If you encounter issues:

1. Check the log files:
   - `rclone_sync.log`: General sync log
   - `rclone_sync_YYYYMMDD_HHMMSS.log`: Detailed log for a specific sync operation
   - `google_drive_setup.log`: Authentication setup log

2. Common issues:
   - Authentication failures: Run `python setup_google_drive.py` to re-authenticate
   - Connection problems: Verify your internet connection
   - Permission issues: Ensure you're logged into the correct Google account

## Manual Sync

If needed, you can manually run the sync with:

```
python rclone_sync.py
```

This will use the existing configuration but allow you to monitor the process in real-time.
#!/bin/bash
# Script to build the Android APK for Mashaaer Feelings

echo "===== Building Mashaaer Feelings APK ====="
echo "This script will build the Android APK using buildozer."

# Make the script exit on any errors
set -e

# Ensure we're in the right directory
cd "$(dirname "$0")"
echo "Working in directory: $(pwd)"

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Buildozer not found. Installing buildozer..."
    pip install --user buildozer
    
    # Check if installation was successful
    if ! command -v buildozer &> /dev/null; then
        echo "Failed to install buildozer. Please install it manually."
        exit 1
    fi
fi

# Check for required build dependencies
echo "Checking build dependencies..."
MISSING_DEPS=0

# Check for Java
if ! command -v java &> /dev/null; then
    echo "Java JDK not found. Required for Android build."
    MISSING_DEPS=1
fi

# Check for Android build tools (optional, buildozer can download them)
if [ ! -d "$HOME/.buildozer/android/platform/android-sdk" ]; then
    echo "Note: Android SDK not found locally. Buildozer will download it."
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo "Please install the missing dependencies and try again."
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf .buildozer bin || true

# Run buildozer
echo "Building APK with buildozer..."
buildozer -v android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "===== Build Successful! ====="
    echo "APK file is located in: $(pwd)/bin/"
    ls -lh bin/
else
    echo "===== Build Failed! ====="
    echo "Please check the logs for errors."
    exit 1
fi
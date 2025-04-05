"""
Generate Emotion-Specific Cosmic Ambient Tracks for Mashaaer

This script creates a set of emotion-specific cosmic ambient tracks:
- sad_cosmic.mp3
- happy_cosmic.mp3
- angry_cosmic.mp3
- calm_cosmic.mp3

These tracks will be used by the auto-switching ambient sound engine.
"""

import os
import logging
from generate_sad_cosmic import generate_sad_cosmic_track
from generate_happy_cosmic import generate_happy_cosmic_track
from generate_angry_cosmic import generate_angry_cosmic_track
from generate_calm_cosmic import generate_calm_cosmic_track

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_emotion_tracks():
    """Generate cosmic ambient tracks for each emotion and save to destination"""
    
    logger.info("Starting generation of emotion-specific cosmic ambient tracks...")
    
    # Create destination directory if it doesn't exist
    destination_dir = "static/mobile/audio"
    os.makedirs(destination_dir, exist_ok=True)
    
    # Generate sad cosmic track
    sad_track = generate_sad_cosmic_track()
    if sad_track:
        logger.info(f"Successfully generated sad cosmic track: {sad_track}")
    else:
        logger.error("Failed to generate sad cosmic track")
    
    # Generate happy cosmic track
    happy_track = generate_happy_cosmic_track()
    if happy_track:
        logger.info(f"Successfully generated happy cosmic track: {happy_track}")
    else:
        logger.error("Failed to generate happy cosmic track")
    
    # Generate angry cosmic track
    angry_track = generate_angry_cosmic_track()
    if angry_track:
        logger.info(f"Successfully generated angry cosmic track: {angry_track}")
    else:
        logger.error("Failed to generate angry cosmic track")
    
    # Generate calm cosmic track
    calm_track = generate_calm_cosmic_track()
    if calm_track:
        logger.info(f"Successfully generated calm cosmic track: {calm_track}")
    else:
        logger.error("Failed to generate calm cosmic track")
    
    # Check if all tracks were generated successfully
    tracks = [
        os.path.join(destination_dir, "sad_cosmic.mp3"),
        os.path.join(destination_dir, "happy_cosmic.mp3"),
        os.path.join(destination_dir, "angry_cosmic.mp3"),
        os.path.join(destination_dir, "calm_cosmic.mp3")
    ]
    
    missing_tracks = [track for track in tracks if not os.path.exists(track)]
    
    if missing_tracks:
        logger.warning(f"Missing tracks: {missing_tracks}")
        return False
    else:
        logger.info("All emotion-specific cosmic ambient tracks generated successfully")
        return True

if __name__ == "__main__":
    success = generate_emotion_tracks()
    if success:
        print("✅ All emotion-specific cosmic ambient tracks generated successfully")
    else:
        print("❌ Failed to generate some emotion-specific cosmic ambient tracks")
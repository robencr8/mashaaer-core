"""
Generate a peaceful cosmic ambient track for Mashaaer
This script creates a custom cosmic ambient track using the CosmicSoundscapeGenerator
"""

import os
import logging
from cosmic_soundscape import cosmic_soundscape_generator, CosmicSoundscapeGenerator
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_cosmic_music():
    """Generate a peaceful cosmic ambient track and save to destination"""
    
    # Initialize generator if not already done
    if cosmic_soundscape_generator is None:
        logger.info("Initializing Cosmic Soundscape Generator")
        generator = CosmicSoundscapeGenerator()
    else:
        generator = cosmic_soundscape_generator
        
    # Output directory for generated file
    output_dir = "static/cosmic_sounds"
    destination_dir = "static/mobile/audio"
    output_filename = "cosmicmusic.wav"  # Will be converted to MP3 by the generator
    
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Generate a peaceful cosmic ambient track (10 seconds - shorter for faster generation)
    logger.info("Generating peaceful cosmic ambient track...")
    _, output_path = generator.generate_cosmic_soundscape(
        duration=10.0,
        mood="peaceful",
        layers=2,  # Using fewer layers for faster generation
        output_filename=output_filename
    )
    
    if output_path and os.path.exists(output_path):
        # The generator should have created an MP3 version
        mp3_path = output_path.replace('.wav', '.mp3')
        
        if os.path.exists(mp3_path):
            # Copy to destination
            destination_file = os.path.join(destination_dir, "cosmicmusic.mp3")
            shutil.copy2(mp3_path, destination_file)
            logger.info(f"Cosmic ambient track created and copied to {destination_file}")
            return destination_file
        else:
            logger.warning(f"MP3 file not found at {mp3_path}")
    else:
        logger.error("Failed to generate cosmic ambient track")
    
    return None

if __name__ == "__main__":
    output_file = generate_cosmic_music()
    if output_file:
        print(f"Successfully created cosmic ambient track: {output_file}")
    else:
        print("Failed to create cosmic ambient track")
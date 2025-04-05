"""
Generate Sad Cosmic Ambient Track for Mashaaer
"""

import os
import logging
import shutil
from cosmic_soundscape import cosmic_soundscape_generator, CosmicSoundscapeGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sad_cosmic_track():
    """Generate sad cosmic ambient track and save to destination"""
    
    # Initialize generator if not already done
    if cosmic_soundscape_generator is None:
        logger.info("Initializing Cosmic Soundscape Generator")
        generator = CosmicSoundscapeGenerator()
    else:
        generator = cosmic_soundscape_generator
        
    # Output directory for generated file
    output_dir = "static/cosmic_sounds"
    destination_dir = "static/mobile/audio"
    
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Sad emotion parameters
    emotion = "sad"
    output_filename = f"{emotion}_cosmic.wav"
    
    logger.info(f"Generating {emotion} cosmic ambient track...")
    
    try:
        # Generate the cosmic soundscape with emotion-specific parameters
        _, output_path = generator.generate_cosmic_soundscape(
            duration=8.0,  # shorter duration for faster generation
            mood="melancholic",
            layers=2,  # fewer layers for faster generation
            output_filename=output_filename
        )
        
        if output_path and os.path.exists(output_path):
            # The generator should have created an MP3 version
            mp3_path = output_path.replace('.wav', '.mp3')
            
            if os.path.exists(mp3_path):
                # Copy to destination
                destination_file = os.path.join(destination_dir, f"{emotion}_cosmic.mp3")
                shutil.copy2(mp3_path, destination_file)
                logger.info(f"{emotion.capitalize()} cosmic ambient track created and copied to {destination_file}")
                return destination_file
            else:
                logger.warning(f"MP3 file not found at {mp3_path}")
        else:
            logger.error(f"Failed to generate {emotion} cosmic ambient track")
            
    except Exception as e:
        logger.error(f"Error generating {emotion} cosmic track: {str(e)}")
    
    return None

if __name__ == "__main__":
    output_file = generate_sad_cosmic_track()
    if output_file:
        print(f"Successfully created sad cosmic track: {output_file}")
    else:
        print("Failed to create sad cosmic track")
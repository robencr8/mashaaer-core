"""
Cosmic Soundscape Generator for Mashaaer

This module provides functionality to generate cosmic ambient sounds
based on specified parameters. It creates layered audio compositions
that can be used for background ambience, transitions, and interactive
elements in the Mashaaer application.
"""

import os
import logging
import numpy as np
import time
import math
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from scipy.io import wavfile
from pydub import AudioSegment

# Configure logging
logger = logging.getLogger(__name__)

class CosmicSoundscapeGenerator:
    """
    Generates cosmic ambient soundscapes using synthesis techniques.
    
    This class provides methods to create various cosmic sounds including
    ambient drones, shimmering textures, evolving pads, and cosmic effects.
    """
    
    def __init__(self, output_dir: str = "static/cosmic_sounds"):
        """
        Initialize the cosmic soundscape generator.
        
        Args:
            output_dir: Directory to save generated soundscapes
        """
        self.output_dir = output_dir
        self.ensure_output_directory()
        self.sample_rate = 44100  # Standard CD quality
        logger.info(f"Cosmic Soundscape Generator initialized with output directory: {output_dir}")
        
    def ensure_output_directory(self) -> None:
        """Ensure the output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def generate_sine_tone(self, 
                          frequency: float,
                          duration: float,
                          amplitude: float = 0.5,
                          fade_in: float = 0.1,
                          fade_out: float = 0.1) -> np.ndarray:
        """
        Generate a sine wave tone.
        
        Args:
            frequency: Frequency of the tone in Hz
            duration: Duration of the tone in seconds
            amplitude: Amplitude of the tone (0.0 to 1.0)
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        tone = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in
        if fade_in > 0:
            fade_in_samples = int(self.sample_rate * fade_in)
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            tone[:fade_in_samples] *= fade_in_curve
            
        # Apply fade out
        if fade_out > 0:
            fade_out_samples = int(self.sample_rate * fade_out)
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            tone[-fade_out_samples:] *= fade_out_curve
            
        return tone
    
    def generate_noise(self,
                      duration: float,
                      noise_type: str = 'white',
                      amplitude: float = 0.1,
                      fade_in: float = 0.1,
                      fade_out: float = 0.1) -> np.ndarray:
        """
        Generate noise of various types.
        
        Args:
            duration: Duration of noise in seconds
            noise_type: Type of noise ('white', 'pink', 'brown')
            amplitude: Amplitude of noise (0.0 to 1.0)
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        
        if noise_type == 'white':
            # White noise (equal energy per frequency)
            noise = np.random.normal(0, amplitude, num_samples)
        elif noise_type == 'pink':
            # Pink noise (equal energy per octave)
            noise = np.random.normal(0, amplitude, num_samples)
            
            # Apply 1/f filter
            X = np.fft.rfft(noise)
            S = np.arange(1, len(X) + 1)
            S[0] = 1
            X = X / np.sqrt(S)
            noise = np.fft.irfft(X, len(noise))
            
            # Normalize
            noise = noise / np.max(np.abs(noise)) * amplitude
        elif noise_type == 'brown':
            # Brown noise (random walk / integrated white noise)
            noise = np.random.normal(0, amplitude, num_samples)
            noise = np.cumsum(noise)
            
            # Normalize
            noise = noise / np.max(np.abs(noise)) * amplitude
        else:
            noise = np.random.normal(0, amplitude, num_samples)
        
        # Apply fade in
        if fade_in > 0:
            fade_in_samples = int(self.sample_rate * fade_in)
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            noise[:fade_in_samples] *= fade_in_curve
            
        # Apply fade out
        if fade_out > 0:
            fade_out_samples = int(self.sample_rate * fade_out)
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            noise[-fade_out_samples:] *= fade_out_curve
            
        return noise
    
    def generate_cosmic_pad(self,
                          duration: float,
                          base_frequency: float = 55.0,
                          num_harmonics: int = 6,
                          detune_factor: float = 0.05,
                          amplitude: float = 0.3,
                          fade_in: float = 1.0,
                          fade_out: float = 2.0) -> np.ndarray:
        """
        Generate a cosmic pad sound with multiple harmonics and slight detuning.
        
        Args:
            duration: Duration of the pad in seconds
            base_frequency: Base frequency of the pad in Hz
            num_harmonics: Number of harmonics to include
            detune_factor: Amount of detuning between layers
            amplitude: Amplitude of the resulting pad
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        pad = np.zeros(num_samples)
        
        # Generate multiple layers of sine waves with different harmonics
        for i in range(num_harmonics):
            # Calculate harmonic frequency with slight detuning
            harmonic = i + 1
            frequency = base_frequency * harmonic
            detune = 1.0 + (random.random() * 2 - 1) * detune_factor
            
            # Generate the harmonic layer
            layer_amplitude = amplitude / (harmonic * 0.8)  # Amplitude decreases for higher harmonics
            layer = layer_amplitude * np.sin(2 * np.pi * frequency * detune * t)
            
            # Add slow LFO modulation to the layer
            lfo_rate = 0.1 + (random.random() * 0.3)  # 0.1 to 0.4 Hz
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * lfo_rate * t)
            layer = layer * lfo
            
            # Add the layer to the pad
            pad += layer
        
        # Add subtle noise for texture
        noise = self.generate_noise(duration, 'pink', amplitude=amplitude*0.05)
        pad += noise
        
        # Normalize
        pad = pad / np.max(np.abs(pad)) * amplitude
        
        # Apply fade in
        if fade_in > 0:
            fade_in_samples = int(self.sample_rate * fade_in)
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            pad[:fade_in_samples] *= fade_in_curve
            
        # Apply fade out
        if fade_out > 0:
            fade_out_samples = int(self.sample_rate * fade_out)
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            pad[-fade_out_samples:] *= fade_out_curve
            
        return pad
    
    def generate_cosmic_shimmer(self,
                              duration: float,
                              frequency_range: Tuple[float, float] = (1000.0, 5000.0),
                              num_layers: int = 20,
                              amplitude: float = 0.2,
                              fade_in: float = 0.5,
                              fade_out: float = 1.0) -> np.ndarray:
        """
        Generate a shimmering cosmic texture with multiple random sine waves.
        
        Args:
            duration: Duration of the shimmer in seconds
            frequency_range: Range of frequencies to use (min, max)
            num_layers: Number of sine wave layers
            amplitude: Amplitude of the resulting shimmer
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        shimmer = np.zeros(num_samples)
        
        for _ in range(num_layers):
            # Random frequency within the specified range
            freq = random.uniform(frequency_range[0], frequency_range[1])
            
            # Random start time within the duration
            start_time = random.uniform(0, duration * 0.8)
            start_sample = int(start_time * self.sample_rate)
            
            # Random duration for this layer
            layer_duration = random.uniform(0.2, 1.0)
            layer_samples = min(int(layer_duration * self.sample_rate), num_samples - start_sample)
            
            # Generate the layer
            layer_amplitude = amplitude / num_layers * random.uniform(0.5, 1.5)
            layer = np.zeros(num_samples)
            layer_t = t[start_sample:start_sample+layer_samples] - start_time
            layer[start_sample:start_sample+layer_samples] = layer_amplitude * np.sin(2 * np.pi * freq * layer_t)
            
            # Apply envelope to the layer
            envelope = np.zeros(layer_samples)
            attack = int(layer_samples * 0.2)
            release = int(layer_samples * 0.5)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[attack:layer_samples-release] = 1
            envelope[layer_samples-release:] = np.linspace(1, 0, release)
            layer[start_sample:start_sample+layer_samples] *= envelope
            
            # Add the layer to the shimmer
            shimmer += layer
        
        # Add gentle filtered noise for texture
        noise = self.generate_noise(duration, 'pink', amplitude=amplitude*0.1)
        # Apply bandpass filter to the noise (simple implementation)
        filter_freq = (frequency_range[0] + frequency_range[1]) / 2
        filter_width = (frequency_range[1] - frequency_range[0]) / 2
        fft_noise = np.fft.rfft(noise)
        freqs = np.fft.rfftfreq(len(noise), 1/self.sample_rate)
        filter_mask = np.exp(-0.5 * ((freqs - filter_freq) / filter_width) ** 2)
        filtered_noise = np.fft.irfft(fft_noise * filter_mask, len(noise))
        shimmer += filtered_noise * 0.3
        
        # Normalize
        shimmer = shimmer / np.max(np.abs(shimmer) + 1e-9) * amplitude
        
        # Apply overall fade in and fade out
        if fade_in > 0:
            fade_in_samples = int(self.sample_rate * fade_in)
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            shimmer[:fade_in_samples] *= fade_in_curve
            
        if fade_out > 0:
            fade_out_samples = int(self.sample_rate * fade_out)
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            shimmer[-fade_out_samples:] *= fade_out_curve
            
        return shimmer
    
    def generate_cosmic_transition(self,
                                 duration: float = 3.0,
                                 transition_type: str = 'sweep',
                                 amplitude: float = 0.4) -> np.ndarray:
        """
        Generate a cosmic transition effect.
        
        Args:
            duration: Duration of the transition in seconds
            transition_type: Type of transition ('sweep', 'whoosh', 'glitch')
            amplitude: Amplitude of the resulting transition
            
        Returns:
            Numpy array of audio samples
        """
        num_samples = int(self.sample_rate * duration)
        transition = np.zeros(num_samples)
        
        if transition_type == 'sweep':
            # Frequency sweep from low to high
            t = np.linspace(0, duration, num_samples, False)
            start_freq = 100.0
            end_freq = 5000.0
            
            # Exponential frequency sweep
            exponent = 4
            normalized_t = t / duration
            freq_t = start_freq + (end_freq - start_freq) * (normalized_t ** exponent)
            
            # Integrate to get the phase
            phase = 2 * np.pi * np.cumsum(freq_t) / self.sample_rate
            
            # Generate the sweep
            sweep = amplitude * np.sin(phase)
            
            # Apply amplitude envelope
            envelope = np.sin(np.pi * normalized_t)
            transition = sweep * envelope
            
        elif transition_type == 'whoosh':
            # A whoosh effect with filtered noise
            noise = self.generate_noise(duration, 'pink', amplitude=amplitude)
            t = np.linspace(0, duration, num_samples, False)
            
            # Create a time-varying filter
            filter_freqs = 10000 * np.exp(-4 * t / duration)  # Exponential decay
            
            # Apply the filter in frequency domain (simple implementation)
            fft_noise = np.fft.rfft(noise)
            freqs = np.fft.rfftfreq(len(noise), 1/self.sample_rate)
            
            for i, freq in enumerate(freqs):
                # Time-varying lowpass filter
                filter_gain = np.zeros(len(t))
                for j, cutoff in enumerate(filter_freqs):
                    filter_gain[j] = 1.0 / (1.0 + (freq / cutoff) ** 8)
                
                # Apply the filter
                fft_noise[i] *= np.mean(filter_gain)
            
            # Convert back to time domain
            filtered_noise = np.fft.irfft(fft_noise, len(noise))
            
            # Apply amplitude envelope
            envelope = 1.5 * np.sin(np.pi * t / duration) * np.exp(-3 * t / duration)
            transition = filtered_noise * envelope
            
        elif transition_type == 'glitch':
            # Create a glitchy digital-sounding transition
            t = np.linspace(0, duration, num_samples, False)
            
            # Base noise layer
            noise = self.generate_noise(duration, 'white', amplitude=amplitude*0.5)
            
            # Add random sine grains
            for _ in range(30):
                grain_start = random.uniform(0, duration * 0.9)
                grain_length = random.uniform(0.02, 0.1)
                grain_freq = random.uniform(300, 3000)
                
                start_idx = int(grain_start * self.sample_rate)
                length_idx = int(grain_length * self.sample_rate)
                end_idx = min(start_idx + length_idx, num_samples)
                
                grain_t = t[start_idx:end_idx] - grain_start
                grain = 0.5 * amplitude * np.sin(2 * np.pi * grain_freq * grain_t)
                
                # Apply quick envelope
                grain_env = np.sin(np.pi * np.linspace(0, 1, len(grain)))
                grain *= grain_env
                
                noise[start_idx:end_idx] += grain
            
            # Add digital artifacts
            for _ in range(10):
                artifact_start = random.uniform(0, duration * 0.9)
                artifact_length = random.uniform(0.01, 0.05)
                
                start_idx = int(artifact_start * self.sample_rate)
                length_idx = int(artifact_length * self.sample_rate)
                end_idx = min(start_idx + length_idx, num_samples)
                
                artifact = np.random.choice([-1, 0, 1], size=(end_idx - start_idx)) * amplitude
                noise[start_idx:end_idx] = artifact
            
            # Overall envelope
            envelope = np.ones_like(t)
            fade_samples = int(0.1 * self.sample_rate)
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            transition = noise * envelope
        
        else:
            # Default to a simple noise burst
            transition = self.generate_noise(duration, 'white', amplitude=amplitude)
            t = np.linspace(0, 1, num_samples)
            envelope = np.sin(np.pi * t)
            transition *= envelope
        
        # Normalize to desired amplitude
        transition = transition / np.max(np.abs(transition) + 1e-9) * amplitude
        
        return transition
    
    def generate_cosmic_soundscape(self, 
                                 duration: float = 30.0,
                                 mood: str = 'peaceful',
                                 layers: int = 3,
                                 output_filename: Optional[str] = None) -> Tuple[np.ndarray, str]:
        """
        Generate a complete cosmic soundscape by layering multiple sounds.
        
        Args:
            duration: Duration of the soundscape in seconds
            mood: Mood of the soundscape ('peaceful', 'mysterious', 'energetic')
            layers: Number of sound layers to combine
            output_filename: Optional filename to save the soundscape
            
        Returns:
            Tuple of (audio_data, output_path)
        """
        logger.info(f"Generating cosmic soundscape: duration={duration}s, mood={mood}, layers={layers}")
        
        # Define parameters based on mood
        if mood == 'peaceful':
            base_freq = 55.0  # A1 note
            pad_amplitude = 0.4
            shimmer_amplitude = 0.15
            noise_amplitude = 0.05
            noise_type = 'pink'
        elif mood == 'mysterious':
            base_freq = 38.89  # D#1 note
            pad_amplitude = 0.35
            shimmer_amplitude = 0.2
            noise_amplitude = 0.08
            noise_type = 'brown'
        elif mood == 'energetic':
            base_freq = 65.41  # C2 note
            pad_amplitude = 0.3
            shimmer_amplitude = 0.25
            noise_amplitude = 0.1
            noise_type = 'white'
        else:
            # Default to peaceful
            base_freq = 55.0
            pad_amplitude = 0.4
            shimmer_amplitude = 0.15
            noise_amplitude = 0.05
            noise_type = 'pink'
        
        # Generate the layers
        soundscape = np.zeros(int(self.sample_rate * duration))
        
        # Base pad layer
        if layers >= 1:
            pad = self.generate_cosmic_pad(
                duration=duration,
                base_frequency=base_freq,
                num_harmonics=6,
                amplitude=pad_amplitude,
                fade_in=2.0,
                fade_out=4.0
            )
            soundscape += pad
        
        # Shimmering layer
        if layers >= 2:
            shimmer = self.generate_cosmic_shimmer(
                duration=duration,
                frequency_range=(1000, 5000),
                num_layers=20,
                amplitude=shimmer_amplitude,
                fade_in=3.0,
                fade_out=5.0
            )
            soundscape += shimmer
        
        # Background noise layer
        if layers >= 3:
            noise = self.generate_noise(
                duration=duration,
                noise_type=noise_type,
                amplitude=noise_amplitude,
                fade_in=2.0,
                fade_out=3.0
            )
            soundscape += noise
        
        # Add occasional transition effects for longer soundscapes
        if duration > 10 and layers >= 3:
            # Add 1-3 transition effects
            num_transitions = random.randint(1, 3)
            for _ in range(num_transitions):
                # Random position (avoiding the very beginning and end)
                pos = random.uniform(duration * 0.2, duration * 0.8)
                transition_type = random.choice(['sweep', 'whoosh', 'glitch'])
                transition_duration = random.uniform(1.0, 3.0)
                
                # Generate the transition
                transition = self.generate_cosmic_transition(
                    duration=transition_duration,
                    transition_type=transition_type,
                    amplitude=0.15
                )
                
                # Add the transition at the specified position
                pos_idx = int(pos * self.sample_rate)
                end_idx = min(pos_idx + len(transition), len(soundscape))
                transition_len = end_idx - pos_idx
                soundscape[pos_idx:end_idx] += transition[:transition_len]
        
        # Normalize the final soundscape
        soundscape = soundscape / np.max(np.abs(soundscape) + 1e-9) * 0.9
        
        # Generate output filename if not provided
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"cosmic_{mood}_{layers}layers_{timestamp}.wav"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Save as WAV file
        try:
            # Convert to 16-bit PCM
            soundscape_int16 = (soundscape * 32767).astype(np.int16)
            wavfile.write(output_path, self.sample_rate, soundscape_int16)
            logger.info(f"Saved cosmic soundscape to {output_path}")
            
            # Convert to MP3 for web playback if pydub is available
            try:
                mp3_path = output_path.replace('.wav', '.mp3')
                audio = AudioSegment.from_wav(output_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")
                logger.info(f"Converted to MP3: {mp3_path}")
                
                # Use the MP3 path as output since it's better for web
                output_path = mp3_path
            except Exception as e:
                logger.warning(f"Could not convert to MP3: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to save soundscape: {str(e)}")
            output_path = ''
        
        return soundscape, output_path

# Create singleton instance
try:
    cosmic_soundscape_generator = CosmicSoundscapeGenerator()
    logger.info("Cosmic Soundscape Generator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cosmic Soundscape Generator: {str(e)}")
    cosmic_soundscape_generator = None
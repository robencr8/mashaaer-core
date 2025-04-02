"""
Mashaaer Feelings - Mobile Emotion Analysis Application
===================================================

This is the main entry point for the Mashaaer Feelings Android application.
It imports and runs the Kivy application defined in kivy_app.py.

"""
# Make sure kivy modules are properly loaded
import kivy
from kivy.config import Config

# Configure app settings
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'window_icon', '../data/icon.png')

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our application
from kivy_app import MashaaerApp

# Run the application
if __name__ == "__main__":
    MashaaerApp().run()
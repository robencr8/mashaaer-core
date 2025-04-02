import os
import logging
import json
import base64
from datetime import datetime
import threading
import sqlite3
# Efficient query caching for better performance

class FaceRecognitionModule:
    """Module for interfacing with face recognition capabilities"""

    def __init__(self, face_detector, db_manager):
        self.logger = logging.getLogger(__name__)
        self.face_detector = face_detector
        self.db_manager = db_manager
        self.face_memory_lock = threading.Lock()

        # Ensure profiles directory exists
        self.profiles_dir = "face_profiles"
        os.makedirs(self.profiles_dir, exist_ok=True)

        # Initialize face memory from database
        self.face_memory = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load face profiles from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Create faces table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    encoding BLOB,
                    last_seen TEXT,
                    face_metadata TEXT
                )
            ''')

            # Load existing profiles
            cursor.execute("SELECT name, encoding, last_seen, face_metadata FROM faces")
            profiles = cursor.fetchall()

            with self.face_memory_lock:
                for name, encoding, last_seen, metadata in profiles:
                    if encoding:
                        # Convert BLOB to list of floats
                        encoding_list = json.loads(encoding)

                        # Parse metadata
                        profile_metadata = {}
                        if metadata:
                            profile_metadata = json.loads(metadata)

                        self.face_memory[name] = {
                            "encoding": encoding_list,
                            "last_seen": last_seen,
                            "metadata": profile_metadata
                        }

            self.logger.info(f"Loaded {len(profiles)} face profiles")

        except Exception as e:
            self.logger.error(f"Failed to load face profiles: {str(e)}")

    def recognize_face(self, image_path):
        """Recognize a face in the given image"""
        try:
            # Call the face detector to get encodings
            face_data = self.face_detector.detect_faces(image_path)

            if not face_data or not face_data.get("encodings"):
                return {"recognized": False, "message": "No faces detected"}

            # Get the first face encoding
            encoding = face_data["encodings"][0]

            # Compare with stored profiles
            best_match = None
            best_match_distance = 0.6  # Threshold for face recognition

            with self.face_memory_lock:
                for name, profile in self.face_memory.items():
                    # Use the face_recognition library to compare
                    distance = self._calculate_face_distance(encoding, profile["encoding"])

                    if distance < best_match_distance:
                        best_match = name
                        best_match_distance = distance

            # If we found a match
            if best_match:
                # Update last seen timestamp
                self._update_last_seen(best_match)

                # Check if this is Roben Edwan (developer mode)
                is_developer = (best_match.lower() == "roben edwan")

                result = {
                    "recognized": True,
                    "name": best_match,
                    "confidence": 1.0 - best_match_distance,
                    "dev_mode": is_developer
                }

                # Include profile metadata if available
                if best_match in self.face_memory and "metadata" in self.face_memory[best_match]:
                    result["metadata"] = self.face_memory[best_match]["metadata"]

                return result

            return {"recognized": False, "message": "Face not recognized"}

        except Exception as e:
            self.logger.error(f"Face recognition error: {str(e)}")
            return {"recognized": False, "error": str(e)}

    def _calculate_face_distance(self, encoding1, encoding2):
        """Calculate the distance between two face encodings"""
        import numpy as np

        # Convert to numpy arrays
        try:
            a = np.array(encoding1)
            b = np.array(encoding2)

            # Calculate Euclidean distance
            return np.linalg.norm(a - b)
        except Exception as e:
            self.logger.error(f"Error calculating face distance: {str(e)}")
            return 1.0  # Return max distance on error

    def _update_last_seen(self, name):
        """Update the last seen timestamp for a profile"""
        try:
            timestamp = datetime.now().isoformat()

            # Update in-memory record
            with self.face_memory_lock:
                if name in self.face_memory:
                    self.face_memory[name]["last_seen"] = timestamp

            # Update database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE faces SET last_seen = ? WHERE name = ?",
                (timestamp, name)
            )

            conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to update last seen timestamp: {str(e)}")

    def add_face(self, name, image_path, metadata=None):
        """Add a new face profile"""
        try:
            # Detect face in the image
            face_data = self.face_detector.detect_faces(image_path)

            if not face_data or not face_data.get("encodings"):
                return False, "No faces detected in the image"

            # Get the encoding
            encoding = face_data["encodings"][0]

            # Convert encoding to JSON string for storage
            encoding_json = json.dumps(encoding)

            # Prepare metadata
            if metadata is None:
                metadata = {}

            metadata_json = json.dumps(metadata)
            timestamp = datetime.now().isoformat()

            # Store in database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Check if this name already exists
            cursor.execute("SELECT id FROM faces WHERE name = ?", (name,))
            existing = cursor.fetchone()

            if existing:
                # Update existing record
                cursor.execute(
                    "UPDATE faces SET encoding = ?, last_seen = ?, face_metadata = ? WHERE name = ?",
                    (encoding_json, timestamp, metadata_json, name)
                )
            else:
                # Insert new record
                cursor.execute(
                    "INSERT INTO faces (name, encoding, last_seen, face_metadata) VALUES (?, ?, ?, ?)",
                    (name, encoding_json, timestamp, metadata_json)
                )

            conn.commit()

            # Update in-memory database
            with self.face_memory_lock:
                self.face_memory[name] = {
                    "encoding": encoding,
                    "last_seen": timestamp,
                    "metadata": metadata
                }

            self.logger.info(f"Added face profile for {name}")
            return True, f"Face profile for {name} added successfully"

        except Exception as e:
            self.logger.error(f"Failed to add face: {str(e)}")
            return False, f"Error: {str(e)}"

    def get_all_profiles(self):
        """Get all face profiles with metadata"""
        try:
            profiles = []

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT name, last_seen, face_metadata FROM faces ORDER BY last_seen DESC")
            results = cursor.fetchall()

            for name, last_seen, face_metadata in results:
                profile = {
                    "name": name,
                    "last_seen": last_seen
                }

                if face_metadata:
                    profile["metadata"] = json.loads(face_metadata)

                profiles.append(profile)

            return profiles

        except Exception as e:
            self.logger.error(f"Failed to get profiles: {str(e)}")
            return []
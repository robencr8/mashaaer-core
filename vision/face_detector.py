import os
import logging
import json
import cv2
# Temporarily comment out face_recognition dependency for development
# import face_recognition
import threading
import time
import numpy as np
from datetime import datetime

class FaceDetector:
    """Handles face detection and recognition"""
    
    def __init__(self, config, db_manager):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_manager = db_manager
        
        # Create face profiles directory
        self.profiles_dir = "face_profiles"
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # For storing face encodings and data
        self.known_faces = {}
        self.face_metadata = {}
        self.face_lock = threading.Lock()
        
        # Detection settings
        self.detection_interval = 1.0  # seconds
        self.face_tolerance = 0.6      # recognition threshold
        
        # For continuous detection
        self.is_running = False
        self.detection_thread = None
        
        # Greeting templates
        self.first_time_greetings = [
            "Hello {name}, nice to meet you for the first time!",
            "Welcome {name}, I'm Robin AI. It's a pleasure to meet you!",
            "Hi {name}! I don't think we've met before. I'm Robin!"
        ]
        
        self.returning_greetings = [
            "Welcome back {name}! It's been {time_passed} since I last saw you.",
            "Hello again {name}! It's been {time_passed} since your last visit.",
            "Nice to see you again {name}! It's been {time_passed}.",
            "{name}! Good to see you after {time_passed}."
        ]
        
        self.recent_greetings = [
            "Hello again {name}! Nice to see you twice in the same day!",
            "Back so soon, {name}? Great to see you again!",
            "Welcome back {name}! Thanks for visiting again today!"
        ]
    
    def initialize(self):
        """Initialize the face detection system"""
        self.logger.info("Initializing face detection...")
        
        try:
            # Create database tables if needed
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    encoding BLOB,
                    last_seen TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            
            # Load saved face profiles
            self._load_face_profiles()
            
            self.logger.info("Face detection initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize face detection: {str(e)}")
            return False
    
    def _load_face_profiles(self):
        """Load saved face profiles from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, encoding, metadata FROM faces")
            rows = cursor.fetchall()
            
            with self.face_lock:
                for name, encoding_blob, metadata_json in rows:
                    if encoding_blob:
                        # Convert BLOB to face encoding
                        encoding_list = json.loads(encoding_blob)
                        encoding_array = np.array(encoding_list)
                        
                        self.known_faces[name] = encoding_array
                        
                        # Load metadata if available
                        if metadata_json:
                            self.face_metadata[name] = json.loads(metadata_json)
                        else:
                            self.face_metadata[name] = {}
            
            self.logger.info(f"Loaded {len(rows)} face profiles")
        
        except Exception as e:
            self.logger.error(f"Failed to load face profiles: {str(e)}")
    
    def detect_faces(self, image_path):
        """Detect and recognize faces in the given image"""
        try:
            # Temporary mock implementation for development
            # This returns a dummy response until face_recognition is properly installed
            self.logger.info(f"Mock face detection called for {image_path}")
            
            # Get profiles from the database to simulate real recognition
            profiles = self.get_all_profiles()
            
            # If no profiles exist, return an unknown face
            if not profiles:
                return {
                    "count": 1,
                    "faces": [{
                        "location": [0, 0, 100, 100],  # top, right, bottom, left
                        "recognized": False,
                        "name": "Unknown",
                        "confidence": 0.0,
                    }],
                    "encodings": []
                }
            
            # Select a random profile to simulate recognition
            import random
            profile = random.choice(profiles)
            
            # Get the last seen information
            last_seen_str = profile.get('last_seen', 'never')
            last_seen_time = None
            try:
                if last_seen_str and last_seen_str != 'never':
                    last_seen_time = datetime.fromisoformat(last_seen_str)
            except:
                last_seen_time = None
                
            # Generate a personalized greeting based on recognition history
            greeting = self._generate_greeting(profile['name'], last_seen_time)
            
            # Mock face recognition result
            mock_result = {
                "count": 1,
                "faces": [{
                    "location": [0, 0, 100, 100],  # top, right, bottom, left
                    "recognized": True,
                    "name": profile['name'],
                    "confidence": 0.92,
                    "metadata": profile.get('metadata', {}),
                    "dev_mode": profile['name'] == "Roben Edwan",
                    "greeting": greeting,
                    "last_seen": last_seen_str
                }],
                "encodings": []
            }
            
            return mock_result
        
        except Exception as e:
            self.logger.error(f"Face detection error: {str(e)}")
            return {"count": 0, "faces": [], "error": str(e)}
    
    def add_face(self, name, image_path, metadata=None):
        """Add a new face profile"""
        try:
            # Temporary mock implementation for development
            self.logger.info(f"Mock face profile addition for {name}")
            
            # Generate mock metadata if not provided
            if metadata is None:
                metadata = {
                    "added": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat()
                }
            
            metadata_json = json.dumps(metadata)
            
            # Create mock encoding (just an array of random values)
            mock_encoding = np.random.rand(128).tolist()
            encoding_json = json.dumps(mock_encoding)
            
            # Save to database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if name already exists
            cursor.execute("SELECT id FROM faces WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing face
                cursor.execute(
                    "UPDATE faces SET encoding = ?, last_seen = ?, metadata = ? WHERE name = ?",
                    (encoding_json, datetime.now().isoformat(), metadata_json, name)
                )
            else:
                # Add new face
                cursor.execute(
                    "INSERT INTO faces (name, encoding, last_seen, metadata) VALUES (?, ?, ?, ?)",
                    (name, encoding_json, datetime.now().isoformat(), metadata_json)
                )
            
            conn.commit()
            
            # Update in-memory cache
            with self.face_lock:
                self.known_faces[name] = np.array(mock_encoding)
                self.face_metadata[name] = metadata
            
            # Create face profiles directory if it doesn't exist
            face_dir = os.path.join(self.profiles_dir, name)
            os.makedirs(face_dir, exist_ok=True)
            
            # Save a copy of the image for reference
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            face_file = os.path.join(face_dir, f"{timestamp}.jpg")
            
            # Just copy the original image for now
            if os.path.exists(image_path):
                try:
                    # Try to load and save the image using OpenCV
                    img = cv2.imread(image_path)
                    if img is not None:
                        cv2.imwrite(face_file, img)
                except Exception as img_e:
                    self.logger.warning(f"Could not process image: {str(img_e)}")
            
            self.logger.info(f"Added mock face profile for {name}")
            return True, f"Face profile for {name} added successfully"
        
        except Exception as e:
            self.logger.error(f"Failed to add face: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _update_last_seen(self, name):
        """Update the last seen timestamp for a face"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Update database
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE faces SET last_seen = ? WHERE name = ?",
                (timestamp, name)
            )
            
            conn.commit()
            
            # Update metadata
            with self.face_lock:
                if name in self.face_metadata:
                    self.face_metadata[name]["last_seen"] = timestamp
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to update last seen: {str(e)}")
            return False
    
    def start_detection(self, camera_id=0, callback=None):
        """Start continuous face detection from camera"""
        if self.is_running:
            self.logger.warning("Face detection already running")
            return False
        
        # Start detection thread
        self.is_running = True
        self.detection_thread = threading.Thread(
            target=self._detection_thread,
            args=(camera_id, callback)
        )
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        self.logger.info("Started continuous face detection")
        return True
    
    def stop_detection(self):
        """Stop continuous face detection"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        
        self.logger.info("Stopped face detection")
    
    def _detection_thread(self, camera_id, callback):
        """Thread for continuous face detection"""
        try:
            # Mock camera detection for development
            self.logger.info("Starting mock camera detection")
            
            # Keep track of last detected faces to avoid duplicates
            last_detected = {}
            
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Mock continuous detection
            while self.is_running:
                # Sleep to simulate processing time
                time.sleep(self.detection_interval)
                
                # Simulate a detected face without using the camera
                result = {
                    "count": 1,
                    "faces": [{
                        "location": [0, 0, 100, 100],
                        "recognized": True,
                        "name": "Roben Edwan",
                        "confidence": 0.92,
                        "metadata": {
                            "last_seen": datetime.now().isoformat()
                        },
                        "dev_mode": True
                    }]
                }
                
                # Call the callback with results
                if callback and result["count"] > 0:
                    # Filter out faces we just reported to avoid spamming
                    now = time.time()
                    faces_to_report = []
                    
                    for face in result["faces"]:
                        if face["recognized"]:
                            name = face["name"]
                            # Only report if we haven't seen this face recently
                            if name not in last_detected or (now - last_detected[name]) > 10.0:
                                faces_to_report.append(face)
                                last_detected[name] = now
                    
                    if faces_to_report:
                        callback(faces_to_report)
        
        except Exception as e:
            self.logger.error(f"Face detection thread error: {str(e)}")
            self.is_running = False
    
    def get_profile_count(self):
        """Get the number of face profiles"""
        return len(self.known_faces)
        
    def get_all_profiles(self):
        """Get all face profiles with metadata"""
        try:
            profiles = []
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, last_seen, metadata 
                FROM faces 
                ORDER BY last_seen DESC
            """)
            
            rows = cursor.fetchall()
            
            for profile_id, name, last_seen, metadata_json in rows:
                profile = {
                    "id": profile_id,
                    "name": name,
                    "last_seen": last_seen
                }
                
                # Get image path if available
                face_dir = os.path.join(self.profiles_dir, name)
                if os.path.exists(face_dir):
                    image_files = [f for f in os.listdir(face_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                    if image_files:
                        profile["image_path"] = os.path.join(face_dir, image_files[0])
                
                # Parse metadata
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                        profile["metadata"] = metadata
                        
                        # Add some mock stats for demonstration
                        profile["interactions"] = metadata.get("interactions", 
                                                             int(np.random.randint(5, 50)))
                        profile["recognition_rate"] = metadata.get("recognition_rate", 
                                                                 int(np.random.randint(70, 100)))
                    except:
                        pass
                
                profiles.append(profile)
            
            return profiles
        
        except Exception as e:
            self.logger.error(f"Failed to get profiles: {str(e)}")
            return []
            
    def _generate_greeting(self, name, last_seen_time):
        """Generate a personalized greeting based on recognition history"""
        import random
        
        # If this is a first-time greeting (no last_seen)
        if not last_seen_time:
            greeting_template = random.choice(self.first_time_greetings)
            return greeting_template.format(name=name)
        
        # Calculate time difference
        now = datetime.now()
        time_diff = now - last_seen_time
        
        # If seen within the last 24 hours
        if time_diff.days < 1:
            greeting_template = random.choice(self.recent_greetings)
            return greeting_template.format(name=name)
        
        # Format the time difference for returning greeting
        if time_diff.days == 1:
            time_passed = "a day"
        elif time_diff.days < 7:
            time_passed = f"{time_diff.days} days"
        elif time_diff.days < 30:
            weeks = time_diff.days // 7
            time_passed = f"{weeks} {'week' if weeks == 1 else 'weeks'}"
        elif time_diff.days < 365:
            months = time_diff.days // 30
            time_passed = f"{months} {'month' if months == 1 else 'months'}"
        else:
            years = time_diff.days // 365
            time_passed = f"{years} {'year' if years == 1 else 'years'}"
        
        # Generate returning greeting
        greeting_template = random.choice(self.returning_greetings)
        return greeting_template.format(name=name, time_passed=time_passed)

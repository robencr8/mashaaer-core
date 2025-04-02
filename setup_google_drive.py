import os
import subprocess
import logging
import webbrowser
import http.server
import socketserver
import urllib.parse
from threading import Thread
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("google_drive_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GoogleDriveSetup")

# Configuration
CONFIG_FILE = "rclone.conf"
AUTH_PORT = 8080
AUTH_CODE = None

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global AUTH_CODE
        
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            AUTH_CODE = query_params['code'][0]
            logger.info("Authentication code received")
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head><title>Google Drive Authentication</title></head>
            <body>
                <h1>Authentication Successful</h1>
                <p>You can close this window and return to the application.</p>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head><title>Google Drive Authentication</title></head>
            <body>
                <h1>Authentication Failed</h1>
                <p>No authentication code received. Please try again.</p>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))

def start_auth_server():
    """Start the authentication server to receive the OAuth code"""
    try:
        handler = AuthHandler
        httpd = socketserver.TCPServer(("", AUTH_PORT), handler)
        logger.info(f"Authentication server started on port {AUTH_PORT}")
        
        httpd.timeout = 60  # Set timeout to 60 seconds
        httpd.handle_request()  # Handle one request then exit
        
        logger.info("Authentication server stopped")
    except Exception as e:
        logger.error(f"Error starting authentication server: {e}")

def setup_google_drive():
    """Setup Google Drive authentication for rclone"""
    if os.path.exists(CONFIG_FILE):
        logger.info(f"Config file {CONFIG_FILE} already exists")
        return True
    
    # Start the authentication server in a separate thread
    auth_thread = Thread(target=start_auth_server)
    auth_thread.daemon = True
    auth_thread.start()
    
    time.sleep(1)  # Give the server time to start
    
    # Generate config
    try:
        # Start the config process
        logger.info("Starting rclone config process for Google Drive")
        print("\n==== GOOGLE DRIVE AUTHENTICATION ====")
        print("Please follow these steps to authenticate with Google Drive:")
        print("1. In the next step, you'll see the rclone configuration process")
        print("2. Choose 'n' for new remote")
        print("3. Name it 'googledrive'")
        print("4. Select 'drive' for Google Drive")
        print("5. Follow the on-screen instructions for Google Drive authentication")
        print("6. When asked for root folder ID, enter: 1wUodMcwES79gB18uul2xACChciO-X2Um")
        print("7. The authentication may open a browser window; if it does not, copy the URL and open it manually")
        print("8. After authentication, the process will continue automatically")
        print("=========================================\n")
        
        input("Press Enter to continue...")
        
        # Run rclone config interactively
        subprocess.run(["./rclone", "config"])
        
        # Wait for auth thread to complete
        auth_thread.join(timeout=120)
        
        if os.path.exists(CONFIG_FILE):
            logger.info("Google Drive configuration successful")
            return True
        else:
            logger.error("Google Drive configuration failed - config file not created")
            return False
    
    except Exception as e:
        logger.error(f"Error setting up Google Drive: {e}")
        return False

if __name__ == "__main__":
    if setup_google_drive():
        print("\nGoogle Drive setup completed successfully!")
        print("You can now run the sync script: python rclone_sync.py")
    else:
        print("\nGoogle Drive setup failed. Check the logs for more information.")
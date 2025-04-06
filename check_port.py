"""
Check Port Binding Script

This script checks if a port is correctly bound and accessible externally.
"""
import socket
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_port_binding(port):
    """Check if a port is bound and listening on all interfaces"""
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        # Bind to all interfaces on the specified port
        result = sock.connect_ex(('localhost', port))
        
        if result == 0:
            logger.info(f"✅ Port {port} is OPEN on localhost")
        else:
            logger.error(f"❌ Port {port} is CLOSED on localhost (error code: {result})")
            return False
        
        sock.close()
        
        # Try to connect from different interfaces
        interfaces = [
            ('127.0.0.1', 'Loopback IPv4'),
            ('0.0.0.0', 'All IPv4 interfaces'),
        ]
        
        for interface, name in interfaces:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                # Try to bind to the interface (will fail if already bound)
                try:
                    sock.bind((interface, port))
                    logger.warning(f"⚠️ Port {port} is NOT bound on {name} - can bind to it")
                    sock.close()
                except socket.error:
                    logger.info(f"✅ Port {port} is already bound on {name}")
            except Exception as e:
                logger.error(f"Error checking {name}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking port binding: {str(e)}")
        return False

if __name__ == "__main__":
    # Default port
    port = 5000
    
    # Use command-line argument if provided
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    success = check_port_binding(port)
    
    if not success:
        logger.error("❌ Port binding check failed")
        sys.exit(1)
    else:
        logger.info("✅ Port binding check successful")
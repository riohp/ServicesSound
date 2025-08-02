import os
import sys
import platform
import uuid
import socket
import netifaces as ni

def get_system_info():
    """Get system information for diagnostics"""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "hostname": socket.gethostname(),
        "ip_address": get_local_ip(),
        "mac_address": get_mac_address()
    }

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Get default gateway interface
        default_interface = ni.gateways()['default'][ni.AF_INET][1]
        # Get IP address for that interface
        return ni.ifaddresses(default_interface)[ni.AF_INET][0]['addr']
    except Exception:
        # Fallback to socket approach
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"  # Last resort fallback

def get_mac_address():
    """Get the MAC address of the machine"""
    try:
        # Get default gateway interface
        default_interface = ni.gateways()['default'][ni.AF_INET][1]
        # Get MAC address for that interface
        return ni.ifaddresses(default_interface)[ni.AF_LINK][0]['addr']
    except Exception:
        return "00:00:00:00:00:00"  # Fallback

def generate_device_id():
    """Generate a unique device ID"""
    # Use MAC address as a seed if possible
    mac = get_mac_address()
    if mac != "00:00:00:00:00:00":
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, mac))
    else:
        # Fallback to a random UUID
        return str(uuid.uuid4())

def get_app_directory():
    """Get the application directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8000):
    """Find an available port starting from a given port"""
    port = start_port
    while is_port_in_use(port):
        port += 1
        if port > 65535:  # Port range limit
            raise RuntimeError("No available ports found")
    return port
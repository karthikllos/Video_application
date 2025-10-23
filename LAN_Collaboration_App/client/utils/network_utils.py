"""
Network utilities for LAN Collaboration App
Reusable socket creation, sending, and receiving functions
"""

import socket
import struct
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.constants import BUFFER_SIZE, CONNECTION_TIMEOUT


def create_socket(socket_type='tcp', timeout=None):
    """Create and configure a socket
    
    Args:
        socket_type (str): 'tcp' or 'udp'
        timeout (float): Socket timeout in seconds (None for blocking)
        
    Returns:
        socket.socket: Configured socket object
    """
    if socket_type.lower() == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif socket_type.lower() == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        raise ValueError(f"Invalid socket type: {socket_type}. Use 'tcp' or 'udp'")
    
    if timeout is not None:
        sock.settimeout(timeout)
    
    return sock


def send_data(sock, data, chunk_size=BUFFER_SIZE):
    """Send data over socket with proper error handling
    
    Args:
        sock (socket.socket): Socket to send data through
        data (bytes): Data to send
        chunk_size (int): Size of chunks for sending
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ConnectionError: If connection is lost
    """
    try:
        if sock.type == socket.SOCK_STREAM:  # TCP
            # Send all data (handles partial sends)
            sock.sendall(data)
        else:  # UDP
            # UDP sends entire datagram
            sock.send(data)
        return True
    except BrokenPipeError:
        raise ConnectionError("Connection lost - broken pipe")
    except ConnectionResetError:
        raise ConnectionError("Connection reset by peer")
    except socket.timeout:
        raise ConnectionError("Send timeout")
    except Exception as e:
        raise ConnectionError(f"Send error: {e}")


def recv_data(sock, num_bytes, exact=True):
    """Receive data from socket
    
    Args:
        sock (socket.socket): Socket to receive data from
        num_bytes (int): Number of bytes to receive
        exact (bool): If True, receive exactly num_bytes. If False, receive up to num_bytes
        
    Returns:
        bytes: Received data, or None if connection closed
        
    Raises:
        ConnectionError: If connection is lost
    """
    try:
        if not exact:
            # Receive up to num_bytes
            data = sock.recv(num_bytes)
            return data if data else None
        
        # Receive exactly num_bytes
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(min(num_bytes - len(data), BUFFER_SIZE))
            if not chunk:
                return None  # Connection closed
            data += chunk
        return data
        
    except socket.timeout:
        raise ConnectionError("Receive timeout")
    except ConnectionResetError:
        raise ConnectionError("Connection reset by peer")
    except Exception as e:
        raise ConnectionError(f"Receive error: {e}")


def send_with_size(sock, data):
    """Send data with 4-byte size prefix
    
    Args:
        sock (socket.socket): Socket to send through
        data (bytes): Data to send
        
    Returns:
        bool: True if successful
    """
    # Send size first (4 bytes, big-endian)
    size_bytes = struct.pack('!I', len(data))
    send_data(sock, size_bytes)
    
    # Send data
    send_data(sock, data)
    return True


def recv_with_size(sock, max_size=None):
    """Receive data with 4-byte size prefix
    
    Args:
        sock (socket.socket): Socket to receive from
        max_size (int): Maximum allowed size (None for no limit)
        
    Returns:
        bytes: Received data, or None if connection closed
        
    Raises:
        ValueError: If received size exceeds max_size
    """
    # Receive size (4 bytes)
    size_bytes = recv_data(sock, 4, exact=True)
    if not size_bytes:
        return None
    
    size = struct.unpack('!I', size_bytes)[0]
    
    # Validate size
    if max_size is not None and size > max_size:
        raise ValueError(f"Data size {size} exceeds maximum {max_size}")
    
    # Receive data
    data = recv_data(sock, size, exact=True)
    return data


def connect_with_retry(sock, address, max_retries=3, retry_delay=1):
    """Connect to server with retry logic
    
    Args:
        sock (socket.socket): Socket to connect
        address (tuple): (host, port) tuple
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay between retries in seconds
        
    Returns:
        bool: True if connected successfully
    """
    import time
    
    for attempt in range(max_retries):
        try:
            sock.connect(address)
            return True
        except (ConnectionRefusedError, socket.timeout) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return False
    return False


def get_local_ip():
    """Get local IP address
    
    Returns:
        str: Local IP address
    """
    try:
        # Create a dummy socket to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def is_port_open(host, port, timeout=1):
    """Check if a port is open on a host
    
    Args:
        host (str): Hostname or IP address
        port (int): Port number
        timeout (float): Connection timeout
        
    Returns:
        bool: True if port is open
    """
    try:
        sock = create_socket('tcp', timeout=timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False


def set_socket_buffers(sock, send_buffer=None, recv_buffer=None):
    """Set socket send and receive buffer sizes
    
    Args:
        sock (socket.socket): Socket to configure
        send_buffer (int): Send buffer size in bytes
        recv_buffer (int): Receive buffer size in bytes
    """
    if send_buffer is not None:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buffer)
    
    if recv_buffer is not None:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buffer)


def enable_keepalive(sock, idle=60, interval=10, count=5):
    """Enable TCP keepalive on socket
    
    Args:
        sock (socket.socket): Socket to configure
        idle (int): Seconds before sending keepalive probes
        interval (int): Seconds between keepalive probes
        count (int): Number of failed probes before closing
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    
    # Platform-specific settings
    if hasattr(socket, 'TCP_KEEPIDLE'):
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle)
    if hasattr(socket, 'TCP_KEEPINTVL'):
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval)
    if hasattr(socket, 'TCP_KEEPCNT'):
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, count)


def enable_broadcast(sock):
    """Enable broadcast on UDP socket
    
    Args:
        sock (socket.socket): UDP socket to configure
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def close_socket(sock, timeout=1):
    """Safely close a socket
    
    Args:
        sock (socket.socket): Socket to close
        timeout (float): Timeout for graceful shutdown
    """
    if sock is None:
        return
    
    try:
        # For TCP, try graceful shutdown
        if sock.type == socket.SOCK_STREAM:
            sock.settimeout(timeout)
            sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass  # Ignore errors during shutdown
    finally:
        try:
            sock.close()
        except Exception:
            pass
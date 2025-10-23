"""
Screen sharing module for LAN Collaboration App
Handles screen capture, compression, transmission, and display
"""

import mss
import cv2
import numpy as np
import socket
import threading
import sys
import os
import time
import struct
from io import BytesIO
from PIL import Image

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, SCREEN_SHARE_PORT, VIDEO_QUALITY,
    BUFFER_SIZE, CONNECTION_TIMEOUT
)
from shared.protocol import SCREEN_SHARE
from shared.helpers import pack_message


class ScreenStreamer:
    """Handles screen capture and streaming"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=SCREEN_SHARE_PORT, fps=10, quality=VIDEO_QUALITY):
        self.server_ip = server_ip
        self.server_port = server_port
        self.fps = fps
        self.quality = quality
        self.sock = None
        self.running = False
        self.sct = None
        
    def connect(self):
        """Connect to the screen share server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip, self.server_port))
            print(f"✓ Connected to screen share server at {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def start_streaming(self):
        """Capture and stream screen"""
        if not self.connect():
            return
        
        self.sct = mss.mss()
        self.running = True
        
        # Get primary monitor
        monitor = self.sct.monitors[1]  # Monitor 1 is primary screen
        
        print(f"\n🖥️  Starting screen share")
        print(f"📊 Resolution: {monitor['width']}x{monitor['height']}")
        print(f"🎬 FPS: {self.fps}")
        print(f"📦 Quality: {self.quality}%")
        print("Press Ctrl+C to stop\n")
        
        frame_count = 0
        start_time = time.time()
        frame_interval = 1.0 / self.fps
        
        try:
            while self.running:
                frame_start = time.time()
                
                # Capture screen
                screenshot = self.sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Compress to JPEG
                jpeg_bytes = self._compress_image(img)
                
                # Send via TCP in chunks
                if self._send_frame(jpeg_bytes):
                    frame_count += 1
                    
                    # Statistics
                    if frame_count % (self.fps * 5) == 0:  # Every 5 seconds
                        elapsed = time.time() - start_time
                        actual_fps = frame_count / elapsed
                        avg_size = len(jpeg_bytes)
                        print(f"📡 Frames: {frame_count} | "
                              f"FPS: {actual_fps:.1f} | "
                              f"Size: {avg_size//1024} KB")
                else:
                    print("❌ Failed to send frame, stopping...")
                    break
                
                # Control frame rate
                elapsed = time.time() - frame_start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.stop_streaming()
    
    def _compress_image(self, img):
        """Compress PIL Image to JPEG bytes"""
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=self.quality, optimize=True)
        return buffer.getvalue()
    
    def _send_frame(self, jpeg_bytes):
        """Send a frame over TCP in chunks"""
        try:
            # Pack the frame data with protocol header
            packet = pack_message(SCREEN_SHARE, jpeg_bytes)
            
            # Send the entire packet
            # TCP will handle chunking automatically, but we send size first
            frame_size = len(packet)
            
            # Send frame size (4 bytes, big-endian)
            self.sock.sendall(struct.pack('!I', frame_size))
            
            # Send frame data
            self.sock.sendall(packet)
            
            return True
            
        except BrokenPipeError:
            print("\n❌ Connection lost")
            return False
        except Exception as e:
            print(f"\n❌ Send error: {e}")
            return False
    
    def stop_streaming(self):
        """Clean up resources"""
        self.running = False
        if self.sct:
            self.sct.close()
        if self.sock:
            self.sock.close()
        print("\n🛑 Screen sharing stopped")


class ScreenReceiver:
    """Handles receiving and displaying screen shares"""
    
    def __init__(self, listen_port=SCREEN_SHARE_PORT):
        self.listen_port = listen_port
        self.server_sock = None
        self.client_sock = None
        self.running = False
        
    def start_receiving(self):
        """Start receiving and displaying screen shares"""
        try:
            # Create TCP server socket
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(('0.0.0.0', self.listen_port))
            self.server_sock.listen(1)
            
            print(f"\n🖥️  Waiting for screen share connection on port {self.listen_port}...")
            print("Press Ctrl+C to stop\n")
            
            # Accept connection
            self.client_sock, address = self.server_sock.accept()
            print(f"✓ Connected to {address[0]}:{address[1]}")
            print("Press 'q' in the window to stop\n")
            
            self.running = True
            frame_count = 0
            start_time = time.time()
            
            while self.running:
                try:
                    # Receive frame
                    frame_data = self._receive_frame()
                    
                    if frame_data is None:
                        print("\n⚠️  Connection closed")
                        break
                    
                    # Decompress and display
                    frame = self._decompress_frame(frame_data)
                    
                    if frame is not None:
                        cv2.imshow(f'Screen Share from {address[0]}', frame)
                        
                        frame_count += 1
                        
                        # Statistics
                        if frame_count % 50 == 0:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            print(f"📺 Received {frame_count} frames | {fps:.1f} FPS")
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"\n❌ Error receiving frame: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.stop_receiving()
    
    def _receive_frame(self):
        """Receive a complete frame from TCP stream"""
        try:
            # Receive frame size (4 bytes)
            size_data = self._recv_exact(4)
            if not size_data:
                return None
            
            frame_size = struct.unpack('!I', size_data)[0]
            
            # Validate size
            if frame_size > 10 * 1024 * 1024:  # Max 10MB per frame
                print(f"⚠️  Frame size too large: {frame_size}")
                return None
            
            # Receive frame data
            frame_data = self._recv_exact(frame_size)
            if not frame_data:
                return None
            
            return frame_data
            
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def _recv_exact(self, num_bytes):
        """Receive exactly num_bytes from socket"""
        data = b''
        while len(data) < num_bytes:
            chunk = self.client_sock.recv(min(num_bytes - len(data), BUFFER_SIZE))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _decompress_frame(self, data):
        """Decompress frame data to OpenCV image"""
        try:
            # Unpack protocol header
            from shared.helpers import unpack_message
            version, msg_type, payload_length, seq_num, payload = unpack_message(data)
            
            # Decode JPEG
            nparr = np.frombuffer(payload, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
        except Exception as e:
            print(f"Error decompressing frame: {e}")
            return None
    
    def stop_receiving(self):
        """Clean up resources"""
        self.running = False
        cv2.destroyAllWindows()
        
        if self.client_sock:
            self.client_sock.close()
        if self.server_sock:
            self.server_sock.close()
        
        print("\n🛑 Screen receiving stopped")


def capture_screenshot():
    """Helper function to capture a single screenshot
    
    Returns:
        PIL.Image: Captured screenshot
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        screenshot = sct.grab(monitor)
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        return img


def compress_screenshot(img, quality=VIDEO_QUALITY):
    """Helper function to compress screenshot to JPEG bytes
    
    Args:
        img (PIL.Image): Image to compress
        quality (int): JPEG quality (0-100)
        
    Returns:
        bytes: Compressed JPEG data
    """
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    return buffer.getvalue()


def send_screen_chunk(sock, data, chunk_size=BUFFER_SIZE):
    """Helper function to send data in chunks over TCP
    
    Args:
        sock (socket.socket): Connected TCP socket
        data (bytes): Data to send
        chunk_size (int): Size of each chunk
        
    Returns:
        bool: True if sent successfully
    """
    try:
        # Send total size first
        total_size = len(data)
        sock.sendall(struct.pack('!I', total_size))
        
        # Send data in chunks
        offset = 0
        while offset < total_size:
            chunk = data[offset:offset + chunk_size]
            sock.sendall(chunk)
            offset += len(chunk)
        
        return True
    except Exception as e:
        print(f"Error sending chunk: {e}")
        return False


def receive_screen_chunk(sock):
    """Helper function to receive chunked data from TCP
    
    Args:
        sock (socket.socket): Connected TCP socket
        
    Returns:
        bytes: Received data, or None if error
    """
    try:
        # Receive total size
        size_data = sock.recv(4)
        if len(size_data) < 4:
            return None
        
        total_size = struct.unpack('!I', size_data)[0]
        
        # Receive all data
        data = b''
        while len(data) < total_size:
            chunk = sock.recv(min(total_size - len(data), BUFFER_SIZE))
            if not chunk:
                return None
            data += chunk
        
        return data
    except Exception as e:
        print(f"Error receiving chunk: {e}")
        return None


def main():
    """Main function for testing screen sharing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LAN Screen Sharing')
    parser.add_argument('mode', choices=['share', 'view'],
                       help='Mode: share (stream your screen) or view (watch remote screen)')
    parser.add_argument('--ip', default='127.0.0.1',
                       help='Server IP address (for share mode)')
    parser.add_argument('--port', type=int, default=SCREEN_SHARE_PORT,
                       help=f'Port number (default: {SCREEN_SHARE_PORT})')
    parser.add_argument('--fps', type=int, default=10,
                       help='Frames per second (default: 10)')
    parser.add_argument('--quality', type=int, default=VIDEO_QUALITY,
                       help=f'JPEG quality 0-100 (default: {VIDEO_QUALITY})')
    
    args = parser.parse_args()
    
    if args.mode == 'share':
        streamer = ScreenStreamer(
            server_ip=args.ip,
            server_port=args.port,
            fps=args.fps,
            quality=args.quality
        )
        streamer.start_streaming()
    elif args.mode == 'view':
        receiver = ScreenReceiver(listen_port=args.port)
        receiver.start_receiving()


if __name__ == '__main__':
    main()
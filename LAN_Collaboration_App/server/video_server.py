"""
Video Conference Server - FIXED VERSION
Properly handles client registration for broadcasting
"""

import socket
import threading
import sys
import os
from collections import defaultdict
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import VIDEO_PORT, VIDEO_BUFFER_SIZE
from shared.protocol import VIDEO
from shared.helpers import unpack_message


class VideoConferenceServer:
    """Multi-user video conferencing server with proper registration"""
    
    def __init__(self, port=VIDEO_PORT):
        self.port = port
        self.sock = None
        self.running = False
        
        # Track ALL clients (both senders and receivers)
        self.clients = {}  # {(ip, port): last_seen_time}
        self.clients_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'clients_served': set()
        }
    
    def start(self):
        """Start the video conference server"""
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, VIDEO_BUFFER_SIZE)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, VIDEO_BUFFER_SIZE)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.settimeout(0.1)  # Non-blocking with short timeout
            
            self.running = True
            
            print(f"📹 Video Conference Server listening on UDP port {self.port}")
            print(f"📡 Broadcast mode: ALL registered clients")
            
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_stale_clients, daemon=True)
            cleanup_thread.start()
            
            # Main loop
            while self.running:
                try:
                    # Receive packet
                    data, sender_addr = self.sock.recvfrom(VIDEO_BUFFER_SIZE)
                    
                    # Try to parse message
                    try:
                        version, msg_type, payload_length, seq_num, payload = unpack_message(data)
                        
                        # Handle REGISTER messages (client wants to receive broadcasts)
                        if payload == b"REGISTER":
                            with self.clients_lock:
                                if sender_addr not in self.clients:
                                    self.clients[sender_addr] = time.time()
                                    print(f"📹 Video client registered: {sender_addr[0]}:{sender_addr[1]}")
                                else:
                                    self.clients[sender_addr] = time.time()  # Update timestamp
                            continue  # Don't broadcast REGISTER messages
                        
                        # Regular video frame - register sender and broadcast
                        with self.clients_lock:
                            self.clients[sender_addr] = time.time()
                            self.stats['clients_served'].add(sender_addr[0])
                        
                        # Update stats
                        self.stats['total_packets'] += 1
                        self.stats['total_bytes'] += len(data)
                        
                        # Broadcast to ALL registered clients
                        self._broadcast_video(data, sender_addr)
                        
                        # Log stats periodically
                        if self.stats['total_packets'] % 500 == 0:
                            self._log_stats()
                            
                    except ValueError:
                        # Invalid packet, skip
                        continue
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Video receive error: {e}")
                        
        except Exception as e:
            print(f"❌ Video server error: {e}")
        finally:
            self.stop()
    
    def _broadcast_video(self, data, sender_addr):
        """Broadcast video packet to ALL registered clients (including sender for loopback)"""
        with self.clients_lock:
            disconnected = []
            broadcast_count = 0
            
            for client_addr in list(self.clients.keys()):
                # Skip sender to avoid echo
                if client_addr == sender_addr:
                    continue
                
                try:
                    self.sock.sendto(data, client_addr)
                    broadcast_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to send to {client_addr[0]}:{client_addr[1]}: {e}")
                    disconnected.append(client_addr)
            
            # Remove disconnected clients
            for addr in disconnected:
                if addr in self.clients:
                    del self.clients[addr]
                    print(f"🔌 Video client removed: {addr[0]}:{addr[1]}")
    
    def _cleanup_stale_clients(self):
        """Remove clients that haven't sent data recently"""
        TIMEOUT = 30  # 30 seconds
        
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            
            current_time = time.time()
            with self.clients_lock:
                stale = [
                    addr for addr, last_seen in self.clients.items()
                    if current_time - last_seen > TIMEOUT
                ]
                
                for addr in stale:
                    del self.clients[addr]
                    print(f"🔌 Video client timed out: {addr[0]}:{addr[1]}")
    
    def _log_stats(self):
        """Log server statistics"""
        with self.clients_lock:
            active = len(self.clients)
        
        mbytes = self.stats['total_bytes'] / (1024 * 1024)
        print(f"📊 Video: {self.stats['total_packets']} packets | "
              f"{mbytes:.2f} MB | "
              f"{active} registered clients")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.sock:
            self.sock.close()
        print("🛑 Video server stopped")
    
    def get_stats(self):
        """Get server statistics"""
        with self.clients_lock:
            return {
                'active_clients': len(self.clients),
                'total_packets': self.stats['total_packets'],
                'total_bytes': self.stats['total_bytes'],
                'unique_clients': len(self.stats['clients_served'])
            }


if __name__ == '__main__':
    server = VideoConferenceServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n")
        server.stop()
"""
Dummy test servers for testing client modules
Provides simple echo/receive servers for each protocol
"""

import socket
import threading
import argparse
import sys
import os

# Add to path
sys.path.append(os.path.dirname(__file__))

from shared.constants import (
    VIDEO_PORT, AUDIO_PORT, CHAT_PORT, 
    FILE_TRANSFER_PORT, SCREEN_SHARE_PORT,
    BUFFER_SIZE, VIDEO_BUFFER_SIZE, AUDIO_BUFFER_SIZE
)


class DummyVideoServer:
    """Dummy UDP server for video testing"""
    
    def __init__(self, port=VIDEO_PORT):
        self.port = port
        self.sock = None
        self.running = False
    
    def start(self):
        """Start dummy video server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))
        self.running = True
        
        print(f"\n🎥 Dummy Video Server")
        print(f"📡 Listening on UDP port {self.port}")
        print("Receiving video packets (not displaying)")
        print("Press Ctrl+C to stop\n")
        
        packet_count = 0
        
        try:
            while self.running:
                data, addr = self.sock.recvfrom(VIDEO_BUFFER_SIZE)
                packet_count += 1
                
                if packet_count % 30 == 0:
                    print(f"📦 Received {packet_count} packets from {addr[0]}:{addr[1]} | "
                          f"Last size: {len(data)} bytes")
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping video server...")
        finally:
            self.sock.close()


class DummyAudioServer:
    """Dummy UDP server for audio testing"""
    
    def __init__(self, port=AUDIO_PORT):
        self.port = port
        self.sock = None
        self.running = False
    
    def start(self):
        """Start dummy audio server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))
        self.running = True
        
        print(f"\n🎵 Dummy Audio Server")
        print(f"📡 Listening on UDP port {self.port}")
        print("Receiving audio packets (not playing)")
        print("Press Ctrl+C to stop\n")
        
        packet_count = 0
        
        try:
            while self.running:
                data, addr = self.sock.recvfrom(AUDIO_BUFFER_SIZE)
                packet_count += 1
                
                if packet_count % 100 == 0:
                    print(f"🔊 Received {packet_count} packets from {addr[0]}:{addr[1]} | "
                          f"Last size: {len(data)} bytes")
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping audio server...")
        finally:
            self.sock.close()


class DummyFileServer:
    """Dummy TCP server for file transfer testing"""
    
    def __init__(self, port=FILE_TRANSFER_PORT):
        self.port = port
        self.sock = None
        self.running = False
    
    def start(self):
        """Start dummy file server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.running = True
        
        print(f"\n📁 Dummy File Transfer Server")
        print(f"📡 Listening on TCP port {self.port}")
        print("Receiving file data (not saving)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                client_sock, addr = self.sock.accept()
                print(f"✓ Client connected: {addr[0]}:{addr[1]}")
                
                threading.Thread(
                    target=self.handle_client,
                    args=(client_sock, addr),
                    daemon=True
                ).start()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping file server...")
        finally:
            self.sock.close()
    
    def handle_client(self, client_sock, addr):
        """Handle file transfer client"""
        try:
            total_received = 0
            packet_count = 0
            
            while True:
                data = client_sock.recv(BUFFER_SIZE)
                if not data:
                    break
                
                total_received += len(data)
                packet_count += 1
                
                if packet_count % 10 == 0:
                    print(f"📦 Received {total_received:,} bytes in {packet_count} packets")
            
            # Send acknowledgment
            client_sock.send(b"OK")
            
            print(f"✅ Transfer complete: {total_received:,} bytes total")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client_sock.close()


class DummyScreenServer:
    """Dummy TCP server for screen share testing"""
    
    def __init__(self, port=SCREEN_SHARE_PORT):
        self.port = port
        self.sock = None
        self.running = False
    
    def start(self):
        """Start dummy screen share server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.running = True
        
        print(f"\n🖥️  Dummy Screen Share Server")
        print(f"📡 Listening on TCP port {self.port}")
        print("Receiving screen frames (not displaying)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                client_sock, addr = self.sock.accept()
                print(f"✓ Client connected: {addr[0]}:{addr[1]}")
                
                threading.Thread(
                    target=self.handle_client,
                    args=(client_sock, addr),
                    daemon=True
                ).start()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping screen server...")
        finally:
            self.sock.close()
    
    def handle_client(self, client_sock, addr):
        """Handle screen share client"""
        try:
            frame_count = 0
            total_received = 0
            
            while True:
                # Receive frame size (4 bytes)
                size_data = client_sock.recv(4)
                if len(size_data) < 4:
                    break
                
                import struct
                frame_size = struct.unpack('!I', size_data)[0]
                
                # Receive frame data
                received = 0
                while received < frame_size:
                    chunk = client_sock.recv(min(frame_size - received, BUFFER_SIZE))
                    if not chunk:
                        break
                    received += len(chunk)
                
                frame_count += 1
                total_received += received
                
                if frame_count % 10 == 0:
                    avg_size = total_received // frame_count
                    print(f"📺 Received {frame_count} frames | "
                          f"Avg size: {avg_size//1024} KB")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            client_sock.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Dummy Test Servers')
    parser.add_argument('--mode', choices=['video', 'audio', 'file', 'screen', 'chat'],
                       default='chat',
                       help='Server type to run')
    parser.add_argument('--port', type=int,
                       help='Port to listen on (default varies by mode)')
    
    args = parser.parse_args()
    
    # Determine port
    if args.port:
        port = args.port
    else:
        ports = {
            'video': VIDEO_PORT,
            'audio': AUDIO_PORT,
            'file': FILE_TRANSFER_PORT,
            'screen': SCREEN_SHARE_PORT,
            'chat': CHAT_PORT
        }
        port = ports[args.mode]
    
    # Start appropriate server
    if args.mode == 'video':
        server = DummyVideoServer(port)
    elif args.mode == 'audio':
        server = DummyAudioServer(port)
    elif args.mode == 'file':
        server = DummyFileServer(port)
    elif args.mode == 'screen':
        server = DummyScreenServer(port)
    elif args.mode == 'chat':
        print("\n💬 For chat, use: python simple_chat_server.py\n")
        return
    
    server.start()


if __name__ == '__main__':
    main()

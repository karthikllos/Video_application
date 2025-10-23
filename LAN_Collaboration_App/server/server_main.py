"""
Main Unified Server for LAN Collaboration App
Manages all services: Video, Audio, Chat, File Transfer, Screen Sharing
"""

import sys
import os
import threading
import signal
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    VIDEO_PORT, AUDIO_PORT, CHAT_PORT,
    FILE_TRANSFER_PORT, SCREEN_SHARE_PORT
)

# Import server modules
from video_server import VideoConferenceServer
from audio_server import AudioConferenceServer
from chat_server import ChatServer
from file_server import FileTransferServer
from screen_share_server import ScreenShareServer


class UnifiedServer:
    """Unified server managing all collaboration services"""
    
    def __init__(self):
        self.servers = {}
        self.running = False
        self.server_threads = []
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start_all(self):
        """Start all server services"""
        print("\n" + "=" * 70)
        print("🌐 LAN COLLABORATION SERVER - STARTING ALL SERVICES")
        print("=" * 70)
        print(f"⏰ Server started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.running = True
        
        # Start each service in a separate thread
        services = [
            ('Video Conference', VideoConferenceServer, VIDEO_PORT),
            ('Audio Conference', AudioConferenceServer, AUDIO_PORT),
            ('Chat', ChatServer, CHAT_PORT),
            ('File Transfer', FileTransferServer, FILE_TRANSFER_PORT),
            ('Screen Share', ScreenShareServer, SCREEN_SHARE_PORT)
        ]
        
        for name, server_class, port in services:
            try:
                server = server_class(port)
                self.servers[name] = server
                
                thread = threading.Thread(
                    target=self._run_server,
                    args=(name, server),
                    daemon=True
                )
                thread.start()
                self.server_threads.append(thread)
                
                print(f"✓ {name:20s} → Port {port:5d} [RUNNING]")
                time.sleep(0.2)  # Stagger startups
                
            except Exception as e:
                print(f"✗ {name:20s} → Port {port:5d} [FAILED: {e}]")
        
        print("\n" + "=" * 70)
        print("🚀 ALL SERVICES ACTIVE")
        print("=" * 70)
        print("\n📊 Server Status Dashboard:")
        print("-" * 70)
        self._print_status()
        print("-" * 70)
        print("\n💡 Clients can now connect to this server")
        print("🛑 Press Ctrl+C to stop all services\n")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
    
    def _run_server(self, name, server):
        """Run a server instance"""
        try:
            server.start()
        except Exception as e:
            print(f"\n❌ {name} server error: {e}")
    
    def stop_all(self):
        """Stop all server services"""
        if not self.running:
            return
        
        print("\n\n" + "=" * 70)
        print("🛑 SHUTTING DOWN ALL SERVICES")
        print("=" * 70)
        
        self.running = False
        
        for name, server in self.servers.items():
            try:
                print(f"⏳ Stopping {name}...")
                server.stop()
                print(f"✓ {name} stopped")
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
        
        print("\n" + "=" * 70)
        print("✓ ALL SERVICES STOPPED")
        print("=" * 70)
        print(f"⏰ Server stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n\n⚠️  Received signal {signum}")
        self.stop_all()
        sys.exit(0)
    
    def _print_status(self):
        """Print server status"""
        print(f"  Video Conference  : Port {VIDEO_PORT}")
        print(f"  Audio Conference  : Port {AUDIO_PORT}")
        print(f"  Chat Service      : Port {CHAT_PORT}")
        print(f"  File Transfer     : Port {FILE_TRANSFER_PORT}")
        print(f"  Screen Sharing    : Port {SCREEN_SHARE_PORT}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='LAN Collaboration Server - Unified Multi-Service Server'
    )
    parser.add_argument(
        '--service',
        choices=['all', 'video', 'audio', 'chat', 'file', 'screen'],
        default='all',
        help='Service to start (default: all)'
    )
    
    args = parser.parse_args()
    
    if args.service == 'all':
        server = UnifiedServer()
        server.start_all()
    else:
        # Start individual service
        service_map = {
            'video': (VideoConferenceServer, VIDEO_PORT, 'Video Conference'),
            'audio': (AudioConferenceServer, AUDIO_PORT, 'Audio Conference'),
            'chat': (ChatServer, CHAT_PORT, 'Chat'),
            'file': (FileTransferServer, FILE_TRANSFER_PORT, 'File Transfer'),
            'screen': (ScreenShareServer, SCREEN_SHARE_PORT, 'Screen Share')
        }
        
        server_class, port, name = service_map[args.service]
        print(f"\n🚀 Starting {name} Server on port {port}...")
        
        server = server_class(port)
        try:
            server.start()
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopping {name} Server...")
            server.stop()


if __name__ == '__main__':
    main()
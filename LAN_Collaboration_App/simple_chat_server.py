"""
Simple Chat Server for testing client_chat.py
Broadcasts messages to all connected clients
"""

import socket
import threading
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from shared.constants import CHAT_PORT, BUFFER_SIZE
from shared.protocol import CHAT, DISCONNECT
from shared.helpers import pack_message, unpack_message


class SimpleChatServer:
    """Simple chat server that broadcasts messages to all clients"""
    
    def __init__(self, port=CHAT_PORT):
        self.port = port
        self.clients = []  # List of connected client sockets
        self.clients_lock = threading.Lock()
        self.running = False
        self.server_socket = None
        
    def start(self):
        """Start the chat server"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to all interfaces
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            print(f"\n🚀 Chat Server Started")
            print(f"📡 Listening on port {self.port}")
            print(f"💡 Clients can connect using:")
            print(f"   python client/client_chat.py --username <name> --ip 127.0.0.1 --port {self.port}")
            print("\nPress Ctrl+C to stop\n")
            print("=" * 60)
            
            # Accept connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    print(f"\n✓ New connection from {address[0]}:{address[1]}")
                    
                    # Add to clients list
                    with self.clients_lock:
                        self.clients.append(client_socket)
                    
                    # Start handler thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the chat server"""
        print("\n\n🛑 Shutting down chat server...")
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        print("✓ Server stopped")
    
    def _handle_client(self, client_socket, address):
        """Handle a single client connection"""
        buffer = b""
        
        try:
            while self.running:
                # Receive data
                data = client_socket.recv(BUFFER_SIZE)
                
                if not data:
                    break
                
                buffer += data
                
                # Try to extract complete messages
                while len(buffer) >= 12:
                    try:
                        version, msg_type, payload_length, seq_num, payload = unpack_message(buffer)
                        message_size = 12 + payload_length
                        
                        if len(buffer) < message_size:
                            break
                        
                        # Process message
                        if msg_type == CHAT:
                            message_text = payload.decode('utf-8')
                            print(f"📨 {message_text}")
                            
                            # Broadcast to all clients
                            self._broadcast_message(message_text, sender=client_socket)
                        
                        elif msg_type == DISCONNECT:
                            print(f"👋 Client {address[0]}:{address[1]} disconnecting")
                            break
                        
                        # Remove processed message
                        buffer = buffer[message_size:]
                        
                    except ValueError:
                        break
                    except Exception as e:
                        print(f"⚠️  Error processing message: {e}")
                        buffer = buffer[1:]
                        
        except Exception as e:
            print(f"⚠️  Client {address[0]}:{address[1]} error: {e}")
        finally:
            # Remove client from list
            with self.clients_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            
            client_socket.close()
            print(f"✗ Client {address[0]}:{address[1]} disconnected ({len(self.clients)} remaining)")
    
    def _broadcast_message(self, message, sender=None):
        """Broadcast a message to all clients except sender"""
        # Encode message
        message_bytes = message.encode('utf-8')
        packet = pack_message(CHAT, message_bytes)
        
        # Send to all clients
        with self.clients_lock:
            disconnected = []
            
            for client in self.clients:
                if client == sender:
                    continue  # Don't echo back to sender
                
                try:
                    client.sendall(packet)
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                if client in self.clients:
                    self.clients.remove(client)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Chat Server')
    parser.add_argument('--port', type=int, default=CHAT_PORT,
                       help=f'Port to listen on (default: {CHAT_PORT})')
    
    args = parser.parse_args()
    
    server = SimpleChatServer(port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n")
        server.stop()


if __name__ == '__main__':
    main()

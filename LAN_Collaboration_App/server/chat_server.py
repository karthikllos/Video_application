"""
Chat Server
Manages multi-user text chat with message broadcasting
Uses TCP for reliable message delivery
"""

import socket
import threading
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import CHAT_PORT, BUFFER_SIZE, MAX_CONNECTIONS
from shared.protocol import CHAT, DISCONNECT, USER_LIST
from shared.helpers import pack_message, unpack_message
import json


class ChatServer:
    """Multi-user chat server with broadcasting"""
    
    def __init__(self, port=CHAT_PORT):
        self.port = port
        self.server_socket = None
        self.running = False
        
        # Connected clients: {socket: {'addr': addr, 'username': username, 'connected_at': time}}
        self.clients = {}
        self.clients_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'total_connections': 0,
            'current_connections': 0
        }
    
    def start(self):
        """Start the chat server"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            
            print(f"💬 Chat Server listening on TCP port {self.port}")
            
            # Accept connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    with self.clients_lock:
                        self.stats['total_connections'] += 1
                        self.stats['current_connections'] += 1
                    
                    print(f"✓ New chat connection from {address[0]}:{address[1]}")
                    
                    # Start handler thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ Chat server error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket, address):
        """Handle a single client connection"""
        buffer = b""
        username = "Unknown"
        
        try:
            # Add to clients
            with self.clients_lock:
                self.clients[client_socket] = {
                    'addr': address,
                    'username': username,
                    'connected_at': time.time()
                }
            
            # Receive and process messages
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                
                if not data:
                    break  # Client disconnected
                
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 12:  # Minimum header size
                    try:
                        version, msg_type, payload_length, seq_num, payload = unpack_message(buffer)
                        message_size = 12 + payload_length
                        
                        if len(buffer) < message_size:
                            break  # Wait for more data
                        
                        # Process message
                        if msg_type == CHAT:
                            message_text = payload.decode('utf-8')
                            
                            # Log message
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] {message_text}")
                            
                            # Extract username from first message (join message)
                            if username == "Unknown" and ":" in message_text:
                                username = message_text.split(":", 1)[0].strip()
                                with self.clients_lock:
                                    self.clients[client_socket]['username'] = username

                                # Wait a bit to ensure username is set everywhere
                                time.sleep(0.05)



                                # NOW broadcast user list
                                self._broadcast_user_list()
                            
                            # Broadcast message to ALL clients (including sender for acknowledgment)
                            self._broadcast_message(message_text, sender=None)
                            self.stats['messages_sent'] += 1
                        
                        elif msg_type == DISCONNECT:
                            print(f"👋 {username} disconnecting")
                            break
                        
                        # Remove processed message
                        buffer = buffer[message_size:]
                        
                    except ValueError:
                        break  # Incomplete message
                    except Exception as e:
                        print(f"⚠️  Error processing message: {e}")
                        buffer = buffer[1:]  # Skip one byte
                        
        except Exception as e:
            print(f"⚠️  Client {address[0]}:{address[1]} error: {e}")
        finally:
            # Remove client
            with self.clients_lock:
                if client_socket in self.clients:
                    username = self.clients[client_socket]['username']
                    del self.clients[client_socket]
                    self.stats['current_connections'] -= 1
            
            # Announce departure and update user list
            if username != "Unknown":
                leave_msg = f"{username} has left the chat"
                self._broadcast_message(leave_msg)
                self._broadcast_user_list()
            
            client_socket.close()
            print(f"✗ {username} ({address[0]}:{address[1]}) disconnected "
                  f"[{self.stats['current_connections']} remaining]")
    
    def _broadcast_message(self, message, sender=None):
        """Broadcast message to all clients except sender"""
        message_bytes = message.encode('utf-8')
        packet = pack_message(CHAT, message_bytes)
        
        with self.clients_lock:
            disconnected = []
            
            for client_socket in list(self.clients.keys()):
                if client_socket == sender:
                    continue  # Don't echo back to sender
                
                try:
                    client_socket.sendall(packet)
                except Exception as e:
                    disconnected.append(client_socket)
            
            # Remove disconnected clients
            for socket in disconnected:
                if socket in self.clients:
                    del self.clients[socket]
    
    def _broadcast_user_list(self):
        """Broadcast updated user list to all clients"""
        with self.clients_lock:
            usernames = [info['username'] for info in self.clients.values() if info['username'] != "Unknown"]
        
        user_list_data = json.dumps(usernames).encode('utf-8')
        packet = pack_message(USER_LIST, user_list_data)
        
        with self.clients_lock:
            disconnected = []
            
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.sendall(packet)
                except Exception as e:
                    disconnected.append(client_socket)
            
            # Remove disconnected clients
            for socket in disconnected:
                if socket in self.clients:
                    del self.clients[socket]
    
    def stop(self):
        """Stop the server"""
        print("\n🛑 Shutting down chat server...")
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        print("🛑 Chat server stopped")
    
    def get_stats(self):
        """Get server statistics"""
        with self.clients_lock:
            return {
                'current_connections': self.stats['current_connections'],
                'total_connections': self.stats['total_connections'],
                'messages_sent': self.stats['messages_sent'],
                'users': [info['username'] for info in self.clients.values()]
            }


if __name__ == '__main__':
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n")
        server.stop()
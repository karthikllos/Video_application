"""
Chat client module for LAN Collaboration App
Handles TCP-based text messaging with continuous message reception
"""

import socket
import threading
import sys
import os
import time
from datetime import datetime

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, CHAT_PORT, BUFFER_SIZE,
    CONNECTION_TIMEOUT, MAX_RETRIES, RETRY_DELAY
)
from shared.protocol import CHAT, DISCONNECT, USER_LIST
from shared.helpers import pack_message, unpack_message
import json


class ChatClient:
    """Handles TCP-based chat communication"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=CHAT_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.username = ""
        self.running = False
        self.listener_thread = None
        self.user_list = []
        self.user_list_callback = None  # Callback for user list updates
        self.message_callback = None  # Callback for incoming messages
        
    def connect(self, username):
        """Connect to the chat server"""
        self.username = username
        
        try:
            # Create TCP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(CONNECTION_TIMEOUT)
            
            print(f"\n🔌 Connecting to chat server at {self.server_ip}:{self.server_port}...")
            
            # Connect to server
            self.sock.connect((self.server_ip, self.server_port))
            
            print(f"✓ Connected as '{username}'")
            print("=" * 60)
            
            # Send join message
            join_msg = f"{username} has joined the chat"
            self._send_raw_message(join_msg)
            
            # Start listening thread
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            self.listener_thread.start()
            
            return True
            
        except socket.timeout:
            print(f"❌ Connection timeout - server not responding")
            return False
        except ConnectionRefusedError:
            print(f"❌ Connection refused - is the server running?")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the chat server"""
        if self.running:
            self.running = False
            
            # Send disconnect message
            try:
                leave_msg = f"{self.username} has left the chat"
                self._send_raw_message(leave_msg)
                
                # Send protocol disconnect
                disconnect_packet = pack_message(DISCONNECT, b"")
                self.sock.sendall(disconnect_packet)
            except:
                pass
            
            # Close socket
            if self.sock:
                self.sock.close()
            
            print("\n🛑 Disconnected from chat server")
    
    def send_message(self, text):
        """Send a chat message with username formatting"""
        if not self.running or not self.sock:
            print("❌ Not connected to server")
            return False
        
        # Format message as "username: text"
        formatted_message = f"{self.username}: {text}"
        return self._send_raw_message(formatted_message)
    
    def _send_raw_message(self, message):
        """Send a raw message to server"""
        try:
            # Encode message as UTF-8
            message_bytes = message.encode('utf-8')
            
            # Pack with protocol header
            packet = pack_message(CHAT, message_bytes)
            
            # Send via TCP
            self.sock.sendall(packet)
            return True
            
        except BrokenPipeError:
            print("\n❌ Connection lost - server disconnected")
            self.running = False
            return False
        except Exception as e:
            print(f"\n❌ Error sending message: {e}")
            return False
    
    def _listen_for_messages(self):
        """Continuously listen for incoming messages (runs in thread)"""
        print("👂 Listening for messages...\n")
        
        buffer = b""
        
        while self.running:
            try:
                # Receive data
                data = self.sock.recv(BUFFER_SIZE)
                
                if not data:
                    # Server closed connection
                    print("\n⚠️  Server closed the connection")
                    self.running = False
                    break
                
                buffer += data
                
                # Try to extract complete messages from buffer
                while len(buffer) >= 12:  # Minimum header size
                    try:
                        # Try to unpack message
                        version, msg_type, payload_length, seq_num, payload = unpack_message(buffer)
                        
                        # Calculate total message size
                        message_size = 12 + payload_length
                        
                        # Check if we have the complete message
                        if len(buffer) < message_size:
                            break  # Wait for more data
                        
                        # Decode and display message
                        if msg_type == CHAT:
                            message_text = payload.decode('utf-8')
                            self._display_message(message_text)
                        elif msg_type == USER_LIST:
                            user_list_json = payload.decode('utf-8')
                            self.user_list = json.loads(user_list_json)
                            if self.user_list_callback:
                                self.user_list_callback(self.user_list)
                        
                        # Remove processed message from buffer
                        buffer = buffer[message_size:]
                        
                    except ValueError:
                        # Incomplete message, wait for more data
                        break
                    except Exception as e:
                        print(f"\n⚠️  Error processing message: {e}")
                        buffer = buffer[1:]  # Skip one byte and try again
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"\n❌ Error receiving message: {e}")
                break
        
        print("\n👂 Stopped listening for messages")
    
    def _display_message(self, message):
        """Display a received message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # Call callback if set
        if self.message_callback:
            self.message_callback(message, timestamp)
    
    def set_user_list_callback(self, callback):
        """Set callback function for user list updates"""
        self.user_list_callback = callback
    
    def set_message_callback(self, callback):
        """Set callback function for incoming messages"""
        self.message_callback = callback
    
    def get_user_list(self):
        """Get current user list"""
        return self.user_list.copy()
    
    def start_interactive_mode(self):
        """Start interactive chat mode"""
        print("\n" + "=" * 60)
        print("💬 CHAT READY - Type your messages below")
        print("Commands: /quit to exit, /help for help")
        print("=" * 60 + "\n")
        
        try:
            while self.running:
                try:
                    # Read user input
                    message = input()
                    
                    if not message:
                        continue
                    
                    # Handle commands
                    if message.startswith('/'):
                        self._handle_command(message)
                    else:
                        # Send regular message
                        self.send_message(message)
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
        finally:
            self.disconnect()
    
    def _handle_command(self, command):
        """Handle chat commands"""
        cmd = command.lower().strip()
        
        if cmd == '/quit' or cmd == '/exit':
            print("\n👋 Leaving chat...")
            self.running = False
        elif cmd == '/help':
            print("\n📖 Available commands:")
            print("  /quit or /exit  - Leave the chat")
            print("  /help           - Show this help message")
            print("  /status         - Show connection status")
            print()
        elif cmd == '/status':
            status = "Connected" if self.running else "Disconnected"
            print(f"\n📊 Status: {status}")
            print(f"   Username: {self.username}")
            print(f"   Server: {self.server_ip}:{self.server_port}")
            print()
        else:
            print(f"\n❓ Unknown command: {command}")
            print("   Type /help for available commands\n")


def send_message(sock, username, text):
    """Helper function to send a formatted message
    
    Args:
        sock (socket.socket): Connected TCP socket
        username (str): Sender's username
        text (str): Message text
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Format message as "username: text"
        formatted_message = f"{username}: {text}"
        
        # Encode as UTF-8
        message_bytes = formatted_message.encode('utf-8')
        
        # Pack with protocol header
        packet = pack_message(CHAT, message_bytes)
        
        # Send via TCP
        sock.sendall(packet)
        return True
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def receive_message(sock, timeout=None):
    """Helper function to receive and decode a message
    
    Args:
        sock (socket.socket): Connected TCP socket
        timeout (float): Optional timeout in seconds
        
    Returns:
        str: Decoded message text, or None if error
    """
    try:
        if timeout:
            sock.settimeout(timeout)
        
        # Receive header first
        header = sock.recv(12)
        if len(header) < 12:
            return None
        
        # Parse payload length from header
        import struct
        payload_length = struct.unpack('!I', header[2:6])[0]
        
        # Receive payload
        payload = b""
        while len(payload) < payload_length:
            chunk = sock.recv(min(payload_length - len(payload), BUFFER_SIZE))
            if not chunk:
                return None
            payload += chunk
        
        # Unpack complete message
        complete_data = header + payload
        version, msg_type, payload_length, seq_num, payload = unpack_message(complete_data)
        
        # Decode UTF-8 message
        if msg_type == CHAT:
            return payload.decode('utf-8')
        
        return None
        
    except socket.timeout:
        return None
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None


def main():
    """Main function for testing chat client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LAN Chat Client')
    parser.add_argument('--username', '-u', required=True,
                       help='Your username')
    parser.add_argument('--ip', default='127.0.0.1',
                       help='Chat server IP address')
    parser.add_argument('--port', type=int, default=CHAT_PORT,
                       help=f'Chat server port (default: {CHAT_PORT})')
    
    args = parser.parse_args()
    
    # Create and connect client
    client = ChatClient(server_ip=args.ip, server_port=args.port)
    
    if client.connect(args.username):
        # Start interactive chat
        client.start_interactive_mode()
    else:
        print("\n❌ Failed to connect to chat server")
        sys.exit(1)


if __name__ == '__main__':
    main()
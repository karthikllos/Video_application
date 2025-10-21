import socket
import threading

class Discovery:
    def __init__(self, port=5000):
        self.port = port
        self.servers = []

    def discover_servers(self):
        """Broadcast a message to discover available servers on the LAN."""
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind(('', self.port))

        message = b'DISCOVER_SERVERS'
        broadcast_socket.sendto(message, ('<broadcast>', self.port))

        # Listen for responses
        threading.Thread(target=self.listen_for_servers, args=(broadcast_socket,), daemon=True).start()

    def listen_for_servers(self, broadcast_socket):
        """Listen for server responses to the discovery message."""
        while True:
            try:
                data, addr = broadcast_socket.recvfrom(1024)
                if data == b'SERVER_RESPONSE':
                    self.servers.append(addr[0])
                    print(f"Discovered server at {addr[0]}")
            except Exception as e:
                print(f"Error while listening for servers: {e}")
                break

    def get_discovered_servers(self):
        """Return the list of discovered servers."""
        return self.servers
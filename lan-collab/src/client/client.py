# File: /lan-collab/lan-collab/src/client/client.py

import socket
import sys
from ui import UserInterface

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ui = UserInterface(self)

    def connect(self):
        try:
            self.socket.connect((self.server_ip, self.server_port))
            self.ui.display_message("Connected to server.")
        except Exception as e:
            self.ui.display_message(f"Connection failed: {e}")
            sys.exit(1)

    def send_message(self, message):
        try:
            self.socket.sendall(message.encode('utf-8'))
            self.ui.display_message("Message sent.")
        except Exception as e:
            self.ui.display_message(f"Failed to send message: {e}")

    def receive_message(self):
        try:
            response = self.socket.recv(1024).decode('utf-8')
            self.ui.display_message(f"Received message: {response}")
        except Exception as e:
            self.ui.display_message(f"Failed to receive message: {e}")

    def run(self):
        self.connect()
        self.ui.run()

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    client = Client(server_ip, server_port)
    client.run()
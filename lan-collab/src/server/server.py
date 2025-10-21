from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Store active sessions
active_sessions = {}

def handle_client_connection(client_socket, address):
    # Handle incoming messages from the client
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            # Process the message (this can be expanded)
            print(f"Received message from {address}: {message}")
            # Echo the message back to the client
            client_socket.send(f"Echo: {message}".encode('utf-8'))
        except Exception as e:
            print(f"Error handling message from {address}: {e}")
            break
    client_socket.close()

@app.route('/start', methods=['POST'])
def start_server():
    # Start the server and listen for incoming connections
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    return jsonify({"status": "Server started"}), 200

def run_server():
    import socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(5)
    print("Server listening on port 5000")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Accepted connection from {address}")
        threading.Thread(target=handle_client_connection, args=(client_socket, address)).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
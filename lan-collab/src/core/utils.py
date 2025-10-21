def get_ip_address():
    import socket
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def format_message(message):
    return message.strip()

def log_event(event):
    with open('event_log.txt', 'a') as log_file:
        log_file.write(f"{event}\n")
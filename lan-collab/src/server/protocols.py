# File: /lan-collab/lan-collab/src/server/protocols.py

class Protocols:
    @staticmethod
    def handshake():
        return {
            "type": "handshake",
            "message": "Hello from the server!"
        }

    @staticmethod
    def message(data):
        return {
            "type": "message",
            "content": data
        }

    @staticmethod
    def disconnect():
        return {
            "type": "disconnect",
            "message": "Client has disconnected."
        }

    @staticmethod
    def error(message):
        return {
            "type": "error",
            "message": message
        }
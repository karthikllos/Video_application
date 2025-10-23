"""
Protocol definitions for LAN Collaboration App
Defines all message types and their identifiers
"""

# Message Type Constants
VIDEO = 0x01
AUDIO = 0x02
CHAT = 0x03
FILE_UPLOAD = 0x04
FILE_DOWNLOAD = 0x05
SCREEN_SHARE = 0x06
HANDSHAKE = 0x07
DISCONNECT = 0x08
ACK = 0x09
HEARTBEAT = 0x0A
USER_LIST_REQUEST = 0x0B
USER_LIST_RESPONSE = 0x0C
FILE_METADATA = 0x0D
FILE_CHUNK = 0x0E
ERROR = 0xFF

# Message Type Names (for debugging/logging)
MESSAGE_TYPES = {
    VIDEO: "VIDEO",
    AUDIO: "AUDIO",
    CHAT: "CHAT",
    FILE_UPLOAD: "FILE_UPLOAD",
    FILE_DOWNLOAD: "FILE_DOWNLOAD",
    SCREEN_SHARE: "SCREEN_SHARE",
    HANDSHAKE: "HANDSHAKE",
    DISCONNECT: "DISCONNECT",
    ACK: "ACK",
    HEARTBEAT: "HEARTBEAT",
    USER_LIST_REQUEST: "USER_LIST_REQUEST",
    USER_LIST_RESPONSE: "USER_LIST_RESPONSE",
    FILE_METADATA: "FILE_METADATA",
    FILE_CHUNK: "FILE_CHUNK",
    ERROR: "ERROR"
}

def get_message_type_name(msg_type):
    """Get the name of a message type from its code"""
    return MESSAGE_TYPES.get(msg_type, f"UNKNOWN({hex(msg_type)})")
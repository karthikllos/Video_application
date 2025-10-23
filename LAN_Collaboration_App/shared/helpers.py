"""
Helper functions for message serialization and deserialization
Uses struct for efficient binary packing/unpacking
"""

import struct
from shared.constants import HEADER_SIZE, PROTOCOL_VERSION, MAX_MESSAGE_SIZE

def pack_message(msg_type, payload=b""):
    """
    Pack a message with header and payload for network transmission
    
    Header Format (12 bytes):
    - Version (1 byte): Protocol version
    - Message Type (1 byte): Type of message (from protocol.py)
    - Payload Length (4 bytes): Length of payload data
    - Sequence Number (4 bytes): Message sequence number
    - Reserved (2 bytes): Reserved for future use
    
    Args:
        msg_type (int): Message type constant from protocol.py
        payload (bytes): Message payload data
        
    Returns:
        bytes: Packed message (header + payload)
        
    Raises:
        ValueError: If payload exceeds maximum message size
    """
    if not isinstance(payload, bytes):
        payload = str(payload).encode('utf-8')
    
    payload_length = len(payload)
    
    if payload_length > MAX_MESSAGE_SIZE:
        raise ValueError(f"Payload size {payload_length} exceeds maximum {MAX_MESSAGE_SIZE}")
    
    # Static sequence number (can be enhanced with actual sequence tracking)
    sequence_number = 0
    reserved = 0
    
    # Pack header: !BBIHH = network byte order, unsigned char, unsigned char, 
    # unsigned int, unsigned short, unsigned short
    header = struct.pack(
        '!BBIHH',
        PROTOCOL_VERSION,    # 1 byte
        msg_type,            # 1 byte
        payload_length,      # 4 bytes
        sequence_number,     # 4 bytes
        reserved             # 2 bytes
    )
    
    return header + payload


def unpack_message(data):
    """
    Unpack a message into header components and payload
    
    Args:
        data (bytes): Raw message data from network
        
    Returns:
        tuple: (version, msg_type, payload_length, sequence_number, payload)
            - version (int): Protocol version
            - msg_type (int): Message type
            - payload_length (int): Length of payload
            - sequence_number (int): Sequence number
            - payload (bytes): Message payload data
            
    Raises:
        ValueError: If data is too short or corrupted
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Data too short: {len(data)} bytes (minimum {HEADER_SIZE})")
    
    # Unpack header
    header = data[:HEADER_SIZE]
    payload = data[HEADER_SIZE:]
    
    try:
        version, msg_type, payload_length, sequence_number, reserved = struct.unpack(
            '!BBIHH',
            header
        )
    except struct.error as e:
        raise ValueError(f"Failed to unpack header: {e}")
    
    # Validate payload length
    if len(payload) != payload_length:
        raise ValueError(
            f"Payload length mismatch: expected {payload_length}, got {len(payload)}"
        )
    
    # Validate protocol version
    if version != PROTOCOL_VERSION:
        raise ValueError(
            f"Protocol version mismatch: expected {PROTOCOL_VERSION}, got {version}"
        )
    
    return version, msg_type, payload_length, sequence_number, payload


def pack_string(text):
    """
    Pack a string with its length prefix
    
    Args:
        text (str): String to pack
        
    Returns:
        bytes: Length-prefixed string
    """
    encoded = text.encode('utf-8')
    length = len(encoded)
    return struct.pack('!I', length) + encoded


def unpack_string(data, offset=0):
    """
    Unpack a length-prefixed string
    
    Args:
        data (bytes): Data containing the string
        offset (int): Starting position in data
        
    Returns:
        tuple: (string, new_offset)
    """
    length = struct.unpack('!I', data[offset:offset+4])[0]
    offset += 4
    text = data[offset:offset+length].decode('utf-8')
    offset += length
    return text, offset


def pack_file_metadata(filename, filesize, checksum=""):
    """
    Pack file metadata for file transfer
    
    Args:
        filename (str): Name of the file
        filesize (int): Size of file in bytes
        checksum (str): Optional file checksum
        
    Returns:
        bytes: Packed file metadata
    """
    filename_bytes = filename.encode('utf-8')
    checksum_bytes = checksum.encode('utf-8')
    
    # Format: filename_length(4) + filename + filesize(8) + checksum_length(4) + checksum
    metadata = struct.pack('!I', len(filename_bytes))
    metadata += filename_bytes
    metadata += struct.pack('!Q', filesize)
    metadata += struct.pack('!I', len(checksum_bytes))
    metadata += checksum_bytes
    
    return metadata


def unpack_file_metadata(data):
    """
    Unpack file metadata
    
    Args:
        data (bytes): Packed file metadata
        
    Returns:
        dict: File metadata with keys: filename, filesize, checksum
    """
    offset = 0
    
    # Unpack filename
    filename_length = struct.unpack('!I', data[offset:offset+4])[0]
    offset += 4
    filename = data[offset:offset+filename_length].decode('utf-8')
    offset += filename_length
    
    # Unpack filesize
    filesize = struct.unpack('!Q', data[offset:offset+8])[0]
    offset += 8
    
    # Unpack checksum
    checksum_length = struct.unpack('!I', data[offset:offset+4])[0]
    offset += 4
    checksum = data[offset:offset+checksum_length].decode('utf-8')
    
    return {
        'filename': filename,
        'filesize': filesize,
        'checksum': checksum
    }

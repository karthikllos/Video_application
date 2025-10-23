"""
Constants and configuration values for LAN Collaboration App
Stores all port numbers, buffer sizes, timeouts, and connection settings
"""

# Server Configuration
SERVER_IP = "0.0.0.0"  # Placeholder - will be replaced with actual server IP
DEFAULT_SERVER_PORT = 5000

# Service-Specific Ports
VIDEO_PORT = 5001
AUDIO_PORT = 5002
CHAT_PORT = 5003
FILE_TRANSFER_PORT = 5004
SCREEN_SHARE_PORT = 5005
DISCOVERY_PORT = 5006

# Buffer Sizes (in bytes)
BUFFER_SIZE = 4096           # Default buffer size
HEADER_SIZE = 12             # Fixed header size for message packets
VIDEO_BUFFER_SIZE = 65536    # 64 KB for video frames
AUDIO_BUFFER_SIZE = 8192     # 8 KB for audio chunks
FILE_CHUNK_SIZE = 32768      # 32 KB for file transfers
MAX_MESSAGE_SIZE = 1048576   # 1 MB maximum message size

# Timeouts (in seconds)
CONNECTION_TIMEOUT = 30
SOCKET_TIMEOUT = 10
HEARTBEAT_INTERVAL = 5
DISCOVERY_TIMEOUT = 3

# Network Settings
MAX_CONNECTIONS = 10
BROADCAST_ADDRESS = "255.255.255.255"
MULTICAST_GROUP = "224.0.0.1"

# Video Settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 30
VIDEO_QUALITY = 80  # JPEG compression quality (0-100)

# Audio Settings
AUDIO_RATE = 44100      # Sample rate in Hz
AUDIO_CHANNELS = 2      # Stereo
AUDIO_CHUNK = 1024      # Frames per buffer
AUDIO_FORMAT = 16       # Bits per sample (16-bit)

# File Transfer Settings
MAX_FILENAME_LENGTH = 255
MAX_FILE_SIZE = 104857600  # 100 MB

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Protocol Version
PROTOCOL_VERSION = 1
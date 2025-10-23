# LAN Collaboration App

A comprehensive LAN-based collaboration platform supporting video conferencing, audio chat, text messaging, file transfer, and screen sharing.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Network Configuration](#network-configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## 🎯 Overview

LAN Collaboration App is a multi-service collaboration platform designed for local area networks. It provides real-time communication features without requiring internet connectivity, making it ideal for educational institutions, offices, and secure environments.

### Key Components

- **Unified Server**: Manages all services on dedicated ports
- **Client Application**: PyQt5-based GUI for accessing all features
- **Shared Protocol**: Custom binary protocol for efficient data transmission

---

## ✨ Features

### 1. **Video Conferencing**
- Multi-user video streaming
- Configurable resolution (default: 640x480)
- Real-time frame broadcasting
- UDP-based for low latency

### 2. **Audio Conferencing**
- Multi-user audio mixing
- Real-time audio streaming
- Server-side audio mixing (clients hear each other)
- 44.1kHz stereo audio support

### 3. **Text Chat**
- Group chat functionality
- Message broadcasting
- Username support
- Connection status tracking

### 4. **File Transfer**
- Upload/Download files to/from server
- MD5 checksum verification
- Progress tracking
- Support for files up to 100MB

### 5. **Screen Sharing**
- Desktop streaming
- Presenter/Viewer model
- Real-time screen broadcasting
- Multiple viewers supported

---

## 🏗️ Architecture

```
LAN_Collaboration_App/
├── server/                    # Server-side code
│   ├── server_main.py        # Unified server managing all services
│   ├── video_server.py       # Video conferencing server (UDP)
│   ├── audio_server.py       # Audio conferencing server (UDP)
│   ├── chat_server.py        # Text chat server (TCP)
│   ├── file_server.py        # File transfer server (TCP)
│   ├── screen_share_server.py # Screen sharing server (TCP)
│   └── utils/                # Server utilities
│       ├── audio_mixer.py    # Audio mixing logic
│       ├── server_logger.py  # Logging utilities
│       └── session_manager.py # Client session management
│
├── client/                    # Client-side code
│   ├── client_gui.py         # Main PyQt5 GUI application
│   ├── client_main.py        # Client initialization
│   ├── client_config.py      # Client configuration
│   ├── client_video.py       # Video streaming client
│   ├── client_audio.py       # Audio streaming client
│   ├── client_chat.py        # Chat client
│   ├── client_file_transfer.py # File transfer client
│   ├── client_screen_share.py  # Screen sharing client
│   └── utils/                # Client utilities
│       ├── video_tools.py    # Video encoding/decoding
│       ├── audio_tools.py    # Audio processing
│       ├── compression.py    # Data compression
│       ├── file_utils.py     # File handling
│       └── network_utils.py  # Network utilities
│
└── shared/                    # Shared code between client and server
    ├── constants.py          # Configuration constants
    ├── protocol.py           # Message type definitions
    └── helpers.py            # Serialization/deserialization functions
```

### Port Assignments

| Service         | Port | Protocol | Purpose                        |
|----------------|------|----------|--------------------------------|
| Main Server    | 5000 | TCP      | Default/Reserved               |
| Video          | 5001 | UDP      | Video frame streaming          |
| Audio          | 5002 | UDP      | Audio chunk streaming          |
| Chat           | 5003 | TCP      | Text message exchange          |
| File Transfer  | 5004 | TCP      | File upload/download           |
| Screen Share   | 5005 | TCP      | Screen frame streaming         |
| Discovery      | 5006 | UDP      | Server discovery (future use)  |

---

## 💻 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, Linux, or macOS
- **RAM**: Minimum 4GB (8GB recommended)
- **Network**: Connected to the same LAN

### Python Dependencies

```txt
opencv-python>=4.8.0      # Video processing
pyaudio>=0.2.11          # Audio I/O
PyQt5>=5.15.9            # GUI framework
numpy>=1.24.0            # Numerical computing
tqdm>=4.65.0             # Progress bars
mss>=9.0.0               # Screen capture
Pillow>=10.0.0           # Image processing
```

### Platform-Specific Requirements

**Windows:**
- PyAudio may require manual wheel installation
- Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3-pyaudio portaudio19-dev python3-pyqt5
```

**macOS:**
```bash
brew install portaudio
```

---

## 📦 Installation

### Step 1: Clone or Download

Navigate to the project directory:
```bash
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

Check that all packages are installed:
```bash
python -c "import cv2, pyaudio, PyQt5, numpy, mss, PIL; print('All packages installed successfully!')"
```

---

## 🚀 Quick Start

### Option 1: Using Batch Files (Windows)

#### Start Server:
```bash
run_server.bat
```

#### Start Client(s):
```bash
run_client.bat
```

### Option 2: Manual Execution

#### Start Server:
```bash
python server/server_main.py
```

#### Start Client:
```bash
python client/client_gui.py
```

### Option 3: Start Individual Services

Start only specific services:

```bash
# Video only
python server/server_main.py --service video

# Audio only
python server/server_main.py --service audio

# Chat only
python server/server_main.py --service chat

# File transfer only
python server/server_main.py --service file

# Screen sharing only
python server/server_main.py --service screen
```

---

## 📖 Detailed Usage

### Server Setup

1. **Start the Server:**
   - Run `run_server.bat` (Windows) or `python server/server_main.py`
   - Note the IP address displayed (e.g., `192.168.1.100`)
   - Server will start all services on ports 5001-5006

2. **Server Output:**
   ```
   🌐 LAN COLLABORATION SERVER - STARTING ALL SERVICES
   ======================================================================
   ✓ Video Conference    → Port  5001 [RUNNING]
   ✓ Audio Conference    → Port  5002 [RUNNING]
   ✓ Chat                → Port  5003 [RUNNING]
   ✓ File Transfer       → Port  5004 [RUNNING]
   ✓ Screen Share        → Port  5005 [RUNNING]
   ======================================================================
   🚀 ALL SERVICES ACTIVE
   💡 Clients can now connect to this server
   🛑 Press Ctrl+C to stop all services
   ```

3. **Share the Server IP with Clients**

### Client Setup

1. **Launch the Client:**
   - Run `run_client.bat` (Windows) or `python client/client_gui.py`

2. **Connect to Server:**
   - Enter the server IP address (e.g., `192.168.1.100`)
   - Click "Connect"

3. **Using Features:**

#### Video Conferencing
- Click "Start Video" to begin streaming your camera
- Your video will be broadcast to all other clients
- You'll see other clients' video streams in the interface

#### Audio Chat
- Click "Start Audio" to begin voice communication
- Server mixes all audio streams automatically
- You'll hear all other connected users

#### Text Chat
- Enter your message in the text box
- Press Enter or click Send
- Messages are broadcast to all connected users
- Chat history is displayed in the window

#### File Transfer

**Upload File:**
1. Click "Upload File"
2. Select a file from your computer
3. File is sent to the server
4. Progress bar shows upload status
5. MD5 checksum is verified

**Download File:**
1. Click "List Files" to see available files
2. Select a file from the list
3. Click "Download"
4. Choose save location
5. Progress bar shows download status

#### Screen Sharing

**As Presenter:**
1. Click "Start Screen Share"
2. Your screen will be captured and streamed
3. All viewers will see your screen in real-time

**As Viewer:**
1. Click "View Screen Share"
2. You'll see the presenter's screen
3. Multiple viewers can watch simultaneously

---

## 🌐 Network Configuration

### Finding Your Server IP

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Linux/macOS:**
```bash
ifconfig
# or
ip addr show
```
Look for inet address under your network interface

### Firewall Configuration

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Advanced Settings"
3. Create inbound rules for ports 5001-5006
4. Allow Python through firewall

**Linux (UFW):**
```bash
sudo ufw allow 5001:5006/tcp
sudo ufw allow 5001:5006/udp
```

**macOS:**
```bash
# Allow Python through firewall in System Preferences > Security & Privacy > Firewall
```

### Network Requirements
- All devices must be on the same LAN
- No special router configuration needed for LAN use
- Ensure no network segmentation/isolation between devices

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Cannot connect to server"

**Causes & Solutions:**
- Server not running → Start the server first
- Wrong IP address → Verify server IP with `ipconfig`/`ifconfig`
- Firewall blocking → Check firewall settings
- Different networks → Ensure same LAN/WiFi

#### 2. "PyAudio installation failed"

**Windows Solution:**
1. Download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Choose the correct version (e.g., `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl` for Python 3.9)
3. Install: `pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`

**Linux Solution:**
```bash
sudo apt install python3-pyaudio portaudio19-dev
pip install pyaudio
```

#### 3. "No video/audio device found"

**Solutions:**
- Ensure camera/microphone is connected
- Check device permissions
- Restart the application
- Try a different USB port

#### 4. "Port already in use"

**Solutions:**
- Check if another instance is running
- Kill the process using the port:
  - Windows: `netstat -ano | findstr :5001` then `taskkill /PID <PID> /F`
  - Linux/macOS: `lsof -ti:5001 | xargs kill`
- Change port numbers in `shared/constants.py`

#### 5. "File transfer fails"

**Solutions:**
- Check file size (must be < 100MB)
- Verify network stability
- Ensure sufficient disk space
- Check file permissions

### Debug Mode

Enable verbose logging by setting environment variable:

**Windows:**
```bash
set DEBUG=1
python server/server_main.py
```

**Linux/macOS:**
```bash
export DEBUG=1
python server/server_main.py
```

---

## 👨‍💻 Development

### Project Structure

- **`shared/`**: Protocol definitions and utilities shared between client and server
- **`server/`**: All server-side implementations
- **`client/`**: All client-side implementations and GUI

### Protocol Details

#### Message Format
```
Header (12 bytes):
  - Version (1 byte): Protocol version
  - Message Type (1 byte): Type identifier
  - Payload Length (4 bytes): Size of payload
  - Sequence Number (4 bytes): Message sequence
  - Reserved (2 bytes): Future use

Payload (variable): Actual message data
```

#### Message Types
```python
VIDEO = 0x01           # Video frame data
AUDIO = 0x02           # Audio chunk data
CHAT = 0x03            # Chat message
FILE_UPLOAD = 0x04     # File upload request
FILE_DOWNLOAD = 0x05   # File download request
SCREEN_SHARE = 0x06    # Screen frame data
HANDSHAKE = 0x07       # Connection handshake
DISCONNECT = 0x08      # Disconnect notification
ACK = 0x09             # Acknowledgment
HEARTBEAT = 0x0A       # Keep-alive ping
```

### Extending the Application

#### Adding a New Service

1. Create server module in `server/your_service_server.py`
2. Create client module in `client/client_your_service.py`
3. Add message type to `shared/protocol.py`
4. Add port to `shared/constants.py`
5. Integrate into `server_main.py` and `client_gui.py`

#### Modifying Configuration

Edit `shared/constants.py` to change:
- Port numbers
- Buffer sizes
- Video/audio quality settings
- Timeouts and intervals

### Testing

Run individual services for testing:

```bash
# Test video server
python server/video_server.py

# Test audio server
python server/audio_server.py

# Test chat server
python server/chat_server.py
```

Test utilities are available:
- `test_audio_streaming.py` - Audio functionality test
- `test_video_streaming.py` - Video functionality test
- `test_dummy_servers.py` - Mock server testing
- `simple_chat_server.py` - Standalone chat test

---

## 📊 Performance Notes

### Network Bandwidth

Approximate bandwidth usage per client:

| Service      | Bandwidth      | Protocol |
|-------------|----------------|----------|
| Video       | ~1-2 Mbps     | UDP      |
| Audio       | ~128-256 Kbps | UDP      |
| Chat        | ~1-10 Kbps    | TCP      |
| Screen Share| ~2-5 Mbps     | TCP      |

### Scalability

- Recommended max clients: 10 simultaneous users
- Video quality automatically adjusts based on compression
- Audio mixing scales with number of participants
- File transfer uses separate connections (no bottleneck)

---

## 📝 License

This project is for educational purposes as part of the Computer Networks course (Sem5/CN).

---

## 🤝 Contributing

This is an academic project. For improvements or bug fixes:
1. Test your changes thoroughly
2. Document any new features
3. Update this README as needed

---

## ⚙️ Configuration Reference

### Default Values (shared/constants.py)

```python
# Ports
VIDEO_PORT = 5001
AUDIO_PORT = 5002
CHAT_PORT = 5003
FILE_TRANSFER_PORT = 5004
SCREEN_SHARE_PORT = 5005

# Video Settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 30
VIDEO_QUALITY = 80  # JPEG quality

# Audio Settings
AUDIO_RATE = 44100    # Hz
AUDIO_CHANNELS = 2    # Stereo
AUDIO_CHUNK = 1024    # Frames per buffer

# Buffer Sizes
BUFFER_SIZE = 4096
VIDEO_BUFFER_SIZE = 65536
AUDIO_BUFFER_SIZE = 8192
FILE_CHUNK_SIZE = 32768

# Limits
MAX_FILE_SIZE = 104857600  # 100 MB
MAX_CONNECTIONS = 10
```

---

## 📞 Support

For issues related to this project, refer to:
- This README file
- Code comments in source files
- Test scripts for examples

---

**Version**: 1.0  
**Last Updated**: 2025  
**Course**: Computer Networks (CN) - Semester 5

---

## 🎓 Academic Notes

This project demonstrates:
- Socket programming (TCP/UDP)
- Client-server architecture
- Binary protocol design
- Multi-threading
- Audio/video streaming
- Real-time data transmission
- Network application development

**Key Learning Outcomes:**
- Understanding network protocols
- Implementing reliable vs unreliable data transmission
- Managing concurrent connections
- Handling real-time streaming data
- Building cross-platform network applications

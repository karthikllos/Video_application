# LAN Collaboration App - Setup Guide

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Client Setup](#client-setup)
- [Running the Application](#running-the-application)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements:
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4 GB (8 GB recommended)
- **Network**: Local Area Network (LAN) connection
- **Webcam**: Optional (for video streaming)
- **Microphone**: Optional (for audio streaming)
- **Display**: 1280x720 or higher

### Hardware Peripherals:
- Webcam (USB or built-in) for video calls
- Microphone (USB or built-in) for audio streaming
- Speakers/Headphones for audio playback

---

## 📥 Installation

### Step 1: Install Python

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Click "Install Now"
5. Verify installation:
   ```powershell
   python --version
   ```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python3
```

### Step 2: Clone or Download Project

```powershell
# If using Git:
git clone <repository-url>
cd LAN_Collaboration_App

# Or extract from ZIP:
# Download ZIP, extract, then:
cd LAN_Collaboration_App
```

### Step 3: Install Dependencies

**Option A: Using requirements.txt (Recommended)**
```powershell
pip install -r requirements.txt
```

**Option B: Manual Installation**
```powershell
pip install opencv-python pyaudio PyQt5 numpy tqdm mss pillow
```

### Step 4: Verify Installation

```powershell
python -c "import cv2, pyaudio, PyQt5, numpy, mss, PIL; print('✅ All dependencies installed!')"
```

---

## 🚀 Quick Start

### 1. Start Chat Server (One Machine)

```powershell
python simple_chat_server.py
```

Expected output:
```
🚀 Chat Server Started
📡 Listening on port 5003
Press Ctrl+C to stop
```

### 2. Run Client on Each Machine

**Windows:**
```powershell
run_client.bat
```

**Linux/Mac:**
```bash
python client/client_gui.py
```

### 3. Connect to Server

1. Application will prompt for:
   - **Username**: Enter your name (e.g., "Alice")
   - **Server IP**: Enter server's IP address (e.g., "192.168.1.100")
   
2. Click "OK"

3. You're ready to collaborate!

---

## 🔧 Client Setup

### Finding Server IP Address

**On Server Machine:**

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" under your network adapter (e.g., `192.168.1.100`)

**Linux/Mac:**
```bash
ip addr show
# or
ifconfig
```

### Configuration File

Edit `client/client_config.py` to change default settings:

```python
# Server settings
DEFAULT_SERVER_IP = "192.168.1.100"  # Change to your server IP
DEFAULT_USERNAME = "User"

# Port settings
VIDEO_PORT = 5001
AUDIO_PORT = 5002
CHAT_PORT = 5003
FILE_TRANSFER_PORT = 5004
SCREEN_SHARE_PORT = 5005
```

### Network Configuration

#### Firewall Rules (Windows)

1. Open **Windows Defender Firewall**
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Allow another app..."
4. Browse and add:
   - `python.exe` (usually in `C:\Users\<YourName>\AppData\Local\Programs\Python\`)
   - `pythonw.exe` (same directory)
5. ✅ Check both "Private" and "Public" networks
6. Click "OK"

#### Firewall Rules (Linux)

```bash
# Allow Python through firewall
sudo ufw allow from 192.168.1.0/24 to any port 5001:5005 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 5001:5002 proto udp
```

#### Router Configuration (Optional)

For connections across different networks:
1. Access router admin panel (usually `192.168.1.1`)
2. Port forwarding:
   - Forward ports 5001-5005 to server machine's local IP
3. Use public IP address for remote connections

---

## 🎮 Running the Application

### Method 1: Using Batch File (Windows)

**Double-click:**
```
run_client.bat
```

### Method 2: Using Command Line

**Windows:**
```powershell
cd C:\path\to\LAN_Collaboration_App
python client\client_gui.py
```

**Linux/Mac:**
```bash
cd /path/to/LAN_Collaboration_App
python3 client/client_gui.py
```

### Method 3: Individual Modules

Run specific modules independently:

**Chat Client:**
```powershell
python client/client_chat.py --username Alice --ip 192.168.1.100 --port 5003
```

**Video Sender:**
```powershell
python client/client_video.py send --ip 192.168.1.100 --port 5001
```

**Video Receiver:**
```powershell
python client/client_video.py receive --port 5001
```

**Audio Sender:**
```powershell
python client/client_audio.py send --ip 192.168.1.100 --port 5002
```

**Audio Receiver:**
```powershell
python client/client_audio.py receive --port 5002
```

**Screen Share Sender:**
```powershell
python client/client_screen_share.py share --ip 192.168.1.100 --port 5005
```

**Screen Share Viewer:**
```powershell
python client/client_screen_share.py view --port 5005
```

**File Upload:**
```powershell
python client/client_file_transfer.py upload myfile.pdf --ip 192.168.1.100 --port 5004
```

---

## ⚙️ Configuration

### Video Settings

Edit `shared/constants.py`:

```python
# Video quality
VIDEO_QUALITY = 80  # JPEG quality (1-100)
VIDEO_FPS = 30      # Frames per second
VIDEO_WIDTH = 640   # Video width
VIDEO_HEIGHT = 480  # Video height
```

### Audio Settings

```python
# Audio quality
AUDIO_RATE = 44100      # Sample rate (Hz)
AUDIO_CHANNELS = 2      # Stereo (1 for mono)
AUDIO_CHUNK = 1024      # Buffer size
AUDIO_FORMAT = pyaudio.paInt16  # 16-bit audio
```

### Network Buffer Sizes

```python
# Buffer sizes
BUFFER_SIZE = 4096
VIDEO_BUFFER_SIZE = 65535
AUDIO_BUFFER_SIZE = 8192
```

### Screen Share Settings

```python
# Screen share
SCREEN_SHARE_FPS = 10        # Lower FPS for bandwidth
SCREEN_SHARE_QUALITY = 80    # JPEG quality
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```powershell
pip install opencv-python
```

### Issue: "Could not open webcam"

**Solutions:**
1. Check if webcam is connected
2. Close other apps using webcam (Zoom, Skype, etc.)
3. Check camera index:
   ```powershell
   python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"
   ```
4. Update `VIDEO_CAMERA_INDEX` in `shared/constants.py`

### Issue: "No audio devices found"

**Solutions:**
1. Check microphone/speaker connections
2. Update audio drivers
3. List audio devices:
   ```powershell
   python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'[{i}] {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]; p.terminate()"
   ```
4. Set device index in code:
   ```python
   stream = audio.open(..., input_device_index=1)
   ```

### Issue: "Connection refused" / "Cannot connect to server"

**Solutions:**
1. Verify server is running:
   ```powershell
   python simple_chat_server.py
   ```
2. Check firewall settings (see Configuration section)
3. Ping server IP:
   ```powershell
   ping 192.168.1.100
   ```
4. Verify both machines on same network:
   ```powershell
   ipconfig  # Should have same subnet (e.g., 192.168.1.x)
   ```
5. Check if port is in use:
   ```powershell
   netstat -an | findstr :5003
   ```

### Issue: "Address already in use"

**Solutions:**
1. Wait 30-60 seconds for port to release
2. Kill process using port:
   ```powershell
   # Windows
   netstat -ano | findstr :5003
   taskkill /PID <PID> /F
   
   # Linux
   sudo lsof -i :5003
   kill -9 <PID>
   ```
3. Use different port:
   ```powershell
   python client/client_chat.py --port 5010
   ```

### Issue: PyAudio installation fails on Windows

**Solutions:**
1. Download precompiled wheel from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Install wheel:
   ```powershell
   pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
   ```

### Issue: Video/Audio lag or poor quality

**Solutions:**
1. Reduce quality in `shared/constants.py`:
   ```python
   VIDEO_QUALITY = 60  # Lower value
   VIDEO_FPS = 15      # Lower FPS
   AUDIO_CHUNK = 2048  # Larger chunks
   ```
2. Close bandwidth-heavy applications
3. Use wired Ethernet instead of WiFi
4. Check network speed:
   ```powershell
   ping 192.168.1.100 -t
   ```

### Issue: GUI doesn't start

**Solutions:**
1. Verify PyQt5 installation:
   ```powershell
   python -c "from PyQt5.QtWidgets import QApplication; print('✅ PyQt5 works')"
   ```
2. Run with verbose output:
   ```powershell
   python client/client_gui.py --verbose
   ```
3. Try individual modules first to isolate issue

### Issue: File transfer fails

**Solutions:**
1. Check file permissions
2. Ensure sufficient disk space
3. Verify file path:
   ```powershell
   python client/client_file_transfer.py upload "C:\full\path\to\file.txt"
   ```
4. Check server is listening:
   ```powershell
   python test_dummy_servers.py --mode file
   ```

---

## 📞 Getting Help

### Testing Before Asking

Before reporting issues, run diagnostics:

**1. Test connectivity:**
```powershell
python -c "import socket; s=socket.socket(); s.connect(('192.168.1.100', 5003)); print('✅ Connected'); s.close()"
```

**2. Test camera:**
```powershell
python -c "import cv2; c=cv2.VideoCapture(0); ret,_=c.read(); print('✅ Camera works' if ret else '❌ Camera failed'); c.release()"
```

**3. Test audio:**
```powershell
python -c "import pyaudio; p=pyaudio.PyAudio(); print(f'✅ Audio: {p.get_device_count()} devices'); p.terminate()"
```

### Logs

Check log files in project directory:
- `client.log` - Client errors
- `server.log` - Server errors

### Common Error Patterns

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `WinError 10061` | Server not running | Start server first |
| `WinError 10048` | Port in use | Wait or change port |
| `OSError: [Errno -9997]` | Audio device issue | Check mic/speaker |
| `cv2.error: (-215:Assertion failed)` | Camera issue | Check webcam connection |
| `ImportError` | Missing dependency | Run `pip install -r requirements.txt` |

---

## 🎓 Next Steps

After setup:
1. Read [README.md](../README.md) for feature overview
2. Check [TESTING_STEP_BY_STEP.md](../TESTING_STEP_BY_STEP.md) for module testing
3. Review [GUI_GUIDE.md](../GUI_GUIDE.md) for GUI usage
4. Explore individual modules for customization

---

## 🛠️ Advanced Configuration

### Running as Service (Linux)

Create systemd service:

```bash
sudo nano /etc/systemd/system/lan-collab-server.service
```

```ini
[Unit]
Description=LAN Collaboration Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/LAN_Collaboration_App
ExecStart=/usr/bin/python3 simple_chat_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lan-collab-server
sudo systemctl start lan-collab-server
```

### Custom SSL/TLS (Future Enhancement)

For encrypted communication, add certificates in `certs/` directory and update socket creation.

---

## 📊 Performance Optimization

### Low Bandwidth Networks

```python
# In shared/constants.py
VIDEO_WIDTH = 320
VIDEO_HEIGHT = 240
VIDEO_FPS = 10
VIDEO_QUALITY = 50
AUDIO_RATE = 22050
AUDIO_CHANNELS = 1
```

### High Quality Networks

```python
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS = 30
VIDEO_QUALITY = 90
AUDIO_RATE = 48000
AUDIO_CHANNELS = 2
```

---

**Happy Collaborating! 🎉**

# Video Streaming Testing Guide

## 📋 What Was Created

### `client_video.py` Features:

1. **VideoStreamer Class**
   - Captures webcam frames using OpenCV
   - Compresses frames to JPEG with configurable quality (80% default)
   - Packs frames with protocol header using `pack_message()`
   - Sends via UDP to specified server IP and port
   - Displays local preview window
   - Shows real-time FPS and packet size statistics

2. **VideoReceiver Class**
   - Listens for incoming video packets on UDP port
   - Unpacks protocol headers using `unpack_message()`
   - Decompresses JPEG frames
   - Displays received video stream
   - Shows FPS and source IP statistics

---

## 🧪 How to Test Locally

### Method 1: Manual (Two Terminal Windows)

**Step 1: Open Terminal 1 (Receiver)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_video.py receive --port 5001
```

**Step 2: Open Terminal 2 (Sender)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_video.py send --ip 127.0.0.1 --port 5001
```

**Expected Output:**
- Terminal 1: "Listening for video on port 5001"
- Terminal 2: "Starting video stream to 127.0.0.1:5001"
- Two OpenCV windows will appear showing your webcam

---

### Method 2: Automated Test Script

**Step 1: Run the test script**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python test_video_streaming.py
```

**Step 2: Answer 'yes' when prompted**
- Script will automatically launch both sender and receiver
- Both windows will appear automatically

---

## 🌐 Testing on LAN (Different Computers)

### On Receiver Computer:

**Step 1: Find your IP address**
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Step 2: Start receiver**
```powershell
python client/client_video.py receive --port 5001
```

**Step 3: Allow firewall access if prompted**
- Windows Firewall may ask for permission
- Click "Allow access"

### On Sender Computer:

**Step 1: Start sender with receiver's IP**
```powershell
python client/client_video.py send --ip 192.168.1.100 --port 5001
```

Replace `192.168.1.100` with the actual receiver IP.

---

## 🎮 Controls

| Action | Key |
|--------|-----|
| Stop streaming | Press `q` in any window |
| Force quit | Press `Ctrl+C` in terminal |

---

## ⚙️ Configuration

Edit `shared/constants.py` to customize:

```python
VIDEO_WIDTH = 640           # Resolution width
VIDEO_HEIGHT = 480          # Resolution height
VIDEO_FPS = 30              # Frames per second
VIDEO_QUALITY = 80          # JPEG quality (0-100)
VIDEO_BUFFER_SIZE = 65536   # UDP buffer size
VIDEO_PORT = 5001           # Default port
```

---

## 🐛 Troubleshooting

### Problem: "Error: Could not open webcam"
**Solutions:**
- Close other apps using the webcam (Zoom, Teams, etc.)
- Try a different camera index:
  - Edit `client_video.py` line 38
  - Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

### Problem: "Connection refused" or no video received
**Solutions:**
- Start receiver BEFORE sender
- Check firewall settings
- Verify both computers are on same network
- Try pinging receiver IP: `ping 192.168.1.100`

### Problem: Video is laggy or choppy
**Solutions:**
- Reduce resolution in `constants.py`:
  ```python
  VIDEO_WIDTH = 320
  VIDEO_HEIGHT = 240
  ```
- Lower quality:
  ```python
  VIDEO_QUALITY = 60
  ```
- Increase buffer size:
  ```python
  VIDEO_BUFFER_SIZE = 131072  # 128 KB
  ```

### Problem: Video quality is poor
**Solutions:**
- Increase quality in `constants.py`:
  ```python
  VIDEO_QUALITY = 95
  ```
- Increase resolution:
  ```python
  VIDEO_WIDTH = 1280
  VIDEO_HEIGHT = 720
  ```

### Problem: High CPU usage
**Solutions:**
- Lower FPS:
  ```python
  VIDEO_FPS = 15
  ```
- Reduce resolution (see above)

---

## 📊 What You Should See

### Sender Output:
```
Starting video stream to 127.0.0.1:5001
Press 'q' to quit
Streaming at 29.87 FPS | Packet size: 15234 bytes
Streaming at 30.12 FPS | Packet size: 14891 bytes
```

### Receiver Output:
```
Listening for video on port 5001
Press 'q' to quit
Receiving at 29.91 FPS from 127.0.0.1:52341
Receiving at 30.08 FPS from 127.0.0.1:52341
```

### Windows:
- **"Video Stream - Sending"**: Your webcam feed (preview)
- **"Video Stream - Receiving from 127.0.0.1"**: Received video

---

## 🔧 Advanced Testing

### Test with different ports:
```powershell
# Receiver
python client/client_video.py receive --port 6000

# Sender
python client/client_video.py send --ip 127.0.0.1 --port 6000
```

### Test with multiple senders (broadcast):
1. Start one receiver
2. Start multiple senders pointing to same receiver IP
3. Receiver will show the last sender's stream

### Monitor network usage:
```powershell
# Windows Resource Monitor
resmon.exe
# Go to Network tab and look for python.exe
```

---

## 📝 Code Structure

```
VideoStreamer (Sender)
    ├── capture frame from webcam
    ├── compress to JPEG
    ├── pack with protocol header
    └── send via UDP

VideoReceiver (Receiver)
    ├── receive UDP packet
    ├── unpack protocol header
    ├── decompress JPEG
    └── display frame
```

---

## ✅ Success Checklist

- [ ] Webcam opens successfully
- [ ] Sender window shows webcam preview
- [ ] Receiver window shows received video
- [ ] Both terminals show FPS statistics
- [ ] Video streams smoothly (25-30 FPS)
- [ ] Can stop with 'q' key
- [ ] Works on localhost (127.0.0.1)
- [ ] Works on LAN (different computers)

---

## 🚀 Next Steps

After successful testing:
1. Integrate with server for multi-client support
2. Add user authentication
3. Implement room/channel system
4. Add video recording capability
5. Create GUI for easier control

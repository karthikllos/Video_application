# Screen Sharing Testing Guide

## 📋 What Was Created

### `client_screen_share.py` Features:

**ScreenStreamer Class (Screen → Network):**
- Uses **mss library** for fast screen capture
- Captures entire primary monitor in real-time
- Compresses screenshots to JPEG format
- Sends via **TCP** in chunks with size prefix
- Configurable FPS (default: 10)
- Configurable quality (default: 80%)
- Real-time statistics (frames, FPS, size)

**ScreenReceiver Class (Network → Display):**
- TCP server that accepts screen share connections
- Receives chunked screen data
- Decompresses JPEG frames
- Displays in OpenCV window
- Real-time FPS statistics

**Helper Functions:**
- `capture_screenshot()` - Capture single screenshot
- `compress_screenshot(img, quality)` - Compress to JPEG
- `send_screen_chunk(sock, data)` - Send with chunking
- `receive_screen_chunk(sock)` - Receive chunked data

---

## 🧪 How to Test

### Method 1: Two Terminal Windows

**Step 1: Terminal 1 (Receiver/Viewer)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_screen_share.py view --port 5005
```

**Expected Output:**
```
🖥️  Waiting for screen share connection on port 5005...
Press Ctrl+C to stop
```

**Step 2: Terminal 2 (Sharer)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_screen_share.py share --ip 127.0.0.1 --port 5005
```

**Expected Output:**
```
✓ Connected to screen share server at 127.0.0.1:5005

🖥️  Starting screen share
📊 Resolution: 1920x1080
🎬 FPS: 10
📦 Quality: 80%
Press Ctrl+C to stop

📡 Frames: 50 | FPS: 10.0 | Size: 156 KB
📡 Frames: 100 | FPS: 10.0 | Size: 158 KB
```

**Step 3: Watch Screen**
- A window will appear on Terminal 1 showing the shared screen
- Press 'q' in the window to stop
- Or press Ctrl+C in either terminal

---

## 🌐 Testing on LAN (Different Computers)

### On Viewer Computer:

**Step 1: Find your IP address**
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Step 2: Start viewer (receiver)**
```powershell
python client/client_screen_share.py view --port 5005
```

### On Sharer Computer:

**Share your screen to viewer**
```powershell
python client/client_screen_share.py share --ip 192.168.1.100 --port 5005
```

---

## ⚙️ Configuration Options

### Adjust Frame Rate (FPS):
```powershell
# Lower FPS = less bandwidth, choppier
python client/client_screen_share.py share --fps 5

# Higher FPS = more bandwidth, smoother
python client/client_screen_share.py share --fps 20
```

### Adjust Quality (0-100):
```powershell
# Lower quality = smaller files, more artifacts
python client/client_screen_share.py share --quality 60

# Higher quality = larger files, better image
python client/client_screen_share.py share --quality 95
```

### Custom Port:
```powershell
# Viewer
python client/client_screen_share.py view --port 6000

# Sharer
python client/client_screen_share.py share --port 6000
```

---

## 📊 Performance Tuning

### For Low Bandwidth Networks:
```powershell
python client/client_screen_share.py share --fps 5 --quality 50
```
- **Bandwidth**: ~500 KB/s
- **Latency**: Higher (~400-600ms)
- **Use case**: Slow WiFi, remote work

### For High Quality Presentations:
```powershell
python client/client_screen_share.py share --fps 15 --quality 90
```
- **Bandwidth**: ~3-5 MB/s
- **Latency**: Lower (~200-300ms)
- **Use case**: Demos, presentations on LAN

### For Balanced Performance:
```powershell
python client/client_screen_share.py share --fps 10 --quality 80
```
- **Bandwidth**: ~1-2 MB/s (default)
- **Latency**: ~250-350ms
- **Use case**: General screen sharing

---

## 🔧 Testing Scenarios

### Scenario 1: Local Screen Share (Same Machine)
```powershell
# Terminal 1
python client/client_screen_share.py view

# Terminal 2
python client/client_screen_share.py share --ip 127.0.0.1
```
You'll see your own screen in a window with slight delay.

---

### Scenario 2: Remote Presentation
**Computer A (Presenter):**
```powershell
# Find Computer B's IP, then share to it
python client/client_screen_share.py share --ip 192.168.1.100
```

**Computer B (Viewer):**
```powershell
# Start viewer first
python client/client_screen_share.py view
```

---

### Scenario 3: Programmatic Screen Capture
Use helper functions directly:

```python
from client.client_screen_share import (
    capture_screenshot, 
    compress_screenshot,
    send_screen_chunk
)
import socket

# Capture screen
img = capture_screenshot()
print(f"Captured: {img.size}")

# Compress
jpeg_data = compress_screenshot(img, quality=85)
print(f"Compressed: {len(jpeg_data)} bytes")

# Send over TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5005))
send_screen_chunk(sock, jpeg_data)
sock.close()
```

---

## 📊 What You Should See

### Viewer (Receiver) Output:
```
🖥️  Waiting for screen share connection on port 5005...
Press Ctrl+C to stop

✓ Connected to 127.0.0.1:52341
Press 'q' in the window to stop

📺 Received 50 frames | 9.8 FPS
📺 Received 100 frames | 9.9 FPS
📺 Received 150 frames | 10.0 FPS
```

**Window Title:** `Screen Share from 127.0.0.1`

### Sharer Output:
```
✓ Connected to screen share server at 127.0.0.1:5005

🖥️  Starting screen share
📊 Resolution: 1920x1080
🎬 FPS: 10
📦 Quality: 80%
Press Ctrl+C to stop

📡 Frames: 50 | FPS: 10.0 | Size: 156 KB
📡 Frames: 100 | FPS: 10.1 | Size: 158 KB
📡 Frames: 150 | FPS: 10.0 | Size: 157 KB
```

---

## 🐛 Troubleshooting

### Problem: "Connection error: [WinError 10061] Connection refused"
**Solutions:**
- Start **viewer (receiver) FIRST**, then sharer
- Viewer must be listening before sharer connects
- Check that port is not in use

### Problem: Very low FPS (< 5)
**Solutions:**
- Close resource-intensive applications
- Reduce quality: `--quality 60`
- Reduce FPS target: `--fps 5`
- Use wired connection instead of WiFi
- Check network bandwidth

### Problem: High latency/delay
**Solutions:**
- Increase FPS: `--fps 15` or `--fps 20`
- Use wired Ethernet connection
- Close bandwidth-consuming apps
- Lower screen resolution on sharing computer

### Problem: Window shows black screen or corrupted image
**Solutions:**
- Check that mss captured correctly (test with capture_screenshot())
- Verify JPEG compression worked
- Check network connection stability
- Try lower quality settings

### Problem: "Frame size too large" warnings
**Solutions:**
- Reduce quality: `--quality 50`
- Reduce FPS to allow more time per frame
- Check for extremely high-resolution monitors
- The limit is 10MB per frame for safety

### Problem: Screen capture fails on multi-monitor setup
**Solutions:**
- By default captures primary monitor (monitor 1)
- To capture different monitor, edit code:
  ```python
  monitor = self.sct.monitors[2]  # For second monitor
  ```
- List all monitors:
  ```python
  with mss.mss() as sct:
      for i, m in enumerate(sct.monitors):
          print(f"Monitor {i}: {m}")
  ```

### Problem: High CPU usage
**Solutions:**
- Reduce FPS: `--fps 5`
- Reduce quality: `--quality 60`
- Close other applications
- mss is already optimized, but capturing large screens is CPU-intensive

---

## 🔍 Technical Details

### Screen Capture (mss):
```
mss library benefits:
- Fast: ~100x faster than PIL
- Cross-platform: Windows, Linux, macOS
- No dependencies on external tools
- Direct framebuffer access
```

### Data Flow:
```
1. Capture screen → mss.grab()
2. Convert to PIL Image
3. Compress to JPEG (quality=80%)
4. Add protocol header (12 bytes)
5. Send frame size (4 bytes)
6. Send frame data via TCP
7. Receiver gets size → receives exact bytes
8. Unpack protocol header
9. Decompress JPEG to OpenCV image
10. Display in window
```

### Bandwidth Calculation:
```
Example (1920x1080, 10 FPS, quality=80):
- Average frame size: ~150 KB
- Bandwidth: 150 KB × 10 FPS = 1.5 MB/s
- Per minute: ~90 MB
- Per hour: ~5.4 GB

Lower quality (quality=60):
- Average frame size: ~80 KB
- Bandwidth: 80 KB × 10 FPS = 800 KB/s
```

### Protocol:
```
Message Format:
[4 bytes: Frame Size][12 bytes: Protocol Header][Variable: JPEG Data]

Protocol Header:
- Version (1 byte)
- Message Type (1 byte): 0x06 (SCREEN_SHARE)
- Payload Length (4 bytes)
- Sequence Number (4 bytes)
- Reserved (2 bytes)
```

### TCP vs UDP:
```
Why TCP?
✓ Guaranteed delivery (no lost frames)
✓ In-order delivery
✓ Built-in chunking and reassembly
✓ Better for large frames

UDP would be:
✗ Faster but frames could be lost
✗ Requires manual reassembly
✗ Better for real-time video (which we handle separately)
```

---

## ✅ Success Checklist

- [ ] Viewer starts and listens on port
- [ ] Sharer connects successfully
- [ ] Window appears showing remote screen
- [ ] Screen updates smoothly (target FPS)
- [ ] Statistics show in both terminals
- [ ] Can quit with 'q' or Ctrl+C
- [ ] Works on localhost (127.0.0.1)
- [ ] Works on LAN (different computers)
- [ ] Acceptable latency (<500ms)
- [ ] No constant errors or warnings

---

## 📝 Comparison with Video Streaming

| Feature | Screen Share | Video (Webcam) |
|---------|--------------|----------------|
| Protocol | TCP | UDP |
| Source | Screen capture | Camera |
| FPS | 5-20 (typical) | 25-30 |
| Latency | 200-500ms | 100-200ms |
| Quality | High (documents) | Medium (faces) |
| Bandwidth | 0.5-5 MB/s | 1-2 MB/s |
| Use Case | Presentations | Video calls |

---

## 🚀 Next Steps

After successful testing:
1. Add mouse cursor overlay on shared screen
2. Implement region selection (share part of screen)
3. Add remote control capability
4. Support multiple viewers (broadcast)
5. Add annotation tools
6. Implement recording functionality
7. Add bandwidth adaptation
8. Support screen rotation
9. Add privacy filters (blur sensitive areas)
10. Create GUI for easy control

---

## 💡 Integration Tips

### Combine with Chat:
Run screen share and chat simultaneously:

**Terminal 1:** Screen Viewer
**Terminal 2:** Screen Sharer  
**Terminal 3:** Chat Server
**Terminal 4:** Chat Client (Alice)
**Terminal 5:** Chat Client (Bob)

This allows collaborative screen sharing with discussion!

### Performance Tips:
1. **Wired > WiFi**: Use Ethernet for best performance
2. **Lower resolution**: Share at 1280x720 instead of 4K
3. **Static content**: Lower FPS (5) works great for documents
4. **Dynamic content**: Higher FPS (15-20) for videos/animations
5. **Quality**: Use 70-80% for best size/quality balance

---

## 🎯 Bandwidth Requirements

| Quality | FPS | Bandwidth | Use Case |
|---------|-----|-----------|----------|
| Low (50%) | 5 | ~400 KB/s | Slow network, documents |
| Medium (70%) | 10 | ~1 MB/s | General sharing |
| High (80%) | 10 | ~1.5 MB/s | Standard quality |
| Very High (90%) | 15 | ~3 MB/s | Presentations, demos |
| Maximum (95%) | 20 | ~5 MB/s | High-quality LAN only |

Test your network: `ping <remote_ip>` should be <50ms on good LAN.

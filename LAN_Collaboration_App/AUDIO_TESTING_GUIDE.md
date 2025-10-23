# Audio Streaming Testing Guide

## 📋 What Was Created

### `client_audio.py` Features:

1. **AudioStreamer Class**
   - Captures microphone input using PyAudio
   - Uses 16-bit PCM format at 44100 Hz sample rate
   - Frames per buffer: 1024 samples
   - Packs audio data with protocol header using `pack_message()`
   - Sends via UDP to specified server IP and port
   - Shows real-time statistics (packets/sec, kbps)
   - Lists available audio input devices

2. **AudioReceiver Class**
   - Listens for incoming audio packets on UDP port
   - Unpacks protocol headers using `unpack_message()`
   - Plays received audio through speakers in real-time
   - Shows packet statistics and sender information
   - Lists available audio output devices

---

## 🎵 Audio Configuration

```python
# From shared/constants.py
AUDIO_RATE = 44100          # 44.1 kHz sample rate (CD quality)
AUDIO_CHANNELS = 2          # Stereo
AUDIO_CHUNK = 1024          # Frames per buffer
AUDIO_FORMAT = 16           # 16-bit depth
AUDIO_PORT = 5002           # Default port
```

**Bandwidth Calculation:**
- Sample rate: 44100 Hz
- Bit depth: 16 bits
- Channels: 2 (stereo)
- **Total bandwidth: ~1.4 Mbps** (44100 × 16 × 2 = 1,411,200 bits/sec)

---

## 🧪 How to Test Locally

### Method 1: Two Terminal Windows (Recommended)

**Step 1: Open Terminal 1 (Receiver)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_audio.py receive --port 5002
```

**Expected Output:**
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Output
  [1] Speakers (Realtek High Definition Audio)
  [2] Headphones (USB Audio Device)
==================================================

🔊 Listening for audio on port 5002
📊 Format: 16-bit PCM, 44100Hz, 2 channel(s)
📦 Chunk size: 1024 frames
Press Ctrl+C to stop
```

**Step 2: Open Terminal 2 (Sender)**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_audio.py send --ip 127.0.0.1 --port 5002
```

**Expected Output:**
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Input
  [1] Microphone (Realtek High Definition Audio)
  [2] Webcam Microphone
==================================================

🎤 Starting audio stream to 127.0.0.1:5002
📊 Format: 16-bit PCM, 44100Hz, 2 channel(s)
📦 Chunk size: 1024 frames
Press Ctrl+C to stop

📡 Sent 100 packets | 43.1 pkt/s | 1402.3 kbps | Packet size: 4108 bytes
```

**Step 3: Test**
- Speak into your microphone
- You should hear your voice through speakers with minimal delay (~100-200ms)
- Watch the packet statistics in both terminals

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
python client/client_audio.py receive --port 5002
```

**Step 3: Allow firewall access if prompted**
- Windows Firewall may ask for permission
- Click "Allow access"

### On Sender Computer:

**Start sender with receiver's IP**
```powershell
python client/client_audio.py send --ip 192.168.1.100 --port 5002
```

### Testing Tips:
1. Use headphones on the sender side to avoid feedback/echo
2. Start receiver first, then sender
3. Speak clearly into microphone to test
4. Check packet statistics to verify data flow

---

## 🎮 Controls

| Action | Key |
|--------|-----|
| Stop streaming | `Ctrl+C` in terminal |
| Adjust volume | Use system volume controls |

---

## 🔧 Testing Scenarios

### Scenario 1: Echo Test (Loopback)
Test your microphone by hearing yourself:
```powershell
# Terminal 1
python client/client_audio.py receive --port 5002

# Terminal 2
python client/client_audio.py send --ip 127.0.0.1 --port 5002

# Speak into mic - you should hear yourself
```

### Scenario 2: One-Way Communication (Intercom)
```powershell
# Computer A (Receiver - Listener)
python client/client_audio.py receive --port 5002

# Computer B (Sender - Speaker)
python client/client_audio.py send --ip <COMPUTER_A_IP> --port 5002
```

### Scenario 3: Two-Way Communication (Requires 2 terminals on each PC)
**Computer A:**
```powershell
# Terminal 1: Receive from B on port 5002
python client/client_audio.py receive --port 5002

# Terminal 2: Send to B on port 5003
python client/client_audio.py send --ip <COMPUTER_B_IP> --port 5003
```

**Computer B:**
```powershell
# Terminal 1: Receive from A on port 5003
python client/client_audio.py receive --port 5003

# Terminal 2: Send to A on port 5002
python client/client_audio.py send --ip <COMPUTER_A_IP> --port 5002
```

---

## 🐛 Troubleshooting

### Problem: "Error starting audio stream: Invalid number of channels"
**Solutions:**
- Your audio device might not support stereo (2 channels)
- Edit `shared/constants.py`:
  ```python
  AUDIO_CHANNELS = 1  # Use mono instead of stereo
  ```

### Problem: "Audio buffer overflow" warnings
**Solutions:**
- This is normal under high CPU load
- The system automatically continues
- To reduce: Close other applications
- Or increase buffer size in `constants.py`:
  ```python
  AUDIO_CHUNK = 2048  # Larger buffer = more delay but fewer overflows
  ```

### Problem: No sound on receiver
**Solutions:**
- Check volume levels (system and application)
- Verify correct output device is selected
- Make sure firewall allows the connection
- Confirm sender is actually sending (check statistics)
- Try plugging in headphones/speakers

### Problem: Microphone not working
**Solutions:**
- Check Windows Privacy Settings > Microphone permissions
- Test microphone in Windows Sound Settings
- Try a different microphone (USB, built-in, etc.)
- Check the device list printed on startup
- Grant microphone access to Python if prompted

### Problem: High latency (delay)
**Solutions:**
- Expected latency on LAN: 100-300ms
- Reduce chunk size for lower latency:
  ```python
  AUDIO_CHUNK = 512  # Lower = less delay but more CPU
  ```
- Use wired connection instead of WiFi
- Close bandwidth-intensive applications

### Problem: Audio sounds choppy or distorted
**Solutions:**
- Increase chunk size:
  ```python
  AUDIO_CHUNK = 2048  # More stable but higher latency
  ```
- Close other audio applications
- Check network quality (ping between computers)
- Reduce sample rate (edit constants.py):
  ```python
  AUDIO_RATE = 22050  # Half CD quality, less bandwidth
  ```

### Problem: "Connection refused" or receiver not receiving
**Solutions:**
- Start receiver BEFORE sender
- Check firewall settings on receiver computer
- Verify both computers are on same network
- Test with localhost first (127.0.0.1)
- Try different port numbers

---

## 📊 What You Should See

### Sender Terminal:
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Input
  [1] Microphone (Realtek High Definition Audio)
==================================================

🎤 Starting audio stream to 127.0.0.1:5002
📊 Format: 16-bit PCM, 44100Hz, 2 channel(s)
📦 Chunk size: 1024 frames
Press Ctrl+C to stop

📡 Sent 100 packets | 43.1 pkt/s | 1402.3 kbps | Packet size: 4108 bytes
📡 Sent 200 packets | 43.0 pkt/s | 1403.1 kbps | Packet size: 4108 bytes
📡 Sent 300 packets | 43.1 pkt/s | 1402.8 kbps | Packet size: 4108 bytes
```

### Receiver Terminal:
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Output
  [1] Speakers (Realtek High Definition Audio)
==================================================

🔊 Listening for audio on port 5002
📊 Format: 16-bit PCM, 44100Hz, 2 channel(s)
📦 Chunk size: 1024 frames
Press Ctrl+C to stop

🎧 Receiving audio from 127.0.0.1:54321

🎵 Received 100 packets | 43.0 pkt/s | Audio data: 4096 bytes
🎵 Received 200 packets | 43.1 pkt/s | Audio data: 4096 bytes
🎵 Received 300 packets | 43.0 pkt/s | Audio data: 4096 bytes
```

---

## ⚙️ Performance Tuning

### For Low Latency (Real-time conversation):
```python
AUDIO_CHUNK = 512           # Small chunks
AUDIO_BUFFER_SIZE = 4096    # Small buffer
```
- **Pros**: Lower delay (~50-100ms)
- **Cons**: Higher CPU usage, more packet overhead

### For Stable Streaming (Music/Broadcasting):
```python
AUDIO_CHUNK = 2048          # Larger chunks
AUDIO_BUFFER_SIZE = 16384   # Larger buffer
```
- **Pros**: More stable, less CPU usage
- **Cons**: Higher latency (~200-400ms)

### For Low Bandwidth (Slow networks):
```python
AUDIO_RATE = 22050          # Lower sample rate
AUDIO_CHANNELS = 1          # Mono instead of stereo
```
- **Bandwidth reduction**: From 1.4 Mbps to ~350 kbps

---

## 🔍 Technical Details

### Packet Structure:
```
[12-byte Protocol Header][4096 bytes Audio Data]
Total: 4108 bytes per packet

Protocol Header (from helpers.py):
- Version (1 byte)
- Message Type (1 byte) = 0x02 (AUDIO)
- Payload Length (4 bytes) = 4096
- Sequence Number (4 bytes)
- Reserved (2 bytes)
```

### Timing:
- 1024 frames at 44100 Hz = ~23.2 ms per packet
- Theoretical max: ~43 packets/second
- Actual rate: ~40-43 packets/second (due to overhead)

### Audio Format (16-bit PCM):
- Each sample: 2 bytes (16 bits)
- Stereo: 2 channels × 2 bytes = 4 bytes per frame
- 1024 frames × 4 bytes = 4096 bytes per packet

---

## ✅ Success Checklist

- [ ] Microphone is detected and listed
- [ ] Speakers/headphones are detected
- [ ] Sender shows statistics (packets, kbps)
- [ ] Receiver shows "Receiving audio from..."
- [ ] Can hear microphone audio on receiver
- [ ] Packet rate is stable (~43 pkt/s)
- [ ] Works on localhost (127.0.0.1)
- [ ] Works on LAN (different computers)
- [ ] Latency is acceptable (<300ms)
- [ ] No constant buffer overflow errors

---

## 🚀 Next Steps

After successful testing:
1. Implement full-duplex communication (simultaneous send/receive)
2. Add echo cancellation for speaker-to-mic feedback
3. Integrate with video streaming for complete conferencing
4. Add audio recording/saving capability
5. Implement push-to-talk functionality
6. Add volume level indicators
7. Support multiple simultaneous audio streams

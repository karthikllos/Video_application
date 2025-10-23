# Step-by-Step Testing Guide

## 🧪 Testing All Client Modules

This guide will help you test each module one by one using dummy servers.

---

## 📋 Pre-Testing Checklist

### Install Dependencies:
```powershell
pip install opencv-python pyaudio PyQt5 numpy tqdm mss pillow
```

### Navigate to Project:
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
```

---

## 1️⃣ Test Chat (TCP)

### **Step 1: Start Chat Server**

**Terminal 1:**
```powershell
python simple_chat_server.py --port 5003
```

**Expected Output:**
```
🚀 Chat Server Started
📡 Listening on port 5003
Press Ctrl+C to stop
============================================================
```

### **Step 2: Connect First Client**

**Terminal 2:**
```powershell
python client/client_chat.py --username Alice --ip 127.0.0.1 --port 5003
```

**Expected Output:**
```
🔌 Connecting to chat server at 127.0.0.1:5003...
✓ Connected as 'Alice'
============================================================
👂 Listening for messages...

============================================================
💬 CHAT READY - Type your messages below
Commands: /quit to exit, /help for help
============================================================
```

### **Step 3: Connect Second Client**

**Terminal 3:**
```powershell
python client/client_chat.py --username Bob --ip 127.0.0.1 --port 5003
```

### **Step 4: Test Messaging**

In Alice's terminal, type:
```
Hello Bob!
```

In Bob's terminal, you should see:
```
[14:30:15] Alice: Hello Bob!
```

In Bob's terminal, type:
```
Hi Alice!
```

### **✅ Success Criteria:**
- ✓ Both clients connect
- ✓ Messages appear with timestamps
- ✓ `/help` command works
- ✓ `/quit` disconnects cleanly

---

## 2️⃣ Test Video (UDP)

### **Step 1: Start Video Receiver**

**Terminal 1:**
```powershell
python client/client_video.py receive --port 5001
```

**Expected Output:**
```
Listening for video on port 5001
Press 'q' to quit
```

### **Step 2: Start Video Sender**

**Terminal 2:**
```powershell
python client/client_video.py send --ip 127.0.0.1 --port 5001
```

**Expected Output:**
```
Starting video stream to 127.0.0.1:5001
Press 'q' to quit

Streaming at 29.87 FPS | Packet size: 15234 bytes
```

### **Step 3: Verify Video Display**

Two windows should appear:
1. **"Video Stream - Sending"** - Your webcam preview
2. **"Video Stream - Receiving from 127.0.0.1"** - Received video

### **✅ Success Criteria:**
- ✓ Webcam opens successfully
- ✓ Preview window shows your face
- ✓ Receiver window shows video feed
- ✓ FPS is around 25-30
- ✓ Press 'q' to quit both

### **Troubleshooting:**
```powershell
# If webcam fails, list cameras:
python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"

# If no camera, test with dummy server (see dummy servers section)
```

---

## 3️⃣ Test Audio (UDP)

### **Step 1: Start Audio Receiver**

**Terminal 1:**
```powershell
python client/client_audio.py receive --port 5002
```

**Expected Output:**
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Output
  [1] Speakers (Realtek High Definition Audio)
==================================================

🔊 Listening for audio on port 5002
Press Ctrl+C to stop
```

### **Step 2: Start Audio Sender**

**Terminal 2:**
```powershell
python client/client_audio.py send --ip 127.0.0.1 --port 5002
```

**Expected Output:**
```
🔊 Available Audio Devices:
==================================================
  [0] Microsoft Sound Mapper - Input
  [1] Microphone (Realtek High Definition Audio)
==================================================

🎤 Starting audio stream to 127.0.0.1:5002
Press Ctrl+C to stop

📡 Sent 100 packets | 43.1 pkt/s | 1402.3 kbps
```

### **Step 3: Test Audio**

**Speak into microphone** - you should hear your voice through speakers!

**⚠️ Use HEADPHONES to avoid feedback!**

### **✅ Success Criteria:**
- ✓ Microphone detected
- ✓ Speakers detected
- ✓ Can hear your voice with slight delay (~100-200ms)
- ✓ Packet rate is stable (~43 pkt/s)
- ✓ No constant "buffer overflow" errors

### **Troubleshooting:**
```powershell
# Test microphone:
python -c "import pyaudio; p=pyaudio.PyAudio(); print('Inputs:', [p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels']>0])"

# If stereo fails, try mono (edit shared/constants.py):
# AUDIO_CHANNELS = 1
```

---

## 4️⃣ Test File Transfer (TCP)

### **Method A: Using Dummy Server (Recommended)**

Create a test file first:
```powershell
echo "Hello, World! This is a test file." > test.txt
```

**Terminal 1 - Start Dummy Server:**
```powershell
python test_dummy_servers.py --mode file_server --port 5004
```

**Terminal 2 - Upload File:**
```powershell
python client/client_file_transfer.py upload test.txt --ip 127.0.0.1 --port 5004
```

**Expected Output:**
```
📤 Uploading: test.txt
📊 Size: 37 B
🔒 Calculating checksum...
🔑 MD5: 5d41402abc4b2a76b9719d911017c592
✓ Connected to file transfer server at 127.0.0.1:5004

📦 Sending metadata...
📡 Sending file data...
Uploading: 100%|████████████████████| 37B/37B [00:00<00:00, 2.1KB/s]

⏳ Waiting for server acknowledgment...
✓ Upload successful!
📊 Total sent: 37 B
```

### **Method B: Real Upload/Download**

You'll need a full file transfer server (not included, but chat server can be adapted).

### **✅ Success Criteria:**
- ✓ File metadata sent correctly
- ✓ Progress bar displays
- ✓ Checksum calculated
- ✓ Upload completes successfully
- ✓ File size matches

---

## 5️⃣ Test Screen Share (TCP)

### **Step 1: Start Screen Receiver**

**Terminal 1:**
```powershell
python client/client_screen_share.py view --port 5005
```

**Expected Output:**
```
🖥️  Waiting for screen share connection on port 5005...
Press Ctrl+C to stop
```

### **Step 2: Start Screen Sharer**

**Terminal 2:**
```powershell
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
```

### **Step 3: Verify Screen Sharing**

A window should appear showing your desktop screen.

### **✅ Success Criteria:**
- ✓ Screen capture works
- ✓ Receiver window displays your screen
- ✓ FPS is around 8-10
- ✓ Screen updates smoothly
- ✓ Can see mouse movements
- ✓ Press Ctrl+C to stop

---

## 🎯 Quick Test Summary

### **Test All in 10 Minutes:**

```powershell
# 1. Chat (2 minutes)
# Terminal 1:
python simple_chat_server.py

# Terminal 2:
python client/client_chat.py -u Alice

# Terminal 3:
python client/client_chat.py -u Bob

# Type messages, press Ctrl+C when done

# 2. Video (2 minutes)
# Terminal 1:
python client/client_video.py receive

# Terminal 2:
python client/client_video.py send --ip 127.0.0.1

# Press 'q' when done

# 3. Audio (2 minutes)
# Use HEADPHONES!
# Terminal 1:
python client/client_audio.py receive

# Terminal 2:
python client/client_audio.py send --ip 127.0.0.1

# Speak, then Ctrl+C when done

# 4. File Transfer (2 minutes)
# Create test file:
echo "test" > test.txt

# Terminal 1:
python test_dummy_servers.py --mode file_server

# Terminal 2:
python client/client_file_transfer.py upload test.txt

# 5. Screen Share (2 minutes)
# Terminal 1:
python client/client_screen_share.py view

# Terminal 2:
python client/client_screen_share.py share --ip 127.0.0.1

# Press Ctrl+C when done
```

---

## 🔧 Common Issues and Solutions

### **Issue: "Address already in use"**
```powershell
# Solution: Wait 30 seconds or change port
python script.py --port 5010
```

### **Issue: Webcam not found**
```powershell
# Solution: Check camera index
python -c "import cv2; [print(f'Camera {i}') for i in range(5) if cv2.VideoCapture(i).isOpened()]"
```

### **Issue: Microphone permission denied**
```
Solution:
1. Open Windows Settings
2. Privacy & Security > Microphone
3. Allow apps to access microphone
4. Enable for Python
```

### **Issue: Firewall blocks connection**
```
Solution:
1. Windows Defender Firewall
2. Allow an app
3. Add Python
4. Check both Private and Public
```

### **Issue: Import errors**
```powershell
# Solution: Reinstall dependencies
pip install --upgrade opencv-python pyaudio PyQt5 numpy tqdm mss pillow
```

---

## 📊 Test Results Template

```
TEST RESULTS - [Date]
=====================

1. Chat Module:
   ☐ Server starts
   ☐ Clients connect
   ☐ Messages send/receive
   ☐ Commands work
   Status: PASS / FAIL
   Notes: _______________

2. Video Module:
   ☐ Webcam opens
   ☐ Video streams
   ☐ Receiver displays
   ☐ FPS acceptable
   Status: PASS / FAIL
   Notes: _______________

3. Audio Module:
   ☐ Mic detected
   ☐ Audio streams
   ☐ Playback works
   ☐ Low latency
   Status: PASS / FAIL
   Notes: _______________

4. File Transfer:
   ☐ File selected
   ☐ Metadata sent
   ☐ Upload completes
   ☐ Checksum valid
   Status: PASS / FAIL
   Notes: _______________

5. Screen Share:
   ☐ Screen captured
   ☐ Frames stream
   ☐ Display works
   ☐ Smooth updates
   Status: PASS / FAIL
   Notes: _______________

Overall: PASS / FAIL
```

---

## 🎓 Next Steps After Testing

1. **All Pass**: Try GUI (`python client/client_gui.py`)
2. **Some Fail**: Check error messages and troubleshooting
3. **Network Issues**: Test with actual LAN (different computers)
4. **Performance Issues**: Adjust quality/FPS in `shared/constants.py`

---

## 💡 Pro Tips

1. **Test localhost first** (127.0.0.1) before LAN
2. **Start receivers before senders** always
3. **Use headphones** for audio tests
4. **Close other apps** using webcam/mic
5. **Check Task Manager** if ports seem stuck
6. **Read console output** for helpful errors
7. **Test one at a time** to isolate issues

# LAN Collaboration App - GUI Guide

## 🎨 Overview

The GUI provides a unified interface for all collaboration features:
- **Video/Audio Tab**: Start/stop webcam and microphone streaming
- **Chat Tab**: Join chat rooms and send messages
- **Screen Share Tab**: Share your screen or view others
- **File Transfer Tab**: Upload and download files with progress bars

---

## 🚀 How to Run

### Start the GUI:
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_gui.py
```

### On First Launch:
1. **Enter Username**: Choose your display name
2. **Enter Server IP**: Default is `127.0.0.1` (localhost)

---

## 📹 Video/Audio Tab

### Features:
- **Start Video**: Begin streaming your webcam
- **Stop Video**: End video streaming
- **Receive Video**: Watch incoming video stream
- **Start Audio**: Begin streaming your microphone
- **Stop Audio**: End audio streaming  
- **Receive Audio**: Listen to incoming audio

### Usage:
1. Click **Start Video** to stream your webcam
2. On another computer (or terminal), click **Receive Video**
3. Video appears in OpenCV window
4. Same workflow for audio

---

## 💬 Chat Tab

### Features:
- **Join Chat**: Connect to chat server
- **Leave Chat**: Disconnect from chat
- **Send Message**: Type and send text messages
- **Chat Display**: View all messages with timestamps

### Usage:
1. Click **Join Chat**
2. Type message in text box at bottom
3. Press Enter or click **Send**
4. Messages appear in chat display with `[HH:MM:SS]` timestamps
5. Click **Leave Chat** when done

### Example:
```
[14:25:30] ✓ Joined chat as Alice
[14:25:45] Bob has joined the chat
[14:26:00] Alice: Hello everyone!
[14:26:05] Bob: Hi Alice!
```

---

## 🖥️ Screen Share Tab

### Features:
- **Share Screen**: Broadcast your screen
- **Stop Sharing**: End screen broadcast
- **View Screen**: Watch someone else's screen

### Usage:
1. Click **Share Screen** to start broadcasting
2. On another computer, click **View Screen**
3. Screen appears in OpenCV window
4. Click **Stop Sharing** to end

### Notes:
- Default quality: 80%
- Default FPS: 10
- Adjust in `shared/constants.py` for better performance

---

## 📁 File Transfer Tab

### Upload Section:
1. Click **Select File**
2. Choose file from file browser
3. Click **Upload File**
4. Watch progress bar
5. Check transfer log for status

### Download Section:
1. Enter filename in text box
2. Click **Download**
3. Choose save directory
4. Watch progress bar
5. Check transfer log for status

### Transfer Log:
```
✓ Uploaded: document.pdf
✓ Downloaded: image.png
✗ Upload failed: large_file.zip
```

---

## 🎯 Quick Start Workflow

### Two-User Video Call:

**User A (Alice):**
1. Launch GUI
2. Enter username: `Alice`
3. Enter server IP: `192.168.1.100` (Bob's IP)
4. Go to **Video/Audio** tab
5. Click **Start Video** and **Start Audio**

**User B (Bob):**
1. Launch GUI  
2. Enter username: `Bob`
3. Enter server IP: `127.0.0.1`
4. Go to **Video/Audio** tab
5. Click **Receive Video** and **Receive Audio**

---

### Group Chat:

**Everyone:**
1. Launch GUI
2. Enter unique username
3. Enter server IP (chat server address)
4. Go to **Chat** tab
5. Click **Join Chat**
6. Start messaging!

---

### Screen Sharing Presentation:

**Presenter:**
1. Launch GUI
2. Go to **Screen Share** tab
3. Click **Share Screen**

**Viewers:**
1. Launch GUI
2. Go to **Screen Share** tab
3. Click **View Screen**

---

## ⚙️ Connection Settings

### On Startup:
- **Username Dialog**: Enter your display name
- **Server IP Dialog**: Enter target server IP
  - `127.0.0.1` for local testing
  - `192.168.1.x` for LAN
  
### To Change Settings:
- Restart the application
- Enter new values in dialogs

---

## 🔘 Button States

### Active/Inactive:
- **Disabled buttons** (gray): Feature not available
- **Enabled buttons** (colored): Ready to click
- Buttons disable during operations to prevent conflicts

### Examples:
- After clicking **Join Chat**:
  - Join button → Disabled
  - Leave button → Enabled
  - Send button → Enabled

---

## 📊 Status Updates

### Bottom Status Bar:
Shows current activity:
```
Status: Ready
Status: Video streaming started
Status: Connected to chat
Status: Viewing shared screen...
```

### Connection Label:
Shows your settings:
```
User: Alice | Server: 192.168.1.100
```

---

## 🧵 Multi-Threading

### Background Operations:
All streaming operations run in background threads:
- Video streaming
- Audio streaming
- Screen sharing
- File transfers

### Benefits:
- GUI remains responsive
- Can use multiple features simultaneously
- No freezing during operations

---

## 🎨 Window Layout

```
┌────────────────────────────────────────┐
│      🌐 LAN Collaboration App          │
│  User: Alice | Server: 192.168.1.100   │
├────────────────────────────────────────┤
│ ┌──┬────┬────────┬───────┐            │
│ │📹│💬 │🖥️    │📁    │   Tabs     │
│ └──┴────┴────────┴───────┘            │
│                                        │
│  [Tab Content Area]                    │
│  - Buttons                             │
│  - Text areas                          │
│  - Progress bars                       │
│  - Status labels                       │
│                                        │
├────────────────────────────────────────┤
│ Status: Ready                          │
└────────────────────────────────────────┘
```

---

## ⌨️ Keyboard Shortcuts

### Chat:
- **Enter**: Send message (when in chat input)
- **Tab**: Switch between tabs

### General:
- **Alt+F4**: Close window (Windows)
- **Ctrl+Q**: Quit (if implemented)

---

## 🚨 Error Handling

### Error Dialogs:
Pop-up messages show when:
- Connection fails
- File not found
- Invalid input
- Network errors

### Example Messages:
```
❌ Failed to start video: Connection refused
❌ Failed to connect to chat server
⚠️ Enter a filename
```

---

## 🔧 Troubleshooting

### GUI Won't Start:
```bash
# Check PyQt5 installation
pip install PyQt5

# Check if all modules import
python -c "from PyQt5.QtWidgets import QApplication"
```

### Buttons Not Working:
- Check that required servers are running
- Verify network connection
- Check firewall settings

### Chat Not Receiving Messages:
- Ensure chat server is running
- Check that you clicked "Join Chat"
- Verify server IP is correct

### Video/Audio Windows Not Appearing:
- Check OpenCV installation
- Verify webcam/microphone permissions
- Try manual command-line versions first

---

## 💡 Tips

### Best Practices:
1. **Start Receivers First**: Launch receiving ends before senders
2. **One Feature at a Time**: Test each feature individually first
3. **Check Logs**: Watch console output for debugging
4. **Save Settings**: Remember working server IPs

### Performance:
1. **Close Unused Apps**: Free up bandwidth
2. **Use Wired Connection**: Better than WiFi
3. **Lower Quality**: If experiencing lag
4. **Close Tabs**: GUI uses less memory with fewer active features

---

## 🖱️ Common Workflows

### Workflow 1: Video Conference
```
1. Launch GUI
2. Chat Tab → Join Chat
3. Video/Audio Tab → Start Video + Start Audio
4. Chat with participants
5. Video/Audio Tab → Stop when done
6. Chat Tab → Leave Chat
```

### Workflow 2: File Sharing
```
1. Launch GUI
2. File Transfer Tab
3. Select File → Choose file
4. Upload File → Wait for completion
5. Check transfer log for confirmation
```

### Workflow 3: Presentation
```
1. Launch GUI
2. Screen Share Tab → Share Screen
3. Chat Tab → Join Chat (for Q&A)
4. Present content
5. Screen Share Tab → Stop Sharing
```

---

## 📸 Screenshot Descriptions

### Main Window:
- Clean, modern interface
- Four clearly labeled tabs
- Fusion style (native-looking)
- Emoji icons for visual appeal

### Video/Audio Tab:
- Two grouped sections
- Clear start/stop buttons
- Status indicators
- Minimal, functional design

### Chat Tab:
- Large message display area
- Input box at bottom
- Send button with emoji
- Join/Leave controls at top

### Screen Share Tab:
- Three action buttons
- Status label
- Info text
- Simple, straightforward

### File Transfer Tab:
- Upload section (select + upload)
- Download section (name + download)
- Progress bars (hidden until active)
- Transfer log at bottom

---

## 🎓 Learning Exercises

### Exercise 1: Local Test
1. Run GUI
2. Test each feature on localhost
3. Verify all buttons work
4. Check status messages

### Exercise 2: Two-Computer Setup
1. Find IP addresses
2. Launch GUI on both
3. Test video streaming between them
4. Try chat communication

### Exercise 3: Full Collaboration
1. Set up 3+ computers
2. One person shares screen
3. Everyone joins chat
4. Transfer files between users
5. Use video for face-to-face

---

## ⚡ Advanced Features

### Simultaneous Operations:
- Run video + audio + chat together
- Screen share while chatting
- Upload file while in video call

### Multi-User:
- Multiple people can view same video
- Chat supports unlimited users
- Screen share can have multiple viewers

---

## 🔒 Cleanup on Exit

### Automatic Cleanup:
When closing the GUI, it automatically:
- Disconnects from chat
- Stops video streaming
- Stops audio streaming
- Stops screen sharing
- Closes all network connections

### Manual Cleanup:
Can also manually stop each feature using stop buttons

---

## 📞 Support

### If Issues Persist:
1. Check console output for errors
2. Verify all dependencies installed
3. Test command-line versions first
4. Check network connectivity
5. Review individual testing guides

---

## 🎉 Enjoy!

The GUI provides an easy way to access all collaboration features. Experiment with different combinations and workflows to find what works best for your use case!

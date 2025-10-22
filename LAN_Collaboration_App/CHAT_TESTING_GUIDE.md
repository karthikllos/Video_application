# Chat Client Testing Guide

## 📋 What Was Created

### `client_chat.py` Features:

**ChatClient Class:**
- TCP connection to chat server
- UTF-8 message encoding/decoding
- Continuous message listening in background thread
- Message formatting: `"username: text"`
- Interactive chat interface with commands
- Automatic reconnection handling
- Timestamped message display

**Helper Functions:**
- `send_message(sock, username, text)` - Format and send message
- `receive_message(sock, timeout)` - Receive and decode message

**Built-in Commands:**
- `/quit` or `/exit` - Leave chat
- `/help` - Show available commands
- `/status` - Show connection info

### `simple_chat_server.py`:
- Multi-client TCP chat server
- Broadcasts messages to all connected clients
- Thread-per-client architecture
- Proper connection/disconnection handling

---

## 🧪 How to Test

### Step 1: Start the Chat Server

**Terminal 1 (Server):**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python simple_chat_server.py --port 5003
```

**Expected Output:**
```
🚀 Chat Server Started
📡 Listening on port 5003
💡 Clients can connect using:
   python client/client_chat.py --username <name> --ip 127.0.0.1 --port 5003

Press Ctrl+C to stop

============================================================
```

---

### Step 2: Connect First Client

**Terminal 2 (Client 1):**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
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

**Server should show:**
```
✓ New connection from 127.0.0.1:xxxxx
📨 Alice has joined the chat
```

---

### Step 3: Connect Second Client

**Terminal 3 (Client 2):**
```powershell
cd C:\Onedrive_Docs\Sem5\CN\PROJECT\LAN_Collaboration_App
python client/client_chat.py --username Bob --ip 127.0.0.1 --port 5003
```

**Expected Output:**
```
🔌 Connecting to chat server at 127.0.0.1:5003...
✓ Connected as 'Bob'
============================================================
👂 Listening for messages...

============================================================
💬 CHAT READY - Type your messages below
Commands: /quit to exit, /help for help
============================================================

```

**Alice (Terminal 2) should see:**
```
[14:23:45] Bob has joined the chat
```

---

### Step 4: Send Messages

**In Alice's terminal (Terminal 2), type:**
```
Hello everyone!
```

**Bob's terminal will show:**
```
[14:24:10] Alice: Hello everyone!
```

**In Bob's terminal (Terminal 3), type:**
```
Hi Alice!
```

**Alice's terminal will show:**
```
[14:24:15] Bob: Hi Alice!
```

---

## 🎮 Chat Commands

### While in chat, you can use these commands:

**Show Help:**
```
/help
```

**Check Status:**
```
/status
```
Output:
```
📊 Status: Connected
   Username: Alice
   Server: 127.0.0.1:5003
```

**Leave Chat:**
```
/quit
```
or
```
/exit
```

---

## 🌐 Testing on LAN (Different Computers)

### On Server Computer:

**Step 1: Find IP address**
```powershell
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Step 2: Start server**
```powershell
python simple_chat_server.py --port 5003
```

**Step 3: Allow firewall if prompted**

### On Client Computers:

**Connect using server's IP:**
```powershell
python client/client_chat.py --username YourName --ip 192.168.1.100 --port 5003
```

---

## 🔧 Testing Scenarios

### Scenario 1: Group Chat (Multiple Users)

**Terminal 1 (Server):**
```powershell
python simple_chat_server.py
```

**Terminal 2 (Alice):**
```powershell
python client/client_chat.py -u Alice
```

**Terminal 3 (Bob):**
```powershell
python client/client_chat.py -u Bob
```

**Terminal 4 (Charlie):**
```powershell
python client/client_chat.py -u Charlie
```

All users can now chat together!

---

### Scenario 2: Programmatic Message Sending

You can also use the helper functions directly:

```python
import socket
from client.client_chat import send_message, receive_message
from shared.constants import CHAT_PORT

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', CHAT_PORT))

# Send a message
send_message(sock, "TestBot", "Hello from Python!")

# Receive a message (with 5 second timeout)
message = receive_message(sock, timeout=5.0)
if message:
    print(f"Received: {message}")

sock.close()
```

---

### Scenario 3: Connection Recovery Test

1. Start server and connect clients
2. Stop server (Ctrl+C)
3. Restart server
4. Clients should detect disconnection
5. Reconnect clients manually

---

## 📊 What You Should See

### Server Output:
```
🚀 Chat Server Started
📡 Listening on port 5003
💡 Clients can connect using:
   python client/client_chat.py --username <name> --ip 127.0.0.1 --port 5003

Press Ctrl+C to stop

============================================================

✓ New connection from 127.0.0.1:52341
📨 Alice has joined the chat

✓ New connection from 127.0.0.1:52342
📨 Bob has joined the chat
📨 Alice: Hello everyone!
📨 Bob: Hi Alice!
```

### Client Output (Alice):
```
🔌 Connecting to chat server at 127.0.0.1:5003...
✓ Connected as 'Alice'
============================================================
👂 Listening for messages...

============================================================
💬 CHAT READY - Type your messages below
Commands: /quit to exit, /help for help
============================================================

[14:23:45] Bob has joined the chat
Hello everyone!
[14:24:15] Bob: Hi Alice!
```

### Client Output (Bob):
```
🔌 Connecting to chat server at 127.0.0.1:5003...
✓ Connected as 'Bob'
============================================================
👂 Listening for messages...

============================================================
💬 CHAT READY - Type your messages below
Commands: /quit to exit, /help for help
============================================================

[14:24:10] Alice: Hello everyone!
Hi Alice!
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
**Solutions:**
- Make sure server is running BEFORE connecting clients
- Check server IP and port
- Verify firewall allows connections on port 5003

### Problem: Messages not appearing
**Solutions:**
- Check that listener thread is running (should see "👂 Listening for messages...")
- Verify network connection between client and server
- Check for error messages in terminals
- Try restarting both server and client

### Problem: "Connection timeout"
**Solutions:**
- Verify server IP is correct
- Check if server is actually listening
- Ensure no firewall blocking
- Try with localhost (127.0.0.1) first

### Problem: Encoding errors
**Solutions:**
- Stick to UTF-8 compatible characters
- Avoid special/control characters
- If using emoji, ensure terminal supports UTF-8

### Problem: Client hangs on input
**Solutions:**
- Press Enter to send message
- Use /quit to exit properly
- If stuck, press Ctrl+C

### Problem: "Address already in use"
**Solutions:**
- Wait a few seconds and try again
- Change port number: `--port 5004`
- Kill existing process using the port

---

## 🔍 Technical Details

### Message Format:
```
[12-byte Protocol Header][Variable-length UTF-8 Text]

Header:
- Version (1 byte): Protocol version
- Message Type (1 byte): 0x03 (CHAT)
- Payload Length (4 bytes): Length of UTF-8 text
- Sequence Number (4 bytes)
- Reserved (2 bytes)

Example:
"Alice: Hello" → 12 bytes header + UTF-8 bytes of text
```

### Threading Model:
```
Client:
  Main Thread: User input and command handling
  Listener Thread: Continuous message reception

Server:
  Main Thread: Accept new connections
  Per-Client Thread: Handle each client's messages
```

### Connection Flow:
```
1. Client creates TCP socket
2. Client connects to server IP:PORT
3. Client sends join message
4. Client starts listener thread
5. Client enters interactive mode
6. User types messages → sent to server
7. Server broadcasts → listener thread receives → displays
8. User types /quit → sends leave message → closes socket
```

---

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] Client can connect to server
- [ ] Join message appears for all clients
- [ ] Messages are sent and received properly
- [ ] Messages show correct timestamps
- [ ] Messages show correct username formatting
- [ ] Multiple clients can chat simultaneously
- [ ] Commands (/help, /status, /quit) work
- [ ] Leave message appears when disconnecting
- [ ] Works on localhost (127.0.0.1)
- [ ] Works on LAN (different computers)

---

## 📝 Message Examples

### System Messages:
```
Alice has joined the chat
Bob has left the chat
```

### User Messages:
```
Alice: Hello everyone!
Bob: How are you?
Charlie: Great, thanks!
```

### Timestamped Display:
```
[14:23:45] Alice has joined the chat
[14:24:10] Alice: Hello everyone!
[14:24:15] Bob: How are you?
```

---

## 🚀 Next Steps

After successful testing:
1. Add private messaging (DM) functionality
2. Implement chat rooms/channels
3. Add message history/logging
4. Implement file sharing in chat
5. Add emoji support
6. Create GUI chat interface
7. Add user authentication
8. Implement message encryption
9. Add typing indicators
10. Support multimedia messages

---

## 💡 Integration Tips

### Combine with Video/Audio:
You can run all three features simultaneously:

**Terminal 1:** Chat Server
**Terminal 2:** Video Receiver  
**Terminal 3:** Audio Receiver
**Terminal 4:** Chat Client (Alice) + Video Sender + Audio Sender
**Terminal 5:** Chat Client (Bob) + Video Sender + Audio Sender

This creates a complete collaboration experience!

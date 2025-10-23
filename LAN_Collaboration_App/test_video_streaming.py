"""
Test script for video streaming functionality
Demonstrates how to test video sender and receiver locally
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║        LAN Collaboration App - Video Streaming Test           ║
╚════════════════════════════════════════════════════════════════╝

This script will help you test the video streaming functionality.

TESTING LOCALLY (Same Machine):
================================

Option 1: Using Two Terminal Windows
-------------------------------------
Terminal 1 (Receiver):
    python client/client_video.py receive --port 5001

Terminal 2 (Sender):
    python client/client_video.py send --ip 127.0.0.1 --port 5001


Option 2: Quick Test Script
----------------------------
Run this script to automatically open both sender and receiver:
    python test_video_streaming.py


TESTING ON LAN (Different Machines):
=====================================

On Receiver Machine:
    1. Find your IP address:
       Windows: ipconfig
       Linux/Mac: ifconfig or ip addr

    2. Start receiver:
       python client/client_video.py receive --port 5001

On Sender Machine:
    python client/client_video.py send --ip <RECEIVER_IP> --port 5001


CONTROLS:
=========
- Press 'q' in any window to stop
- Ctrl+C in terminal to force quit


TROUBLESHOOTING:
================
1. Webcam not working:
   - Check if another app is using the webcam
   - Try changing camera index: cv2.VideoCapture(1) instead of (0)

2. Connection refused:
   - Make sure receiver is started BEFORE sender
   - Check firewall settings (may need to allow port 5001)

3. Poor video quality:
   - Adjust VIDEO_QUALITY in shared/constants.py (0-100)
   - Change resolution in constants.py

""")

import sys
import subprocess
import time
import os

def run_local_test():
    """Run both sender and receiver in separate processes"""
    
    print("\n🎥 Starting Video Streaming Test...")
    print("=" * 60)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    client_script = os.path.join(project_dir, 'client', 'client_video.py')
    
    print(f"\n📁 Project directory: {project_dir}")
    print(f"📄 Client script: {client_script}\n")
    
    # Start receiver first
    print("🔵 Starting RECEIVER...")
    try:
        receiver_process = subprocess.Popen(
            [sys.executable, client_script, 'receive', '--port', '5001'],
            cwd=project_dir
        )
        print("✓ Receiver started (PID: {})".format(receiver_process.pid))
    except Exception as e:
        print(f"✗ Failed to start receiver: {e}")
        return
    
    # Wait a bit for receiver to initialize
    time.sleep(2)
    
    # Start sender
    print("\n🟢 Starting SENDER...")
    try:
        sender_process = subprocess.Popen(
            [sys.executable, client_script, 'send', '--ip', '127.0.0.1', '--port', '5001'],
            cwd=project_dir
        )
        print("✓ Sender started (PID: {})".format(sender_process.pid))
    except Exception as e:
        print(f"✗ Failed to start sender: {e}")
        receiver_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("✨ Both processes are running!")
    print("📹 You should see two windows:")
    print("   1. 'Video Stream - Sending' (your webcam)")
    print("   2. 'Video Stream - Receiving' (received stream)")
    print("\n💡 Press 'q' in any window or Ctrl+C here to stop")
    print("=" * 60)
    
    try:
        # Wait for processes to finish
        sender_process.wait()
        receiver_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping processes...")
        sender_process.terminate()
        receiver_process.terminate()
        sender_process.wait()
        receiver_process.wait()
        print("✓ All processes stopped")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        run_local_test()
    else:
        # Just show instructions
        response = input("\n👉 Would you like to run the automated test? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            run_local_test()
        else:
            print("\n💡 Run the commands manually as shown above!")

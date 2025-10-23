"""
Quick test script for audio streaming functionality
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║        LAN Collaboration App - Audio Streaming Test           ║
╚════════════════════════════════════════════════════════════════╝

This script will help you test the audio streaming functionality.

QUICK TEST (Echo Test - Hear Yourself):
========================================

1. Open TWO terminal windows
2. Run these commands:

   Terminal 1 (Receiver):
   ----------------------
   cd C:\\Onedrive_Docs\\Sem5\\CN\\PROJECT\\LAN_Collaboration_App
   python client/client_audio.py receive --port 5002

   Terminal 2 (Sender):
   --------------------
   cd C:\\Onedrive_Docs\\Sem5\\CN\\PROJECT\\LAN_Collaboration_App
   python client/client_audio.py send --ip 127.0.0.1 --port 5002

3. Speak into your microphone
4. You should hear your voice through speakers!
5. Press Ctrl+C to stop

IMPORTANT TIPS:
===============
⚠️  Use HEADPHONES when testing to avoid feedback/echo!
⚠️  Start RECEIVER first, then SENDER
⚠️  Grant microphone permissions if Windows prompts you

TESTING CONFIGURATION:
======================
- Sample Rate: 44100 Hz (CD Quality)
- Format: 16-bit PCM
- Channels: Stereo (2)
- Chunk Size: 1024 frames
- Expected Latency: 100-200ms
- Expected Bandwidth: ~1.4 Mbps

WHAT YOU'LL SEE:
================
✓ List of available audio devices (microphones/speakers)
✓ Real-time statistics showing packets per second
✓ Bitrate (kbps) being transmitted
✓ Audio should play through speakers with minimal delay

TROUBLESHOOTING:
================
No microphone detected?
  → Check Windows Privacy Settings → Microphone
  → Grant permission to Python

No sound?
  → Check volume levels
  → Verify correct output device is selected
  → Make sure receiver started first

Choppy audio?
  → Close other applications
  → Try wired connection instead of WiFi
  → Edit shared/constants.py: AUDIO_CHUNK = 2048

High CPU usage?
  → Edit shared/constants.py: AUDIO_CHUNK = 2048
  → Or: AUDIO_RATE = 22050 (lower quality but less CPU)

For full documentation, see: AUDIO_TESTING_GUIDE.md
""")

import sys
import subprocess
import time
import os

def run_automated_test():
    """Run both sender and receiver (may cause feedback!)"""
    
    print("\n⚠️  WARNING: This will run both sender and receiver on same machine!")
    print("This WILL cause audio feedback/echo unless you use headphones!")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    print("\n🎵 Starting Audio Streaming Test...")
    print("=" * 60)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    client_script = os.path.join(project_dir, 'client', 'client_audio.py')
    
    print(f"\n📁 Project directory: {project_dir}")
    print(f"📄 Client script: {client_script}\n")
    
    # Start receiver first
    print("🔵 Starting RECEIVER...")
    try:
        receiver_process = subprocess.Popen(
            [sys.executable, client_script, 'receive', '--port', '5002'],
            cwd=project_dir
        )
        print(f"✓ Receiver started (PID: {receiver_process.pid})")
    except Exception as e:
        print(f"✗ Failed to start receiver: {e}")
        return
    
    # Wait for receiver to initialize
    time.sleep(2)
    
    # Start sender
    print("\n🟢 Starting SENDER...")
    try:
        sender_process = subprocess.Popen(
            [sys.executable, client_script, 'send', '--ip', '127.0.0.1', '--port', '5002'],
            cwd=project_dir
        )
        print(f"✓ Sender started (PID: {sender_process.pid})")
    except Exception as e:
        print(f"✗ Failed to start sender: {e}")
        receiver_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("✨ Both processes are running!")
    print("🎤 Speak into your microphone")
    print("🔊 You should hear your voice through speakers")
    print("\n💡 Press Ctrl+C to stop both processes")
    print("=" * 60)
    
    try:
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
        run_automated_test()
    else:
        response = input("\n👉 Would you like to run the AUTOMATED test? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            run_automated_test()
        else:
            print("\n💡 Follow the manual instructions above!")
            print("📖 Or read AUDIO_TESTING_GUIDE.md for detailed instructions")

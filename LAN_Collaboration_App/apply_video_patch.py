"""
Auto-apply Video Receiving Patch to client_gui.py
Run this script to automatically add video receiving capability
"""

import shutil
from pathlib import Path

# Backup original file
gui_file = Path("client/client_gui.py")
backup_file = Path("client/client_gui_backup.py")

print("="*50)
print("VIDEO RECEIVING PATCH - AUTO INSTALLER")
print("="*50)

# Create backup
print(f"\n1. Creating backup: {backup_file}")
shutil.copy(gui_file, backup_file)
print("   ✓ Backup created")

# Read current file
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("\n2. Applying patches...")

# Patch 1: Update frame buffer variables
old1 = """        # Video frame buffers
        self.current_frame = None
        self.received_frame = None
        self.video_receive_socket = None"""

new1 = """        # Video frame buffers
        self.current_frame = None
        self.received_frames = {}  # {sender_addr: frame}
        self.video_receive_socket = None
        self.video_send_socket = None"""

if old1 in content:
    content = content.replace(old1, new1)
    print("   ✓ Updated frame buffer variables")
else:
    print("   ⚠ Could not find frame buffer section (may already be patched)")

# Patch 2: Add receive_video function after capture_video
receive_video_function = '''
    
    def receive_video(self):
        """Receive video broadcasts from server"""
        import socket
        from shared.helpers import unpack_message
        
        try:
            # Create UDP socket for receiving
            self.video_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Enable address reuse
            self.video_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set timeout
            self.video_receive_socket.settimeout(0.5)
            
            # Bind to VIDEO_PORT
            try:
                self.video_receive_socket.bind(('', VIDEO_PORT))
                self.add_system_message(f"✓ Receiving video on port {VIDEO_PORT}")
            except OSError as e:
                self.add_system_message(f"⚠ Could not bind to port {VIDEO_PORT}: {e}")
                return
            
            while self.video_active:
                try:
                    data, addr = self.video_receive_socket.recvfrom(65536)
                    
                    # Unpack message
                    version, msg_type, payload_length, seq_num, payload = unpack_message(data)
                    
                    if msg_type == 0x01:  # VIDEO message
                        # Decode JPEG frame
                        nparr = np.frombuffer(payload, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            # Store received frame
                            self.received_frames[addr] = frame
                            
                except socket.timeout:
                    pass
                except Exception as e:
                    pass
                        
        except Exception as e:
            self.add_system_message(f"Video receive error: {e}")
        finally:
            if self.video_receive_socket:
                try:
                    self.video_receive_socket.close()
                except:
                    pass
'''

# Find where to insert receive_video function
marker = "    def update_video_frame(self):"
if marker in content and "def receive_video(self):" not in content:
    content = content.replace(marker, receive_video_function + "\n    " + marker)
    print("   ✓ Added receive_video() function")
else:
    print("   ⚠ receive_video() may already exist or marker not found")

# Patch 3: Update toggle_video to call receive_video
old_toggle = '''    def toggle_video(self):
        """Toggle video"""
        if not self.video_active:
            try:
                # Start video capture in separate thread
                self.video_active = True
                threading.Thread(target=self.capture_video, daemon=True).start()
                
                self.add_system_message("Camera turned on")
            except Exception as e:
                self.add_system_message(f"Camera error: {e}")
                self.btn_camera.setChecked(False)
                self.video_active = False
        else:
            self.video_active = False
            self.current_frame = None
            self.add_system_message("Camera turned off")'''

new_toggle = '''    def toggle_video(self):
        """Toggle video"""
        if not self.video_active:
            try:
                self.video_active = True
                
                # Start video capture and sending
                threading.Thread(target=self.capture_video, daemon=True).start()
                
                # Start video receiving
                threading.Thread(target=self.receive_video, daemon=True).start()
                
                self.add_system_message("Camera ON - Broadcasting & Receiving")
            except Exception as e:
                self.add_system_message(f"Camera error: {e}")
                self.btn_camera.setChecked(False)
                self.video_active = False
        else:
            self.video_active = False
            self.current_frame = None
            if hasattr(self, 'received_frames'):
                self.received_frames.clear()
            
            # Close sockets
            if hasattr(self, 'video_send_socket') and self.video_send_socket:
                try:
                    self.video_send_socket.close()
                except:
                    pass
            if hasattr(self, 'video_receive_socket') and self.video_receive_socket:
                try:
                    self.video_receive_socket.close()
                except:
                    pass
                    
            self.add_system_message("Camera turned off")'''

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle)
    print("   ✓ Updated toggle_video() function")
else:
    print("   ⚠ toggle_video() may already be updated or format differs")

# Save patched file
with open(gui_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n3. Saving changes...")
print(f"   ✓ Saved to {gui_file}")

print("\n" + "="*50)
print("PATCH APPLIED SUCCESSFULLY!")
print("="*50)
print(f"\nBackup saved at: {backup_file}")
print("\nTo test:")
print("1. python server/server_main.py")
print("2. python client/client_gui.py  (Client 1)")
print("3. python client/client_gui.py  (Client 2)")
print("4. Both click camera button")
print("5. Check messages - should say 'Receiving video on port 5001'")
print("\nVideo broadcasting between clients is now enabled!")
print("="*50)

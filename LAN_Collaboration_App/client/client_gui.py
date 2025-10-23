"""
Google Meet-style GUI for LAN Collaboration App
Simple, clean interface with toggle buttons for video/audio
"""

import sys
import os
import threading
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QInputDialog,
    QFileDialog, QMessageBox, QGroupBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import SERVER_IP, VIDEO_PORT, AUDIO_PORT, CHAT_PORT, FILE_TRANSFER_PORT, SCREEN_SHARE_PORT

# Import client modules
from client_video import VideoStreamer, VideoReceiver
from client_audio import AudioStreamer, AudioReceiver
from client_chat import ChatClient
from client_screen_share import ScreenStreamer, ScreenReceiver
from client_file_transfer import FileTransferClient


class ChatDialog(QDialog):
    """Chat dialog with message input and file attachment"""
    
    def __init__(self, parent, chat_client):
        super().__init__(parent)
        self.parent_gui = parent
        self.chat_client = chat_client
        
        self.setWindowTitle("💬 Chat")
        self.setMinimumSize(400, 200)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize chat dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        info_label = QLabel("💬 Type your message or attach a file")
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(info_label)
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(100)
        layout.addWidget(self.message_input)
        
        # Attachment label
        self.attachment_label = QLabel("No file attached")
        self.attachment_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        layout.addWidget(self.attachment_label)
        self.attached_file = None
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Attach file button
        self.btn_attach = QPushButton("📎 Attach File")
        self.btn_attach.clicked.connect(self.attach_file)
        self.btn_attach.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #333;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
        """)
        button_layout.addWidget(self.btn_attach)
        
        button_layout.addStretch()
        
        # Send button
        self.btn_send = QPushButton("📤 Send")
        self.btn_send.clicked.connect(self.send_message)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        button_layout.addWidget(self.btn_send)
        
        # Close button
        self.btn_close = QPushButton("✕ Close Chat")
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c5221f;
            }
        """)
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
    
    def attach_file(self):
        """Attach a file to send"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Attach", "", "All Files (*.*)"
        )
        if file_path:
            self.attached_file = file_path
            filename = Path(file_path).name
            self.attachment_label.setText(f"📎 Attached: {filename}")
            self.attachment_label.setStyleSheet("color: #1a73e8; font-size: 11px;")
    
    def send_message(self):
        """Send message and/or file"""
        message_text = self.message_input.toPlainText().strip()
        
        # Send text message if present
        if message_text and self.chat_client:
            self.chat_client.send_message(message_text)
            self.parent_gui.log_status(f"💬 Sent: {message_text}")
        
        # Upload file if attached
        if self.attached_file:
            self.parent_gui.log_status(f"📤 Sending file: {Path(self.attached_file).name}")
            
            def upload_thread():
                try:
                    file_client = FileTransferClient(
                        self.parent_gui.server_ip, 
                        FILE_TRANSFER_PORT
                    )
                    success = file_client.upload_file(self.attached_file)
                    
                    if success:
                        self.parent_gui.log_status(f"✓ File sent: {Path(self.attached_file).name}")
                        # Notify in chat
                        if self.chat_client:
                            self.chat_client.send_message(
                                f"📎 Shared file: {Path(self.attached_file).name}"
                            )
                    else:
                        self.parent_gui.log_status(f"✗ File send failed")
                except Exception as e:
                    self.parent_gui.log_status(f"✗ File error: {e}")
                finally:
                    if file_client:
                        file_client.disconnect()
            
            threading.Thread(target=upload_thread, daemon=True).start()
        
        # Clear and accept if something was sent
        if message_text or self.attached_file:
            self.message_input.clear()
            self.attached_file = None
            self.attachment_label.setText("No file attached")
            self.attachment_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
            self.accept()
        else:
            QMessageBox.warning(self, "Empty Message", "Please enter a message or attach a file.")


class CollaborationGUI(QMainWindow):
    """Google Meet-style collaboration GUI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌐 LAN Collaboration")
        self.setGeometry(100, 100, 800, 600)
        
        # Connection settings
        self.server_ip = "127.0.0.1"
        self.username = "User"
        
        # Client instances
        self.video_streamer = None
        self.video_receiver = None
        self.audio_streamer = None
        self.audio_receiver = None
        self.chat_client = None
        self.screen_streamer = None
        self.file_client = None
        
        # State flags
        self.video_active = False
        self.audio_active = False
        self.chat_active = False
        self.screen_active = False
        
        # Prompt for connection details
        self.setup_connection()
        
        # Initialize UI
        self.init_ui()
    
    def setup_connection(self):
        """Get username and server IP"""
        # Get username
        username, ok = QInputDialog.getText(
            self, "Username", "Enter your username:",
            QLineEdit.Normal, "User"
        )
        if ok and username:
            self.username = username
        
        # Get server IP
        server_ip, ok = QInputDialog.getText(
            self, "Server IP", "Enter server IP address:",
            QLineEdit.Normal, "127.0.0.1"
        )
        if ok and server_ip:
            self.server_ip = server_ip
    
    def init_ui(self):
        """Initialize UI - Google Meet style"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title and connection info
        header_layout = QVBoxLayout()
        
        title = QLabel("🌐 LAN Collaboration")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        self.connection_label = QLabel(f"👤 {self.username} | 🖥️ {self.server_ip}")
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(self.connection_label)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # Main control panel (like Google Meet bottom bar)
        controls_group = QGroupBox("Meeting Controls")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 10px;
                margin-top: 10px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        controls_layout = QHBoxLayout()
        controls_group.setLayout(controls_layout)
        
        # Video toggle button
        self.btn_video = QPushButton("📹 Video\nOFF")
        self.btn_video.setMinimumSize(120, 80)
        self.btn_video.setCheckable(True)
        self.btn_video.clicked.connect(self.toggle_video)
        self.btn_video.setStyleSheet(self.get_button_style(False))
        controls_layout.addWidget(self.btn_video)
        
        # Audio toggle button
        self.btn_audio = QPushButton("🎤 Audio\nOFF")
        self.btn_audio.setMinimumSize(120, 80)
        self.btn_audio.setCheckable(True)
        self.btn_audio.clicked.connect(self.toggle_audio)
        self.btn_audio.setStyleSheet(self.get_button_style(False))
        controls_layout.addWidget(self.btn_audio)
        
        # Chat button
        self.btn_chat = QPushButton("💬 Chat")
        self.btn_chat.setMinimumSize(120, 80)
        self.btn_chat.clicked.connect(self.open_chat)
        self.btn_chat.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        controls_layout.addWidget(self.btn_chat)
        
        # Screen share button
        self.btn_screen = QPushButton("🖥️ Share\nScreen")
        self.btn_screen.setMinimumSize(120, 80)
        self.btn_screen.setCheckable(True)
        self.btn_screen.clicked.connect(self.toggle_screen_share)
        self.btn_screen.setStyleSheet(self.get_button_style(False))
        controls_layout.addWidget(self.btn_screen)
        
        # File transfer button
        self.btn_file = QPushButton("📁 Files")
        self.btn_file.setMinimumSize(120, 80)
        self.btn_file.clicked.connect(self.open_file_transfer)
        self.btn_file.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        controls_layout.addWidget(self.btn_file)
        
        main_layout.addWidget(controls_group)
        
        # Status area
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(200)
        self.status_display.setPlaceholderText("Activity log...")
        self.status_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.status_display)
        
        # Leave button (red)
        self.btn_leave = QPushButton("🚪 Leave Meeting")
        self.btn_leave.setMinimumHeight(50)
        self.btn_leave.clicked.connect(self.leave_meeting)
        self.btn_leave.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c5221f;
            }
        """)
        main_layout.addWidget(self.btn_leave)
        
        self.log_status("✓ Ready to connect")
    
    def get_button_style(self, active):
        """Get button style based on state"""
        if active:
            return """
                QPushButton {
                    background-color: #34a853;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2d8e47;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #5f6368;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4a4d50;
                }
            """
    
    # Toggle functions
    def toggle_video(self):
        """Toggle video on/off"""
        if not self.video_active:
            # Turn ON
            try:
                self.log_status("📹 Starting video...")
                self.video_streamer = VideoStreamer(self.server_ip, VIDEO_PORT)
                self.video_receiver = VideoReceiver(VIDEO_PORT)
                
                threading.Thread(target=self.video_streamer.start_streaming, daemon=True).start()
                threading.Thread(target=self.video_receiver.start_receiving, daemon=True).start()
                
                self.video_active = True
                self.btn_video.setText("📹 Video\nON")
                self.btn_video.setStyleSheet(self.get_button_style(True))
                self.log_status("✓ Video streaming active")
            except Exception as e:
                self.log_status(f"✗ Video error: {e}")
                self.btn_video.setChecked(False)
        else:
            # Turn OFF
            self.log_status("📹 Stopping video...")
            if self.video_streamer:
                self.video_streamer.stop_streaming()
            if self.video_receiver:
                self.video_receiver.stop_receiving()
            
            self.video_active = False
            self.btn_video.setText("📹 Video\nOFF")
            self.btn_video.setStyleSheet(self.get_button_style(False))
            self.log_status("✓ Video stopped")
    
    def toggle_audio(self):
        """Toggle audio on/off"""
        if not self.audio_active:
            # Turn ON
            try:
                self.log_status("🎤 Starting audio...")
                self.audio_streamer = AudioStreamer(self.server_ip, AUDIO_PORT)
                self.audio_receiver = AudioReceiver(AUDIO_PORT)
                
                threading.Thread(target=self.audio_streamer.start_streaming, daemon=True).start()
                threading.Thread(target=self.audio_receiver.start_receiving, daemon=True).start()
                
                self.audio_active = True
                self.btn_audio.setText("🎤 Audio\nON")
                self.btn_audio.setStyleSheet(self.get_button_style(True))
                self.log_status("✓ Audio streaming active")
            except Exception as e:
                self.log_status(f"✗ Audio error: {e}")
                self.btn_audio.setChecked(False)
        else:
            # Turn OFF
            self.log_status("🎤 Stopping audio...")
            if self.audio_streamer:
                self.audio_streamer.stop_streaming()
            if self.audio_receiver:
                self.audio_receiver.stop_receiving()
            
            self.audio_active = False
            self.btn_audio.setText("🎤 Audio\nOFF")
            self.btn_audio.setStyleSheet(self.get_button_style(False))
            self.log_status("✓ Audio stopped")
    
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not self.screen_active:
            # Turn ON
            try:
                self.log_status("🖥️ Starting screen share...")
                self.screen_streamer = ScreenStreamer(self.server_ip, SCREEN_SHARE_PORT)
                
                threading.Thread(target=self.screen_streamer.start_streaming, daemon=True).start()
                
                self.screen_active = True
                self.btn_screen.setText("🖥️ Sharing\nON")
                self.btn_screen.setStyleSheet(self.get_button_style(True))
                self.log_status("✓ Screen sharing active")
            except Exception as e:
                self.log_status(f"✗ Screen share error: {e}")
                self.btn_screen.setChecked(False)
        else:
            # Turn OFF
            self.log_status("🖥️ Stopping screen share...")
            if self.screen_streamer:
                self.screen_streamer.stop_streaming()
            
            self.screen_active = False
            self.btn_screen.setText("🖥️ Share\nScreen")
            self.btn_screen.setStyleSheet(self.get_button_style(False))
            self.log_status("✓ Screen sharing stopped")
    
    # Button actions
    def open_chat(self):
        """Open chat window"""
        if not self.chat_active:
            try:
                self.log_status("💬 Joining chat...")
                self.chat_client = ChatClient(self.server_ip, CHAT_PORT)
                
                if self.chat_client.connect(self.username):
                    self.chat_active = True
                    self.log_status(f"✓ Joined chat as {self.username}")
                    self.show_chat_window()
                else:
                    self.log_status("✗ Failed to join chat")
            except Exception as e:
                self.log_status(f"✗ Chat error: {e}")
        else:
            self.show_chat_window()
    
    def show_chat_window(self):
        """Show chat window with message input and attachments"""
        dialog = ChatDialog(self, self.chat_client)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # User sent message, show again
            self.show_chat_window()
        else:
            # User closed chat
            if self.chat_client:
                self.chat_client.disconnect()
                self.chat_active = False
                self.log_status("✗ Left chat")
    
    def open_file_transfer(self):
        """Open file transfer dialog"""
        choice = QMessageBox.question(
            self, "File Transfer",
            "Upload or Download?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if choice == QMessageBox.Yes:
            self.upload_file()
        elif choice == QMessageBox.No:
            self.download_file()
    
    def upload_file(self):
        """Upload file to server"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "", "All Files (*.*)"
        )
        if file_path:
            self.log_status(f"📤 Uploading {Path(file_path).name}...")
            
            def upload_thread():
                try:
                    self.file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                    success = self.file_client.upload_file(file_path)
                    
                    if success:
                        self.log_status(f"✓ Uploaded: {Path(file_path).name}")
                    else:
                        self.log_status(f"✗ Upload failed")
                except Exception as e:
                    self.log_status(f"✗ Upload error: {e}")
                finally:
                    if self.file_client:
                        self.file_client.disconnect()
            
            threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download file from server"""
        filename, ok = QInputDialog.getText(
            self, "Download File", "Enter filename to download:"
        )
        if ok and filename:
            save_dir = QFileDialog.getExistingDirectory(self, "Save to Directory")
            if save_dir:
                self.log_status(f"📥 Downloading {filename}...")
                
                def download_thread():
                    try:
                        self.file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                        success = self.file_client.download_file(filename, save_dir)
                        
                        if success:
                            self.log_status(f"✓ Downloaded: {filename}")
                        else:
                            self.log_status(f"✗ Download failed")
                    except Exception as e:
                        self.log_status(f"✗ Download error: {e}")
                    finally:
                        if self.file_client:
                            self.file_client.disconnect()
                
                threading.Thread(target=download_thread, daemon=True).start()
    
    def leave_meeting(self):
        """Leave meeting and close app"""
        reply = QMessageBox.question(
            self, "Leave Meeting",
            "Are you sure you want to leave?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cleanup()
            self.close()
    
    def log_status(self, message):
        """Log message to status display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_display.append(f"[{timestamp}] {message}")
    
    def cleanup(self):
        """Clean up all connections"""
        self.log_status("🛑 Cleaning up...")
        
        if self.video_streamer:
            self.video_streamer.stop_streaming()
        if self.video_receiver:
            self.video_receiver.stop_receiving()
        if self.audio_streamer:
            self.audio_streamer.stop_streaming()
        if self.audio_receiver:
            self.audio_receiver.stop_receiving()
        if self.screen_streamer:
            self.screen_streamer.stop_streaming()
        if self.chat_client:
            self.chat_client.disconnect()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.cleanup()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = CollaborationGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

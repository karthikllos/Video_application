"""
Graphical User Interface for LAN Collaboration App
Integrates video, audio, chat, screen sharing, and file transfer
"""

import sys
import os
import threading
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QTextEdit, QLineEdit,
    QFileDialog, QProgressBar, QGroupBox, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import SERVER_IP, VIDEO_PORT, AUDIO_PORT, CHAT_PORT, FILE_TRANSFER_PORT

# Import client modules
try:
    from client_video import VideoStreamer, VideoReceiver
    from client_audio import AudioStreamer, AudioReceiver
    from client_chat import ChatClient
    from client_screen_share import ScreenStreamer, ScreenReceiver
    from client_file_transfer import FileTransferClient
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")


class ChatSignals(QObject):
    """Signals for thread-safe GUI updates"""
    message_received = pyqtSignal(str)
    status_update = pyqtSignal(str)


class LANCollaborationGUI(QMainWindow):
    """Main GUI window for LAN Collaboration App"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAN Collaboration App")
        self.setGeometry(100, 100, 900, 700)
        
        # Connection settings
        self.server_ip = SERVER_IP
        self.username = "User"
        
        # Client instances
        self.video_streamer = None
        self.video_receiver = None
        self.audio_streamer = None
        self.audio_receiver = None
        self.chat_client = None
        self.screen_streamer = None
        self.screen_receiver = None
        self.file_client = None
        
        # Threads
        self.video_thread = None
        self.audio_thread = None
        self.screen_thread = None
        
        # Signals
        self.chat_signals = ChatSignals()
        self.chat_signals.message_received.connect(self.display_chat_message)
        self.chat_signals.status_update.connect(self.update_status)
        
        # Initialize UI
        self.init_ui()
        
        # Prompt for username and server IP
        self.setup_connection()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("🌐 LAN Collaboration App")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Connection info
        self.connection_label = QLabel("Not connected")
        self.connection_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.connection_label)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_video_tab()
        self.create_chat_tab()
        self.create_screen_share_tab()
        self.create_file_transfer_tab()
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def create_video_tab(self):
        """Create Video/Audio tab"""
        video_widget = QWidget()
        layout = QVBoxLayout()
        video_widget.setLayout(layout)
        
        # Video controls
        video_group = QGroupBox("Video Streaming")
        video_layout = QVBoxLayout()
        video_group.setLayout(video_layout)
        
        btn_layout = QHBoxLayout()
        
        self.btn_start_video = QPushButton("📹 Start Video")
        self.btn_start_video.clicked.connect(self.start_video)
        btn_layout.addWidget(self.btn_start_video)
        
        self.btn_stop_video = QPushButton("⏹ Stop Video")
        self.btn_stop_video.clicked.connect(self.stop_video)
        self.btn_stop_video.setEnabled(False)
        btn_layout.addWidget(self.btn_stop_video)
        
        self.btn_receive_video = QPushButton("📺 Receive Video")
        self.btn_receive_video.clicked.connect(self.receive_video)
        btn_layout.addWidget(self.btn_receive_video)
        
        video_layout.addLayout(btn_layout)
        
        self.video_status = QLabel("Video: Not active")
        video_layout.addWidget(self.video_status)
        
        layout.addWidget(video_group)
        
        # Audio controls
        audio_group = QGroupBox("Audio Streaming")
        audio_layout = QVBoxLayout()
        audio_group.setLayout(audio_layout)
        
        audio_btn_layout = QHBoxLayout()
        
        self.btn_start_audio = QPushButton("🎤 Start Audio")
        self.btn_start_audio.clicked.connect(self.start_audio)
        audio_btn_layout.addWidget(self.btn_start_audio)
        
        self.btn_stop_audio = QPushButton("⏹ Stop Audio")
        self.btn_stop_audio.clicked.connect(self.stop_audio)
        self.btn_stop_audio.setEnabled(False)
        audio_btn_layout.addWidget(self.btn_stop_audio)
        
        self.btn_receive_audio = QPushButton("🔊 Receive Audio")
        self.btn_receive_audio.clicked.connect(self.receive_audio)
        audio_btn_layout.addWidget(self.btn_receive_audio)
        
        audio_layout.addLayout(audio_btn_layout)
        
        self.audio_status = QLabel("Audio: Not active")
        audio_layout.addWidget(self.audio_status)
        
        layout.addWidget(audio_group)
        
        layout.addStretch()
        
        self.tabs.addTab(video_widget, "📹 Video/Audio")
    
    def create_chat_tab(self):
        """Create Chat tab"""
        chat_widget = QWidget()
        layout = QVBoxLayout()
        chat_widget.setLayout(layout)
        
        # Connection controls
        conn_layout = QHBoxLayout()
        
        self.btn_join_chat = QPushButton("🔌 Join Chat")
        self.btn_join_chat.clicked.connect(self.join_chat)
        conn_layout.addWidget(self.btn_join_chat)
        
        self.btn_leave_chat = QPushButton("🚪 Leave Chat")
        self.btn_leave_chat.clicked.connect(self.leave_chat)
        self.btn_leave_chat.setEnabled(False)
        conn_layout.addWidget(self.btn_leave_chat)
        
        layout.addLayout(conn_layout)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Chat messages will appear here...")
        layout.addWidget(self.chat_display)
        
        # Message input
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        self.btn_send = QPushButton("📤 Send")
        self.btn_send.clicked.connect(self.send_chat_message)
        self.btn_send.setEnabled(False)
        input_layout.addWidget(self.btn_send)
        
        layout.addLayout(input_layout)
        
        self.tabs.addTab(chat_widget, "💬 Chat")
    
    def create_screen_share_tab(self):
        """Create Screen Share tab"""
        screen_widget = QWidget()
        layout = QVBoxLayout()
        screen_widget.setLayout(layout)
        
        # Screen share controls
        screen_group = QGroupBox("Screen Sharing")
        screen_layout = QVBoxLayout()
        screen_group.setLayout(screen_layout)
        
        btn_layout = QHBoxLayout()
        
        self.btn_share_screen = QPushButton("🖥️ Share Screen")
        self.btn_share_screen.clicked.connect(self.share_screen)
        btn_layout.addWidget(self.btn_share_screen)
        
        self.btn_stop_screen = QPushButton("⏹ Stop Sharing")
        self.btn_stop_screen.clicked.connect(self.stop_screen_share)
        self.btn_stop_screen.setEnabled(False)
        btn_layout.addWidget(self.btn_stop_screen)
        
        self.btn_view_screen = QPushButton("👁️ View Screen")
        self.btn_view_screen.clicked.connect(self.view_screen)
        btn_layout.addWidget(self.btn_view_screen)
        
        screen_layout.addLayout(btn_layout)
        
        self.screen_status = QLabel("Screen sharing: Not active")
        screen_layout.addWidget(self.screen_status)
        
        layout.addWidget(screen_group)
        
        # Info
        info_label = QLabel(
            "Screen Sharing allows you to broadcast your screen to others or view their screens.\n"
            "Quality and FPS can be adjusted in the settings."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.tabs.addTab(screen_widget, "🖥️ Screen Share")
    
    def create_file_transfer_tab(self):
        """Create File Transfer tab"""
        file_widget = QWidget()
        layout = QVBoxLayout()
        file_widget.setLayout(layout)
        
        # Upload section
        upload_group = QGroupBox("Upload File")
        upload_layout = QVBoxLayout()
        upload_group.setLayout(upload_layout)
        
        file_layout = QHBoxLayout()
        
        self.selected_file_label = QLabel("No file selected")
        file_layout.addWidget(self.selected_file_label)
        
        self.btn_select_file = QPushButton("📁 Select File")
        self.btn_select_file.clicked.connect(self.select_file)
        file_layout.addWidget(self.btn_select_file)
        
        upload_layout.addLayout(file_layout)
        
        self.btn_upload = QPushButton("📤 Upload File")
        self.btn_upload.clicked.connect(self.upload_file)
        self.btn_upload.setEnabled(False)
        upload_layout.addWidget(self.btn_upload)
        
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        upload_layout.addWidget(self.upload_progress)
        
        layout.addWidget(upload_group)
        
        # Download section
        download_group = QGroupBox("Download File")
        download_layout = QVBoxLayout()
        download_group.setLayout(download_layout)
        
        dl_layout = QHBoxLayout()
        
        self.download_filename = QLineEdit()
        self.download_filename.setPlaceholderText("Enter filename to download...")
        dl_layout.addWidget(self.download_filename)
        
        self.btn_download = QPushButton("📥 Download")
        self.btn_download.clicked.connect(self.download_file)
        dl_layout.addWidget(self.btn_download)
        
        download_layout.addLayout(dl_layout)
        
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        download_layout.addWidget(self.download_progress)
        
        layout.addWidget(download_group)
        
        # Transfer log
        self.transfer_log = QTextEdit()
        self.transfer_log.setReadOnly(True)
        self.transfer_log.setPlaceholderText("File transfer history will appear here...")
        self.transfer_log.setMaximumHeight(200)
        layout.addWidget(self.transfer_log)
        
        layout.addStretch()
        
        self.tabs.addTab(file_widget, "📁 File Transfer")
    
    def setup_connection(self):
        """Setup connection parameters"""
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
        
        self.connection_label.setText(
            f"User: {self.username} | Server: {self.server_ip}"
        )
    
    # Video methods
    def start_video(self):
        """Start video streaming"""
        try:
            self.video_streamer = VideoStreamer(self.server_ip, VIDEO_PORT)
            self.video_thread = threading.Thread(
                target=self.video_streamer.start_streaming,
                daemon=True
            )
            self.video_thread.start()
            
            self.video_status.setText("Video: Streaming active")
            self.btn_start_video.setEnabled(False)
            self.btn_stop_video.setEnabled(True)
            self.update_status("Video streaming started")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start video: {e}")
    
    def stop_video(self):
        """Stop video streaming"""
        if self.video_streamer:
            self.video_streamer.stop_streaming()
            self.video_streamer = None
        
        self.video_status.setText("Video: Not active")
        self.btn_start_video.setEnabled(True)
        self.btn_stop_video.setEnabled(False)
        self.update_status("Video streaming stopped")
    
    def receive_video(self):
        """Receive video stream"""
        try:
            self.video_receiver = VideoReceiver(VIDEO_PORT)
            self.video_thread = threading.Thread(
                target=self.video_receiver.start_receiving,
                daemon=True
            )
            self.video_thread.start()
            self.update_status("Receiving video stream...")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to receive video: {e}")
    
    # Audio methods
    def start_audio(self):
        """Start audio streaming"""
        try:
            self.audio_streamer = AudioStreamer(self.server_ip, AUDIO_PORT)
            self.audio_thread = threading.Thread(
                target=self.audio_streamer.start_streaming,
                daemon=True
            )
            self.audio_thread.start()
            
            self.audio_status.setText("Audio: Streaming active")
            self.btn_start_audio.setEnabled(False)
            self.btn_stop_audio.setEnabled(True)
            self.update_status("Audio streaming started")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start audio: {e}")
    
    def stop_audio(self):
        """Stop audio streaming"""
        if self.audio_streamer:
            self.audio_streamer.stop_streaming()
            self.audio_streamer = None
        
        self.audio_status.setText("Audio: Not active")
        self.btn_start_audio.setEnabled(True)
        self.btn_stop_audio.setEnabled(False)
        self.update_status("Audio streaming stopped")
    
    def receive_audio(self):
        """Receive audio stream"""
        try:
            self.audio_receiver = AudioReceiver(AUDIO_PORT)
            self.audio_thread = threading.Thread(
                target=self.audio_receiver.start_receiving,
                daemon=True
            )
            self.audio_thread.start()
            self.update_status("Receiving audio stream...")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to receive audio: {e}")
    
    # Chat methods
    def join_chat(self):
        """Join chat server"""
        try:
            self.chat_client = ChatClient(self.server_ip, CHAT_PORT)
            
            if self.chat_client.connect(self.username):
                self.btn_join_chat.setEnabled(False)
                self.btn_leave_chat.setEnabled(True)
                self.btn_send.setEnabled(True)
                self.chat_input.setEnabled(True)
                
                # Start message listener
                threading.Thread(
                    target=self.chat_message_listener,
                    daemon=True
                ).start()
                
                self.display_chat_message(f"✓ Joined chat as {self.username}")
                self.update_status("Connected to chat")
            else:
                QMessageBox.warning(self, "Error", "Failed to connect to chat server")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Chat error: {e}")
    
    def leave_chat(self):
        """Leave chat server"""
        if self.chat_client:
            self.chat_client.disconnect()
            self.chat_client = None
        
        self.btn_join_chat.setEnabled(True)
        self.btn_leave_chat.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.display_chat_message("✗ Left chat")
        self.update_status("Disconnected from chat")
    
    def send_chat_message(self):
        """Send chat message"""
        message = self.chat_input.text().strip()
        if message and self.chat_client:
            self.chat_client.send_message(message)
            self.chat_input.clear()
    
    def chat_message_listener(self):
        """Listen for incoming chat messages"""
        # Note: The actual listening is handled by ChatClient's thread
        # This is a placeholder for GUI integration
        pass
    
    def display_chat_message(self, message):
        """Display message in chat area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.append(f"[{timestamp}] {message}")
    
    # Screen share methods
    def share_screen(self):
        """Start screen sharing"""
        try:
            self.screen_streamer = ScreenStreamer(self.server_ip, CHAT_PORT + 2)
            self.screen_thread = threading.Thread(
                target=self.screen_streamer.start_streaming,
                daemon=True
            )
            self.screen_thread.start()
            
            self.screen_status.setText("Screen sharing: Active")
            self.btn_share_screen.setEnabled(False)
            self.btn_stop_screen.setEnabled(True)
            self.update_status("Screen sharing started")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to share screen: {e}")
    
    def stop_screen_share(self):
        """Stop screen sharing"""
        if self.screen_streamer:
            self.screen_streamer.stop_streaming()
            self.screen_streamer = None
        
        self.screen_status.setText("Screen sharing: Not active")
        self.btn_share_screen.setEnabled(True)
        self.btn_stop_screen.setEnabled(False)
        self.update_status("Screen sharing stopped")
    
    def view_screen(self):
        """View shared screen"""
        try:
            self.screen_receiver = ScreenReceiver(CHAT_PORT + 2)
            self.screen_thread = threading.Thread(
                target=self.screen_receiver.start_receiving,
                daemon=True
            )
            self.screen_thread.start()
            self.update_status("Viewing shared screen...")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to view screen: {e}")
    
    # File transfer methods
    def select_file(self):
        """Select file for upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.setText(Path(file_path).name)
            self.btn_upload.setEnabled(True)
    
    def upload_file(self):
        """Upload selected file"""
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, "Error", "No file selected")
            return
        
        self.upload_progress.setVisible(True)
        self.upload_progress.setValue(0)
        self.btn_upload.setEnabled(False)
        
        def upload_thread():
            try:
                self.file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                success = self.file_client.upload_file(self.selected_file)
                
                if success:
                    self.transfer_log.append(
                        f"✓ Uploaded: {Path(self.selected_file).name}"
                    )
                    self.upload_progress.setValue(100)
                else:
                    self.transfer_log.append(
                        f"✗ Upload failed: {Path(self.selected_file).name}"
                    )
            except Exception as e:
                self.transfer_log.append(f"✗ Error: {e}")
            finally:
                self.btn_upload.setEnabled(True)
                if self.file_client:
                    self.file_client.disconnect()
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download file from server"""
        filename = self.download_filename.text().strip()
        if not filename:
            QMessageBox.warning(self, "Error", "Enter a filename")
            return
        
        save_dir = QFileDialog.getExistingDirectory(self, "Save to Directory")
        if not save_dir:
            return
        
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.btn_download.setEnabled(False)
        
        def download_thread():
            try:
                self.file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                success = self.file_client.download_file(filename, save_dir)
                
                if success:
                    self.transfer_log.append(f"✓ Downloaded: {filename}")
                    self.download_progress.setValue(100)
                else:
                    self.transfer_log.append(f"✗ Download failed: {filename}")
            except Exception as e:
                self.transfer_log.append(f"✗ Error: {e}")
            finally:
                self.btn_download.setEnabled(True)
                if self.file_client:
                    self.file_client.disconnect()
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(f"Status: {message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up all connections
        if self.chat_client:
            self.chat_client.disconnect()
        if self.video_streamer:
            self.video_streamer.stop_streaming()
        if self.audio_streamer:
            self.audio_streamer.stop_streaming()
        if self.screen_streamer:
            self.screen_streamer.stop_streaming()
        
        event.accept()


def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = LANCollaborationGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
"""
Modern Video Conferencing GUI - Google Meet/Zoom Style
Dark theme with grid layout, integrated chat, and sleek controls
"""

import sys
import os
import threading
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QInputDialog,
    QFileDialog, QMessageBox, QGroupBox, QDialog, QScrollArea,
    QFrame, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage
import cv2
import numpy as np

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import SERVER_IP, VIDEO_PORT, AUDIO_PORT, CHAT_PORT, FILE_TRANSFER_PORT, SCREEN_SHARE_PORT

# Import client modules
from client_video import VideoStreamer, VideoReceiver
from client_audio import AudioStreamer, AudioReceiver
from client_chat import ChatClient
from client_screen_share import ScreenStreamer, ScreenReceiver
from client_file_transfer import FileTransferClient


class ChatMessage(QWidget):
    """Individual chat message widget"""
    
    def __init__(self, username, message, timestamp, is_file=False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)
        
        # Header with username and time
        header = QHBoxLayout()
        
        username_label = QLabel(username)
        username_label.setStyleSheet("color: #a8c7fa; font-weight: bold; font-size: 13px;")
        header.addWidget(username_label)
        
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: #9aa0a6; font-size: 11px;")
        header.addWidget(time_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Message content
        if is_file:
            msg_label = QLabel(f"📎 {message}")
            msg_label.setStyleSheet("""
                color: #8ab4f8; 
                font-size: 13px;
                background-color: #1e3a5f;
                padding: 8px;
                border-radius: 5px;
            """)
        else:
            msg_label = QLabel(message)
            msg_label.setStyleSheet("color: #e8eaed; font-size: 13px;")
            msg_label.setWordWrap(True)
        
        layout.addWidget(msg_label)


class VideoTile(QFrame):
    """Individual video tile for participant"""
    
    def __init__(self, username, video_id):
        super().__init__()
        self.username = username
        self.video_id = video_id
        
        self.setStyleSheet("""
            QFrame {
                background-color: #202124;
                border: 2px solid #3c4043;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Video placeholder
        self.video_label = QLabel("📹")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            color: #5f6368;
            font-size: 48px;
            background-color: #000;
            border-radius: 8px;
        """)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setMaximumSize(640, 480)
        self.video_label.setScaledContents(False)
        layout.addWidget(self.video_label, 1)
        
        # Controls overlay (bottom)
        controls = QHBoxLayout()
        controls.addStretch()
        
        # Mute indicators
        self.mic_icon = QLabel("🎤")
        self.mic_icon.setStyleSheet("""
            background-color: rgba(60, 64, 67, 0.9);
            color: #ea4335;
            padding: 5px 8px;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.mic_icon.hide()
        controls.addWidget(self.mic_icon)
        
        self.cam_icon = QLabel("📹")
        self.cam_icon.setStyleSheet("""
            background-color: rgba(60, 64, 67, 0.9);
            color: #ea4335;
            padding: 5px 8px;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.cam_icon.hide()
        controls.addWidget(self.cam_icon)
        
        layout.addLayout(controls)
        
        # Username label
        name_label = QLabel(username)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            background-color: rgba(32, 33, 36, 0.9);
            color: #e8eaed;
            padding: 8px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: bold;
        """)
        layout.addWidget(name_label)


class ModernCollaborationGUI(QMainWindow):
    """Modern video conferencing GUI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Conference")
        self.setGeometry(50, 50, 1400, 900)
        
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
        self.chat_visible = True
        self.screen_active = False
        
        # Video frame buffer
        self.current_frame = None
        
        # Prompt for connection details
        self.setup_connection()
        
        # Initialize UI
        self.init_ui()
        
        # Video update timer
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)
        self.video_timer.start(33)  # ~30 FPS
        
        # Meeting time tracker
        self.meeting_start_time = datetime.now()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)
        
        # Auto-connect to chat
        self.connect_to_chat()
    
    def setup_connection(self):
        """Get username and server IP"""
        username, ok = QInputDialog.getText(
            self, "Join Meeting", "Enter your name:",
            QLineEdit.Normal, "User"
        )
        if ok and username:
            self.username = username
        
        server_ip, ok = QInputDialog.getText(
            self, "Server Connection", "Server IP address:",
            QLineEdit.Normal, "127.0.0.1"
        )
        if ok and server_ip:
            self.server_ip = server_ip
    
    def init_ui(self):
        """Initialize modern UI"""
        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e8eaed;
            }
            QPushButton {
                background-color: #3c4043;
                color: #e8eaed;
                border: none;
                border-radius: 24px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QPushButton:checked {
                background-color: #ea4335;
            }
        """)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Main splitter (video area | chat)
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Left side: Video grid + controls
        video_container = QWidget()
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_container.setLayout(video_layout)
        
        # Video grid area
        self.video_grid = QWidget()
        self.video_grid.setStyleSheet("background-color: #0a0a0a;")
        grid_layout = QVBoxLayout()
        self.video_grid.setLayout(grid_layout)
        
        # Add participant tiles (simulated)
        tiles_container = QWidget()
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(15)
        tiles_layout.setContentsMargins(20, 20, 20, 20)
        tiles_container.setLayout(tiles_layout)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        self.tile_self = VideoTile(self.username, "self")
        row1.addWidget(self.tile_self)
        
        tiles_layout.addLayout(row1)
        
        grid_layout.addWidget(tiles_container, 1)
        
        # Meeting info overlay (top-left)
        info_overlay = QWidget()
        info_overlay.setStyleSheet("""
            background-color: rgba(32, 33, 36, 0.95);
            border-radius: 8px;
        """)
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(15, 10, 15, 10)
        info_overlay.setLayout(info_layout)
        
        self.meeting_time = QLabel("00:00")
        self.meeting_time.setStyleSheet("color: #e8eaed; font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.meeting_time)
        
        info_layout.addWidget(QLabel("|"))
        
        self.participant_count = QLabel("👥 1")
        self.participant_count.setStyleSheet("color: #9aa0a6; font-size: 13px;")
        info_layout.addWidget(self.participant_count)
        
        info_overlay.setMaximumSize(150, 40)
        info_overlay.move(20, 20)
        
        video_layout.addWidget(self.video_grid, 1)
        
        # Bottom control bar
        control_bar = QWidget()
        control_bar.setStyleSheet("background-color: #202124;")
        control_bar.setMinimumHeight(90)
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(30, 15, 30, 15)
        control_bar.setLayout(control_layout)
        
        # Left side - meeting info
        info_section = QHBoxLayout()
        time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        time_label.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        info_section.addWidget(time_label)
        
        meeting_code = QLabel(f"Meeting: {self.server_ip}")
        meeting_code.setStyleSheet("color: #9aa0a6; font-size: 12px; margin-left: 15px;")
        info_section.addWidget(meeting_code)
        
        control_layout.addLayout(info_section)
        control_layout.addStretch()
        
        # Center - main controls
        center_controls = QHBoxLayout()
        center_controls.setSpacing(15)
        
        # Microphone toggle
        self.btn_mic = QPushButton()
        self.btn_mic.setIcon(self.style().standardIcon(self.style().SP_MediaVolume))
        self.btn_mic.setCheckable(True)
        self.btn_mic.setToolTip("Toggle Microphone")
        self.btn_mic.clicked.connect(self.toggle_audio)
        self.btn_mic.setMinimumSize(56, 56)
        self.btn_mic.setStyleSheet("""
            QPushButton {
                background-color: #3c4043;
                border-radius: 28px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QPushButton:checked {
                background-color: #ea4335;
            }
        """)
        center_controls.addWidget(self.btn_mic)
        
        # Camera toggle
        self.btn_camera = QPushButton()
        self.btn_camera.setIcon(self.style().standardIcon(self.style().SP_DialogYesButton))
        self.btn_camera.setCheckable(True)
        self.btn_camera.setToolTip("Toggle Camera")
        self.btn_camera.clicked.connect(self.toggle_video)
        self.btn_camera.setMinimumSize(56, 56)
        self.btn_camera.setStyleSheet("""
            QPushButton {
                background-color: #3c4043;
                border-radius: 28px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QPushButton:checked {
                background-color: #ea4335;
            }
        """)
        center_controls.addWidget(self.btn_camera)
        
        # Share screen
        self.btn_share = QPushButton()
        self.btn_share.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.btn_share.setCheckable(True)
        self.btn_share.setToolTip("Share Screen")
        self.btn_share.clicked.connect(self.toggle_screen_share)
        self.btn_share.setMinimumSize(56, 56)
        self.btn_share.setStyleSheet("""
            QPushButton {
                background-color: #3c4043;
                border-radius: 28px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QPushButton:checked {
                background-color: #1a73e8;
            }
        """)
        center_controls.addWidget(self.btn_share)
        
        # Leave button
        self.btn_leave = QPushButton("Leave")
        self.btn_leave.clicked.connect(self.leave_meeting)
        self.btn_leave.setMinimumSize(100, 56)
        self.btn_leave.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                border-radius: 28px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #c5221f;
            }
        """)
        center_controls.addWidget(self.btn_leave)
        
        control_layout.addLayout(center_controls)
        control_layout.addStretch()
        
        # Right side - utility buttons
        utility_controls = QHBoxLayout()
        utility_controls.setSpacing(10)
        
        # Chat toggle
        self.btn_chat_toggle = QPushButton("💬")
        self.btn_chat_toggle.setCheckable(True)
        self.btn_chat_toggle.setChecked(True)
        self.btn_chat_toggle.setToolTip("Toggle Chat")
        self.btn_chat_toggle.clicked.connect(self.toggle_chat_panel)
        self.btn_chat_toggle.setMinimumSize(48, 48)
        self.btn_chat_toggle.setStyleSheet("""
            QPushButton {
                background-color: #3c4043;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
            QPushButton:checked {
                background-color: #1a73e8;
            }
        """)
        utility_controls.addWidget(self.btn_chat_toggle)
        
        # More options
        btn_more = QPushButton("⋮")
        btn_more.setToolTip("More Options")
        btn_more.clicked.connect(self.show_more_options)
        btn_more.setMinimumSize(48, 48)
        btn_more.setStyleSheet("""
            QPushButton {
                background-color: #3c4043;
                border-radius: 24px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #5f6368;
            }
        """)
        utility_controls.addWidget(btn_more)
        
        control_layout.addLayout(utility_controls)
        
        video_layout.addWidget(control_bar)
        
        # Right side: Chat panel
        self.chat_panel = QWidget()
        self.chat_panel.setMinimumWidth(320)
        self.chat_panel.setMaximumWidth(400)
        self.chat_panel.setStyleSheet("""
            QWidget {
                background-color: #202124;
                border-left: 1px solid #3c4043;
            }
        """)
        
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_panel.setLayout(chat_layout)
        
        # Chat header
        chat_header = QWidget()
        chat_header.setStyleSheet("background-color: #292a2d; border-bottom: 1px solid #3c4043;")
        chat_header.setMinimumHeight(60)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        chat_header.setLayout(header_layout)
        
        chat_title = QLabel("💬 Chat")
        chat_title.setStyleSheet("color: #e8eaed; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(chat_title)
        
        header_layout.addStretch()
        
        btn_close_chat = QPushButton("✕")
        btn_close_chat.clicked.connect(self.toggle_chat_panel)
        btn_close_chat.setMaximumSize(32, 32)
        btn_close_chat.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9aa0a6;
                border-radius: 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3c4043;
            }
        """)
        header_layout.addWidget(btn_close_chat)
        
        chat_layout.addWidget(chat_header)
        
        # Chat messages area
        self.chat_messages = QScrollArea()
        self.chat_messages.setWidgetResizable(True)
        self.chat_messages.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #202124;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #5f6368;
                border-radius: 4px;
            }
        """)
        
        messages_container = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setAlignment(Qt.AlignTop)
        messages_container.setLayout(self.messages_layout)
        self.chat_messages.setWidget(messages_container)
        
        # Add welcome message
        self.add_system_message("Welcome to the meeting!")
        
        chat_layout.addWidget(self.chat_messages, 1)
        
        # Chat input area
        input_container = QWidget()
        input_container.setStyleSheet("background-color: #292a2d; border-top: 1px solid #3c4043;")
        input_container.setMinimumHeight(80)
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_container.setLayout(input_layout)
        
        input_row = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Send a message...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c4043;
                color: #e8eaed;
                border: 1px solid #5f6368;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #8ab4f8;
            }
        """)
        input_row.addWidget(self.chat_input)
        
        btn_send = QPushButton("➤")
        btn_send.clicked.connect(self.send_chat_message)
        btn_send.setMaximumSize(40, 40)
        btn_send.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        input_row.addWidget(btn_send)
        
        input_layout.addLayout(input_row)
        
        # File attach button
        btn_attach = QPushButton("📎 Attach File")
        btn_attach.clicked.connect(self.attach_and_send_file)
        btn_attach.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8ab4f8;
                border: none;
                text-align: left;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #aecbfa;
            }
        """)
        input_layout.addWidget(btn_attach)
        
        chat_layout.addWidget(input_container)
        
        # Add to splitter
        self.splitter.addWidget(video_container)
        self.splitter.addWidget(self.chat_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
    
    def add_system_message(self, message):
        """Add system message to chat"""
        msg_widget = QWidget()
        msg_layout = QVBoxLayout()
        msg_layout.setContentsMargins(10, 5, 10, 5)
        msg_widget.setLayout(msg_layout)
        
        label = QLabel(f"ℹ️ {message}")
        label.setStyleSheet("""
            color: #9aa0a6;
            font-size: 12px;
            font-style: italic;
            padding: 8px;
        """)
        label.setAlignment(Qt.AlignCenter)
        msg_layout.addWidget(label)
        
        self.messages_layout.addWidget(msg_widget)
        self.chat_messages.verticalScrollBar().setValue(
            self.chat_messages.verticalScrollBar().maximum()
        )
    
    def connect_to_chat(self):
        """Connect to chat server automatically"""
        try:
            self.chat_client = ChatClient(self.server_ip, CHAT_PORT)
            if self.chat_client.connect(self.username):
                self.add_system_message(f"Connected as {self.username}")
            else:
                self.add_system_message("Chat connection failed")
        except Exception as e:
            self.add_system_message(f"Chat error: {e}")
    
    def send_chat_message(self):
        """Send chat message"""
        message = self.chat_input.text().strip()
        if message:
            # Add to UI
            timestamp = datetime.now().strftime("%I:%M %p")
            msg = ChatMessage(self.username, message, timestamp)
            self.messages_layout.addWidget(msg)
            
            # Send via client
            if self.chat_client:
                try:
                    self.chat_client.send_message(message)
                except:
                    self.add_system_message("Failed to send message")
            
            self.chat_input.clear()
            self.chat_messages.verticalScrollBar().setValue(
                self.chat_messages.verticalScrollBar().maximum()
            )
    
    def attach_and_send_file(self):
        """Attach and send file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            filename = Path(file_path).name
            timestamp = datetime.now().strftime("%I:%M %p")
            msg = ChatMessage(self.username, filename, timestamp, is_file=True)
            self.messages_layout.addWidget(msg)
            
            # Upload file
            def upload_thread():
                try:
                    file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                    file_client.upload_file(file_path)
                    file_client.disconnect()
                except Exception as e:
                    print(f"File upload error: {e}")
            
            threading.Thread(target=upload_thread, daemon=True).start()
            
            self.chat_messages.verticalScrollBar().setValue(
                self.chat_messages.verticalScrollBar().maximum()
            )
    
    
    def toggle_video(self):
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
            self.add_system_message("Camera turned off")
    
    def capture_video(self):
        """Capture video from webcam and stream to server"""
        import socket
        from shared.helpers import pack_message
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.add_system_message("Failed to open camera")
            return
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            while self.video_active:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Store frame for display
                self.current_frame = frame.copy()
                
                # Compress and send
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                _, encoded = cv2.imencode('.jpg', frame, encode_param)
                packet = pack_message(0x01, encoded.tobytes())  # VIDEO = 0x01
                
                try:
                    sock.sendto(packet, (self.server_ip, VIDEO_PORT))
                except:
                    pass
                
        finally:
            cap.release()
            sock.close()
    
    
    def update_video_frame(self):
        """Update video display in GUI"""
        try:
            if self.current_frame is not None and self.video_active:
                # Resize frame to fixed size first
                frame_resized = cv2.resize(self.current_frame, (320, 240))
                
                # Convert frame to QPixmap
                frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                
                # Set pixmap directly (already correct size)
                self.tile_self.video_label.setPixmap(pixmap)
        except (RuntimeError, AttributeError, Exception) as e:
            # Widget has been deleted or other error, stop timer
            pass
    
    def toggle_audio(self):
        """Toggle audio"""
        if not self.audio_active:
            try:
                self.add_system_message("Starting audio...")
                
                # Start audio streaming
                self.audio_streamer = AudioStreamer(self.server_ip, AUDIO_PORT)
                audio_thread = threading.Thread(target=self._run_audio_streamer, daemon=True)
                audio_thread.start()
                
                self.audio_active = True
                self.add_system_message("Microphone turned on")
            except Exception as e:
                self.add_system_message(f"Microphone error: {e}")
                self.btn_mic.setChecked(False)
                self.audio_active = False
        else:
            self.audio_active = False
            if self.audio_streamer:
                try:
                    self.audio_streamer.stop_streaming()
                except:
                    pass
            self.add_system_message("Microphone turned off")
    
    def _run_audio_streamer(self):
        """Run audio streamer in thread"""
        try:
            if self.audio_streamer:
                self.audio_streamer.start_streaming()
        except Exception as e:
            self.add_system_message(f"Audio streaming error: {e}")
    
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not self.screen_active:
            try:
                self.screen_streamer = ScreenStreamer(self.server_ip, SCREEN_SHARE_PORT)
                threading.Thread(target=self.screen_streamer.start_streaming, daemon=True).start()
                
                self.screen_active = True
                self.add_system_message("Screen sharing started")
            except Exception as e:
                self.add_system_message(f"Screen share error: {e}")
                self.btn_share.setChecked(False)
        else:
            if self.screen_streamer:
                self.screen_streamer.stop_streaming()
            
            self.screen_active = False
            self.add_system_message("Screen sharing stopped")
    
    def toggle_chat_panel(self):
        """Toggle chat panel visibility"""
        self.chat_visible = not self.chat_visible
        self.chat_panel.setVisible(self.chat_visible)
        self.btn_chat_toggle.setChecked(self.chat_visible)
    
    def show_more_options(self):
        """Show more options menu"""
        menu = QMessageBox(self)
        menu.setWindowTitle("More Options")
        menu.setText("Choose an option:")
        
        btn_settings = menu.addButton("⚙️ Settings", QMessageBox.ActionRole)
        btn_files = menu.addButton("📁 File Transfer", QMessageBox.ActionRole)
        btn_download = menu.addButton("📥 Download File", QMessageBox.ActionRole)
        btn_cancel = menu.addButton("Cancel", QMessageBox.RejectRole)
        
        menu.exec_()
        
        if menu.clickedButton() == btn_files:
            self.upload_file()
        elif menu.clickedButton() == btn_download:
            self.download_file()
    
    def upload_file(self):
        """Upload file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload File", "", "All Files (*.*)")
        if file_path:
            self.add_system_message(f"Uploading {Path(file_path).name}...")
            
            def upload_thread():
                try:
                    file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                    success = file_client.upload_file(file_path)
                    file_client.disconnect()
                    
                    if success:
                        self.add_system_message(f"✓ Uploaded {Path(file_path).name}")
                except Exception as e:
                    self.add_system_message(f"Upload failed: {e}")
            
            threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download file"""
        filename, ok = QInputDialog.getText(self, "Download File", "Enter filename:")
        if ok and filename:
            save_dir = QFileDialog.getExistingDirectory(self, "Save to Directory")
            if save_dir:
                self.add_system_message(f"Downloading {filename}...")
                
                def download_thread():
                    try:
                        file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                        success = file_client.download_file(filename, save_dir)
                        file_client.disconnect()
                        
                        if success:
                            self.add_system_message(f"✓ Downloaded {filename}")
                    except Exception as e:
                        self.add_system_message(f"Download failed: {e}")
                
                threading.Thread(target=download_thread, daemon=True).start()
    
    def leave_meeting(self):
        """Leave meeting"""
        reply = QMessageBox.question(
            self, "Leave Meeting",
            "Are you sure you want to leave the meeting?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.add_system_message("Leaving meeting...")
            self.cleanup()
            self.close()
    
    def update_ui(self):
        """Update UI elements periodically"""
        try:
            # Update meeting time
            elapsed = datetime.now() - self.meeting_start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.meeting_time.setText(f"{minutes:02d}:{seconds:02d}")
        except (RuntimeError, AttributeError):
            # Widget has been deleted, stop timer
            self.update_timer.stop()
    
    def cleanup(self):
        """Cleanup all connections"""
        # Stop timers first
        try:
            self.update_timer.stop()
            self.video_timer.stop()
        except:
            pass
        
        # Stop all services
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
    
    # Set application-wide dark palette
    from PyQt5.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.WindowText, QColor(232, 234, 237))
    palette.setColor(QPalette.Base, QColor(32, 33, 36))
    palette.setColor(QPalette.AlternateBase, QColor(42, 43, 46))
    palette.setColor(QPalette.ToolTipBase, QColor(232, 234, 237))
    palette.setColor(QPalette.ToolTipText, QColor(232, 234, 237))
    palette.setColor(QPalette.Text, QColor(232, 234, 237))
    palette.setColor(QPalette.Button, QColor(60, 64, 67))
    palette.setColor(QPalette.ButtonText, QColor(232, 234, 237))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(138, 180, 248))
    palette.setColor(QPalette.Highlight, QColor(26, 115, 232))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = ModernCollaborationGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
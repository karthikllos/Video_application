"""
Modern Video Conferencing GUI - Fixed Version
Fixes: Video broadcast, file transfer acknowledgment, audio termination, error handling
"""

"""
Modern Video Conferencing GUI - Fixed Version
"""

import sys
import os

# FIX: Add project root to path FIRST
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now the rest of your imports
import threading
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QInputDialog,
    QFileDialog, QMessageBox, QScrollArea,
    QFrame, QSplitter, QGridLayout
)
# ... rest of imports
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QImage
import cv2
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.constants import (
    SERVER_IP, VIDEO_PORT, AUDIO_PORT, CHAT_PORT, 
    FILE_TRANSFER_PORT, SCREEN_SHARE_PORT
)

# Core client modules (only import what's actually used)
from client_audio import AudioStreamer
from client_chat import ChatClient
from client_screen_share import ScreenStreamer
from client_file_transfer import FileTransferClient


class ChatMessage(QWidget):
    """Individual chat message bubble widget"""
    
    def __init__(self, username, message, timestamp, is_file=False):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)
        
        header = QHBoxLayout()
        username_label = QLabel(username)
        username_label.setStyleSheet(
            "color: #a8c7fa; font-weight: bold; font-size: 13px;"
        )
        header.addWidget(username_label)
        
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: #9aa0a6; font-size: 11px;")
        header.addWidget(time_label)
        header.addStretch()
        layout.addLayout(header)
        
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
    """Individual video tile for participant display"""
    
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
        
        controls = QHBoxLayout()
        controls.addStretch()
        
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


class GUISignals(QObject):
    """Thread-safe signals for GUI updates"""
    status_message = pyqtSignal(str)
    video_frame_ready = pyqtSignal(str, object)
    user_list_updated = pyqtSignal(list)
    chat_message_received = pyqtSignal(str, str)


class ModernCollaborationGUI(QMainWindow):
    """Main video conferencing GUI window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Conference")
        self.setGeometry(50, 50, 1400, 900)
        
        self.server_ip = "127.0.0.1"
        self.username = "User"
        
        # Client module instances
        self.audio_streamer = None
        self.chat_client = None
        self.screen_streamer = None
        
        self.video_active = False
        self.audio_active = False
        self.chat_visible = True
        self.screen_active = False
        
        self.current_frame = None
        self.received_frames = {}
        self.video_receive_socket = None
        self.video_send_socket = None
        self.video_capture = None
        
        self.user_tiles = {}
        self.connected_users = []
        
        # Audio streaming thread reference
        self.audio_thread = None
        
        self.gui_signals = GUISignals()
        self.gui_signals.status_message.connect(self.add_system_message)
        self.gui_signals.user_list_updated.connect(self.update_user_tiles)
        self.gui_signals.chat_message_received.connect(self.display_received_message)
        
        self.setup_connection()
        self.init_ui()
        
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)
        self.video_timer.start(33)
        
        self.meeting_start_time = datetime.now()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)
        
        # Initialize grid layout with self tile
        self._reorganize_grid_layout()
        
        QTimer.singleShot(500, self.connect_to_chat)
    
    def setup_connection(self):
        """Prompt user for connection details"""
        username, ok = QInputDialog.getText(
            self, "Join Meeting", "Enter your name:",
            QLineEdit.Normal, "User"
        )
        if ok and username.strip():
            self.username = username.strip()
        
        server_ip, ok = QInputDialog.getText(
            self, "Server Connection", "Server IP address:",
            QLineEdit.Normal, "127.0.0.1"
        )
        if ok and server_ip.strip():
            self.server_ip = server_ip.strip()
    
    def init_ui(self):
        """Initialize the user interface"""
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
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        video_container = QWidget()
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_container.setLayout(video_layout)
        
        self.video_grid = QWidget()
        self.video_grid.setStyleSheet("background-color: #0a0a0a;")
        main_grid_layout = QVBoxLayout()
        main_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.video_grid.setLayout(main_grid_layout)
        
        # Main tiles container with grid layout
        self.tiles_container = QWidget()
        self.tiles_grid = QGridLayout()
        self.tiles_grid.setSpacing(15)
        self.tiles_grid.setContentsMargins(20, 20, 20, 20)
        self.tiles_container.setLayout(self.tiles_grid)
        
        # Create self tile (will be positioned in bottom-right)
        self.tile_self = VideoTile(self.username + " (You)", "self")
        self.tile_self.setMinimumSize(200, 150)
        self.tile_self.setMaximumSize(300, 225)
        
        main_grid_layout.addWidget(self.tiles_container, 1)
        
        info_overlay = QWidget()
        info_overlay.setStyleSheet("""
            background-color: rgba(32, 33, 36, 0.95);
            border-radius: 8px;
        """)
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(15, 10, 15, 10)
        info_overlay.setLayout(info_layout)
        
        self.meeting_time = QLabel("00:00")
        self.meeting_time.setStyleSheet(
            "color: #e8eaed; font-size: 14px; font-weight: bold;"
        )
        info_layout.addWidget(self.meeting_time)
        
        info_layout.addWidget(QLabel("|"))
        
        self.participant_count = QLabel("👥 1")
        self.participant_count.setStyleSheet("color: #9aa0a6; font-size: 13px;")
        info_layout.addWidget(self.participant_count)
        
        info_overlay.setMaximumSize(150, 40)
        info_overlay.move(20, 20)
        
        video_layout.addWidget(self.video_grid, 1)
        
        control_bar = self._create_control_bar()
        video_layout.addWidget(control_bar)
        
        self.chat_panel = self._create_chat_panel()
        
        self.splitter.addWidget(video_container)
        self.splitter.addWidget(self.chat_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
    
    def _create_control_bar(self):
        """Create the bottom control bar with buttons"""
        control_bar = QWidget()
        control_bar.setStyleSheet("background-color: #202124;")
        control_bar.setMinimumHeight(90)
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(30, 15, 30, 15)
        control_bar.setLayout(control_layout)
        
        info_section = QHBoxLayout()
        time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        time_label.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        info_section.addWidget(time_label)
        
        meeting_code = QLabel(f"Meeting: {self.server_ip}")
        meeting_code.setStyleSheet(
            "color: #9aa0a6; font-size: 12px; margin-left: 15px;"
        )
        info_section.addWidget(meeting_code)
        
        control_layout.addLayout(info_section)
        control_layout.addStretch()
        
        center_controls = QHBoxLayout()
        center_controls.setSpacing(15)
        
        self.btn_mic = self._create_control_button(
            "SP_MediaVolume", "Toggle Microphone", self.toggle_audio
        )
        center_controls.addWidget(self.btn_mic)
        
        self.btn_camera = self._create_control_button(
            "SP_DialogYesButton", "Toggle Camera", self.toggle_video
        )
        center_controls.addWidget(self.btn_camera)
        
        self.btn_share = self._create_control_button(
            "SP_FileIcon", "Share Screen", self.toggle_screen_share, "#1a73e8"
        )
        center_controls.addWidget(self.btn_share)
        
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
        
        utility_controls = QHBoxLayout()
        utility_controls.setSpacing(10)
        
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
        
        return control_bar
    
    def _create_control_button(self, icon_name, tooltip, callback, checked_color="#ea4335"):
        """Helper to create control buttons"""
        btn = QPushButton()
        btn.setIcon(self.style().standardIcon(getattr(self.style(), icon_name)))
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        btn.setMinimumSize(56, 56)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3c4043;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background-color: #5f6368;
            }}
            QPushButton:checked {{
                background-color: {checked_color};
            }}
        """)
        return btn
    
    def _create_chat_panel(self):
        """Create the chat panel widget"""
        chat_panel = QWidget()
        chat_panel.setMinimumWidth(320)
        chat_panel.setMaximumWidth(400)
        chat_panel.setStyleSheet("""
            QWidget {
                background-color: #202124;
                border-left: 1px solid #3c4043;
            }
        """)
        
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_panel.setLayout(chat_layout)
        
        chat_header = QWidget()
        chat_header.setStyleSheet(
            "background-color: #292a2d; border-bottom: 1px solid #3c4043;"
        )
        chat_header.setMinimumHeight(60)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        chat_header.setLayout(header_layout)
        
        chat_title = QLabel("💬 Chat")
        chat_title.setStyleSheet(
            "color: #e8eaed; font-size: 16px; font-weight: bold;"
        )
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
        
        self.add_system_message("Welcome to the meeting!")
        
        chat_layout.addWidget(self.chat_messages, 1)
        
        input_container = self._create_chat_input()
        chat_layout.addWidget(input_container)
        
        return chat_panel
    
    def _create_chat_input(self):
        """Create the chat input area"""
        input_container = QWidget()
        input_container.setStyleSheet(
            "background-color: #292a2d; border-top: 1px solid #3c4043;"
        )
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
        
        return input_container
    
    def add_system_message(self, message):
        """Add system notification to chat"""
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
        
        scrollbar = self.chat_messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def connect_to_chat(self):
        """Establish chat server connection"""
        try:
            self.chat_client = ChatClient(self.server_ip, CHAT_PORT)
            if self.chat_client.connect(self.username):
                self.chat_client.set_user_list_callback(self.on_user_list_update)
                self.chat_client.set_message_callback(self.on_chat_message_received)
                self.add_system_message(f"Connected as {self.username}")
                return True
            else:
                self.add_system_message("Chat connection failed")
                return False
        except Exception as e:
            self.add_system_message(f"Chat error: {str(e)}")
            return False
    
    def on_user_list_update(self, user_list):
        """Called when user list is updated from server"""
        self.gui_signals.user_list_updated.emit(user_list)
    
    def on_chat_message_received(self, message, timestamp):
        """Called when chat message is received"""
        self.gui_signals.chat_message_received.emit(message, timestamp)
    
    def display_received_message(self, message, timestamp):
        """Display received chat message in GUI"""
        try:
            from datetime import datetime
            time_obj = datetime.strptime(timestamp, "%H:%M:%S")
            display_time = time_obj.strftime("%I:%M %p")
        except:
            display_time = timestamp
        
        if ": " in message:
            username, text = message.split(": ", 1)
            msg_widget = ChatMessage(username, text, display_time)
        else:
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
        
        scrollbar = self.chat_messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_user_tiles(self, user_list):
        """Update video tiles based on connected users with dynamic grid layout"""
        self.connected_users = user_list
        
        # Remove tiles for disconnected users
        for username in list(self.user_tiles.keys()):
            if username not in user_list and username != self.username:
                tile = self.user_tiles[username]
                self.tiles_grid.removeWidget(tile)
                tile.deleteLater()
                del self.user_tiles[username]
        
        # Add tiles for new users
        for username in user_list:
            if username != self.username and username not in self.user_tiles:
                tile = VideoTile(username, username)
                self.user_tiles[username] = tile
        
        # Update participant count
        total_count = len(user_list) + 1
        self.participant_count.setText(f"👥 {total_count}")
        
        # Reorganize layout
        self._reorganize_grid_layout()
    
    def _reorganize_grid_layout(self):
        """Reorganize video tiles in optimal grid with self in bottom-right"""
        # Clear existing layout
        while self.tiles_grid.count():
            item = self.tiles_grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Get all other users (excluding self)
        other_users = list(self.user_tiles.keys())
        num_others = len(other_users)
        total_participants = num_others + 1  # +1 for self
        
        if total_participants == 1:
            # Only self - center it
            self.tiles_grid.addWidget(self.tile_self, 0, 0, 1, 1)
            return
        
        # Calculate optimal grid dimensions
        import math
        
        if total_participants == 2:
            cols, rows = 2, 1
        elif total_participants <= 4:
            cols, rows = 2, 2
        elif total_participants <= 6:
            cols, rows = 3, 2
        elif total_participants <= 9:
            cols, rows = 3, 3
        elif total_participants <= 12:
            cols, rows = 4, 3
        else:
            cols = math.ceil(math.sqrt(total_participants))
            rows = math.ceil(total_participants / cols)
        
        # Place other users first (left-to-right, top-to-bottom)
        idx = 0
        for row in range(rows):
            for col in range(cols):
                # Reserve bottom-right spot for self
                is_bottom_right = (row == rows - 1 and col == cols - 1)
                
                if is_bottom_right:
                    # Place self tile in bottom-right
                    self.tiles_grid.addWidget(self.tile_self, row, col, 1, 1)
                elif idx < num_others:
                    # Place other user tile
                    username = other_users[idx]
                    tile = self.user_tiles[username]
                    self.tiles_grid.addWidget(tile, row, col, 1, 1)
                    idx += 1
        
        # If we didn't place self yet (odd number of tiles), place in last position
        if idx == num_others and total_participants > 1:
            # Calculate position for remaining spot
            row = idx // cols
            col = idx % cols
            self.tiles_grid.addWidget(self.tile_self, row, col, 1, 1)
    
    def send_chat_message(self):
        """Send chat message to server"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        if not self.chat_client:
            self.connect_to_chat()
        
        if self.chat_client:
            try:
                success = self.chat_client.send_message(message)
                if not success:
                    self.add_system_message("Failed to send message")
            except Exception as e:
                self.add_system_message(f"Failed to send: {str(e)}")
        
        self.chat_input.clear()
    
    def attach_and_send_file(self):
        """Select and upload file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if not file_path:
            return
        
        filename = Path(file_path).name
        timestamp = datetime.now().strftime("%I:%M %p")
        msg = ChatMessage(self.username, filename, timestamp, is_file=True)
        self.messages_layout.addWidget(msg)
        
        def upload_thread():
            try:
                file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                if file_client.connect():
                    success = file_client.upload_file(file_path)
                    file_client.disconnect()
                    if success:
                        self.gui_signals.status_message.emit(f"✓ Uploaded {filename}")
                    else:
                        self.gui_signals.status_message.emit(f"Upload failed: {filename}")
                else:
                    self.gui_signals.status_message.emit("Could not connect to file server")
            except Exception as e:
                self.gui_signals.status_message.emit(f"Upload error: {str(e)}")
        
        threading.Thread(target=upload_thread, daemon=True).start()
        
        scrollbar = self.chat_messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def toggle_video(self):
        """Toggle video streaming - FIXED VERSION"""
        if not self.video_active:
            try:
                self.video_active = True
                # Start capture thread
                threading.Thread(target=self.capture_video, daemon=True).start()
                # Start receive thread with delay to allow server setup
                threading.Thread(target=self.receive_video_delayed, daemon=True).start()
                self.add_system_message("Camera ON - Broadcasting")
            except Exception as e:
                self.add_system_message(f"Camera error: {str(e)}")
                self.btn_camera.setChecked(False)
                self.video_active = False
        else:
            self.video_active = False
            self.current_frame = None
            self.received_frames.clear()
            
            # Hide camera icons
            self.tile_self.cam_icon.hide()
            for tile in self.user_tiles.values():
                tile.cam_icon.hide()
            
            if self.video_capture:
                try:
                    self.video_capture.release()
                except:
                    pass
                self.video_capture = None
            
            if self.video_send_socket:
                try:
                    self.video_send_socket.close()
                except:
                    pass
                self.video_send_socket = None
            
            if self.video_receive_socket:
                try:
                    self.video_receive_socket.close()
                except:
                    pass
                self.video_receive_socket = None
            
            self.add_system_message("Camera turned off")
    
    def receive_video_delayed(self):
        """Delayed start for video receiver to avoid conflicts"""
        time.sleep(0.5)  # Wait 500ms before starting receiver
        self.receive_video()
    
    def capture_video(self):
        """Capture and stream video from webcam - FIXED"""
        import socket
        from shared.helpers import pack_message
        from shared.protocol import VIDEO
        
        # Try DirectShow first (Windows), fallback to default
        self.video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.video_capture.isOpened():
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                self.gui_signals.status_message.emit(
                    "❌ Camera unavailable - check if in use"
                )
                self.video_active = False
                self.btn_camera.setChecked(False)
                return
        
        self.video_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            frame_count = 0
            while self.video_active:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                
                self.current_frame = frame.copy()
                
                # Compress frame
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                _, encoded = cv2.imencode('.jpg', frame, encode_param)
                packet = pack_message(VIDEO, encoded.tobytes())
                
                try:
                    self.video_send_socket.sendto(
                        packet, (self.server_ip, VIDEO_PORT)
                    )
                    frame_count += 1
                except Exception as e:
                    if self.video_active:
                        print(f"Send error: {e}")
                
                # Small delay to control frame rate (~30 FPS)
                time.sleep(0.033)
        except Exception as e:
            self.gui_signals.status_message.emit(f"Video error: {str(e)}")
        finally:
            if self.video_capture:
                try:
                    self.video_capture.release()
                except:
                    pass
            if self.video_send_socket:
                try:
                    self.video_send_socket.close()
                except:
                    pass
    
    def receive_video(self):
        """Receive video broadcasts from server - FIXED"""
        import socket
        from shared.helpers import unpack_message
        from shared.protocol import VIDEO
        
        try:
            self.video_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.video_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.video_receive_socket.settimeout(0.5)
            
            # Bind to receive broadcasts
            self.video_receive_socket.bind(('', 0))
            local_port = self.video_receive_socket.getsockname()[1]
            
            # Send registration packet
            from shared.helpers import pack_message
            for _ in range(3):
                register_packet = pack_message(VIDEO, b"REGISTER")
                try:
                    self.video_receive_socket.sendto(register_packet, (self.server_ip, VIDEO_PORT))
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Registration error: {e}")

            self.gui_signals.status_message.emit(
                f"✓ Video receiver registered"
            )
            
            try:
                while self.video_active:
                    try:
                        data, addr = self.video_receive_socket.recvfrom(65536)
                        
                        # Accept all packets from server (server broadcasts to all clients)
                        # No need to filter by address since server handles the broadcasting
                        
                        try:
                            version, msg_type, payload_length, seq_num, payload = unpack_message(data)
                            if msg_type == VIDEO and len(payload) > 0:
                                # Decode JPEG frame
                                nparr = np.frombuffer(payload, np.uint8)
                                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                
                                if frame is not None:
                                    # Store received frame
                                    self.received_frames['broadcast'] = frame
                        except Exception as e:
                            pass  # Silently ignore decode errors
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.video_active:
                            pass  # Silently ignore receive errors
            except Exception as e:
                if self.video_active:
                    print(f"Video receive error: {e}")
        finally:
            if self.video_receive_socket:
                try:
                    self.video_receive_socket.close()
                except:
                    pass
    
    def update_video_frame(self):
        """Update video display in GUI (called by timer)"""
        try:
            # Update self video
            if self.current_frame is not None and self.video_active:
                frame_resized = cv2.resize(self.current_frame, (320, 240))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(
                    frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(qt_image)
                self.tile_self.video_label.setPixmap(pixmap)
                # Show camera icon to indicate video is active
                self.tile_self.cam_icon.show()
            
            # Update received video frames
            if 'broadcast' in self.received_frames:
                frame = self.received_frames['broadcast']
                # Display on first available tile (since server broadcasts to all)
                if len(self.user_tiles) > 0:
                    first_tile = list(self.user_tiles.values())[0]
                    frame_resized = cv2.resize(frame, (320, 240))
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame_rgb.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(
                        frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
                    )
                    pixmap = QPixmap.fromImage(qt_image)
                    first_tile.video_label.setPixmap(pixmap)
                    # Show camera icon to indicate video is active
                    first_tile.cam_icon.show()
        except (RuntimeError, AttributeError):
            pass  # Widget deleted, ignore
    
    def toggle_audio(self):
        """Toggle audio streaming - FIXED to prevent termination"""
        if not self.audio_active:
            try:
                self.add_system_message("Starting audio...")
                self.audio_streamer = AudioStreamer(self.server_ip, AUDIO_PORT)
                
                # Run in daemon thread so it doesn't block app termination
                self.audio_thread = threading.Thread(
                    target=self._run_audio_streamer, daemon=True
                )
                self.audio_thread.start()
                
                self.audio_active = True
                self.add_system_message("Microphone turned on")
            except Exception as e:
                self.add_system_message(f"Microphone error: {str(e)}")
                self.btn_mic.setChecked(False)
                self.audio_active = False
        else:
            self.audio_active = False
            if self.audio_streamer:
                try:
                    # Stop the streamer gracefully
                    self.audio_streamer.running = False
                    self.audio_streamer.stop_streaming()
                except Exception as e:
                    print(f"Error stopping audio: {e}")
            self.audio_streamer = None
            self.add_system_message("Microphone turned off")
    
    def _run_audio_streamer(self):
        """Run audio streamer in background thread - FIXED"""
        try:
            if self.audio_streamer:
                self.audio_streamer.start_streaming()
        except Exception as e:
            # Don't crash the app if audio fails
            self.gui_signals.status_message.emit(f"Audio error: {str(e)}")
            self.audio_active = False
    
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not self.screen_active:
            try:
                self.screen_streamer = ScreenStreamer(
                    self.server_ip, SCREEN_SHARE_PORT
                )
                threading.Thread(
                    target=self._run_screen_streamer, daemon=True
                ).start()
                self.screen_active = True
                self.add_system_message("Screen sharing started")
            except Exception as e:
                self.add_system_message(f"Screen share error: {str(e)}")
                self.btn_share.setChecked(False)
                self.screen_active = False
        else:
            if self.screen_streamer:
                try:
                    self.screen_streamer.running = False
                    self.screen_streamer.stop_streaming()
                except Exception as e:
                    print(f"Error stopping screen share: {e}")
            self.screen_streamer = None
            self.screen_active = False
            self.add_system_message("Screen sharing stopped")
    
    def _run_screen_streamer(self):
        """Run screen streamer in background thread"""
        try:
            if self.screen_streamer:
                self.screen_streamer.start_streaming()
        except Exception as e:
            self.gui_signals.status_message.emit(f"Screen share error: {str(e)}")
            self.screen_active = False
    
    def toggle_chat_panel(self):
        """Toggle chat panel visibility"""
        self.chat_visible = not self.chat_visible
        self.chat_panel.setVisible(self.chat_visible)
        self.btn_chat_toggle.setChecked(self.chat_visible)
    
    def show_more_options(self):
        """Display more options dialog"""
        menu = QMessageBox(self)
        menu.setWindowTitle("More Options")
        menu.setText("Choose an option:")
        
        btn_settings = menu.addButton("⚙️ Settings", QMessageBox.ActionRole)
        btn_files = menu.addButton("📁 Upload File", QMessageBox.ActionRole)
        btn_download = menu.addButton("📥 Download File", QMessageBox.ActionRole)
        btn_cancel = menu.addButton("Cancel", QMessageBox.RejectRole)
        
        menu.exec_()
        
        clicked = menu.clickedButton()
        if clicked == btn_files:
            self.upload_file()
        elif clicked == btn_download:
            self.download_file()
        elif clicked == btn_settings:
            self.add_system_message("Settings coming soon")
    
    def upload_file(self):
        """Upload file to server - FIXED with proper acknowledgment"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload File", "", "All Files (*.*)"
        )
        if not file_path:
            return
        
        filename = Path(file_path).name
        self.add_system_message(f"Uploading {filename}...")
        
        def upload_thread():
            try:
                file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                if not file_client.connect():
                    self.gui_signals.status_message.emit("Failed to connect to file server")
                    return
                
                success = file_client.upload_file(file_path, verify_checksum=True)
                file_client.disconnect()
                
                if success:
                    self.gui_signals.status_message.emit(f"✓ Uploaded {filename}")
                else:
                    self.gui_signals.status_message.emit(f"Upload failed: {filename}")
            except Exception as e:
                self.gui_signals.status_message.emit(f"Upload error: {str(e)}")
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def download_file(self):
        """Download file from server - FIXED"""
        filename, ok = QInputDialog.getText(
            self, "Download File", "Enter filename:"
        )
        if not ok or not filename.strip():
            return
        
        filename = filename.strip()
        save_dir = QFileDialog.getExistingDirectory(self, "Save to Directory")
        if not save_dir:
            return
        
        self.add_system_message(f"Downloading {filename}...")
        
        def download_thread():
            try:
                file_client = FileTransferClient(self.server_ip, FILE_TRANSFER_PORT)
                if not file_client.connect():
                    self.gui_signals.status_message.emit("Failed to connect to file server")
                    return
                
                success = file_client.download_file(filename, save_dir, verify_checksum=True)
                file_client.disconnect()
                
                if success:
                    self.gui_signals.status_message.emit(f"✓ Downloaded {filename}")
                else:
                    self.gui_signals.status_message.emit(f"Download failed: {filename}")
            except Exception as e:
                self.gui_signals.status_message.emit(f"Download error: {str(e)}")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def leave_meeting(self):
        """Leave the meeting with confirmation"""
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
        """Update UI elements periodically (timer callback)"""
        try:
            elapsed = datetime.now() - self.meeting_start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.meeting_time.setText(f"{minutes:02d}:{seconds:02d}")
        except (RuntimeError, AttributeError):
            self.update_timer.stop()
    
    def cleanup(self):
        """Cleanup all resources and connections - FIXED"""
        print("Cleaning up resources...")
        
        # Stop timers
        try:
            self.update_timer.stop()
            self.video_timer.stop()
        except:
            pass
        
        # Set all flags to False
        self.video_active = False
        self.audio_active = False
        self.screen_active = False
        
        # Clean up video
        if self.video_capture:
            try:
                self.video_capture.release()
            except Exception as e:
                print(f"Error releasing camera: {e}")
        
        if self.video_send_socket:
            try:
                self.video_send_socket.close()
            except Exception as e:
                print(f"Error closing video send socket: {e}")
        
        if self.video_receive_socket:
            try:
                self.video_receive_socket.close()
            except Exception as e:
                print(f"Error closing video receive socket: {e}")
        
        # Clean up audio - gracefully stop first
        if self.audio_streamer:
            try:
                self.audio_streamer.running = False
                import time
                time.sleep(0.1)  # Give it time to stop
                self.audio_streamer.stop_streaming()
            except Exception as e:
                print(f"Error stopping audio: {e}")
        
        # Clean up screen share
        if self.screen_streamer:
            try:
                self.screen_streamer.running = False
                self.screen_streamer.stop_streaming()
            except Exception as e:
                print(f"Error stopping screen share: {e}")
        
        # Clean up chat
        if self.chat_client:
            try:
                self.chat_client.disconnect()
            except Exception as e:
                print(f"Error disconnecting chat: {e}")
        
        print("Cleanup complete")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.cleanup()
        event.accept()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
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
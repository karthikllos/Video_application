"""
Audio streaming module - FIXED VERSION
Properly closes PyAudio streams to prevent crashes
"""

import pyaudio
import socket
import sys
import os
import threading
import time
import struct

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, AUDIO_PORT, AUDIO_BUFFER_SIZE,
    AUDIO_RATE, AUDIO_CHANNELS, AUDIO_CHUNK, AUDIO_FORMAT
)
from shared.protocol import AUDIO
from shared.helpers import pack_message


class AudioStreamer:
    """Handles microphone capture and transmission - FIXED"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=AUDIO_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, AUDIO_BUFFER_SIZE)
        self.running = False
        self.audio = None
        self.stream = None
        
        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = AUDIO_CHANNELS
        self.rate = AUDIO_RATE
        self.chunk = AUDIO_CHUNK
        
    def start_streaming(self):
        """Capture microphone audio and stream it to server"""
        self.audio = pyaudio.PyAudio()
        
        try:
            # Open microphone stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print(f"\n🎤 Starting audio stream to {self.server_ip}:{self.server_port}")
            print(f"📊 Format: {AUDIO_FORMAT}-bit PCM, {self.rate}Hz, {self.channels} channel(s)")
            print(f"📦 Chunk size: {self.chunk} frames")
            
            self.running = True
            packet_count = 0
            
            while self.running:
                try:
                    # Read audio data from microphone
                    audio_data = self.stream.read(self.chunk, exception_on_overflow=False)
                    
                    # Pack message with protocol header
                    packet = pack_message(AUDIO, audio_data)
                    
                    # Send via UDP
                    self.sock.sendto(packet, (self.server_ip, self.server_port))
                    
                    packet_count += 1
                        
                except OSError as e:
                    print(f"⚠️  Audio buffer overflow: {e}")
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Audio error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
        finally:
            self.stop_streaming()
    
    def stop_streaming(self):
        """Clean up resources - FIXED ORDER"""
        self.running = False
        
        # CRITICAL: Stop stream BEFORE closing/terminating
        if self.stream:
            try:
                self.stream.stop_stream()
            except Exception as e:
                print(f"⚠️  Error stopping stream: {e}")
            
            try:
                self.stream.close()
            except Exception as e:
                print(f"⚠️  Error closing stream: {e}")
            
            self.stream = None
        
        # Terminate PyAudio AFTER all streams are closed
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                print(f"⚠️  Error terminating PyAudio: {e}")
            
            self.audio = None
        
        # Close socket
        try:
            self.sock.close()
        except:
            pass
        
        print("\n🛑 Audio streaming stopped")


class AudioReceiver:
    """Handles receiving and playing audio streams - FIXED"""
    
    def __init__(self, listen_port=AUDIO_PORT):
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, AUDIO_BUFFER_SIZE)
        self.running = False
        self.audio = None
        self.stream = None
        
        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = AUDIO_CHANNELS
        self.rate = AUDIO_RATE
        self.chunk = AUDIO_CHUNK
        
    def start_receiving(self):
        """Receive and play audio streams"""
        self.audio = pyaudio.PyAudio()
        
        try:
            # Bind socket
            self.sock.bind(('0.0.0.0', self.listen_port))
            self.sock.settimeout(0.1)
            
            # Open audio output stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk
            )
            
            print(f"\n🔊 Listening for audio on port {self.listen_port}")
            
            self.running = True
            packet_count = 0
            
            while self.running:
                try:
                    # Receive packet
                    data, addr = self.sock.recvfrom(AUDIO_BUFFER_SIZE)
                    
                    # Unpack message
                    audio_data = self._extract_audio_data(data)
                    
                    if audio_data:
                        # Play audio
                        self.stream.write(audio_data)
                        packet_count += 1
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Audio receive error: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error starting audio receiver: {e}")
        finally:
            self.stop_receiving()
    
    def _extract_audio_data(self, data):
        """Extract audio data from protocol packet"""
        try:
            from shared.helpers import unpack_message
            version, msg_type, payload_length, seq_num, payload = unpack_message(data)
            return payload
        except Exception:
            return None
    
    def stop_receiving(self):
        """Clean up resources - FIXED ORDER"""
        self.running = False
        
        # CRITICAL: Stop stream BEFORE closing/terminating
        if self.stream:
            try:
                self.stream.stop_stream()
            except Exception as e:
                print(f"⚠️  Error stopping stream: {e}")
            
            try:
                self.stream.close()
            except Exception as e:
                print(f"⚠️  Error closing stream: {e}")
            
            self.stream = None
        
        # Terminate PyAudio AFTER all streams are closed
        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                print(f"⚠️  Error terminating PyAudio: {e}")
            
            self.audio = None
        
        # Close socket
        try:
            self.sock.close()
        except:
            pass
        
        print("\n🛑 Audio receiving stopped")
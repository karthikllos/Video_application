"""
Audio streaming module for LAN Collaboration App
Handles microphone capture, transmission, and playback of audio streams
"""

import pyaudio
import socket
import sys
import os
import threading
import time
import struct

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, AUDIO_PORT, AUDIO_BUFFER_SIZE,
    AUDIO_RATE, AUDIO_CHANNELS, AUDIO_CHUNK, AUDIO_FORMAT
)
from shared.protocol import AUDIO
from shared.helpers import pack_message


class AudioStreamer:
    """Handles microphone capture and transmission"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=AUDIO_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, AUDIO_BUFFER_SIZE)
        self.running = False
        self.audio = None
        self.stream = None
        
        # Audio parameters
        self.format = pyaudio.paInt16  # 16-bit PCM
        self.channels = AUDIO_CHANNELS
        self.rate = AUDIO_RATE
        self.chunk = AUDIO_CHUNK
        
    def start_streaming(self):
        """Capture microphone audio and stream it to server"""
        self.audio = pyaudio.PyAudio()
        
        # List available input devices
        self._list_audio_devices()
        
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
            print("Press Ctrl+C to stop\n")
            
            self.running = True
            packet_count = 0
            start_time = time.time()
            total_bytes = 0
            
            while self.running:
                try:
                    # Read audio data from microphone
                    audio_data = self.stream.read(self.chunk, exception_on_overflow=False)
                    
                    # Pack message with protocol header
                    packet = pack_message(AUDIO, audio_data)
                    
                    # Send via UDP
                    self.sock.sendto(packet, (self.server_ip, self.server_port))
                    
                    # Statistics
                    packet_count += 1
                    total_bytes += len(packet)
                    
                    # Print stats every 100 packets (~2.3 seconds at 44100Hz)
                    if packet_count % 100 == 0:
                        elapsed = time.time() - start_time
                        packets_per_sec = packet_count / elapsed
                        kbps = (total_bytes * 8) / (elapsed * 1000)
                        print(f"📡 Sent {packet_count} packets | "
                              f"{packets_per_sec:.1f} pkt/s | "
                              f"{kbps:.1f} kbps | "
                              f"Packet size: {len(packet)} bytes")
                        
                except OSError as e:
                    print(f"⚠️  Audio buffer overflow: {e}")
                    continue
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
        finally:
            self.stop_streaming()
    
    def _list_audio_devices(self):
        """List available audio input devices"""
        print("\n🔊 Available Audio Devices:")
        print("=" * 50)
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                print(f"  [{i}] {device_info.get('name')}")
        print("=" * 50)
    
    def stop_streaming(self):
        """Clean up resources"""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        self.sock.close()
        print("\n🛑 Audio streaming stopped")


class AudioReceiver:
    """Handles receiving and playing audio streams"""
    
    def __init__(self, listen_port=AUDIO_PORT):
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, AUDIO_BUFFER_SIZE)
        self.running = False
        self.audio = None
        self.stream = None
        
        # Audio parameters
        self.format = pyaudio.paInt16  # 16-bit PCM
        self.channels = AUDIO_CHANNELS
        self.rate = AUDIO_RATE
        self.chunk = AUDIO_CHUNK
        
    def start_receiving(self):
        """Receive and play audio streams"""
        self.audio = pyaudio.PyAudio()
        
        # List available output devices
        self._list_audio_devices()
        
        try:
            # Bind socket
            self.sock.bind(('0.0.0.0', self.listen_port))
            self.sock.settimeout(0.1)  # Non-blocking with timeout
            
            # Open audio output stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk
            )
            
            print(f"\n🔊 Listening for audio on port {self.listen_port}")
            print(f"📊 Format: {AUDIO_FORMAT}-bit PCM, {self.rate}Hz, {self.channels} channel(s)")
            print(f"📦 Chunk size: {self.chunk} frames")
            print("Press Ctrl+C to stop\n")
            
            self.running = True
            packet_count = 0
            start_time = time.time()
            last_sender = None
            
            while self.running:
                try:
                    # Receive packet
                    data, addr = self.sock.recvfrom(AUDIO_BUFFER_SIZE)
                    
                    # Track sender
                    if last_sender != addr[0]:
                        last_sender = addr[0]
                        print(f"\n🎧 Receiving audio from {addr[0]}:{addr[1]}")
                    
                    # Unpack message
                    audio_data = self._extract_audio_data(data)
                    
                    if audio_data:
                        # Play audio
                        self.stream.write(audio_data)
                        
                        # Statistics
                        packet_count += 1
                        
                        # Print stats every 100 packets
                        if packet_count % 100 == 0:
                            elapsed = time.time() - start_time
                            packets_per_sec = packet_count / elapsed
                            print(f"🎵 Received {packet_count} packets | "
                                  f"{packets_per_sec:.1f} pkt/s | "
                                  f"Audio data: {len(audio_data)} bytes")
                        
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    # print(f"⚠️  Error receiving audio: {e}")
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
        except Exception as e:
            # print(f"Error unpacking audio: {e}")
            return None
    
    def _list_audio_devices(self):
        """List available audio output devices"""
        print("\n🔊 Available Audio Devices:")
        print("=" * 50)
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        for i in range(num_devices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxOutputChannels') > 0:
                print(f"  [{i}] {device_info.get('name')}")
        print("=" * 50)
    
    def stop_receiving(self):
        """Clean up resources"""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        self.sock.close()
        print("\n🛑 Audio receiving stopped")


def main():
    """Main function for testing audio streaming"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LAN Audio Streaming')
    parser.add_argument('mode', choices=['send', 'receive'], 
                       help='Mode: send (stream microphone) or receive (play audio)')
    parser.add_argument('--ip', default='127.0.0.1', 
                       help='Server IP address (for sender mode)')
    parser.add_argument('--port', type=int, default=AUDIO_PORT,
                       help=f'Port number (default: {AUDIO_PORT})')
    
    args = parser.parse_args()
    
    if args.mode == 'send':
        streamer = AudioStreamer(server_ip=args.ip, server_port=args.port)
        streamer.start_streaming()
    elif args.mode == 'receive':
        receiver = AudioReceiver(listen_port=args.port)
        receiver.start_receiving()


if __name__ == '__main__':
    main()
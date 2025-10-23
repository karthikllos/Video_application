"""
Audio Conference Server
Receives audio from multiple clients, mixes them, and broadcasts back
Uses UDP for real-time audio transmission
"""

import socket
import threading
import sys
import os
import time
import numpy as np
from collections import deque

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import AUDIO_PORT, AUDIO_BUFFER_SIZE, AUDIO_CHUNK
from shared.protocol import AUDIO
from shared.helpers import unpack_message, pack_message


class AudioConferenceServer:
    """Multi-user audio conferencing server with mixing"""
    
    def __init__(self, port=AUDIO_PORT):
        self.port = port
        self.sock = None
        self.running = False
        
        # Audio buffers for each client: {addr: deque of audio chunks}
        self.audio_buffers = {}
        self.buffers_lock = threading.Lock()
        
        # Client tracking
        self.clients = {}  # {addr: last_seen_time}
        self.clients_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'mixed_packets': 0
        }
        
        # Mixing parameters
        self.mix_interval = 0.02  # 20ms mixing interval
    
    def start(self):
        """Start the audio conference server"""
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, AUDIO_BUFFER_SIZE)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.settimeout(0.1)
            
            self.running = True
            
            print(f"🎵 Audio Conference Server listening on UDP port {self.port}")
            
            # Start mixer thread
            mixer_thread = threading.Thread(target=self._audio_mixer, daemon=True)
            mixer_thread.start()
            
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_stale_clients, daemon=True)
            cleanup_thread.start()
            
            # Main receiver loop
            while self.running:
                try:
                    # Receive audio packet
                    data, sender_addr = self.sock.recvfrom(AUDIO_BUFFER_SIZE)
                    
                    # Update client tracking
                    with self.clients_lock:
                        self.clients[sender_addr] = time.time()
                    
                    # Extract audio data
                    try:
                        version, msg_type, payload_length, seq_num, audio_data = unpack_message(data)
                        
                        # Add to client's buffer
                        with self.buffers_lock:
                            if sender_addr not in self.audio_buffers:
                                self.audio_buffers[sender_addr] = deque(maxlen=10)
                            self.audio_buffers[sender_addr].append(audio_data)
                        
                        # Update stats
                        self.stats['total_packets'] += 1
                        self.stats['total_bytes'] += len(data)
                        
                    except Exception as e:
                        continue
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Audio receive error: {e}")
                        
        except Exception as e:
            print(f"❌ Audio server error: {e}")
        finally:
            self.stop()
    
    def _audio_mixer(self):
        """Mix audio from all clients and broadcast"""
        print("🎛️  Audio mixer started")
        
        while self.running:
            try:
                time.sleep(self.mix_interval)
                
                with self.buffers_lock:
                    if len(self.audio_buffers) < 2:
                        continue  # Need at least 2 clients to mix
                    
                    # Collect audio chunks from all clients
                    chunks_to_mix = []
                    clients_to_send = []
                    
                    for addr, buffer in self.audio_buffers.items():
                        if buffer:
                            chunk = buffer.popleft()
                            chunks_to_mix.append((addr, chunk))
                            clients_to_send.append(addr)
                    
                    if len(chunks_to_mix) < 2:
                        continue
                
                # Mix audio for each client (excluding their own audio)
                for target_addr in clients_to_send:
                    mixed_audio = self._mix_audio_for_client(chunks_to_mix, target_addr)
                    
                    if mixed_audio:
                        # Pack and send
                        packet = pack_message(AUDIO, mixed_audio)
                        try:
                            self.sock.sendto(packet, target_addr)
                            self.stats['mixed_packets'] += 1
                        except Exception as e:
                            pass
                
                # Log stats periodically
                if self.stats['mixed_packets'] % 500 == 0 and self.stats['mixed_packets'] > 0:
                    self._log_stats()
                    
            except Exception as e:
                if self.running:
                    print(f"⚠️  Mixer error: {e}")
    
    def _mix_audio_for_client(self, chunks_to_mix, target_addr):
        """Mix audio from all clients except target"""
        try:
            # Convert all chunks to numpy arrays
            arrays = []
            for addr, chunk in chunks_to_mix:
                if addr == target_addr:
                    continue  # Don't include client's own audio
                
                arr = np.frombuffer(chunk, dtype=np.int16)
                arrays.append(arr)
            
            if not arrays:
                return None
            
            # Ensure all arrays are same length (pad if needed)
            max_len = max(len(arr) for arr in arrays)
            padded = []
            for arr in arrays:
                if len(arr) < max_len:
                    padded_arr = np.pad(arr, (0, max_len - len(arr)), mode='constant')
                    padded.append(padded_arr)
                else:
                    padded.append(arr)
            
            # Mix: average all audio streams
            mixed = np.mean(padded, axis=0).astype(np.int16)
            
            return mixed.tobytes()
            
        except Exception as e:
            print(f"⚠️  Mix error: {e}")
            return None
    
    def _cleanup_stale_clients(self):
        """Remove clients that haven't sent data recently"""
        TIMEOUT = 30  # 30 seconds
        
        while self.running:
            time.sleep(10)
            
            current_time = time.time()
            with self.clients_lock:
                stale = [
                    addr for addr, last_seen in self.clients.items()
                    if current_time - last_seen > TIMEOUT
                ]
            
            if stale:
                with self.buffers_lock:
                    for addr in stale:
                        if addr in self.clients:
                            del self.clients[addr]
                        if addr in self.audio_buffers:
                            del self.audio_buffers[addr]
                        print(f"🔌 Audio client {addr[0]}:{addr[1]} timed out")
    
    def _log_stats(self):
        """Log server statistics"""
        with self.clients_lock:
            active = len(self.clients)
        
        mbytes = self.stats['total_bytes'] / (1024 * 1024)
        print(f"📊 Audio: {self.stats['total_packets']} recv | "
              f"{self.stats['mixed_packets']} mixed | "
              f"{mbytes:.2f} MB | "
              f"{active} active clients")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.sock:
            self.sock.close()
        print("🛑 Audio server stopped")
    
    def get_stats(self):
        """Get server statistics"""
        with self.clients_lock:
            return {
                'active_clients': len(self.clients),
                'total_packets': self.stats['total_packets'],
                'mixed_packets': self.stats['mixed_packets'],
                'total_bytes': self.stats['total_bytes']
            }


if __name__ == '__main__':
    server = AudioConferenceServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n")
        server.stop()
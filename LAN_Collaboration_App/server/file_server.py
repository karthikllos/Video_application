"""
File Transfer Server
Handles file uploads/downloads with metadata and checksum verification
Uses TCP for reliable file transfer
"""

import socket
import threading
import sys
import os
import time
import hashlib
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    FILE_TRANSFER_PORT, FILE_CHUNK_SIZE, 
    MAX_FILE_SIZE, BUFFER_SIZE
)
from shared.protocol import FILE_UPLOAD, FILE_DOWNLOAD, FILE_METADATA, FILE_CHUNK
from shared.helpers import (
    pack_message, unpack_message,
    pack_file_metadata, unpack_file_metadata
)


class FileTransferServer:
    """Multi-user file transfer server"""
    
    def __init__(self, port=FILE_TRANSFER_PORT, storage_dir='server_files'):
        self.port = port
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.server_socket = None
        self.running = False
        
        # Statistics
        self.stats = {
            'files_uploaded': 0,
            'files_downloaded': 0,
            'bytes_uploaded': 0,
            'bytes_downloaded': 0,
            'active_transfers': 0
        }
        self.stats_lock = threading.Lock()
    
    def start(self):
        """Start the file transfer server"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            
            print(f"📁 File Transfer Server listening on TCP port {self.port}")
            print(f"💾 Storage directory: {self.storage_dir.absolute()}")
            
            # Accept connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    print(f"✓ File transfer connection from {address[0]}:{address[1]}")
                    
                    # Handle in new thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ File server error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket, address):
        """Handle file transfer client"""
        try:
            with self.stats_lock:
                self.stats['active_transfers'] += 1
            
            # Receive first message to determine operation
            header = self._recv_exact(client_socket, 12)
            if not header:
                return
            
            # Parse message type
            import struct
            msg_type = struct.unpack('!B', header[1:2])[0]
            
            if msg_type == FILE_METADATA:
                # This is an upload
                self._handle_upload(client_socket, address, header)
            elif msg_type == FILE_DOWNLOAD:
                # This is a download request
                self._handle_download(client_socket, address, header)
            else:
                print(f"⚠️  Unknown message type from {address[0]}")
                
        except Exception as e:
            print(f"⚠️  Error handling client {address[0]}: {e}")
        finally:
            with self.stats_lock:
                self.stats['active_transfers'] -= 1
            client_socket.close()
    
    def _handle_upload(self, client_socket, address, header):
        """Handle file upload"""
        try:
            # Receive metadata payload
            import struct
            payload_length = struct.unpack('!I', header[2:6])[0]
            metadata_payload = self._recv_exact(client_socket, payload_length)
            
            if not metadata_payload:
                print(f"❌ Failed to receive metadata from {address[0]}")
                return
            
            # Parse metadata
            metadata = unpack_file_metadata(metadata_payload)
            filename = metadata['filename']
            filesize = metadata['filesize']
            checksum = metadata['checksum']
            
            print(f"📤 Upload started: {filename} ({filesize:,} bytes) from {address[0]}")
            
            if filesize > MAX_FILE_SIZE:
                print(f"❌ File too large: {filesize} > {MAX_FILE_SIZE}")
                return
            
            # Receive file data
            file_path = self.storage_dir / filename
            bytes_received = 0
            
            with open(file_path, 'wb') as f:
                while bytes_received < filesize:
                    # Receive chunk message
                    chunk_header = self._recv_exact(client_socket, 12)
                    if not chunk_header:
                        break
                    
                    chunk_length = struct.unpack('!I', chunk_header[2:6])[0]
                    chunk_data = self._recv_exact(client_socket, chunk_length)
                    
                    if not chunk_data:
                        break
                    
                    # Extract payload from message
                    _, _, _, _, payload = unpack_message(chunk_header + chunk_data)
                    
                    # Write to file
                    f.write(payload)
                    bytes_received += len(payload)
            
            # Verify checksum if provided
            if checksum:
                actual_checksum = self._calculate_md5(file_path)
                if actual_checksum != checksum:
                    print(f"⚠️  Checksum mismatch for {filename}")
                    os.remove(file_path)
                    return
            
            # Send acknowledgment
            client_socket.send(b"OK")
            
            with self.stats_lock:
                self.stats['files_uploaded'] += 1
                self.stats['bytes_uploaded'] += bytes_received
            
            print(f"✅ Upload complete: {filename} ({bytes_received:,} bytes)")
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
    
    def _handle_download(self, client_socket, address, header):
        """Handle file download"""
        try:
            # Receive filename request
            import struct
            payload_length = struct.unpack('!I', header[2:6])[0]
            filename_bytes = self._recv_exact(client_socket, payload_length)
            
            if not filename_bytes:
                return
            
            filename = filename_bytes.decode('utf-8')
            file_path = self.storage_dir / filename
            
            print(f"📥 Download requested: {filename} by {address[0]}")
            
            if not file_path.exists():
                print(f"❌ File not found: {filename}")
                return
            
            # Get file info
            filesize = file_path.stat().st_size
            checksum = self._calculate_md5(file_path)
            
            # Send metadata
            metadata = pack_file_metadata(filename, filesize, checksum)
            metadata_packet = pack_message(FILE_METADATA, metadata)
            client_socket.sendall(metadata_packet)
            
            # Send file data
            bytes_sent = 0
            with open(file_path, 'rb') as f:
                while bytes_sent < filesize:
                    chunk = f.read(FILE_CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # Pack and send chunk
                    chunk_packet = pack_message(FILE_CHUNK, chunk)
                    client_socket.sendall(chunk_packet)
                    
                    bytes_sent += len(chunk)
            
            with self.stats_lock:
                self.stats['files_downloaded'] += 1
                self.stats['bytes_downloaded'] += bytes_sent
            
            print(f"✅ Download complete: {filename} ({bytes_sent:,} bytes)")
            
        except Exception as e:
            print(f"❌ Download error: {e}")
    
    def _recv_exact(self, sock, num_bytes):
        """Receive exactly num_bytes"""
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(min(num_bytes - len(data), BUFFER_SIZE))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _calculate_md5(self, file_path):
        """Calculate MD5 checksum"""
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(FILE_CHUNK_SIZE), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 File server stopped")
    
    def get_stats(self):
        """Get server statistics"""
        with self.stats_lock:
            return dict(self.stats)


if __name__ == '__main__':
    server = FileTransferServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n")
        server.stop()
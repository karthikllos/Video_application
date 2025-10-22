"""
File transfer module for LAN Collaboration App
Handles file upload/download with progress tracking and checksum verification
"""

import socket
import os
import sys
import hashlib
import struct
import time
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, FILE_TRANSFER_PORT, FILE_CHUNK_SIZE,
    MAX_FILE_SIZE, CONNECTION_TIMEOUT
)
from shared.protocol import FILE_UPLOAD, FILE_DOWNLOAD, FILE_METADATA, FILE_CHUNK
from shared.helpers import (
    pack_message, unpack_message,
    pack_file_metadata, unpack_file_metadata
)


class FileTransferClient:
    """Handles file upload and download operations"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=FILE_TRANSFER_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        
    def connect(self):
        """Connect to file transfer server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(CONNECTION_TIMEOUT)
            self.sock.connect((self.server_ip, self.server_port))
            print(f"✓ Connected to file transfer server at {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def upload_file(self, file_path, verify_checksum=True):
        """Upload a file to the server
        
        Args:
            file_path (str): Path to file to upload
            verify_checksum (bool): Whether to verify MD5 checksum
            
        Returns:
            bool: True if successful
        """
        file_path = Path(file_path)
        
        # Validate file
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        if not file_path.is_file():
            print(f"❌ Not a file: {file_path}")
            return False
        
        file_size = file_path.stat().st_size
        
        if file_size > MAX_FILE_SIZE:
            print(f"❌ File too large: {file_size} bytes (max {MAX_FILE_SIZE})")
            return False
        
        if file_size == 0:
            print("❌ File is empty")
            return False
        
        print(f"\n📤 Uploading: {file_path.name}")
        print(f"📊 Size: {self._format_size(file_size)}")
        
        # Calculate checksum if requested
        checksum = ""
        if verify_checksum:
            print("🔒 Calculating checksum...")
            checksum = self._calculate_md5(file_path)
            print(f"🔑 MD5: {checksum}")
        
        # Connect if not connected
        if not self.sock:
            if not self.connect():
                return False
        
        try:
            # Send metadata
            print("\n📦 Sending metadata...")
            metadata = pack_file_metadata(file_path.name, file_size, checksum)
            metadata_packet = pack_message(FILE_METADATA, metadata)
            self.sock.sendall(metadata_packet)
            
            # Send file data in chunks
            print("📡 Sending file data...")
            bytes_sent = 0
            
            with open(file_path, 'rb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, 
                         desc="Uploading", ncols=80) as pbar:
                    while bytes_sent < file_size:
                        # Read chunk
                        chunk_size = min(FILE_CHUNK_SIZE, file_size - bytes_sent)
                        chunk = f.read(chunk_size)
                        
                        if not chunk:
                            break
                        
                        # Pack and send chunk
                        chunk_packet = pack_message(FILE_CHUNK, chunk)
                        self.sock.sendall(chunk_packet)
                        
                        bytes_sent += len(chunk)
                        pbar.update(len(chunk))
            
            # Wait for acknowledgment
            print("\n⏳ Waiting for server acknowledgment...")
            response = self._receive_response()
            
            if response:
                print(f"✓ Upload successful!")
                print(f"📊 Total sent: {self._format_size(bytes_sent)}")
                return True
            else:
                print("❌ Upload failed - no acknowledgment")
                return False
                
        except Exception as e:
            print(f"\n❌ Upload error: {e}")
            return False
    
    def download_file(self, file_name, save_path=".", verify_checksum=True):
        """Download a file from the server
        
        Args:
            file_name (str): Name of file to download
            save_path (str): Directory to save file
            verify_checksum (bool): Whether to verify MD5 checksum
            
        Returns:
            bool: True if successful
        """
        print(f"\n📥 Requesting download: {file_name}")
        
        # Connect if not connected
        if not self.sock:
            if not self.connect():
                return False
        
        try:
            # Send download request
            request = file_name.encode('utf-8')
            request_packet = pack_message(FILE_DOWNLOAD, request)
            self.sock.sendall(request_packet)
            
            # Receive metadata
            print("⏳ Waiting for metadata...")
            metadata_data = self._receive_message()
            
            if not metadata_data:
                print("❌ Failed to receive metadata")
                return False
            
            # Unpack metadata
            version, msg_type, payload_length, seq_num, payload = unpack_message(metadata_data)
            
            if msg_type != FILE_METADATA:
                print(f"❌ Unexpected message type: {msg_type}")
                return False
            
            metadata = unpack_file_metadata(payload)
            file_size = metadata['filesize']
            original_checksum = metadata['checksum']
            
            print(f"📊 Size: {self._format_size(file_size)}")
            if original_checksum:
                print(f"🔑 MD5: {original_checksum}")
            
            # Prepare save path
            save_path = Path(save_path)
            save_path.mkdir(parents=True, exist_ok=True)
            output_file = save_path / file_name
            
            # Receive file data
            print(f"\n📥 Downloading to: {output_file}")
            bytes_received = 0
            
            with open(output_file, 'wb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True,
                         desc="Downloading", ncols=80) as pbar:
                    while bytes_received < file_size:
                        # Receive chunk
                        chunk_data = self._receive_message()
                        
                        if not chunk_data:
                            print("\n❌ Connection lost")
                            return False
                        
                        # Unpack chunk
                        version, msg_type, payload_length, seq_num, chunk = unpack_message(chunk_data)
                        
                        if msg_type != FILE_CHUNK:
                            print(f"\n❌ Unexpected message type: {msg_type}")
                            return False
                        
                        # Write chunk
                        f.write(chunk)
                        bytes_received += len(chunk)
                        pbar.update(len(chunk))
            
            print(f"\n✓ Download complete!")
            print(f"📊 Total received: {self._format_size(bytes_received)}")
            
            # Verify checksum if requested
            if verify_checksum and original_checksum:
                print("\n🔒 Verifying checksum...")
                downloaded_checksum = self._calculate_md5(output_file)
                
                if downloaded_checksum == original_checksum:
                    print("✓ Checksum verified!")
                else:
                    print("❌ Checksum mismatch!")
                    print(f"  Expected: {original_checksum}")
                    print(f"  Got:      {downloaded_checksum}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"\n❌ Download error: {e}")
            return False
    
    def _receive_message(self):
        """Receive a complete message from server"""
        try:
            # Receive header (12 bytes)
            header = self._recv_exact(12)
            if not header:
                return None
            
            # Parse payload length
            payload_length = struct.unpack('!I', header[2:6])[0]
            
            # Receive payload
            payload = self._recv_exact(payload_length)
            if not payload:
                return None
            
            return header + payload
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def _recv_exact(self, num_bytes):
        """Receive exactly num_bytes from socket"""
        data = b''
        while len(data) < num_bytes:
            chunk = self.sock.recv(min(num_bytes - len(data), FILE_CHUNK_SIZE))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _receive_response(self, timeout=5.0):
        """Receive acknowledgment response"""
        try:
            self.sock.settimeout(timeout)
            data = self.sock.recv(1024)
            return len(data) > 0
        except socket.timeout:
            return False
        except Exception as e:
            print(f"Error receiving response: {e}")
            return False
    
    def _calculate_md5(self, file_path):
        """Calculate MD5 checksum of file"""
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(FILE_CHUNK_SIZE), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def _format_size(self, size_bytes):
        """Format byte size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


def upload_file(file_path, server_ip=SERVER_IP, server_port=FILE_TRANSFER_PORT, verify_checksum=True):
    """Helper function to upload a file
    
    Args:
        file_path (str): Path to file to upload
        server_ip (str): Server IP address
        server_port (int): Server port
        verify_checksum (bool): Whether to verify MD5 checksum
        
    Returns:
        bool: True if successful
    """
    client = FileTransferClient(server_ip, server_port)
    success = client.upload_file(file_path, verify_checksum)
    client.disconnect()
    return success


def download_file(file_name, save_path=".", server_ip=SERVER_IP, 
                 server_port=FILE_TRANSFER_PORT, verify_checksum=True):
    """Helper function to download a file
    
    Args:
        file_name (str): Name of file to download
        save_path (str): Directory to save file
        server_ip (str): Server IP address
        server_port (int): Server port
        verify_checksum (bool): Whether to verify MD5 checksum
        
    Returns:
        bool: True if successful
    """
    client = FileTransferClient(server_ip, server_port)
    success = client.download_file(file_name, save_path, verify_checksum)
    client.disconnect()
    return success


def main():
    """Main function for testing file transfer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LAN File Transfer')
    parser.add_argument('mode', choices=['upload', 'download'],
                       help='Mode: upload or download')
    parser.add_argument('file', help='File path (upload) or file name (download)')
    parser.add_argument('--ip', default='127.0.0.1',
                       help='Server IP address')
    parser.add_argument('--port', type=int, default=FILE_TRANSFER_PORT,
                       help=f'Server port (default: {FILE_TRANSFER_PORT})')
    parser.add_argument('--output', '-o', default='.',
                       help='Output directory for downloads (default: current dir)')
    parser.add_argument('--no-checksum', action='store_true',
                       help='Disable checksum verification')
    
    args = parser.parse_args()
    
    verify = not args.no_checksum
    
    if args.mode == 'upload':
        success = upload_file(args.file, args.ip, args.port, verify)
    else:
        success = download_file(args.file, args.output, args.ip, args.port, verify)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
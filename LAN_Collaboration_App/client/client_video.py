"""
Video streaming module for LAN Collaboration App
Handles webcam capture, compression, transmission, and receiving of video frames
"""

import cv2
import socket
import numpy as np
import sys
import os
import threading
import time

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.constants import (
    SERVER_IP, VIDEO_PORT, VIDEO_BUFFER_SIZE,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, VIDEO_QUALITY
)
from shared.protocol import VIDEO
from shared.helpers import pack_message


class VideoStreamer:
    """Handles video capture and transmission"""
    
    def __init__(self, server_ip=SERVER_IP, server_port=VIDEO_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, VIDEO_BUFFER_SIZE)
        self.running = False
        self.cap = None
        
    def start_streaming(self):
        """Capture webcam frames and stream them to server"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
        
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        print(f"Starting video stream to {self.server_ip}:{self.server_port}")
        print("Press 'q' to quit")
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # Compress frame to JPEG
                compressed_frame = self.compress_frame(frame)
                
                # Pack message with protocol header
                packet = pack_message(VIDEO, compressed_frame)
                
                # Send via UDP
                try:
                    self.sock.sendto(packet, (self.server_ip, self.server_port))
                except Exception as e:
                    print(f"Error sending frame: {e}")
                
                # Display local preview
                cv2.imshow('Video Stream - Sending', frame)
                
                # Calculate and display FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Streaming at {fps:.2f} FPS | Packet size: {len(packet)} bytes")
                
                # Control frame rate
                if cv2.waitKey(int(1000/VIDEO_FPS)) & 0xFF == ord('q'):
                    break
                    
        finally:
            self.stop_streaming()
    
    def compress_frame(self, frame):
        """Compress frame to JPEG bytes"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), VIDEO_QUALITY]
        result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
        
        if not result:
            raise Exception("Failed to encode frame")
        
        return encoded_frame.tobytes()
    
    def stop_streaming(self):
        """Clean up resources"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.sock.close()
        print("Video streaming stopped")


class VideoReceiver:
    """Handles receiving and displaying video streams"""
    
    def __init__(self, listen_port=VIDEO_PORT):
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, VIDEO_BUFFER_SIZE)
        self.running = False
        
    def start_receiving(self):
        """Receive and display video frames"""
        try:
            self.sock.bind(('0.0.0.0', self.listen_port))
            print(f"Listening for video on port {self.listen_port}")
            print("Press 'q' to quit")
            
            self.running = True
            frame_count = 0
            start_time = time.time()
            
            while self.running:
                try:
                    # Receive packet
                    data, addr = self.sock.recvfrom(VIDEO_BUFFER_SIZE)
                    
                    # Decompress and display frame
                    frame = self.decompress_frame(data)
                    
                    if frame is not None:
                        cv2.imshow(f'Video Stream - Receiving from {addr[0]}', frame)
                        
                        # Calculate and display FPS
                        frame_count += 1
                        if frame_count % 30 == 0:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            print(f"Receiving at {fps:.2f} FPS from {addr[0]}:{addr[1]}")
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error receiving frame: {e}")
                    
        finally:
            self.stop_receiving()
    
    def decompress_frame(self, data):
        """Decompress JPEG bytes to frame"""
        try:
            # Skip protocol header (12 bytes) and decode the payload
            from shared.helpers import unpack_message
            version, msg_type, payload_length, seq_num, payload = unpack_message(data)
            
            # Decode JPEG
            nparr = np.frombuffer(payload, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
        except Exception as e:
            print(f"Error decompressing frame: {e}")
            return None
    
    def stop_receiving(self):
        """Clean up resources"""
        self.running = False
        cv2.destroyAllWindows()
        self.sock.close()
        print("Video receiving stopped")


def main():
    """Main function for testing video streaming"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LAN Video Streaming')
    parser.add_argument('mode', choices=['send', 'receive'], 
                       help='Mode: send (stream webcam) or receive (display stream)')
    parser.add_argument('--ip', default='127.0.0.1', 
                       help='Server IP address (for sender mode)')
    parser.add_argument('--port', type=int, default=VIDEO_PORT,
                       help=f'Port number (default: {VIDEO_PORT})')
    
    args = parser.parse_args()
    
    if args.mode == 'send':
        streamer = VideoStreamer(server_ip=args.ip, server_port=args.port)
        streamer.start_streaming()
    elif args.mode == 'receive':
        receiver = VideoReceiver(listen_port=args.port)
        receiver.start_receiving()


if __name__ == '__main__':
    main()

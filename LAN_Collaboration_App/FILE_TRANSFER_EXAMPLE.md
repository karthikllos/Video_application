# File Transfer Workflow Example

## 📋 Upload File Workflow

### Example 1: Basic Upload

```python
from client.client_file_transfer import upload_file

# Upload a file
success = upload_file('document.pdf', server_ip='127.0.0.1', server_port=5004)

if success:
    print("File uploaded successfully!")
else:
    print("Upload failed!")
```

**Output:**
```
📤 Uploading: document.pdf
📊 Size: 2.45 MB
🔒 Calculating checksum...
🔑 MD5: 5d41402abc4b2a76b9719d911017c592
✓ Connected to file transfer server at 127.0.0.1:5004

📦 Sending metadata...
📡 Sending file data...
Uploading: 100%|████████████████████| 2.45M/2.45M [00:03<00:00, 820kB/s]

⏳ Waiting for server acknowledgment...
✓ Upload successful!
📊 Total sent: 2.45 MB
```

---

### Example 2: Upload Without Checksum

```python
from client.client_file_transfer import upload_file

# Upload without checksum verification (faster)
success = upload_file(
    'large_video.mp4',
    server_ip='192.168.1.100',
    verify_checksum=False
)
```

---

### Example 3: Using FileTransferClient Class

```python
from client.client_file_transfer import FileTransferClient

# Create client
client = FileTransferClient(server_ip='127.0.0.1', server_port=5004)

# Connect
if client.connect():
    # Upload multiple files
    files = ['file1.txt', 'file2.pdf', 'image.jpg']
    
    for file_path in files:
        success = client.upload_file(file_path)
        if success:
            print(f"✓ {file_path} uploaded")
        else:
            print(f"✗ {file_path} failed")
    
    # Disconnect
    client.disconnect()
```

---

### Example 4: Command Line Upload

```bash
# Upload a file
python client/client_file_transfer.py upload document.pdf --ip 127.0.0.1 --port 5004

# Upload without checksum
python client/client_file_transfer.py upload large_file.zip --no-checksum

# Upload to remote server
python client/client_file_transfer.py upload report.docx --ip 192.168.1.100
```

---

## 📥 Download File Workflow

### Example 1: Basic Download

```python
from client.client_file_transfer import download_file

# Download a file
success = download_file(
    'document.pdf',
    save_path='./downloads',
    server_ip='127.0.0.1',
    server_port=5004
)

if success:
    print("File downloaded successfully!")
```

**Output:**
```
📥 Requesting download: document.pdf
✓ Connected to file transfer server at 127.0.0.1:5004
⏳ Waiting for metadata...
📊 Size: 2.45 MB
🔑 MD5: 5d41402abc4b2a76b9719d911017c592

📥 Downloading to: downloads\document.pdf
Downloading: 100%|████████████████| 2.45M/2.45M [00:02<00:00, 1.02MB/s]

✓ Download complete!
📊 Total received: 2.45 MB

🔒 Verifying checksum...
✓ Checksum verified!
```

---

### Example 2: Command Line Download

```bash
# Download a file
python client/client_file_transfer.py download document.pdf --output ./downloads

# Download without checksum verification
python client/client_file_transfer.py download large_file.zip --no-checksum

# Download from remote server
python client/client_file_transfer.py download report.docx --ip 192.168.1.100 -o ./received
```

---

## 🔧 Complete Workflow Example

### Scenario: File Sharing Between Two Computers

**Computer A (Sender):**
```python
from client.client_file_transfer import FileTransferClient

# Create and connect client
sender = FileTransferClient(server_ip='192.168.1.100', server_port=5004)

if sender.connect():
    # Upload a file
    print("Uploading project files...")
    
    success = sender.upload_file(
        'project_report.pdf',
        verify_checksum=True
    )
    
    if success:
        print("✓ File sent successfully!")
    
    sender.disconnect()
```

**Computer B (Receiver - Running Server):**
```python
# Server receives the file and saves it
# Then Computer B can download from server
from client.client_file_transfer import download_file

download_file(
    'project_report.pdf',
    save_path='./received_files',
    server_ip='127.0.0.1',  # Local server
    verify_checksum=True
)
```

---

## 📊 Progress Bar Output Examples

### Small File (< 1 MB):
```
Uploading: 100%|████████████████████████| 485k/485k [00:00<00:00, 2.1MB/s]
```

### Medium File (10 MB):
```
Uploading: 100%|████████████████████████| 10.5M/10.5M [00:05<00:00, 2.0MB/s]
```

### Large File (100 MB):
```
Uploading:  45%|█████████▌          | 45.2M/100M [00:22<00:27, 2.0MB/s]
```

---

## 🔒 Checksum Verification Example

```python
from client.client_file_transfer import FileTransferClient
import hashlib

# Upload with checksum
client = FileTransferClient('127.0.0.1', 5004)
client.connect()

file_path = 'important_data.db'

# Manual checksum calculation
with open(file_path, 'rb') as f:
    original_md5 = hashlib.md5(f.read()).hexdigest()
    print(f"Original MD5: {original_md5}")

# Upload (checksum calculated automatically)
success = client.upload_file(file_path, verify_checksum=True)

client.disconnect()
```

**Output:**
```
Original MD5: 098f6bcd4621d373cade4e832627b4f6
📤 Uploading: important_data.db
📊 Size: 5.23 MB
🔒 Calculating checksum...
🔑 MD5: 098f6bcd4621d373cade4e832627b4f6
...
✓ Upload successful!
```

---

## 🎯 Error Handling Example

```python
from client.client_file_transfer import FileTransferClient

def safe_upload(file_path, server_ip):
    \"\"\"Safely upload a file with error handling\"\"\"
    client = FileTransferClient(server_ip, 5004)
    
    try:
        if not client.connect():
            print("Failed to connect to server")
            return False
        
        success = client.upload_file(file_path)
        
        if not success:
            print("Upload failed - retrying...")
            # Retry logic
            success = client.upload_file(file_path)
        
        return success
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        client.disconnect()

# Use it
result = safe_upload('data.csv', '192.168.1.100')
```

---

## 📈 Batch Upload Example

```python
from client.client_file_transfer import FileTransferClient
from pathlib import Path

def upload_directory(directory, server_ip):
    \"\"\"Upload all files in a directory\"\"\"
    client = FileTransferClient(server_ip, 5004)
    
    if not client.connect():
        return
    
    directory = Path(directory)
    files = list(directory.glob('*'))
    
    print(f"Uploading {len(files)} files...")
    
    successful = 0
    failed = 0
    
    for file_path in files:
        if file_path.is_file():
            print(f"\n{'='*60}")
            print(f"File {successful + failed + 1}/{len(files)}")
            
            if client.upload_file(str(file_path)):
                successful += 1
            else:
                failed += 1
    
    client.disconnect()
    
    print(f"\n\n{'='*60}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")

# Upload all files in a folder
upload_directory('./documents', '192.168.1.100')
```

**Output:**
```
Uploading 5 files...

============================================================
File 1/5
📤 Uploading: report.pdf
...
✓ Upload successful!

============================================================
File 2/5
📤 Uploading: data.xlsx
...
✓ Upload successful!

...

============================================================
✓ Successful: 4
✗ Failed: 1
```

---

## 🚀 Performance Tips

### 1. Disable Checksum for Large Files
```python
# Faster for trusted networks
upload_file('movie.mp4', verify_checksum=False)
```

### 2. Adjust Chunk Size
```python
# In shared/constants.py
FILE_CHUNK_SIZE = 65536  # 64 KB (default is 32 KB)
```

### 3. Use Wired Connection
- Upload speeds: Ethernet >> WiFi
- 100 Mbps Ethernet: ~10 MB/s
- WiFi: ~2-5 MB/s typical

### 4. Close Other Network Apps
- Stop downloads/streaming
- Close cloud sync services
- Disable background updates

---

## 📝 File Size Limits

```python
# From shared/constants.py
MAX_FILE_SIZE = 104857600  # 100 MB

# To change, edit constants.py
MAX_FILE_SIZE = 1073741824  # 1 GB
```

---

## ✅ Success Indicators

**Upload Success:**
```
✓ Connected to file transfer server
📦 Sending metadata...
📡 Sending file data...
Uploading: 100%|████████████████████| ...
⏳ Waiting for server acknowledgment...
✓ Upload successful!
```

**Download Success:**
```
✓ Connected to file transfer server
⏳ Waiting for metadata...
📥 Downloading to: ...
Downloading: 100%|████████████████| ...
✓ Download complete!
🔒 Verifying checksum...
✓ Checksum verified!
```

---

## 🔍 Metadata Structure

```python
# Metadata sent before file transfer
{
    'filename': 'document.pdf',
    'filesize': 2567890,  # bytes
    'checksum': '5d41402abc4b2a76b9719d911017c592'  # MD5
}

# Packed format (from helpers.py):
# [4 bytes: filename_length]
# [variable: filename_bytes]
# [8 bytes: filesize]
# [4 bytes: checksum_length]
# [variable: checksum_bytes]
```

---

## 🎓 Educational Notes

### Why TCP?
- **Guaranteed delivery**: No lost data
- **In-order**: Chunks arrive in sequence
- **Error checking**: Built-in integrity
- **Flow control**: Automatic speed adjustment

### Why Chunking?
- **Memory efficient**: Don't load entire file
- **Progress tracking**: Update after each chunk
- **Resumable**: Could implement resume later
- **Network friendly**: Avoid timeout on large files

### Why MD5 Checksum?
- **Data integrity**: Verify no corruption
- **Fast**: Quick calculation even for large files
- **Standard**: Widely supported
- **Collision resistant**: (for this use case)

Note: For security, use SHA-256 instead of MD5

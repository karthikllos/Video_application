# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using Poetry
poetry install
```

### Running the Application
```bash
# Start as server
python -m src server

# Start as client
python -m src client

# Run Flask app directly (deprecated approach)
python src/app.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_discovery.py

# Run tests with coverage
pytest --cov=src

# Run tests with verbose output
pytest -v
```

## Architecture

### High-Level Overview
The LAN Collaboration App is a client-server application enabling real-time communication (video, audio, text) over a local area network. The architecture follows a clear separation between server, client, and core functionality.

### Key Components

**Server Architecture (`src/server/`)**
- **server.py**: Dual-mode server combining Flask HTTP endpoints and raw socket communication. Flask runs on port 5001 for control, while raw sockets handle client connections on port 5000. Each client connection spawns a dedicated thread via `handle_client_connection()`.
- **protocols.py**: Defines message protocol formats (handshake, message, disconnect, error) as dictionaries for client-server communication.
- **handlers.py**: Contains message type handlers (`handle_chat_message`, `handle_audio_message`, `handle_video_message`) that process different communication types.

**Client Architecture (`src/client/`)**
- **client.py**: Socket-based client that connects to server, manages message send/receive, and integrates with the UI layer.
- **ui.py**: PyQt5-based GUI with `MainWindow` class providing chat area, message input, and send button. Currently displays messages locally but needs integration with client.py's network layer.

**Core Utilities (`src/core/`)**
- **discovery.py**: UDP broadcast-based server discovery mechanism. Broadcasts `DISCOVER_SERVERS` message and listens for `SERVER_RESPONSE` to build a list of available servers on the LAN.
- **sync.py**: `SyncManager` class maintains shared state dictionary, allowing clients to synchronize data with server through `synchronize()` method.
- **utils.py**: Placeholder for shared utility functions.

### Important Patterns

**Dual Network Stack**: The server uses both Flask (HTTP/REST) and raw sockets (TCP). Flask handles server control endpoints (`/start`), while raw sockets handle actual client communication. When working on networking code, be clear about which layer you're modifying.

**Threading Model**: Each client connection runs in its own thread. The discovery service also uses daemon threads for listening. Be mindful of thread safety when modifying shared state like `active_sessions` in server.py.

**Configuration**: All network settings (IPs, ports, timeouts) are centralized in `src/config.py`. Use these constants rather than hardcoding values.

**Message Protocol**: Communication follows a dictionary-based protocol defined in `protocols.py`. All message types must include a `type` field. When adding new message types, extend both `protocols.py` and the corresponding handler in `handlers.py`.

### Current Architecture Gaps
- The UI in `client.py` references a `UserInterface` class that doesn't exist; actual GUI is `MainWindow` in `ui.py`
- `app.py` appears to be an early Flask prototype separate from the main server implementation
- Tests reference functions/methods that don't match the actual implementation (e.g., `discover_servers()` function vs `Discovery` class)
- No integration between PyQt5 UI and socket communication layer in the client

## Project Structure
```
lan-collab/
├── src/
│   ├── __main__.py      # Entry point, parses server/client mode
│   ├── app.py           # Legacy Flask app (likely superseded by server/server.py)
│   ├── config.py        # Centralized configuration constants
│   ├── server/          # Server implementation
│   │   ├── server.py    # Main server with Flask + socket handling
│   │   ├── protocols.py # Message protocol definitions
│   │   └── handlers.py  # Message type handlers
│   ├── client/          # Client implementation
│   │   ├── client.py    # Socket client with send/receive logic
│   │   └── ui.py        # PyQt5 GUI interface
│   └── core/            # Shared utilities
│       ├── discovery.py # LAN server discovery via UDP broadcast
│       └── sync.py      # Data synchronization manager
└── tests/
    ├── conftest.py      # Pytest fixtures
    ├── test_discovery.py
    └── test_sync.py
```

## Dependencies
- **PyQt5**: GUI framework for client interface
- **PyAudio**: Audio streaming (planned feature)
- **opencv-python**: Video streaming (planned feature)
- **pytest**: Testing framework
- **requests**: HTTP requests
- **Flask**: Web framework for server control endpoints (implicit dependency)

Note: `requirements.txt` lists dependencies, but Flask is missing despite being used in server code.

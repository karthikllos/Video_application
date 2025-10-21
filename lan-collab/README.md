# LAN Collaboration App

## Overview
The LAN Collaboration App is designed to facilitate real-time collaboration among users on a local area network (LAN). It supports various communication types, including video, audio, and text chat, allowing users to work together seamlessly.

## Features
- **Real-time Communication**: Engage in video, audio, and text chats.
- **Network Discovery**: Automatically find available servers on the LAN.
- **Synchronization**: Keep data in sync between clients and the server.
- **User Interface**: Intuitive UI built with a modern GUI framework.

## Getting Started

### Prerequisites
- Python 3.x
- Required libraries listed in `requirements.txt`

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd lan-collab
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
To start the application, run the following command:
```
python -m src
```
You will be prompted to choose between starting the server or the client.

## Directory Structure
```
lan-collab/
├── src/                # Source code for the application
│   ├── server/         # Server-side implementation
│   ├── client/         # Client-side implementation
│   └── core/           # Core functionalities
├── tests/              # Unit tests for the application
├── docs/               # Documentation files
├── requirements.txt     # Project dependencies
├── pyproject.toml      # Project metadata
├── setup.cfg           # Packaging configuration
├── .gitignore          # Files to ignore in version control
└── README.md           # Project overview and instructions
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
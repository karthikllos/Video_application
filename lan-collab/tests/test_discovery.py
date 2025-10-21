import pytest
from src.core.discovery import discover_servers

def test_discover_servers(mocker):
    mocker.patch('src.core.discovery.socket.socket')
    mock_socket = mocker.Mock()
    mock_socket.recv.return_value = b'{"servers": ["192.168.1.1", "192.168.1.2"]}'
    mocker.patch('src.core.discovery.socket.socket.return_value', mock_socket)

    servers = discover_servers()
    
    assert len(servers) == 2
    assert "192.168.1.1" in servers
    assert "192.168.1.2" in servers

def test_discover_servers_no_response(mocker):
    mocker.patch('src.core.discovery.socket.socket')
    mock_socket = mocker.Mock()
    mock_socket.recv.return_value = b'{}'
    mocker.patch('src.core.discovery.socket.socket.return_value', mock_socket)

    servers = discover_servers()
    
    assert len(servers) == 0
import pytest
from src.core.sync import SyncManager

@pytest.fixture
def sync_manager():
    return SyncManager()

def test_sync_data(sync_manager):
    data = {"message": "Hello, World!"}
    sync_manager.sync(data)
    assert sync_manager.get_last_sync() == data

def test_sync_multiple_clients(sync_manager):
    data1 = {"client1": "Data from client 1"}
    data2 = {"client2": "Data from client 2"}
    
    sync_manager.sync(data1)
    sync_manager.sync(data2)
    
    assert sync_manager.get_last_sync() == data2  # Last sync should be from client 2

def test_sync_empty_data(sync_manager):
    data = {}
    sync_manager.sync(data)
    assert sync_manager.get_last_sync() == data  # Should handle empty data gracefully
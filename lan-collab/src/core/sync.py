# File: /lan-collab/lan-collab/src/core/sync.py

class SyncManager:
    def __init__(self):
        self.data = {}

    def synchronize(self, client_data):
        # Update the local data with the client's data
        self.data.update(client_data)
        return self.data

    def get_data(self):
        return self.data

    def clear_data(self):
        self.data.clear()
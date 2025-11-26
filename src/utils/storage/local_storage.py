import os
from .storage_base import StorageBase
from config import Config

class LocalStorage(StorageBase):
    def __init__(self):
        os.makedirs(Config.LOCAL_LOG_DIR, exist_ok=True)
        os.makedirs(Config.LOCAL_META_DIR, exist_ok=True)
        os.makedirs(Config.LOCAL_DATA_DIR, exist_ok=True)

    def save(self, file_path, file_name, content):
        full_path = os.path.join(file_path, file_name)
        with open(full_path, 'wb') as f:
            f.write(content)
        return full_path
# import sys
# import os
#
# # 프로젝트 루트 디렉토리를 path에 추가
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config import Config
from .local_storage import LocalStorage

def get_storage():
    if Config.STORAGE_TYPE == "local":
        return LocalStorage()
    else:
        raise ValueError(f"Unsupported storage type: {Config.STORAGE_TYPE}")
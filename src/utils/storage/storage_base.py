from abc import ABC, abstractmethod

class StorageBase(ABC):
    @abstractmethod
    def save(self, file_path: str, content: bytes) -> str:
        pass

    # @abstractmethod
    # def read(self, file_path: str) -> bytes:
    #     pass
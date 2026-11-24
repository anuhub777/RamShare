from abc import ABC, abstractmethod
from typing import List

class FileStorageBackend(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        pass

    @abstractmethod
    async def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        pass

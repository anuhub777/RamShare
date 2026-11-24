import os
import asyncio
from typing import List
from app.file_storage.base import FileStorageBackend

class LocalFileStorage(FileStorageBackend):
    def __init__(self, base_dir: str = "./ramshare-storage"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _resolve(self, key: str) -> str:
        clean_key = os.path.normpath(key).replace("\\", "/")
        clean_key = clean_key.lstrip("/")
        return os.path.join(self.base_dir, clean_key)

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        full_path = self._resolve(key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        def _write():
            with open(full_path, "wb") as f:
                f.write(data)
        await asyncio.to_thread(_write)
        return key

    async def download(self, key: str) -> bytes:
        full_path = self._resolve(key)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File key not found: {key}")
        def _read():
            with open(full_path, "rb") as f:
                return f.read()
        return await asyncio.to_thread(_read)

    async def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        return f"/api/files/{key}"

    async def delete(self, key: str) -> bool:
        full_path = self._resolve(key)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    async def list_keys(self, prefix: str = "") -> List[str]:
        keys = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.base_dir)
                if rel_path.startswith(prefix):
                    keys.append(rel_path)
        return keys

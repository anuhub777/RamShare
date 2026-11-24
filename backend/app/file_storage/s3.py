from typing import List
from app.file_storage.base import FileStorageBackend
class S3FileStorage(FileStorageBackend):
    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region_name = region_name
        try:
            import boto3
            self.boto3 = boto3
        except ImportError:
            self.boto3 = None

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        raise NotImplementedError("S3 storage not enabled for local mode.")

    async def download(self, key: str) -> bytes:
        raise NotImplementedError("S3 storage not enabled for local mode.")

    async def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        raise NotImplementedError("S3 storage not enabled for local mode.")

    async def delete(self, key: str) -> bool:
        raise NotImplementedError("S3 storage not enabled for local mode.")

    async def list_keys(self, prefix: str = "") -> List[str]:
        raise NotImplementedError("S3 storage not enabled for local mode.")

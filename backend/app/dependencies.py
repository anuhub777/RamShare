from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.storage.base import StorageBackend
from app.storage.local import LocalStorage
from app.storage.dynamodb import DynamoDBStorage
from app.queue.base import QueueBackend
from app.queue.local import LocalQueue
from app.queue.sqs import SQSQueue
from app.file_storage.base import FileStorageBackend
from app.file_storage.local import LocalFileStorage
from app.file_storage.s3 import S3FileStorage
from app.services.auth_service import AuthService
from app.services.provider_service import ProviderService
from app.services.job_service import JobService
from app.services.matchmaking_service import MatchmakingService
from app.services.credit_service import CreditService
from app.services.marketplace_service import MarketplaceService
from app.models.user import User
from app.utils.security import decode_access_token
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Singletons for local dev
_storage_instance: Optional[StorageBackend] = None
_queue_instance: Optional[QueueBackend] = None
_file_storage_instance: Optional[FileStorageBackend] = None

def get_storage_instance() -> StorageBackend:
    global _storage_instance
    if _storage_instance is None:
        if settings.mode == "aws":
            _storage_instance = DynamoDBStorage(region_name=settings.aws_region)
        else:
            _storage_instance = LocalStorage(db_path=settings.database_url)
    return _storage_instance

def set_storage_instance(instance: StorageBackend) -> None:
    global _storage_instance
    _storage_instance = instance

def get_queue_instance() -> QueueBackend:
    global _queue_instance
    if _queue_instance is None:
        if settings.mode == "aws":
            _queue_instance = SQSQueue(queue_url=settings.sqs_job_queue_url)
        else:
            _queue_instance = LocalQueue()
    return _queue_instance

def get_file_storage_instance() -> FileStorageBackend:
    global _file_storage_instance
    if _file_storage_instance is None:
        if settings.mode == "aws":
            _file_storage_instance = S3FileStorage(bucket_name=settings.s3_bucket, region_name=settings.aws_region)
        else:
            _file_storage_instance = LocalFileStorage()
    return _file_storage_instance

def get_storage() -> StorageBackend:
    return get_storage_instance()

def get_queue() -> QueueBackend:
    return get_queue_instance()

def get_file_storage() -> FileStorageBackend:
    return get_file_storage_instance()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    storage: StorageBackend = Depends(get_storage)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = await storage.get_user_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def get_auth_service(storage: StorageBackend = Depends(get_storage)) -> AuthService:
    return AuthService(storage)

def get_provider_service(storage: StorageBackend = Depends(get_storage)) -> ProviderService:
    return ProviderService(storage)

def get_job_service(
    storage: StorageBackend = Depends(get_storage),
    queue: QueueBackend = Depends(get_queue)
) -> JobService:
    return JobService(storage, queue)

def get_matchmaking_service(
    storage: StorageBackend = Depends(get_storage),
    queue: QueueBackend = Depends(get_queue)
) -> MatchmakingService:
    return MatchmakingService(storage, queue)

def get_credit_service(storage: StorageBackend = Depends(get_storage)) -> CreditService:
    return CreditService(storage)

def get_marketplace_service(storage: StorageBackend = Depends(get_storage)) -> MarketplaceService:
    return MarketplaceService(storage)

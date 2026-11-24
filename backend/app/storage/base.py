from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.user import User
from app.models.provider import Provider
from app.models.job import Job
from app.models.credit import CreditTransaction

class StorageBackend(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        pass

    # Users
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        pass

    @abstractmethod
    async def list_users(self) -> List[User]:
        pass

    # Providers
    @abstractmethod
    async def create_provider(self, provider: Provider) -> Provider:
        pass

    @abstractmethod
    async def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        pass

    @abstractmethod
    async def get_providers_by_user(self, user_id: str) -> List[Provider]:
        pass

    @abstractmethod
    async def update_provider(self, provider_id: str, **kwargs) -> Optional[Provider]:
        pass

    @abstractmethod
    async def list_providers(self, online_only: bool = False) -> List[Provider]:
        pass

    @abstractmethod
    async def delete_provider(self, provider_id: str) -> bool:
        pass

    # Jobs
    @abstractmethod
    async def create_job(self, job: Job) -> Job:
        pass

    @abstractmethod
    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        pass

    @abstractmethod
    async def get_jobs_by_consumer(self, consumer_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        pass

    @abstractmethod
    async def get_jobs_by_provider(self, provider_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        pass

    @abstractmethod
    async def update_job(self, job_id: str, **kwargs) -> Optional[Job]:
        pass

    @abstractmethod
    async def list_jobs(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Job]:
        pass

    @abstractmethod
    async def get_job_by_idempotency_key(self, key: str) -> Optional[Job]:
        pass

    # Credits
    @abstractmethod
    async def create_transaction(self, txn: CreditTransaction) -> CreditTransaction:
        pass

    @abstractmethod
    async def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[CreditTransaction]:
        pass

    @abstractmethod
    async def get_transaction_by_idempotency_key(self, key: str) -> Optional[CreditTransaction]:
        pass

    @abstractmethod
    async def update_user_balance(self, user_id: str, new_balance: float) -> bool:
        pass

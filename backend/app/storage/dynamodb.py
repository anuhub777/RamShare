from typing import Optional, List
from app.storage.base import StorageBackend
from app.models.user import User
from app.models.provider import Provider
from app.models.job import Job
from app.models.credit import CreditTransaction
class DynamoDBStorage(StorageBackend):
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.client = None
        try:
            import boto3
            self.boto3 = boto3
        except ImportError:
            self.boto3 = None

    async def initialize(self) -> None:
        # Tables are provisioned via AWS SAM template
        pass

    async def create_user(self, user: User) -> User:
        raise NotImplementedError("DynamoDB storage not enabled for local mode. Use RAMSHARE_MODE=local.")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_user_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def list_users(self) -> List[User]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def create_provider(self, provider: Provider) -> Provider:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_providers_by_user(self, user_id: str) -> List[Provider]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def update_provider(self, provider_id: str, **kwargs) -> Optional[Provider]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def list_providers(self, online_only: bool = False) -> List[Provider]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def delete_provider(self, provider_id: str) -> bool:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def create_job(self, job: Job) -> Job:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_jobs_by_consumer(self, consumer_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_jobs_by_provider(self, provider_id: str, limit: int = 50, offset: int = 0) -> List[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def update_job(self, job_id: str, **kwargs) -> Optional[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def list_jobs(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_job_by_idempotency_key(self, key: str) -> Optional[Job]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def create_transaction(self, txn: CreditTransaction) -> CreditTransaction:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[CreditTransaction]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def get_transaction_by_idempotency_key(self, key: str) -> Optional[CreditTransaction]:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

    async def update_user_balance(self, user_id: str, new_balance: float) -> bool:
        raise NotImplementedError("DynamoDB storage not enabled for local mode.")

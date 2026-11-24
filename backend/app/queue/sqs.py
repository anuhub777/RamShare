from typing import Dict, Any, List
from app.queue.base import QueueBackend
class SQSQueue(QueueBackend):
    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        try:
            import boto3
            self.boto3 = boto3
        except ImportError:
            self.boto3 = None

    async def send_message(self, message: Dict[str, Any]) -> str:
        raise NotImplementedError("SQS Queue not enabled for local mode.")

    async def receive_messages(self, max_messages: int = 1) -> List[Dict[str, Any]]:
        raise NotImplementedError("SQS Queue not enabled for local mode.")

    async def delete_message(self, receipt_handle: str) -> bool:
        raise NotImplementedError("SQS Queue not enabled for local mode.")

    async def get_queue_size(self) -> int:
        raise NotImplementedError("SQS Queue not enabled for local mode.")

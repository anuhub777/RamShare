from abc import ABC, abstractmethod
from typing import Dict, Any, List

class QueueBackend(ABC):
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def receive_messages(self, max_messages: int = 1) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_message(self, receipt_handle: str) -> bool:
        pass

    @abstractmethod
    async def get_queue_size(self) -> int:
        pass

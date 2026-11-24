import asyncio
import uuid
import time
from typing import Dict, Any, List
from app.queue.base import QueueBackend

class LocalQueue(QueueBackend):
    def __init__(self, visibility_timeout: int = 30):
        self.visibility_timeout = visibility_timeout
        self._queue = asyncio.Queue()
        self._in_flight: Dict[str, Dict[str, Any]] = {}

    async def send_message(self, message: Dict[str, Any]) -> str:
        msg_id = uuid.uuid4().hex
        item = {
            "message_id": msg_id,
            "body": message,
            "receive_count": 0
        }
        await self._queue.put(item)
        return msg_id

    async def receive_messages(self, max_messages: int = 1) -> List[Dict[str, Any]]:
        # First check expired in-flight messages and re-queue them
        now = time.time()
        expired = [rh for rh, data in self._in_flight.items() if now > data["visible_at"]]
        for rh in expired:
            item = self._in_flight.pop(rh)
            await self._queue.put({
                "message_id": item["message_id"],
                "body": item["body"],
                "receive_count": item["receive_count"]
            })

        results = []
        for _ in range(max_messages):
            if self._queue.empty():
                break
            try:
                item = self._queue.get_nowait()
                receipt_handle = uuid.uuid4().hex
                item["receive_count"] += 1
                self._in_flight[receipt_handle] = {
                    "message_id": item["message_id"],
                    "body": item["body"],
                    "receive_count": item["receive_count"],
                    "visible_at": time.time() + self.visibility_timeout
                }
                results.append({
                    "message_id": item["message_id"],
                    "body": item["body"],
                    "receipt_handle": receipt_handle,
                    "receive_count": item["receive_count"]
                })
            except asyncio.QueueEmpty:
                break
        return results

    async def delete_message(self, receipt_handle: str) -> bool:
        return self._in_flight.pop(receipt_handle, None) is not None

    async def get_queue_size(self) -> int:
        return self._queue.qsize() + len(self._in_flight)

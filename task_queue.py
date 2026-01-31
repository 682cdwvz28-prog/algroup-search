import asyncio
from collections import deque

class TaskQueue:
    def __init__(self):
        self._queue = deque()
        self._lock = asyncio.Lock()

    async def put(self, task):
        async with self._lock:
            self._queue.append(task)

    async def get(self):
        async with self._lock:
        # если пусто — вернуть None
            if not self._queue:
                return None
            return self._queue.popleft()

    def __len__(self):
        return len(self._queue)

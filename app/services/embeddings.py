from __future__ import annotations

import asyncio
import hashlib
import struct
from typing import List, Optional, Tuple


class EmbeddingsWorker:
    """Async queue worker that produces deterministic hash-based embeddings."""

    def __init__(self) -> None:
        self._queue: Optional[
            asyncio.Queue[Tuple[str, asyncio.Future[List[float]]]]
        ] = None
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._queue is None:
            self._queue = asyncio.Queue()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._runner())

    async def shutdown(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self._queue = None

    async def embed(self, text: str) -> List[float]:
        if self._queue is None:
            raise RuntimeError("Embeddings worker not started")
        loop = asyncio.get_running_loop()
        result: asyncio.Future[List[float]] = loop.create_future()
        await self._queue.put((text, result))
        return await result

    async def _runner(self) -> None:
        assert self._queue is not None
        while True:
            text, future = await self._queue.get()
            try:
                embedding = self._compute_embedding(text)
                future.set_result(embedding)
            except Exception as exc:  # pragma: no cover - unexpected runtime errors
                future.set_exception(exc)

    @staticmethod
    def _compute_embedding(text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        parts = struct.unpack("!8I", digest[:32])
        scale = float(2**32)
        return [round(value / scale, 6) for value in parts]

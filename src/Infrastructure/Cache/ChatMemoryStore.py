from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from redis.exceptions import RedisError

from src.Infrastructure.Cache.RedisClient import get_redis_client
from src.SharedKernel.Logging.Logger import get_logger


class ChatMemoryStore:
    """
    Camada simples de persistência de memória do chat no Redis.
    """

    def __init__(
        self,
        *,
        key_prefix: str = "chat:session:",
        ttl_seconds: Optional[int] = None,
        max_history_entries: int = 50,
    ):
        self._redis = get_redis_client()
        self._logger = get_logger(__name__)
        self._key_prefix = key_prefix
        self._ttl = ttl_seconds
        self._max_history_entries = max_history_entries

    def _build_key(self, session_id: str) -> str:
        return f"{self._key_prefix}{session_id}"

    def _base_memory(
        self,
        *,
        symptom_list: Optional[list[str]] = None,
        disease: Optional[str] = None,
        history: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        return {
            "symptom_list": symptom_list or [],
            "disease": disease,
            "history": history or [],
        }

    async def get_memory(self, session_id: str) -> Optional[dict[str, Any]]:
        key = self._build_key(session_id)
        try:
            raw_data = await self._redis.get(key)
        except RedisError as exc:
            self._logger.error("Erro ao recuperar memória do Redis para %s: %s", key, exc)
            return None

        if not raw_data:
            return None

        try:
            return json.loads(raw_data)
        except json.JSONDecodeError:
            self._logger.warning("Payload inválido na memória do chat para %s", key)
            return None

    async def save_memory(
        self,
        session_id: str,
        symptom_list: list[str],
        disease: Optional[str],
        *,
        history: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        key = self._build_key(session_id)
        data = self._base_memory(
            symptom_list=symptom_list,
            disease=disease,
            history=history,
        )
        return await self._write_data(key, data)

    async def append_history(self, session_id: str, role: str, message: str) -> dict[str, Any]:
        """
        Adiciona uma entrada (role/message) ao histórico, respeitando o limite configurado.
        """
        key = self._build_key(session_id)
        data = await self.get_memory(session_id) or self._base_memory()

        history = data.get("history") or []
        history.append(
            {
                "role": role,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        if self._max_history_entries:
            history = history[-self._max_history_entries :]

        data["history"] = history
        return await self._write_data(key, data)

    async def _write_data(self, key: str, data: dict[str, Any]) -> dict[str, Any]:
        try:
            if self._ttl:
                await self._redis.set(key, json.dumps(data), ex=self._ttl)
            else:
                await self._redis.set(key, json.dumps(data))
        except RedisError as exc:
            self._logger.error("Erro ao salvar memória no Redis para %s: %s", key, exc)

        return data


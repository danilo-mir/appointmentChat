from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import redis.asyncio as redis
from redis.asyncio.client import Redis


def _load_env_from_project_root() -> None:
    """
    Garante que variáveis do arquivo .env na raiz do projeto sejam carregadas
    quando o serviço estiver rodando localmente.
    """
    project_root = Path(__file__).resolve().parents[3]
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


def get_redis_url() -> str:
    """
    Recupera a URL do Redis a partir da variável REDIS_URL.

    Caso não esteja definida, tenta carregar um arquivo .env local.
    Como fallback final, assume uma instância local padrão.
    """
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis_url

    _load_env_from_project_root()
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis_url

    return "redis://localhost:6379/0"


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    """
    Retorna um cliente Redis compartilhado (async) configurado para retornar
    strings (decode_responses=True).
    """
    redis_url = get_redis_url()
    return redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


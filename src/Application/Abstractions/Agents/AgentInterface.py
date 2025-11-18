from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from src.SharedKernel.Logging.Logger import get_logger

@dataclass
class AgentResponse:
    message: Optional[str] = None
    payload: dict = field(default_factory=dict)

@dataclass
class AgentConfig:
    model: str
    temperature: float
    max_tokens: int

class AgentInterface(ABC):
    def __init__(self, config: AgentConfig, system_prompt: str):
        self.config = config
        self.system_prompt = system_prompt
        self.logger = get_logger(__name__)

    @abstractmethod
    async def process(self, context: list[str]) -> AgentResponse:
        pass
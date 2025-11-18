from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from src.Application.Abstractions.Agents.AgentInterface import AgentInterface
from enum import Enum

class HandlerType(Enum):
    NEXT = "next"
    FINAL = "final"

@dataclass
class HandlerResponse:
    handler_type: HandlerType
    next_handler: str | None = None
    message: str | None = None
    payload: dict = field(default_factory=dict)

class Handler(ABC):
    def __init__(self, agent: AgentInterface):
        self.agent = agent

    @abstractmethod
    async def handle(self, context: list[str]) -> HandlerResponse:
        pass

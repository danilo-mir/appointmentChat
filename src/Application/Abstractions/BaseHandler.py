from abc import ABC, abstractmethod
from typing import List
from src.Application.Abstractions.BaseAgent import AgentResponse, Agent

class Handler(ABC):
    def __init__(self, agent: Agent):
        self.agent = agent

    @abstractmethod
    async def handle(self, context: List[str]) -> AgentResponse:
        """Processa o contexto usando o agent e retorna uma resposta."""
        pass

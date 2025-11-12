from abc import ABC, abstractmethod
from typing import List
from src.agents.base_agent import AgentResponse, Agent

class Handler(ABC):
    def __init__(self, agent: Agent):
        self.agent = agent

    @abstractmethod
    async def handle(self, context: List[str]) -> AgentResponse:
        """Processa o contexto usando o agent e retorna uma resposta."""
        pass

class RouterHandler(Handler):
    async def handle(self, context: List[str]) -> AgentResponse:
        return await self.agent.process(context)

class SintomasHandler(Handler):
    """
    Handler responsável por processar mensagens relacionadas aos sintomas
    durante uma anamnese, incluindo histórico de perguntas e respostas.
    """
    async def handle(self, context: List[str]) -> AgentResponse:
        return await self.agent.process(context)

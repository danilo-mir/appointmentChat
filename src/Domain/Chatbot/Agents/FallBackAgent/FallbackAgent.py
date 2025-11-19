from typing import List
from src.Domain.Chatbot.Abstractions.AgentInterface import (
    AgentInterface,
    AgentResponse,
    AgentType,
)
from src.SharedKernel.Logging.Logger import get_logger
from src.Domain.Chatbot.Abstractions.AgentInterface import (
    AgentResponse,
    AgentType,
)

class FallbackAgent(AgentInterface):

    def __init__(self, llm=None):
        super().__init__(llm)
        self.logger = get_logger(__name__)

    async def generate_response(self, context: List[str]) -> AgentResponse:
        try:
            last_message = context[-1] if context else ""
            
            agent_response = await self.agent.process(context)
            response_text = agent_response.message.strip()

            return AgentResponse(
                agent_type=AgentType.FINAL,
                message=response_text,
                next_agent=None
            )

        except Exception as e:
            self.logger.error(f"Erro no FallbackAgent: {str(e)}")
            return AgentResponse(
                agent_type=AgentType.FINAL,
                message="Ocorreu um erro inesperado ao processar sua mensagem.",
                next_agent=None
            )

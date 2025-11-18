from typing import List
from src.Application.Abstractions.Handlers.HandlerInterface import Handler, HandlerResponse, HandlerType
from src.SharedKernel.Logging.Logger import get_logger
from src.Application.Abstractions.Agents.AgentInterface import AgentConfig
from src.Application.Abstractions.Agents.GeminiAgent import GeminiAgent

class FallbackAgentHandler(Handler):
    """
    Handler que usa um agente IA para gerar uma resposta simples quando a
    mensagem do usuário não foi compreendida pelo fluxo principal.
    """

    def __init__(self, agent=None):
        super().__init__(agent)
        self.logger = get_logger(__name__)

    async def handle(self, context: List[str]) -> HandlerResponse:
        try:
            last_message = context[-1] if context else ""
            
            agent_response = await self.agent.process(context)
            response_text = agent_response.message.strip()

            return HandlerResponse(
                handler_type=HandlerType.FINAL,
                message=response_text,
                next_handler=None
            )

        except Exception as e:
            self.logger.error(f"Erro no FallbackAIHandler: {str(e)}")
            return HandlerResponse(
                handler_type=HandlerType.FINAL,
                message="Ocorreu um erro inesperado ao processar sua mensagem.",
                next_handler=None
            )

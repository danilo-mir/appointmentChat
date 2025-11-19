from typing import List
from src.SharedKernel.Logging.Logger import get_logger
from src.Domain.Chatbot.Abstractions.AgentInterface import AgentInterface, AgentType, AgentResponse


class RouterAgent(AgentInterface):
    def __init__(self, agent):
        super().__init__(agent)
        self.logger = get_logger(__name__)
        self.current_agent = None

    async def generate_response(self, context: List[str]) -> AgentResponse:
        try:
            user_message = context[-1]

            if self.current_agent and self._is_follow_up_question(user_message):
                return AgentResponse(
                    agent_type=AgentType.NEXT,
                    next_handler=self.current_handler
                )

            agent_result = await self.agent.process(context)

            predicted_handler = (agent_result.message or "").strip().lower()

            if not predicted_handler:
                predicted_handler = "sintomas"

            self.current_handler = predicted_handler

            return AgentResponse(
                agent_type=AgentType.NEXT,
                next_handler=self.current_handler
            )

        except Exception as e:
            self.logger.error(f"Erro no RouterHandler: {str(e)}")
            self.current_handler = "sintomas"
            return AgentResponse(
                agent_type=AgentType.NEXT,
                next_handler="sintomas"
            )

    def _is_follow_up_question(self, message: str) -> bool:
        follow_up_indicators = [
            "como", "pode", "exemplo", "explique",
            "mostre", "e se", "então", "mas", "e",
            "também", "mais detalhes", "melhor",
            "por que", "?", "..."
        ]

        message = message.lower().strip()
        return any(ind in message for ind in follow_up_indicators)

from typing import List
from src.Application.Abstractions.Handlers.HandlerInterface import Handler, HandlerResponse, HandlerType
from src.SharedKernel.Logging.Logger import get_logger
from src.Application.Abstractions.Tools.GetRandomSymptomsTool import GetRandomSymptomsTool

class GetRandomSymptomsHandler(Handler):
    def __init__(self, agent=None):
        super().__init__(agent)
        self.logger = get_logger(__name__)
        self.tool = GetRandomSymptomsTool()

    async def handle(self, context: List[str]) -> HandlerResponse:
        try:
            # Executa a tool para pegar sintomas do paciente aleatório
            tool_response = await self.tool.execute()
            payload = tool_response.payload

            self.logger.info(f"Sintomas selecionados aleatoriamente: {payload.get('symptom_list', [])}")

            # Retorna para o router com NEXT, agora usando payload
            return HandlerResponse(
                handler_type=HandlerType.NEXT,
                next_handler="router",
                payload=payload
            )

        except Exception as e:
            self.logger.error(f"Erro no GetRandomSymptomsHandler: {str(e)}")
            return HandlerResponse(
                handler_type=HandlerType.NEXT,
                next_handler="router",
                payload={"error": "Erro ao obter sintomas aleatórios."}
            )

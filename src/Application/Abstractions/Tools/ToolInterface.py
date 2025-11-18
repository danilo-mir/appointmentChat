import random
from typing import Any
from src.Application.Abstractions.Tools.ToolInterface import ToolInterface, ToolResponse

class GetRandomSymptomTool(ToolInterface):
    def __init__(self, symptoms_list: list[str] = None):
        super().__init__()
        self.symptoms_list = symptoms_list or [
            "headache", "fever", "nausea", "fatigue", "retal pain"
        ]

    async def execute(self, input_data: Any = None) -> ToolResponse:
        # Seleciona aleatoriamente um sintoma
        symptom = random.choice(self.symptoms_list)

        # Retorna dentro do payload
        return ToolResponse(payload={"symptom_list": symptom_list})

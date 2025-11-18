from src.Application.Abstractions.Agents.AgentInterface import AgentResponse, AgentConfig, AgentInterface
from src.Application.Abstractions.Handlers.HandlerInterface import HandlerType
import os
import asyncio
from google import genai
from google.genai import types

class GeminiAgent(AgentInterface):
    def __init__(self, config: AgentConfig, system_prompt: str):
        super().__init__(config, system_prompt)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente!")
        self.client = genai.Client(api_key=api_key)

    async def process(self, context: list[str]) -> AgentResponse:
        if not context:
            raise ValueError("Contexto vazio não é permitido")
        try:
            full_prompt = f"{self.system_prompt}\n\n{context[-1]}"

            # Chamada compatível com a SDK
            response = await asyncio.to_thread(
                lambda: self.client.models.generate_content(
                    model=self.config.model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens
                    )
                )
            )

            content = (
                    response.text
                    or (response.candidates[0].content.parts[0].text if response.candidates else "")
                    ).strip()

            return AgentResponse(
                message=content
            )

        except Exception as e:
            self.logger.error(f"Erro no GeminiAgent: {str(e)}")
            raise RuntimeError(f"Erro ao processar mensagem com Gemini: {str(e)}")

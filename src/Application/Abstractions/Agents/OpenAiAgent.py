from src.Application.Abstractions.Agents.AgentInterface import AgentResponse, AgentConfig, AgentInterface
import os
import openai
import asyncio

class OpenAIAgent(AgentInterface):
    def __init__(self, config: AgentConfig, system_prompt: str):
        super().__init__(config, system_prompt)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente!")
        openai.api_key = api_key

    async def process(self, context: list[str]) -> AgentResponse:
        if not context:
            raise ValueError("Contexto vazio não é permitido")

        try:
            response = await asyncio.to_thread(
                lambda: openai.ChatCompletion.create(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": context[-1]}
                    ]
                )
            )

            content = response.choices[0].message.content.strip()

            return AgentResponse(message=content)

        except Exception as e:
            self.logger.error(f"Erro no OpenAIAgent: {str(e)}")
            raise openai.error.OpenAIError(f"Erro ao processar mensagem com OpenAI: {str(e)}")

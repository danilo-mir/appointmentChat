from src.Domain.Interfaces.Llm.LlmInterface import LlmInterface, LlmResponse, LlmConfig
import os
import openai
import asyncio
from pathlib import Path
from dotenv import load_dotenv


class OpenAILlm(LlmInterface):
    def __init__(self, config: LlmConfig, system_prompt: str):
        super().__init__(config, system_prompt)
        
        # Carrega o .env da raiz do projeto
        src_dir = Path(__file__).resolve().parents[2]
        project_root = src_dir.parent
        env_path = project_root / ".env"
        
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente!")
        openai.api_key = api_key

    async def process(self, message: str) -> LlmResponse:
        if not message:
            raise ValueError("Mensagem vazia não é permitida")

        try:
            response = await asyncio.to_thread(
                lambda: openai.ChatCompletion.create(
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": message},
                    ],
                )
            )

            content = response.choices[0].message.content.strip()

            return LlmResponse(message=content)

        except Exception as e:
            self.logger.error(f"Erro no OpenAIAgent: {str(e)}")
            raise openai.error.OpenAIError(f"Erro ao processar mensagem com OpenAI: {str(e)}")

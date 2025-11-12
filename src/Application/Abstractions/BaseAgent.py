from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import os
import asyncio
import openai
from src.SharedKernel.Logging.Logger import get_logger
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class HandlerType(Enum):
    NEXT = "next"
    FINAL = "final"

@dataclass
class AgentResponse:
    handler_type: HandlerType
    next_handler: Optional[str] = None
    message: Optional[str] = None

@dataclass
class AgentConfig:
    model: str
    temperature: float
    max_tokens: int

class Agent(ABC):
    def __init__(self, config: AgentConfig, system_prompt: str):
        self.config = config
        self.system_prompt = system_prompt
        self.logger = get_logger(__name__)

    @abstractmethod
    async def process(self, context: list[str]) -> AgentResponse:
        """Processa o contexto e retorna uma resposta."""
        pass

class OpenAIAgent(Agent):
    def __init__(self, config: AgentConfig, system_prompt: str):
        super().__init__(config, system_prompt)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente!")
        openai.api_key = api_key

    async def process(self, context: list[str]) -> AgentResponse:
        """
        Processa o contexto usando a API da OpenAI.
        
        Args:
            context: Lista de mensagens do histórico da conversa
            
        Returns:
            AgentResponse: Resposta do agente contendo o tipo de handler e a mensagem/próximo handler
            
        Raises:
            openai.error.OpenAIError: Se houver erro na comunicação com a API
        """
        if not context:
            raise ValueError("Contexto vazio não é permitido")
            
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context[-1]}  # Última mensagem do contexto
                ]
            )

            content = response.choices[0].message.content.strip()

            # Se for o router, a resposta deve ser um dos handlers válidos
            if "router" in self.system_prompt.lower():
                valid_handlers = ["sintomas"]
                # Verifica se o conteúdo corresponde a um handler válido
                handler = content.lower().strip()
                if handler in valid_handlers:
                    return AgentResponse(
                        handler_type=HandlerType.NEXT,
                        next_handler=handler
                    )
                else:
                    # Se não for um handler válido, usa o handler de sintomas como padrão
                    return AgentResponse(
                        handler_type=HandlerType.NEXT,
                        next_handler="sintomas"
                    )
            
            # Para outros agents, a resposta é a mensagem final
            return AgentResponse(
                handler_type=HandlerType.FINAL,
                message=content
            )
            
        except Exception as e:
            self.logger.error(f"Erro no OpenAIAgent: {str(e)}")
            raise openai.error.OpenAIError(f"Erro ao processar mensagem com OpenAI: {str(e)}")  
        

class GeminiAgent(Agent):
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

            content = response.text.strip()

            if "router" in self.system_prompt.lower():
                valid_handlers = ["sintomas"]
                handler = content.lower().strip()
                if handler in valid_handlers:
                    return AgentResponse(
                        handler_type=HandlerType.NEXT,
                        next_handler=handler
                    )
                else:
                    return AgentResponse(
                        handler_type=HandlerType.NEXT,
                        next_handler="sintomas"
                    )

            return AgentResponse(
                handler_type=HandlerType.FINAL,
                message=content
            )

        except Exception as e:
            self.logger.error(f"Erro no GeminiAgent: {str(e)}")
            raise RuntimeError(f"Erro ao processar mensagem com Gemini: {str(e)}")

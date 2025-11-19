from typing import Dict
from src.Domain.Chatbot.Abstractions.AgentInterface import (
    AgentInterface,
    AgentType,
    AgentResponse,
)
from src.Domain.Factories.HandlerFactory import AgentFactory
from src.SharedKernel.Messages.Exceptions import (
    HandlerNotFoundError,
    MessageProcessingError,
    AgentConfigurationError,
    AgentTypeNotFoundError,
)
from src.SharedKernel.Logging.Logger import get_logger
from src.SharedKernel.Observer.Observer import MessageSubject, LoggingObserver
from src.Application.Handlers.Chat.DTOs_.ChatCommand import ChatCommand


class ChatCommandHandler:
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.agent_factory = AgentFactory()
        
        # Configuração do sistema de observadores
        self.message_subject = MessageSubject()
        self.message_subject.attach(LoggingObserver(self.logger))

        # Imagino que essas variaveis NAO devam ficar no controller pq tao armazenando memoria
        # Mas funciona por enquanto
        self.conversation_started = False
        self.data = {
            "symptom_list": {},
            "disease": {},
        }
        
        self.logger.info("💬 Chat inicializado e pronto para uso")

    async def handle(self, command: ChatCommand) -> str:
        try:
            current_agent_type = "router"

            message = command.message

            # Notifica sobre a mensagem do usuário
            self.message_subject.notify(
                message=message,
                role="user"
            )
            
            while True:
                if current_agent_type == "sintomas":
                    prompt_data = {
                        "symptom_list": self.data['symptom_list'],
                        "disease": self.data['disease']
                    }
                else:
                    prompt_data = {}

                agent = self._get_agent(
                    agent_type=current_agent_type,
                    llm_type='gemini',
                    prompt_data=prompt_data
                )

                response = await agent.generate_response(message)
                
                # Notifica sobre a resposta do handler
                if response.message:
                    self.message_subject.notify(
                        message=response.message,
                        role="assistant"
                    )
                
                if response.agent_type == AgentType.FINAL:
                    return response.message

                # Valida next_agent retornado pelo agent e aplica fallback mínimo
                next_agent = response.next_agent or "sintomas"
                # Se o agent factory não conhece esse tipo, cai para 'sintomas'
                if not isinstance(next_agent, str) or next_agent not in self.agent_factory.agent_classes:
                    self.logger.warning(f"Next agent inválido recebido: {next_agent!r}, usando 'sintomas' como fallback")
                    current_agent_type = "sintomas"
                else:
                    current_agent_type = next_agent
            
        except Exception as e:
            raise

    def _get_agent(self, agent_type: str, llm_type: str, prompt_data: dict[str, object]) -> AgentInterface:
        try:
            return self.agent_factory.create_agent(
                agent_type=agent_type,
                llm_type=llm_type,
                prompt_data=prompt_data
            )
        except (HandlerNotFoundError, AgentConfigurationError, AgentTypeNotFoundError):
            # Re-raise domain-specific exceptions as-is
            raise
        except ValueError as e:
            # Convert ValueError (e.g., missing API key) to AgentConfigurationError
            raise AgentConfigurationError(f"Erro de configuração ao criar o agente: {str(e)}")
        except Exception as e:
            # For other unexpected errors, wrap as HandlerNotFoundError
            raise HandlerNotFoundError(f"Não foi possível obter o agente: {str(e)}")

    

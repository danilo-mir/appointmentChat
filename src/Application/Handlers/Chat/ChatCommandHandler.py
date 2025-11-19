from typing import List, Dict
from src.Domain.Chatbot.Abstractions.AgentInterface import (
    AgentInterface,
    AgentType as HandlerType,
    AgentResponse,
)
from src.Domain.Factories.HandlerFactory import AgentFactory
from src.SharedKernel.Messages.Exceptions import HandlerNotFoundError, MessageProcessingError
from src.SharedKernel.Logging.Logger import get_logger
from src.SharedKernel.Observer.Observer import MessageSubject, LoggingObserver


class ChatCommandHandler:
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.agent_factory = AgentFactory()
        
        # Configuração do sistema de observadores
        self.message_subject = MessageSubject()
        self.message_subject.attach(LoggingObserver(self.logger))

        # Kwargs a serem adicionados em prompts
        # Vai ser obtido por ex do handler do random symptom
        # self.prompt_data = {
        #     "symptom_list": ["retal pain"],
        #     "disease": "ligma"
        # }

        # Imagino que essas variaveis NAO devam ficar no controller pq tao armazenando memoria @Buzz
        # Mas funciona por enquanto
        self.conversation_started = False
        self.data = {
            "symptom_list": {},
            "disease": {},
        }
        
        self.logger.info("💬 Chat inicializado e pronto para uso")

        async def handle(self, context: List[str]) -> str:
            try:
                if not self.conversation_started:
                    self.conversation_started = True
                    current_handler_type = 'get_random_symptoms_handler'
                else:
                    current_handler_type = "router"
                user_message = context[-1] if context else ""
                
                # Notifica sobre a mensagem do usuário
                self.message_subject.notify(
                    message=user_message,
                    role="user"
                )
                
                while True:
                    if current_handler_type == "sintomas":
                        prompt_data = {
                            "symptom_list": self.data['symptom_list'],
                            "disease": self.data['disease']
                        }
                    else:
                        prompt_data = {}

                    handler = self.get_handler(
                        handler_type=current_handler_type,
                        agent_type='gemini',
                        prompt_data=prompt_data
                    )

                    response = await handler.handle(context)

                    if current_handler_type == 'get_random_symptoms_handler':
                        for key in response.payload:
                            self.data[key] = response.payload[key]
                    
                    # Notifica sobre a resposta do handler
                    if response.message:
                        self.message_subject.notify(
                            message=response.message,
                            role="assistant"
                        )
                    
                    if response.handler_type == HandlerType.FINAL:
                        return response.message
                    
                    current_handler_type = response.next_handler
                
            except Exception as e:
                raise MessageProcessingError(f"Erro ao processar mensagem: {str(e)}")

    def _get_agent(self, agent_type: str, llm_type: str, prompt_data: dict[str, object]) -> AgentInterface:
        try:
            return self.agent_factory.create_agent(
                agent_type=agent_type,
                llm_type=llm_type,
                prompt_data=prompt_data
            )
        except Exception as e:
            raise HandlerNotFoundError(f"Não foi possível obter o agente: {str(e)}")

    

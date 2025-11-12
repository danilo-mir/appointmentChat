from typing import List, Dict, Optional
from src.handlers.base_handler import Handler
from src.agents.base_agent import HandlerType
from src.registry import Registry
from src.utils.exceptions import HandlerNotFoundError, MessageProcessingError
from src.utils.logger import get_logger
from src.utils.observer import MessageSubject, LoggingObserver

class ChatController:
    """
    Controlador principal do chat, responsável por gerenciar o fluxo de mensagens
    entre handlers e manter o estado da conversa.
    
    Attributes:
        registry: Instância do Registry para criar handlers
        handlers: Dicionário de handlers ativos
        message_subject: Subject para notificação de observadores
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.registry = Registry()
        self.handlers: Dict[str, Handler] = {}
        
        # Configuração do sistema de observadores
        self.message_subject = MessageSubject()
        self.message_subject.attach(LoggingObserver(self.logger))
        
        self.logger.info("💬 Chat inicializado e pronto para uso")

    def get_handler(self, handler_type: str) -> Handler:
        """
        Obtém um handler existente ou cria um novo se necessário.
        
        Args:
            handler_type: Tipo do handler desejado
            
        Returns:
            Handler: Instância do handler solicitado
            
        Raises:
            HandlerNotFoundError: Se o tipo de handler não for válido
        """
        try:
            if handler_type not in self.handlers:
                self.handlers[handler_type] = self.registry.create_handler(handler_type)
            return self.handlers[handler_type]
        except Exception as e:
            raise HandlerNotFoundError(f"Não foi possível obter o handler: {str(e)}")

    async def process_message(self, context: List[str]) -> str:
        """
        Processa a mensagem através dos handlers até receber uma resposta final.
        
        Args:
            context: Lista de mensagens do histórico da conversa
            
        Returns:
            str: Resposta final do processamento
            
        Raises:
            MessageProcessingError: Se houver erro no processamento da mensagem
        """
        try:
            current_handler = "router"
            user_message = context[-1] if context else ""
            
            # Notifica sobre a mensagem do usuário
            self.message_subject.notify(
                message=user_message,
                role="user"
            )
            
            while True:
                handler = self.get_handler(current_handler)
                response = await handler.handle(context)
                
                # Notifica sobre a resposta do handler
                if response.message:
                    self.message_subject.notify(
                        message=response.message,
                        role="assistant"
                    )
                
                if response.handler_type == HandlerType.FINAL:
                    return response.message
                
                current_handler = response.next_handler
                
        except Exception as e:
            raise MessageProcessingError(f"Erro ao processar mensagem: {str(e)}") 
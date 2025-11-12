# src/registry.py
from typing import Dict, Type, Tuple, Optional
from src.Application.base_handler import Handler
from src.SharedKernel.AgentsConfig.base_agent import Agent, GeminiAgent
from src.SharedKernel.Messages.Exceptions import HandlerNotFoundError, AgentConfigurationError
from src.SharedKernel.Logging.Logger import get_logger

# Imports dos handlers
from src.Application.Router.RouterAgentHandler import RouterAgentHandler
from src.Application.Sintomas.SintomasAgentHandler import SintomasAgentHandler

# Imports dos prompts e configs
from src.SharedKernel.AgentsConfig.RouterAgentConfig import ROUTER_PROMPT, ROUTER_CONFIG
from src.SharedKernel.AgentsConfig.SintomasAgentConfig import SINTOMAS_PROMPT, SINTOMAS_CONFIG

class Registry:
    """
    Registro central para handlers e agents do Chat de Anamnese.
    Implementa o padrão Singleton.
    """
    
    _instance: Optional['Registry'] = None
    
    def __new__(cls) -> 'Registry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = get_logger(__name__)
        
        # Mapeamento de nomes para classes de handlers
        self.handler_types: Dict[str, Type[Handler]] = {
            "router": RouterAgentHandler,
            "sintomas": SintomasAgentHandler,
        }

        # Mapeamento de nomes para configurações de agents
        self.agent_configs: Dict[str, Tuple] = {
            "router": (ROUTER_CONFIG, ROUTER_PROMPT),
            "sintomas": (SINTOMAS_CONFIG, SINTOMAS_PROMPT),
        }
        
        self._initialized = True
        self.logger.info("Registry inicializado com sucesso")
    
    def create_handler(self, handler_type: str) -> Handler:
        """
        Cria um handler do tipo especificado com seu agent correspondente.
        """
        try:
            if handler_type not in self.handler_types:
                raise HandlerNotFoundError(f"Tipo de handler não registrado: {handler_type}")

            if handler_type not in self.agent_configs:
                raise AgentConfigurationError(f"Configuração de agent não encontrada: {handler_type}")

            config, prompt = self.agent_configs[handler_type]
            agent = GeminiAgent(config=config, system_prompt=prompt)

            handler_class = self.handler_types[handler_type]
            handler = handler_class(agent=agent)
            
            return handler
        
        except Exception as e:
            raise HandlerNotFoundError(f"Não foi possível obter o handler: {str(e)}")

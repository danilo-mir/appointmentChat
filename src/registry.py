# src/registry.py
from typing import Dict, Type, Tuple, Optional
from src.handlers.base_handler import Handler
from src.agents.base_agent import Agent, GeminiAgent
from src.utils.exceptions import HandlerNotFoundError, AgentConfigurationError
from src.utils.logger import get_logger

# Imports dos handlers
from src.handlers.router.handler import RouterHandler
from src.handlers.sintomas.handler import SintomasHandler

# Imports dos prompts e configs (placeholders)
from src.agents.router.prompt import ROUTER_PROMPT
from src.agents.router.config import ROUTER_CONFIG

from src.agents.sintomas.prompt import SINTOMAS_PROMPT
from src.agents.sintomas.config import SINTOMAS_CONFIG

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
            "router": RouterHandler,
            "sintomas": SintomasHandler,
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

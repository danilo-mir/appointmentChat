# src/registry.py
from typing import Dict, Type, Tuple, Optional
from src.Application.Abstractions.BaseHandler import Handler
from src.Application.Abstractions.BaseAgent import GeminiAgent
from src.SharedKernel.Messages.Exceptions import HandlerNotFoundError, AgentConfigurationError
from src.SharedKernel.Logging.Logger import get_logger

# Imports dos handlers
from src.Application.Router.RouterAgentHandler import RouterAgentHandler
from src.Application.Sintomas.SintomasAgentHandler import SintomasAgentHandler
from src.Application.Get_Random_Patient.GetRandomPatientHandler import GetRandomPatientHandler

# Imports das funções de configuração e prompt
from src.Application.Router.RouterAgentConfig import get_router_config, get_router_prompt
from src.Application.Sintomas.SintomasAgentConfig import get_sintomas_config, get_sintomas_prompt
from src.Application.Get_Random_Patient.GetRandomPatientConfig import get_random_patient_config, get_random_patient_prompt

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
            "get_random_patient": GetRandomPatientHandler,
        }

        # Mapeamento de nomes para funções de configuração e prompt
        # Essas funções podem receber argumentos para gerar prompts dinâmicos
        self.agent_configs: Dict[str, Tuple] = {
            "router": (get_router_config, get_router_prompt),
            "sintomas": (get_sintomas_config, get_sintomas_prompt),
            "get_random_patient": (get_random_patient_config, get_random_patient_prompt)
        }
        
        self._initialized = True
        self.logger.info("Registry inicializado com sucesso")
    
    def create_handler(self, handler_type: str, **kwargs) -> Handler:
        """
        Cria um handler do tipo especificado com seu agent correspondente.
        
        Args:
            handler_type: Nome do handler ("router", "sintomas", etc.)
            **kwargs: Argumentos opcionais para gerar prompts/configs dinâmicos
                      Ex: symptoms_list para o SINTOMAS_HANDLER
        
        Returns:
            Handler: Instância do handler criado
        """
        try:
            if handler_type not in self.handler_types:
                raise HandlerNotFoundError(f"Tipo de handler não registrado: {handler_type}")

            if handler_type not in self.agent_configs:
                raise AgentConfigurationError(f"Configuração de agent não encontrada: {handler_type}")

            config_func, prompt_func = self.agent_configs[handler_type]

            # Chama as funções passando kwargs (ex: sintomas dinâmicos)
            config = config_func(**kwargs)
            prompt = prompt_func(**kwargs)

            agent = GeminiAgent(config=config, system_prompt=prompt)

            handler_class = self.handler_types[handler_type]
            handler = handler_class(agent=agent)
            
            return handler
        
        except Exception as e:
            raise HandlerNotFoundError(f"Não foi possível criar o handler '{handler_type}': {str(e)}")

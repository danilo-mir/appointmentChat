# src/HandlerFactory.py
from typing import Dict, Type, Tuple, Optional
from src.Application.Abstractions.Handlers.HandlerInterface import Handler
from src.Application.Abstractions.Agents.AgentInterface import AgentInterface
from src.Application.Abstractions.Agents.GeminiAgent import GeminiAgent
from src.Application.Abstractions.Agents.OpenAiAgent import OpenAIAgent
from src.SharedKernel.Messages.Exceptions import HandlerNotFoundError, AgentConfigurationError, AgentTypeNotFoundError
from src.SharedKernel.Logging.Logger import get_logger

# Imports dos handlers
from src.Application.Abstractions.Handlers.RouterAgentHandler import RouterAgentHandler
from src.Application.Abstractions.Handlers.SintomasAgentHandler import SintomasAgentHandler

# Imports dos prompts e configs
from src.Application.Router.RouterAgentConfig import ROUTER_CONFIG, GET_ROUTER_PROMPT
from src.Application.Sintomas.SintomasAgentConfig import SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT

class HandlerFactory:    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Mapeamento de nomes para classes de handlers
        self.handler_types: dict[str, type[Handler]] = {
            "router": RouterAgentHandler,
            "sintomas": SintomasAgentHandler,
        }

        # Mapeamento de nomes para configurações de agents
        self.agent_configs: dict[str, Tuple[dict, callable]] = {
            "router": (ROUTER_CONFIG, GET_ROUTER_PROMPT),
            "sintomas": (SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT),
        }

        # Mapeamento de nomes para tipos de agents
        self.agent_types: dict[str, type[AgentInterface]] = {
            "gemini": GeminiAgent,
            "gpt": OpenAIAgent,
        }
        
        self.logger.info("HandlerFactory inicializado com sucesso")
    
    def create_handler(self, handler_type: str, agent_type: str, prompt_data: dict[str, object]) -> Handler:
        """
        Cria um handler do tipo especificado com seu agent correspondente.
        """
        try:
            if handler_type not in self.handler_types:
                raise HandlerNotFoundError(f"Tipo de handler não registrado: {handler_type}")

            if handler_type not in self.agent_configs:
                raise AgentConfigurationError(f"Configuração de agent não encontrada: {handler_type}")
            
            if agent_type not in self.agent_types:
                raise AgentTypeNotFoundError(f"Tipo de agente não registrado: {agent_type}")

            config, prompt_getter = self.agent_configs[handler_type]
            agent_class = self.agent_types[agent_type]

            prompt = prompt_getter(**prompt_data)
            agent = agent_class(config=config, system_prompt=prompt)

            handler_class = self.handler_types[handler_type]
            handler = handler_class(agent=agent)
            
            return handler
        
        except Exception as e:
            self.logger.exception("Erro ao criar handler")
            raise
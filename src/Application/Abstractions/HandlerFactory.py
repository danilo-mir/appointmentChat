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
from src.Application.Abstractions.Handlers.GetRandomSymptomsToolHandler import GetRandomSymptomsHandler
from src.Application.Abstractions.Handlers.FallbackAgentHandler import FallbackAgentHandler

# Imports dos prompts e configs
from src.Application.Router.RouterAgentConfig import ROUTER_CONFIG, GET_ROUTER_PROMPT
from src.Application.Sintomas.SintomasAgentConfig import SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT
from src.Application.Fallback.FallbackAgentConfig import FALLBACK_CONFIG, GET_FALLBACK_PROMPT

class HandlerFactory:    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # --- Handlers com agente ---
        self.agent_handler_types: Dict[str, Type[Handler]] = {
            "router": RouterAgentHandler,
            "sintomas": SintomasAgentHandler,
            "fallback": FallbackAgentHandler
        }

        # Configs para cada handler com agente
        self.agent_configs: Dict[str, Tuple[dict, callable]] = {
            "router": (ROUTER_CONFIG, GET_ROUTER_PROMPT),
            "sintomas": (SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT),
            "fallback": (FALLBACK_CONFIG, GET_FALLBACK_PROMPT)
        }

        # Tipos de agents disponíveis
        self.agent_types: Dict[str, Type[AgentInterface]] = {
            "gemini": GeminiAgent,
            "gpt": OpenAIAgent,
        }

        # --- Handlers que usam apenas tools ---
        self.tool_only_handlers: Dict[str, Type[Handler]] = {
            "get_random_symptoms_handler": GetRandomSymptomsHandler
        }

        self.logger.info("HandlerFactory inicializado com sucesso")

    def create_handler(self, handler_type: str, agent_type: Optional[str] = None, prompt_data: Optional[dict[str, object]] = None) -> Handler:
        try:
            # --- Caso handler seja apenas tool ---
            if handler_type in self.tool_only_handlers:
                handler_class = self.tool_only_handlers[handler_type]
                return handler_class(agent=None)

            # --- Caso handler use agente ---
            if handler_type not in self.agent_handler_types:
                raise HandlerNotFoundError(f"Tipo de handler não registrado: {handler_type}")

            if handler_type not in self.agent_configs:
                raise AgentConfigurationError(f"Configuração de agent não encontrada: {handler_type}")

            if not agent_type or agent_type not in self.agent_types:
                raise AgentTypeNotFoundError(f"Tipo de agente não registrado: {agent_type}")

            config, prompt_getter = self.agent_configs[handler_type]
            agent_class = self.agent_types[agent_type]

            prompt = prompt_getter(**(prompt_data or {}))
            agent = agent_class(config=config, system_prompt=prompt)

            handler_class = self.agent_handler_types[handler_type]
            return handler_class(agent=agent)

        except Exception as e:
            self.logger.exception("Erro ao criar handler")
            raise

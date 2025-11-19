# src/HandlerFactory.py
from typing import Dict, Type, Tuple, Optional

from src.Domain.Chatbot.Abstractions.AgentInterface import AgentInterface
from src.Domain.Interfaces.Llm.LlmInterface import LlmInterface
from src.Infrastructure.Llm.GemniLlm import GeminiLlm
from src.Infrastructure.Llm.OpenAiLlm import OpenAILlm
from src.SharedKernel.Messages.Exceptions import (
    HandlerNotFoundError,
    AgentConfigurationError,
    AgentTypeNotFoundError,
)
from src.SharedKernel.Logging.Logger import get_logger


from src.Domain.Chatbot.Agents.RouterAgent.RouterAgent import RouterAgent
from src.Domain.Chatbot.Agents.SintomasAgent.SintomasAgent import SintomasAgent
from src.Domain.Chatbot.Agents.FallBackAgent.FallbackAgent import FallbackAgent
from src.Domain.Chatbot.Agents.ConversationAgent.ConversationAgent import ConversationAgent
from src.Domain.Chatbot.Agents.FinalAgent.FinalAgent import FinalAgent


from src.Domain.Chatbot.Agents.RouterAgent.RouterAgentConfig import ROUTER_CONFIG, GET_ROUTER_PROMPT
from src.Domain.Chatbot.Agents.SintomasAgent.SintomasAgentConfig import SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT
from src.Domain.Chatbot.Agents.FallBackAgent.FallbackAgentConfig import FALLBACK_CONFIG, GET_FALLBACK_PROMPT
from src.Domain.Chatbot.Agents.ConversationAgent.ConversationAgentConfig import (
    CONVERSATION_CONFIG,
    GET_CONVERSATION_PROMPT,
)
from src.Domain.Chatbot.Agents.FinalAgent.FinalAgentConfig import (
    FINAL_CONFIG,
    GET_FINAL_PROMPT,
)


class AgentFactory:
    def __init__(self):
        self.logger = get_logger(__name__)

        # --- Agentes de alto nível (antes: handlers com agente) ---
        self.agent_classes: Dict[str, Type[AgentInterface]] = {
            "router": RouterAgent,
            "conversation": ConversationAgent,
            "sintomas": SintomasAgent,
            "final": FinalAgent,
            "fallback": FallbackAgent,
        }

        # Configs para cada agente
        self.agent_configs: Dict[str, Tuple[dict, callable]] = {
            "router": (ROUTER_CONFIG, GET_ROUTER_PROMPT),
            "conversation": (CONVERSATION_CONFIG, GET_CONVERSATION_PROMPT),
            "sintomas": (SINTOMAS_CONFIG, GET_SINTOMAS_PROMPT),
            "final": (FINAL_CONFIG, GET_FINAL_PROMPT),
            "fallback": (FALLBACK_CONFIG, GET_FALLBACK_PROMPT),
        }

        # Tipos de LLMs disponíveis (antes: agents)
        self.llm_types: Dict[str, Type[LlmInterface]] = {
            "gemini": GeminiLlm,
            "gpt": OpenAILlm,
        }

        # --- Agentes que usam apenas tools (antes: handlers only) ---
        self.tool_only_agents: Dict[str, Type[AgentInterface]] = {
        }

        self.logger.info("AgentFactory inicializado com sucesso")

    def create_agent(
        self,
        agent_type: str,
        llm_type: Optional[str] = None,
        prompt_data: Optional[dict[str, object]] = None,
    ) -> AgentInterface:
        try:
            # --- Caso agente use apenas tool ---
            if agent_type in self.tool_only_agents:
                agent_class = self.tool_only_agents[agent_type]
                return agent_class(llm=None)

            # --- Caso agente use LLM ---
            if agent_type not in self.agent_classes:
                raise HandlerNotFoundError(f"Tipo de agent não registrado: {agent_type}")

            if agent_type not in self.agent_configs:
                raise AgentConfigurationError(
                    f"Configuração de agent não encontrada: {agent_type}"
                )

            if not llm_type or llm_type not in self.llm_types:
                raise AgentTypeNotFoundError(f"Tipo de llm não registrado: {llm_type}")

            config, prompt_getter = self.agent_configs[agent_type]
            llm_class = self.llm_types[llm_type]

            prompt = prompt_getter(**(prompt_data or {}))
            llm = llm_class(config=config, system_prompt=prompt)

            agent_class = self.agent_classes[agent_type]

            return agent_class(llm=llm)

        except Exception:
            self.logger.exception("Erro ao criar agent")
            raise

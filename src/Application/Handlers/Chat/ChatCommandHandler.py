from typing import Any, List, Optional, Tuple
import random
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

from src.Infrastructure.Repositories.PatientRepositoryPstgres import PatientRepositoryPostgres
from src.Infrastructure.Repositories.PatientSymptomRepositoryPostgres import PatientSymptomRepositoryPostgres
from src.Domain.Entities.Symptom import Symptom
from src.Infrastructure.Cache.ChatMemoryStore import ChatMemoryStore


class ChatCommandHandler:
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.agent_factory = AgentFactory()
        
        # Configuração do sistema de observadores
        self.message_subject = MessageSubject()
        self.message_subject.attach(LoggingObserver(self.logger))

        # Repositórios
        self.patient_repository = PatientRepositoryPostgres()
        self.patient_symptom_repository = PatientSymptomRepositoryPostgres()
        self.chat_memory_store = ChatMemoryStore()

        # Imagino que essas variaveis NAO devam ficar no controller pq tao armazenando memoria
        # Mas funciona por enquanto
        self.conversation_started = False
        self.data = {
            "symptom_list": [],
            "disease": None,
            "conversation_history": [],
        }
        self.history_window = 20
        
        self.logger.info("💬 Chat inicializado e pronto para uso")

    async def handle(self, command: ChatCommand) -> str:
        try:
            current_agent_type = "router"

            session_id = str(command.session_id)
            message = command.message
            
            memory_snapshot = await self._ensure_session_memory(session_id)
            self._hydrate_session_state(memory_snapshot)

            memory_snapshot = await self.chat_memory_store.append_history(session_id, "user", message)
            self._hydrate_session_state(memory_snapshot)
            conversation_context = self._format_conversation_history(self.data["conversation_history"])

            # Notifica sobre a mensagem do usuário
            self.message_subject.notify(
                message=message,
                role="user"
            )
            
            while True:
                prompt_data = self._build_prompt_data(
                    agent_type=current_agent_type,
                    conversation_context=conversation_context,
                )

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
                    memory_snapshot = await self.chat_memory_store.append_history(
                        session_id,
                        "assistant",
                        response.message,
                    )
                    self._hydrate_session_state(memory_snapshot)
                    conversation_context = self._format_conversation_history(
                        self.data["conversation_history"]
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

    async def _ensure_session_memory(self, session_id: str) -> dict[str, Any]:
        """
        Garante que a sessão possua memória persistida no Redis.

        - Caso exista, retorna os dados.
        - Caso não exista, cria um novo registro com dados aleatórios.
        """
        existing_memory = await self.chat_memory_store.get_memory(session_id)
        if existing_memory:
            return existing_memory

        symptom_entities, disease = self._get_random_user_disease_data()
        symptom_list = [symptom.symptom_name for symptom in symptom_entities]

        return await self.chat_memory_store.save_memory(
            session_id=session_id,
            symptom_list=symptom_list,
            disease=disease,
        )

    def _get_random_user_disease_data(self) -> Tuple[List[Symptom], Optional[str]]:
        all_patients = self.patient_repository.list_all()
        
        if not all_patients:
            self.logger.warning("Nenhum paciente encontrado no banco de dados")
            return [], None
        
        random_patient = random.choice(all_patients)
        random_user_id = random_patient.patient_id
        
        self.logger.info(f"Usuário aleatório selecionado: {random_user_id}")
        
        symptoms = self.patient_symptom_repository.list_symptoms_for_patient(random_user_id)
        disease = random_patient.disease
        
        self.logger.info(f"Sintomas encontrados para o usuário {random_user_id}: {[symptom.symptom_name for symptom in symptoms]}")
        
        return symptoms, disease

    def _hydrate_session_state(self, memory_snapshot: Optional[dict[str, Any]]) -> None:
        if not memory_snapshot:
            return

        self.data["symptom_list"] = memory_snapshot.get("symptom_list") or []
        self.data["disease"] = memory_snapshot.get("disease")
        self.data["conversation_history"] = memory_snapshot.get("history") or []

    def _format_conversation_history(self, history: List[dict[str, Any]]) -> str:
        if not history:
            return ""

        relevant_history = history[-self.history_window :]
        formatted_messages = []
        for entry in relevant_history:
            role = (entry.get("role") or "user").upper()
            content = entry.get("message") or ""
            formatted_messages.append(f"{role}: {content}")

        return "\n".join(formatted_messages)

    def _build_prompt_data(self, agent_type: str, conversation_context: str) -> dict[str, Any]:
        prompt_data: dict[str, Any] = {
            "conversation_history": conversation_context,
        }

        if agent_type == "sintomas":
            prompt_data["symptom_list"] = self.data["symptom_list"]
            prompt_data["disease"] = self.data["disease"]

        return prompt_data

    

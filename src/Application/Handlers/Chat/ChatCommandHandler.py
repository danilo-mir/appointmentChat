from typing import Dict, List
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
from src.Infrastructure.Repositories.SymptomRepositoryPostgres import SymptomRepositoryPostgres
from src.Infrastructure.Repositories.PatientSymptomRepositoryPostgres import PatientSymptomRepositoryPostgres
from src.Domain.Entities.Symptom import Symptom


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

            session_id = command.session_id
            message = command.message

            # TODO: Checar se a session_id já existe no banco de dados
            symptom_list, disease = self._get_random_user_disease_data()
            
            self.data['symptom_list'] = [symptom.symptom_name for symptom in symptom_list]
            self.data['disease'] = disease

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

    def _get_random_user_disease_data(self) -> List[Symptom]:
        all_patients = self.patient_repository.list_all()
        
        if not all_patients:
            self.logger.warning("Nenhum paciente encontrado no banco de dados")
            return []
        
        random_patient = random.choice(all_patients)
        random_user_id = random_patient.patient_id
        
        self.logger.info(f"Usuário aleatório selecionado: {random_user_id}")
        
        symptoms = self.patient_symptom_repository.list_symptoms_for_patient(random_user_id)
        disease = random_patient.disease
        
        self.logger.info(f"Sintomas encontrados para o usuário {random_user_id}: {[symptom.symptom_name for symptom in symptoms]}")
        
        return symptoms, disease

    

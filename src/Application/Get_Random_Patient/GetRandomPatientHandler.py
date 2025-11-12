import random
from typing import List
from src.Application.Abstractions.BaseAgent import AgentResponse, HandlerType
from src.Application.Abstractions.BaseHandler import Handler
from src.SharedKernel.Logging.Logger import get_logger
from src.Infrastructure.Repositories.PatientRepository import PatientRepository
from src.Infrastructure.Repositories.PatientSymptomRepository import PatientSymptomRepository
from src.Infrastructure.Repositories.SymptomRepository import SymptomRepository

class GetRandomPatientHandler(Handler):
    """
    Handler que retorna um paciente aleatório do repositório ou lista
    de pacientes e direciona o fluxo de volta para o Router.
    """

    def __init__(self, agent):
        """
        :param agent: referência ao agente principal
        :param patient_repository: objeto que permite acessar os pacientes
        """
        super().__init__(agent)
        self.logger = get_logger(__name__)

        self.patient_repository=PatientRepository()
        self.patient_symptom_repository = PatientSymptomRepository()

    async def handle(self, context: List[str]) -> AgentResponse:
        try:
            all_patients = self.patient_repository.list_all()

            if not all_patients:
                self.logger.warning("Nenhum paciente encontrado.")
                selected_patient = None
            else:
                selected_patient = random.choice(all_patients)
                random_id = selected_patient.patient_id  
              
            symptoms = self.patient_symptom_repository.list_symptoms_for_patient(random_id)
            symptom_names = [s.symptom_name for s in symptoms]
            
            # Armazenar ou logar o paciente selecionado
            self.logger.info(f"Paciente selecionado: {selected_patient}")

            # Sempre retorna para o Router
            return AgentResponse(
                handler_type=HandlerType.NEXT,
                next_handler="router",
                message=" ".join(symptom_names)
            )

        except Exception as e:
            self.logger.error(f"Erro no GetRandomPatientHandler: {str(e)}")
            return AgentResponse(
                handler_type=HandlerType.NEXT,
                next_handler="router",
                message="Erro ao selecionar paciente"
            )

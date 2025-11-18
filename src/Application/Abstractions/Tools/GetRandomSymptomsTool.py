import random
from typing import Any
from src.Application.Abstractions.Tools.ToolInterface import ToolInterface, ToolResponse
from src.Infrastructure.Repositories.PatientRepository import PatientRepository
from src.Infrastructure.Repositories.PatientSymptomRepository import PatientSymptomRepository

class GetRandomSymptomsTool(ToolInterface):
    def __init__(self):
        super().__init__()
        self.patient_repository = PatientRepository()
        self.patient_symptom_repository = PatientSymptomRepository()

    async def execute(self, input_data: Any = None) -> ToolResponse:
        try:
            all_patients = self.patient_repository.list_all()

            selected_patient = random.choice(all_patients)
            patient_id = selected_patient.patient_id
            disease = selected_patient.disease

            symptoms = self.patient_symptom_repository.list_symptoms_for_patient(patient_id)
            symptom_names = [s.symptom_name for s in symptoms]

            return ToolResponse(payload={
                "symptom_list": symptom_names,
                "disease": disease,
            })

        except Exception as e:
            return ToolResponse(payload={"symptom_list": [], "error": str(e)})

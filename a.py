import random
from uuid import UUID

from src.Infrastructure.Repositories.PatientRepository import PatientRepository
from src.Infrastructure.Repositories.PatientSymptomRepository import PatientSymptomRepository

patient_repository=PatientRepository()
patient_symptom_repository = PatientSymptomRepository()

all_patients = patient_repository.list_all()
patient_ids = [p.patient_id for p in all_patients]
random_id = random.choice(patient_ids)

symptoms = patient_symptom_repository.list_symptoms_for_patient(random_id)
symptom_names = [s.symptom_name for s in symptoms]

print(symptom_names)
from typing import List
from uuid import UUID

from src.Domain.Entities.Patient import Patient
from src.Domain.Entities.Symptom import Symptom
from src.Infrastructure.Database.Connection import get_connection
from src.Domain.Interfaces.Repositories.PatientSymptomRepository import PatientSymptomRepository


class PatientSymptomRepositoryPostgres(PatientSymptomRepository):
    def __init__(self):
        self.connection = get_connection()

    def list_symptoms_for_patient(self, patient_id: UUID) -> List[Symptom]:
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "symptom_id", "symptom_name" FROM symptoms WHERE "patient_id" = %s',
                    (str(patient_id),),
                )
                rows = cur.fetchall()
                return [Symptom(symptom_id=r[0], symptom_name=r[1]) for r in rows]

    def list_patients_for_symptom(self, symptom_id: UUID) -> List[Patient]:
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "patient_id", "disease" FROM patients WHERE "symptom_id" = %s',
                    (str(symptom_id),),
                )
                rows = cur.fetchall()
                return [Patient(patient_id=r[0], disease=r[1]) for r in rows]



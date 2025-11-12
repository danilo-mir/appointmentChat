from typing import List
from uuid import UUID

from src.Domain.Entities.Patient import Patient
from src.Domain.Entities.Symptom import Symptom
from src.Infrastructure.Database.Connection import get_connection


class PatientSymptomRepository:
    def list_symptoms_for_patient(self, patient_id: UUID) -> List[Symptom]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s."symptom_id", s."symptom_name"
                    FROM patient_symptoms ps
                    JOIN symptoms s ON s."symptom_id" = ps.symptom_id
                    WHERE ps.patient_id = %s
                    ORDER BY s."symptom_name"
                    """,
                    (str(patient_id),),
                )
                rows = cur.fetchall()
                return [Symptom(symptom_id=r[0], symptom_name=r[1]) for r in rows]

    def list_patients_for_symptom(self, symptom_id: UUID) -> List[Patient]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p."patientID", p.disease
                    FROM patient_symptoms ps
                    JOIN patients p ON p."patientID" = ps.patient_id
                    WHERE ps.symptom_id = %s
                    ORDER BY p."patientID"
                    """,
                    (str(symptom_id),),
                )
                rows = cur.fetchall()
                return [Patient(patient_id=r[0], disease=r[1]) for r in rows]



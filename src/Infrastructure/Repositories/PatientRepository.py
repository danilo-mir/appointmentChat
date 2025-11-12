from typing import List, Optional
from uuid import UUID

from src.Domain.Entities.Patient import Patient
from src.Infrastructure.Database.Connection import get_connection


class PatientRepository:
    def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "patientID", disease FROM patients WHERE "patientID" = %s',
                    (str(patient_id),),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Patient(patient_id=row[0], disease=row[1])

    def list_all(self) -> List[Patient]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT "patientID", disease FROM patients ORDER BY "patientID"')
                rows = cur.fetchall()
                return [Patient(patient_id=r[0], disease=r[1]) for r in rows]



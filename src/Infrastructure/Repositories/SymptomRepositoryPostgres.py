from typing import List, Optional
from uuid import UUID

from src.Domain.Entities.Symptom import Symptom
from src.Infrastructure.Database.Connection import get_connection
from src.Domain.Interfaces.Repositories.SymptomRepository import SymptomRepository


class SymptomRepositoryPostgres(SymptomRepository):
    def __init__(self):
        self.connection = get_connection()

    def get_by_id(self, symptom_id: UUID) -> Optional[Symptom]:
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "symptomID", "symptomNAME" FROM symptoms WHERE "symptomID" = %s',
                    (str(symptom_id),),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Symptom(symptom_id=row[0], symptom_name=row[1])

    def get_by_name(self, name: str) -> Optional[Symptom]:
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "symptomID", "symptomNAME" FROM symptoms WHERE "symptomNAME" ILIKE %s',
                    (name,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Symptom(symptom_id=row[0], symptom_name=row[1])

    def list_all(self) -> List[Symptom]:
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT "symptomID", "symptomNAME" FROM symptoms ORDER BY "symptomNAME"')
                rows = cur.fetchall()
                return [Symptom(symptom_id=r[0], symptom_name=r[1]) for r in rows]



from uuid import UUID
from typing import Optional


class Patient:
    patient_id: UUID
    disease: Optional[str]



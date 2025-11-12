from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass(frozen=True)
class Patient:
    patient_id: UUID
    disease: Optional[str]



from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Symptom:
    symptom_id: UUID
    symptom_name: str



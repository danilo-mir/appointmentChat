from typing import Optional

from src.Infrastructure.Repositories.PatientRepository import PatientRepository
from src.Infrastructure.Repositories.SymptomRepository import SymptomRepository
from src.Infrastructure.Repositories.PatientSymptomRepository import PatientSymptomRepository

_patient_repo: Optional[PatientRepository] = None
_symptom_repo: Optional[SymptomRepository] = None
_patient_symptom_repo: Optional[PatientSymptomRepository] = None


def get_patient_repository() -> PatientRepository:
    global _patient_repo
    if _patient_repo is None:
        _patient_repo = PatientRepository()
    return _patient_repo


def get_symptom_repository() -> SymptomRepository:
    global _symptom_repo
    if _symptom_repo is None:
        _symptom_repo = SymptomRepository()
    return _symptom_repo


def get_patient_symptom_repository() -> PatientSymptomRepository:
    global _patient_symptom_repo
    if _patient_symptom_repo is None:
        _patient_symptom_repo = PatientSymptomRepository()
    return _patient_symptom_repo



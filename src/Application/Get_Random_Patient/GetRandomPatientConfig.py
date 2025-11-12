# src/Application/Get_Random_Patient/GetRandomPatientConfig.py

from src.Application.Abstractions.BaseAgent import AgentConfig

def get_random_patient_config(**kwargs) -> AgentConfig:
    """
    Dummy de configuração de agente para o handler GetRandomPatient.
    Esse handler não utiliza IA, mas o Registry exige que exista uma função de configuração.
    """
    return AgentConfig(
        model="none",
        temperature=0.0,
        max_tokens=1
    )

def get_random_patient_prompt(**kwargs) -> str:
    """
    Dummy de prompt para o handler GetRandomPatient.
    Esse handler não utiliza prompts, portanto retorna uma string vazia.
    """
    return "DUMMY"

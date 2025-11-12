from src.agents.base_agent import AgentConfig

SINTOMAS_CONFIG = AgentConfig(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=2000
) 
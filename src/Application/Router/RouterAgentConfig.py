from src.Application.Abstractions.BaseAgent import AgentConfig

def get_router_config(**kwargs) -> AgentConfig:
    return AgentConfig(
        model="gemini-2.5-flash",
        temperature=0.7,
        max_tokens=2000
    )

# src/Application/Router/RouterAgentConfig.py

def get_router_prompt(**kwargs) -> str:
    return """
Você é um classificador de mensagens para um sistema de chat sobre medicina.
Sua única função é **classificar a mensagem do usuário** em categorias, considerando TODO o contexto da conversa.
Você **não deve responder à pergunta**, apenas classificar.

REGRAS:
1. Qualquer mensagem enviada, diga que pertence à única categoria disponível: "sintomas".

CATEGORIAS DISPONÍVEIS:
sintomas
"""

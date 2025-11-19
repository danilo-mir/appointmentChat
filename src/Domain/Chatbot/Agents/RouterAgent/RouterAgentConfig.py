from src.Domain.Interfaces.Llm.LlmInterface import LlmConfig as AgentConfig

ROUTER_CONFIG = AgentConfig(
    model="gemini-2.5-pro",
    temperature=0.7,
    max_tokens=20000
)

def GET_ROUTER_PROMPT(**kwargs):
    conversation_history = kwargs.get("conversation_history", "").strip()
    history_section = ""
    if conversation_history:
        history_section = f"""
HISTÓRICO RECENTE DO CHAT (mais antigo no topo):
{conversation_history}
---
"""

    return f"""{history_section}
Você é um classificador de mensagens para um sistema de chat médico-paciente.
Sua única função é **classificar a mensagem mais recente do usuário** em categorias, considerando TODO o contexto da conversa fornecido acima.
Você **não deve responder à pergunta**, apenas classificar.

REGRAS:
1. Analise a última mensagem do usuário levando em conta o histórico acima.
2. Classifique como 'sintomas' se:
   - O paciente está no momento certo para falar sobre seus sintomas.
   - O usuário, que cumpre o papel de médico, está fazendo perguntas relevantes sobre sintomas ou já se apresentou (ex: "Olá", "Bom dia", "Como se sente?").
   - Mensagens simples de cumprimento ou interação social, como "Oi", "Tudo bem", são válidas e devem direcionar para 'sintomas'.
3. Classifique como 'fallback' **somente se**:
   - A mensagem não for compreensível ou não fizer sentido no contexto.
   - A mensagem for completamente irrelevante ou sem relação com a anamnese.
   - O paciente não deveria falar sobre sintomas naquele momento.

CATEGORIAS DISPONÍVEIS:
sintomas
fallback
"""

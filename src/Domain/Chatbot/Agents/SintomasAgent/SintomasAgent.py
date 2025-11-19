from typing import List
from src.Domain.Chatbot.Abstractions.AgentInterface import AgentInterface, AgentType, AgentResponse
from src.SharedKernel.Logging.Logger import get_logger
from src.Domain.Interfaces.Llm.LlmInterface import LlmConfig
from src.Infrastructure.Llm.GemniLlm import GeminiLlm

# Configuração para o agente de sumarização
SUMMARY_CONFIG = LlmConfig(
    model="gemini-2.5-flash",
    temperature=0.3,
    max_tokens=20000
)

SUMMARY_PROMPT = """
Você é um assistente que resume conversas médico-paciente.
Dado o histórico abaixo, produza um resumo curto e claro com o essencial da conversa até o momento.
Não perca informações médicas relevantes.
Histórico:
{conversation}
Resumo:
"""

class SintomasAgent(AgentInterface):
    """
    Handler responsável por processar mensagens relacionadas aos sintomas do paciente
    durante a anamnese, incluindo histórico de perguntas e respostas sobre sintomas.
    """

    def __init__(self, llm):
        super().__init__(llm)
        self.logger = get_logger(__name__)
        self.memory_summary = ""  # 🧠 Armazena resumo da conversa
        self.max_context_length = 50  # Quantas mensagens antes de resumir novamente

        # Cria um agente de sumarização separado
        self.summary_llm = GeminiLlm(SUMMARY_CONFIG, SUMMARY_PROMPT)

    # async def summarize_context(self, context: List[str]) -> str:
    #     """Usa o modelo Gemini para resumir o histórico de conversa."""
    #     try:
    #         joined = "\n".join(context)
    #         prompt = SUMMARY_PROMPT.format(conversation=joined)
    #         response = await self.summary_agent.process([prompt])
    #         summary = response.message.strip()
    #         self.logger.info(f"Resumo atualizado: {summary}")
    #         return summary
    #     except Exception as e:
    #         self.logger.error(f"Erro ao resumir contexto: {str(e)}")
    #         # Fallback: apenas pegar as últimas mensagens
    #         return " ".join(context[-2:])

    async def generate_response(self, context: List[str]) -> AgentResponse:
        """
        Processa a mensagem considerando o contexto da conversa e o histórico
        de perguntas e respostas sobre sintomas do paciente.
        Retorna sempre um AgentResponse.
        """
        try:
            # --- Step 1: combinar memória + contexto atual ---
            working_context = []
            if self.memory_summary:
                working_context.append(f"[Resumo anterior da conversa: {self.memory_summary}]")
            working_context.extend(context)

            # --- Step 2: Processar com o agente principal ---
            agent_response = await self.llm.process(working_context)

            # --- Step 3: Decidir se deve resumir ---
            if len(context) >= self.max_context_length:
                all_text = []
                if self.memory_summary:
                    all_text.append(self.memory_summary)
                all_text.extend(context)
                self.memory_summary = await self.summarize_context(all_text)

                # Limpar contexto para evitar crescimento infinito
                context.clear()
                context.append(f"[Resumo atualizado: {self.memory_summary}]")

            self.logger.info(f"Processada mensagem sobre sintomas: {context[-1]}")

            # --- Step 4: Retornar como AgentResponse ---
            return AgentResponse(
                agent_type=AgentType.FINAL,
                message=agent_response.message,
                next_agent="sintomas"  # ou outro agente se necessário
            )

        except Exception as e:
            self.logger.error(f"Erro no SintomasAgent: {str(e)}")
            return AgentResponse(
                agent_type=AgentType.FINAL,
                message="Desculpe, ocorreu um erro ao processar sua mensagem.",
                next_agent=None
            )
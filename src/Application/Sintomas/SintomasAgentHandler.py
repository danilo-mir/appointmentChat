from typing import List
from src.Application.Abstractions.BaseAgent import AgentResponse, HandlerType
from src.Application.Abstractions.BaseHandler import Handler
from src.SharedKernel.Logging.Logger import get_logger
from src.Application.Abstractions.BaseAgent import AgentConfig
from src.Application.Abstractions.BaseAgent import GeminiAgent

# Config for summarization agent (can reuse gemini-2.5-flash)
SUMMARY_CONFIG = AgentConfig(
    model="gemini-2.5-flash",
    temperature=0.3,
    max_tokens=500
)

SUMMARY_PROMPT = """
Você é um assistente que resume conversas médico-paciente.
Dado o histórico abaixo, produza um resumo curto e claro com o essencial da conversa até o momento.
Não perca informações médicas relevantes.
Histórico:
{conversation}
Resumo:
"""

class SintomasAgentHandler(Handler):
    """
    Handler responsável por processar mensagens relacionadas aos sintomas do paciente
    durante a anamnese, incluindo histórico de perguntas e respostas sobre sintomas.
    """
    
    def __init__(self, agent):
        super().__init__(agent)
        self.logger = get_logger(__name__)
        self.memory_summary = ""  # 🧠 store summarized memory
        self.max_context_length = 50  # how many turns before summarizing again

        # Create a summarization agent
        self.summary_agent = GeminiAgent(SUMMARY_CONFIG, SUMMARY_PROMPT)
        
    async def summarize_context(self, context: List[str]) -> str:
        """Usa o modelo Gemini para resumir o histórico de conversa."""
        try:
            joined = "\n".join(context)
            prompt = SUMMARY_PROMPT.format(conversation=joined)
            response = await self.summary_agent.process([prompt])
            summary = response.message.strip()
            self.logger.info(f"Resumo atualizado: {summary}")
            return summary
        except Exception as e:
            self.logger.error(f"Erro ao resumir contexto: {str(e)}")
            # Fallback: just truncate if summarization fails
            return " ".join(context[-2:])
        
    async def handle(self, context: List[str]) -> AgentResponse:
        """
        Processa a mensagem considerando o contexto da conversa e o histórico
        de perguntas e respostas sobre sintomas do paciente.
        """
        try:
            # --- Step 1: combine memory + new user context ---
            working_context = []
            if self.memory_summary:
                working_context.append(f"[Resumo anterior da conversa: {self.memory_summary}]")
            
            # Append the latest messages
            working_context.extend(context)

            # --- Step 2: Process with the main agent ---
            response = await self.agent.process(working_context)

            # --- Step 3: Decide if we should summarize ---
            if len(context) >= self.max_context_length:
                # Summarize both old memory + current conversation
                all_text = []
                if self.memory_summary:
                    all_text.append(self.memory_summary)
                all_text.extend(context)
                self.memory_summary = await self.summarize_context(all_text)
                # Clear context to avoid infinite growth
                context.clear()
                context.append(f"[Resumo atualizado: {self.memory_summary}]")

            # --- Step 4: Log and return ---
            self.logger.info(
                f"Processada mensagem sobre sintomas do paciente: {context[-1]}"
            )
            return response
            
        except Exception as e:
            self.logger.error(f"Erro no SintomasHandler: {str(e)}")
            return AgentResponse(
                handler_type=HandlerType.FINAL,
                message="Desculpe, ocorreu um erro ao processar sua mensagem."
            )

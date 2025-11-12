from typing import List
from src.Application.Abstractions.BaseAgent import AgentResponse, HandlerType
from src.Application.Abstractions.BaseHandler import Handler
from src.SharedKernel.Logging.Logger import get_logger



class SintomasAgentHandler(Handler):
    """
    Handler responsável por processar mensagens relacionadas aos sintomas do paciente
    durante a anamnese, incluindo histórico de perguntas e respostas sobre sintomas.
    """
    
    def __init__(self, agent):
        super().__init__(agent)
        self.logger = get_logger(__name__)
        
    async def handle(self, context: List[str]) -> AgentResponse:
        """
        Processa a mensagem considerando o contexto da conversa e o histórico
        de perguntas e respostas sobre sintomas do paciente.
        """
        try:
            # Processa a mensagem com o agente
            response = await self.agent.process(context)
            
            # Registra a resposta para debug
            self.logger.info(
                f"Processada mensagem sobre sintomas do paciente: {context[-1]}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro no SintomasHandler: {str(e)}")
            return AgentResponse(
                handler_type=HandlerType.FINAL,
                message="Desculpe, ocorreu um erro ao processar sua mensagem sobre sintomas. "
                        "Pode reformular ou detalhar melhor os sintomas?"
            )

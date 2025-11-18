# backend/main.py
from typing import List, Optional
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.Controllers.ChatController import ChatController
from src.SharedKernel.Messages.Exceptions import POOChatException

# Models para API
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    content: str
    error: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.controller = ChatController()
    print("✅ ChatController instanciado e backend pronto.")
    yield  # <-- aqui o app fica rodando
    print("🛑 Encerrando o backend...")

app = FastAPI(title="POO Chat Backend", lifespan=lifespan)

# Permita chamadas do Streamlit (ajuste origem em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # URL     do Streamlit em dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI
from fastapi.responses import JSONResponse

@app.get("/")
async def root():
    return JSONResponse({"status": "ok", "message": "Backend do Appointment Chat está rodando 🚀"})

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, request: Request):
    """
    Recebe uma lista de mensagens (histórico), passa para o controller e retorna a resposta.
    O controller é responsável por processar o contexto.
    """
    controller: ChatController = request.app.state.controller
    # Extrair apenas o conteúdo — adapte se o controller precisar do papel (role).
    messages_content = [m.content for m in req.messages]

    try:
        response = await controller.process_message(messages_content)
        return ChatResponse(content=response)
    except POOChatException as e:
        # Erro de domínio: retorne mensagem clara
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erro inesperado
        raise HTTPException(status_code=500, detail="Erro interno do servidor: " + str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.Api.chatController import router as chat_router


app = FastAPI(
    title="Appointment Chat API",
    version="0.1.0",
    description="API de chat para agendamentos",
)

# Configuração de CORS
# Em produção, troque ["*"] pelos domínios específicos do seu front-end,
# por exemplo: ["https://meu-front.com", "https://app.meu-front.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Endpoint simples de healthcheck para verificar se a API está de pé.
    """
    return {"status": "ok"}



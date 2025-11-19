from fastapi import FastAPI

from src.Api.chatController import router as chat_router


app = FastAPI(
    title="Appointment Chat API",
    version="0.1.0",
    description="API de chat para agendamentos",
)


app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Endpoint simples de healthcheck para verificar se a API está de pé.
    """
    return {"status": "ok"}



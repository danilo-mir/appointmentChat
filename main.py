import streamlit as st
import requests
import asyncio
from src.SharedKernel.Logging.Logger import get_logger

BACKEND_URL = "http://localhost:8000/chat"

# Configuração do logger
logger = get_logger(__name__)

# CSS personalizado
st.markdown("""
<style>
    /* Reset do Streamlit */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Container das mensagens */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        padding-bottom: 6rem;
        height: calc(100vh - 120px);
        overflow-y: auto;
    }
    
    /* Container do input */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #262730;
        border-top: 1px solid #0E1117;
        padding: 1rem;
        z-index: 1000;
    }
    
    .input-container > div {
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Mensagens do chat */
    .stChatMessage {
        padding: 1rem !important;
        border-radius: 15px !important;
        margin-bottom: 1rem !important;
        animation: fadeIn 0.3s ease-in !important;
    }
    
    /* Animação de fade in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Indicador de digitação */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 10px;
        background: #f0f2f6;
        border-radius: 10px;
        width: fit-content;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #6c757d;
        border-radius: 50%;
        animation: typingAnimation 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingAnimation {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
</style>

<script>
    // Script para manter o scroll sempre no final
    const observer = new MutationObserver((mutations) => {
        const chatContainer = document.querySelector('.main');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
</script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_typing_indicator():
    """Exibe o indicador de digitação."""
    st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    """, unsafe_allow_html=True)


def send_message_to_backend(messages):
    """
    Envia a lista de mensagens para o backend FastAPI e retorna a resposta.
    """
    payload = {
        "messages": [
            {"role": "user", "content": msg}
            for msg in messages
        ]
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["content"]
    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar ao backend: {e}"

def main():
    """Função principal da aplicação."""
    try:
        st.title("Assistente de POO 🎓")
        
        # Inicializa o estado da sessão
        initialize_session_state()
        
        # Container para as mensagens (com scroll)
        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Exibe mensagens anteriores
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Container fixo para o input
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Input do usuário
        if prompt := st.chat_input("Digite sua mensagem...", key="chat_input"):
            # Adiciona mensagem do usuário ao histórico e exibe
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Reexibe todas as mensagens anteriores para garantir ordem correta
            st.rerun()

        # Se temos uma nova mensagem do usuário para processar
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            # Mostra o indicador de digitação
            with st.chat_message("assistant"):
                typing_placeholder = st.empty()
                typing_placeholder.markdown("""
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                """, unsafe_allow_html=True)
            
            try:
                # Extrai apenas o conteúdo das mensagens para o contexto
                context = [msg["content"] for msg in st.session_state.messages]
                
                # Processa a mensagem com o contexto
                response = send_message_to_backend(context)

                # Adiciona a resposta do backend ao histórico
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Reexibe todas as mensagens com a nova resposta
                st.rerun()
                
            except Exception as e:
                error_msg = f"Ocorreu um erro: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error("Ocorreu um erro na aplicação. Por favor, recarregue a página.")

if __name__ == "__main__":
    main() 
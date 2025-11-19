# Appointment Chat

Backend em FastAPI para orquestrar um chatbot que simula pacientes fictícios e apoia alunos de medicina no treinamento de diagnóstico. O serviço combina agentes especialistas, memória de conversa em Redis, dados clínicos em PostgreSQL e provedores LLM pluggáveis (OpenAI ou Gemini) para manter diálogos consistentes e cada vez mais próximos de um encontro clínico real.

## Visão geral
- **Objetivo**: permitir que o aluno (papel de médico) converse com um paciente virtual com sintomas coerentes, avaliando hipóteses diagnósticas e conduzindo o atendimento.
- **Domínio principal**: pacientes, sintomas e históricos armazenados em banco; LLMs guiam a persona do paciente e os agentes que definem o fluxo da conversa.
- **Stack**: FastAPI + Uvicorn, PostgreSQL, Redis, OpenAI/Gemini, Pydantic v2, psycopg_pool.

## Principais funcionalidades
- Seleção automática de um paciente/sintomatologia aleatória para cada sessão.
- Pipeline multiagente (`router`, `conversation`, `sintomas`, `final`, `fallback`) com prompts específicos.
- Memória curta/longa em Redis (`ChatMemoryStore`) para garantir coerência durante toda a sessão.
- Observabilidade básica via Observer pattern e health check dedicado.
- Scripts de carga em `tests/` para validar throughput e estabilidade.

## Arquitetura em camadas
- `src/Api`: roteadores FastAPI (ex.: `chatController`) e validação HTTP.
- `src/Application`: handlers de caso de uso (ex.: `ChatCommandHandler`) que orquestram agentes, memória e repositórios.
- `src/Domain`: entidades, agentes, contratos (`AgentInterface`, `LlmInterface`) e fábricas.
- `src/Infrastructure`: integrações externas (LLM providers, PostgreSQL, Redis).
- `src/SharedKernel`: logging, exceções e observadores reutilizáveis.

## Requisitos
- Python 3.11 ou superior.
- PostgreSQL 14+ com as tabelas `patients`, `patient_symptoms`, `symptoms`.
- Redis 7+ para armazenamento de contexto.
- Chaves de API válidas para pelo menos um provedor LLM suportado (`OPENAI_API_KEY` ou `GEMINI_API_KEY`).
- `pip` atualizado e acesso à internet para instalar dependências.

## Configuração e execução local
1. **Clonar** o repositório  
   ```bash
   git clone https://github.com/<org>/appointmentChat.git
   cd appointmentChat
   ```
2. **Criar ambiente virtual**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   ```
3. **Instalar dependências** (usa `pyproject.toml`)  
   ```bash
   pip install -e .
   ```
4. **Configurar o `.env`** na raiz (ver seção abaixo).
5. **Provisionar dependências locais**: siga as instruções das seções *PostgreSQL local* e *Redis local* (Docker, serviço nativo ou Render). Popular o banco com pacientes e sintomas antes de iniciar as conversas.
6. **Executar a API**: `uvicorn app:app --reload --port 8000` (detalhado em *Como executar a API*). Recarregue o Swagger em `http://localhost:8000/docs`.

> Dica: use `python -m pip install --upgrade pip` e `pip cache purge` se tiver problemas de dependência.

## Variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/appointment_chat
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
# Opcional para testes de carga
CHAT_API_URL=http://localhost:8000/chat/chat
```

- `DATABASE_URL`: obrigatório; o pool PostgreSQL não sobe sem ele.
- `REDIS_URL`: opcional em dev (fallback para `redis://localhost:6379/0`).
- `OPENAI_API_KEY` / `GEMINI_API_KEY`: defina ao menos uma conforme o tipo de LLM solicitado pelo `AgentFactory`.
- `CHAT_API_URL`: usado apenas pelos scripts em `tests/`.

## Banco de dados e cache
### PostgreSQL local
- O projeto usa `psycopg_pool`; recomenda-se uma instância 14+.
- Exemplo com Docker:
  ```bash
  docker run --name appointment-postgres \
    -e POSTGRES_USER=app \
    -e POSTGRES_PASSWORD=app \
    -e POSTGRES_DB=appointment_chat \
    -p 5432:5432 -d postgres:14
  ```
- Após subir, exporte `DATABASE_URL=postgresql://app:app@localhost:5432/appointment_chat` e crie/popule as tabelas `patients`, `patient_symptoms`, `symptoms` com registros coerentes (UUIDs).

### Redis local
- Necessário para persistir memória de conversa (`ChatMemoryStore`).
- Suba via Docker:
  ```bash
  docker run --name appointment-redis -p 6379:6379 -d redis:7-alpine
  ```
- Teste com `redis-cli -h localhost ping` (esperado `PONG`).
- Ajuste `REDIS_URL` se usar outra porta/host ou um serviço gerenciado.

## Como executar a API
```bash
uvicorn app:app --reload --port 8000
```
Endpoints relevantes:
- `GET /health` – verifica se a API está viva.
- `POST /chat/chat` – corpo `{"session_id": "<uuid>", "message": "texto do médico"}`. Retorna `{"message": "resposta do paciente virtual"}`.

A API fica disponível em `http://localhost:8000` por padrão.

## Ambiente publicado (Render)
- Toda a stack (frontend, backend FastAPI, PostgreSQL e Redis) está deployada no Render.
- **Frontend** (interface do aluno/médico): https://appointmentchat-web.onrender.com  
- **Backend** (API FastAPI + Swagger): https://appointmentchat.onrender.com — use `https://appointmentchat.onrender.com/docs` para a documentação interativa e `https://appointmentchat.onrender.com/chat/chat` para o endpoint principal.
- Os serviços de banco e cache rodam como *private services* dentro do Render e expõem as URLs já configuradas via `DATABASE_URL` e `REDIS_URL`. Para depuração, utilize `Render Dashboard > Logs` ou acione o health check `https://appointmentchat.onrender.com/health`.

## Documentação da API
- **Swagger-like (FastAPI)**: `http://localhost:8000/docs`
- **Redoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

Use o Swagger (`/docs`) para testar rapidamente o fluxo de chat enviando `session_id` (UUID v4) e mensagens sequenciais.

## Build do pacote
O projeto usa build backend `setuptools`. Para gerar `wheel`/`sdist`:

```bash
python -m pip install --upgrade build
python -m build
```

Os artefatos são criados em `dist/`. Para instalar o pacote resultante:

```bash
pip install dist/appointment_chat-0.1.0-py3-none-any.whl
```

## Scripts e testes auxiliares
- `tests/many_requests.py`: stress test que dispara múltiplas mensagens simulando médicos. Ajuste `CHAT_API_URL` ou use `--base-url`.  
  ```bash
  python tests/many_requests.py --total 30 --pause 0.2
  ```
- `tests/disease_disclosure_probe.py` / `tests/extreme_messages.py`: variações de cenários para validar limites de persona.

## Estrutura resumida
```
app.py                       # ponto de entrada FastAPI
src/
  Api/                       # controladores HTTP
  Application/Handlers/      # casos de uso
  Domain/                    # agentes, entidades e factories
  Infrastructure/            # integrações (DB, Redis, LLM)
  SharedKernel/              # logging, observer, exceptions
tests/                       # scripts utilitários
```



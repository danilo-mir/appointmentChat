import os
from pathlib import Path
from dotenv import load_dotenv


def get_database_dsn() -> str:
    """
    Retorna a connection string (DSN) exclusivamente do arquivo .env
    localizado no mesmo nível da pasta 'src' (raiz do projeto).
    
    Espera a variável: DATABASE_URL
    Exemplo:
      DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
    """
    # Caminho: .../src/Infrastructure/Database/Config.py -> subir até 'src', depois pegar o pai (raiz)
    src_dir = Path(__file__).resolve().parents[2]
    project_root = src_dir.parent
    env_path = project_root / ".env"

    # Carrega exclusivamente do .env na raiz do projeto
    if not env_path.exists():
        raise RuntimeError(f"Arquivo .env não encontrado em: {env_path}")
    load_dotenv(dotenv_path=env_path, override=False)

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Variável DATABASE_URL não definida no .env")
    return dsn
import os
from pathlib import Path
from dotenv import load_dotenv


def get_database_dsn() -> str:
    """
    Retorna a connection string (DSN) exclusivamente do arquivo .env
    localizado no mesmo nível da pasta 'src' (raiz do projeto).
    
    Espera a variável: DATABASE_URL
    Exemplo:
      DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
    """
    # Caminho: .../src/Infrastructure/Database/Config.py -> subir até 'src', depois pegar o pai (raiz)
    src_dir = Path(__file__).resolve().parents[2]
    project_root = src_dir.parent
    env_path = project_root / ".env"

    # Carrega exclusivamente do .env na raiz do projeto
    if not env_path.exists():
        raise RuntimeError(f"Arquivo .env não encontrado em: {env_path}")
    load_dotenv(dotenv_path=env_path, override=False)

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Variável DATABASE_URL não definida no .env")
    return dsn



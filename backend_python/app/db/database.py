"""
Configuração do banco de dados SQLite com SQLAlchemy.
Banco simples para armazenar campanhas e leads durante a fase de desenvolvimento.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Banco local SQLite — arquivo na raiz do backend
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database.sqlite")
DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessário para SQLite com FastAPI async
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency FastAPI para injetar sessão do banco nas rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas no banco (chamado no startup do servidor)."""
    from app.db import models  # noqa: F401 — importar para registrar os modelos
    Base.metadata.create_all(bind=engine)

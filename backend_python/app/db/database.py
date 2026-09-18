import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass


def _get_sqlite_engine():
    """Retorna o engine para o SQLite local."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "database.sqlite")
    sqlite_url = f"sqlite:///{os.path.abspath(db_path)}"
    return create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )


# Lê DATABASE_URL das configurações
db_url = os.getenv("DATABASE_URL", "").strip()

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Só tenta conectar ao PostgreSQL se houver uma URL válida e não for placeholder genérico
if db_url.startswith("postgresql://") and "user:password" not in db_url:
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível configurar PostgreSQL ({e}). Usando SQLite local.")
        engine = _get_sqlite_engine()
else:
    engine = _get_sqlite_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency FastAPI para injetar sessão do banco nas rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas no banco com fallback automático caso o Postgres remoto/local falhe."""
    global engine, SessionLocal
    from app.db import models  # noqa: F401 — importar para registrar os modelos

    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            from sqlalchemy import text
            try:
                conn.execute(text("ALTER TABLE leads ADD COLUMN instagram_candidates TEXT"))
            except Exception:
                pass
    except Exception as err:
        logger.warning(f"⚠️ Falha ao conectar ao banco principal ({err}). Alternando automaticamente para SQLite local...")
        engine = _get_sqlite_engine()
        SessionLocal.configure(bind=engine)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            from sqlalchemy import text
            try:
                conn.execute(text("ALTER TABLE leads ADD COLUMN instagram_candidates TEXT"))
            except Exception:
                pass
        logger.info("✅ Banco SQLite local inicializado com sucesso.")

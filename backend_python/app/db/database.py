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


def _apply_migrations(target_engine):
    """Aplica migrações incrementais de forma segura para SQLite e PostgreSQL."""
    from sqlalchemy import inspect, text

    is_postgres = target_engine.dialect.name == "postgresql"

    migrations = [
        ("leads", "instagram_candidates", "TEXT"),
        ("leads", "commercial_status", "VARCHAR(50) DEFAULT 'new'"),
        ("leads", "source_provider", "VARCHAR(50) DEFAULT 'google_places'"),
        ("leads", "raw_data_path", "TEXT"),
        ("leads", "logo_url", "TEXT"),
        ("leads", "gallery_urls", "TEXT"),
        ("leads", "cnpj", "VARCHAR(20)"),
        ("leads", "owners_info", "TEXT"),
        ("diagnostics", "sales_approach", "TEXT"),
        ("diagnostics", "pain_points", "TEXT"),
        ("diagnostics", "talking_points", "TEXT"),
        ("diagnostics", "value_proposition", "TEXT"),
        ("diagnostics", "stitch_prompt", "TEXT"),
        ("diagnostics", "brand_colors", "TEXT"),
        ("diagnostics", "owners_info", "TEXT"),
        ("diagnostics", "logo_url", "TEXT"),
        ("diagnostics", "generated_site_html", "TEXT"),
        ("diagnostics", "email_draft", "TEXT"),
        ("diagnostics", "whatsapp_draft", "TEXT"),
        ("diagnostics", "instagram_draft", "TEXT"),
        ("diagnostics", "diagnostic_status", "VARCHAR(50) DEFAULT 'completed'"),
        ("diagnostics", "error_message", "TEXT"),
    ]

    try:
        inspector = inspect(target_engine)
        existing_tables = set(inspector.get_table_names())
    except Exception as e:
        logger.warning(f"⚠️ Erro ao inspecionar tabelas para migrações: {e}")
        existing_tables = set()

    results = []

    for table, col, col_type in migrations:
        if existing_tables and table not in existing_tables:
            continue

        col_exists = False
        if existing_tables:
            try:
                table_cols = {c["name"].lower() for c in inspector.get_columns(table)}
                col_exists = col.lower() in table_cols
            except Exception:
                col_exists = False

        if col_exists:
            results.append({"table": table, "column": col, "status": "already_exists"})
            continue

        sql = (
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}"
            if is_postgres
            else f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"
        )
        try:
            with target_engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            logger.info(f"✅ Migração concluída: {table}.{col} adicionada.")
            results.append({"table": table, "column": col, "status": "added"})
        except Exception as e:
            logger.warning(f"⚠️ Migração {table}.{col}: {e}")
            results.append({"table": table, "column": col, "status": "error", "error": str(e)})

    return results


def init_db():
    """Cria todas as tabelas no banco com fallback automático caso o Postgres remoto/local falhe."""
    global engine, SessionLocal
    from app.db import models  # noqa: F401 — importar para registrar os modelos

    try:
        Base.metadata.create_all(bind=engine)
        _apply_migrations(engine)
    except Exception as err:
        logger.warning(f"⚠️ Falha ao conectar ao banco principal ({err}). Alternando automaticamente para SQLite local...")
        engine = _get_sqlite_engine()
        SessionLocal.configure(bind=engine)
        Base.metadata.create_all(bind=engine)
        _apply_migrations(engine)
        logger.info("✅ Banco SQLite local inicializado com sucesso.")



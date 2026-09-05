"""Database connection and session lifecycle management."""
import os
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database.models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./ai_teacher.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


# Correctly set SQLite PRAGMAs outside of transactions via connection event
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables in the database and ensure new columns exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Apply non-destructive column additions for SQLite upgrades
        migration_statements = [
            "ALTER TABLE learning_sessions ADD COLUMN knowledge_mode VARCHAR(32) DEFAULT 'topic'",
            "ALTER TABLE learning_sessions ADD COLUMN document_id VARCHAR(64) DEFAULT NULL",
            "ALTER TABLE documents ADD COLUMN file_size_bytes INTEGER DEFAULT 0",
            "ALTER TABLE documents ADD COLUMN page_count INTEGER DEFAULT 0",
            "ALTER TABLE documents ADD COLUMN chunk_count INTEGER DEFAULT 0",
            "ALTER TABLE documents ADD COLUMN status VARCHAR(32) DEFAULT 'uploaded'",
            "ALTER TABLE documents ADD COLUMN error_message TEXT DEFAULT NULL",
            "ALTER TABLE documents ADD COLUMN document_metadata JSON DEFAULT '{}'",
            "ALTER TABLE document_chunks ADD COLUMN page_number INTEGER DEFAULT NULL",
            "ALTER TABLE document_chunks ADD COLUMN slide_number INTEGER DEFAULT NULL",
            "ALTER TABLE document_chunks ADD COLUMN heading VARCHAR(256) DEFAULT NULL",
            "ALTER TABLE document_chunks ADD COLUMN chunk_metadata JSON DEFAULT '{}'",
        ]
        from sqlalchemy import text
        for stmt in migration_statements:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

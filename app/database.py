from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fks(dbapi_connection, _record) -> None:
        if url.startswith("sqlite"):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def ensure_schema(engine) -> None:
    """Add columns create_all will not add on an existing database."""
    with engine.begin() as conn:
        dialect = engine.dialect.name
        if dialect == "sqlite":
            columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()}
            if "is_admin" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
        elif dialect == "postgresql":
            conn.execute(
                text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT false")
            )

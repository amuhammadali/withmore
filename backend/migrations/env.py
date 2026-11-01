import sys
from pathlib import Path

from alembic import context
from sqlalchemy import pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import models  # noqa: E402,F401
from app.config import get_settings  # noqa: E402
from app.db import Base, make_engine  # noqa: E402

target_metadata = Base.metadata


def run_migrations_online():
    connectable = make_engine(get_settings().DATABASE_URL)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=connection.dialect.name == "sqlite", compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()

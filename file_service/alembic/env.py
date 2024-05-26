import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# import your models here
from src.models.file_model import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    pg_user = os.environ["POSTGRES_USER"]
    pg_password = os.environ["POSTGRES_PASSWORD"]
    pg_host = os.environ["POSTGRES_HOST"]
    pg_port = os.environ["POSTGRES_PORT"]
    pg_db = os.environ["FASTAPI_POSTGRES_DB"]
    db_config = {
        "sqlalchemy.url": f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}",
        "sqlalchemy.echo": "True",
    }
    connectable = engine_from_config(db_config)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

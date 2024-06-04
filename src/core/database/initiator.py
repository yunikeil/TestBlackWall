import logging

from sqlalchemy.ext.asyncio import create_async_engine

from core.settings import config
from core.database.base import Base


logger = logging.getLogger("uvicorn")

engine = create_async_engine(
    url=config.DATABASE_URL,
    pool_size=10,
    max_overflow = 0,
    pool_pre_ping = True,
    connect_args = {
        "timeout": 30,
        "command_timeout": 15,
        "server_settings": {
            "jit": "off",
            "application_name": config.DATABASE_APP_NAME,
        },
    },
    echo=config.ECHO_SQL
)


async def init_models(*, drop_all=False):
    if not config.DEBUG:
        raise ValueError(
            "Init model action is possible only when the debug is enabled, use alembic instead!"
        )

    async with engine.begin() as conn:
        if drop_all:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Drop models finished.")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Init models finished.")

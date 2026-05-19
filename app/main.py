import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from app.routers import abastecimentos, health

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied successfully")
    except Exception:
        logger.warning("Alembic migration failed, falling back to create_all")
        import asyncio

        from app.core.database import engine
        from app.models import Base

        async def _create():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        asyncio.run(_create())


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(
    title="V-Lab Abastecimentos API",
    description="API Gateway para Data Lake de abastecimentos da frota nacional",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(abastecimentos.router)
